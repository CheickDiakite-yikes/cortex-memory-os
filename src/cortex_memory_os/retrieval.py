"""Deterministic retrieval scoring before vector/graph fusion."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime

from cortex_memory_os.contracts import (
    EvidenceType,
    InfluenceLevel,
    MemoryRecord,
    MemoryStatus,
    ScopeLevel,
    Sensitivity,
)


NON_RETRIEVABLE_STATUSES = {
    MemoryStatus.DELETED,
    MemoryStatus.REVOKED,
    MemoryStatus.SUPERSEDED,
    MemoryStatus.QUARANTINED,
}


@dataclass(frozen=True)
class RetrievalScore:
    memory_id: str
    eligible: bool
    total: float
    query_relevance: float
    confidence_component: float
    source_trust_component: float
    recency_component: float
    status_penalty: float
    privacy_penalty: float
    staleness_penalty: float
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class RankedMemory:
    memory: MemoryRecord
    score: RetrievalScore


@dataclass(frozen=True)
class RetrievalScope:
    active_project: str | None = None
    agent_id: str | None = None
    session_id: str | None = None
    include_global: bool = True


def score_memory(
    memory: MemoryRecord,
    query: str,
    *,
    now: datetime | None = None,
    scope: RetrievalScope | None = None,
) -> RetrievalScore:
    timestamp = now or datetime.now(UTC)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=UTC)

    reasons: list[str] = []
    query_terms = tokenize(query)
    memory_terms = tokenize(memory.content)
    overlap = query_terms & memory_terms
    query_relevance = 0.0 if not query_terms else len(overlap) / len(query_terms)

    eligible = True
    if not query_terms:
        eligible = False
        reasons.append("empty_query")
    if not overlap:
        eligible = False
        reasons.append("no_query_overlap")
    if memory.status in NON_RETRIEVABLE_STATUSES:
        eligible = False
        reasons.append(f"status_{memory.status.value}")
    if memory.influence_level == InfluenceLevel.STORED_ONLY:
        eligible = False
        reasons.append("stored_only")
    if memory.valid_to is not None and memory.valid_to < timestamp.date():
        eligible = False
        reasons.append("expired_validity_window")
    if memory.sensitivity == Sensitivity.SECRET:
        eligible = False
        reasons.append("secret_sensitivity")
    scope_allowed, scope_reasons = _scope_allowed(memory, scope)
    if not scope_allowed:
        eligible = False
        reasons.extend(scope_reasons)

    confidence_component = memory.confidence
    source_trust_component = _source_trust_component(memory.evidence_type)
    recency_component = _recency_component(memory.created_at, timestamp)
    status_penalty = _status_penalty(memory.status)
    privacy_penalty = _privacy_penalty(memory.sensitivity)
    staleness_penalty = _staleness_penalty(memory.created_at, timestamp)

    total = (
        query_relevance * 0.42
        + confidence_component * 0.24
        + source_trust_component * 0.20
        + recency_component * 0.14
        - status_penalty
        - privacy_penalty
        - staleness_penalty
    )
    if not eligible:
        total = 0.0

    return RetrievalScore(
        memory_id=memory.memory_id,
        eligible=eligible,
        total=max(total, 0.0),
        query_relevance=query_relevance,
        confidence_component=confidence_component,
        source_trust_component=source_trust_component,
        recency_component=recency_component,
        status_penalty=status_penalty,
        privacy_penalty=privacy_penalty,
        staleness_penalty=staleness_penalty,
        reasons=tuple(reasons),
    )


def rank_memories(
    memories: Iterable[MemoryRecord],
    query: str,
    *,
    now: datetime | None = None,
    scope: RetrievalScope | None = None,
    limit: int = 5,
) -> list[RankedMemory]:
    ranked = [
        RankedMemory(memory=memory, score=score_memory(memory, query, now=now, scope=scope))
        for memory in memories
    ]
    eligible = [item for item in ranked if item.score.eligible]
    eligible.sort(key=lambda item: (-item.score.total, item.memory.memory_id))
    return eligible[:limit]


def tokenize(text: str) -> set[str]:
    normalized = text.replace("-", " ").replace("/", " ")
    return {
        token.strip(".,:;!?()[]{}\"'").lower()
        for token in normalized.split()
        if token.strip(".,:;!?()[]{}\"'")
    }


def _scope_allowed(memory: MemoryRecord, scope: RetrievalScope | None) -> tuple[bool, list[str]]:
    if scope is None:
        return True, []
    if memory.scope == ScopeLevel.NEVER_STORE:
        return False, ["scope_never_store"]
    if memory.scope in {ScopeLevel.PERSONAL_GLOBAL, ScopeLevel.WORK_GLOBAL}:
        if scope.include_global:
            return True, []
        return False, ["global_scope_excluded"]
    if memory.scope == ScopeLevel.PROJECT_SPECIFIC:
        return _tag_scope_allowed(
            memory,
            prefix="project",
            requested=scope.active_project,
            missing_reason="project_scope_missing",
            mismatch_reason="project_scope_mismatch",
            allow_untagged=True,
        )
    if memory.scope == ScopeLevel.AGENT_SPECIFIC:
        return _tag_scope_allowed(
            memory,
            prefix="agent",
            requested=scope.agent_id,
            missing_reason="agent_scope_missing",
            mismatch_reason="agent_scope_mismatch",
            allow_untagged=False,
        )
    if memory.scope in {ScopeLevel.SESSION_ONLY, ScopeLevel.EPHEMERAL}:
        return _tag_scope_allowed(
            memory,
            prefix="session",
            requested=scope.session_id,
            missing_reason="session_scope_missing",
            mismatch_reason="session_scope_mismatch",
            allow_untagged=False,
        )
    return True, []


def _tag_scope_allowed(
    memory: MemoryRecord,
    *,
    prefix: str,
    requested: str | None,
    missing_reason: str,
    mismatch_reason: str,
    allow_untagged: bool,
) -> tuple[bool, list[str]]:
    tags = _source_ref_tags(memory, prefix)
    if not tags:
        if allow_untagged:
            return True, []
        return False, [missing_reason]
    if requested is None:
        return False, [missing_reason]
    if requested in tags:
        return True, []
    return False, [mismatch_reason]


def _source_ref_tags(memory: MemoryRecord, prefix: str) -> set[str]:
    marker = f"{prefix}:"
    return {
        source_ref[len(marker) :]
        for source_ref in memory.source_refs
        if source_ref.startswith(marker) and len(source_ref) > len(marker)
    }


def _source_trust_component(evidence_type: EvidenceType) -> float:
    return {
        EvidenceType.USER_CONFIRMED: 1.0,
        EvidenceType.OBSERVED: 0.86,
        EvidenceType.OBSERVED_AND_INFERRED: 0.74,
        EvidenceType.INFERRED: 0.42,
        EvidenceType.EXTERNAL_EVIDENCE: 0.18,
    }[evidence_type]


def _status_penalty(status: MemoryStatus) -> float:
    return {
        MemoryStatus.ACTIVE: 0.0,
        MemoryStatus.CANDIDATE: 0.06,
        MemoryStatus.DEPRECATED: 0.28,
        MemoryStatus.SUPERSEDED: 1.0,
        MemoryStatus.REVOKED: 1.0,
        MemoryStatus.DELETED: 1.0,
        MemoryStatus.QUARANTINED: 1.0,
    }[status]


def _privacy_penalty(sensitivity: Sensitivity) -> float:
    return {
        Sensitivity.PUBLIC: 0.0,
        Sensitivity.LOW: 0.0,
        Sensitivity.PRIVATE_WORK: 0.03,
        Sensitivity.CONFIDENTIAL: 0.12,
        Sensitivity.REGULATED: 0.22,
        Sensitivity.SECRET: 1.0,
    }[sensitivity]


def _recency_component(created_at: datetime, now: datetime) -> float:
    age_days = _age_days(created_at, now)
    if age_days <= 7:
        return 1.0
    if age_days <= 30:
        return 0.72
    if age_days <= 90:
        return 0.44
    if age_days <= 180:
        return 0.22
    return 0.08


def _staleness_penalty(created_at: datetime, now: datetime) -> float:
    age_days = _age_days(created_at, now)
    if age_days <= 90:
        return 0.0
    if age_days <= 180:
        return 0.04
    if age_days <= 365:
        return 0.08
    return 0.16


def _age_days(created_at: datetime, now: datetime) -> int:
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=UTC)
    return max((now - created_at).days, 0)
