from datetime import UTC, datetime, timedelta

import pytest

from cortex_memory_os.contracts import EvidenceType, MemoryRecord, Sensitivity
from cortex_memory_os.fixtures import load_json
from cortex_memory_os.hybrid_index import (
    CONTEXT_FUSION_INDEX_STUB_ID,
    HYBRID_CONTEXT_FUSION_POLICY_REF,
    HybridFusionResult,
    HybridIndexCandidate,
    build_memory_fusion_candidate,
    fuse_hybrid_candidates,
)


def test_hybrid_fusion_prefers_trusted_graph_relevant_current_memory():
    now = datetime(2026, 4, 30, 12, 0, tzinfo=UTC)
    base = MemoryRecord.model_validate(load_json("tests/fixtures/memory_preference.json"))
    trusted = build_memory_fusion_candidate(
        base.model_copy(
            update={
                "memory_id": "mem_trusted_graph",
                "evidence_type": EvidenceType.USER_CONFIRMED,
                "created_at": now - timedelta(days=1),
                "sensitivity": Sensitivity.PUBLIC,
            }
        ),
        semantic_score=0.74,
        sparse_score=0.52,
        graph_score=0.91,
        now=now,
    )
    risky_similar = build_memory_fusion_candidate(
        base.model_copy(
            update={
                "memory_id": "mem_similar_but_risky",
                "evidence_type": EvidenceType.EXTERNAL_EVIDENCE,
                "created_at": now - timedelta(days=420),
                "sensitivity": Sensitivity.REGULATED,
            }
        ),
        semantic_score=0.98,
        sparse_score=0.88,
        graph_score=0.14,
        now=now,
        prompt_injection_risk=0.80,
    )

    results = fuse_hybrid_candidates([risky_similar, trusted])

    assert CONTEXT_FUSION_INDEX_STUB_ID == "CONTEXT-FUSION-INDEX-STUB-001"
    assert [result.memory_id for result in results] == [
        "mem_trusted_graph",
        "mem_similar_but_risky",
    ]
    assert results[0].included
    assert not results[1].included
    assert "prompt_injection_risk" in results[1].excluded_reason_tags
    assert "privacy_risk" not in results[0].excluded_reason_tags


def test_hybrid_candidate_rejects_raw_refs_and_missing_policy():
    with pytest.raises(ValueError, match="raw source refs"):
        HybridIndexCandidate(
            memory_id="mem_raw",
            semantic_score=0.5,
            sparse_score=0.5,
            graph_score=0.5,
            recency_score=0.5,
            trust_score=0.5,
            source_refs=["raw://screen/frame_001"],
        )

    with pytest.raises(ValueError, match="fusion policy ref"):
        HybridIndexCandidate(
            memory_id="mem_policy",
            semantic_score=0.5,
            sparse_score=0.5,
            graph_score=0.5,
            recency_score=0.5,
            trust_score=0.5,
            source_refs=["scene:one"],
            policy_refs=["policy_other"],
        )


def test_hybrid_results_are_content_redacted_and_exclusion_reasoned():
    result = fuse_hybrid_candidates(
        [
            HybridIndexCandidate(
                memory_id="mem_prompt_risk",
                content_preview="This preview stays internal to the candidate.",
                semantic_score=0.99,
                sparse_score=0.96,
                graph_score=0.95,
                recency_score=1.0,
                trust_score=0.18,
                source_refs=["external:webpage"],
                prompt_injection_risk=0.75,
            )
        ]
    )[0]

    assert not result.included
    assert result.content_redacted is True
    assert result.excluded_reason_tags == ["prompt_injection_risk"]
    assert HYBRID_CONTEXT_FUSION_POLICY_REF in result.policy_refs
    assert "content_preview" not in result.model_dump()

    with pytest.raises(ValueError, match="content redacted"):
        HybridFusionResult(
            memory_id="mem_bad",
            score=0.1,
            included=False,
            excluded_reason_tags=["score_below_threshold"],
            component_scores={},
            source_refs=["scene:one"],
            content_redacted=False,
            policy_refs=[HYBRID_CONTEXT_FUSION_POLICY_REF],
        )


def test_hybrid_fusion_uses_deterministic_tie_ordering():
    candidates = [
        HybridIndexCandidate(
            memory_id="mem_b",
            semantic_score=0.5,
            sparse_score=0.5,
            graph_score=0.5,
            recency_score=0.5,
            trust_score=0.5,
            source_refs=["scene:b"],
        ),
        HybridIndexCandidate(
            memory_id="mem_a",
            semantic_score=0.5,
            sparse_score=0.5,
            graph_score=0.5,
            recency_score=0.5,
            trust_score=0.5,
            source_refs=["scene:a"],
        ),
    ]

    results = fuse_hybrid_candidates(candidates)

    assert [result.memory_id for result in results] == ["mem_a", "mem_b"]
