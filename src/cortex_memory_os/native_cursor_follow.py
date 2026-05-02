"""Native macOS cursor-following Shadow Clicker wrapper."""

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

NATIVE_CURSOR_FOLLOW_ID = "NATIVE-CURSOR-FOLLOW-001"
NATIVE_CURSOR_FOLLOW_POLICY_REF = "policy_native_cursor_follow_v1"
NATIVE_CURSOR_FOLLOW_COMMAND = "cortex-shadow-clicker"


class RunnerCompleted(Protocol):
    returncode: int
    stdout: str
    stderr: str


Runner = Callable[..., RunnerCompleted]


class NativeCursorFollowConfig(StrictModel):
    policy_ref: str = NATIVE_CURSOR_FOLLOW_POLICY_REF
    sample_hz: int = Field(ge=5, le=60)
    overlay_diameter: float = Field(ge=16, le=96)
    offset_x: float
    offset_y: float
    display_only: bool
    ignores_mouse_events: bool
    allowed_effects: list[str] = Field(default_factory=list)
    blocked_effects: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def enforce_display_only_config(self) -> "NativeCursorFollowConfig":
        if self.policy_ref != NATIVE_CURSOR_FOLLOW_POLICY_REF:
            raise ValueError("native cursor follow policy mismatch")
        if not self.display_only or not self.ignores_mouse_events:
            raise ValueError("native cursor follower must be display-only and ignore mouse events")
        required_allowed = {
            "read_global_cursor_position",
            "render_shadow_clicker_overlay",
            "move_overlay_window",
        }
        if missing := sorted(required_allowed.difference(self.allowed_effects)):
            raise ValueError(f"native cursor follower missing allowed effects: {missing}")
        required_blocked = {
            "start_screen_capture",
            "start_accessibility_observer",
            "execute_click",
            "type_text",
            "read_window_contents",
            "write_memory",
            "store_raw_evidence",
            "export_payload",
        }
        if missing := sorted(required_blocked.difference(self.blocked_effects)):
            raise ValueError(f"native cursor follower missing blocked effects: {missing}")
        return self


class NativeCursorSample(StrictModel):
    x: float
    y: float
    timestamp: datetime


class NativeOverlayWindowSpec(StrictModel):
    policy_ref: str
    level: str
    style_masks: list[str] = Field(default_factory=list)
    collection_behaviors: list[str] = Field(default_factory=list)
    is_opaque: bool
    background_color: str
    ignores_mouse_events_by_default: bool
    can_become_key: bool
    can_become_main: bool
    has_shadow: bool
    accessibility_label: str


class NativeCursorFollowSmokeResult(StrictModel):
    benchmark_id: str = Field(min_length=1)
    policy_ref: str = Field(min_length=1)
    checked_at: datetime
    config: NativeCursorFollowConfig
    overlay_spec: NativeOverlayWindowSpec | None = None
    cursor_samples: list[NativeCursorSample] = Field(min_length=1)
    display_only: bool
    capture_started: bool
    accessibility_observer_started: bool
    memory_write_allowed: bool
    raw_ref_retained: bool
    external_effects: list[str] = Field(default_factory=list)
    passed: bool

    @model_validator(mode="after")
    def enforce_cursor_only_boundary(self) -> "NativeCursorFollowSmokeResult":
        if self.benchmark_id != NATIVE_CURSOR_FOLLOW_ID:
            raise ValueError("native cursor follower benchmark mismatch")
        if self.policy_ref != NATIVE_CURSOR_FOLLOW_POLICY_REF:
            raise ValueError("native cursor follower policy mismatch")
        if not self.display_only:
            raise ValueError("native cursor follower must be display-only")
        if self.capture_started or self.accessibility_observer_started:
            raise ValueError("native cursor follower cannot start capture or observers")
        if self.memory_write_allowed:
            raise ValueError("native cursor follower cannot allow memory writes")
        if self.raw_ref_retained:
            raise ValueError("native cursor follower cannot retain raw refs")
        if self.external_effects:
            raise ValueError("native cursor follower cannot produce external effects")
        return self


def native_cursor_follow_command(
    *,
    package_path: Path = NATIVE_PACKAGE_PATH,
    smoke: bool = True,
    json_output: bool = True,
    duration_seconds: float | None = None,
) -> list[str]:
    command = [
        "swift",
        "run",
        "--package-path",
        str(package_path),
        NATIVE_CURSOR_FOLLOW_COMMAND,
    ]
    if smoke:
        command.append("--smoke")
    if json_output:
        command.append("--json")
    if duration_seconds is not None:
        command.extend(["--duration", str(duration_seconds)])
    return command


def parse_native_cursor_follow_output(output: str) -> NativeCursorFollowSmokeResult:
    payload = json.loads(output)
    return NativeCursorFollowSmokeResult.model_validate(payload)


def run_native_cursor_follow_smoke(
    *,
    package_path: Path = NATIVE_PACKAGE_PATH,
    runner: Runner | None = None,
) -> NativeCursorFollowSmokeResult:
    completed = (runner or subprocess.run)(
        native_cursor_follow_command(package_path=package_path),
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "no output"
        raise RuntimeError(f"native cursor follow smoke failed: {detail}")
    return parse_native_cursor_follow_output(completed.stdout)


def build_fixture_native_cursor_follow_smoke_result(
    *,
    checked_at: datetime | None = None,
) -> NativeCursorFollowSmokeResult:
    timestamp = checked_at or datetime(2026, 5, 2, 16, 0, tzinfo=UTC)
    return NativeCursorFollowSmokeResult(
        benchmark_id=NATIVE_CURSOR_FOLLOW_ID,
        policy_ref=NATIVE_CURSOR_FOLLOW_POLICY_REF,
        checked_at=timestamp,
        config=NativeCursorFollowConfig(
            sample_hz=30,
            overlay_diameter=34,
            offset_x=14,
            offset_y=-14,
            display_only=True,
            ignores_mouse_events=True,
            allowed_effects=[
                "read_global_cursor_position",
                "render_shadow_clicker_overlay",
                "move_overlay_window",
            ],
            blocked_effects=[
                "start_screen_capture",
                "start_accessibility_observer",
                "execute_click",
                "type_text",
                "read_window_contents",
                "write_memory",
                "store_raw_evidence",
                "export_payload",
            ],
        ),
        cursor_samples=[
            NativeCursorSample(x=120, y=240, timestamp=timestamp),
            NativeCursorSample(x=180, y=260, timestamp=timestamp),
        ],
        display_only=True,
        capture_started=False,
        accessibility_observer_started=False,
        memory_write_allowed=False,
        raw_ref_retained=False,
        external_effects=[],
        passed=True,
    )


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--fixture", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    result = (
        build_fixture_native_cursor_follow_smoke_result()
        if args.fixture
        else run_native_cursor_follow_smoke()
    )
    if args.json:
        print(result.model_dump_json(indent=2))
    else:
        print(f"{result.benchmark_id}: passed={result.passed}; samples={len(result.cursor_samples)}")
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
