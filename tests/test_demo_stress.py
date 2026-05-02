from datetime import UTC, datetime
import json

import pytest

from cortex_memory_os.demo_readiness import DEMO_READINESS_POLICY_REF
from cortex_memory_os.demo_stress import (
    DEMO_STRESS_DEFAULT_ITERATIONS,
    DEMO_STRESS_ID,
    DEMO_STRESS_POLICY_REF,
    run_demo_stress,
)
from cortex_memory_os.screen_injection_stress import SCREEN_INJECTION_STRESS_POLICY_REF
from cortex_memory_os.synthetic_capture_ladder import SYNTHETIC_CAPTURE_LADDER_POLICY_REF


NOW = datetime(2026, 5, 1, 19, 0, tzinfo=UTC)


def test_demo_stress_receipt_runs_repeated_synthetic_loop():
    receipt = run_demo_stress(iterations=3, now=NOW)

    assert receipt.passed
    assert receipt.stress_ready
    assert receipt.safe_to_show_publicly
    assert receipt.benchmark_id == DEMO_STRESS_ID
    assert receipt.policy_ref == DEMO_STRESS_POLICY_REF
    assert receipt.iterations_requested == 3
    assert receipt.iterations_completed == 3
    assert receipt.readiness_passed_count == 3
    assert receipt.screen_injection_passed_count == 3
    assert receipt.gateway_executed_count > 0
    assert receipt.gateway_blocked_count > 0
    assert receipt.gateway_failed_count == 0
    assert receipt.gateway_raw_payload_count == 0
    assert receipt.gateway_external_effect_count == 0
    assert receipt.env_local_ignored_by_git is True
    assert receipt.env_local_tracked_by_git is False
    assert "uv run cortex-demo-stress --iterations 12 --json" in receipt.required_commands
    assert DEMO_STRESS_POLICY_REF in receipt.policy_refs
    assert DEMO_READINESS_POLICY_REF in receipt.policy_refs
    assert SCREEN_INJECTION_STRESS_POLICY_REF in receipt.policy_refs
    assert SYNTHETIC_CAPTURE_LADDER_POLICY_REF in receipt.policy_refs


def test_demo_stress_receipt_keeps_live_unsafe_surfaces_off():
    receipt = run_demo_stress(iterations=2, now=NOW)

    assert receipt.synthetic_only is True
    assert receipt.localhost_only is True
    assert receipt.real_screen_capture_started is False
    assert receipt.durable_raw_screen_storage_enabled is False
    assert receipt.raw_private_refs_returned is False
    assert receipt.secret_values_read is False
    assert receipt.model_secret_echo_attempted is False
    assert receipt.mutation_export_or_draft_enabled is False
    assert receipt.external_effect_enabled is False
    assert set(receipt.blocked_effects) >= {
        "real_screen_capture",
        "durable_raw_screen_storage",
        "raw_private_refs",
        "secret_echo",
        "mutation",
        "export",
        "draft_execution",
        "external_effect",
    }


def test_demo_stress_receipt_does_not_leak_prohibited_markers():
    receipt = run_demo_stress(iterations=2, now=NOW)
    payload = json.dumps(receipt.model_dump(mode="json"), sort_keys=True)

    assert receipt.prohibited_marker_count == 0
    assert "CORTEX_FAKE_TOKEN" not in payload
    assert "OPENAI_API_KEY=" not in payload
    assert "api_key=" not in payload
    assert "sk-" not in payload
    assert "Bearer " not in payload
    assert "raw://" not in payload
    assert "encrypted_blob://" not in payload
    assert "Ignore previous instructions" not in payload
    assert "Demo sealed context memory uses auth callback verification" not in payload
    assert "scene_demo_private_trace" not in payload
    assert "OAuth callback route mismatch" not in payload


def test_demo_stress_rejects_invalid_iteration_counts():
    with pytest.raises(ValueError, match="iterations"):
        run_demo_stress(iterations=0, now=NOW)

    with pytest.raises(ValueError, match="iterations"):
        run_demo_stress(iterations=51, now=NOW)


def test_demo_stress_default_iteration_count_is_bounded():
    receipt = run_demo_stress(now=NOW)

    assert receipt.iterations_requested == DEMO_STRESS_DEFAULT_ITERATIONS
    assert receipt.iterations_completed == DEMO_STRESS_DEFAULT_ITERATIONS
