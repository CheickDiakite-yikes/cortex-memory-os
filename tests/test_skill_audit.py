from datetime import UTC, datetime

from cortex_memory_os.contracts import ExecutionMode, MemoryStatus, SkillRecord
from cortex_memory_os.fixtures import load_json
from cortex_memory_os.skill_audit import (
    SKILL_AUDIT_POLICY_REF,
    record_skill_maturity_audit,
    record_skill_promotion_audit,
    record_skill_rollback_audit,
)
from cortex_memory_os.skill_policy import (
    evaluate_skill_promotion,
    evaluate_skill_rollback,
)
from cortex_memory_os.sqlite_store import SQLiteMemoryGraphStore


def _skill(**updates) -> SkillRecord:
    payload = load_json("tests/fixtures/skill_draft.json")
    payload.update(updates)
    return SkillRecord.model_validate(payload)


def test_skill_promotion_audit_persists_without_skill_procedure(tmp_path):
    store = SQLiteMemoryGraphStore(tmp_path / "cortex.sqlite3")
    skill = _skill()
    decision = evaluate_skill_promotion(
        skill,
        target_maturity=3,
        observed_successes=2,
        user_approved=True,
    )

    event = record_skill_promotion_audit(
        store,
        skill,
        decision,
        actor="tester",
        now=datetime(2026, 4, 27, 21, 40, tzinfo=UTC),
    )
    audits = store.audit_for_target(skill.skill_id)
    serialized = audits[0].model_dump_json()

    assert audits == [event]
    assert event.action == "promote_skill"
    assert event.actor == "tester"
    assert event.result == "promotion_allowed"
    assert event.human_visible is True
    assert event.redacted_summary == (
        "Skill promotion decision: target maturity 3, allowed true."
    )
    assert SKILL_AUDIT_POLICY_REF in event.policy_refs
    assert skill.description not in serialized
    assert skill.procedure[0] not in serialized


def test_skill_rollback_audit_persists_without_skill_procedure(tmp_path):
    store = SQLiteMemoryGraphStore(tmp_path / "cortex.sqlite3")
    skill = _skill().model_copy(
        update={
            "maturity_level": 4,
            "execution_mode": ExecutionMode.BOUNDED_AUTONOMY,
            "status": MemoryStatus.ACTIVE,
        }
    )
    decision = evaluate_skill_rollback(skill, target_maturity=2, failure_count=1)

    event = record_skill_rollback_audit(
        store,
        skill,
        decision,
        actor="tester",
        now=datetime(2026, 4, 27, 21, 41, tzinfo=UTC),
    )
    audits = store.audit_for_target(skill.skill_id)
    serialized = audits[0].model_dump_json()

    assert audits == [event]
    assert event.action == "rollback_skill"
    assert event.result == "rollback_allowed"
    assert event.redacted_summary == (
        "Skill rollback decision: target maturity 2, allowed true."
    )
    assert SKILL_AUDIT_POLICY_REF in event.policy_refs
    assert skill.description not in serialized
    assert skill.procedure[0] not in serialized


def test_structured_gateway_style_skill_audit_uses_only_decision_fields(tmp_path):
    store = SQLiteMemoryGraphStore(tmp_path / "cortex.sqlite3")

    event = record_skill_maturity_audit(
        store,
        skill_id="skill_research_synthesis_v1",
        action="promote_skill",
        target_maturity=3,
        allowed=True,
        reason="promotion_allowed",
        actor="gateway",
        now=datetime(2026, 4, 27, 21, 45, tzinfo=UTC),
    )
    audits = store.audit_for_target("skill_research_synthesis_v1")

    assert audits == [event]
    assert event.action == "promote_skill"
    assert event.actor == "gateway"
    assert event.redacted_summary == (
        "Skill maturity decision: target maturity 3, allowed true."
    )
    assert SKILL_AUDIT_POLICY_REF in event.policy_refs
