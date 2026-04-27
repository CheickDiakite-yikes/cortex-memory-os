"""Skill Forge maturity promotion gates."""

from __future__ import annotations

from dataclasses import dataclass

from cortex_memory_os.contracts import ActionRisk, ExecutionMode, MemoryStatus, SkillRecord


@dataclass(frozen=True)
class SkillPromotionDecision:
    allowed: bool
    target_maturity: int
    required_behavior: str
    reason: str
    recommended_execution_mode: ExecutionMode


@dataclass(frozen=True)
class SkillRollbackDecision:
    allowed: bool
    target_maturity: int
    required_behavior: str
    reason: str
    recommended_execution_mode: ExecutionMode


def evaluate_skill_promotion(
    skill: SkillRecord,
    *,
    target_maturity: int,
    observed_successes: int,
    user_approved: bool,
) -> SkillPromotionDecision:
    if target_maturity < skill.maturity_level:
        return _deny(skill, target_maturity, "promotion_cannot_downgrade")
    if target_maturity > 5:
        return _deny(skill, target_maturity, "target_maturity_out_of_range")
    if target_maturity - skill.maturity_level > 1:
        return _deny(skill, target_maturity, "promotion_must_be_incremental")
    if target_maturity >= 3 and not user_approved:
        return _deny(skill, target_maturity, "user_approval_required")
    if target_maturity >= 3 and observed_successes < 2:
        return _deny(skill, target_maturity, "insufficient_success_evidence")
    if skill.risk_level == ActionRisk.CRITICAL and target_maturity > 2:
        return _deny(skill, target_maturity, "critical_skill_stays_draft_only")
    if skill.risk_level == ActionRisk.HIGH and target_maturity >= 4:
        return _deny(skill, target_maturity, "high_risk_no_autonomy")
    if target_maturity >= 4 and skill.risk_level != ActionRisk.LOW:
        return _deny(skill, target_maturity, "only_low_risk_can_reach_bounded_autonomy")
    if target_maturity == 4 and observed_successes < 5:
        return _deny(skill, target_maturity, "bounded_autonomy_requires_five_successes")
    if target_maturity == 5:
        return _deny(skill, target_maturity, "recurring_automation_disabled_in_mvp")

    behavior = {
        0: "observe_only",
        1: "suggest_only",
        2: "draft_only",
        3: "confirm_external_effects",
        4: "bounded_sandbox_with_audit",
    }.get(target_maturity, "blocked_by_default")
    return SkillPromotionDecision(
        allowed=True,
        target_maturity=target_maturity,
        required_behavior=behavior,
        reason="promotion_allowed",
        recommended_execution_mode=recommended_execution_mode(target_maturity),
    )


def evaluate_skill_rollback(
    skill: SkillRecord,
    *,
    target_maturity: int,
    failure_count: int,
    user_requested: bool = False,
) -> SkillRollbackDecision:
    if target_maturity < 0:
        return _deny_rollback(skill, target_maturity, "target_maturity_out_of_range")
    if target_maturity >= skill.maturity_level:
        return _deny_rollback(skill, target_maturity, "rollback_must_reduce_maturity")
    if failure_count < 1 and not user_requested:
        return _deny_rollback(skill, target_maturity, "failure_evidence_or_user_request_required")
    if skill.risk_level == ActionRisk.CRITICAL and target_maturity > 2:
        return _deny_rollback(skill, target_maturity, "critical_skill_stays_draft_only")
    return SkillRollbackDecision(
        allowed=True,
        target_maturity=target_maturity,
        required_behavior=_required_behavior(target_maturity),
        reason="rollback_allowed",
        recommended_execution_mode=recommended_execution_mode(target_maturity),
    )


def rollback_skill(
    skill: SkillRecord,
    *,
    target_maturity: int,
    failure_count: int,
    user_requested: bool = False,
    reason_ref: str | None = None,
) -> SkillRecord:
    decision = evaluate_skill_rollback(
        skill,
        target_maturity=target_maturity,
        failure_count=failure_count,
        user_requested=user_requested,
    )
    if not decision.allowed:
        raise ValueError(decision.reason)

    failure_modes = list(skill.failure_modes)
    if reason_ref:
        rollback_ref = f"rollback:{reason_ref}"
        if rollback_ref not in failure_modes:
            failure_modes.append(rollback_ref)

    return skill.model_copy(
        update={
            "maturity_level": target_maturity,
            "execution_mode": decision.recommended_execution_mode,
            "status": MemoryStatus.CANDIDATE if target_maturity <= 2 else skill.status,
            "failure_modes": failure_modes,
        }
    )


def recommended_execution_mode(maturity_level: int) -> ExecutionMode:
    if maturity_level <= 2:
        return ExecutionMode.DRAFT_ONLY
    if maturity_level == 3:
        return ExecutionMode.ASSISTIVE
    if maturity_level == 4:
        return ExecutionMode.BOUNDED_AUTONOMY
    return ExecutionMode.RECURRING_AUTOMATION


def _required_behavior(maturity_level: int) -> str:
    return {
        0: "observe_only",
        1: "suggest_only",
        2: "draft_only",
        3: "confirm_external_effects",
        4: "bounded_sandbox_with_audit",
    }.get(maturity_level, "blocked_by_default")


def _deny(skill: SkillRecord, target_maturity: int, reason: str) -> SkillPromotionDecision:
    return SkillPromotionDecision(
        allowed=False,
        target_maturity=target_maturity,
        required_behavior="keep_current_maturity",
        reason=reason,
        recommended_execution_mode=skill.execution_mode,
    )


def _deny_rollback(
    skill: SkillRecord,
    target_maturity: int,
    reason: str,
) -> SkillRollbackDecision:
    return SkillRollbackDecision(
        allowed=False,
        target_maturity=target_maturity,
        required_behavior="keep_current_maturity",
        reason=reason,
        recommended_execution_mode=skill.execution_mode,
    )
