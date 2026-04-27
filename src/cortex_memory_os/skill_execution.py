"""Draft-only Skill Forge execution contracts."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from cortex_memory_os.contracts import ExecutionMode, SkillRecord

DRAFT_SKILL_EXECUTION_POLICY_REF = "policy_draft_skill_execution_v1"


class DraftSkillExecutionStatus(str, Enum):
    DRAFT_READY = "draft_ready"
    BLOCKED = "blocked"


class DraftSkillOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    output_id: str = Field(min_length=1)
    kind: str = Field(min_length=1)
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    review_required: bool = True


class DraftSkillExecutionResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    execution_id: str = Field(min_length=1)
    skill_id: str = Field(min_length=1)
    created_at: datetime
    status: DraftSkillExecutionStatus
    execution_mode: ExecutionMode
    policy_refs: tuple[str, ...]
    inputs: dict[str, Any]
    proposed_outputs: tuple[DraftSkillOutput, ...]
    external_effects_requested: tuple[str, ...] = ()
    external_effects_performed: tuple[str, ...] = ()
    required_review_actions: tuple[str, ...]
    blocked_reason: str | None = None


def prepare_draft_skill_execution(
    skill: SkillRecord,
    *,
    inputs: dict[str, Any] | None = None,
    requested_external_effects: tuple[str, ...] = (),
    now: datetime | None = None,
) -> DraftSkillExecutionResult:
    created_at = now or datetime.now(UTC)
    execution_id = _execution_id(skill.skill_id, created_at)
    normalized_inputs = dict(inputs or {})

    if skill.execution_mode != ExecutionMode.DRAFT_ONLY or skill.maturity_level > 2:
        return _blocked_result(
            skill=skill,
            execution_id=execution_id,
            created_at=created_at,
            inputs=normalized_inputs,
            requested_external_effects=requested_external_effects,
            reason="skill_not_draft_only",
        )

    if requested_external_effects:
        return _blocked_result(
            skill=skill,
            execution_id=execution_id,
            created_at=created_at,
            inputs=normalized_inputs,
            requested_external_effects=requested_external_effects,
            reason="draft_mode_blocks_external_effects",
        )

    return DraftSkillExecutionResult(
        execution_id=execution_id,
        skill_id=skill.skill_id,
        created_at=created_at,
        status=DraftSkillExecutionStatus.DRAFT_READY,
        execution_mode=ExecutionMode.DRAFT_ONLY,
        policy_refs=(DRAFT_SKILL_EXECUTION_POLICY_REF,),
        inputs=normalized_inputs,
        proposed_outputs=(
            DraftSkillOutput(
                output_id=f"{execution_id}_plan",
                kind="draft_plan",
                title=f"Draft plan for {skill.name}",
                content=_render_draft_plan(skill, normalized_inputs),
            ),
            DraftSkillOutput(
                output_id=f"{execution_id}_review",
                kind="review_checklist",
                title="Required review before any external effect",
                content=(
                    "Review the draft, edit outputs if needed, and explicitly approve "
                    "before any message, file change, purchase, deployment, or other "
                    "external effect."
                ),
            ),
        ),
        external_effects_requested=(),
        external_effects_performed=(),
        required_review_actions=("review", "edit", "approve_or_discard"),
    )


def _blocked_result(
    *,
    skill: SkillRecord,
    execution_id: str,
    created_at: datetime,
    inputs: dict[str, Any],
    requested_external_effects: tuple[str, ...],
    reason: str,
) -> DraftSkillExecutionResult:
    return DraftSkillExecutionResult(
        execution_id=execution_id,
        skill_id=skill.skill_id,
        created_at=created_at,
        status=DraftSkillExecutionStatus.BLOCKED,
        execution_mode=skill.execution_mode,
        policy_refs=(DRAFT_SKILL_EXECUTION_POLICY_REF,),
        inputs=inputs,
        proposed_outputs=(),
        external_effects_requested=tuple(requested_external_effects),
        external_effects_performed=(),
        required_review_actions=("revise_request", "choose_safer_mode"),
        blocked_reason=reason,
    )


def _render_draft_plan(skill: SkillRecord, inputs: dict[str, Any]) -> str:
    input_lines = [
        f"- {key}: {value}"
        for key, value in sorted(inputs.items())
    ] or ["- No explicit inputs provided."]
    procedure_lines = [
        f"{index}. {step}"
        for index, step in enumerate(skill.procedure, start=1)
    ]
    return "\n".join(
        [
            "Inputs:",
            *input_lines,
            "",
            "Procedure to draft for review:",
            *procedure_lines,
            "",
            "External effects performed: none.",
        ]
    )


def _execution_id(skill_id: str, created_at: datetime) -> str:
    timestamp = created_at.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"exec_{skill_id}_{timestamp}"
