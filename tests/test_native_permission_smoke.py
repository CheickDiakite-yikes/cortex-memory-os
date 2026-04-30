import json
from datetime import UTC, datetime

import pytest

from cortex_memory_os.native_permission_smoke import (
    NATIVE_CAPTURE_PERMISSION_SMOKE_ID,
    NATIVE_CAPTURE_PERMISSION_SMOKE_POLICY_REF,
    build_fixture_permission_smoke_result,
    native_permission_smoke_command,
    parse_native_permission_smoke_output,
    run_native_permission_smoke,
)


class FakeCompleted:
    def __init__(self, stdout: str, returncode: int = 0, stderr: str = ""):
        self.stdout = stdout
        self.returncode = returncode
        self.stderr = stderr


def test_fixture_permission_smoke_is_read_only_without_required_permissions():
    result = build_fixture_permission_smoke_result(
        screen_recording_preflight=False,
        accessibility_trusted=False,
    )

    assert result.passed
    assert result.benchmark_id == NATIVE_CAPTURE_PERMISSION_SMOKE_ID
    assert result.policy_ref == NATIVE_CAPTURE_PERMISSION_SMOKE_POLICY_REF
    assert not result.prompt_requested
    assert not result.capture_started
    assert not result.accessibility_observer_started
    assert not result.memory_write_allowed
    assert result.evidence_refs == []
    assert result.allowed_effects == ["read_permission_status"]
    assert "request_screen_recording_permission" in result.blocked_effects
    assert "start_screen_capture" in result.blocked_effects


def test_parse_native_permission_smoke_output_enforces_no_prompt_boundary():
    result = build_fixture_permission_smoke_result(
        checked_at=datetime(2026, 4, 30, 12, 0, tzinfo=UTC)
    )
    payload = result.model_dump(mode="json")
    payload["prompt_requested"] = True

    with pytest.raises(ValueError, match="cannot request permission prompts"):
        parse_native_permission_smoke_output(json.dumps(payload))


def test_run_native_permission_smoke_uses_swiftpm_command_with_fake_runner():
    fixture = build_fixture_permission_smoke_result()
    seen_command: list[str] = []

    def fake_runner(command, **kwargs):
        seen_command.extend(command)
        assert kwargs["check"] is False
        assert kwargs["capture_output"] is True
        assert kwargs["text"] is True
        return FakeCompleted(fixture.model_dump_json())

    result = run_native_permission_smoke(runner=fake_runner)

    assert result == fixture
    assert seen_command == native_permission_smoke_command()


def test_run_native_permission_smoke_reports_native_failures():
    def fake_runner(command, **kwargs):
        return FakeCompleted("", returncode=1, stderr="swift build failed")

    with pytest.raises(RuntimeError, match="swift build failed"):
        run_native_permission_smoke(runner=fake_runner)
