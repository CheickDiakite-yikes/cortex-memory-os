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
NATIVE_CURSOR_RESPONSIVENESS_ID = "NATIVE-CURSOR-RESPONSIVENESS-001"
NATIVE_OVERLAY_VISUAL_POLISH_ID = "NATIVE-OVERLAY-VISUAL-POLISH-001"
NATIVE_OVERLAY_VISUAL_POLISH_POLICY_REF = "policy_native_overlay_visual_polish_v1"


class RunnerCompleted(Protocol):
    returncode: int
    stdout: str
    stderr: str


Runner = Callable[..., RunnerCompleted]


class NativeCursorFollowConfig(StrictModel):
    policy_ref: str = NATIVE_CURSOR_FOLLOW_POLICY_REF
    sample_hz: int = Field(ge=30, le=120)
    overlay_diameter: float = Field(ge=16, le=96)
    offset_x: float
    offset_y: float
    cursor_hotspot_x: float = Field(ge=0)
    cursor_hotspot_y: float = Field(ge=0)
    display_only: bool
    ignores_mouse_events: bool
    follows_system_wide: bool
    surface_scope: str
    coordinate_space: str
    browser_dependency: bool
    max_render_latency_ms: float = Field(gt=0, le=24)
    max_pointer_drift_px: float = Field(ge=0, le=18)
    bubble_anchor_strategy: str
    bubble_min_clearance_px: float = Field(ge=8)
    allowed_effects: list[str] = Field(default_factory=list)
    blocked_effects: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def enforce_display_only_config(self) -> "NativeCursorFollowConfig":
        if self.policy_ref != NATIVE_CURSOR_FOLLOW_POLICY_REF:
            raise ValueError("native cursor follow policy mismatch")
        if not self.display_only or not self.ignores_mouse_events:
            raise ValueError("native cursor follower must be display-only and ignore mouse events")
        if not self.follows_system_wide:
            raise ValueError("native cursor follower must follow the system cursor")
        if self.surface_scope != "system_wide_macos":
            raise ValueError("native cursor follower cannot be scoped to a browser surface")
        if self.coordinate_space != "global_display_pixels":
            raise ValueError("native cursor follower must use global display pixels")
        if self.browser_dependency:
            raise ValueError("native cursor follower cannot depend on Chrome or any browser")
        if self.bubble_anchor_strategy != "cursor_adjacent_edge_aware":
            raise ValueError("native response bubble must be cursor-adjacent and edge-aware")
        required_allowed = {
            "read_global_cursor_position",
            "render_shadow_clicker_overlay",
            "move_overlay_window",
            "anchor_response_bubble",
        }
        if missing := sorted(required_allowed.difference(self.allowed_effects)):
            raise ValueError(f"native cursor follower missing allowed effects: {missing}")
        required_blocked = {
            "start_screen_capture",
            "start_accessibility_observer",
            "execute_click",
            "type_text",
            "read_window_contents",
            "move_system_cursor",
            "steal_focus",
            "browser_only_tracking",
            "unanchored_response_bubble",
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


class NativeDisplayFrame(StrictModel):
    min_x: float
    min_y: float
    width: float = Field(gt=0)
    height: float = Field(gt=0)


class NativeOverlayPlacement(StrictModel):
    overlay_origin_x: float
    overlay_origin_y: float
    visual_cursor_x: float
    visual_cursor_y: float
    desired_cursor_x: float
    desired_cursor_y: float
    pointer_drift_px: float = Field(ge=0)
    bubble_x: float
    bubble_y: float
    bubble_side: str = Field(min_length=1)
    bubble_anchored_to: str
    display_frame: NativeDisplayFrame

    @model_validator(mode="after")
    def enforce_cursor_anchored_bubble(self) -> "NativeOverlayPlacement":
        if self.bubble_anchored_to != "system_cursor":
            raise ValueError("native bubble must anchor to the system cursor")
        if self.pointer_drift_px > 18:
            raise ValueError("native overlay drift exceeds product budget")
        return self


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


class NativeOverlayVisualSpec(StrictModel):
    benchmark_id: str = NATIVE_OVERLAY_VISUAL_POLISH_ID
    policy_ref: str = NATIVE_OVERLAY_VISUAL_POLISH_POLICY_REF
    visual_style: str
    material: str
    vibrancy_enabled: bool
    tint_semantic_only: bool
    cursor_shape: str
    cursor_stroke_color: str
    cursor_fill_color: str
    cursor_hotspot_visible: bool
    bubble_corner_radius: float = Field(ge=14, le=24)
    bubble_shadow_radius: float = Field(ge=12, le=36)
    bubble_max_width: float = Field(ge=220, le=320)
    loading_animation: str
    loading_dot_count: int = Field(ge=3, le=3)
    loading_frame_rate_hz: int = Field(ge=24, le=60)
    motion_curve: str
    animation_respects_reduced_motion: bool
    max_text_lines: int = Field(ge=1, le=2)
    foreground_style: str
    avoids_opaque_scrim: bool
    glass_elements_grouped: bool
    display_only: bool
    blocked_effects: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def enforce_native_visual_polish(self) -> "NativeOverlayVisualSpec":
        if self.benchmark_id != NATIVE_OVERLAY_VISUAL_POLISH_ID:
            raise ValueError("native overlay visual benchmark mismatch")
        if self.policy_ref != NATIVE_OVERLAY_VISUAL_POLISH_POLICY_REF:
            raise ValueError("native overlay visual policy mismatch")
        if self.visual_style != "apple_liquid_glass_companion":
            raise ValueError("native overlay visual style mismatch")
        if self.material != "hud_window_vibrant_material" or not self.vibrancy_enabled:
            raise ValueError("native overlay must use system material and vibrancy")
        if not self.tint_semantic_only or not self.avoids_opaque_scrim:
            raise ValueError("native overlay glass treatment is too decorative or heavy")
        if not self.glass_elements_grouped:
            raise ValueError("native overlay glass elements must be grouped")
        if self.cursor_shape != "secondary_arrow" or not self.cursor_hotspot_visible:
            raise ValueError("native overlay cursor affordance is unclear")
        if (
            self.loading_animation != "three_dot_breathing"
            or not self.animation_respects_reduced_motion
        ):
            raise ValueError("native overlay loading animation is not product-ready")
        if self.foreground_style != "vibrant_label_and_secondary_label":
            raise ValueError("native overlay foreground style is not system-vibrant")
        if not self.display_only:
            raise ValueError("native overlay visual layer must be display-only")
        required_blocked = {
            "start_screen_capture",
            "start_accessibility_observer",
            "execute_click",
            "type_text",
            "move_system_cursor",
            "steal_focus",
            "write_memory",
            "store_raw_evidence",
            "export_payload",
        }
        if missing := sorted(required_blocked.difference(self.blocked_effects)):
            raise ValueError(f"native overlay visual spec missing blocked effects: {missing}")
        return self


class NativeCursorFollowSmokeResult(StrictModel):
    benchmark_id: str = Field(min_length=1)
    policy_ref: str = Field(min_length=1)
    checked_at: datetime
    config: NativeCursorFollowConfig
    overlay_spec: NativeOverlayWindowSpec | None = None
    visual_spec: NativeOverlayVisualSpec
    cursor_samples: list[NativeCursorSample] = Field(min_length=1)
    display_only: bool
    capture_started: bool
    accessibility_observer_started: bool
    memory_write_allowed: bool
    raw_ref_retained: bool
    external_effects: list[str] = Field(default_factory=list)
    placement_samples: list[NativeOverlayPlacement] = Field(min_length=1)
    sample_interval_ms: float = Field(gt=0, le=34)
    max_render_latency_ms_allowed: float = Field(gt=0, le=24)
    max_pointer_drift_px_measured: float = Field(ge=0, le=18)
    system_wide_ready: bool
    bubble_anchor_ready: bool
    browser_dependency: bool
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
        if not self.system_wide_ready or self.browser_dependency:
            raise ValueError("native cursor follower must be system-wide and browser-independent")
        if not self.bubble_anchor_ready:
            raise ValueError("native cursor follower must anchor response bubbles to the cursor")
        if self.sample_interval_ms > self.config.max_render_latency_ms:
            raise ValueError("native cursor follower sample interval exceeds render latency budget")
        if self.max_pointer_drift_px_measured > self.config.max_pointer_drift_px:
            raise ValueError("native cursor follower drift exceeds budget")
        if not self.visual_spec.display_only:
            raise ValueError("native overlay visual layer must remain display-only")
        if self.visual_spec.material != "hud_window_vibrant_material":
            raise ValueError("native overlay must use system material")
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
            sample_hz=60,
            overlay_diameter=34,
            offset_x=14,
            offset_y=-14,
            cursor_hotspot_x=7,
            cursor_hotspot_y=58,
            display_only=True,
            ignores_mouse_events=True,
            follows_system_wide=True,
            surface_scope="system_wide_macos",
            coordinate_space="global_display_pixels",
            browser_dependency=False,
            max_render_latency_ms=24,
            max_pointer_drift_px=18,
            bubble_anchor_strategy="cursor_adjacent_edge_aware",
            bubble_min_clearance_px=12,
            allowed_effects=[
                "read_global_cursor_position",
                "render_shadow_clicker_overlay",
                "move_overlay_window",
                "anchor_response_bubble",
            ],
            blocked_effects=[
                "start_screen_capture",
                "start_accessibility_observer",
                "execute_click",
                "type_text",
                "read_window_contents",
                "move_system_cursor",
                "steal_focus",
                "browser_only_tracking",
                "unanchored_response_bubble",
                "write_memory",
                "store_raw_evidence",
                "export_payload",
            ],
        ),
        visual_spec=NativeOverlayVisualSpec(
            visual_style="apple_liquid_glass_companion",
            material="hud_window_vibrant_material",
            vibrancy_enabled=True,
            tint_semantic_only=True,
            cursor_shape="secondary_arrow",
            cursor_stroke_color="system_blue",
            cursor_fill_color="vibrant_white",
            cursor_hotspot_visible=True,
            bubble_corner_radius=18,
            bubble_shadow_radius=24,
            bubble_max_width=260,
            loading_animation="three_dot_breathing",
            loading_dot_count=3,
            loading_frame_rate_hz=30,
            motion_curve="low_latency_linear_follow_soft_opacity",
            animation_respects_reduced_motion=True,
            max_text_lines=2,
            foreground_style="vibrant_label_and_secondary_label",
            avoids_opaque_scrim=True,
            glass_elements_grouped=True,
            display_only=True,
            blocked_effects=[
                "start_screen_capture",
                "start_accessibility_observer",
                "execute_click",
                "type_text",
                "move_system_cursor",
                "steal_focus",
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
        placement_samples=[
            NativeOverlayPlacement(
                overlay_origin_x=127,
                overlay_origin_y=168,
                visual_cursor_x=134,
                visual_cursor_y=226,
                desired_cursor_x=134,
                desired_cursor_y=226,
                pointer_drift_px=0,
                bubble_x=146,
                bubble_y=190,
                bubble_side="right",
                bubble_anchored_to="system_cursor",
                display_frame=NativeDisplayFrame(min_x=0, min_y=0, width=1440, height=900),
            ),
            NativeOverlayPlacement(
                overlay_origin_x=187,
                overlay_origin_y=188,
                visual_cursor_x=194,
                visual_cursor_y=246,
                desired_cursor_x=194,
                desired_cursor_y=246,
                pointer_drift_px=0,
                bubble_x=206,
                bubble_y=210,
                bubble_side="right",
                bubble_anchored_to="system_cursor",
                display_frame=NativeDisplayFrame(min_x=0, min_y=0, width=1440, height=900),
            ),
        ],
        sample_interval_ms=1000 / 60,
        max_render_latency_ms_allowed=24,
        max_pointer_drift_px_measured=0,
        system_wide_ready=True,
        bubble_anchor_ready=True,
        browser_dependency=False,
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
