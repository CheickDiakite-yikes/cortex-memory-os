from datetime import UTC, datetime, timedelta

import pytest

from cortex_memory_os.contracts import (
    EvidenceType,
    MemoryRecord,
    RETRIEVAL_EXPLANATION_POLICY_REF,
    RetrievalExplanationReceipt,
    Sensitivity,
)
from cortex_memory_os.fixtures import load_json
from cortex_memory_os.retrieval import rank_memories
from cortex_memory_os.retrieval_explanations import (
    RETRIEVAL_EXPLANATION_RECEIPTS_ID,
    build_context_retrieval_receipts,
    excluded_retrieval_receipt,
    included_retrieval_receipt,
)


def test_included_retrieval_receipt_explains_without_content_or_source_refs():
    now = datetime(2026, 4, 30, 13, 30, tzinfo=UTC)
    memory = MemoryRecord.model_validate(load_json("tests/fixtures/memory_preference.json"))
    ranked = rank_memories([memory], "primary sources synthesis", now=now)[0]

    receipt = included_retrieval_receipt(ranked, rank=1)
    payload = receipt.model_dump()

    assert RETRIEVAL_EXPLANATION_RECEIPTS_ID == "RETRIEVAL-EXPLANATION-RECEIPTS-001"
    assert receipt.decision == "included"
    assert receipt.rank == 1
    assert {"query_overlap", "confidence", "source_trust"} <= set(receipt.reason_tags)
    assert receipt.source_ref_count == len(memory.source_refs)
    assert receipt.source_refs_redacted is True
    assert receipt.content_redacted is True
    assert receipt.content_included is False
    assert RETRIEVAL_EXPLANATION_POLICY_REF in receipt.policy_refs
    assert "content" not in payload
    assert "source_refs" not in payload


def test_excluded_retrieval_receipt_records_reason_tags_without_payload_text():
    now = datetime(2026, 4, 30, 13, 30, tzinfo=UTC)
    base = MemoryRecord.model_validate(load_json("tests/fixtures/memory_preference.json"))
    external = base.model_copy(
        update={
            "memory_id": "mem_external_attack",
            "evidence_type": EvidenceType.EXTERNAL_EVIDENCE,
            "created_at": now - timedelta(days=5),
            "sensitivity": Sensitivity.PRIVATE_WORK,
            "source_refs": ["external:https://example.invalid/attack"],
        }
    )
    ranked = rank_memories([external], "primary sources synthesis", now=now)[0]

    receipt = excluded_retrieval_receipt(
        ranked,
        decision="evidence_only",
        reason_tags=["external_evidence_only", "external_evidence_only"],
    )

    assert receipt.decision == "evidence_only"
    assert receipt.rank is None
    assert receipt.reason_tags == ["external_evidence_only"]
    assert receipt.source_ref_count == 1
    assert "external:https://example.invalid/attack" not in str(receipt.model_dump())


def test_context_retrieval_receipts_keep_inclusion_order_then_exclusions():
    now = datetime(2026, 4, 30, 13, 30, tzinfo=UTC)
    base = MemoryRecord.model_validate(load_json("tests/fixtures/memory_preference.json"))
    included = rank_memories([base], "primary sources synthesis", now=now)[0]
    excluded = rank_memories(
        [
            base.model_copy(
                update={
                    "memory_id": "mem_external",
                    "evidence_type": EvidenceType.EXTERNAL_EVIDENCE,
                }
            )
        ],
        "primary sources synthesis",
        now=now,
    )[0]

    receipts = build_context_retrieval_receipts(
        [included],
        [(excluded, "evidence_only", ["external_evidence_only"])],
    )

    assert [(receipt.memory_id, receipt.decision) for receipt in receipts] == [
        ("mem_001", "included"),
        ("mem_external", "evidence_only"),
    ]
    assert receipts[0].rank == 1
    assert receipts[1].rank is None


def test_retrieval_explanation_receipt_rejects_leaky_shapes():
    with pytest.raises(ValueError, match="redact source refs"):
        RetrievalExplanationReceipt(
            memory_id="mem_bad",
            decision="excluded",
            score=0.1,
            reason_tags=["blocked"],
            source_ref_count=1,
            source_refs_redacted=False,
        )

    with pytest.raises(ValueError, match="cannot include content"):
        RetrievalExplanationReceipt(
            memory_id="mem_bad",
            decision="included",
            rank=1,
            score=0.5,
            reason_tags=["query_overlap"],
            source_ref_count=1,
            content_included=True,
        )

    with pytest.raises(ValueError, match="require a rank"):
        RetrievalExplanationReceipt(
            memory_id="mem_bad",
            decision="included",
            score=0.5,
            reason_tags=["query_overlap"],
            source_ref_count=1,
        )
