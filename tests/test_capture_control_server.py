from __future__ import annotations

from cortex_memory_os.capture_control_server import (
    CAPTURE_CONTROL_SERVER_POLICY_REF,
    CaptureControlProcessManager,
    FakePopen,
    run_capture_control_server_smoke,
)


def test_capture_control_manager_launches_fixed_shadow_clicker_command() -> None:
    manager = CaptureControlProcessManager(popen_factory=FakePopen)

    start = manager.start(duration_seconds=2)
    status = manager.status()
    stop = manager.stop()

    assert start.policy_ref == CAPTURE_CONTROL_SERVER_POLICY_REF
    assert start.running
    assert start.pid == 4242
    assert "cortex-shadow-clicker" in start.command
    assert "--duration" in start.command
    assert start.duration_seconds == 2
    assert not start.capture_started
    assert not start.accessibility_observer_started
    assert not start.memory_write_allowed
    assert not start.raw_ref_retained
    assert not start.raw_screen_storage_enabled
    assert status.running
    assert stop.state == "stopped"
    assert not stop.running


def test_capture_control_server_smoke_serves_dashboard_and_blocks_remote_probe() -> None:
    smoke = run_capture_control_server_smoke()

    assert smoke.passed
    assert smoke.policy_ref == CAPTURE_CONTROL_SERVER_POLICY_REF
    assert smoke.status_code == 200
    assert smoke.start_status_code == 200
    assert smoke.stop_status_code == 200
    assert smoke.served_dashboard
    assert smoke.remote_rejected_status_code == 403
    assert smoke.start_receipt.fixed_command_only
    assert smoke.start_receipt.localhost_only
    assert "cortex-shadow-clicker" in smoke.start_receipt.command
    assert smoke.stop_receipt.action == "stop"
