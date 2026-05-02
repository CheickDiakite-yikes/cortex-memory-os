from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest

from cortex_memory_os.native_screen_capture_probe import (
    NATIVE_SCREEN_CAPTURE_PROBE_ID,
    NATIVE_SCREEN_CAPTURE_PROBE_POLICY_REF,
    build_fixture_native_screen_capture_probe_result,
    native_screen_capture_probe_command,
    parse_native_screen_capture_probe_output,
    run_native_screen_capture_probe,
)


class FakeCompleted:
    def __init__(self, stdout: str, returncode: int = 0, stderr: str = "") -> None:
        self.stdout = stdout
        self.returncode = returncode
        self.stderr = stderr


def test_screen_capture_probe_fixture_is_read_only_without_allow_flag() -> None:
    result = build_fixture_native_screen_capture_probe_result(
        allow_real_capture=False,
        screen_recording_preflight=True,
    )

    assert result.passed
    assert result.benchmark_id == NATIVE_SCREEN_CAPTURE_PROBE_ID
    assert result.policy_ref == NATIVE_SCREEN_CAPTURE_PROBE_POLICY_REF
    assert not result.allow_real_capture
    assert not result.capture_attempted
    assert not result.frame_captured
    assert result.skip_reason == "allow_real_capture_false"
    assert result.next_user_actions
    assert not result.raw_pixels_returned
    assert not result.raw_ref_retained
    assert not result.memory_write_allowed
    assert result.evidence_refs == []


def test_screen_capture_probe_fixture_can_capture_metadata_only_with_allow_flag() -> None:
    result = build_fixture_native_screen_capture_probe_result(
        allow_real_capture=True,
        screen_recording_preflight=True,
    )

    assert result.passed
    assert result.allow_real_capture
    assert result.capture_attempted
    assert result.frame_captured
    assert result.skip_reason is None
    assert result.frame_width == 1440
    assert result.frame_height == 900
    assert not result.raw_pixels_returned
    assert not result.raw_ref_retained
    assert not result.memory_write_allowed
    assert "capture_one_frame_in_memory" in result.allowed_effects


def test_screen_capture_probe_parser_rejects_raw_pixels() -> None:
    result = build_fixture_native_screen_capture_probe_result(
        checked_at=datetime(2026, 5, 2, 19, 0, tzinfo=UTC)
    )
    payload = result.model_dump(mode="json")
    payload["raw_pixels_returned"] = True

    with pytest.raises(ValueError, match="cannot return pixels"):
        parse_native_screen_capture_probe_output(json.dumps(payload))


def test_screen_capture_probe_fixture_explains_permission_skip() -> None:
    result = build_fixture_native_screen_capture_probe_result(
        allow_real_capture=True,
        screen_recording_preflight=False,
    )

    assert result.passed
    assert result.allow_real_capture
    assert not result.capture_attempted
    assert not result.frame_captured
    assert result.skip_reason == "screen_recording_preflight_false"
    assert "Screen Recording" in result.next_user_actions[0]


def test_run_screen_capture_probe_uses_swiftpm_command_with_fake_runner() -> None:
    fixture = build_fixture_native_screen_capture_probe_result(
        allow_real_capture=True,
        screen_recording_preflight=True,
    )
    seen_command: list[str] = []

    def fake_runner(command, **kwargs):
        seen_command.extend(command)
        assert kwargs["check"] is False
        assert kwargs["capture_output"] is True
        assert kwargs["text"] is True
        return FakeCompleted(fixture.model_dump_json())

    result = run_native_screen_capture_probe(allow_real_capture=True, runner=fake_runner)

    assert result == fixture
    assert seen_command == native_screen_capture_probe_command(allow_real_capture=True)


def test_run_screen_capture_probe_reports_native_failures() -> None:
    def fake_runner(command, **kwargs):
        return FakeCompleted("", returncode=1, stderr="capture probe failed")

    with pytest.raises(RuntimeError, match="capture probe failed"):
        run_native_screen_capture_probe(runner=fake_runner)
