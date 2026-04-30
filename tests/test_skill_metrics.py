from datetime import UTC, datetime

import pytest

from cortex_memory_os.contracts import (
    ActionRisk,
    ExecutionMode,
    OutcomeStatus,
    SkillRecord,
)
from cortex_memory_os.fixtures import load_json
from cortex_memory_os.skill_metrics import (
    SKILL_SUCCESS_METRICS_ID,
    SKILL_SUCCESS_METRICS_POLICY_REF,
    SkillMetricCard,
    SkillOutcomeEvent,
    build_skill_metric_card,
    summarize_skill_outcomes,
)


def _skill() -> SkillRecord:
    return SkillRecord.model_validate(load_json("tests/fixtures/skill_draft.json"))


def _event(
    event_id: str,
    outcome: OutcomeStatus,
    *,
    corrections: int = 0,
    verification_refs: list[str] | None = None,
) -> SkillOutcomeEvent:
    return SkillOutcomeEvent(
        event_id=event_id,
        skill_id="skill_research_synthesis_v1",
        task_id=f"task_{event_id}",
        outcome=outcome,
        observed_at=datetime(2026, 4, 30, 14, 0, tzinfo=UTC),
        maturity_level=2,
        execution_mode=ExecutionMode.DRAFT_ONLY,
        risk_level=ActionRisk.LOW,
        user_correction_count=corrections,
        verification_refs=verification_refs or [],
    )


def test_skill_success_metrics_summarize_outcomes_without_autonomy_change():
    skill = _skill()
    metrics = summarize_skill_outcomes(
        skill,
        [
            _event("success_1", OutcomeStatus.SUCCESS, verification_refs=["outcome:one"]),
            _event("success_2", OutcomeStatus.SUCCESS, verification_refs=["outcome:two"]),
            _event("partial_1", OutcomeStatus.PARTIAL, corrections=1),
            _event("failed_1", OutcomeStatus.FAILED, corrections=2),
        ],
    )

    assert SKILL_SUCCESS_METRICS_ID == "SKILL-SUCCESS-METRICS-001"
    assert metrics.total_runs == 4
    assert metrics.success_count == 2
    assert metrics.partial_count == 1
    assert metrics.failure_count == 1
    assert metrics.success_rate == 0.5
    assert metrics.correction_rate == 0.75
    assert metrics.verification_ref_count == 2
    assert metrics.review_recommendation == "eligible_for_human_promotion_review"
    assert metrics.promotion_blockers == ["user_approval_required"]
    assert metrics.autonomy_change_allowed is False
    assert metrics.content_redacted is True
    assert SKILL_SUCCESS_METRICS_POLICY_REF in metrics.policy_refs
    assert skill.maturity_level == 2
    assert skill.execution_mode == ExecutionMode.DRAFT_ONLY


def test_skill_metric_card_is_dashboard_safe_and_redacted():
    skill = _skill()
    metrics = summarize_skill_outcomes(
        skill,
        [_event("success_1", OutcomeStatus.SUCCESS), _event("success_2", OutcomeStatus.SUCCESS)],
    )
    card = build_skill_metric_card(skill, metrics)
    payload = card.model_dump()

    assert card.outcome_counts["success"] == 2
    assert card.review_actions == [
        "skill.review_metrics",
        "skill.inspect_outcomes",
        "skill.review_promotion_gate",
    ]
    assert card.procedure_redacted is True
    assert card.content_redacted is True
    assert card.autonomy_change_allowed is False
    assert "procedure" not in payload
    assert "Search current primary sources" not in str(payload)


def test_skill_outcome_event_rejects_external_effects_for_draft_only_metrics():
    with pytest.raises(ValueError, match="draft-only skill metrics"):
        SkillOutcomeEvent(
            event_id="evt_external",
            skill_id="skill_research_synthesis_v1",
            task_id="task_external",
            outcome=OutcomeStatus.SUCCESS,
            maturity_level=2,
            execution_mode=ExecutionMode.DRAFT_ONLY,
            risk_level=ActionRisk.LOW,
            external_effects_performed=["sent_email"],
        )

    with pytest.raises(ValueError, match="raw verification refs"):
        SkillOutcomeEvent(
            event_id="evt_raw_ref",
            skill_id="skill_research_synthesis_v1",
            task_id="task_raw",
            outcome=OutcomeStatus.SUCCESS,
            maturity_level=2,
            execution_mode=ExecutionMode.DRAFT_ONLY,
            risk_level=ActionRisk.LOW,
            verification_refs=["raw://screen/frame_1"],
        )


def test_skill_metric_card_rejects_leaky_or_autonomous_shapes():
    with pytest.raises(ValueError, match="redact procedure and content"):
        SkillMetricCard(
            skill_id="skill_research_synthesis_v1",
            name="Research",
            maturity_level=2,
            execution_mode=ExecutionMode.DRAFT_ONLY,
            risk_level=ActionRisk.LOW,
            outcome_counts={"success": 1},
            success_rate=1.0,
            correction_rate=0.0,
            verification_ref_count=1,
            review_recommendation="review",
            procedure_redacted=False,
        )

    with pytest.raises(ValueError, match="cannot authorize autonomy changes"):
        SkillMetricCard(
            skill_id="skill_research_synthesis_v1",
            name="Research",
            maturity_level=2,
            execution_mode=ExecutionMode.DRAFT_ONLY,
            risk_level=ActionRisk.LOW,
            outcome_counts={"success": 1},
            success_rate=1.0,
            correction_rate=0.0,
            verification_ref_count=1,
            review_recommendation="review",
            autonomy_change_allowed=True,
        )
