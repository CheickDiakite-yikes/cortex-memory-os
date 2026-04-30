"""Context-pack integration for local hybrid retrieval diagnostics."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime

from cortex_memory_os.contracts import (
    HYBRID_FUSION_CONTEXT_DIAGNOSTIC_POLICY_REF,
    HybridFusionContextDiagnostic,
    MemoryRecord,
    TemporalEdge,
)
from cortex_memory_os.fusion_adapters import (
    LOCAL_FUSION_ADAPTER_POLICY_REF,
    LocalFusionQuery,
    build_local_fusion_candidates,
)
from cortex_memory_os.hybrid_index import (
    HYBRID_CONTEXT_FUSION_POLICY_REF,
    HybridFusionResult,
    fuse_hybrid_candidates,
)

HYBRID_FUSION_CONTEXT_PACK_INTEGRATION_ID = (
    "HYBRID-FUSION-CONTEXT-PACK-INTEGRATION-001"
)
CONTEXT_FUSION_STRESS_ID = "CONTEXT-FUSION-STRESS-001"


def build_context_fusion_diagnostics(
    memories: Iterable[MemoryRecord],
    query: str | LocalFusionQuery,
    *,
    temporal_edges: Iterable[TemporalEdge] = (),
    now: datetime | None = None,
    limit: int = 3,
) -> list[HybridFusionContextDiagnostic]:
    """Return metadata-only hybrid fusion diagnostics for context packs.

    Memory content and source refs are consumed only inside local scoring.
    The returned diagnostics keep source refs collapsed to counts so agents
    can debug retrieval quality without receiving a second memory-content lane.
    """

    fusion_query = query if isinstance(query, LocalFusionQuery) else LocalFusionQuery(query=query)
    candidates = build_local_fusion_candidates(
        memories,
        fusion_query,
        temporal_edges=temporal_edges,
        now=now,
    )
    return [
        _diagnostic_from_fusion_result(result)
        for result in fuse_hybrid_candidates(candidates, limit=limit)
    ]


def _diagnostic_from_fusion_result(
    result: HybridFusionResult,
) -> HybridFusionContextDiagnostic:
    return HybridFusionContextDiagnostic(
        memory_id=result.memory_id,
        score=round(result.score, 4),
        included=result.included,
        excluded_reason_tags=list(result.excluded_reason_tags),
        component_scores={
            key: round(value, 4) for key, value in result.component_scores.items()
        },
        source_ref_count=len(result.source_refs),
        content_redacted=True,
        source_refs_redacted=True,
        policy_refs=[
            HYBRID_FUSION_CONTEXT_DIAGNOSTIC_POLICY_REF,
            LOCAL_FUSION_ADAPTER_POLICY_REF,
            HYBRID_CONTEXT_FUSION_POLICY_REF,
        ],
    )
