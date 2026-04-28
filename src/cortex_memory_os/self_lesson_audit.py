"""Human-visible audit receipts for self-lesson promotion and rollback."""

from __future__ import annotations

from datetime import UTC, datetime

from cortex_memory_os.contracts import AuditEvent, MemoryStatus, SelfLesson
from cortex_memory_os.self_lessons import (
    SELF_LESSON_POLICY_REF,
    SelfLessonDecision,
    SelfLessonProposal,
)
from cortex_memory_os.sqlite_store import SQLiteMemoryGraphStore

SELF_LESSON_AUDIT_POLICY_REF = "policy_self_lesson_audit_receipt_v1"


def record_self_lesson_promotion_audit(
    store: SQLiteMemoryGraphStore,
    proposal: SelfLessonProposal,
    decision: SelfLessonDecision,
    *,
    actor: str = "user",
    now: datetime | None = None,
) -> AuditEvent:
    event = _self_lesson_audit_event(
        lesson_id=proposal.lesson.lesson_id,
        action="promote_self_lesson",
        actor=actor,
        timestamp=now or datetime.now(UTC),
        target_status=decision.target_status,
        allowed=decision.allowed,
        result=decision.reason,
        decision_label="promotion",
    )
    store.add_audit_event(event)
    return event


def record_self_lesson_rollback_audit(
    store: SQLiteMemoryGraphStore,
    lesson: SelfLesson,
    decision: SelfLessonDecision,
    *,
    actor: str = "user",
    now: datetime | None = None,
) -> AuditEvent:
    event = _self_lesson_audit_event(
        lesson_id=lesson.lesson_id,
        action="rollback_self_lesson",
        actor=actor,
        timestamp=now or datetime.now(UTC),
        target_status=decision.target_status,
        allowed=decision.allowed,
        result=decision.reason,
        decision_label="rollback",
    )
    store.add_audit_event(event)
    return event


def record_self_lesson_decision_audit(
    store: SQLiteMemoryGraphStore,
    *,
    lesson_id: str,
    action: str,
    target_status: MemoryStatus,
    allowed: bool,
    reason: str,
    actor: str = "agent",
    now: datetime | None = None,
) -> AuditEvent:
    labels = {
        "promote_self_lesson": "promotion",
        "rollback_self_lesson": "rollback",
        "correct_self_lesson": "correction",
    }
    if action not in labels:
        raise ValueError("unsupported self-lesson audit action")
    event = _self_lesson_audit_event(
        lesson_id=lesson_id,
        action=action,
        actor=actor,
        timestamp=now or datetime.now(UTC),
        target_status=target_status,
        allowed=allowed,
        result=reason,
        decision_label=labels[action],
    )
    store.add_audit_event(event)
    return event


def _self_lesson_audit_event(
    *,
    lesson_id: str,
    action: str,
    actor: str,
    timestamp: datetime,
    target_status: MemoryStatus,
    allowed: bool,
    result: str,
    decision_label: str,
) -> AuditEvent:
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=UTC)
    return AuditEvent(
        audit_event_id=(
            f"audit_{action}_{_safe_id_fragment(lesson_id)}_"
            f"{timestamp.strftime('%Y%m%dT%H%M%S%fZ')}"
        ),
        timestamp=timestamp,
        actor=actor,
        action=action,
        target_ref=lesson_id,
        policy_refs=[SELF_LESSON_POLICY_REF, SELF_LESSON_AUDIT_POLICY_REF],
        result=result,
        human_visible=True,
        redacted_summary=(
            f"Self-lesson {decision_label} decision: "
            f"target status {target_status.value}, "
            f"allowed {str(allowed).lower()}."
        ),
    )


def _safe_id_fragment(value: str) -> str:
    return "".join(char if char.isalnum() else "_" for char in value)
