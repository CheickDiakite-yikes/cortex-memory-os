"""Dependency-free hybrid retrieval fusion contracts.

This module defines the stable scoring seam that future vector, sparse, and
graph adapters should feed. It deliberately does not embed, index, or call a
network service.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime

from pydantic import Field, model_validator

from cortex_memory_os.contracts import EvidenceType, MemoryRecord, Sensitivity, StrictModel

CONTEXT_FUSION_INDEX_STUB_ID = "CONTEXT-FUSION-INDEX-STUB-001"
HYBRID_CONTEXT_FUSION_POLICY_REF = "policy_hybrid_context_fusion_index_v1"

DEFAULT_FUSION_THRESHOLD = 0.05
HIGH_PROMPT_INJECTION_RISK = 0.75
HIGH_PRIVACY_RISK = 0.85


class HybridFusionWeights(StrictModel):
    semantic: float = Field(default=0.34, ge=0.0)
    sparse: float = Field(default=0.20, ge=0.0)
    graph: float = Field(default=0.22, ge=0.0)
    recency: float = Field(default=0.12, ge=0.0)
    trust: float = Field(default=0.12, ge=0.0)

    @property
    def total(self) -> float:
        return self.semantic + self.sparse + self.graph + self.recency + self.trust

    @model_validator(mode="after")
    def require_some_signal(self) -> HybridFusionWeights:
        if self.total <= 0:
            raise ValueError("at least one fusion weight must be positive")
        return self


class HybridIndexCandidate(StrictModel):
    memory_id: str = Field(min_length=1)
    content_preview: str | None = Field(default=None, max_length=180)
    semantic_score: float = Field(ge=0.0, le=1.0)
    sparse_score: float = Field(ge=0.0, le=1.0)
    graph_score: float = Field(ge=0.0, le=1.0)
    recency_score: float = Field(ge=0.0, le=1.0)
    trust_score: float = Field(ge=0.0, le=1.0)
    source_refs: list[str] = Field(min_length=1)
    privacy_risk: float = Field(default=0.0, ge=0.0, le=1.0)
    prompt_injection_risk: float = Field(default=0.0, ge=0.0, le=1.0)
    staleness_penalty: float = Field(default=0.0, ge=0.0, le=1.0)
    contradiction_penalty: float = Field(default=0.0, ge=0.0, le=1.0)
    policy_refs: list[str] = Field(default_factory=lambda: [HYBRID_CONTEXT_FUSION_POLICY_REF])

    @model_validator(mode="after")
    def enforce_safe_candidate_refs(self) -> HybridIndexCandidate:
        if HYBRID_CONTEXT_FUSION_POLICY_REF not in self.policy_refs:
            raise ValueError("hybrid fusion candidates require the fusion policy ref")
        if any(source_ref.startswith("raw://") for source_ref in self.source_refs):
            raise ValueError("hybrid fusion candidates cannot carry raw source refs")
        return self


class HybridFusionResult(StrictModel):
    memory_id: str = Field(min_length=1)
    score: float = Field(ge=0.0, le=1.0)
    included: bool
    excluded_reason_tags: list[str] = Field(default_factory=list)
    component_scores: dict[str, float]
    source_refs: list[str] = Field(min_length=1)
    content_redacted: bool = True
    policy_refs: list[str]

    @model_validator(mode="after")
    def enforce_result_redaction(self) -> HybridFusionResult:
        if not self.content_redacted:
            raise ValueError("hybrid fusion results must keep content redacted")
        if HYBRID_CONTEXT_FUSION_POLICY_REF not in self.policy_refs:
            raise ValueError("hybrid fusion results require the fusion policy ref")
        if self.included and self.excluded_reason_tags:
            raise ValueError("included fusion results cannot carry exclusion reasons")
        if not self.included and not self.excluded_reason_tags:
            raise ValueError("excluded fusion results require reason tags")
        return self


def fuse_hybrid_candidates(
    candidates: Iterable[HybridIndexCandidate],
    *,
    weights: HybridFusionWeights | None = None,
    limit: int = 5,
    minimum_score: float = DEFAULT_FUSION_THRESHOLD,
) -> list[HybridFusionResult]:
    """Fuse candidate scores while preserving safe exclusion diagnostics.

    ``limit`` caps included results. Excluded results remain in the returned
    list as redacted diagnostics so UIs and benchmark receipts can explain why
    a candidate was not eligible.
    """

    if limit < 1:
        raise ValueError("limit must be at least 1")
    if minimum_score < 0 or minimum_score > 1:
        raise ValueError("minimum_score must be between 0 and 1")

    fusion_weights = weights or HybridFusionWeights()
    results = [
        _fuse_candidate(
            candidate,
            fusion_weights,
            minimum_score=minimum_score,
        )
        for candidate in candidates
    ]
    included = sorted(
        (result for result in results if result.included),
        key=lambda result: (-result.score, result.memory_id),
    )[:limit]
    excluded = sorted(
        (result for result in results if not result.included),
        key=lambda result: (-result.score, result.memory_id),
    )
    return included + excluded


def build_memory_fusion_candidate(
    memory: MemoryRecord,
    *,
    semantic_score: float,
    sparse_score: float,
    graph_score: float,
    now: datetime | None = None,
    prompt_injection_risk: float = 0.0,
    contradiction_penalty: float = 0.0,
) -> HybridIndexCandidate:
    """Build a fusion candidate from an already-governed memory record."""

    timestamp = now or datetime.now(UTC)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=UTC)
    recency_score = _recency_score(memory.created_at, timestamp)
    staleness_penalty = _staleness_penalty(memory.created_at, timestamp)
    trust_score = _trust_score(memory.evidence_type)
    privacy_risk = _privacy_risk(memory.sensitivity)
    content_preview = _safe_content_preview(memory)

    return HybridIndexCandidate(
        memory_id=memory.memory_id,
        content_preview=content_preview,
        semantic_score=semantic_score,
        sparse_score=sparse_score,
        graph_score=graph_score,
        recency_score=recency_score,
        trust_score=trust_score,
        source_refs=memory.source_refs,
        privacy_risk=privacy_risk,
        prompt_injection_risk=prompt_injection_risk,
        staleness_penalty=staleness_penalty,
        contradiction_penalty=contradiction_penalty,
    )


def _fuse_candidate(
    candidate: HybridIndexCandidate,
    weights: HybridFusionWeights,
    *,
    minimum_score: float,
) -> HybridFusionResult:
    raw_score = (
        candidate.semantic_score * weights.semantic
        + candidate.sparse_score * weights.sparse
        + candidate.graph_score * weights.graph
        + candidate.recency_score * weights.recency
        + candidate.trust_score * weights.trust
    ) / weights.total
    penalty = (
        candidate.privacy_risk * 0.18
        + candidate.prompt_injection_risk * 0.42
        + candidate.staleness_penalty * 0.22
        + candidate.contradiction_penalty * 0.18
    )
    score = _clamp(raw_score - penalty)
    excluded_reason_tags = _exclusion_reasons(candidate, score, minimum_score)

    return HybridFusionResult(
        memory_id=candidate.memory_id,
        score=score,
        included=not excluded_reason_tags,
        excluded_reason_tags=excluded_reason_tags,
        component_scores={
            "semantic": candidate.semantic_score,
            "sparse": candidate.sparse_score,
            "graph": candidate.graph_score,
            "recency": candidate.recency_score,
            "trust": candidate.trust_score,
            "privacy_risk": candidate.privacy_risk,
            "prompt_injection_risk": candidate.prompt_injection_risk,
            "staleness_penalty": candidate.staleness_penalty,
            "contradiction_penalty": candidate.contradiction_penalty,
        },
        source_refs=candidate.source_refs,
        content_redacted=True,
        policy_refs=candidate.policy_refs,
    )


def _exclusion_reasons(
    candidate: HybridIndexCandidate,
    score: float,
    minimum_score: float,
) -> list[str]:
    reasons: list[str] = []
    if candidate.prompt_injection_risk >= HIGH_PROMPT_INJECTION_RISK:
        reasons.append("prompt_injection_risk")
    if candidate.privacy_risk >= HIGH_PRIVACY_RISK:
        reasons.append("privacy_risk")
    if score < minimum_score:
        reasons.append("score_below_threshold")
    return reasons


def _trust_score(evidence_type: EvidenceType) -> float:
    return {
        EvidenceType.USER_CONFIRMED: 1.0,
        EvidenceType.OBSERVED: 0.86,
        EvidenceType.OBSERVED_AND_INFERRED: 0.74,
        EvidenceType.INFERRED: 0.42,
        EvidenceType.EXTERNAL_EVIDENCE: 0.18,
    }[evidence_type]


def _privacy_risk(sensitivity: Sensitivity) -> float:
    return {
        Sensitivity.PUBLIC: 0.0,
        Sensitivity.LOW: 0.04,
        Sensitivity.PRIVATE_WORK: 0.16,
        Sensitivity.CONFIDENTIAL: 0.42,
        Sensitivity.REGULATED: 0.74,
        Sensitivity.SECRET: 1.0,
    }[sensitivity]


def _recency_score(created_at: datetime, now: datetime) -> float:
    age_days = max((now - _as_aware_utc(created_at)).days, 0)
    if age_days <= 1:
        return 1.0
    if age_days <= 7:
        return 0.82
    if age_days <= 30:
        return 0.64
    if age_days <= 90:
        return 0.42
    if age_days <= 365:
        return 0.22
    return 0.08


def _staleness_penalty(created_at: datetime, now: datetime) -> float:
    age_days = max((now - _as_aware_utc(created_at)).days, 0)
    if age_days <= 30:
        return 0.0
    if age_days <= 90:
        return 0.10
    if age_days <= 365:
        return 0.24
    return 0.50


def _safe_content_preview(memory: MemoryRecord) -> str | None:
    if memory.sensitivity in {Sensitivity.CONFIDENTIAL, Sensitivity.REGULATED, Sensitivity.SECRET}:
        return None
    return memory.content[:180]


def _as_aware_utc(timestamp: datetime) -> datetime:
    if timestamp.tzinfo is None:
        return timestamp.replace(tzinfo=UTC)
    return timestamp.astimezone(UTC)


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))
