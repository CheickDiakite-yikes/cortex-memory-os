"""Shadow Pointer state contract."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from cortex_memory_os.contracts import SourceTrust
from cortex_memory_os.native_permission_smoke import NativePermissionSmokeResult


SHADOW_POINTER_PERMISSION_ONBOARDING_ID = "SHADOW-POINTER-PERMISSION-ONBOARDING-001"
SHADOW_POINTER_PERMISSION_ONBOARDING_POLICY_REF = (
    "policy_shadow_pointer_permission_onboarding_v1"
)
SHADOW_POINTER_POINTING_POLICY_REF = "policy_shadow_pointer_pointing_proposal_v1"
SHADOW_POINTER_STATE_MACHINE_ID = "SHADOW-POINTER-STATE-MACHINE-001"
SHADOW_POINTER_STATE_MACHINE_POLICY_REF = "policy_shadow_pointer_state_machine_v1"
SHADOW_POINTER_LIVE_RECEIPT_ID = "SHADOW-POINTER-LIVE-RECEIPT-001"
SHADOW_POINTER_LIVE_RECEIPT_POLICY_REF = "policy_shadow_pointer_live_receipt_v1"
CONSENT_FIRST_ONBOARDING_ID = "CONSENT-FIRST-ONBOARDING-001"
CONSENT_FIRST_ONBOARDING_POLICY_REF = "policy_consent_first_onboarding_v1"
SPATIAL_PROPOSAL_SCHEMA_ID = "SPATIAL-PROPOSAL-SCHEMA-001"
SPATIAL_PROPOSAL_SCHEMA_POLICY_REF = "policy_spatial_proposal_schema_v1"


class ShadowPointerState(str, Enum):
    OFF = "off"
    OBSERVING = "observing"
    PRIVATE_MASKING = "private_masking"
    SEGMENTING = "segmenting"
    REMEMBERING = "remembering"
    LEARNING_SKILL = "learning_skill"
    AGENT_CONTEXTING = "agent_contexting"
    AGENT_ACTING = "agent_acting"
    NEEDS_APPROVAL = "needs_approval"
    PAUSED = "paused"


class ShadowPointerObservationMode(str, Enum):
    OFF = "off"
    INVOKED = "invoked"
    SESSION = "session"
    PAUSED = "paused"
    BLOCKED = "blocked"


class ShadowPointerControlAction(str, Enum):
    STATUS = "status"
    PAUSE_OBSERVATION = "pause_observation"
    RESUME_OBSERVATION = "resume_observation"
    DELETE_RECENT = "delete_recent"
    IGNORE_APP = "ignore_app"


class ShadowPointerCoordinateSpace(str, Enum):
    SCREEN_NORMALIZED = "screen_normalized"
    WINDOW_NORMALIZED = "window_normalized"
    ELEMENT_BOUNDS_NORMALIZED = "element_bounds_normalized"


class ShadowPointerPointingAction(str, Enum):
    DISPLAY_OVERLAY = "display_overlay"
    HIGHLIGHT_ELEMENT = "highlight_element"
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    TYPE_TEXT = "type_text"
    DRAG = "drag"
    SCROLL = "scroll"
    OPEN_URL = "open_url"
    EXECUTE_TOOL = "execute_tool"


class ShadowPointerStatePresentation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state: ShadowPointerState
    label: str = Field(min_length=1)
    compact_label: str = Field(min_length=1, max_length=28)
    icon: str = Field(min_length=1)
    tone: str = Field(min_length=1)
    pointer_shape: str = Field(min_length=1)
    peripheral_cue: str = Field(min_length=1)
    allowed_effects: list[str] = Field(min_length=1)
    blocked_effects: list[str] = Field(default_factory=list)
    policy_refs: tuple[str, ...] = Field(
        default=(SHADOW_POINTER_STATE_MACHINE_POLICY_REF,)
    )

    @model_validator(mode="after")
    def require_state_policy_ref(self) -> ShadowPointerStatePresentation:
        if SHADOW_POINTER_STATE_MACHINE_POLICY_REF not in self.policy_refs:
            raise ValueError("state presentation requires policy ref")
        if self.state in {
            ShadowPointerState.AGENT_ACTING,
            ShadowPointerState.NEEDS_APPROVAL,
        } and "privileged_action_without_confirmation" not in self.blocked_effects:
            raise ValueError("high-attention states must block unconfirmed actions")
        return self


class ShadowPointerSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state: ShadowPointerState
    workstream_label: str = Field(min_length=1)
    seeing: list[str] = Field(default_factory=list)
    ignoring: list[str] = Field(default_factory=list)
    possible_memory: str | None = None
    possible_skill: str | None = None
    approval_reason: str | None = None

    @model_validator(mode="after")
    def state_requires_matching_context(self) -> ShadowPointerSnapshot:
        if self.state == ShadowPointerState.PRIVATE_MASKING and not self.ignoring:
            raise ValueError("private masking state requires ignored/masked items")
        if self.state == ShadowPointerState.REMEMBERING and not self.possible_memory:
            raise ValueError("remembering state requires a possible memory")
        if self.state == ShadowPointerState.LEARNING_SKILL and not self.possible_skill:
            raise ValueError("learning skill state requires a possible skill")
        if self.state == ShadowPointerState.NEEDS_APPROVAL and not self.approval_reason:
            raise ValueError("needs approval state requires an approval reason")
        if self.state == ShadowPointerState.OFF and (self.seeing or self.possible_memory):
            raise ValueError("off state cannot include active observation details")
        return self


class ShadowPointerControlCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: ShadowPointerControlAction
    requested_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    actor: str = Field(default="user", min_length=1)
    duration_minutes: int | None = Field(default=None, ge=1, le=24 * 60)
    delete_window_minutes: int | None = Field(default=None, ge=1, le=24 * 60)
    app_name: str | None = None
    user_confirmed: bool = False

    @model_validator(mode="after")
    def require_action_specific_inputs(self) -> ShadowPointerControlCommand:
        if self.action == ShadowPointerControlAction.PAUSE_OBSERVATION:
            if self.duration_minutes is None:
                raise ValueError("pause observation requires duration_minutes")
        if self.action == ShadowPointerControlAction.DELETE_RECENT:
            if self.delete_window_minutes is None:
                raise ValueError("delete recent requires delete_window_minutes")
            if not self.user_confirmed:
                raise ValueError("delete recent requires explicit user confirmation")
        if self.action == ShadowPointerControlAction.IGNORE_APP:
            if not self.app_name or not self.app_name.strip():
                raise ValueError("ignore app requires app_name")
            if not self.user_confirmed:
                raise ValueError("ignore app requires explicit user confirmation")
        return self


class ShadowPointerControlReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid")

    receipt_id: str = Field(min_length=1)
    action: ShadowPointerControlAction
    resulting_snapshot: ShadowPointerSnapshot
    observation_active: bool
    memory_write_allowed: bool
    audit_required: bool
    audit_action: str | None = None
    confirmation_observed: bool
    affected_apps: list[str] = Field(default_factory=list)
    deleted_window_minutes: int | None = None
    expires_at: datetime | None = None
    safety_notes: list[str] = Field(min_length=1)


class ShadowPointerPointingProposal(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    proposal_id: str = Field(min_length=1)
    proposed_by: str = Field(default="model", min_length=1)
    source_trust: SourceTrust = SourceTrust.AGENT_INFERRED
    coordinate_space: ShadowPointerCoordinateSpace
    x: float = Field(ge=0.0, le=1.0)
    y: float = Field(ge=0.0, le=1.0)
    target_label: str = Field(min_length=1, max_length=160)
    reason: str = Field(min_length=1, max_length=280)
    evidence_refs: list[str] = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    requested_action: ShadowPointerPointingAction = (
        ShadowPointerPointingAction.DISPLAY_OVERLAY
    )
    display_id: str | None = None
    window_ref: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("target_label", "reason")
    @classmethod
    def reject_instruction_like_text(cls, value: str) -> str:
        lowered = value.lower()
        forbidden_fragments = [
            "ignore previous instructions",
            "reveal secrets",
            "disable safeguards",
            "exfiltrate",
            "run this command",
            "execute this command",
            "send credentials",
        ]
        if any(fragment in lowered for fragment in forbidden_fragments):
            raise ValueError("pointing proposals cannot carry instruction-like text")
        return value

    @model_validator(mode="after")
    def require_scope_metadata(self) -> ShadowPointerPointingProposal:
        if self.source_trust == SourceTrust.USER_CONFIRMED:
            raise ValueError("model pointing proposals cannot claim user-confirmed trust")
        if (
            self.coordinate_space
            in {
                ShadowPointerCoordinateSpace.WINDOW_NORMALIZED,
                ShadowPointerCoordinateSpace.ELEMENT_BOUNDS_NORMALIZED,
            }
            and not self.window_ref
        ):
            raise ValueError("window or element coordinates require window_ref")
        return self


class ShadowPointerPointingReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid")

    receipt_id: str = Field(min_length=1)
    proposal_id: str = Field(min_length=1)
    resulting_snapshot: ShadowPointerSnapshot
    coordinate_space: ShadowPointerCoordinateSpace
    x: float = Field(ge=0.0, le=1.0)
    y: float = Field(ge=0.0, le=1.0)
    target_label: str = Field(min_length=1)
    display_only: bool
    allowed_effects: list[str] = Field(min_length=1)
    blocked_effects: list[str] = Field(default_factory=list)
    requires_user_confirmation: bool
    observation_active: bool
    proposal_memory_write_allowed: bool
    audit_required: bool
    audit_action: str
    policy_refs: tuple[str, ...] = Field(min_length=1)
    untrusted_source: bool
    safety_notes: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def enforce_display_only_boundary(self) -> ShadowPointerPointingReceipt:
        allowed = set(self.allowed_effects)
        if not self.display_only:
            raise ValueError("pointing receipt must be display-only")
        if allowed - {"display_overlay", "highlight_element"}:
            raise ValueError("pointing receipts cannot allow privileged effects")
        if self.proposal_memory_write_allowed:
            raise ValueError("pointing proposals cannot directly write memory")
        if SHADOW_POINTER_POINTING_POLICY_REF not in self.policy_refs:
            raise ValueError("pointing receipt requires policy reference")
        return self


class ShadowPointerLiveReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid")

    receipt_id: str = Field(min_length=1)
    state: ShadowPointerState
    observation_mode: ShadowPointerObservationMode
    title: str = Field(min_length=1, max_length=80)
    primary_line: str = Field(min_length=1, max_length=160)
    trust_class: SourceTrust
    firewall_decision: str = Field(min_length=1)
    evidence_write_mode: str = Field(min_length=1)
    memory_eligible: bool
    raw_ref_retained: bool
    raw_payload_included: bool = False
    action_required: bool
    compact_fields: dict[str, str] = Field(default_factory=dict)
    allowed_effects: list[str] = Field(min_length=1)
    blocked_effects: list[str] = Field(default_factory=list)
    policy_refs: tuple[str, ...] = Field(
        default=(SHADOW_POINTER_LIVE_RECEIPT_POLICY_REF,)
    )

    @model_validator(mode="after")
    def enforce_live_receipt_boundaries(self) -> ShadowPointerLiveReceipt:
        if SHADOW_POINTER_LIVE_RECEIPT_POLICY_REF not in self.policy_refs:
            raise ValueError("live receipt requires policy ref")
        if self.raw_payload_included:
            raise ValueError("live receipts cannot include raw payloads")
        if self.trust_class in {
            SourceTrust.EXTERNAL_UNTRUSTED,
            SourceTrust.HOSTILE_UNTIL_SAFE,
        }:
            if self.memory_eligible:
                raise ValueError("external live receipts cannot be memory eligible")
            if self.raw_ref_retained:
                raise ValueError("external live receipts cannot retain raw refs")
        if self.observation_mode in {
            ShadowPointerObservationMode.OFF,
            ShadowPointerObservationMode.PAUSED,
            ShadowPointerObservationMode.BLOCKED,
        } and self.memory_eligible:
            raise ValueError("inactive observation modes cannot be memory eligible")
        required_fields = {"trust", "memory", "raw_refs", "policy"}
        if missing := sorted(required_fields.difference(self.compact_fields)):
            raise ValueError(f"live receipt missing compact fields: {missing}")
        return self


class ShadowPointerSpatialMapping(BaseModel):
    model_config = ConfigDict(extra="forbid")

    proposal_id: str = Field(min_length=1)
    coordinate_space: ShadowPointerCoordinateSpace
    viewport_width_px: int = Field(gt=0)
    viewport_height_px: int = Field(gt=0)
    device_pixel_ratio: float = Field(default=1.0, gt=0.0, le=8.0)
    x_normalized: float = Field(ge=0.0, le=1.0)
    y_normalized: float = Field(ge=0.0, le=1.0)
    x_css_px: int = Field(ge=0)
    y_css_px: int = Field(ge=0)
    x_device_px: int = Field(ge=0)
    y_device_px: int = Field(ge=0)
    clamped: bool
    display_only: bool = True
    policy_refs: tuple[str, ...] = Field(
        default=(
            SPATIAL_PROPOSAL_SCHEMA_POLICY_REF,
            SHADOW_POINTER_POINTING_POLICY_REF,
        )
    )

    @model_validator(mode="after")
    def enforce_spatial_mapping_boundary(self) -> ShadowPointerSpatialMapping:
        if not self.display_only:
            raise ValueError("spatial mapping must remain display-only")
        if SPATIAL_PROPOSAL_SCHEMA_POLICY_REF not in self.policy_refs:
            raise ValueError("spatial mapping requires policy ref")
        if self.x_css_px > self.viewport_width_px:
            raise ValueError("x_css_px exceeds viewport")
        if self.y_css_px > self.viewport_height_px:
            raise ValueError("y_css_px exceeds viewport")
        return self


class ConsentFirstOnboardingStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step_id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    proof: str = Field(min_length=1)
    allowed_effects: list[str] = Field(min_length=1)
    blocked_effects: list[str] = Field(default_factory=list)
    requires_user_action: bool


class ConsentFirstOnboardingPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan_id: str = CONSENT_FIRST_ONBOARDING_ID
    observation_mode: ShadowPointerObservationMode = ShadowPointerObservationMode.INVOKED
    synthetic_only: bool = True
    real_capture_started: bool = False
    raw_storage_enabled: bool = False
    durable_private_memory_write_enabled: bool = False
    external_effect_enabled: bool = False
    steps: list[ConsentFirstOnboardingStep] = Field(min_length=5)
    policy_refs: tuple[str, ...] = Field(
        default=(CONSENT_FIRST_ONBOARDING_POLICY_REF,)
    )

    @model_validator(mode="after")
    def enforce_consent_first_boundaries(self) -> ConsentFirstOnboardingPlan:
        if CONSENT_FIRST_ONBOARDING_POLICY_REF not in self.policy_refs:
            raise ValueError("consent onboarding requires policy ref")
        if not self.synthetic_only:
            raise ValueError("onboarding plan must start synthetic-only")
        if self.real_capture_started:
            raise ValueError("onboarding cannot start real capture")
        if self.raw_storage_enabled:
            raise ValueError("onboarding cannot enable raw storage")
        if self.durable_private_memory_write_enabled:
            raise ValueError("onboarding cannot write private durable memory")
        if self.external_effect_enabled:
            raise ValueError("onboarding cannot create external effects")
        required_steps = {
            "show_off",
            "invoke_synthetic_observation",
            "prove_masking",
            "create_candidate_memory",
            "delete_candidate_memory",
            "show_audit_receipt",
        }
        actual_steps = {step.step_id for step in self.steps}
        if missing := sorted(required_steps.difference(actual_steps)):
            raise ValueError(f"onboarding plan missing required steps: {missing}")
        return self


class ShadowPointerPermissionOnboardingReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid")

    proof_id: str = Field(min_length=1)
    policy_ref: str = Field(min_length=1)
    checked_at: datetime
    screen_recording_preflight: bool
    accessibility_trusted: bool
    permission_status_visible: bool
    resulting_snapshot: ShadowPointerSnapshot
    prompt_requested: bool
    capture_started: bool
    accessibility_observer_started: bool
    memory_write_allowed: bool
    evidence_refs: list[str] = Field(default_factory=list)
    allowed_effects: list[str] = Field(min_length=1)
    blocked_effects: list[str] = Field(min_length=1)
    passed: bool

    @model_validator(mode="after")
    def enforce_onboarding_boundary(self) -> ShadowPointerPermissionOnboardingReceipt:
        if self.proof_id != SHADOW_POINTER_PERMISSION_ONBOARDING_ID:
            raise ValueError("permission onboarding proof_id mismatch")
        if self.policy_ref != SHADOW_POINTER_PERMISSION_ONBOARDING_POLICY_REF:
            raise ValueError("permission onboarding policy_ref mismatch")
        if not self.permission_status_visible:
            raise ValueError("permission onboarding must render permission status")
        if self.resulting_snapshot.state != ShadowPointerState.NEEDS_APPROVAL:
            raise ValueError("permission onboarding must stop at needs-approval")
        if self.prompt_requested:
            raise ValueError("permission onboarding cannot request permission prompts")
        if self.capture_started:
            raise ValueError("permission onboarding cannot start screen capture")
        if self.accessibility_observer_started:
            raise ValueError("permission onboarding cannot start Accessibility observers")
        if self.memory_write_allowed:
            raise ValueError("permission onboarding cannot allow memory writes")
        if self.evidence_refs:
            raise ValueError("permission onboarding cannot emit evidence refs")
        if set(self.allowed_effects) != {
            "read_permission_status",
            "render_shadow_pointer_permission_state",
        }:
            raise ValueError("permission onboarding allowed effects are too broad")
        required_blocked = {
            "request_screen_recording_permission",
            "request_accessibility_permission",
            "start_screen_capture",
            "start_accessibility_observer",
            "write_memory",
            "store_raw_evidence",
        }
        if missing := sorted(required_blocked.difference(self.blocked_effects)):
            raise ValueError(f"permission onboarding missing blocked effects: {missing}")
        return self


def build_permission_onboarding_receipt(
    permission_result: NativePermissionSmokeResult,
) -> ShadowPointerPermissionOnboardingReceipt:
    """Render permission readiness without escalating into capture or writes."""

    screen_status = (
        "Screen Recording: ready"
        if permission_result.screen_recording_preflight
        else "Screen Recording: not ready"
    )
    accessibility_status = (
        "Accessibility: ready"
        if permission_result.accessibility_trusted
        else "Accessibility: not ready"
    )
    approval_reason = (
        "Start observation requires explicit consent."
        if permission_result.screen_recording_preflight
        and permission_result.accessibility_trusted
        else "Review missing macOS permissions before observation can start."
    )
    snapshot = ShadowPointerSnapshot(
        state=ShadowPointerState.NEEDS_APPROVAL,
        workstream_label="Permission onboarding",
        seeing=[screen_status, accessibility_status],
        ignoring=[
            "screen capture not started",
            "accessibility observer not started",
            "memory writes disabled",
        ],
        possible_memory=None,
        possible_skill=None,
        approval_reason=approval_reason,
    )
    return ShadowPointerPermissionOnboardingReceipt(
        proof_id=SHADOW_POINTER_PERMISSION_ONBOARDING_ID,
        policy_ref=SHADOW_POINTER_PERMISSION_ONBOARDING_POLICY_REF,
        checked_at=permission_result.checked_at,
        screen_recording_preflight=permission_result.screen_recording_preflight,
        accessibility_trusted=permission_result.accessibility_trusted,
        permission_status_visible=True,
        resulting_snapshot=snapshot,
        prompt_requested=permission_result.prompt_requested,
        capture_started=permission_result.capture_started,
        accessibility_observer_started=permission_result.accessibility_observer_started,
        memory_write_allowed=False,
        evidence_refs=[],
        allowed_effects=[
            "read_permission_status",
            "render_shadow_pointer_permission_state",
        ],
        blocked_effects=[
            "request_screen_recording_permission",
            "request_accessibility_permission",
            "start_screen_capture",
            "start_accessibility_observer",
            "write_memory",
            "store_raw_evidence",
        ],
        passed=permission_result.passed,
    )


def state_presentation(state: ShadowPointerState) -> ShadowPointerStatePresentation:
    """Return a compact visual contract for a Shadow Pointer state."""

    return _STATE_PRESENTATIONS[state]


def all_state_presentations() -> list[ShadowPointerStatePresentation]:
    """Return the full state table used by native, browser, and dashboard surfaces."""

    return [state_presentation(state) for state in ShadowPointerState]


def build_live_receipt(
    snapshot: ShadowPointerSnapshot,
    *,
    observation_mode: ShadowPointerObservationMode,
    source_trust: SourceTrust,
    firewall_decision: str,
    evidence_write_mode: str,
    memory_eligible: bool,
    raw_ref_retained: bool,
    raw_payload_included: bool = False,
    latest_action: str = "Observation update",
    receipt_id: str | None = None,
) -> ShadowPointerLiveReceipt:
    """Compile the small trust receipt shown near the Shadow Pointer."""

    presentation = state_presentation(snapshot.state)
    trust_label = source_trust.name.lower()
    memory_label = "eligible" if memory_eligible else "not eligible"
    raw_ref_label = "retained" if raw_ref_retained else "none"
    policy_label = f"{firewall_decision}; {evidence_write_mode}"
    action_required = snapshot.state == ShadowPointerState.NEEDS_APPROVAL
    blocked_effects = list(presentation.blocked_effects)
    if source_trust in {SourceTrust.EXTERNAL_UNTRUSTED, SourceTrust.HOSTILE_UNTIL_SAFE}:
        blocked_effects = _append_unique(blocked_effects, "trusted_instruction_promotion")
        blocked_effects = _append_unique(blocked_effects, "durable_memory_write")
        blocked_effects = _append_unique(blocked_effects, "raw_ref_retention")

    return ShadowPointerLiveReceipt(
        receipt_id=receipt_id
        or f"shadow_live_{snapshot.state.value}_{observation_mode.value}",
        state=snapshot.state,
        observation_mode=observation_mode,
        title=presentation.label,
        primary_line=f"{latest_action}: {snapshot.workstream_label}",
        trust_class=source_trust,
        firewall_decision=firewall_decision,
        evidence_write_mode=evidence_write_mode,
        memory_eligible=memory_eligible,
        raw_ref_retained=raw_ref_retained,
        raw_payload_included=raw_payload_included,
        action_required=action_required,
        compact_fields={
            "trust": trust_label,
            "memory": memory_label,
            "raw_refs": raw_ref_label,
            "policy": policy_label,
        },
        allowed_effects=list(presentation.allowed_effects),
        blocked_effects=blocked_effects,
        policy_refs=(
            SHADOW_POINTER_LIVE_RECEIPT_POLICY_REF,
            SHADOW_POINTER_STATE_MACHINE_POLICY_REF,
        ),
    )


def map_pointing_proposal_to_viewport(
    proposal: ShadowPointerPointingProposal,
    *,
    viewport_width_px: int,
    viewport_height_px: int,
    device_pixel_ratio: float = 1.0,
) -> ShadowPointerSpatialMapping:
    """Map normalized proposal coordinates to bounded display pixels."""

    x_normalized = min(max(proposal.x, 0.0), 1.0)
    y_normalized = min(max(proposal.y, 0.0), 1.0)
    x_css = round(x_normalized * viewport_width_px)
    y_css = round(y_normalized * viewport_height_px)
    x_device = round(x_css * device_pixel_ratio)
    y_device = round(y_css * device_pixel_ratio)
    return ShadowPointerSpatialMapping(
        proposal_id=proposal.proposal_id,
        coordinate_space=proposal.coordinate_space,
        viewport_width_px=viewport_width_px,
        viewport_height_px=viewport_height_px,
        device_pixel_ratio=device_pixel_ratio,
        x_normalized=x_normalized,
        y_normalized=y_normalized,
        x_css_px=x_css,
        y_css_px=y_css,
        x_device_px=x_device,
        y_device_px=y_device,
        clamped=x_normalized != proposal.x or y_normalized != proposal.y,
    )


def default_consent_first_onboarding_plan() -> ConsentFirstOnboardingPlan:
    """Build the safe first-run walkthrough before real observation."""

    return ConsentFirstOnboardingPlan(
        steps=[
            ConsentFirstOnboardingStep(
                step_id="show_off",
                label="Show Cortex off",
                proof="Shadow Pointer renders off state before any observation.",
                allowed_effects=["render_shadow_pointer"],
                blocked_effects=["screen_capture", "memory_write"],
                requires_user_action=False,
            ),
            ConsentFirstOnboardingStep(
                step_id="invoke_synthetic_observation",
                label="Invoke disposable observation",
                proof="Synthetic page event produces an ephemeral receipt.",
                allowed_effects=["synthetic_observation", "ephemeral_receipt"],
                blocked_effects=["real_screen_capture", "raw_ref_retention"],
                requires_user_action=True,
            ),
            ConsentFirstOnboardingStep(
                step_id="prove_masking",
                label="Prove masking",
                proof="Secret-looking fixture is redacted before any write.",
                allowed_effects=["redaction_preview"],
                blocked_effects=["secret_echo", "raw_payload_display"],
                requires_user_action=False,
            ),
            ConsentFirstOnboardingStep(
                step_id="create_candidate_memory",
                label="Create synthetic memory candidate",
                proof="Candidate is synthetic, scoped, and user-visible.",
                allowed_effects=["candidate_memory_preview"],
                blocked_effects=["private_durable_memory_write"],
                requires_user_action=True,
            ),
            ConsentFirstOnboardingStep(
                step_id="delete_candidate_memory",
                label="Delete candidate",
                proof="User can remove the candidate and see the tombstone receipt.",
                allowed_effects=["candidate_delete", "audit_tombstone"],
                blocked_effects=["silent_retention"],
                requires_user_action=True,
            ),
            ConsentFirstOnboardingStep(
                step_id="show_audit_receipt",
                label="Show audit receipt",
                proof="Final receipt explains what was seen, masked, stored, and deleted.",
                allowed_effects=["audit_receipt_preview"],
                blocked_effects=["external_effect"],
                requires_user_action=False,
            ),
        ]
    )


def transition(snapshot: ShadowPointerSnapshot, next_state: ShadowPointerState) -> ShadowPointerSnapshot:
    updates: dict[str, object] = {"state": next_state}
    if next_state == ShadowPointerState.OFF:
        updates.update(
            {
                "workstream_label": "Off",
                "seeing": [],
                "ignoring": [],
                "possible_memory": None,
                "possible_skill": None,
                "approval_reason": None,
            }
        )
    elif next_state == ShadowPointerState.PAUSED:
        updates.update(
            {
                "seeing": [],
                "possible_memory": None,
                "approval_reason": None,
            }
        )
    return snapshot.model_copy(update=updates)


def apply_control(
    snapshot: ShadowPointerSnapshot,
    command: ShadowPointerControlCommand,
) -> ShadowPointerControlReceipt:
    """Apply a user-visible Shadow Pointer control command."""

    requested_at = _ensure_utc(command.requested_at)
    receipt_id = f"shadow_receipt_{command.action.value}_{int(requested_at.timestamp())}"

    if command.action == ShadowPointerControlAction.STATUS:
        return ShadowPointerControlReceipt(
            receipt_id=receipt_id,
            action=command.action,
            resulting_snapshot=snapshot,
            observation_active=_observation_active(snapshot.state),
            memory_write_allowed=_memory_write_allowed(snapshot.state),
            audit_required=False,
            confirmation_observed=command.user_confirmed,
            safety_notes=["status is read-only"],
        )

    if command.action == ShadowPointerControlAction.PAUSE_OBSERVATION:
        paused = ShadowPointerSnapshot(
            state=ShadowPointerState.PAUSED,
            workstream_label=f"Paused for {command.duration_minutes} min",
            seeing=[],
            ignoring=["all observation until resume or timeout"],
            possible_memory=None,
            possible_skill=snapshot.possible_skill,
        )
        return ShadowPointerControlReceipt(
            receipt_id=receipt_id,
            action=command.action,
            resulting_snapshot=paused,
            observation_active=False,
            memory_write_allowed=False,
            audit_required=True,
            audit_action="pause_observation",
            confirmation_observed=command.user_confirmed,
            expires_at=_minutes_from(requested_at, command.duration_minutes),
            safety_notes=[
                "observation disabled",
                "memory writes blocked while paused",
            ],
        )

    if command.action == ShadowPointerControlAction.RESUME_OBSERVATION:
        resumed = ShadowPointerSnapshot(
            state=ShadowPointerState.OBSERVING,
            workstream_label="Observation resumed",
            seeing=snapshot.seeing or ["authorized apps"],
            ignoring=snapshot.ignoring,
            possible_memory=snapshot.possible_memory,
            possible_skill=snapshot.possible_skill,
        )
        return ShadowPointerControlReceipt(
            receipt_id=receipt_id,
            action=command.action,
            resulting_snapshot=resumed,
            observation_active=True,
            memory_write_allowed=True,
            audit_required=True,
            audit_action="resume_observation",
            confirmation_observed=command.user_confirmed,
            safety_notes=["observation resumed within current consent scope"],
        )

    if command.action == ShadowPointerControlAction.DELETE_RECENT:
        deleted = ShadowPointerSnapshot(
            state=ShadowPointerState.PRIVATE_MASKING,
            workstream_label="Recent observation deletion",
            seeing=[],
            ignoring=[f"last {command.delete_window_minutes} minutes"],
            possible_memory=None,
            possible_skill=snapshot.possible_skill,
        )
        return ShadowPointerControlReceipt(
            receipt_id=receipt_id,
            action=command.action,
            resulting_snapshot=deleted,
            observation_active=_observation_active(snapshot.state),
            memory_write_allowed=False,
            audit_required=True,
            audit_action="delete_recent_observation",
            confirmation_observed=command.user_confirmed,
            deleted_window_minutes=command.delete_window_minutes,
            safety_notes=[
                "raw and derived observations in the selected window must be deleted or tombstoned",
                "new memory writes are blocked until deletion completes",
            ],
        )

    if command.action == ShadowPointerControlAction.IGNORE_APP:
        app_name = (command.app_name or "").strip()
        seeing = [item for item in snapshot.seeing if item != app_name]
        ignoring = _append_unique(snapshot.ignoring, app_name)
        ignored = ShadowPointerSnapshot(
            state=ShadowPointerState.PRIVATE_MASKING,
            workstream_label=f"Ignoring {app_name}",
            seeing=seeing,
            ignoring=ignoring,
            possible_memory=snapshot.possible_memory,
            possible_skill=snapshot.possible_skill,
        )
        return ShadowPointerControlReceipt(
            receipt_id=receipt_id,
            action=command.action,
            resulting_snapshot=ignored,
            observation_active=_observation_active(snapshot.state),
            memory_write_allowed=False,
            audit_required=True,
            audit_action="ignore_app_observation",
            confirmation_observed=command.user_confirmed,
            affected_apps=[app_name],
            safety_notes=[
                "ignored app must be excluded from capture adapters",
                "memory writes from ignored app are blocked",
            ],
        )

    raise ValueError(f"unsupported Shadow Pointer control action: {command.action}")


def evaluate_pointing_proposal(
    snapshot: ShadowPointerSnapshot,
    proposal: ShadowPointerPointingProposal,
) -> ShadowPointerPointingReceipt:
    """Convert model-proposed coordinates into a display-only overlay receipt."""

    created_at = _ensure_utc(proposal.created_at)
    receipt_id = f"shadow_pointing_{proposal.proposal_id}_{int(created_at.timestamp())}"
    privileged_effects = _privileged_pointing_effects(proposal.requested_action)
    untrusted_source = proposal.source_trust in {
        SourceTrust.AGENT_INFERRED,
        SourceTrust.EXTERNAL_UNTRUSTED,
        SourceTrust.HOSTILE_UNTIL_SAFE,
    }
    blocking_notes = list(privileged_effects)
    if proposal.source_trust in {
        SourceTrust.EXTERNAL_UNTRUSTED,
        SourceTrust.HOSTILE_UNTIL_SAFE,
    }:
        blocking_notes.append("trusted_instruction_promotion")

    overlay = ShadowPointerSnapshot(
        state=ShadowPointerState.NEEDS_APPROVAL,
        workstream_label=snapshot.workstream_label,
        seeing=_append_unique(snapshot.seeing, f"pointer proposal: {proposal.target_label}"),
        ignoring=_append_unique(snapshot.ignoring, "model-proposed pointer is display-only"),
        possible_memory=snapshot.possible_memory,
        possible_skill=snapshot.possible_skill,
        approval_reason="Review model-proposed pointer before any action.",
    )
    return ShadowPointerPointingReceipt(
        receipt_id=receipt_id,
        proposal_id=proposal.proposal_id,
        resulting_snapshot=overlay,
        coordinate_space=proposal.coordinate_space,
        x=proposal.x,
        y=proposal.y,
        target_label=proposal.target_label,
        display_only=True,
        allowed_effects=["display_overlay"],
        blocked_effects=blocking_notes,
        requires_user_confirmation=True,
        observation_active=_observation_active(snapshot.state),
        proposal_memory_write_allowed=False,
        audit_required=True,
        audit_action="shadow_pointer_pointing_proposal",
        policy_refs=(SHADOW_POINTER_POINTING_POLICY_REF,),
        untrusted_source=untrusted_source,
        safety_notes=[
            "coordinates may be rendered as an overlay only",
            "model-proposed coordinates cannot click, type, drag, open URLs, or call tools",
            "durable memory writes require a separate governed memory proposal",
        ],
    )


def default_shadow_pointer_snapshot() -> ShadowPointerSnapshot:
    return ShadowPointerSnapshot(
        state=ShadowPointerState.OBSERVING,
        workstream_label="Debugging auth flow",
        seeing=["VS Code", "Terminal", "Chrome"],
        ignoring=["password fields", "private messages"],
        possible_memory="Auth bug reproduction flow",
        possible_skill="Frontend auth debugging",
    )


def _append_unique(values: list[str], value: str) -> list[str]:
    if value in values:
        return list(values)
    return [*values, value]


def _memory_write_allowed(state: ShadowPointerState) -> bool:
    return state not in {
        ShadowPointerState.OFF,
        ShadowPointerState.PAUSED,
        ShadowPointerState.PRIVATE_MASKING,
        ShadowPointerState.NEEDS_APPROVAL,
    }


def _observation_active(state: ShadowPointerState) -> bool:
    return state not in {ShadowPointerState.OFF, ShadowPointerState.PAUSED}


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _minutes_from(start: datetime, minutes: int | None) -> datetime | None:
    if minutes is None:
        return None
    return start + timedelta(minutes=minutes)


def _privileged_pointing_effects(action: ShadowPointerPointingAction) -> list[str]:
    if action in {
        ShadowPointerPointingAction.DISPLAY_OVERLAY,
        ShadowPointerPointingAction.HIGHLIGHT_ELEMENT,
    }:
        return []
    return [action.value]


_STATE_PRESENTATIONS: dict[ShadowPointerState, ShadowPointerStatePresentation] = {
    ShadowPointerState.OFF: ShadowPointerStatePresentation(
        state=ShadowPointerState.OFF,
        label="Observation Off",
        compact_label="Off",
        icon="power",
        tone="neutral",
        pointer_shape="hidden",
        peripheral_cue="no halo",
        allowed_effects=["render_off_badge"],
        blocked_effects=["capture", "memory_write"],
    ),
    ShadowPointerState.OBSERVING: ShadowPointerStatePresentation(
        state=ShadowPointerState.OBSERVING,
        label="Observing With Consent",
        compact_label="Observing",
        icon="eye",
        tone="healthy",
        pointer_shape="soft_ring",
        peripheral_cue="steady halo",
        allowed_effects=["render_pointer", "show_receipt"],
        blocked_effects=["raw_ref_retention_without_policy"],
    ),
    ShadowPointerState.PRIVATE_MASKING: ShadowPointerStatePresentation(
        state=ShadowPointerState.PRIVATE_MASKING,
        label="Private Masking",
        compact_label="Masking",
        icon="shield",
        tone="warning",
        pointer_shape="shield_ring",
        peripheral_cue="amber shield pulse",
        allowed_effects=["render_masking_state", "show_blocked_sources"],
        blocked_effects=["memory_write", "raw_ref_retention"],
    ),
    ShadowPointerState.SEGMENTING: ShadowPointerStatePresentation(
        state=ShadowPointerState.SEGMENTING,
        label="Segmenting Workstream",
        compact_label="Segmenting",
        icon="route",
        tone="info",
        pointer_shape="dotted_ring",
        peripheral_cue="slow dotted sweep",
        allowed_effects=["render_pointer", "show_workstream_label"],
        blocked_effects=["durable_skill_promotion"],
    ),
    ShadowPointerState.REMEMBERING: ShadowPointerStatePresentation(
        state=ShadowPointerState.REMEMBERING,
        label="Memory Candidate",
        compact_label="Remembering",
        icon="archive",
        tone="info",
        pointer_shape="small_badge",
        peripheral_cue="brief save glint",
        allowed_effects=["render_pointer", "show_memory_candidate"],
        blocked_effects=["unreviewed_private_write"],
    ),
    ShadowPointerState.LEARNING_SKILL: ShadowPointerStatePresentation(
        state=ShadowPointerState.LEARNING_SKILL,
        label="Skill Candidate",
        compact_label="Learning Skill",
        icon="spark",
        tone="info",
        pointer_shape="small_badge",
        peripheral_cue="brief pattern pulse",
        allowed_effects=["render_pointer", "show_skill_candidate"],
        blocked_effects=["autonomy_promotion_without_review"],
    ),
    ShadowPointerState.AGENT_CONTEXTING: ShadowPointerStatePresentation(
        state=ShadowPointerState.AGENT_CONTEXTING,
        label="Agent Contexting",
        compact_label="Contexting",
        icon="package",
        tone="info",
        pointer_shape="ring_with_dot",
        peripheral_cue="blue context pulse",
        allowed_effects=["render_pointer", "show_context_receipt"],
        blocked_effects=["raw_context_dump"],
    ),
    ShadowPointerState.AGENT_ACTING: ShadowPointerStatePresentation(
        state=ShadowPointerState.AGENT_ACTING,
        label="Agent Action Pending",
        compact_label="Acting",
        icon="cursor",
        tone="danger",
        pointer_shape="attention_ring",
        peripheral_cue="red approval pulse",
        allowed_effects=["render_pointer", "show_action_receipt"],
        blocked_effects=["privileged_action_without_confirmation"],
    ),
    ShadowPointerState.NEEDS_APPROVAL: ShadowPointerStatePresentation(
        state=ShadowPointerState.NEEDS_APPROVAL,
        label="Needs Approval",
        compact_label="Approval",
        icon="hand",
        tone="warning",
        pointer_shape="attention_ring",
        peripheral_cue="amber approval pulse",
        allowed_effects=["render_pointer", "show_approval_receipt"],
        blocked_effects=["privileged_action_without_confirmation"],
    ),
    ShadowPointerState.PAUSED: ShadowPointerStatePresentation(
        state=ShadowPointerState.PAUSED,
        label="Observation Paused",
        compact_label="Paused",
        icon="pause",
        tone="neutral",
        pointer_shape="muted_ring",
        peripheral_cue="dimmed halo",
        allowed_effects=["render_pause_badge"],
        blocked_effects=["capture", "memory_write"],
    ),
}
