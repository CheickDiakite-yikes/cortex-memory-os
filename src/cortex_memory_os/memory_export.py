"""Deletion-aware user memory export contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field

from cortex_memory_os.contracts import AuditEvent, MemoryRecord
from cortex_memory_os.firewall import redact_sensitive_text
from cortex_memory_os.memory_lifecycle import recall_allowed
from cortex_memory_os.retrieval import RetrievalScope, score_memory
from cortex_memory_os.sensitive_data_policy import SECRET_PII_POLICY_REF
from cortex_memory_os.sqlite_store import SQLiteMemoryGraphStore

MEMORY_EXPORT_POLICY_REF = "policy_memory_export_deletion_aware_v1"


class ExportedMemory(BaseModel):
    model_config = ConfigDict(extra="forbid")

    memory_id: str = Field(min_length=1)
    type: str = Field(min_length=1)
    content: str = Field(min_length=1)
    source_refs: list[str] = Field(default_factory=list)
    confidence: float
    status: str = Field(min_length=1)
    sensitivity: str = Field(min_length=1)
    scope: str = Field(min_length=1)
    allowed_influence: list[str] = Field(default_factory=list)
    forbidden_influence: list[str] = Field(default_factory=list)


class MemoryExportBundle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    export_id: str = Field(min_length=1)
    created_at: datetime
    active_project: str | None = None
    agent_id: str | None = None
    session_id: str | None = None
    memories: list[ExportedMemory] = Field(default_factory=list)
    omitted_memory_ids: list[str] = Field(default_factory=list)
    omission_reasons: dict[str, list[str]] = Field(default_factory=dict)
    redaction_count: int = 0
    policy_refs: list[str] = Field(default_factory=list)


@dataclass(frozen=True)
class MemoryExportResult:
    bundle: MemoryExportBundle
    audit_event: AuditEvent


def export_memories(
    memories: list[MemoryRecord],
    *,
    scope: RetrievalScope | None = None,
    now: datetime | None = None,
) -> MemoryExportBundle:
    timestamp = now or datetime.now(UTC)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=UTC)
    exported: list[ExportedMemory] = []
    omitted_ids: list[str] = []
    omission_reasons: dict[str, list[str]] = {}
    redaction_count = 0

    for memory in memories:
        reasons = _omission_reasons(memory, scope=scope, now=timestamp)
        if reasons:
            omitted_ids.append(memory.memory_id)
            omission_reasons[memory.memory_id] = reasons
            continue

        redacted_content, redactions = redact_sensitive_text(memory.content)
        redaction_count += len(redactions)
        exported.append(
            ExportedMemory(
                memory_id=memory.memory_id,
                type=memory.type.value,
                content=redacted_content,
                source_refs=memory.source_refs,
                confidence=memory.confidence,
                status=memory.status.value,
                sensitivity=memory.sensitivity.value,
                scope=memory.scope.value,
                allowed_influence=memory.allowed_influence,
                forbidden_influence=memory.forbidden_influence,
            )
        )

    return MemoryExportBundle(
        export_id=f"export_{timestamp.strftime('%Y%m%dT%H%M%SZ')}",
        created_at=timestamp,
        active_project=scope.active_project if scope else None,
        agent_id=scope.agent_id if scope else None,
        session_id=scope.session_id if scope else None,
        memories=exported,
        omitted_memory_ids=omitted_ids,
        omission_reasons=omission_reasons,
        redaction_count=redaction_count,
        policy_refs=[MEMORY_EXPORT_POLICY_REF, SECRET_PII_POLICY_REF],
    )


def export_memories_with_audit(
    store: SQLiteMemoryGraphStore,
    memories: list[MemoryRecord],
    *,
    scope: RetrievalScope | None = None,
    actor: str = "user",
    now: datetime | None = None,
) -> MemoryExportResult:
    bundle = export_memories(memories, scope=scope, now=now)
    audit_event = export_audit_event(bundle, actor=actor)
    store.add_audit_event(audit_event)
    return MemoryExportResult(bundle=bundle, audit_event=audit_event)


def export_audit_event(bundle: MemoryExportBundle, *, actor: str = "user") -> AuditEvent:
    return AuditEvent(
        audit_event_id=f"audit_export_memories_{bundle.export_id}",
        timestamp=bundle.created_at,
        actor=actor,
        action="export_memories",
        target_ref=bundle.export_id,
        policy_refs=list(bundle.policy_refs),
        result="export_created",
        human_visible=True,
        redacted_summary=(
            "Memory export created with "
            f"{len(bundle.memories)} memories, "
            f"{len(bundle.omitted_memory_ids)} omitted, "
            f"{bundle.redaction_count} redactions."
        ),
    )


def _omission_reasons(
    memory: MemoryRecord,
    *,
    scope: RetrievalScope | None,
    now: datetime,
) -> list[str]:
    reasons: list[str] = []
    if not memory.user_visible:
        reasons.append("not_user_visible")
    if not recall_allowed(memory):
        reasons.append("not_recall_allowed")
    if scope is not None:
        score = score_memory(memory, memory.content, now=now, scope=scope)
        scope_reasons = [
            reason
            for reason in score.reasons
            if reason.endswith("_scope_missing")
            or reason.endswith("_scope_mismatch")
            or reason == "global_scope_excluded"
            or reason == "scope_never_store"
        ]
        reasons.extend(scope_reasons)
    return sorted(set(reasons))
