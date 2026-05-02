from datetime import UTC, datetime

from cortex_memory_os.receipt_leak_stress import (
    RECEIPT_LEAK_STRESS_ID,
    RECEIPT_LEAK_STRESS_POLICY_REF,
    run_receipt_leak_stress,
)


def test_receipt_leak_stress_passes_across_dashboard_backbone_payloads():
    result = run_receipt_leak_stress(now=datetime(2026, 5, 2, 12, 0, tzinfo=UTC))

    assert result.proof_id == RECEIPT_LEAK_STRESS_ID
    assert result.policy_ref == RECEIPT_LEAK_STRESS_POLICY_REF
    assert result.passed
    assert result.checked_payload_count == 5
    assert result.prohibited_marker_count == 0
    assert result.content_redacted
    assert result.source_refs_redacted
    assert not result.key_material_visible
    assert not result.raw_private_data_retained
