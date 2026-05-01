from datetime import UTC, datetime
import json

from cortex_memory_os.demo_readiness import (
    DEMO_BLOCKED_EFFECTS,
    DEMO_READINESS_ID,
    DEMO_READINESS_POLICY_REF,
    run_demo_readiness,
)
from cortex_memory_os.encrypted_graph_index import UNIFIED_ENCRYPTED_GRAPH_INDEX_POLICY_REF
from cortex_memory_os.synthetic_capture_ladder import SYNTHETIC_CAPTURE_LADDER_POLICY_REF


def test_demo_readiness_receipt_is_safe_and_complete():
    receipt = run_demo_readiness(now=datetime(2026, 5, 1, 18, 0, tzinfo=UTC))

    assert receipt.passed
    assert receipt.demo_ready
    assert receipt.safe_to_show_publicly
    assert receipt.benchmark_id == DEMO_READINESS_ID
    assert receipt.policy_ref == DEMO_READINESS_POLICY_REF
    assert receipt.synthetic_only is True
    assert receipt.localhost_only is True
    assert receipt.real_screen_capture_started is False
    assert receipt.durable_raw_screen_storage_enabled is False
    assert receipt.raw_private_refs_returned is False
    assert receipt.secret_values_read is False
    assert receipt.model_secret_echo_attempted is False
    assert receipt.mutation_export_or_draft_enabled is False
    assert receipt.external_effect_enabled is False
    assert set(DEMO_BLOCKED_EFFECTS) <= set(receipt.blocked_effects)
    assert {check.name for check in receipt.checks} >= {
        "dashboard_safe_surface",
        "synthetic_capture_ladder",
        "encrypted_index_gateway_context",
        "env_local_secret_hygiene",
        "unsafe_effects_blocked",
    }
    assert all(check.passed for check in receipt.checks)
    assert len(receipt.demo_steps) == 4
    assert "uv run cortex-demo --json" in receipt.required_commands
    assert DEMO_READINESS_POLICY_REF in receipt.policy_refs
    assert SYNTHETIC_CAPTURE_LADDER_POLICY_REF in receipt.policy_refs
    assert UNIFIED_ENCRYPTED_GRAPH_INDEX_POLICY_REF in receipt.policy_refs


def test_demo_readiness_receipt_does_not_leak_raw_refs_or_secrets():
    receipt = run_demo_readiness(now=datetime(2026, 5, 1, 18, 0, tzinfo=UTC))
    payload = json.dumps(receipt.model_dump(mode="json"), sort_keys=True)

    assert receipt.prohibited_marker_count == 0
    assert "CORTEX_FAKE_TOKEN" not in payload
    assert "OPENAI_API_KEY=" not in payload
    assert "api_key=" not in payload
    assert "sk-" not in payload
    assert "raw://" not in payload
    assert "encrypted_blob://" not in payload
    assert "Demo sealed context memory uses auth callback verification" not in payload
    assert "scene_demo_private_trace" not in payload
    assert "OAuth callback route mismatch" not in payload


def test_demo_readiness_encrypted_index_check_is_metadata_only():
    receipt = run_demo_readiness(now=datetime(2026, 5, 1, 18, 0, tzinfo=UTC))
    check = next(item for item in receipt.checks if item.name == "encrypted_index_gateway_context")

    assert check.passed
    assert check.details["memory_id"] == "mem_demo_readiness_encrypted_index"
    assert check.details["write_token_digest_count"] > 0
    assert check.details["graph_token_digest_count"] > 0
    assert check.details["search_result_count"] == 1
    assert check.details["gateway_result_count"] == 1
    assert check.details["context_pack_memory_count"] == 1
    assert check.details["context_policy_ref_present"] is True
    assert check.details["prohibited_marker_count"] == 0
