from __future__ import annotations

from cortex_memory_os.capture_control_server import (
    CAPTURE_CONTROL_SERVER_POLICY_REF,
    CaptureControlProcessManager,
    FakePopen,
    _memory_error,
    main,
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


def test_capture_control_manager_reports_user_test_readiness() -> None:
    manager = CaptureControlProcessManager(popen_factory=FakePopen)

    ready = manager.user_test_readiness()
    start = manager.start(duration_seconds=2)
    running = manager.user_test_readiness()

    assert ready.readiness_id == "USER-TEST-READINESS-001"
    assert ready.title == "Test Cortex Cursor"
    assert ready.ready_for_user_test
    assert ready.status == "ready"
    assert ready.helper_cursor_available
    assert not ready.helper_cursor_running
    assert ready.one_button_label == "Start helper cursor"
    assert ready.stop_button_label == "Stop helper cursor"
    assert "Start helper cursor" in ready.user_steps[0]
    assert not ready.screen_capture_required
    assert not ready.voice_required
    assert not ready.memory_write_required
    assert not ready.raw_ref_required
    assert "start_screen_capture" in ready.blocked_effects
    assert "write_memory" in ready.blocked_effects
    assert start.running
    assert running.status == "running"
    assert running.helper_cursor_running
    assert running.pid == 4242


def test_capture_control_user_test_cli_outputs_readiness(capsys) -> None:
    exit_code = main(["--user-test", "--json"])
    payload = capsys.readouterr().out

    assert exit_code == 0
    assert '"readiness_id": "USER-TEST-READINESS-001"' in payload
    assert '"title": "Test Cortex Cursor"' in payload
    assert '"ready_for_user_test": true' in payload
    assert '"screen_capture_required": false' in payload
    assert '"memory_write_required": false' in payload


def test_capture_control_manager_watchdog_reports_exited_overlay() -> None:
    class ExitedPopen(FakePopen):
        def poll(self) -> int | None:
            return 17

    manager = CaptureControlProcessManager(popen_factory=ExitedPopen)

    start = manager.start(duration_seconds=2)
    exited = manager.status()
    summary = manager.receipt_summary()

    assert start.running
    assert exited.action == "watchdog"
    assert exited.state == "exited"
    assert exited.exit_code == 17
    assert not exited.running
    assert exited.next_user_actions
    assert summary.watchdog_exit_count == 1


def test_capture_control_server_smoke_serves_dashboard_and_blocks_remote_probe() -> None:
    smoke = run_capture_control_server_smoke()

    assert smoke.passed
    assert smoke.policy_ref == CAPTURE_CONTROL_SERVER_POLICY_REF
    assert smoke.config_status_code == 200
    assert smoke.config_query_status_code == 200
    assert smoke.token_required
    assert smoke.missing_token_rejected_status_code == 403
    assert smoke.bad_origin_rejected_status_code == 403
    assert smoke.status_code == 200
    assert smoke.user_test_status_code == 200
    assert smoke.start_status_code == 200
    assert smoke.stop_status_code == 200
    assert smoke.permission_status_code == 200
    assert smoke.preflight_status_code == 200
    assert smoke.screen_probe_status_code == 200
    assert smoke.memory_save_status_code == 200
    assert smoke.memory_validate_status_code == 200
    assert smoke.memory_validate_accepted is False
    assert smoke.memory_list_status_code == 200
    assert smoke.memory_search_status_code == 200
    assert smoke.memory_ask_status_code == 200
    assert smoke.memory_context_pack_status_code == 200
    assert smoke.memory_explain_status_code == 200
    assert smoke.memory_correct_status_code == 200
    assert smoke.memory_forget_status_code == 200
    assert smoke.memory_undo_status_code == 200
    assert smoke.memory_after_forget_status_code == 200
    assert smoke.memory_audit_status_code == 200
    assert smoke.memory_status_status_code == 200
    assert smoke.memory_snapshot_status_code == 200
    assert smoke.memory_search_result_count == 1
    assert smoke.memory_ask_result_count == 1
    assert smoke.memory_context_pack_result_count == 1
    assert smoke.memory_after_forget_result_count == 0
    assert smoke.memory_audit_count == 5
    assert smoke.memory_pending_undo_count >= 1
    assert smoke.receipts_status_code == 200
    assert smoke.served_dashboard
    assert smoke.user_test_receipt.ready_for_user_test
    assert smoke.user_test_receipt.title == "Test Cortex Cursor"
    assert not smoke.user_test_receipt.screen_capture_required
    assert "execute_click" in smoke.user_test_receipt.blocked_effects
    assert smoke.remote_rejected_status_code == 403
    assert smoke.start_receipt.fixed_command_only
    assert smoke.start_receipt.localhost_only
    assert "cortex-shadow-clicker" in smoke.start_receipt.command
    assert smoke.permission_receipt.passed
    assert smoke.preflight_receipt.passed
    assert smoke.preflight_receipt.safe_to_start_real_capture_session
    assert smoke.screen_probe_receipt.passed
    assert smoke.screen_probe_receipt.capture_attempted
    assert not smoke.screen_probe_receipt.raw_pixels_returned
    assert not smoke.screen_probe_receipt.raw_ref_retained
    assert smoke.receipt_summary.receipt_count >= 5
    assert smoke.receipt_summary.preflight_count == 1
    assert smoke.receipt_summary.screen_probe_count == 1
    assert not smoke.receipt_summary.raw_ref_retained
    assert not smoke.receipt_summary.memory_write_allowed
    assert smoke.stop_receipt.action == "stop"


def test_manual_memory_errors_are_user_safe_and_redacted() -> None:
    secret_error = _memory_error("secret-like text cannot be saved")
    injection_error = _memory_error("prompt-injection-like text cannot be saved")

    assert secret_error["user_message"] == (
        "Safety lock worked. Cortex blocked secret-like text before saving."
    )
    assert injection_error["user_message"] == (
        "Safety lock worked. Cortex blocked instruction-like text before saving."
    )
    assert secret_error["content_redacted"] is True
    assert secret_error["source_refs_redacted"] is True
    assert secret_error["raw_ref_retained"] is False
    assert secret_error["external_effect_enabled"] is False
