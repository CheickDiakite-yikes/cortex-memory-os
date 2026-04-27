from cortex_memory_os.contracts import ActionRisk, ExecutionMode, SkillRecord
from cortex_memory_os.fixtures import load_json
from cortex_memory_os.skill_policy import (
    evaluate_skill_promotion,
    evaluate_skill_rollback,
    recommended_execution_mode,
    rollback_skill,
)


def _skill(**updates) -> SkillRecord:
    payload = load_json("tests/fixtures/skill_draft.json")
    payload.update(updates)
    return SkillRecord.model_validate(payload)


def test_skill_cannot_jump_from_draft_to_bounded_autonomy():
    skill = _skill()

    decision = evaluate_skill_promotion(
        skill,
        target_maturity=4,
        observed_successes=10,
        user_approved=True,
    )

    assert decision.allowed is False
    assert decision.reason == "promotion_must_be_incremental"
    assert decision.recommended_execution_mode == ExecutionMode.DRAFT_ONLY


def test_assistive_promotion_requires_user_approval_and_success_evidence():
    skill = _skill()

    no_approval = evaluate_skill_promotion(
        skill,
        target_maturity=3,
        observed_successes=3,
        user_approved=False,
    )
    not_enough_evidence = evaluate_skill_promotion(
        skill,
        target_maturity=3,
        observed_successes=1,
        user_approved=True,
    )
    allowed = evaluate_skill_promotion(
        skill,
        target_maturity=3,
        observed_successes=2,
        user_approved=True,
    )

    assert no_approval.reason == "user_approval_required"
    assert not_enough_evidence.reason == "insufficient_success_evidence"
    assert allowed.allowed is True
    assert allowed.recommended_execution_mode == ExecutionMode.ASSISTIVE


def test_high_and_critical_risk_skills_do_not_gain_autonomy():
    high_risk = _skill(
        skill_id="skill_high",
        risk_level=ActionRisk.HIGH.value,
        requires_confirmation_before=["send_message"],
    ).model_copy(update={"maturity_level": 3, "execution_mode": ExecutionMode.ASSISTIVE})
    critical = _skill(
        skill_id="skill_critical",
        risk_level=ActionRisk.CRITICAL.value,
        requires_confirmation_before=["financial_transfer"],
    )

    high_decision = evaluate_skill_promotion(
        high_risk,
        target_maturity=4,
        observed_successes=10,
        user_approved=True,
    )
    critical_decision = evaluate_skill_promotion(
        critical,
        target_maturity=3,
        observed_successes=10,
        user_approved=True,
    )

    assert high_decision.reason == "high_risk_no_autonomy"
    assert critical_decision.reason == "critical_skill_stays_draft_only"


def test_recommended_execution_mode_tracks_maturity_levels():
    assert recommended_execution_mode(2) == ExecutionMode.DRAFT_ONLY
    assert recommended_execution_mode(3) == ExecutionMode.ASSISTIVE
    assert recommended_execution_mode(4) == ExecutionMode.BOUNDED_AUTONOMY
    assert recommended_execution_mode(5) == ExecutionMode.RECURRING_AUTOMATION


def test_skill_rollback_requires_lower_maturity_and_failure_or_user_request():
    skill = _skill().model_copy(
        update={
            "maturity_level": 4,
            "execution_mode": ExecutionMode.BOUNDED_AUTONOMY,
            "status": "active",
        }
    )

    same_level = evaluate_skill_rollback(skill, target_maturity=4, failure_count=1)
    no_evidence = evaluate_skill_rollback(skill, target_maturity=3, failure_count=0)
    user_requested = evaluate_skill_rollback(
        skill,
        target_maturity=3,
        failure_count=0,
        user_requested=True,
    )

    assert same_level.reason == "rollback_must_reduce_maturity"
    assert no_evidence.reason == "failure_evidence_or_user_request_required"
    assert user_requested.allowed is True
    assert user_requested.recommended_execution_mode == ExecutionMode.ASSISTIVE


def test_rollback_skill_lowers_execution_without_expanding_permissions():
    skill = _skill(
        skill_id="skill_medium_assistive",
        risk_level=ActionRisk.MEDIUM.value,
        requires_confirmation_before=["send_message"],
    ).model_copy(
        update={
            "maturity_level": 3,
            "execution_mode": ExecutionMode.ASSISTIVE,
            "status": "active",
        }
    )

    rolled_back = rollback_skill(
        skill,
        target_maturity=2,
        failure_count=1,
        reason_ref="task_332_failed",
    )

    assert rolled_back.maturity_level == 2
    assert rolled_back.execution_mode == ExecutionMode.DRAFT_ONLY
    assert rolled_back.status == "candidate"
    assert rolled_back.requires_confirmation_before == ["send_message"]
    assert "rollback:task_332_failed" in rolled_back.failure_modes
