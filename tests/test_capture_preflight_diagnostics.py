from __future__ import annotations

import pytest

from cortex_memory_os.capture_preflight_diagnostics import (
    CAPTURE_PERMISSION_GUIDE_ID,
    CAPTURE_PREFLIGHT_DIAGNOSTICS_ID,
    SCREEN_METADATA_STREAM_PLAN_ID,
    SCREEN_PROBE_RESULT_UX_ID,
    SCREEN_PROBE_SKIP_RECEIPT_ID,
    ScreenProbeSkipReceipt,
    build_capture_permission_guide,
    build_capture_preflight_diagnostics,
    build_screen_metadata_stream_plan,
    build_screen_probe_skip_receipt,
    build_screen_probe_ux_receipt,
)
from cortex_memory_os.native_permission_smoke import build_fixture_permission_smoke_result
from cortex_memory_os.native_screen_capture_probe import (
    build_fixture_native_screen_capture_probe_result,
)


def test_capture_permission_guide_is_prompt_free_and_actionable() -> None:
    guide = build_capture_permission_guide(host_process_label="Codex")

    assert guide.guide_id == CAPTURE_PERMISSION_GUIDE_ID
    assert guide.restart_required
    assert not guide.prompt_requested
    assert not guide.capture_started
    assert not guide.memory_write_allowed
    assert any("Screen Recording" in step for step in guide.screen_recording_steps)
    assert any("Accessibility" in step for step in guide.accessibility_steps)


def test_preflight_diagnostics_names_missing_permissions_without_capture() -> None:
    permission = build_fixture_permission_smoke_result(
        screen_recording_preflight=False,
        accessibility_trusted=False,
    )

    diagnostics = build_capture_preflight_diagnostics(
        permission,
        host_pid=123,
        executable_path="/Applications/Codex.app/Contents/MacOS/Codex",
    )

    assert diagnostics.diagnostic_id == CAPTURE_PREFLIGHT_DIAGNOSTICS_ID
    assert diagnostics.host_pid == 123
    assert diagnostics.missing_permissions == ["screen_recording", "accessibility"]
    assert diagnostics.safe_to_start_shadow_clicker
    assert not diagnostics.safe_to_attempt_metadata_probe
    assert not diagnostics.safe_to_start_real_capture_session
    assert not diagnostics.prompt_requested
    assert not diagnostics.capture_started
    assert not diagnostics.raw_payloads_included
    assert not diagnostics.raw_ref_retained
    assert not diagnostics.memory_write_allowed
    assert "Screen Recording" in diagnostics.next_user_actions[0]


def test_preflight_diagnostics_allows_probe_when_screen_recording_ready() -> None:
    permission = build_fixture_permission_smoke_result(
        screen_recording_preflight=True,
        accessibility_trusted=False,
    )

    diagnostics = build_capture_preflight_diagnostics(permission, host_pid=123)

    assert diagnostics.missing_permissions == ["accessibility"]
    assert diagnostics.safe_to_attempt_metadata_probe
    assert not diagnostics.safe_to_start_real_capture_session


def test_screen_probe_skip_receipt_explains_screen_permission_block() -> None:
    probe = build_fixture_native_screen_capture_probe_result(
        allow_real_capture=True,
        screen_recording_preflight=False,
    )

    skip = build_screen_probe_skip_receipt(probe)
    ux = build_screen_probe_ux_receipt(probe)

    assert skip is not None
    assert skip.skip_id == SCREEN_PROBE_SKIP_RECEIPT_ID
    assert skip.reason == "screen_recording_preflight_false"
    assert not skip.capture_attempted
    assert not skip.frame_captured
    assert not skip.raw_pixels_returned
    assert not skip.raw_ref_retained
    assert not skip.memory_write_allowed
    assert ux.ux_id == SCREEN_PROBE_RESULT_UX_ID
    assert ux.severity == "blocked"
    assert ux.blocked_by_permission
    assert "Screen Recording" in ux.message


def test_screen_probe_skip_receipt_is_absent_after_metadata_capture() -> None:
    probe = build_fixture_native_screen_capture_probe_result(
        allow_real_capture=True,
        screen_recording_preflight=True,
    )

    assert build_screen_probe_skip_receipt(probe) is None
    ux = build_screen_probe_ux_receipt(probe)

    assert ux.frame_captured
    assert ux.severity == "ok"
    assert not ux.raw_pixels_returned


def test_screen_probe_skip_receipt_rejects_captured_probe_payload() -> None:
    probe = build_fixture_native_screen_capture_probe_result(
        allow_real_capture=True,
        screen_recording_preflight=True,
    )
    payload = {
        "reason": "screen_recording_preflight_false",
        "allow_real_capture": probe.allow_real_capture,
        "screen_recording_preflight": probe.screen_recording_preflight,
        "capture_attempted": True,
        "frame_captured": True,
        "next_user_actions": ["Enable Screen Recording."],
        "passed": True,
    }

    with pytest.raises(ValueError, match="cannot represent a captured frame"):
        ScreenProbeSkipReceipt.model_validate(payload)


def test_screen_metadata_stream_plan_is_metadata_only_and_not_continuous_capture() -> None:
    plan = build_screen_metadata_stream_plan()

    assert plan.plan_id == SCREEN_METADATA_STREAM_PLAN_ID
    assert plan.token_required
    assert plan.screen_recording_preflight_required
    assert plan.output_shape == "metadata_count_receipts"
    assert not plan.continuous_capture_allowed
    assert not plan.raw_pixels_returned
    assert not plan.raw_ref_retained
    assert not plan.memory_write_allowed
    assert "continuous_capture" in plan.blocked_effects
