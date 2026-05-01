from datetime import UTC, datetime

from cortex_memory_os.synthetic_capture_ladder import (
    SYNTHETIC_CAPTURE_LADDER_ID,
    SYNTHETIC_CAPTURE_LADDER_POLICY_REF,
    SYNTHETIC_CAPTURE_MEMORY_ID,
    run_synthetic_capture_ladder,
)


def test_synthetic_capture_ladder_passes_end_to_end():
    result = run_synthetic_capture_ladder(
        now=datetime(2026, 5, 1, 12, 0, tzinfo=UTC)
    )

    assert result.passed
    assert result.proof_id == SYNTHETIC_CAPTURE_LADDER_ID
    assert result.policy_ref == SYNTHETIC_CAPTURE_LADDER_POLICY_REF
    assert result.synthetic_disposable_page_created is True
    assert result.synthetic_page_only is True
    assert result.temp_storage_used is True
    assert result.temp_paths_redacted is True
    assert result.real_screen_capture_started is False
    assert result.consented_real_capture_started is False
    assert result.raw_ref_created is True
    assert result.raw_ref_scheme == "vault"
    assert result.raw_ref_readable_before_expiry is True
    assert result.raw_ref_deleted_after_expiry is True
    assert result.raw_payload_committed is False
    assert result.durable_synthetic_memory_written is True
    assert result.local_test_db_used is True
    assert result.audit_written is True
    assert result.audit_human_visible is True
    assert result.retrieval_hit is True
    assert result.context_pack_hit is True
    assert result.memory_id == SYNTHETIC_CAPTURE_MEMORY_ID
    assert SYNTHETIC_CAPTURE_MEMORY_ID in result.retrieved_memory_ids
    assert SYNTHETIC_CAPTURE_MEMORY_ID in result.context_pack_memory_ids
    assert result.safety_failures == []


def test_synthetic_capture_ladder_blocks_secret_before_writes():
    result = run_synthetic_capture_ladder(
        now=datetime(2026, 5, 1, 12, 5, tzinfo=UTC)
    )

    assert result.passed
    assert result.secret_firewall_decision == "mask"
    assert result.secret_redaction_count == 1
    assert result.secret_raw_write_blocked is True
    assert result.secret_memory_write_blocked is True
    assert result.secret_redacted_before_write is True
    assert result.secret_audit_summary_redacted is True
    assert result.secret_value_leak_count == 0
