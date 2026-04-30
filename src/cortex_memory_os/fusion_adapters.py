"""Local semantic, sparse, and graph adapters for hybrid context fusion."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from datetime import datetime

from pydantic import Field, model_validator

from cortex_memory_os.contracts import EvidenceType, MemoryRecord, StrictModel, TemporalEdge
from cortex_memory_os.hybrid_index import (
    HYBRID_CONTEXT_FUSION_POLICY_REF,
    HybridIndexCandidate,
    build_memory_fusion_candidate,
)

REAL_VECTOR_INDEX_ADAPTER_ID = "REAL-VECTOR-INDEX-ADAPTER-001"
LOCAL_FUSION_ADAPTER_POLICY_REF = "policy_local_fusion_adapters_v1"

_PROMPT_INJECTION_PATTERNS = (
    "ignore previous",
    "ignore all previous",
    "developer message",
    "system prompt",
    "reveal secrets",
    "disable safeguards",
)

_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "for",
    "from",
    "in",
    "into",
    "is",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}


class LocalFusionQuery(StrictModel):
    query: str = Field(min_length=1)
    focus_refs: list[str] = Field(default_factory=list)
    policy_refs: list[str] = Field(
        default_factory=lambda: [LOCAL_FUSION_ADAPTER_POLICY_REF]
    )

    @model_validator(mode="after")
    def require_policy_ref(self) -> LocalFusionQuery:
        if LOCAL_FUSION_ADAPTER_POLICY_REF not in self.policy_refs:
            raise ValueError("local fusion queries require policy refs")
        return self


class LocalFusionAdapterScores(StrictModel):
    memory_id: str = Field(min_length=1)
    semantic_score: float = Field(ge=0.0, le=1.0)
    sparse_score: float = Field(ge=0.0, le=1.0)
    graph_score: float = Field(ge=0.0, le=1.0)
    prompt_injection_risk: float = Field(ge=0.0, le=1.0)
    contradiction_penalty: float = Field(ge=0.0, le=1.0)
    source_ref_count: int = Field(ge=0)
    content_redacted: bool = True
    policy_refs: list[str] = Field(
        default_factory=lambda: [
            LOCAL_FUSION_ADAPTER_POLICY_REF,
            HYBRID_CONTEXT_FUSION_POLICY_REF,
        ]
    )

    @model_validator(mode="after")
    def enforce_redacted_scores(self) -> LocalFusionAdapterScores:
        if not self.content_redacted:
            raise ValueError("local fusion adapter scores must be redacted")
        if LOCAL_FUSION_ADAPTER_POLICY_REF not in self.policy_refs:
            raise ValueError("local fusion adapter scores require local policy refs")
        if HYBRID_CONTEXT_FUSION_POLICY_REF not in self.policy_refs:
            raise ValueError("local fusion adapter scores require fusion policy refs")
        return self


class LocalSemanticAdapter:
    """Deterministic lexical semantic fallback for local-first development."""

    def score(self, memory: MemoryRecord, query: LocalFusionQuery) -> float:
        query_tokens = _tokens(query.query)
        if not query_tokens:
            return 0.0
        memory_tokens = _tokens(
            " ".join(
                [
                    memory.content,
                    memory.type.value,
                    memory.scope.value,
                    " ".join(memory.allowed_influence),
                    " ".join(memory.forbidden_influence),
                ]
            )
        )
        direct_overlap = _coverage(query_tokens, memory_tokens)
        fuzzy_overlap = _coverage(_prefixes(query_tokens), _prefixes(memory_tokens))
        return _clamp((direct_overlap * 0.72) + (fuzzy_overlap * 0.28))


class LocalSparseAdapter:
    """Exact-token adapter standing in for a future BM25 or keyword index."""

    def score(self, memory: MemoryRecord, query: LocalFusionQuery) -> float:
        query_tokens = _tokens(query.query)
        if not query_tokens:
            return 0.0
        document_tokens = _tokens(
            " ".join([memory.content, *memory.allowed_influence, *memory.source_refs])
        )
        return _coverage(query_tokens, document_tokens)


class LocalGraphAdapter:
    """Graph-neighborhood scorer over already-compiled temporal edges."""

    def __init__(self, edges: Iterable[TemporalEdge] = ()):
        self._edges = list(edges)

    def score(self, memory: MemoryRecord, query: LocalFusionQuery) -> float:
        query_tokens = _tokens(query.query)
        focus_refs = set(query.focus_refs)
        best_score = 0.0

        for edge in self._edges:
            if memory.memory_id not in edge.source_refs and not (
                focus_refs and focus_refs.intersection(edge.source_refs)
            ):
                continue
            edge_tokens = _tokens(
                " ".join(
                    [edge.subject, edge.predicate, edge.object, *edge.source_refs]
                )
            )
            score = 0.45
            score += _coverage(query_tokens, edge_tokens) * 0.40
            if focus_refs and focus_refs.intersection(edge.source_refs):
                score += 0.15
            best_score = max(best_score, _clamp(score))

        return best_score


def build_local_fusion_candidates(
    memories: Iterable[MemoryRecord],
    query: str | LocalFusionQuery,
    *,
    temporal_edges: Iterable[TemporalEdge] = (),
    now: datetime | None = None,
    prompt_injection_risks: Mapping[str, float] | None = None,
) -> list[HybridIndexCandidate]:
    """Score memories with local adapters and return fusion-ready candidates."""

    local_query = query if isinstance(query, LocalFusionQuery) else LocalFusionQuery(query=query)
    semantic_adapter = LocalSemanticAdapter()
    sparse_adapter = LocalSparseAdapter()
    graph_adapter = LocalGraphAdapter(temporal_edges)
    risk_overrides = prompt_injection_risks or {}

    candidates: list[HybridIndexCandidate] = []
    for memory in memories:
        scores = score_memory_with_local_adapters(
            memory,
            local_query,
            semantic_adapter=semantic_adapter,
            sparse_adapter=sparse_adapter,
            graph_adapter=graph_adapter,
            prompt_injection_risk=risk_overrides.get(memory.memory_id),
        )
        candidates.append(
            build_memory_fusion_candidate(
                memory,
                semantic_score=scores.semantic_score,
                sparse_score=scores.sparse_score,
                graph_score=scores.graph_score,
                now=now,
                prompt_injection_risk=scores.prompt_injection_risk,
                contradiction_penalty=scores.contradiction_penalty,
            )
        )
    return candidates


def score_memory_with_local_adapters(
    memory: MemoryRecord,
    query: LocalFusionQuery,
    *,
    semantic_adapter: LocalSemanticAdapter | None = None,
    sparse_adapter: LocalSparseAdapter | None = None,
    graph_adapter: LocalGraphAdapter | None = None,
    prompt_injection_risk: float | None = None,
) -> LocalFusionAdapterScores:
    semantic = semantic_adapter or LocalSemanticAdapter()
    sparse = sparse_adapter or LocalSparseAdapter()
    graph = graph_adapter or LocalGraphAdapter()
    detected_risk = (
        prompt_injection_risk
        if prompt_injection_risk is not None
        else _prompt_injection_risk(memory)
    )

    return LocalFusionAdapterScores(
        memory_id=memory.memory_id,
        semantic_score=semantic.score(memory, query),
        sparse_score=sparse.score(memory, query),
        graph_score=graph.score(memory, query),
        prompt_injection_risk=detected_risk,
        contradiction_penalty=0.20 if memory.contradicts else 0.0,
        source_ref_count=len(memory.source_refs),
    )


def _prompt_injection_risk(memory: MemoryRecord) -> float:
    lowered = memory.content.lower()
    if any(pattern in lowered for pattern in _PROMPT_INJECTION_PATTERNS):
        return 0.92
    if memory.evidence_type == EvidenceType.EXTERNAL_EVIDENCE:
        return 0.62
    return 0.0


def _tokens(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", value.lower())
        if len(token) > 1 and token not in _STOPWORDS
    }


def _prefixes(tokens: set[str]) -> set[str]:
    return {token[:5] for token in tokens if len(token) >= 5}


def _coverage(query_tokens: set[str], document_tokens: set[str]) -> float:
    if not query_tokens:
        return 0.0
    return len(query_tokens.intersection(document_tokens)) / len(query_tokens)


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))
