"""Adapter contracts for consented perception events."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import Field, field_validator, model_validator

from cortex_memory_os.contracts import (
    ConsentState,
    FirewallDecisionRecord,
    ObservationEvent,
    ObservationEventType,
    PerceptionEventEnvelope,
    PerceptionRoute,
    PerceptionSourceKind,
    ScopeLevel,
    Sensitivity,
    SourceTrust,
    StrictModel,
)
from cortex_memory_os.evidence_eligibility import (
    EvidenceEligibilityPlan,
    build_evidence_eligibility_plan,
)
from cortex_memory_os.firewall import (
    FirewallAssessment,
    assess_perception_envelope,
    detect_prompt_injection,
)

PERCEPTION_ADAPTER_POLICY_REF = "policy_perception_adapter_contract_v1"
MACOS_PERCEPTION_ADAPTER_POLICY_REF = "policy_macos_perception_adapter_contract_v1"


class AdapterSource(str, Enum):
    TERMINAL = "terminal"
    BROWSER = "browser"
    MACOS_APP_WINDOW = "macos_app_window"
    MACOS_ACCESSIBILITY = "macos_accessibility"


class MacOSPermissionState(str, Enum):
    GRANTED = "granted"
    DENIED = "denied"
    UNKNOWN = "unknown"


class TerminalAdapterEvent(StrictModel):
    event_id: str = Field(min_length=1)
    event_type: ObservationEventType
    observed_at: datetime
    device: str = Field(min_length=1)
    app: str = "Terminal"
    window_title: str | None = None
    project_id: str | None = None
    command_text: str = Field(min_length=1)
    cwd: str | None = None
    shell: str | None = None
    exit_code: int | None = None
    capture_scope: ScopeLevel = ScopeLevel.PROJECT_SPECIFIC
    consent_state: ConsentState = ConsentState.ACTIVE
    raw_ref: str | None = None
    derived_text_ref: str | None = None
    sequence: int = Field(default=0, ge=0)

    @field_validator("event_type")
    @classmethod
    def require_terminal_event_type(
        cls,
        value: ObservationEventType,
    ) -> ObservationEventType:
        if value not in {
            ObservationEventType.TERMINAL_COMMAND,
            ObservationEventType.TERMINAL_OUTPUT,
        }:
            raise ValueError("terminal adapters only emit terminal command or output events")
        return value

    @model_validator(mode="after")
    def raw_refs_require_active_consent(self) -> TerminalAdapterEvent:
        if self.consent_state != ConsentState.ACTIVE and self.raw_ref:
            raise ValueError("terminal raw refs require active consent")
        return self


class BrowserAdapterEvent(StrictModel):
    event_id: str = Field(min_length=1)
    observed_at: datetime
    device: str = Field(min_length=1)
    app: str = "Browser"
    window_title: str | None = None
    tab_title: str | None = None
    url: str = Field(min_length=1)
    visible_text: str = Field(min_length=1)
    dom_ref: str | None = None
    derived_text_ref: str | None = None
    capture_scope: ScopeLevel = ScopeLevel.SESSION_ONLY
    consent_state: ConsentState = ConsentState.ACTIVE
    sequence: int = Field(default=0, ge=0)

    @field_validator("url")
    @classmethod
    def require_http_url(cls, value: str) -> str:
        if not value.startswith(("http://", "https://")):
            raise ValueError("browser adapter URL must be http or https")
        return value

    @model_validator(mode="after")
    def raw_dom_refs_require_active_consent(self) -> BrowserAdapterEvent:
        if self.consent_state != ConsentState.ACTIVE and self.dom_ref:
            raise ValueError("browser DOM refs require active consent")
        return self


class MacOSAppWindowAdapterEvent(StrictModel):
    event_id: str = Field(min_length=1)
    observed_at: datetime
    device: str = Field(min_length=1)
    app: str = Field(min_length=1)
    bundle_id: str = Field(min_length=1)
    window_title: str | None = None
    active: bool = True
    project_id: str | None = None
    capture_scope: ScopeLevel = ScopeLevel.APP_SPECIFIC
    consent_state: ConsentState = ConsentState.UNKNOWN
    screen_recording_permission: MacOSPermissionState = MacOSPermissionState.UNKNOWN
    accessibility_permission: MacOSPermissionState = MacOSPermissionState.UNKNOWN
    app_allowed: bool = False
    sensitive_app: bool = False
    raw_ref: str | None = None
    derived_text_ref: str | None = None
    sequence: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def forbid_raw_window_capture_refs(self) -> MacOSAppWindowAdapterEvent:
        if self.raw_ref:
            raise ValueError("macOS app/window adapter cannot carry raw capture refs")
        if self.sensitive_app and self.window_title:
            raise ValueError("sensitive macOS apps cannot carry window titles")
        return self


class MacOSAccessibilityAdapterEvent(StrictModel):
    event_id: str = Field(min_length=1)
    observed_at: datetime
    device: str = Field(min_length=1)
    app: str = Field(min_length=1)
    bundle_id: str = Field(min_length=1)
    window_title: str | None = None
    focused_role: str = Field(min_length=1)
    focused_label: str | None = None
    value_preview: str | None = None
    project_id: str | None = None
    capture_scope: ScopeLevel = ScopeLevel.APP_SPECIFIC
    consent_state: ConsentState = ConsentState.UNKNOWN
    accessibility_permission: MacOSPermissionState = MacOSPermissionState.UNKNOWN
    app_allowed: bool = False
    private_field_detected: bool = False
    raw_tree_ref: str | None = None
    derived_text_ref: str | None = None
    sequence: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def forbid_raw_or_private_accessibility_capture(
        self,
    ) -> MacOSAccessibilityAdapterEvent:
        if self.raw_tree_ref:
            raise ValueError("macOS accessibility adapter cannot carry raw tree refs")
        if self.private_field_detected and self.value_preview:
            raise ValueError("private accessibility fields cannot carry value previews")
        return self


class AdapterHandoffResult(StrictModel):
    adapter_source: AdapterSource
    envelope: PerceptionEventEnvelope
    firewall: FirewallDecisionRecord
    evidence_plan: EvidenceEligibilityPlan
    redacted_text: str


def build_terminal_envelope(event: TerminalAdapterEvent) -> PerceptionEventEnvelope:
    route = (
        PerceptionRoute.FIREWALL_REQUIRED
        if event.consent_state == ConsentState.ACTIVE
        else PerceptionRoute.DISCARD
    )
    raw_ref = event.raw_ref if event.consent_state == ConsentState.ACTIVE else None
    derived_refs = [event.derived_text_ref] if event.derived_text_ref and route != PerceptionRoute.DISCARD else []
    observation = ObservationEvent(
        event_id=event.event_id,
        event_type=event.event_type,
        timestamp=event.observed_at,
        device=event.device,
        app=event.app,
        window_title=event.window_title,
        project_id=event.project_id,
        payload_ref=f"volatile://terminal/{event.event_id}",
        source_trust=SourceTrust.LOCAL_OBSERVED,
        capture_scope=event.capture_scope,
        consent_state=event.consent_state,
        raw_contains_user_input=True,
    )
    return PerceptionEventEnvelope(
        envelope_id=f"perception_terminal_{event.event_id}",
        source_kind=PerceptionSourceKind.TERMINAL,
        observation=observation,
        observed_at=event.observed_at,
        sequence=event.sequence,
        consent_state=event.consent_state,
        capture_scope=event.capture_scope,
        source_trust=SourceTrust.LOCAL_OBSERVED,
        sensitivity_hint=Sensitivity.PRIVATE_WORK,
        route=route,
        raw_ref=raw_ref,
        derived_refs=derived_refs,
        third_party_content=False,
        prompt_injection_risk=False,
        required_policy_refs=[PERCEPTION_ADAPTER_POLICY_REF],
    )


def build_browser_envelope(event: BrowserAdapterEvent) -> PerceptionEventEnvelope:
    route = (
        PerceptionRoute.FIREWALL_REQUIRED
        if event.consent_state == ConsentState.ACTIVE
        else PerceptionRoute.DISCARD
    )
    prompt_risk = bool(detect_prompt_injection(event.visible_text))
    derived_refs = [event.derived_text_ref] if event.derived_text_ref and route != PerceptionRoute.DISCARD else []
    observation = ObservationEvent(
        event_id=event.event_id,
        event_type=ObservationEventType.BROWSER_DOM,
        timestamp=event.observed_at,
        device=event.device,
        app=event.app,
        window_title=event.window_title or event.tab_title,
        project_id=None,
        payload_ref=f"volatile://browser/{event.event_id}",
        source_trust=SourceTrust.EXTERNAL_UNTRUSTED,
        capture_scope=event.capture_scope,
        consent_state=event.consent_state,
        raw_contains_user_input=False,
    )
    return PerceptionEventEnvelope(
        envelope_id=f"perception_browser_{event.event_id}",
        source_kind=PerceptionSourceKind.BROWSER,
        observation=observation,
        observed_at=event.observed_at,
        sequence=event.sequence,
        consent_state=event.consent_state,
        capture_scope=event.capture_scope,
        source_trust=SourceTrust.EXTERNAL_UNTRUSTED,
        sensitivity_hint=Sensitivity.PRIVATE_WORK,
        route=route,
        raw_ref=event.dom_ref if event.consent_state == ConsentState.ACTIVE else None,
        derived_refs=derived_refs,
        third_party_content=True,
        prompt_injection_risk=prompt_risk,
        required_policy_refs=[PERCEPTION_ADAPTER_POLICY_REF],
    )


def build_macos_app_window_envelope(
    event: MacOSAppWindowAdapterEvent,
) -> PerceptionEventEnvelope:
    route = _macos_route(
        consent_state=event.consent_state,
        permission_state=event.screen_recording_permission,
        app_allowed=event.app_allowed,
        private_or_sensitive=event.sensitive_app,
    )
    derived_refs = [event.derived_text_ref] if event.derived_text_ref and route != PerceptionRoute.DISCARD else []
    observation = ObservationEvent(
        event_id=event.event_id,
        event_type=ObservationEventType.APP_WINDOW,
        timestamp=event.observed_at,
        device=event.device,
        app=event.app,
        window_title=event.window_title if route != PerceptionRoute.DISCARD else None,
        project_id=event.project_id,
        payload_ref=f"volatile://macos/app-window/{event.event_id}",
        source_trust=SourceTrust.LOCAL_OBSERVED,
        capture_scope=event.capture_scope,
        consent_state=event.consent_state,
        raw_contains_user_input=False,
    )
    return PerceptionEventEnvelope(
        envelope_id=f"perception_macos_app_window_{event.event_id}",
        source_kind=PerceptionSourceKind.APP_WINDOW,
        observation=observation,
        observed_at=event.observed_at,
        sequence=event.sequence,
        consent_state=event.consent_state,
        capture_scope=event.capture_scope,
        source_trust=SourceTrust.LOCAL_OBSERVED,
        sensitivity_hint=Sensitivity.PRIVATE_WORK,
        route=route,
        raw_ref=None,
        derived_refs=derived_refs,
        third_party_content=False,
        prompt_injection_risk=False,
        required_policy_refs=[MACOS_PERCEPTION_ADAPTER_POLICY_REF],
    )


def build_macos_accessibility_envelope(
    event: MacOSAccessibilityAdapterEvent,
) -> PerceptionEventEnvelope:
    route = _macos_route(
        consent_state=event.consent_state,
        permission_state=event.accessibility_permission,
        app_allowed=event.app_allowed,
        private_or_sensitive=event.private_field_detected,
    )
    derived_refs = [event.derived_text_ref] if event.derived_text_ref and route != PerceptionRoute.DISCARD else []
    observation = ObservationEvent(
        event_id=event.event_id,
        event_type=ObservationEventType.ACCESSIBILITY_TREE,
        timestamp=event.observed_at,
        device=event.device,
        app=event.app,
        window_title=event.window_title if route != PerceptionRoute.DISCARD else None,
        project_id=event.project_id,
        payload_ref=f"volatile://macos/accessibility/{event.event_id}",
        source_trust=SourceTrust.LOCAL_OBSERVED,
        capture_scope=event.capture_scope,
        consent_state=event.consent_state,
        raw_contains_user_input=event.value_preview is not None,
    )
    return PerceptionEventEnvelope(
        envelope_id=f"perception_macos_accessibility_{event.event_id}",
        source_kind=PerceptionSourceKind.ACCESSIBILITY,
        observation=observation,
        observed_at=event.observed_at,
        sequence=event.sequence,
        consent_state=event.consent_state,
        capture_scope=event.capture_scope,
        source_trust=SourceTrust.LOCAL_OBSERVED,
        sensitivity_hint=(
            Sensitivity.SECRET
            if event.private_field_detected
            else Sensitivity.PRIVATE_WORK
        ),
        route=route,
        raw_ref=None,
        derived_refs=derived_refs,
        third_party_content=False,
        prompt_injection_risk=False,
        required_policy_refs=[MACOS_PERCEPTION_ADAPTER_POLICY_REF],
    )


def handoff_terminal_event(event: TerminalAdapterEvent) -> AdapterHandoffResult:
    envelope = build_terminal_envelope(event)
    assessment = assess_perception_envelope(envelope, event.command_text)
    return _build_handoff_result(
        AdapterSource.TERMINAL,
        envelope,
        assessment,
        redacted_text_ref=f"derived://terminal/redacted/{event.event_id}",
    )


def handoff_browser_event(event: BrowserAdapterEvent) -> AdapterHandoffResult:
    envelope = build_browser_envelope(event)
    assessment = assess_perception_envelope(envelope, event.visible_text)
    return _build_handoff_result(
        AdapterSource.BROWSER,
        envelope,
        assessment,
        redacted_text_ref=f"derived://browser/redacted/{event.event_id}",
    )


def handoff_macos_app_window_event(
    event: MacOSAppWindowAdapterEvent,
) -> AdapterHandoffResult:
    envelope = build_macos_app_window_envelope(event)
    assessment = assess_perception_envelope(envelope, _macos_app_window_text(event))
    return _build_handoff_result(
        AdapterSource.MACOS_APP_WINDOW,
        envelope,
        assessment,
        redacted_text_ref=f"derived://macos/app-window/redacted/{event.event_id}",
    )


def handoff_macos_accessibility_event(
    event: MacOSAccessibilityAdapterEvent,
) -> AdapterHandoffResult:
    envelope = build_macos_accessibility_envelope(event)
    assessment = assess_perception_envelope(envelope, _macos_accessibility_text(event))
    return _build_handoff_result(
        AdapterSource.MACOS_ACCESSIBILITY,
        envelope,
        assessment,
        redacted_text_ref=f"derived://macos/accessibility/redacted/{event.event_id}",
    )


def _build_handoff_result(
    adapter_source: AdapterSource,
    envelope: PerceptionEventEnvelope,
    assessment: FirewallAssessment,
    *,
    redacted_text_ref: str,
) -> AdapterHandoffResult:
    evidence_plan = build_evidence_eligibility_plan(
        envelope,
        assessment.decision,
        redacted_text_ref=redacted_text_ref,
    )
    return AdapterHandoffResult(
        adapter_source=adapter_source,
        envelope=envelope,
        firewall=assessment.decision,
        evidence_plan=evidence_plan,
        redacted_text=assessment.redacted_text,
    )


def _macos_route(
    *,
    consent_state: ConsentState,
    permission_state: MacOSPermissionState,
    app_allowed: bool,
    private_or_sensitive: bool,
) -> PerceptionRoute:
    if consent_state != ConsentState.ACTIVE:
        return PerceptionRoute.DISCARD
    if permission_state != MacOSPermissionState.GRANTED:
        return PerceptionRoute.DISCARD
    if not app_allowed or private_or_sensitive:
        return PerceptionRoute.DISCARD
    return PerceptionRoute.FIREWALL_REQUIRED


def _macos_app_window_text(event: MacOSAppWindowAdapterEvent) -> str:
    parts = [
        f"app={event.app}",
        f"bundle_id={event.bundle_id}",
        f"active={event.active}",
    ]
    if event.window_title:
        parts.append(f"window_title={event.window_title}")
    if event.project_id:
        parts.append(f"project_id={event.project_id}")
    return " ".join(parts)


def _macos_accessibility_text(event: MacOSAccessibilityAdapterEvent) -> str:
    parts = [
        f"app={event.app}",
        f"bundle_id={event.bundle_id}",
        f"role={event.focused_role}",
    ]
    if event.focused_label:
        parts.append(f"label={event.focused_label}")
    if event.value_preview:
        parts.append(f"value={event.value_preview}")
    if event.project_id:
        parts.append(f"project_id={event.project_id}")
    return " ".join(parts)
