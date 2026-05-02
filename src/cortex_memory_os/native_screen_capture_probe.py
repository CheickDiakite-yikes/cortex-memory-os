"""Native macOS single-frame screen capture probe wrapper."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from pydantic import Field, model_validator

from cortex_memory_os.contracts import StrictModel
from cortex_memory_os.native_permission_smoke import NATIVE_PACKAGE_PATH

NATIVE_SCREEN_CAPTURE_PROBE_ID = "NATIVE-SCREEN-CAPTURE-PROBE-001"
NATIVE_SCREEN_CAPTURE_PROBE_POLICY_REF = "policy_native_screen_capture_probe_v1"
NATIVE_SCREEN_CAPTURE_PROBE_COMMAND = "cortex-screen-capture-probe"


class RunnerCompleted(Protocol):
    returncode: int
    stdout: str
    stderr: str


Runner = Callable[..., RunnerCompleted]


class NativeScreenCaptureProbeResult(StrictModel):
    benchmark_id: str = Field(min_length=1)
    policy_ref: str = Field(min_length=1)
    checked_at: datetime
    allow_real_capture: bool
    screen_recording_preflight: bool
    prompt_requested: bool
    capture_attempted: bool
    frame_captured: bool
    frame_width: int | None = Field(default=None, ge=1)
    frame_height: int | None = Field(default=None, ge=1)
    skip_reason: str | None = None
    raw_pixels_returned: bool
    raw_ref_retained: bool
    memory_write_allowed: bool
    evidence_refs: list[str] = Field(default_factory=list)
    next_user_actions: list[str] = Field(default_factory=list)
    allowed_effects: list[str] = Field(default_factory=list)
    blocked_effects: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)
    passed: bool

    @model_validator(mode="after")
    def enforce_metadata_only_probe(self) -> "NativeScreenCaptureProbeResult":
        if self.benchmark_id != NATIVE_SCREEN_CAPTURE_PROBE_ID:
            raise ValueError("native screen capture probe benchmark mismatch")
        if self.policy_ref != NATIVE_SCREEN_CAPTURE_PROBE_POLICY_REF:
            raise ValueError("native screen capture probe policy mismatch")
        if self.prompt_requested:
            raise ValueError("screen capture probe cannot prompt for permissions")
        if not self.allow_real_capture and self.capture_attempted:
            raise ValueError("screen capture probe cannot attempt capture without explicit allow flag")
        if self.raw_pixels_returned or self.raw_ref_retained:
            raise ValueError("screen capture probe cannot return pixels or retain raw refs")
        if self.memory_write_allowed or self.evidence_refs:
            raise ValueError("screen capture probe cannot write memory or evidence refs")
        required_blocked = {
            "request_screen_recording_permission",
            "start_continuous_screen_capture",
            "return_raw_pixels",
            "store_raw_evidence",
            "write_memory",
            "start_accessibility_observer",
            "click",
            "type_text",
            "export_payload",
        }
        if missing := sorted(required_blocked.difference(self.blocked_effects)):
            raise ValueError(f"screen capture probe missing blocked effects: {missing}")
        if self.capture_attempted and not self.frame_captured:
            raise ValueError("capture attempt must capture metadata or fail closed")
        if self.frame_captured and (self.frame_width is None or self.frame_height is None):
            raise ValueError("captured frame must include dimensions only")
        if self.frame_captured and self.skip_reason:
            raise ValueError("captured frame cannot also carry a skip reason")
        if not self.frame_captured:
            if not self.skip_reason:
                raise ValueError("skipped screen probe requires a skip reason")
            if not self.next_user_actions:
                raise ValueError("skipped screen probe requires next user actions")
        if self.skip_reason == "screen_recording_preflight_false" and self.screen_recording_preflight:
            raise ValueError("screen recording skip reason conflicts with preflight state")
        return self


def native_screen_capture_probe_command(
    *,
    package_path: Path = NATIVE_PACKAGE_PATH,
    allow_real_capture: bool = False,
    json_output: bool = True,
) -> list[str]:
    command = [
        "swift",
        "run",
        "--package-path",
        str(package_path),
        NATIVE_SCREEN_CAPTURE_PROBE_COMMAND,
    ]
    if allow_real_capture:
        command.append("--allow-real-capture")
    if json_output:
        command.append("--json")
    return command


def parse_native_screen_capture_probe_output(output: str) -> NativeScreenCaptureProbeResult:
    return NativeScreenCaptureProbeResult.model_validate(json.loads(output))


def run_native_screen_capture_probe(
    *,
    package_path: Path = NATIVE_PACKAGE_PATH,
    allow_real_capture: bool = False,
    runner: Runner | None = None,
) -> NativeScreenCaptureProbeResult:
    completed = (runner or subprocess.run)(
        native_screen_capture_probe_command(
            package_path=package_path,
            allow_real_capture=allow_real_capture,
        ),
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "no output"
        raise RuntimeError(f"native screen capture probe failed: {detail}")
    return parse_native_screen_capture_probe_output(completed.stdout)


def build_fixture_native_screen_capture_probe_result(
    *,
    allow_real_capture: bool = False,
    screen_recording_preflight: bool = False,
    capture_attempted: bool | None = None,
    frame_captured: bool | None = None,
    checked_at: datetime | None = None,
) -> NativeScreenCaptureProbeResult:
    attempted = (
        allow_real_capture and screen_recording_preflight
        if capture_attempted is None
        else capture_attempted
    )
    captured = attempted if frame_captured is None else frame_captured
    skip_reason = None
    next_user_actions = []
    if not captured:
        if not allow_real_capture:
            skip_reason = "allow_real_capture_false"
            next_user_actions = [
                "Use the dashboard Screen Probe button or pass --allow-real-capture explicitly."
            ]
        elif not screen_recording_preflight:
            skip_reason = "screen_recording_preflight_false"
            next_user_actions = [
                "Enable Screen Recording for the hosting app.",
                "Restart the hosting app and run Check Permissions again.",
            ]
        else:
            skip_reason = "frame_metadata_unavailable"
            next_user_actions = ["Run Check Permissions, then retry Screen Probe."]
    return NativeScreenCaptureProbeResult(
        benchmark_id=NATIVE_SCREEN_CAPTURE_PROBE_ID,
        policy_ref=NATIVE_SCREEN_CAPTURE_PROBE_POLICY_REF,
        checked_at=checked_at or datetime(2026, 5, 2, 19, 0, tzinfo=UTC),
        allow_real_capture=allow_real_capture,
        screen_recording_preflight=screen_recording_preflight,
        prompt_requested=False,
        capture_attempted=attempted,
        frame_captured=captured,
        frame_width=1440 if captured else None,
        frame_height=900 if captured else None,
        skip_reason=skip_reason,
        raw_pixels_returned=False,
        raw_ref_retained=False,
        memory_write_allowed=False,
        evidence_refs=[],
        next_user_actions=next_user_actions,
        allowed_effects=(
            ["read_permission_status", "capture_one_frame_in_memory"]
            if allow_real_capture
            else ["read_permission_status"]
        ),
        blocked_effects=[
            "request_screen_recording_permission",
            "start_continuous_screen_capture",
            "return_raw_pixels",
            "store_raw_evidence",
            "write_memory",
            "start_accessibility_observer",
            "click",
            "type_text",
            "export_payload",
        ],
        safety_notes=[
            "real screen capture requires explicit allow flag",
            "one frame may be captured in memory for metadata only",
            "raw pixels, raw refs, evidence refs, and memory writes stay off",
        ],
        passed=True,
    )


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--allow-real-capture", action="store_true")
    parser.add_argument("--fixture", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    result = (
        build_fixture_native_screen_capture_probe_result(
            allow_real_capture=args.allow_real_capture,
            screen_recording_preflight=args.allow_real_capture,
        )
        if args.fixture
        else run_native_screen_capture_probe(allow_real_capture=args.allow_real_capture)
    )
    if args.json:
        print(result.model_dump_json(indent=2))
    else:
        print(
            f"{result.benchmark_id}: passed={result.passed}; "
            f"attempted={result.capture_attempted}; captured={result.frame_captured}"
        )
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
