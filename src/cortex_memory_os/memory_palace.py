"""Memory Palace correction, deletion, and explanation service."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from cortex_memory_os.contracts import (
    AuditEvent,
    EvidenceType,
    MemoryRecord,
    MemoryStatus,
)
from cortex_memory_os.memory_lifecycle import recall_allowed, transition_memory
from cortex_memory_os.memory_palace_dashboard import (
    MemoryPalaceDashboard,
    build_memory_palace_dashboard,
)
from cortex_memory_os.memory_palace_flows import MemoryPalaceFlowId
from cortex_memory_os.retrieval import RetrievalScope
from cortex_memory_os.sqlite_store import SQLiteMemoryGraphStore

MEMORY_PALACE_POLICY_REF = "policy_memory_palace_user_control_v1"


@dataclass(frozen=True)
class MemoryCorrection:
    old_memory: MemoryRecord
    corrected_memory: MemoryRecord
    audit_event: AuditEvent


@dataclass(frozen=True)
class MemoryExplanation:
    memory_id: str
    status: MemoryStatus
    confidence: float
    source_refs: list[str]
    evidence_type: EvidenceType
    allowed_influence: list[str]
    forbidden_influence: list[str]
    recall_eligible: bool
    available_actions: list[str]


class MemoryPalaceService:
    def __init__(self, store: SQLiteMemoryGraphStore, *, actor: str = "user") -> None:
        self.store = store
        self.actor = actor

    def explain_memory(self, memory_id: str) -> MemoryExplanation:
        memory = self._require_memory(memory_id)
        return MemoryExplanation(
            memory_id=memory.memory_id,
            status=memory.status,
            confidence=memory.confidence,
            source_refs=memory.source_refs,
            evidence_type=memory.evidence_type,
            allowed_influence=memory.allowed_influence,
            forbidden_influence=memory.forbidden_influence,
            recall_eligible=recall_allowed(memory),
            available_actions=_available_actions(memory),
        )

    def dashboard(
        self,
        *,
        selected_memory_ids: list[str] | None = None,
        scope: RetrievalScope | None = None,
        now: datetime | None = None,
    ) -> MemoryPalaceDashboard:
        memories = self.store.list_memories()
        target_ids = [memory.memory_id for memory in memories]
        audit_events = [
            event
            for memory_id in target_ids
            for event in self.store.audit_for_target(memory_id)
        ]
        return build_memory_palace_dashboard(
            memories,
            audit_events=audit_events,
            selected_memory_ids=selected_memory_ids,
            scope=scope,
            now=now,
        )

    def delete_memory(self, memory_id: str, *, now: datetime | None = None) -> MemoryRecord:
        timestamp = now or datetime.now(UTC)
        deleted = self.store.forget_memory(memory_id)
        self.store.add_audit_event(
            self._audit_event(
                action="delete_memory",
                target_ref=memory_id,
                timestamp=timestamp,
                result="deleted",
                redacted_summary="Memory was deleted from active recall.",
            )
        )
        return deleted

    def correct_memory(
        self,
        memory_id: str,
        corrected_content: str,
        *,
        now: datetime | None = None,
    ) -> MemoryCorrection:
        original = self._require_memory(memory_id)
        if original.status in {MemoryStatus.DELETED, MemoryStatus.REVOKED}:
            raise ValueError("deleted or revoked memories cannot be corrected")

        timestamp = now or datetime.now(UTC)
        corrected_id = f"{original.memory_id}_corrected_{timestamp.strftime('%Y%m%dT%H%M%SZ')}"
        superseded = transition_memory(
            original,
            MemoryStatus.SUPERSEDED,
            replacement_memory_id=corrected_id,
            now=timestamp,
        )
        corrected = original.model_copy(
            update={
                "memory_id": corrected_id,
                "content": corrected_content,
                "source_refs": [original.memory_id, *original.source_refs],
                "evidence_type": EvidenceType.USER_CONFIRMED,
                "confidence": 1.0,
                "status": MemoryStatus.ACTIVE,
                "created_at": timestamp,
                "valid_from": timestamp.date(),
                "requires_user_confirmation": False,
            }
        )
        self.store.add_memory(superseded)
        self.store.add_memory(corrected)
        audit_event = self._audit_event(
            action="correct_memory",
            target_ref=original.memory_id,
            timestamp=timestamp,
            result="superseded_and_replaced",
            redacted_summary="Memory was corrected by the user; original was superseded.",
        )
        self.store.add_audit_event(audit_event)
        return MemoryCorrection(
            old_memory=superseded,
            corrected_memory=corrected,
            audit_event=audit_event,
        )

    def _require_memory(self, memory_id: str) -> MemoryRecord:
        memory = self.store.get_memory(memory_id)
        if memory is None:
            raise KeyError(memory_id)
        return memory

    def _audit_event(
        self,
        *,
        action: str,
        target_ref: str,
        timestamp: datetime,
        result: str,
        redacted_summary: str,
    ) -> AuditEvent:
        return AuditEvent(
            audit_event_id=(
                f"audit_{action}_{_safe_id_fragment(target_ref)}_"
                f"{timestamp.strftime('%Y%m%dT%H%M%SZ')}"
            ),
            timestamp=timestamp,
            actor=self.actor,
            action=action,
            target_ref=target_ref,
            policy_refs=[MEMORY_PALACE_POLICY_REF],
            result=result,
            human_visible=True,
            redacted_summary=redacted_summary,
        )


def _safe_id_fragment(value: str) -> str:
    return "".join(char if char.isalnum() else "_" for char in value)


def _available_actions(memory: MemoryRecord) -> list[str]:
    actions = [MemoryPalaceFlowId.EXPLAIN.value]
    if memory.status not in {MemoryStatus.DELETED, MemoryStatus.REVOKED}:
        actions.extend(
            [
                MemoryPalaceFlowId.CORRECT.value,
                MemoryPalaceFlowId.DELETE.value,
            ]
        )
    return actions
