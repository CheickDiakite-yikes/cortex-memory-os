"""Consent-first controls for moving Cortex toward real local capture."""

from __future__ import annotations

import argparse
import json
import tempfile
from datetime import UTC, datetime, timedelta
from enum import Enum
from pathlib import Path

from pydantic import Field, model_validator

from cortex_memory_os.contracts import ScopeLevel, StrictModel
from cortex_memory_os.native_cursor_follow import (
    NativeCursorFollowSmokeResult,
    build_fixture_native_cursor_follow_smoke_result,
)
from cortex_memory_os.native_permission_smoke import NativePermissionSmokeResult

REAL_CAPTURE_INTENT_ID = "REAL-CAPTURE-INTENT-001"
REAL_CAPTURE_INTENT_POLICY_REF = "policy_real_capture_intent_v1"
REAL_CAPTURE_READINESS_ID = "REAL-CAPTURE-READINESS-001"
REAL_CAPTURE_READINESS_POLICY_REF = "policy_real_capture_readiness_v1"
REAL_CAPTURE_SENSITIVE_APP_FILTER_ID = "REAL-CAPTURE-SENSITIVE-APP-FILTER-001"
REAL_CAPTURE_SENSITIVE_APP_FILTER_POLICY_REF = "policy_real_capture_sensitive_app_filter_v1"
REAL_CAPTURE_SESSION_PLAN_ID = "REAL-CAPTURE-SESSION-PLAN-001"
REAL_CAPTURE_SESSION_PLAN_POLICY_REF = "policy_real_capture_session_plan_v1"
REAL_CAPTURE_START_RECEIPT_ID = "REAL-CAPTURE-START-RECEIPT-001"
REAL_CAPTURE_START_RECEIPT_POLICY_REF = "policy_real_capture_start_receipt_v1"
REAL_CAPTURE_STOP_RECEIPT_ID = "REAL-CAPTURE-STOP-RECEIPT-001"
REAL_CAPTURE_STOP_RECEIPT_POLICY_REF = "policy_real_capture_stop_receipt_v1"
REAL_CAPTURE_EPHEMERAL_RAW_REF_ID = "REAL-CAPTURE-EPHEMERAL-RAW-REF-001"
REAL_CAPTURE_EPHEMERAL_RAW_REF_POLICY_REF = "policy_real_capture_ephemeral_raw_ref_v1"
REAL_CAPTURE_OBSERVATION_SAMPLER_ID = "REAL-CAPTURE-OBSERVATION-SAMPLER-001"
REAL_CAPTURE_OBSERVATION_SAMPLER_POLICY_REF = "policy_real_capture_observation_sampler_v1"
DASHBOARD_CAPTURE_CONTROL_ID = "DASHBOARD-CAPTURE-CONTROL-001"
DASHBOARD_CAPTURE_CONTROL_POLICY_REF = "policy_dashboard_capture_control_v1"

DEFAULT_SENSITIVE_BUNDLE_IDS = {
    "com.apple.keychainaccess",
    "com.apple.MobileSMS",
    "com.apple.mail",
    "com.apple.Passwords",
    "com.1password.1password",
    "com.agilebits.onepassword7",
}


class CaptureControlState(str, Enum):
    OFF = "off"
    NEEDS_APPROVAL = "needs_approval"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"


class CaptureStorageMode(str, Enum):
    NONE = "none"
    EPHEMERAL_ONLY = "ephemeral_only"


class RealCaptureIntent(StrictModel):
    intent_id: str = REAL_CAPTURE_INTENT_ID
    policy_ref: str = REAL_CAPTURE_INTENT_POLICY_REF
    user_clicked_start: bool
    confirmation_text: str = Field(min_length=1)
    capture_scope: ScopeLevel = ScopeLevel.SESSION_ONLY
    cursor_overlay_requested: bool = True
    screen_capture_requested: bool = True
    accessibility_requested: bool = True
    storage_mode: CaptureStorageMode = CaptureStorageMode.EPHEMERAL_ONLY
    durable_memory_writes_requested: bool = False
    external_effects_requested: bool = False

    @model_validator(mode="after")
    def require_explicit_intent_without_privilege_expansion(self) -> "RealCaptureIntent":
        if self.policy_ref != REAL_CAPTURE_INTENT_POLICY_REF:
            raise ValueError("real capture intent policy mismatch")
        if not self.user_clicked_start:
            raise ValueError("real capture requires explicit button click")
        if self.confirmation_text != "Turn on Cortex observation":
            raise ValueError("real capture requires exact confirmation text")
        if not self.cursor_overlay_requested:
            raise ValueError("real capture milestone requires visible cursor overlay")
        if self.storage_mode != CaptureStorageMode.EPHEMERAL_ONLY:
            raise ValueError("real capture starts with ephemeral raw refs only")
        if self.durable_memory_writes_requested or self.external_effects_requested:
            raise ValueError("real capture intent cannot request memory writes or external effects")
        return self


class SensitiveAppDecision(StrictModel):
    app_name: str
    bundle_id: str
    allowed_for_capture: bool
    window_title_allowed: bool
    reason: str


class SensitiveAppFilterResult(StrictModel):
    filter_id: str = REAL_CAPTURE_SENSITIVE_APP_FILTER_ID
    policy_ref: str = REAL_CAPTURE_SENSITIVE_APP_FILTER_POLICY_REF
    decisions: list[SensitiveAppDecision] = Field(min_length=1)
    default_deny_unknown_private_apps: bool = True
    raw_content_allowed: bool = False
    passed: bool

    @model_validator(mode="after")
    def enforce_sensitive_app_defaults(self) -> "SensitiveAppFilterResult":
        if self.policy_ref != REAL_CAPTURE_SENSITIVE_APP_FILTER_POLICY_REF:
            raise ValueError("sensitive app filter policy mismatch")
        if self.raw_content_allowed:
            raise ValueError("sensitive app filter cannot allow raw content")
        if not any(not decision.allowed_for_capture for decision in self.decisions):
            raise ValueError("sensitive app filter must block at least one sensitive app")
        return self


class RealCaptureReadinessReceipt(StrictModel):
    readiness_id: str = REAL_CAPTURE_READINESS_ID
    policy_ref: str = REAL_CAPTURE_READINESS_POLICY_REF
    checked_at: datetime
    screen_recording_ready: bool
    accessibility_ready: bool
    native_cursor_follow_ready: bool
    can_start_cursor_overlay: bool
    can_start_screen_capture: bool
    missing_permissions: list[str] = Field(default_factory=list)
    raw_storage_mode: CaptureStorageMode = CaptureStorageMode.EPHEMERAL_ONLY
    durable_memory_write_allowed: bool = False
    passed: bool

    @model_validator(mode="after")
    def enforce_readiness_boundaries(self) -> "RealCaptureReadinessReceipt":
        if self.policy_ref != REAL_CAPTURE_READINESS_POLICY_REF:
            raise ValueError("real capture readiness policy mismatch")
        if self.durable_memory_write_allowed:
            raise ValueError("readiness cannot allow durable memory writes")
        if self.raw_storage_mode != CaptureStorageMode.EPHEMERAL_ONLY:
            raise ValueError("readiness raw storage must be ephemeral")
        if self.can_start_screen_capture and (
            not self.screen_recording_ready or not self.accessibility_ready
        ):
            raise ValueError("screen capture cannot start without both native permissions")
        return self


class RealCaptureSessionPlan(StrictModel):
    plan_id: str = REAL_CAPTURE_SESSION_PLAN_ID
    policy_ref: str = REAL_CAPTURE_SESSION_PLAN_POLICY_REF
    session_id: str = Field(min_length=1)
    state: CaptureControlState
    intent: RealCaptureIntent
    readiness: RealCaptureReadinessReceipt
    sensitive_filter: SensitiveAppFilterResult
    max_duration_minutes: int = Field(ge=1, le=120)
    cursor_overlay_command: str = Field(min_length=1)
    raw_storage_mode: CaptureStorageMode = CaptureStorageMode.EPHEMERAL_ONLY
    memory_writes_enabled: bool = False
    external_effects_enabled: bool = False
    raw_screen_storage_enabled: bool = False

    @model_validator(mode="after")
    def keep_session_plan_conservative(self) -> "RealCaptureSessionPlan":
        if self.policy_ref != REAL_CAPTURE_SESSION_PLAN_POLICY_REF:
            raise ValueError("real capture session plan policy mismatch")
        if self.memory_writes_enabled or self.external_effects_enabled:
            raise ValueError("real capture session plan cannot enable memory writes or external effects")
        if self.raw_screen_storage_enabled:
            raise ValueError("real capture session plan cannot enable durable raw screen storage")
        if self.state == CaptureControlState.READY and not self.readiness.can_start_cursor_overlay:
            raise ValueError("ready session requires cursor overlay readiness")
        return self


class CaptureLifecycleReceipt(StrictModel):
    receipt_id: str
    policy_ref: str
    session_id: str
    state: CaptureControlState
    observation_active: bool
    cursor_overlay_running: bool
    screen_capture_running: bool
    accessibility_observer_running: bool
    raw_screen_storage_enabled: bool
    memory_write_allowed: bool
    confirmation_observed: bool
    audit_action: str = Field(min_length=1)
    safety_notes: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def enforce_lifecycle_receipt_safety(self) -> "CaptureLifecycleReceipt":
        if self.raw_screen_storage_enabled or self.memory_write_allowed:
            raise ValueError("capture lifecycle receipt cannot enable raw storage or memory writes")
        if self.screen_capture_running and not self.confirmation_observed:
            raise ValueError("screen capture requires observed confirmation")
        return self


class EphemeralRawRefPolicy(StrictModel):
    policy_id: str = REAL_CAPTURE_EPHEMERAL_RAW_REF_ID
    policy_ref: str = REAL_CAPTURE_EPHEMERAL_RAW_REF_POLICY_REF
    storage_root: str
    ttl_seconds: int = Field(ge=30, le=21_600)
    auto_delete_at: datetime
    durable_storage_allowed: bool = False
    memory_write_allowed_from_raw: bool = False
    raw_ref_prefix: str = "tmp://cortex/raw/"

    @model_validator(mode="after")
    def enforce_ephemeral_raw_refs(self) -> "EphemeralRawRefPolicy":
        if self.policy_ref != REAL_CAPTURE_EPHEMERAL_RAW_REF_POLICY_REF:
            raise ValueError("ephemeral raw-ref policy mismatch")
        if self.durable_storage_allowed or self.memory_write_allowed_from_raw:
            raise ValueError("ephemeral raw refs cannot allow durable storage or memory writes")
        if not self.storage_root.startswith(tempfile.gettempdir()):
            raise ValueError("ephemeral raw refs must live under the system temp directory")
        return self


class ObservationSamplerPlan(StrictModel):
    sampler_id: str = REAL_CAPTURE_OBSERVATION_SAMPLER_ID
    policy_ref: str = REAL_CAPTURE_OBSERVATION_SAMPLER_POLICY_REF
    sample_interval_ms: int = Field(ge=250, le=10_000)
    max_events_per_minute: int = Field(ge=1, le=120)
    output_shape: str = "count_only_receipts"
    include_window_titles: bool = False
    include_raw_pixels: bool = False
    include_accessibility_values: bool = False
    prompt_injection_screening_required: bool = True

    @model_validator(mode="after")
    def keep_sampler_metadata_only(self) -> "ObservationSamplerPlan":
        if self.policy_ref != REAL_CAPTURE_OBSERVATION_SAMPLER_POLICY_REF:
            raise ValueError("observation sampler policy mismatch")
        if self.output_shape != "count_only_receipts":
            raise ValueError("observation sampler starts as count-only receipts")
        if self.include_window_titles or self.include_raw_pixels or self.include_accessibility_values:
            raise ValueError("observation sampler cannot include raw or private values by default")
        if not self.prompt_injection_screening_required:
            raise ValueError("observation sampler requires prompt-injection screening")
        return self


class DashboardCaptureControlPanel(StrictModel):
    panel_id: str = DASHBOARD_CAPTURE_CONTROL_ID
    policy_ref: str = DASHBOARD_CAPTURE_CONTROL_POLICY_REF
    state: CaptureControlState
    primary_button_label: str
    stop_button_label: str
    native_cursor_command: str
    local_only: bool = True
    requires_confirmation: bool = True
    shows_shadow_clicker_status: bool = True
    starts_from_static_dashboard: bool = False
    raw_payload_returned: bool = False
    mutation_enabled: bool = False

    @model_validator(mode="after")
    def keep_dashboard_control_honest(self) -> "DashboardCaptureControlPanel":
        if self.policy_ref != DASHBOARD_CAPTURE_CONTROL_POLICY_REF:
            raise ValueError("dashboard capture control policy mismatch")
        if not self.local_only or not self.requires_confirmation:
            raise ValueError("dashboard capture control must stay local and confirmation-gated")
        if self.starts_from_static_dashboard:
            raise ValueError("static dashboard cannot claim to start native capture directly")
        if self.raw_payload_returned or self.mutation_enabled:
            raise ValueError("dashboard capture control cannot return raw payloads or mutations")
        return self


class RealCaptureControlBundle(StrictModel):
    generated_at: datetime
    intent: RealCaptureIntent
    readiness: RealCaptureReadinessReceipt
    sensitive_filter: SensitiveAppFilterResult
    session_plan: RealCaptureSessionPlan
    start_receipt: CaptureLifecycleReceipt
    stop_receipt: CaptureLifecycleReceipt
    ephemeral_raw_ref_policy: EphemeralRawRefPolicy
    sampler_plan: ObservationSamplerPlan
    native_cursor_follow: NativeCursorFollowSmokeResult
    dashboard_panel: DashboardCaptureControlPanel
    passed: bool


def build_real_capture_intent() -> RealCaptureIntent:
    return RealCaptureIntent(
        user_clicked_start=True,
        confirmation_text="Turn on Cortex observation",
    )


def build_sensitive_app_filter_result() -> SensitiveAppFilterResult:
    decisions = [
        classify_capture_app("VS Code", "com.microsoft.VSCode"),
        classify_capture_app("Messages", "com.apple.MobileSMS"),
        classify_capture_app("1Password", "com.1password.1password"),
    ]
    return SensitiveAppFilterResult(
        decisions=decisions,
        passed=any(decision.allowed_for_capture for decision in decisions)
        and any(not decision.allowed_for_capture for decision in decisions),
    )


def classify_capture_app(app_name: str, bundle_id: str) -> SensitiveAppDecision:
    blocked = bundle_id in DEFAULT_SENSITIVE_BUNDLE_IDS
    return SensitiveAppDecision(
        app_name=app_name,
        bundle_id=bundle_id,
        allowed_for_capture=not blocked,
        window_title_allowed=not blocked,
        reason="sensitive_app_blocked" if blocked else "allowed_by_default_safe_fixture",
    )


def build_real_capture_readiness(
    permission_smoke: NativePermissionSmokeResult,
    native_cursor_follow: NativeCursorFollowSmokeResult,
    *,
    now: datetime | None = None,
) -> RealCaptureReadinessReceipt:
    missing = []
    if not permission_smoke.screen_recording_preflight:
        missing.append("screen_recording")
    if not permission_smoke.accessibility_trusted:
        missing.append("accessibility")
    can_start_screen_capture = not missing
    return RealCaptureReadinessReceipt(
        checked_at=_timestamp(now),
        screen_recording_ready=permission_smoke.screen_recording_preflight,
        accessibility_ready=permission_smoke.accessibility_trusted,
        native_cursor_follow_ready=native_cursor_follow.passed,
        can_start_cursor_overlay=native_cursor_follow.passed,
        can_start_screen_capture=can_start_screen_capture,
        missing_permissions=missing,
        passed=native_cursor_follow.passed,
    )


def build_real_capture_session_plan(
    intent: RealCaptureIntent,
    readiness: RealCaptureReadinessReceipt,
    sensitive_filter: SensitiveAppFilterResult,
) -> RealCaptureSessionPlan:
    return RealCaptureSessionPlan(
        session_id="capture_session_local_001",
        state=CaptureControlState.READY
        if readiness.can_start_cursor_overlay
        else CaptureControlState.NEEDS_APPROVAL,
        intent=intent,
        readiness=readiness,
        sensitive_filter=sensitive_filter,
        max_duration_minutes=30,
        cursor_overlay_command=(
            "swift run --package-path native/macos-shadow-pointer "
            "cortex-shadow-clicker --duration 30"
        ),
    )


def build_capture_start_receipt(plan: RealCaptureSessionPlan) -> CaptureLifecycleReceipt:
    return CaptureLifecycleReceipt(
        receipt_id=REAL_CAPTURE_START_RECEIPT_ID,
        policy_ref=REAL_CAPTURE_START_RECEIPT_POLICY_REF,
        session_id=plan.session_id,
        state=CaptureControlState.RUNNING,
        observation_active=True,
        cursor_overlay_running=True,
        screen_capture_running=plan.readiness.can_start_screen_capture,
        accessibility_observer_running=plan.readiness.can_start_screen_capture,
        raw_screen_storage_enabled=False,
        memory_write_allowed=False,
        confirmation_observed=True,
        audit_action="start_consented_capture_session",
        safety_notes=[
            "Shadow Clicker overlay follows the cursor system-wide.",
            "Screen capture is permission-gated and raw storage remains disabled.",
            "Durable memory writes remain disabled until separate review.",
        ],
    )


def build_capture_stop_receipt(plan: RealCaptureSessionPlan) -> CaptureLifecycleReceipt:
    return CaptureLifecycleReceipt(
        receipt_id=REAL_CAPTURE_STOP_RECEIPT_ID,
        policy_ref=REAL_CAPTURE_STOP_RECEIPT_POLICY_REF,
        session_id=plan.session_id,
        state=CaptureControlState.STOPPED,
        observation_active=False,
        cursor_overlay_running=False,
        screen_capture_running=False,
        accessibility_observer_running=False,
        raw_screen_storage_enabled=False,
        memory_write_allowed=False,
        confirmation_observed=True,
        audit_action="stop_consented_capture_session",
        safety_notes=[
            "Observation stopped.",
            "Ephemeral refs expire or are deleted by policy.",
        ],
    )


def build_ephemeral_raw_ref_policy(*, now: datetime | None = None) -> EphemeralRawRefPolicy:
    timestamp = _timestamp(now)
    return EphemeralRawRefPolicy(
        storage_root=str(Path(tempfile.gettempdir()) / "cortex" / "raw_refs"),
        ttl_seconds=600,
        auto_delete_at=timestamp + timedelta(seconds=600),
    )


def build_observation_sampler_plan() -> ObservationSamplerPlan:
    return ObservationSamplerPlan(sample_interval_ms=1000, max_events_per_minute=60)


def build_dashboard_capture_control_panel(
    plan: RealCaptureSessionPlan,
) -> DashboardCaptureControlPanel:
    return DashboardCaptureControlPanel(
        state=plan.state,
        primary_button_label="Turn On Cortex",
        stop_button_label="Stop Observation",
        native_cursor_command=plan.cursor_overlay_command,
    )


def build_real_capture_control_bundle(
    *,
    permission_smoke: NativePermissionSmokeResult,
    native_cursor_follow: NativeCursorFollowSmokeResult | None = None,
    now: datetime | None = None,
) -> RealCaptureControlBundle:
    timestamp = _timestamp(now)
    native_cursor = native_cursor_follow or build_fixture_native_cursor_follow_smoke_result(
        checked_at=timestamp
    )
    intent = build_real_capture_intent()
    readiness = build_real_capture_readiness(
        permission_smoke,
        native_cursor,
        now=timestamp,
    )
    sensitive_filter = build_sensitive_app_filter_result()
    session_plan = build_real_capture_session_plan(intent, readiness, sensitive_filter)
    start_receipt = build_capture_start_receipt(session_plan)
    stop_receipt = build_capture_stop_receipt(session_plan)
    raw_ref_policy = build_ephemeral_raw_ref_policy(now=timestamp)
    sampler = build_observation_sampler_plan()
    dashboard = build_dashboard_capture_control_panel(session_plan)
    passed = all(
        [
            intent.user_clicked_start,
            readiness.can_start_cursor_overlay,
            sensitive_filter.passed,
            not session_plan.memory_writes_enabled,
            start_receipt.cursor_overlay_running,
            not start_receipt.raw_screen_storage_enabled,
            not stop_receipt.observation_active,
            not raw_ref_policy.durable_storage_allowed,
            sampler.output_shape == "count_only_receipts",
            native_cursor.passed,
            dashboard.shows_shadow_clicker_status,
        ]
    )
    return RealCaptureControlBundle(
        generated_at=timestamp,
        intent=intent,
        readiness=readiness,
        sensitive_filter=sensitive_filter,
        session_plan=session_plan,
        start_receipt=start_receipt,
        stop_receipt=stop_receipt,
        ephemeral_raw_ref_policy=raw_ref_policy,
        sampler_plan=sampler,
        native_cursor_follow=native_cursor,
        dashboard_panel=dashboard,
        passed=passed,
    )


def _timestamp(now: datetime | None) -> datetime:
    timestamp = now or datetime.now(UTC)
    if timestamp.tzinfo is None:
        return timestamp.replace(tzinfo=UTC)
    return timestamp.astimezone(UTC)


def main(argv: list[str] | None = None) -> int:
    from cortex_memory_os.native_permission_smoke import build_fixture_permission_smoke_result

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    bundle = build_real_capture_control_bundle(
        permission_smoke=build_fixture_permission_smoke_result(
            screen_recording_preflight=True,
            accessibility_trusted=True,
        )
    )
    if args.json:
        print(json.dumps(bundle.model_dump(mode="json"), indent=2, sort_keys=True))
    else:
        print(
            f"{REAL_CAPTURE_SESSION_PLAN_ID}: passed={bundle.passed}; "
            f"state={bundle.session_plan.state.value}"
        )
    return 0 if bundle.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
