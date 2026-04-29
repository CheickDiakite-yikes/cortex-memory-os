"""Adapter contracts for first browser and terminal perception events."""

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


class AdapterSource(str, Enum):
    TERMINAL = "terminal"
    BROWSER = "browser"


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
