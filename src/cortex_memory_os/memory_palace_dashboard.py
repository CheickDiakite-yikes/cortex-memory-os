"""Dashboard-facing Memory Palace view models."""

from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from typing import Literal

from pydantic import Field

from cortex_memory_os.contracts import (
    AuditEvent,
    EvidenceType,
    MemoryRecord,
    MemoryStatus,
    MemoryType,
    ScopeLevel,
    Sensitivity,
    StrictModel,
)
from cortex_memory_os.firewall import redact_sensitive_text
from cortex_memory_os.memory_export import MemoryExportBundle, export_memories
from cortex_memory_os.memory_lifecycle import recall_allowed
from cortex_memory_os.memory_palace_flows import (
    MemoryPalaceFlow,
    MemoryPalaceFlowId,
    default_memory_palace_flows,
)
from cortex_memory_os.retrieval import RetrievalScope

MEMORY_PALACE_DASHBOARD_POLICY_REF = "policy_memory_palace_dashboard_v1"

SelectionMode = Literal["visible_scope", "explicit_ids"]

_TERMINAL_CONTENT_STATUSES = {
    MemoryStatus.DELETED,
    MemoryStatus.REVOKED,
    MemoryStatus.QUARANTINED,
}

_GATEWAY_TOOL_BY_FLOW = {
    MemoryPalaceFlowId.EXPLAIN: "memory.explain",
    MemoryPalaceFlowId.CORRECT: "memory.correct",
    MemoryPalaceFlowId.DELETE: "memory.forget",
    MemoryPalaceFlowId.EXPORT: "memory.export",
}


class MemoryPalaceActionPlan(StrictModel):
    flow_id: MemoryPalaceFlowId
    gateway_tool: str = Field(min_length=1)
    required_inputs: list[str] = Field(default_factory=list)
    requires_confirmation: bool
    mutation: bool
    data_egress: bool = False
    audit_action: str | None = None
    content_redacted: bool = True


class MemoryPalaceCard(StrictModel):
    memory_id: str = Field(min_length=1)
    type: MemoryType
    status: MemoryStatus
    confidence: float = Field(ge=0.0, le=1.0)
    sensitivity: Sensitivity
    scope: ScopeLevel
    evidence_type: EvidenceType
    source_count: int = Field(ge=0)
    source_refs: list[str] = Field(default_factory=list)
    user_visible: bool
    recall_eligible: bool
    requires_user_confirmation: bool
    content_preview: str | None = None
    content_redacted: bool = True
    redaction_count: int = Field(default=0, ge=0)
    audit_count: int = Field(default=0, ge=0)
    action_plans: list[MemoryPalaceActionPlan] = Field(default_factory=list)


class MemoryPalaceAuditSummary(StrictModel):
    human_visible_count: int = Field(ge=0)
    counts_by_action: dict[str, int] = Field(default_factory=dict)
    latest_audit_event_id: str | None = None
    content_redacted: bool = True


class MemoryPalaceExportPreview(StrictModel):
    selection_mode: SelectionMode
    selected_memory_ids: list[str] = Field(default_factory=list)
    selected_count: int = Field(ge=0)
    exportable_count: int = Field(ge=0)
    omitted_count: int = Field(ge=0)
    omitted_memory_ids: list[str] = Field(default_factory=list)
    omission_reasons: dict[str, list[str]] = Field(default_factory=dict)
    redaction_count: int = Field(ge=0)
    requires_confirmation: bool = True
    data_egress: bool = True
    gateway_tool: str = "memory.export"
    policy_refs: list[str] = Field(default_factory=list)


class MemoryPalaceDashboard(StrictModel):
    dashboard_id: str = Field(min_length=1)
    generated_at: datetime
    cards: list[MemoryPalaceCard] = Field(default_factory=list)
    status_counts: dict[str, int] = Field(default_factory=dict)
    recall_eligible_count: int = Field(ge=0)
    confirmation_required_count: int = Field(ge=0)
    export_preview: MemoryPalaceExportPreview
    audit_summary: MemoryPalaceAuditSummary
    policy_refs: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)


def build_memory_palace_dashboard(
    memories: list[MemoryRecord],
    *,
    audit_events: list[AuditEvent] | None = None,
    selected_memory_ids: list[str] | None = None,
    scope: RetrievalScope | None = None,
    now: datetime | None = None,
) -> MemoryPalaceDashboard:
    timestamp = _timestamp(now)
    selected = _selected_memories(memories, selected_memory_ids)
    selection_mode: SelectionMode = "explicit_ids" if selected_memory_ids else "visible_scope"
    audit_events = sorted(
        audit_events or [],
        key=lambda event: (event.timestamp, event.audit_event_id),
    )
    audit_count_by_target = Counter(event.target_ref for event in audit_events if event.human_visible)
    flow_by_id = {flow.flow_id: flow for flow in default_memory_palace_flows()}
    cards = [
        _card_for_memory(
            memory,
            flow_by_id=flow_by_id,
            audit_count=audit_count_by_target.get(memory.memory_id, 0),
        )
        for memory in sorted(memories, key=_memory_sort_key)
    ]
    export_bundle = export_memories(selected, scope=scope, now=timestamp)
    human_visible_audits = [event for event in audit_events if event.human_visible]

    return MemoryPalaceDashboard(
        dashboard_id=f"memory_palace_dashboard_{timestamp.strftime('%Y%m%dT%H%M%SZ')}",
        generated_at=timestamp,
        cards=cards,
        status_counts={
            status: count
            for status, count in sorted(
                Counter(memory.status.value for memory in memories).items()
            )
        },
        recall_eligible_count=sum(1 for memory in memories if recall_allowed(memory)),
        confirmation_required_count=sum(
            1
            for card in cards
            for action in card.action_plans
            if action.requires_confirmation
        ),
        export_preview=_export_preview(
            export_bundle,
            selected,
            selection_mode=selection_mode,
        ),
        audit_summary=MemoryPalaceAuditSummary(
            human_visible_count=len(human_visible_audits),
            counts_by_action={
                action: count
                for action, count in sorted(
                    Counter(event.action for event in human_visible_audits).items()
                )
            },
            latest_audit_event_id=(
                human_visible_audits[-1].audit_event_id if human_visible_audits else None
            ),
        ),
        policy_refs=[
            MEMORY_PALACE_DASHBOARD_POLICY_REF,
            *export_bundle.policy_refs,
        ],
        safety_notes=[
            "Dashboard previews redact secret-like text before rendering.",
            "Deleted, revoked, and quarantined memory content stays hidden.",
            "Export previews show counts and omissions; export still requires confirmation.",
            "Action plans point to gateway tools but do not execute mutations.",
        ],
    )


def _card_for_memory(
    memory: MemoryRecord,
    *,
    flow_by_id: dict[MemoryPalaceFlowId, MemoryPalaceFlow],
    audit_count: int,
) -> MemoryPalaceCard:
    preview, redaction_count = _content_preview(memory)
    return MemoryPalaceCard(
        memory_id=memory.memory_id,
        type=memory.type,
        status=memory.status,
        confidence=memory.confidence,
        sensitivity=memory.sensitivity,
        scope=memory.scope,
        evidence_type=memory.evidence_type,
        source_count=len(memory.source_refs),
        source_refs=list(memory.source_refs),
        user_visible=memory.user_visible,
        recall_eligible=recall_allowed(memory),
        requires_user_confirmation=memory.requires_user_confirmation,
        content_preview=preview,
        content_redacted=redaction_count > 0
        or not memory.user_visible
        or memory.status in _TERMINAL_CONTENT_STATUSES,
        redaction_count=redaction_count,
        audit_count=audit_count,
        action_plans=_action_plans_for_memory(memory, flow_by_id=flow_by_id),
    )


def _action_plans_for_memory(
    memory: MemoryRecord,
    *,
    flow_by_id: dict[MemoryPalaceFlowId, MemoryPalaceFlow],
) -> list[MemoryPalaceActionPlan]:
    plans: list[MemoryPalaceActionPlan] = []
    flow_ids = [MemoryPalaceFlowId.EXPLAIN]
    if memory.user_visible and memory.status not in {
        MemoryStatus.DELETED,
        MemoryStatus.REVOKED,
    }:
        flow_ids.extend([MemoryPalaceFlowId.CORRECT, MemoryPalaceFlowId.DELETE])
    if memory.user_visible and recall_allowed(memory):
        flow_ids.append(MemoryPalaceFlowId.EXPORT)

    for flow_id in flow_ids:
        flow = flow_by_id[flow_id]
        plans.append(
            MemoryPalaceActionPlan(
                flow_id=flow.flow_id,
                gateway_tool=_GATEWAY_TOOL_BY_FLOW[flow.flow_id],
                required_inputs=list(flow.required_inputs),
                requires_confirmation=flow.requires_confirmation,
                mutation=flow.mutation,
                data_egress=flow.data_egress,
                audit_action=flow.audit_action,
            )
        )
    return plans


def _content_preview(memory: MemoryRecord) -> tuple[str | None, int]:
    if not memory.user_visible or memory.status in _TERMINAL_CONTENT_STATUSES:
        return None, 0
    redacted, redactions = redact_sensitive_text(memory.content)
    return _truncate(redacted, 180), len(redactions)


def _export_preview(
    bundle: MemoryExportBundle,
    selected: list[MemoryRecord],
    *,
    selection_mode: SelectionMode,
) -> MemoryPalaceExportPreview:
    return MemoryPalaceExportPreview(
        selection_mode=selection_mode,
        selected_memory_ids=[memory.memory_id for memory in selected],
        selected_count=len(selected),
        exportable_count=len(bundle.memories),
        omitted_count=len(bundle.omitted_memory_ids),
        omitted_memory_ids=list(bundle.omitted_memory_ids),
        omission_reasons=dict(bundle.omission_reasons),
        redaction_count=bundle.redaction_count,
        policy_refs=list(bundle.policy_refs),
    )


def _selected_memories(
    memories: list[MemoryRecord],
    selected_memory_ids: list[str] | None,
) -> list[MemoryRecord]:
    if not selected_memory_ids:
        return list(memories)
    memory_by_id = {memory.memory_id: memory for memory in memories}
    missing = [memory_id for memory_id in selected_memory_ids if memory_id not in memory_by_id]
    if missing:
        raise ValueError(f"unknown selected_memory_ids: {', '.join(sorted(missing))}")
    return [memory_by_id[memory_id] for memory_id in selected_memory_ids]


def _memory_sort_key(memory: MemoryRecord) -> tuple[int, str, str]:
    status_order = {
        MemoryStatus.ACTIVE: 0,
        MemoryStatus.CANDIDATE: 1,
        MemoryStatus.DEPRECATED: 2,
        MemoryStatus.SUPERSEDED: 3,
        MemoryStatus.QUARANTINED: 4,
        MemoryStatus.REVOKED: 5,
        MemoryStatus.DELETED: 6,
    }
    return (status_order.get(memory.status, 99), memory.valid_from.isoformat(), memory.memory_id)


def _timestamp(now: datetime | None) -> datetime:
    timestamp = now or datetime.now(UTC)
    if timestamp.tzinfo is None:
        return timestamp.replace(tzinfo=UTC)
    return timestamp


def _truncate(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "..."
