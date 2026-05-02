from datetime import UTC, datetime

from cortex_memory_os.durable_synthetic_memory_receipts import (
    DURABLE_SYNTHETIC_MEMORY_RECEIPTS_ID,
    DURABLE_SYNTHETIC_MEMORY_RECEIPTS_POLICY_REF,
    run_durable_synthetic_memory_receipts,
)
from cortex_memory_os.encrypted_graph_index import UNIFIED_ENCRYPTED_GRAPH_INDEX_POLICY_REF
from cortex_memory_os.memory_encryption import MEMORY_ENCRYPTION_DEFAULT_POLICY_REF


def test_durable_synthetic_memory_receipt_writes_encrypted_metadata_only():
    receipt = run_durable_synthetic_memory_receipts(
        now=datetime(2026, 5, 2, 12, 0, tzinfo=UTC)
    )
    payload = receipt.model_dump_json()

    assert receipt.receipt_id.startswith("durable_synthetic_receipt_")
    assert receipt.policy_ref == DURABLE_SYNTHETIC_MEMORY_RECEIPTS_POLICY_REF
    assert DURABLE_SYNTHETIC_MEMORY_RECEIPTS_POLICY_REF in receipt.policy_refs
    assert MEMORY_ENCRYPTION_DEFAULT_POLICY_REF in receipt.policy_refs
    assert UNIFIED_ENCRYPTED_GRAPH_INDEX_POLICY_REF in receipt.policy_refs
    assert receipt.synthetic_only
    assert receipt.local_test_db_used
    assert receipt.encrypted_store_used
    assert receipt.durable_synthetic_memory_written
    assert not receipt.durable_private_memory_written
    assert not receipt.real_screen_capture_started
    assert not receipt.raw_ref_retained
    assert not receipt.raw_payload_included
    assert receipt.audit_written
    assert receipt.audit_human_visible
    assert receipt.db_plaintext_leak_count == 0
    assert receipt.prohibited_leak_count == 0
    assert receipt.index_write_receipt.content_redacted
    assert receipt.graph_write_receipt.graph_terms_redacted
    assert receipt.search_receipt.query_redacted
    assert "Synthetic durable memory receipt observed" not in payload
    assert "synthetic://durable-memory-receipt/source" not in payload
    assert "raw://" not in payload
    assert "encrypted_blob://" not in payload
    assert DURABLE_SYNTHETIC_MEMORY_RECEIPTS_ID.startswith("DURABLE-")
