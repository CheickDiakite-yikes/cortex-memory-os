"""Governed memory lifecycle transitions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from cortex_memory_os.contracts import (
    EvidenceType,
    InfluenceLevel,
    MemoryRecord,
    MemoryStatus,
    Sensitivity,
)


TERMINAL_MEMORY_STATUSES = {MemoryStatus.DELETED, MemoryStatus.REVOKED}
NON_PROMOTABLE_STATUSES = {
    MemoryStatus.DELETED,
    MemoryStatus.REVOKED,
    MemoryStatus.SUPERSEDED,
    MemoryStatus.QUARANTINED,
}
RETRIEVAL_BLOCKING_STATUSES = {
    MemoryStatus.DELETED,
    MemoryStatus.REVOKED,
    MemoryStatus.SUPERSEDED,
    MemoryStatus.QUARANTINED,
}
MIN_ACTIVE_CONFIDENCE = 0.75
MIN_INFERRED_ACTIVE_CONFIDENCE = 0.90


@dataclass(frozen=True)
class MemoryLifecycleDecision:
    allowed: bool
    source_status: MemoryStatus
    target_status: MemoryStatus
    required_behavior: str
    reason: str


def evaluate_memory_transition(
    memory: MemoryRecord,
    target_status: MemoryStatus,
    *,
    user_approved: bool = False,
    replacement_memory_id: str | None = None,
) -> MemoryLifecycleDecision:
    if memory.status == target_status:
        return _allow(memory, target_status, "no_op", "already_in_target_status")
    if memory.status in TERMINAL_MEMORY_STATUSES:
        return _deny(memory, target_status, "terminal_memory_status")
    if target_status == MemoryStatus.ACTIVE:
        return _evaluate_activation(memory, user_approved=user_approved)
    if target_status == MemoryStatus.SUPERSEDED:
        if memory.status == MemoryStatus.QUARANTINED:
            return _deny(memory, target_status, "quarantined_memory_cannot_be_superseded")
        if not replacement_memory_id:
            return _deny(memory, target_status, "replacement_memory_id_required")
        return _allow(memory, target_status, "store_tombstone", "supersession_allowed")
    if target_status == MemoryStatus.DELETED:
        return _allow(memory, target_status, "delete_and_block_retrieval", "user_delete_allowed")
    if target_status == MemoryStatus.REVOKED:
        return _allow(memory, target_status, "revoke_and_block_retrieval", "policy_revoke_allowed")
    if target_status == MemoryStatus.DEPRECATED:
        if memory.status == MemoryStatus.QUARANTINED:
            return _deny(memory, target_status, "quarantined_memory_cannot_be_deprecated")
        return _allow(memory, target_status, "lower_retrieval_priority", "deprecation_allowed")
    if target_status == MemoryStatus.QUARANTINED:
        return _allow(memory, target_status, "block_retrieval", "quarantine_allowed")
    if target_status == MemoryStatus.CANDIDATE:
        return _deny(memory, target_status, "candidate_reversion_not_allowed")
    return _deny(memory, target_status, "unsupported_transition")


def transition_memory(
    memory: MemoryRecord,
    target_status: MemoryStatus,
    *,
    user_approved: bool = False,
    replacement_memory_id: str | None = None,
    now: datetime | None = None,
) -> MemoryRecord:
    decision = evaluate_memory_transition(
        memory,
        target_status,
        user_approved=user_approved,
        replacement_memory_id=replacement_memory_id,
    )
    if not decision.allowed:
        raise ValueError(decision.reason)

    timestamp = now or datetime.now(UTC)
    updates: dict[str, object] = {"status": target_status}
    if target_status == MemoryStatus.ACTIVE:
        updates["requires_user_confirmation"] = False
    if target_status in RETRIEVAL_BLOCKING_STATUSES:
        updates["influence_level"] = InfluenceLevel.STORED_ONLY
        updates["allowed_influence"] = []
        updates["valid_to"] = timestamp.date()
    if target_status == MemoryStatus.DEPRECATED:
        updates["valid_to"] = timestamp.date()
    if replacement_memory_id:
        updates["contradicts"] = [*memory.contradicts, replacement_memory_id]
    return memory.model_copy(update=updates)


def recall_allowed(memory: MemoryRecord) -> bool:
    return (
        memory.status not in RETRIEVAL_BLOCKING_STATUSES
        and memory.influence_level != InfluenceLevel.STORED_ONLY
        and memory.scope.value != "never_store"
        and memory.sensitivity != Sensitivity.SECRET
    )


def _evaluate_activation(
    memory: MemoryRecord,
    *,
    user_approved: bool,
) -> MemoryLifecycleDecision:
    if memory.status in NON_PROMOTABLE_STATUSES:
        return _deny(memory, MemoryStatus.ACTIVE, f"{memory.status.value}_cannot_activate")
    if memory.sensitivity == Sensitivity.SECRET:
        return _deny(memory, MemoryStatus.ACTIVE, "secret_memory_cannot_activate")
    if memory.evidence_type == EvidenceType.EXTERNAL_EVIDENCE:
        return _deny(memory, MemoryStatus.ACTIVE, "external_evidence_cannot_activate")
    if memory.evidence_type == EvidenceType.INFERRED:
        if not user_approved:
            return _deny(memory, MemoryStatus.ACTIVE, "inferred_memory_requires_user_approval")
        if memory.confidence < MIN_INFERRED_ACTIVE_CONFIDENCE:
            return _deny(memory, MemoryStatus.ACTIVE, "inferred_memory_confidence_too_low")
    elif memory.confidence < MIN_ACTIVE_CONFIDENCE:
        return _deny(memory, MemoryStatus.ACTIVE, "confidence_too_low")
    if memory.requires_user_confirmation and not user_approved:
        return _deny(memory, MemoryStatus.ACTIVE, "user_confirmation_required")
    if memory.influence_level >= InfluenceLevel.TOOL_ACTIONS and not user_approved:
        return _deny(memory, MemoryStatus.ACTIVE, "tool_influence_requires_user_approval")
    return _allow(memory, MemoryStatus.ACTIVE, "promote_with_audit", "activation_allowed")


def _allow(
    memory: MemoryRecord,
    target_status: MemoryStatus,
    required_behavior: str,
    reason: str,
) -> MemoryLifecycleDecision:
    return MemoryLifecycleDecision(
        allowed=True,
        source_status=memory.status,
        target_status=target_status,
        required_behavior=required_behavior,
        reason=reason,
    )


def _deny(
    memory: MemoryRecord,
    target_status: MemoryStatus,
    reason: str,
) -> MemoryLifecycleDecision:
    return MemoryLifecycleDecision(
        allowed=False,
        source_status=memory.status,
        target_status=target_status,
        required_behavior="keep_current_status",
        reason=reason,
    )
