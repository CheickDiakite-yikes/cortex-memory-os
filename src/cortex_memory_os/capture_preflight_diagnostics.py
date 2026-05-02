"""Prompt-free capture preflight diagnostics and permission guidance."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

from pydantic import Field, model_validator

from cortex_memory_os.contracts import StrictModel
from cortex_memory_os.native_permission_smoke import (
    NativePermissionSmokeResult,
    build_fixture_permission_smoke_result,
    run_native_permission_smoke,
)
from cortex_memory_os.native_screen_capture_probe import (
    NATIVE_SCREEN_CAPTURE_PROBE_ID,
    NATIVE_SCREEN_CAPTURE_PROBE_POLICY_REF,
    NativeScreenCaptureProbeResult,
)

CAPTURE_PERMISSION_GUIDE_ID = "CAPTURE-PERMISSION-GUIDE-001"
CAPTURE_PERMISSION_GUIDE_POLICY_REF = "policy_capture_permission_guide_v1"
CAPTURE_PREFLIGHT_DIAGNOSTICS_ID = "CAPTURE-PREFLIGHT-DIAGNOSTICS-001"
CAPTURE_PREFLIGHT_DIAGNOSTICS_POLICY_REF = "policy_capture_preflight_diagnostics_v1"
SCREEN_PROBE_RESULT_UX_ID = "SCREEN-PROBE-RESULT-UX-001"
SCREEN_PROBE_RESULT_UX_POLICY_REF = "policy_screen_probe_result_ux_v1"
SCREEN_PROBE_SKIP_RECEIPT_ID = "SCREEN-PROBE-SKIP-RECEIPT-001"
SCREEN_PROBE_SKIP_RECEIPT_POLICY_REF = "policy_screen_probe_skip_receipt_v1"
SCREEN_PROBE_LIVE_CONTRACT_ID = "SCREEN-PROBE-LIVE-CONTRACT-001"
SCREEN_PROBE_LIVE_CONTRACT_POLICY_REF = "policy_screen_probe_live_contract_v1"
CAPTURE_CONTROL_REAL_PROBE_SMOKE_ID = "CAPTURE-CONTROL-REAL-PROBE-SMOKE-001"
CAPTURE_CONTROL_REAL_PROBE_SMOKE_POLICY_REF = "policy_capture_control_real_probe_smoke_v1"
REAL_CAPTURE_PERMISSION_ONBOARDING_UI_ID = "REAL-CAPTURE-PERMISSION-ONBOARDING-UI-001"
REAL_CAPTURE_PERMISSION_ONBOARDING_UI_POLICY_REF = (
    "policy_real_capture_permission_onboarding_ui_v1"
)
SCREEN_METADATA_STREAM_PLAN_ID = "SCREEN-METADATA-STREAM-PLAN-001"
SCREEN_METADATA_STREAM_PLAN_POLICY_REF = "policy_screen_metadata_stream_plan_v1"


class CapturePermissionGuide(StrictModel):
    guide_id: str = CAPTURE_PERMISSION_GUIDE_ID
    policy_ref: str = CAPTURE_PERMISSION_GUIDE_POLICY_REF
    host_process_label: str = Field(min_length=1)
    system_settings_pane: str = "System Settings > Privacy & Security"
    screen_recording_steps: list[str] = Field(min_length=1)
    accessibility_steps: list[str] = Field(min_length=1)
    restart_required: bool = True
    prompt_requested: bool = False
    capture_started: bool = False
    memory_write_allowed: bool = False
    raw_ref_retained: bool = False

    @model_validator(mode="after")
    def enforce_guide_boundary(self) -> "CapturePermissionGuide":
        if self.policy_ref != CAPTURE_PERMISSION_GUIDE_POLICY_REF:
            raise ValueError("capture permission guide policy mismatch")
        if self.prompt_requested or self.capture_started:
            raise ValueError("permission guide cannot prompt or start capture")
        if self.memory_write_allowed or self.raw_ref_retained:
            raise ValueError("permission guide cannot write memory or retain raw refs")
        joined = " ".join(self.screen_recording_steps + self.accessibility_steps)
        if "Screen Recording" not in joined or "Accessibility" not in joined:
            raise ValueError("permission guide must name Screen Recording and Accessibility")
        return self


class CapturePreflightDiagnostics(StrictModel):
    diagnostic_id: str = CAPTURE_PREFLIGHT_DIAGNOSTICS_ID
    policy_ref: str = CAPTURE_PREFLIGHT_DIAGNOSTICS_POLICY_REF
    checked_at: datetime
    host_pid: int = Field(ge=1)
    host_process_name: str = Field(min_length=1)
    executable_path: str = Field(min_length=1)
    app_permission_hint: str = Field(min_length=1)
    screen_recording_preflight: bool
    accessibility_trusted: bool
    safe_to_start_shadow_clicker: bool
    safe_to_attempt_metadata_probe: bool
    safe_to_start_real_capture_session: bool
    missing_permissions: list[str] = Field(default_factory=list)
    permission_guide: CapturePermissionGuide
    next_user_actions: list[str] = Field(default_factory=list)
    prompt_requested: bool = False
    capture_started: bool = False
    accessibility_observer_started: bool = False
    raw_payloads_included: bool = False
    raw_ref_retained: bool = False
    memory_write_allowed: bool = False
    passed: bool

    @model_validator(mode="after")
    def enforce_preflight_boundary(self) -> "CapturePreflightDiagnostics":
        if self.policy_ref != CAPTURE_PREFLIGHT_DIAGNOSTICS_POLICY_REF:
            raise ValueError("capture preflight diagnostics policy mismatch")
        expected_missing = []
        if not self.screen_recording_preflight:
            expected_missing.append("screen_recording")
        if not self.accessibility_trusted:
            expected_missing.append("accessibility")
        if sorted(self.missing_permissions) != sorted(expected_missing):
            raise ValueError("missing permission list does not match permission state")
        if self.safe_to_attempt_metadata_probe and not self.screen_recording_preflight:
            raise ValueError("metadata probe cannot be safe without Screen Recording preflight")
        if self.safe_to_start_real_capture_session and (
            not self.screen_recording_preflight or not self.accessibility_trusted
        ):
            raise ValueError("real capture session cannot be safe without both permissions")
        if (
            self.prompt_requested
            or self.capture_started
            or self.accessibility_observer_started
            or self.raw_payloads_included
            or self.raw_ref_retained
            or self.memory_write_allowed
        ):
            raise ValueError("preflight diagnostics must be prompt-free and read-only")
        if not self.next_user_actions:
            raise ValueError("preflight diagnostics must include user-facing next actions")
        return self


class ScreenProbeUXReceipt(StrictModel):
    ux_id: str = SCREEN_PROBE_RESULT_UX_ID
    policy_ref: str = SCREEN_PROBE_RESULT_UX_POLICY_REF
    source_probe_id: str = NATIVE_SCREEN_CAPTURE_PROBE_ID
    severity: str
    message: str = Field(min_length=1)
    blocked_by_permission: bool
    frame_captured: bool
    raw_pixels_returned: bool = False
    raw_ref_retained: bool = False
    memory_write_allowed: bool = False
    next_user_actions: list[str] = Field(default_factory=list)
    passed: bool

    @model_validator(mode="after")
    def enforce_ux_boundary(self) -> "ScreenProbeUXReceipt":
        if self.policy_ref != SCREEN_PROBE_RESULT_UX_POLICY_REF:
            raise ValueError("screen probe UX policy mismatch")
        if self.source_probe_id != NATIVE_SCREEN_CAPTURE_PROBE_ID:
            raise ValueError("screen probe UX source mismatch")
        if self.raw_pixels_returned or self.raw_ref_retained or self.memory_write_allowed:
            raise ValueError("screen probe UX cannot expose raw data or memory writes")
        if self.blocked_by_permission and not self.next_user_actions:
            raise ValueError("permission-blocked UX requires next actions")
        return self


class ScreenProbeSkipReceipt(StrictModel):
    skip_id: str = SCREEN_PROBE_SKIP_RECEIPT_ID
    policy_ref: str = SCREEN_PROBE_SKIP_RECEIPT_POLICY_REF
    source_probe_id: str = NATIVE_SCREEN_CAPTURE_PROBE_ID
    source_policy_ref: str = NATIVE_SCREEN_CAPTURE_PROBE_POLICY_REF
    reason: str = Field(min_length=1)
    allow_real_capture: bool
    screen_recording_preflight: bool
    capture_attempted: bool
    frame_captured: bool
    raw_pixels_returned: bool = False
    raw_ref_retained: bool = False
    memory_write_allowed: bool = False
    evidence_refs: list[str] = Field(default_factory=list)
    next_user_actions: list[str] = Field(default_factory=list)
    passed: bool

    @model_validator(mode="after")
    def enforce_skip_boundary(self) -> "ScreenProbeSkipReceipt":
        if self.policy_ref != SCREEN_PROBE_SKIP_RECEIPT_POLICY_REF:
            raise ValueError("screen probe skip receipt policy mismatch")
        if self.source_probe_id != NATIVE_SCREEN_CAPTURE_PROBE_ID:
            raise ValueError("screen probe skip source mismatch")
        if self.source_policy_ref != NATIVE_SCREEN_CAPTURE_PROBE_POLICY_REF:
            raise ValueError("screen probe skip source policy mismatch")
        if self.capture_attempted or self.frame_captured:
            raise ValueError("skip receipt cannot represent a captured frame")
        if self.raw_pixels_returned or self.raw_ref_retained or self.memory_write_allowed:
            raise ValueError("skip receipt cannot expose raw data or memory writes")
        if self.evidence_refs:
            raise ValueError("skip receipt cannot expose evidence refs")
        if self.reason == "screen_recording_preflight_false" and self.screen_recording_preflight:
            raise ValueError("screen recording skip reason conflicts with preflight state")
        if not self.next_user_actions:
            raise ValueError("skip receipt must include next user actions")
        return self


class ScreenMetadataStreamPlan(StrictModel):
    plan_id: str = SCREEN_METADATA_STREAM_PLAN_ID
    policy_ref: str = SCREEN_METADATA_STREAM_PLAN_POLICY_REF
    source_probe_id: str = NATIVE_SCREEN_CAPTURE_PROBE_ID
    token_required: bool = True
    screen_recording_preflight_required: bool = True
    output_shape: str = "metadata_count_receipts"
    sample_interval_ms: int = Field(default=1000, ge=250, le=10_000)
    max_events_per_minute: int = Field(default=60, ge=1, le=120)
    continuous_capture_allowed: bool = False
    raw_pixels_returned: bool = False
    raw_ref_retained: bool = False
    memory_write_allowed: bool = False
    blocked_effects: list[str] = Field(default_factory=list)
    passed: bool = True

    @model_validator(mode="after")
    def enforce_stream_plan_boundary(self) -> "ScreenMetadataStreamPlan":
        if self.policy_ref != SCREEN_METADATA_STREAM_PLAN_POLICY_REF:
            raise ValueError("screen metadata stream plan policy mismatch")
        if self.output_shape != "metadata_count_receipts":
            raise ValueError("metadata stream starts as count-only receipts")
        if (
            not self.token_required
            or not self.screen_recording_preflight_required
            or self.continuous_capture_allowed
            or self.raw_pixels_returned
            or self.raw_ref_retained
            or self.memory_write_allowed
        ):
            raise ValueError("metadata stream plan cannot enable capture side effects")
        required = {"continuous_capture", "raw_pixel_return", "raw_ref_retention", "memory_write"}
        if missing := sorted(required.difference(self.blocked_effects)):
            raise ValueError(f"metadata stream plan missing blocked effects: {missing}")
        return self


def build_capture_permission_guide(
    *,
    host_process_label: str,
) -> CapturePermissionGuide:
    return CapturePermissionGuide(
        host_process_label=host_process_label,
        screen_recording_steps=[
            "Open System Settings > Privacy & Security > Screen Recording.",
            f"Enable Screen Recording for {host_process_label}.",
            "Quit and reopen the hosting app, then run Check Permissions again.",
        ],
        accessibility_steps=[
            "Open System Settings > Privacy & Security > Accessibility.",
            f"Enable Accessibility for {host_process_label} only when cursor or app metadata needs it.",
            "Quit and reopen the hosting app before starting observation.",
        ],
    )


def build_capture_preflight_diagnostics(
    permission_smoke: NativePermissionSmokeResult,
    *,
    checked_at: datetime | None = None,
    host_pid: int | None = None,
    executable_path: str | None = None,
) -> CapturePreflightDiagnostics:
    executable = executable_path or sys.executable
    process_name = Path(executable).name or "python"
    hint = (
        "Grant permissions to the macOS app that launched this bridge "
        f"({process_name}); if running from Codex Desktop, grant Codex."
    )
    missing = []
    actions = []
    if not permission_smoke.screen_recording_preflight:
        missing.append("screen_recording")
        actions.append("Enable Screen Recording for the hosting app, then restart it.")
    if not permission_smoke.accessibility_trusted:
        missing.append("accessibility")
        actions.append("Enable Accessibility for the hosting app before app/action observation.")
    if not actions:
        actions.append("Permissions are ready; use Screen Probe for one metadata-only frame.")
    label = "Codex or " + process_name if process_name != "Codex" else "Codex"
    return CapturePreflightDiagnostics(
        checked_at=checked_at or datetime.now(UTC),
        host_pid=host_pid or os.getpid(),
        host_process_name=process_name,
        executable_path=executable,
        app_permission_hint=hint,
        screen_recording_preflight=permission_smoke.screen_recording_preflight,
        accessibility_trusted=permission_smoke.accessibility_trusted,
        safe_to_start_shadow_clicker=True,
        safe_to_attempt_metadata_probe=permission_smoke.screen_recording_preflight,
        safe_to_start_real_capture_session=(
            permission_smoke.screen_recording_preflight and permission_smoke.accessibility_trusted
        ),
        missing_permissions=missing,
        permission_guide=build_capture_permission_guide(host_process_label=label),
        next_user_actions=actions,
        prompt_requested=False,
        capture_started=False,
        accessibility_observer_started=False,
        raw_payloads_included=False,
        raw_ref_retained=False,
        memory_write_allowed=False,
        passed=permission_smoke.passed,
    )


def build_screen_probe_skip_receipt(
    result: NativeScreenCaptureProbeResult,
) -> ScreenProbeSkipReceipt | None:
    if result.frame_captured:
        return None
    reason = result.skip_reason or _infer_screen_probe_skip_reason(result)
    return ScreenProbeSkipReceipt(
        reason=reason,
        allow_real_capture=result.allow_real_capture,
        screen_recording_preflight=result.screen_recording_preflight,
        capture_attempted=result.capture_attempted,
        frame_captured=result.frame_captured,
        raw_pixels_returned=result.raw_pixels_returned,
        raw_ref_retained=result.raw_ref_retained,
        memory_write_allowed=result.memory_write_allowed,
        evidence_refs=result.evidence_refs,
        next_user_actions=result.next_user_actions
        or _screen_probe_next_actions(reason),
        passed=result.passed,
    )


def build_screen_probe_ux_receipt(
    result: NativeScreenCaptureProbeResult,
) -> ScreenProbeUXReceipt:
    if result.frame_captured:
        message = (
            f"Screen probe captured one in-memory metadata frame "
            f"({result.frame_width}x{result.frame_height}); no pixels, raw refs, or memories returned."
        )
        return ScreenProbeUXReceipt(
            severity="ok",
            message=message,
            blocked_by_permission=False,
            frame_captured=True,
            next_user_actions=["Stop observation when done; memory writes are still disabled."],
            passed=result.passed,
        )
    reason = result.skip_reason or _infer_screen_probe_skip_reason(result)
    blocked = reason == "screen_recording_preflight_false"
    message = (
        "Screen probe skipped because Screen Recording permission is not granted."
        if blocked
        else "Screen probe skipped before any frame was captured."
    )
    return ScreenProbeUXReceipt(
        severity="blocked" if blocked else "info",
        message=message,
        blocked_by_permission=blocked,
        frame_captured=False,
        next_user_actions=result.next_user_actions or _screen_probe_next_actions(reason),
        passed=result.passed,
    )


def build_screen_metadata_stream_plan() -> ScreenMetadataStreamPlan:
    return ScreenMetadataStreamPlan(
        blocked_effects=[
            "continuous_capture",
            "raw_pixel_return",
            "raw_ref_retention",
            "memory_write",
            "accessibility_values",
            "window_titles",
        ]
    )


def _infer_screen_probe_skip_reason(result: NativeScreenCaptureProbeResult) -> str:
    if not result.allow_real_capture:
        return "allow_real_capture_false"
    if not result.screen_recording_preflight:
        return "screen_recording_preflight_false"
    return "frame_metadata_unavailable"


def _screen_probe_next_actions(reason: str) -> list[str]:
    if reason == "screen_recording_preflight_false":
        return [
            "Enable Screen Recording for the hosting app.",
            "Restart the hosting app and run Check Permissions again.",
        ]
    if reason == "allow_real_capture_false":
        return ["Use the dashboard Screen Probe button or pass --allow-real-capture explicitly."]
    return ["Run Check Permissions, then retry Screen Probe."]


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--fixture", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    permission = (
        build_fixture_permission_smoke_result()
        if args.fixture
        else run_native_permission_smoke()
    )
    result = build_capture_preflight_diagnostics(permission)
    if args.json:
        print(json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True))
    else:
        print(
            f"{CAPTURE_PREFLIGHT_DIAGNOSTICS_ID}: passed={result.passed}; "
            f"missing={','.join(result.missing_permissions) or 'none'}"
        )
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
