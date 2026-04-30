"""Read-only macOS capture/accessibility permission smoke wrapper."""

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


NATIVE_CAPTURE_PERMISSION_SMOKE_ID = "NATIVE-CAPTURE-PERMISSION-SMOKE-001"
NATIVE_CAPTURE_PERMISSION_SMOKE_POLICY_REF = "policy_native_capture_permission_smoke_v1"
REPO_ROOT = Path(__file__).resolve().parents[2]
NATIVE_PACKAGE_PATH = REPO_ROOT / "native" / "macos-shadow-pointer"
NATIVE_PERMISSION_SMOKE_COMMAND = "cortex-permission-smoke"


class RunnerCompleted(Protocol):
    returncode: int
    stdout: str
    stderr: str


Runner = Callable[..., RunnerCompleted]


class NativePermissionSmokeResult(StrictModel):
    benchmark_id: str = Field(min_length=1)
    policy_ref: str = Field(min_length=1)
    checked_at: datetime
    screen_recording_preflight: bool
    accessibility_trusted: bool
    prompt_requested: bool
    capture_started: bool
    accessibility_observer_started: bool
    memory_write_allowed: bool
    evidence_refs: list[str] = Field(default_factory=list)
    allowed_effects: list[str] = Field(default_factory=list)
    blocked_effects: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)
    passed: bool

    @model_validator(mode="after")
    def enforce_read_only_boundary(self) -> NativePermissionSmokeResult:
        if self.benchmark_id != NATIVE_CAPTURE_PERMISSION_SMOKE_ID:
            raise ValueError("native permission smoke benchmark_id mismatch")
        if self.policy_ref != NATIVE_CAPTURE_PERMISSION_SMOKE_POLICY_REF:
            raise ValueError("native permission smoke policy_ref mismatch")
        if self.prompt_requested:
            raise ValueError("permission smoke cannot request permission prompts")
        if self.capture_started:
            raise ValueError("permission smoke cannot start screen capture")
        if self.accessibility_observer_started:
            raise ValueError("permission smoke cannot start Accessibility observers")
        if self.memory_write_allowed:
            raise ValueError("permission smoke cannot allow memory writes")
        if self.evidence_refs:
            raise ValueError("permission smoke cannot emit evidence refs")
        if self.allowed_effects != ["read_permission_status"]:
            raise ValueError("permission smoke can only allow read_permission_status")
        required_blocked = {
            "request_screen_recording_permission",
            "request_accessibility_permission",
            "start_screen_capture",
            "start_accessibility_observer",
            "write_memory",
            "store_raw_evidence",
        }
        if missing := sorted(required_blocked.difference(self.blocked_effects)):
            raise ValueError(f"permission smoke missing blocked effects: {missing}")
        if not self.safety_notes:
            raise ValueError("permission smoke requires safety notes")
        return self


def build_fixture_permission_smoke_result(
    *,
    screen_recording_preflight: bool = False,
    accessibility_trusted: bool = False,
    checked_at: datetime | None = None,
) -> NativePermissionSmokeResult:
    return NativePermissionSmokeResult(
        benchmark_id=NATIVE_CAPTURE_PERMISSION_SMOKE_ID,
        policy_ref=NATIVE_CAPTURE_PERMISSION_SMOKE_POLICY_REF,
        checked_at=checked_at or datetime(2026, 4, 30, 12, 0, tzinfo=UTC),
        screen_recording_preflight=screen_recording_preflight,
        accessibility_trusted=accessibility_trusted,
        prompt_requested=False,
        capture_started=False,
        accessibility_observer_started=False,
        memory_write_allowed=False,
        evidence_refs=[],
        allowed_effects=["read_permission_status"],
        blocked_effects=[
            "request_screen_recording_permission",
            "request_accessibility_permission",
            "start_screen_capture",
            "start_accessibility_observer",
            "write_memory",
            "store_raw_evidence",
        ],
        safety_notes=[
            "permission status is read without prompting",
            "no capture, observer, memory write, or evidence storage is started",
        ],
        passed=True,
    )


def parse_native_permission_smoke_output(output: str) -> NativePermissionSmokeResult:
    payload = json.loads(output)
    return NativePermissionSmokeResult.model_validate(payload)


def native_permission_smoke_command(
    *,
    package_path: Path = NATIVE_PACKAGE_PATH,
) -> list[str]:
    return [
        "swift",
        "run",
        "--package-path",
        str(package_path),
        NATIVE_PERMISSION_SMOKE_COMMAND,
    ]


def run_native_permission_smoke(
    *,
    package_path: Path = NATIVE_PACKAGE_PATH,
    runner: Runner | None = None,
) -> NativePermissionSmokeResult:
    command = native_permission_smoke_command(package_path=package_path)
    completed = (runner or subprocess.run)(
        command,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "no output"
        raise RuntimeError(f"native permission smoke failed: {detail}")
    return parse_native_permission_smoke_output(completed.stdout)


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the permission smoke receipt as JSON.",
    )
    parser.add_argument(
        "--fixture",
        action="store_true",
        help="Use a deterministic local fixture instead of invoking SwiftPM.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    result = (
        build_fixture_permission_smoke_result()
        if args.fixture
        else run_native_permission_smoke()
    )
    if args.json:
        print(result.model_dump_json(indent=2))
    else:
        print(
            f"{result.benchmark_id}: passed={result.passed} "
            f"screen_recording_preflight={result.screen_recording_preflight} "
            f"accessibility_trusted={result.accessibility_trusted}"
        )
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
