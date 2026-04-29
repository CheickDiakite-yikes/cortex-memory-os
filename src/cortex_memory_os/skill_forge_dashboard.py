"""Dashboard-facing Skill Forge candidate list view models."""

from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime

from pydantic import Field

from cortex_memory_os.contracts import (
    ActionRisk,
    ExecutionMode,
    MemoryStatus,
    SkillRecord,
    StrictModel,
)
from cortex_memory_os.firewall import redact_sensitive_text
from cortex_memory_os.skill_policy import evaluate_skill_promotion

SKILL_FORGE_CANDIDATE_LIST_POLICY_REF = "policy_skill_forge_candidate_list_v1"

_VISIBLE_STATUSES = {MemoryStatus.CANDIDATE}


class SkillForgeActionPlan(StrictModel):
    action_id: str = Field(min_length=1)
    gateway_tool: str = Field(min_length=1)
    required_inputs: list[str] = Field(default_factory=list)
    requires_confirmation: bool
    mutation: bool
    external_effect: bool = False
    audit_action: str | None = None
    content_redacted: bool = True


class SkillForgeCandidateCard(StrictModel):
    skill_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    status: MemoryStatus
    risk_level: ActionRisk
    maturity_level: int = Field(ge=0, le=5)
    execution_mode: ExecutionMode
    learned_from_count: int = Field(ge=0)
    learned_from_refs: list[str] = Field(default_factory=list)
    trigger_count: int = Field(ge=0)
    procedure_step_count: int = Field(ge=0)
    success_signal_count: int = Field(ge=0)
    failure_mode_count: int = Field(ge=0)
    requires_confirmation_before: list[str] = Field(default_factory=list)
    description_preview: str | None = None
    procedure_preview: list[str] = Field(default_factory=list)
    redaction_count: int = Field(ge=0)
    content_redacted: bool = True
    promotion_target_maturity: int = Field(ge=0, le=5)
    promotion_allowed_now: bool
    promotion_blockers: list[str] = Field(default_factory=list)
    recommended_execution_mode: ExecutionMode
    action_plans: list[SkillForgeActionPlan] = Field(default_factory=list)


class SkillForgeCandidateList(StrictModel):
    list_id: str = Field(min_length=1)
    generated_at: datetime
    cards: list[SkillForgeCandidateCard] = Field(default_factory=list)
    candidate_count: int = Field(ge=0)
    status_counts: dict[str, int] = Field(default_factory=dict)
    risk_counts: dict[str, int] = Field(default_factory=dict)
    review_required_count: int = Field(ge=0)
    external_effect_action_count: int = Field(ge=0)
    policy_refs: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)


def build_skill_forge_candidate_list(
    skills: list[SkillRecord],
    *,
    now: datetime | None = None,
) -> SkillForgeCandidateList:
    timestamp = now or datetime.now(UTC)
    visible = [skill for skill in skills if skill.status in _VISIBLE_STATUSES]
    cards = [_card_for_skill(skill) for skill in sorted(visible, key=_skill_sort_key)]

    return SkillForgeCandidateList(
        list_id=f"skill_forge_candidate_list_{timestamp.strftime('%Y%m%dT%H%M%SZ')}",
        generated_at=timestamp,
        cards=cards,
        candidate_count=len(cards),
        status_counts={
            status: count
            for status, count in sorted(Counter(skill.status.value for skill in skills).items())
        },
        risk_counts={
            risk: count
            for risk, count in sorted(Counter(card.risk_level.value for card in cards).items())
        },
        review_required_count=sum(
            1
            for card in cards
            for action in card.action_plans
            if action.requires_confirmation
        ),
        external_effect_action_count=sum(
            1
            for card in cards
            for action in card.action_plans
            if action.external_effect
        ),
        policy_refs=[SKILL_FORGE_CANDIDATE_LIST_POLICY_REF],
        safety_notes=[
            "Candidate list cards are review surfaces, not execution permission.",
            "Procedure previews are truncated and redacted before rendering.",
            "Promotion blockers show why autonomy cannot expand yet.",
            "Action plans point to gateway tools but do not perform external effects.",
        ],
    )


def _card_for_skill(skill: SkillRecord) -> SkillForgeCandidateCard:
    target_maturity = min(skill.maturity_level + 1, 5)
    promotion = evaluate_skill_promotion(
        skill,
        target_maturity=target_maturity,
        observed_successes=0,
        user_approved=False,
    )
    description_preview, description_redactions = _preview_text(skill.description)
    procedure_preview, procedure_redactions = _procedure_preview(skill.procedure)
    redaction_count = description_redactions + procedure_redactions

    return SkillForgeCandidateCard(
        skill_id=skill.skill_id,
        name=skill.name,
        status=skill.status,
        risk_level=skill.risk_level,
        maturity_level=skill.maturity_level,
        execution_mode=skill.execution_mode,
        learned_from_count=len(skill.learned_from),
        learned_from_refs=list(skill.learned_from[:6]),
        trigger_count=len(skill.trigger_conditions),
        procedure_step_count=len(skill.procedure),
        success_signal_count=len(skill.success_signals),
        failure_mode_count=len(skill.failure_modes),
        requires_confirmation_before=list(skill.requires_confirmation_before),
        description_preview=description_preview,
        procedure_preview=procedure_preview,
        redaction_count=redaction_count,
        content_redacted=redaction_count > 0,
        promotion_target_maturity=target_maturity,
        promotion_allowed_now=promotion.allowed,
        promotion_blockers=[] if promotion.allowed else [promotion.reason],
        recommended_execution_mode=promotion.recommended_execution_mode,
        action_plans=_action_plans_for_skill(skill),
    )


def _action_plans_for_skill(skill: SkillRecord) -> list[SkillForgeActionPlan]:
    plans = [
        SkillForgeActionPlan(
            action_id="review_candidate",
            gateway_tool="skill.review_candidate",
            required_inputs=["skill_id"],
            requires_confirmation=False,
            mutation=False,
            audit_action=None,
        ),
        SkillForgeActionPlan(
            action_id="approve_draft_only",
            gateway_tool="skill.approve_draft_only",
            required_inputs=["skill_id", "approval_ref"],
            requires_confirmation=True,
            mutation=True,
            audit_action="approve_skill_candidate",
        ),
        SkillForgeActionPlan(
            action_id="edit_steps",
            gateway_tool="skill.edit_candidate",
            required_inputs=["skill_id", "corrected_steps", "approval_ref"],
            requires_confirmation=True,
            mutation=True,
            audit_action="edit_skill_candidate",
        ),
        SkillForgeActionPlan(
            action_id="need_more_data",
            gateway_tool="skill.need_more_data",
            required_inputs=["skill_id", "reason"],
            requires_confirmation=False,
            mutation=True,
            audit_action="defer_skill_candidate",
        ),
        SkillForgeActionPlan(
            action_id="reject_candidate",
            gateway_tool="skill.reject_candidate",
            required_inputs=["skill_id", "approval_ref"],
            requires_confirmation=True,
            mutation=True,
            audit_action="reject_skill_candidate",
        ),
    ]
    if skill.execution_mode == ExecutionMode.DRAFT_ONLY:
        plans.insert(
            1,
            SkillForgeActionPlan(
                action_id="execute_draft",
                gateway_tool="skill.execute_draft",
                required_inputs=["skill_id", "input_summary"],
                requires_confirmation=False,
                mutation=False,
                external_effect=False,
                audit_action=None,
            ),
        )
    return plans


def _preview_text(value: str, max_chars: int = 180) -> tuple[str, int]:
    redacted, redactions = redact_sensitive_text(value)
    return _truncate(redacted, max_chars), len(redactions)


def _procedure_preview(steps: list[str]) -> tuple[list[str], int]:
    previews: list[str] = []
    redaction_count = 0
    for step in steps[:2]:
        preview, redactions = _preview_text(step, max_chars=120)
        previews.append(preview)
        redaction_count += redactions
    return previews, redaction_count


def _skill_sort_key(skill: SkillRecord) -> tuple[int, int, str]:
    return (
        _risk_rank(skill.risk_level) * -1,
        skill.maturity_level * -1,
        skill.skill_id,
    )


def _risk_rank(risk: ActionRisk) -> int:
    return {
        ActionRisk.LOW: 0,
        ActionRisk.MEDIUM: 1,
        ActionRisk.HIGH: 2,
        ActionRisk.CRITICAL: 3,
    }[risk]


def _truncate(value: str, max_chars: int) -> str:
    if len(value) <= max_chars:
        return value
    return value[: max_chars - 1].rstrip() + "..."
