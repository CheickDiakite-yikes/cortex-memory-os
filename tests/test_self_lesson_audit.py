from datetime import UTC, date, datetime

from cortex_memory_os.contracts import ActionRisk, MemoryStatus
from cortex_memory_os.self_lesson_audit import (
    SELF_LESSON_AUDIT_POLICY_REF,
    record_self_lesson_decision_audit,
    record_self_lesson_promotion_audit,
    record_self_lesson_rollback_audit,
)
from cortex_memory_os.self_lessons import (
    SELF_LESSON_POLICY_REF,
    SelfLessonChangeType,
    evaluate_self_lesson_promotion,
    evaluate_self_lesson_rollback,
    promote_self_lesson,
    propose_self_lesson,
)
from cortex_memory_os.sqlite_store import SQLiteMemoryGraphStore


def _proposal():
    return propose_self_lesson(
        content=(
            "Before editing auth code, retrieve browser console errors and "
            "recent terminal logs."
        ),
        learned_from=["task_332_failure", "task_333_success"],
        applies_to=["frontend_debugging", "auth_flows"],
        change_type=SelfLessonChangeType.FAILURE_CHECKLIST,
        change_summary="Add a debugging checklist item before auth edits.",
        confidence=0.84,
        risk_level=ActionRisk.LOW,
        now=datetime(2026, 4, 27, 23, 0, tzinfo=UTC),
    )


def test_self_lesson_promotion_audit_persists_reason_without_lesson_content(tmp_path):
    store = SQLiteMemoryGraphStore(tmp_path / "cortex.sqlite3")
    proposal = _proposal()
    decision = evaluate_self_lesson_promotion(proposal, user_confirmed=True)

    event = record_self_lesson_promotion_audit(
        store,
        proposal,
        decision,
        actor="tester",
        now=datetime(2026, 4, 27, 23, 10, tzinfo=UTC),
    )
    audits = store.audit_for_target(proposal.lesson.lesson_id)
    serialized = audits[0].model_dump_json()

    assert audits == [event]
    assert event.action == "promote_self_lesson"
    assert event.actor == "tester"
    assert event.result == "promotion_allowed"
    assert event.human_visible is True
    assert event.redacted_summary == (
        "Self-lesson promotion decision: target status active, allowed true."
    )
    assert event.policy_refs == [SELF_LESSON_POLICY_REF, SELF_LESSON_AUDIT_POLICY_REF]
    assert proposal.lesson.content not in serialized
    assert proposal.change_summary not in serialized
    assert proposal.lesson.learned_from[0] not in serialized


def test_self_lesson_rollback_audit_persists_reason_without_lesson_content(tmp_path):
    store = SQLiteMemoryGraphStore(tmp_path / "cortex.sqlite3")
    proposal = _proposal()
    active = promote_self_lesson(
        proposal,
        user_confirmed=True,
        today=date(2026, 4, 27),
    )
    decision = evaluate_self_lesson_rollback(active, failure_count=1)

    event = record_self_lesson_rollback_audit(
        store,
        active,
        decision,
        actor="tester",
        now=datetime(2026, 4, 27, 23, 11, tzinfo=UTC),
    )
    audits = store.audit_for_target(active.lesson_id)
    serialized = audits[0].model_dump_json()

    assert audits == [event]
    assert event.action == "rollback_self_lesson"
    assert event.result == "rollback_allowed"
    assert event.redacted_summary == (
        "Self-lesson rollback decision: target status revoked, allowed true."
    )
    assert event.policy_refs == [SELF_LESSON_POLICY_REF, SELF_LESSON_AUDIT_POLICY_REF]
    assert active.content not in serialized
    assert active.rollback_if[0] not in serialized


def test_structured_gateway_style_self_lesson_audit_uses_decision_fields_only(tmp_path):
    store = SQLiteMemoryGraphStore(tmp_path / "cortex.sqlite3")

    event = record_self_lesson_decision_audit(
        store,
        lesson_id="lesson_frontend_debugging_20260427T230000Z",
        action="promote_self_lesson",
        target_status=MemoryStatus.CANDIDATE,
        allowed=False,
        reason="user_confirmation_required",
        actor="gateway",
        now=datetime(2026, 4, 27, 23, 12, tzinfo=UTC),
    )
    audits = store.audit_for_target("lesson_frontend_debugging_20260427T230000Z")

    assert audits == [event]
    assert event.action == "promote_self_lesson"
    assert event.actor == "gateway"
    assert event.result == "user_confirmation_required"
    assert event.redacted_summary == (
        "Self-lesson promotion decision: target status candidate, allowed false."
    )
    assert event.policy_refs == [SELF_LESSON_POLICY_REF, SELF_LESSON_AUDIT_POLICY_REF]
