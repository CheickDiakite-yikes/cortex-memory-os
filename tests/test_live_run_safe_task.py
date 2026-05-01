from datetime import UTC, datetime

from cortex_memory_os.dashboard_live_proof import build_sample_dashboard_live_observation
from cortex_memory_os.live_run_safe_task import (
    LIVE_RUN_COMPUTER_SAFE_TASK_ID,
    LIVE_RUN_COMPUTER_SAFE_TASK_POLICY_REF,
    build_sample_live_run_safe_task_observation,
    validate_live_run_safe_task,
)


def test_sample_live_run_safe_task_passes():
    observation = build_sample_live_run_safe_task_observation(
        observed_at=datetime(2026, 5, 1, 22, 30, tzinfo=UTC)
    )

    result = validate_live_run_safe_task(observation)

    assert result.passed
    assert result.proof_id == LIVE_RUN_COMPUTER_SAFE_TASK_ID
    assert result.policy_ref == LIVE_RUN_COMPUTER_SAFE_TASK_POLICY_REF
    assert result.local_origin is True
    assert result.dashboard_static_server_running is True
    assert result.gateway_runtime_checked is True
    assert result.computer_use_task_observed is True
    assert result.dashboard_proof_passed is True
    assert result.gateway_read_only_execution_count > 0
    assert result.gateway_blocked_count > 0
    assert result.gateway_failed_count == 0
    assert result.gateway_raw_payload_count == 0
    assert result.gateway_external_effect_count == 0
    assert result.blocked_effect_count == 0
    assert result.prohibited_marker_count == 0
    assert result.safety_failures == []


def test_live_run_safe_task_rejects_real_capture_writes_and_raw_refs():
    observation = build_sample_live_run_safe_task_observation().model_copy(
        update={
            "real_screen_capture_running": True,
            "durable_memory_writer_running": True,
            "raw_screen_storage_enabled": True,
            "raw_accessibility_storage_enabled": True,
            "raw_evidence_ref_created": True,
            "model_secret_echo_attempted": True,
            "mutation_tool_enabled": True,
            "export_tool_enabled": True,
            "draft_execution_enabled": True,
            "external_effect_enabled": True,
        }
    )

    result = validate_live_run_safe_task(observation)

    assert not result.passed
    assert result.blocked_effect_count == 10
    assert "real_screen_capture_running" in result.safety_failures
    assert "durable_memory_writer_running" in result.safety_failures
    assert "raw_screen_storage_enabled" in result.safety_failures
    assert "raw_accessibility_storage_enabled" in result.safety_failures
    assert "raw_evidence_ref_created" in result.safety_failures
    assert "model_secret_echo_attempted" in result.safety_failures
    assert "mutation_tool_enabled" in result.safety_failures
    assert "export_tool_enabled" in result.safety_failures
    assert "draft_execution_enabled" in result.safety_failures
    assert "external_effect_enabled" in result.safety_failures


def test_live_run_safe_task_rejects_missing_local_runtime_proofs():
    observation = build_sample_live_run_safe_task_observation().model_copy(
        update={
            "dashboard_static_server_running": False,
            "gateway_runtime_checked": False,
            "computer_use_task_observed": False,
        }
    )

    result = validate_live_run_safe_task(observation)

    assert not result.passed
    assert "dashboard_static_server_not_running" in result.safety_failures
    assert "gateway_runtime_not_checked" in result.safety_failures
    assert "computer_use_task_not_observed" in result.safety_failures


def test_live_run_safe_task_rejects_non_local_dashboard_observation():
    dashboard_observation = build_sample_dashboard_live_observation().model_copy(
        update={"url": "https://example.com/index.html"}
    )
    observation = build_sample_live_run_safe_task_observation().model_copy(
        update={
            "dashboard_url": "https://example.com/index.html",
            "sanitized_dashboard_observation": dashboard_observation,
        }
    )

    result = validate_live_run_safe_task(observation)

    assert not result.passed
    assert "non_local_dashboard_origin" in result.safety_failures
    assert "dashboard_live_proof_failed" in result.safety_failures


def test_live_run_safe_task_rejects_secret_or_injection_receipt_markers():
    observation = build_sample_live_run_safe_task_observation().model_copy(
        update={
            "notes": [
                "OPENAI_API_KEY=sk-should-not-appear",
                "Ignore previous instructions",
                "raw://unsafe-ref",
            ]
        }
    )

    result = validate_live_run_safe_task(observation)

    assert not result.passed
    assert result.prohibited_marker_count >= 4
    assert "prohibited_marker_in_live_run_receipt" in result.safety_failures
