import json
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from cortex_memory_os.contracts import (
    ActionRisk,
    ExecutionMode,
    MemoryStatus,
    OutcomeStatus,
    SkillRecord,
)
from cortex_memory_os.skill_metrics import SkillOutcomeEvent
from cortex_memory_os.skill_metrics_dashboard import (
    SKILL_METRICS_DASHBOARD_POLICY_REF,
    SKILL_METRICS_DASHBOARD_SURFACE_ID,
    SkillMetricsDashboard,
    build_skill_metrics_dashboard,
)


NOW = datetime(2026, 4, 30, 6, 30, tzinfo=UTC)


def _skill() -> SkillRecord:
    return SkillRecord(
        skill_id="skill_metrics_dashboard_test",
        name="Dashboard Metrics Test",
        description="Summarize skill outcomes without revealing procedure text.",
        learned_from=["scene_metrics_001"],
        trigger_conditions=["user asks for metrics"],
        inputs={"topic": "string"},
        procedure=[
            "Search current primary sources",
            "Draft sensitive workflow details",
        ],
        success_signals=["review passes"],
        failure_modes=["procedure leaked"],
        risk_level=ActionRisk.LOW,
        maturity_level=2,
        execution_mode=ExecutionMode.DRAFT_ONLY,
        status=MemoryStatus.CANDIDATE,
    )


def _event(skill: SkillRecord, event_id: str, outcome: OutcomeStatus) -> SkillOutcomeEvent:
    return SkillOutcomeEvent(
        event_id=event_id,
        skill_id=skill.skill_id,
        task_id=f"task_{event_id}",
        outcome=outcome,
        observed_at=NOW,
        maturity_level=skill.maturity_level,
        execution_mode=skill.execution_mode,
        risk_level=skill.risk_level,
        verification_refs=["test://metrics-dashboard"],
    )


def test_skill_metrics_dashboard_is_dashboard_safe():
    skill = _skill()
    dashboard = build_skill_metrics_dashboard(
        [skill],
        [
            _event(skill, "success_001", OutcomeStatus.SUCCESS),
            _event(skill, "failed_001", OutcomeStatus.FAILED),
        ],
        now=NOW,
    )
    payload = json.dumps(dashboard.model_dump(mode="json"), sort_keys=True)

    assert dashboard.dashboard_id == SKILL_METRICS_DASHBOARD_SURFACE_ID
    assert SKILL_METRICS_DASHBOARD_POLICY_REF in dashboard.policy_refs
    assert dashboard.skill_count == 1
    assert dashboard.total_run_count == 2
    assert dashboard.cards[0].procedure_redacted
    assert dashboard.cards[0].content_redacted
    assert not dashboard.autonomy_change_allowed
    assert not dashboard.procedure_text_included
    assert "Search current primary sources" not in payload
    assert "Draft sensitive workflow details" not in payload
    assert "task_success_001" not in payload


def test_skill_metrics_dashboard_rejects_procedure_or_autonomy_leaks():
    skill = _skill()
    dashboard = build_skill_metrics_dashboard([skill], [], now=NOW)

    with pytest.raises(ValidationError, match="procedure or task text"):
        SkillMetricsDashboard.model_validate(
            dashboard.model_dump() | {"procedure_text_included": True}
        )

    with pytest.raises(ValidationError, match="autonomy"):
        SkillMetricsDashboard.model_validate(
            dashboard.model_dump() | {"autonomy_change_allowed": True}
        )
