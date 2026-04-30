"""Skill Forge success/failure metrics without autonomy changes."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from datetime import UTC, datetime

from pydantic import Field, model_validator

from cortex_memory_os.contracts import (
    ActionRisk,
    ExecutionMode,
    OutcomeStatus,
    SkillRecord,
    StrictModel,
)
from cortex_memory_os.skill_policy import evaluate_skill_promotion

SKILL_SUCCESS_METRICS_ID = "SKILL-SUCCESS-METRICS-001"
SKILL_SUCCESS_METRICS_POLICY_REF = "policy_skill_success_metrics_v1"


class SkillOutcomeEvent(StrictModel):
    event_id: str = Field(min_length=1)
    skill_id: str = Field(min_length=1)
    task_id: str = Field(min_length=1)
    outcome: OutcomeStatus
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    maturity_level: int = Field(ge=0, le=5)
    execution_mode: ExecutionMode
    risk_level: ActionRisk
    user_correction_count: int = Field(default=0, ge=0)
    verification_refs: list[str] = Field(default_factory=list)
    external_effects_performed: list[str] = Field(default_factory=list)
    content_redacted: bool = True
    policy_refs: list[str] = Field(default_factory=lambda: [SKILL_SUCCESS_METRICS_POLICY_REF])

    @model_validator(mode="after")
    def keep_event_metric_only(self) -> SkillOutcomeEvent:
        if not self.content_redacted:
            raise ValueError("skill outcome metrics must keep task content redacted")
        if self.execution_mode == ExecutionMode.DRAFT_ONLY and self.external_effects_performed:
            raise ValueError("draft-only skill metrics cannot record external effects")
        if any(ref.startswith("raw://") for ref in self.verification_refs):
            raise ValueError("skill outcome metrics cannot carry raw verification refs")
        if SKILL_SUCCESS_METRICS_POLICY_REF not in self.policy_refs:
            raise ValueError("skill outcome metrics require policy ref")
        return self


class SkillSuccessMetrics(StrictModel):
    skill_id: str = Field(min_length=1)
    total_runs: int = Field(ge=0)
    success_count: int = Field(ge=0)
    partial_count: int = Field(ge=0)
    failure_count: int = Field(ge=0)
    user_rejected_count: int = Field(ge=0)
    unsafe_blocked_count: int = Field(ge=0)
    success_rate: float = Field(ge=0.0, le=1.0)
    correction_rate: float = Field(ge=0.0)
    verification_ref_count: int = Field(ge=0)
    maturity_evidence: str = Field(min_length=1)
    review_recommendation: str = Field(min_length=1)
    promotion_blockers: list[str] = Field(default_factory=list)
    autonomy_change_allowed: bool = False
    content_redacted: bool = True
    policy_refs: list[str] = Field(default_factory=lambda: [SKILL_SUCCESS_METRICS_POLICY_REF])

    @model_validator(mode="after")
    def keep_metrics_observational(self) -> SkillSuccessMetrics:
        if self.autonomy_change_allowed:
            raise ValueError("skill metrics cannot authorize autonomy changes")
        if not self.content_redacted:
            raise ValueError("skill metrics must keep content redacted")
        if SKILL_SUCCESS_METRICS_POLICY_REF not in self.policy_refs:
            raise ValueError("skill metrics require policy ref")
        return self


class SkillMetricCard(StrictModel):
    skill_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    maturity_level: int = Field(ge=0, le=5)
    execution_mode: ExecutionMode
    risk_level: ActionRisk
    outcome_counts: dict[str, int]
    success_rate: float = Field(ge=0.0, le=1.0)
    correction_rate: float = Field(ge=0.0)
    verification_ref_count: int = Field(ge=0)
    review_recommendation: str = Field(min_length=1)
    promotion_blockers: list[str] = Field(default_factory=list)
    review_actions: list[str] = Field(default_factory=list)
    procedure_redacted: bool = True
    content_redacted: bool = True
    autonomy_change_allowed: bool = False
    policy_refs: list[str] = Field(default_factory=lambda: [SKILL_SUCCESS_METRICS_POLICY_REF])

    @model_validator(mode="after")
    def keep_card_dashboard_safe(self) -> SkillMetricCard:
        if not self.procedure_redacted or not self.content_redacted:
            raise ValueError("skill metric cards must redact procedure and content")
        if self.autonomy_change_allowed:
            raise ValueError("skill metric cards cannot authorize autonomy changes")
        if SKILL_SUCCESS_METRICS_POLICY_REF not in self.policy_refs:
            raise ValueError("skill metric cards require policy ref")
        return self


def summarize_skill_outcomes(
    skill: SkillRecord,
    events: Iterable[SkillOutcomeEvent],
) -> SkillSuccessMetrics:
    matching_events = [event for event in events if event.skill_id == skill.skill_id]
    counts = Counter(event.outcome for event in matching_events)
    total_runs = len(matching_events)
    success_count = counts[OutcomeStatus.SUCCESS]
    correction_count = sum(event.user_correction_count for event in matching_events)
    verification_ref_count = sum(len(event.verification_refs) for event in matching_events)
    success_rate = success_count / total_runs if total_runs else 0.0
    correction_rate = correction_count / total_runs if total_runs else 0.0
    promotion_decision = evaluate_skill_promotion(
        skill,
        target_maturity=min(skill.maturity_level + 1, 5),
        observed_successes=success_count,
        user_approved=False,
    )
    maturity_evidence = _maturity_evidence(total_runs, success_count, correction_rate)
    blockers = [] if promotion_decision.allowed else [promotion_decision.reason]

    return SkillSuccessMetrics(
        skill_id=skill.skill_id,
        total_runs=total_runs,
        success_count=success_count,
        partial_count=counts[OutcomeStatus.PARTIAL],
        failure_count=counts[OutcomeStatus.FAILED],
        user_rejected_count=counts[OutcomeStatus.USER_REJECTED],
        unsafe_blocked_count=counts[OutcomeStatus.UNSAFE_BLOCKED],
        success_rate=round(success_rate, 4),
        correction_rate=round(correction_rate, 4),
        verification_ref_count=verification_ref_count,
        maturity_evidence=maturity_evidence,
        review_recommendation=_review_recommendation(
            total_runs=total_runs,
            success_count=success_count,
            failure_count=counts[OutcomeStatus.FAILED],
            unsafe_blocked_count=counts[OutcomeStatus.UNSAFE_BLOCKED],
        ),
        promotion_blockers=blockers,
        autonomy_change_allowed=False,
        content_redacted=True,
        policy_refs=[SKILL_SUCCESS_METRICS_POLICY_REF],
    )


def build_skill_metric_card(
    skill: SkillRecord,
    metrics: SkillSuccessMetrics,
) -> SkillMetricCard:
    return SkillMetricCard(
        skill_id=skill.skill_id,
        name=skill.name,
        maturity_level=skill.maturity_level,
        execution_mode=skill.execution_mode,
        risk_level=skill.risk_level,
        outcome_counts={
            "success": metrics.success_count,
            "partial": metrics.partial_count,
            "failed": metrics.failure_count,
            "user_rejected": metrics.user_rejected_count,
            "unsafe_blocked": metrics.unsafe_blocked_count,
        },
        success_rate=metrics.success_rate,
        correction_rate=metrics.correction_rate,
        verification_ref_count=metrics.verification_ref_count,
        review_recommendation=metrics.review_recommendation,
        promotion_blockers=list(metrics.promotion_blockers),
        review_actions=[
            "skill.review_metrics",
            "skill.inspect_outcomes",
            "skill.review_promotion_gate",
        ],
        procedure_redacted=True,
        content_redacted=True,
        autonomy_change_allowed=False,
        policy_refs=list(metrics.policy_refs),
    )


def _maturity_evidence(total_runs: int, success_count: int, correction_rate: float) -> str:
    if total_runs == 0:
        return "no_outcome_evidence"
    if success_count >= 5 and correction_rate <= 0.2:
        return "strong_success_evidence_review_required"
    if success_count >= 2 and correction_rate <= 0.5:
        return "draft_success_evidence_review_required"
    return "insufficient_or_mixed_evidence"


def _review_recommendation(
    *,
    total_runs: int,
    success_count: int,
    failure_count: int,
    unsafe_blocked_count: int,
) -> str:
    if total_runs == 0:
        return "keep_observing"
    if unsafe_blocked_count:
        return "safety_review_before_reuse"
    if failure_count > success_count:
        return "review_failures_before_promotion"
    if success_count >= 2:
        return "eligible_for_human_promotion_review"
    return "keep_draft_only_collect_more_evidence"
