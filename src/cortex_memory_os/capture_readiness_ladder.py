"""Ten-step dashboard ladder for safe real-capture readiness."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from typing import Literal

from pydantic import Field, model_validator

from cortex_memory_os.capture_control_server import (
    CaptureControlReceiptSummary,
)
from cortex_memory_os.capture_preflight_diagnostics import (
    CapturePreflightDiagnostics,
    ScreenMetadataStreamPlan,
    ScreenProbeSkipReceipt,
    ScreenProbeUXReceipt,
    build_capture_preflight_diagnostics,
    build_screen_metadata_stream_plan,
    build_screen_probe_skip_receipt,
    build_screen_probe_ux_receipt,
)
from cortex_memory_os.contracts import StrictModel
from cortex_memory_os.native_permission_smoke import (
    build_fixture_permission_smoke_result,
)
from cortex_memory_os.native_screen_capture_probe import (
    NativeScreenCaptureProbeResult,
    build_fixture_native_screen_capture_probe_result,
)
from cortex_memory_os.real_capture_control import (
    RealCaptureControlBundle,
    build_real_capture_control_bundle,
)
from cortex_memory_os.real_capture_hardening import (
    RawRefScavengerReceipt,
    RealCaptureNextGatePlan,
    RAW_REF_SCAVENGER_POLICY_REF,
    build_real_capture_next_gate_plan,
    run_raw_ref_scavenger,
)

CAPTURE_READINESS_LADDER_ID = "CAPTURE-READINESS-LADDER-001"
CAPTURE_READINESS_LADDER_POLICY_REF = "policy_capture_readiness_ladder_v1"

LadderStepStatus = Literal["ready", "blocked", "planned", "watching"]


class CaptureReadinessLadderStep(StrictModel):
    step_id: str = Field(min_length=1)
    order: int = Field(ge=1, le=10)
    label: str = Field(min_length=1)
    surface: str = Field(min_length=1)
    status: LadderStepStatus
    proof: str = Field(min_length=1)
    next_action: str = Field(min_length=1)
    safety_note: str = Field(min_length=1)
    command: str | None = None
    raw_payloads_included: bool = False
    raw_ref_retained: bool = False
    memory_write_allowed: bool = False
    external_effect_enabled: bool = False

    @model_validator(mode="after")
    def enforce_step_safety(self) -> "CaptureReadinessLadderStep":
        if (
            self.raw_payloads_included
            or self.raw_ref_retained
            or self.memory_write_allowed
            or self.external_effect_enabled
        ):
            raise ValueError("capture ladder steps cannot expose raw data or side effects")
        return self


class CaptureReadinessLadderPanel(StrictModel):
    ladder_id: str = CAPTURE_READINESS_LADDER_ID
    policy_ref: str = CAPTURE_READINESS_LADDER_POLICY_REF
    title: str = "Real Capture Readiness Ladder"
    summary: str = Field(min_length=1)
    generated_at: datetime
    steps: list[CaptureReadinessLadderStep] = Field(min_length=10, max_length=10)
    ready_count: int = Field(ge=0, le=10)
    blocked_count: int = Field(ge=0, le=10)
    planned_count: int = Field(ge=0, le=10)
    watching_count: int = Field(ge=0, le=10)
    next_step_label: str = Field(min_length=1)
    can_demo_now: bool
    can_probe_now: bool
    can_real_capture_now: bool
    display_only: bool = True
    raw_payloads_included: bool = False
    raw_ref_retained: bool = False
    memory_write_allowed: bool = False
    external_effect_enabled: bool = False
    blocked_effects: list[str] = Field(default_factory=list)
    policy_refs: list[str] = Field(
        default_factory=lambda: [CAPTURE_READINESS_LADDER_POLICY_REF]
    )

    @model_validator(mode="after")
    def enforce_panel_safety(self) -> "CaptureReadinessLadderPanel":
        if self.policy_ref != CAPTURE_READINESS_LADDER_POLICY_REF:
            raise ValueError("capture readiness ladder policy mismatch")
        if [step.order for step in self.steps] != list(range(1, 11)):
            raise ValueError("capture readiness ladder must be ordered one through ten")
        if len({step.step_id for step in self.steps}) != 10:
            raise ValueError("capture readiness ladder step IDs must be unique")
        if self.ready_count != sum(int(step.status == "ready") for step in self.steps):
            raise ValueError("ready count mismatch")
        if self.blocked_count != sum(int(step.status == "blocked") for step in self.steps):
            raise ValueError("blocked count mismatch")
        if self.planned_count != sum(int(step.status == "planned") for step in self.steps):
            raise ValueError("planned count mismatch")
        if self.watching_count != sum(int(step.status == "watching") for step in self.steps):
            raise ValueError("watching count mismatch")
        if (
            not self.display_only
            or self.raw_payloads_included
            or self.raw_ref_retained
            or self.memory_write_allowed
            or self.external_effect_enabled
        ):
            raise ValueError("capture readiness ladder cannot enable capture side effects")
        required_blocked = {
            "continuous_capture",
            "raw_pixel_return",
            "durable_memory_write",
            "raw_ref_retention",
            "external_effect",
            "arbitrary_command_execution",
        }
        if missing := sorted(required_blocked.difference(self.blocked_effects)):
            raise ValueError(f"capture readiness ladder missing blocked effects: {missing}")
        if CAPTURE_READINESS_LADDER_POLICY_REF not in self.policy_refs:
            raise ValueError("capture readiness ladder requires policy ref")
        return self


def build_capture_readiness_ladder(
    *,
    bundle: RealCaptureControlBundle,
    preflight: CapturePreflightDiagnostics,
    screen_probe: NativeScreenCaptureProbeResult,
    receipt_summary: CaptureControlReceiptSummary,
    raw_ref_scavenger: RawRefScavengerReceipt,
    next_gate: RealCaptureNextGatePlan | None = None,
    metadata_stream_plan: ScreenMetadataStreamPlan | None = None,
    now: datetime | None = None,
) -> CaptureReadinessLadderPanel:
    timestamp = _timestamp(now)
    gate = next_gate or build_real_capture_next_gate_plan()
    stream_plan = metadata_stream_plan or build_screen_metadata_stream_plan()
    skip_receipt = build_screen_probe_skip_receipt(screen_probe)
    ux_receipt = build_screen_probe_ux_receipt(screen_probe)
    steps = [
        _step(
            1,
            "capture_token",
            "Bridge token",
            "Local bridge",
            "ready",
            "Dynamic config serves an ephemeral token.",
            "Keep the dashboard loaded from the local bridge.",
            "Token is local only and never grants external network authority.",
        ),
        _step(
            2,
            "localhost_origin",
            "Localhost origin",
            "Local bridge",
            "ready",
            "Bridge rejects remote clients and bad origins.",
            "Use 127.0.0.1 or localhost for live testing.",
            "No arbitrary command path is exposed.",
        ),
        _step(
            3,
            "shadow_clicker",
            "Shadow Clicker",
            "Native overlay",
            "ready" if bundle.readiness.can_start_cursor_overlay else "blocked",
            "Display-only cursor follower can run without Screen Recording.",
            "Click Turn On Cortex to start the native clicker.",
            "It follows the cursor without clicks, typing, capture, or memory writes.",
            command=bundle.session_plan.cursor_overlay_command,
        ),
        _step(
            4,
            "permission_preflight",
            "Permission preflight",
            "Dashboard",
            "ready" if not preflight.missing_permissions else "blocked",
            f"Missing permissions: {', '.join(preflight.missing_permissions) or 'none'}.",
            preflight.next_user_actions[0],
            "Preflight is prompt-free and starts no observers.",
        ),
        _step(
            5,
            "sensitive_app_filter",
            "Sensitive app filter",
            "Privacy firewall",
            "ready" if bundle.sensitive_filter.passed else "blocked",
            "Known private apps are blocked before capture eligibility.",
            "Keep password, message, mail, and keychain surfaces excluded.",
            "Window titles from blocked apps are not allowed.",
        ),
        _step(
            6,
            "screen_probe",
            "Screen Probe",
            "Native probe",
            "ready" if screen_probe.frame_captured else "blocked",
            _probe_proof(screen_probe),
            _probe_next_action(ux_receipt),
            "Probe returns metadata only; raw pixels and raw refs stay off.",
        ),
        _step(
            7,
            "probe_skip_or_ux",
            "Probe receipt UX",
            "Dashboard receipt",
            "ready",
            _probe_ux_proof(ux_receipt, skip_receipt),
            "Use the visible receipt to decide the next safe step.",
            "Skipped probes are explicit receipts, not silent failures.",
        ),
        _step(
            8,
            "raw_ref_scavenger",
            "Raw ref scavenger",
            "Temp storage",
            "ready" if raw_ref_scavenger.passed else "blocked",
            f"Scanned {raw_ref_scavenger.scanned_count}; deleted {raw_ref_scavenger.deleted_count}.",
            "Run scavenger before and after real capture experiments.",
            "Scavenger deletes by metadata age and does not read payloads.",
        ),
        _step(
            9,
            "metadata_stream_plan",
            "Metadata stream plan",
            "Future ScreenCaptureKit",
            "planned",
            f"Output shape is {stream_plan.output_shape}.",
            "Keep future streaming count-only until separate review.",
            "Continuous capture, raw pixels, raw refs, and memory writes are blocked.",
        ),
        _step(
            10,
            "receipt_audit",
            "Receipt audit",
            "Dashboard receipts",
            "watching",
            f"{receipt_summary.receipt_count} local events; exits={receipt_summary.watchdog_exit_count}.",
            "Use Receipts after every live action.",
            "Audit summaries are count-only and raw-payload-free.",
        ),
    ]
    next_step = next((step for step in steps if step.status == "blocked"), steps[-1])
    return CaptureReadinessLadderPanel(
        generated_at=timestamp,
        summary=(
            "Ten local gates from button click to metadata-only capture, with "
            "raw payloads, durable memory writes, and external effects off."
        ),
        steps=steps,
        ready_count=sum(int(step.status == "ready") for step in steps),
        blocked_count=sum(int(step.status == "blocked") for step in steps),
        planned_count=sum(int(step.status == "planned") for step in steps),
        watching_count=sum(int(step.status == "watching") for step in steps),
        next_step_label=next_step.label,
        can_demo_now=bundle.readiness.can_start_cursor_overlay,
        can_probe_now=preflight.safe_to_attempt_metadata_probe,
        can_real_capture_now=preflight.safe_to_start_real_capture_session
        and gate.passed
        and not screen_probe.raw_pixels_returned,
        blocked_effects=[
            "continuous_capture",
            "raw_pixel_return",
            "durable_memory_write",
            "raw_ref_retention",
            "external_effect",
            "arbitrary_command_execution",
        ],
        policy_refs=[
            CAPTURE_READINESS_LADDER_POLICY_REF,
            bundle.dashboard_panel.policy_ref,
            preflight.policy_ref,
            screen_probe.policy_ref,
            RAW_REF_SCAVENGER_POLICY_REF,
            gate.policy_ref,
            stream_plan.policy_ref,
            receipt_summary.policy_ref,
        ],
    )


def build_fixture_capture_readiness_ladder(
    *,
    permissions_ready: bool = False,
    now: datetime | None = None,
) -> CaptureReadinessLadderPanel:
    timestamp = _timestamp(now)
    permission = build_fixture_permission_smoke_result(
        screen_recording_preflight=permissions_ready,
        accessibility_trusted=permissions_ready,
        checked_at=timestamp,
    )
    bundle = build_real_capture_control_bundle(permission_smoke=permission, now=timestamp)
    preflight = build_capture_preflight_diagnostics(
        permission,
        checked_at=timestamp,
        host_pid=123,
        executable_path="/Applications/Codex.app/Contents/MacOS/Codex",
    )
    screen_probe = build_fixture_native_screen_capture_probe_result(
        allow_real_capture=True,
        screen_recording_preflight=permissions_ready,
        checked_at=timestamp,
    )
    raw_ref_scavenger = run_raw_ref_scavenger(now=timestamp)
    return build_capture_readiness_ladder(
        bundle=bundle,
        preflight=preflight,
        screen_probe=screen_probe,
        receipt_summary=build_empty_capture_control_receipt_summary(),
        raw_ref_scavenger=raw_ref_scavenger,
        now=timestamp,
    )


def build_empty_capture_control_receipt_summary() -> CaptureControlReceiptSummary:
    return CaptureControlReceiptSummary(
        receipt_count=0,
        running_count=0,
        start_count=0,
        stop_count=0,
        permission_check_count=0,
        preflight_count=0,
        screen_probe_count=0,
        skipped_screen_probe_count=0,
        watchdog_exit_count=0,
        blocked_count=0,
    )


def _step(
    order: int,
    step_id: str,
    label: str,
    surface: str,
    status: LadderStepStatus,
    proof: str,
    next_action: str,
    safety_note: str,
    *,
    command: str | None = None,
) -> CaptureReadinessLadderStep:
    return CaptureReadinessLadderStep(
        step_id=step_id,
        order=order,
        label=label,
        surface=surface,
        status=status,
        proof=proof,
        next_action=next_action,
        safety_note=safety_note,
        command=command,
    )


def _probe_proof(result: NativeScreenCaptureProbeResult) -> str:
    if result.frame_captured:
        return f"Captured one metadata frame: {result.frame_width}x{result.frame_height}."
    return f"Skipped before frame capture: {result.skip_reason or 'unknown'}."


def _probe_ux_proof(
    ux: ScreenProbeUXReceipt,
    skip: ScreenProbeSkipReceipt | None,
) -> str:
    if skip is None:
        return f"Probe UX is {ux.severity}; no skip receipt required."
    return f"Probe UX is {ux.severity}; skip reason is {skip.reason}."


def _probe_next_action(ux: ScreenProbeUXReceipt) -> str:
    return ux.next_user_actions[0] if ux.next_user_actions else "Run Preflight, then retry."


def _timestamp(now: datetime | None) -> datetime:
    timestamp = now or datetime.now(UTC)
    if timestamp.tzinfo is None:
        return timestamp.replace(tzinfo=UTC)
    return timestamp.astimezone(UTC)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--permissions-ready", action="store_true")
    args = parser.parse_args(argv)
    panel = build_fixture_capture_readiness_ladder(
        permissions_ready=args.permissions_ready
    )
    if args.json:
        print(json.dumps(panel.model_dump(mode="json"), indent=2, sort_keys=True))
    else:
        print(
            f"{panel.ladder_id}: ready={panel.ready_count}/10; "
            f"blocked={panel.blocked_count}; next={panel.next_step_label}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
