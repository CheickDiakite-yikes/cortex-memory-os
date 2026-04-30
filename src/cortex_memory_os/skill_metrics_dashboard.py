"""Dashboard surface for Skill Forge success metrics."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime

from pydantic import Field, model_validator

from cortex_memory_os.contracts import SkillRecord, StrictModel
from cortex_memory_os.skill_metrics import (
    SKILL_SUCCESS_METRICS_POLICY_REF,
    SkillMetricCard,
    SkillOutcomeEvent,
    build_skill_metric_card,
    summarize_skill_outcomes,
)

SKILL_METRICS_DASHBOARD_SURFACE_ID = "SKILL-METRICS-DASHBOARD-SURFACE-001"
SKILL_METRICS_DASHBOARD_POLICY_REF = "policy_skill_metrics_dashboard_surface_v1"


class SkillMetricsDashboard(StrictModel):
    dashboard_id: str = SKILL_METRICS_DASHBOARD_SURFACE_ID
    generated_at: datetime
    cards: list[SkillMetricCard] = Field(default_factory=list)
    skill_count: int = Field(ge=0)
    total_run_count: int = Field(ge=0)
    review_required_count: int = Field(ge=0)
    procedure_text_included: bool = False
    task_content_included: bool = False
    autonomy_change_allowed: bool = False
    content_redacted: bool = True
    policy_refs: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def keep_dashboard_observational(self) -> SkillMetricsDashboard:
        if self.procedure_text_included or self.task_content_included:
            raise ValueError("skill metrics dashboard cannot include procedure or task text")
        if self.autonomy_change_allowed:
            raise ValueError("skill metrics dashboard cannot authorize autonomy changes")
        if not self.content_redacted:
            raise ValueError("skill metrics dashboard must keep content redacted")
        if SKILL_METRICS_DASHBOARD_POLICY_REF not in self.policy_refs:
            raise ValueError("skill metrics dashboard requires policy ref")
        if SKILL_SUCCESS_METRICS_POLICY_REF not in self.policy_refs:
            raise ValueError("skill metrics dashboard requires metrics policy ref")
        if any(
            not card.procedure_redacted
            or not card.content_redacted
            or card.autonomy_change_allowed
            for card in self.cards
        ):
            raise ValueError("skill metric cards must stay redacted and observational")
        return self


def build_skill_metrics_dashboard(
    skills: Iterable[SkillRecord],
    events: Iterable[SkillOutcomeEvent],
    *,
    now: datetime | None = None,
) -> SkillMetricsDashboard:
    timestamp = now or datetime.now(UTC)
    skill_list = sorted(skills, key=lambda skill: skill.skill_id)
    event_list = list(events)
    cards: list[SkillMetricCard] = []

    for skill in skill_list:
        metrics = summarize_skill_outcomes(skill, event_list)
        cards.append(build_skill_metric_card(skill, metrics))

    return SkillMetricsDashboard(
        generated_at=timestamp,
        cards=cards,
        skill_count=len(cards),
        total_run_count=sum(sum(card.outcome_counts.values()) for card in cards),
        review_required_count=sum(
            int(bool(card.promotion_blockers) or not card.autonomy_change_allowed)
            for card in cards
        ),
        procedure_text_included=False,
        task_content_included=False,
        autonomy_change_allowed=False,
        content_redacted=True,
        policy_refs=[
            SKILL_METRICS_DASHBOARD_POLICY_REF,
            SKILL_SUCCESS_METRICS_POLICY_REF,
        ],
        safety_notes=[
            "Metrics cards summarize outcomes without procedure text.",
            "Review recommendations do not change maturity or autonomy.",
            "Task content and verification details remain redacted.",
        ],
    )
