from datetime import UTC, datetime

import pytest

from cortex_memory_os.contracts import (
    EvidenceType,
    InfluenceLevel,
    MemoryRecord,
    MemoryStatus,
    Sensitivity,
)
from cortex_memory_os.fixtures import load_json
from cortex_memory_os.memory_lifecycle import (
    evaluate_memory_transition,
    recall_allowed,
    transition_memory,
)


def _memory(**updates) -> MemoryRecord:
    payload = load_json("tests/fixtures/memory_preference.json")
    payload.update(updates)
    return MemoryRecord.model_validate(payload)


def test_candidate_with_sufficient_observed_confidence_can_activate():
    memory = _memory(status=MemoryStatus.CANDIDATE.value, confidence=0.82)

    decision = evaluate_memory_transition(memory, MemoryStatus.ACTIVE)
    active = transition_memory(memory, MemoryStatus.ACTIVE)

    assert decision.allowed is True
    assert decision.required_behavior == "promote_with_audit"
    assert active.status == MemoryStatus.ACTIVE
    assert active.requires_user_confirmation is False
    assert recall_allowed(active) is True


def test_low_confidence_and_external_memory_cannot_activate():
    low_confidence = _memory(status=MemoryStatus.CANDIDATE.value, confidence=0.6)
    external = _memory(
        status=MemoryStatus.CANDIDATE.value,
        evidence_type=EvidenceType.EXTERNAL_EVIDENCE.value,
        confidence=0.95,
    )

    assert evaluate_memory_transition(low_confidence, MemoryStatus.ACTIVE).reason == (
        "confidence_too_low"
    )
    assert evaluate_memory_transition(external, MemoryStatus.ACTIVE).reason == (
        "external_evidence_cannot_activate"
    )


def test_inferred_memory_requires_user_approval_and_high_confidence():
    inferred = _memory(
        status=MemoryStatus.CANDIDATE.value,
        evidence_type=EvidenceType.INFERRED.value,
        confidence=0.91,
        requires_user_confirmation=True,
    )

    denied = evaluate_memory_transition(inferred, MemoryStatus.ACTIVE)
    allowed = evaluate_memory_transition(inferred, MemoryStatus.ACTIVE, user_approved=True)
    active = transition_memory(inferred, MemoryStatus.ACTIVE, user_approved=True)

    assert denied.reason == "inferred_memory_requires_user_approval"
    assert allowed.allowed is True
    assert active.status == MemoryStatus.ACTIVE


def test_deleted_revoked_superseded_and_quarantined_block_recall():
    memory = _memory()
    deleted = transition_memory(memory, MemoryStatus.DELETED, now=datetime(2026, 4, 27, tzinfo=UTC))
    superseded = transition_memory(
        memory,
        MemoryStatus.SUPERSEDED,
        replacement_memory_id="mem_replacement",
        now=datetime(2026, 4, 27, tzinfo=UTC),
    )
    quarantined = transition_memory(memory, MemoryStatus.QUARANTINED)

    assert deleted.status == MemoryStatus.DELETED
    assert deleted.influence_level == InfluenceLevel.STORED_ONLY
    assert deleted.allowed_influence == []
    assert deleted.valid_to is not None
    assert recall_allowed(deleted) is False
    assert recall_allowed(superseded) is False
    assert recall_allowed(quarantined) is False


def test_terminal_memory_cannot_be_reactivated():
    deleted = _memory(
        status=MemoryStatus.DELETED.value,
        influence_level=InfluenceLevel.STORED_ONLY.value,
        allowed_influence=[],
    )

    with pytest.raises(ValueError, match="terminal_memory_status"):
        transition_memory(deleted, MemoryStatus.ACTIVE, user_approved=True)


def test_secret_memory_cannot_be_recalled_or_activated():
    secret = _memory(status=MemoryStatus.CANDIDATE.value, sensitivity=Sensitivity.SECRET.value)

    decision = evaluate_memory_transition(secret, MemoryStatus.ACTIVE, user_approved=True)

    assert decision.reason == "secret_memory_cannot_activate"
    assert recall_allowed(secret) is False
