import json
from datetime import UTC, datetime

import pytest

from cortex_memory_os.native_cursor_follow import (
    NATIVE_CURSOR_FOLLOW_ID,
    NATIVE_CURSOR_FOLLOW_POLICY_REF,
    build_fixture_native_cursor_follow_smoke_result,
    native_cursor_follow_command,
    parse_native_cursor_follow_output,
    run_native_cursor_follow_smoke,
)


class _Completed:
    def __init__(self, *, returncode: int, stdout: str = "", stderr: str = ""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_fixture_native_cursor_follow_is_cursor_only_and_display_only():
    result = build_fixture_native_cursor_follow_smoke_result()

    assert result.benchmark_id == NATIVE_CURSOR_FOLLOW_ID
    assert result.policy_ref == NATIVE_CURSOR_FOLLOW_POLICY_REF
    assert result.passed
    assert result.display_only
    assert not result.capture_started
    assert not result.accessibility_observer_started
    assert not result.memory_write_allowed
    assert not result.raw_ref_retained
    assert not result.external_effects
    assert "read_global_cursor_position" in result.config.allowed_effects
    assert "execute_click" in result.config.blocked_effects
    assert "write_memory" in result.config.blocked_effects


def test_parse_native_cursor_follow_output_rejects_capture_or_memory_writes():
    payload = build_fixture_native_cursor_follow_smoke_result().model_dump(mode="json")
    payload["capture_started"] = True

    with pytest.raises(ValueError, match="cannot start capture"):
        parse_native_cursor_follow_output(json.dumps(payload))

    payload = build_fixture_native_cursor_follow_smoke_result().model_dump(mode="json")
    payload["memory_write_allowed"] = True
    with pytest.raises(ValueError, match="cannot allow memory writes"):
        parse_native_cursor_follow_output(json.dumps(payload))


def test_run_native_cursor_follow_uses_swiftpm_smoke_command_with_fake_runner():
    fixture = build_fixture_native_cursor_follow_smoke_result(
        checked_at=datetime(2026, 5, 2, 16, 0, tzinfo=UTC)
    )
    seen = {}

    def fake_runner(command, **kwargs):
        seen["command"] = command
        assert kwargs["capture_output"] is True
        assert kwargs["text"] is True
        return _Completed(returncode=0, stdout=fixture.model_dump_json())

    result = run_native_cursor_follow_smoke(runner=fake_runner)

    assert result.passed
    assert seen["command"] == native_cursor_follow_command()


def test_run_native_cursor_follow_reports_native_failures():
    def fake_runner(command, **kwargs):
        return _Completed(returncode=1, stderr="no AppKit")

    with pytest.raises(RuntimeError, match="native cursor follow smoke failed"):
        run_native_cursor_follow_smoke(runner=fake_runner)
