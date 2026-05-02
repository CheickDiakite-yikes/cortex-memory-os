from datetime import UTC, datetime

import pytest

from cortex_memory_os.native_permission_smoke import build_fixture_permission_smoke_result
from cortex_memory_os.real_capture_control import (
    DASHBOARD_CAPTURE_CONTROL_ID,
    REAL_CAPTURE_EPHEMERAL_RAW_REF_ID,
    REAL_CAPTURE_INTENT_ID,
    REAL_CAPTURE_OBSERVATION_SAMPLER_ID,
    REAL_CAPTURE_READINESS_ID,
    REAL_CAPTURE_SENSITIVE_APP_FILTER_ID,
    REAL_CAPTURE_SESSION_PLAN_ID,
    REAL_CAPTURE_START_RECEIPT_ID,
    REAL_CAPTURE_STOP_RECEIPT_ID,
    CaptureStorageMode,
    RealCaptureIntent,
    build_capture_start_receipt,
    build_ephemeral_raw_ref_policy,
    build_observation_sampler_plan,
    build_real_capture_control_bundle,
    build_real_capture_intent,
    build_real_capture_readiness,
    build_real_capture_session_plan,
    build_sensitive_app_filter_result,
    classify_capture_app,
)
from cortex_memory_os.native_cursor_follow import build_fixture_native_cursor_follow_smoke_result


def _permission_smoke(*, ready: bool = True):
    return build_fixture_permission_smoke_result(
        screen_recording_preflight=ready,
        accessibility_trusted=ready,
        checked_at=datetime(2026, 5, 2, 16, 0, tzinfo=UTC),
    )


def test_real_capture_intent_requires_exact_button_confirmation():
    intent = build_real_capture_intent()

    assert intent.intent_id == REAL_CAPTURE_INTENT_ID
    assert intent.user_clicked_start
    assert intent.storage_mode == CaptureStorageMode.EPHEMERAL_ONLY
    assert not intent.durable_memory_writes_requested
    assert not intent.external_effects_requested

    with pytest.raises(ValueError, match="exact confirmation"):
        RealCaptureIntent(user_clicked_start=True, confirmation_text="start")


def test_readiness_separates_cursor_overlay_from_screen_capture_permissions():
    readiness = build_real_capture_readiness(
        _permission_smoke(ready=False),
        build_fixture_native_cursor_follow_smoke_result(),
    )

    assert readiness.readiness_id == REAL_CAPTURE_READINESS_ID
    assert readiness.can_start_cursor_overlay
    assert not readiness.can_start_screen_capture
    assert readiness.missing_permissions == ["screen_recording", "accessibility"]
    assert not readiness.durable_memory_write_allowed


def test_sensitive_app_filter_blocks_private_apps_and_redacts_titles():
    result = build_sensitive_app_filter_result()
    one_password = classify_capture_app("1Password", "com.1password.1password")
    vscode = classify_capture_app("VS Code", "com.microsoft.VSCode")

    assert result.filter_id == REAL_CAPTURE_SENSITIVE_APP_FILTER_ID
    assert result.passed
    assert not one_password.allowed_for_capture
    assert not one_password.window_title_allowed
    assert vscode.allowed_for_capture


def test_session_plan_is_ready_without_enabling_raw_storage_or_memory_writes():
    intent = build_real_capture_intent()
    readiness = build_real_capture_readiness(
        _permission_smoke(ready=True),
        build_fixture_native_cursor_follow_smoke_result(),
    )
    plan = build_real_capture_session_plan(intent, readiness, build_sensitive_app_filter_result())

    assert plan.plan_id == REAL_CAPTURE_SESSION_PLAN_ID
    assert plan.state == "ready"
    assert "cortex-shadow-clicker" in plan.cursor_overlay_command
    assert not plan.memory_writes_enabled
    assert not plan.external_effects_enabled
    assert not plan.raw_screen_storage_enabled


def test_start_and_stop_receipts_keep_memory_writes_off():
    bundle = build_real_capture_control_bundle(
        permission_smoke=_permission_smoke(ready=True),
        now=datetime(2026, 5, 2, 16, 0, tzinfo=UTC),
    )

    assert bundle.start_receipt.receipt_id == REAL_CAPTURE_START_RECEIPT_ID
    assert bundle.start_receipt.observation_active
    assert bundle.start_receipt.cursor_overlay_running
    assert bundle.start_receipt.screen_capture_running
    assert not bundle.start_receipt.raw_screen_storage_enabled
    assert not bundle.start_receipt.memory_write_allowed
    assert bundle.stop_receipt.receipt_id == REAL_CAPTURE_STOP_RECEIPT_ID
    assert not bundle.stop_receipt.observation_active
    assert not bundle.stop_receipt.cursor_overlay_running

    unsafe = bundle.session_plan.model_copy(
        update={"readiness": bundle.session_plan.readiness.model_copy(update={"can_start_screen_capture": True})}
    )
    receipt = build_capture_start_receipt(unsafe)
    assert receipt.confirmation_observed


def test_ephemeral_raw_ref_policy_uses_temp_ttl_and_no_memory_writes():
    policy = build_ephemeral_raw_ref_policy(now=datetime(2026, 5, 2, 16, 0, tzinfo=UTC))

    assert policy.policy_id == REAL_CAPTURE_EPHEMERAL_RAW_REF_ID
    assert policy.ttl_seconds == 600
    assert policy.storage_root.startswith("/var/") or policy.storage_root.startswith("/tmp/")
    assert not policy.durable_storage_allowed
    assert not policy.memory_write_allowed_from_raw


def test_observation_sampler_is_count_only_and_prompt_injection_screened():
    sampler = build_observation_sampler_plan()

    assert sampler.sampler_id == REAL_CAPTURE_OBSERVATION_SAMPLER_ID
    assert sampler.output_shape == "count_only_receipts"
    assert not sampler.include_raw_pixels
    assert not sampler.include_accessibility_values
    assert sampler.prompt_injection_screening_required


def test_dashboard_capture_control_panel_is_honest_about_static_button_boundary():
    bundle = build_real_capture_control_bundle(
        permission_smoke=_permission_smoke(ready=True),
        now=datetime(2026, 5, 2, 16, 0, tzinfo=UTC),
    )

    assert bundle.dashboard_panel.panel_id == DASHBOARD_CAPTURE_CONTROL_ID
    assert bundle.dashboard_panel.primary_button_label == "Turn On Cortex"
    assert bundle.dashboard_panel.local_only
    assert bundle.dashboard_panel.requires_confirmation
    assert bundle.dashboard_panel.shows_shadow_clicker_status
    assert not bundle.dashboard_panel.starts_from_static_dashboard
    assert not bundle.dashboard_panel.raw_payload_returned


def test_real_capture_control_bundle_ties_all_ten_slices_together():
    bundle = build_real_capture_control_bundle(
        permission_smoke=_permission_smoke(ready=True),
        now=datetime(2026, 5, 2, 16, 0, tzinfo=UTC),
    )

    assert bundle.passed
    assert bundle.intent.intent_id == REAL_CAPTURE_INTENT_ID
    assert bundle.readiness.readiness_id == REAL_CAPTURE_READINESS_ID
    assert bundle.sensitive_filter.filter_id == REAL_CAPTURE_SENSITIVE_APP_FILTER_ID
    assert bundle.session_plan.plan_id == REAL_CAPTURE_SESSION_PLAN_ID
    assert bundle.start_receipt.receipt_id == REAL_CAPTURE_START_RECEIPT_ID
    assert bundle.stop_receipt.receipt_id == REAL_CAPTURE_STOP_RECEIPT_ID
    assert bundle.ephemeral_raw_ref_policy.policy_id == REAL_CAPTURE_EPHEMERAL_RAW_REF_ID
    assert bundle.sampler_plan.sampler_id == REAL_CAPTURE_OBSERVATION_SAMPLER_ID
    assert bundle.native_cursor_follow.passed
    assert bundle.dashboard_panel.panel_id == DASHBOARD_CAPTURE_CONTROL_ID
