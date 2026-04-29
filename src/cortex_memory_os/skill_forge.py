"""Skill Forge pattern detector."""

from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime
import re

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from cortex_memory_os.contracts import (
    ActionRisk,
    ExecutionMode,
    MemoryStatus,
    Scene,
    Sensitivity,
    SkillRecord,
    SourceTrust,
)


MIN_SCENES_FOR_SKILL = 3
DOCUMENT_SKILL_DERIVATION_POLICY_REF = "policy_document_skill_derivation_v1"


class DocumentSkillDerivationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    document_id: str = Field(min_length=1)
    title: str = Field(min_length=1, max_length=120)
    source_ref: str = Field(min_length=1)
    source_trust: SourceTrust
    sensitivity: Sensitivity = Sensitivity.PRIVATE_WORK
    workflow_name: str = Field(min_length=1, max_length=120)
    trigger_conditions: list[str] = Field(min_length=1, max_length=8)
    procedure_steps: list[str] = Field(min_length=1, max_length=12)
    evidence_refs: list[str] = Field(min_length=1, max_length=12)
    risk_level: ActionRisk = ActionRisk.LOW
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("title", "workflow_name")
    @classmethod
    def reject_instruction_like_title(cls, value: str) -> str:
        _raise_for_instruction_like_text(value)
        return value

    @field_validator("trigger_conditions", "procedure_steps")
    @classmethod
    def reject_instruction_like_lists(cls, values: list[str]) -> list[str]:
        for value in values:
            _raise_for_instruction_like_text(value)
        return values

    @model_validator(mode="after")
    def reject_hostile_or_secret_source(self) -> DocumentSkillDerivationRequest:
        if self.source_trust == SourceTrust.HOSTILE_UNTIL_SAFE:
            raise ValueError("hostile documents cannot derive skill candidates")
        if self.sensitivity == Sensitivity.SECRET:
            raise ValueError("secret documents cannot derive skill candidates")
        return self


class DocumentSkillDerivationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    derivation_id: str = Field(min_length=1)
    skill: SkillRecord
    source_refs: list[str] = Field(min_length=1)
    policy_refs: tuple[str, ...] = Field(min_length=1)
    requires_user_confirmation: bool
    approval_actions: list[str] = Field(min_length=1)
    rollback_actions: list[str] = Field(min_length=1)
    deletion_actions: list[str] = Field(min_length=1)
    blocked_actions: list[str] = Field(min_length=1)
    content_redacted: bool = True

    @model_validator(mode="after")
    def enforce_candidate_only_derivation(self) -> DocumentSkillDerivationResult:
        if self.skill.status != MemoryStatus.CANDIDATE:
            raise ValueError("document-derived skills must remain candidates")
        if self.skill.execution_mode != ExecutionMode.DRAFT_ONLY:
            raise ValueError("document-derived skills must be draft-only")
        if self.skill.maturity_level > 2:
            raise ValueError("document-derived skills cannot exceed draft-only maturity")
        if not self.requires_user_confirmation:
            raise ValueError("document-derived skills require user confirmation")
        if DOCUMENT_SKILL_DERIVATION_POLICY_REF not in self.policy_refs:
            raise ValueError("document skill derivation requires policy reference")
        return self


def detect_skill_candidates(scenes: list[Scene]) -> list[SkillRecord]:
    grouped: dict[str, list[Scene]] = defaultdict(list)
    for scene in scenes:
        grouped[scene.scene_type].append(scene)

    candidates: list[SkillRecord] = []
    for scene_type, group in sorted(grouped.items()):
        if len(group) < MIN_SCENES_FOR_SKILL:
            continue
        candidates.append(_candidate_from_group(scene_type, group))
    return candidates


def derive_skill_candidate_from_document(
    request: DocumentSkillDerivationRequest,
) -> DocumentSkillDerivationResult:
    """Compile a governed document workflow into a draft-only skill candidate."""

    skill_id = f"skill_doc_{_slug(request.document_id)}_candidate_v1"
    source_refs = [request.document_id, request.source_ref, *request.evidence_refs]
    skill = SkillRecord(
        skill_id=skill_id,
        name=request.workflow_name,
        description=(
            "Draft-only skill candidate derived from a governed document workflow. "
            f"Source trust: {request.source_trust.value}."
        ),
        learned_from=source_refs,
        trigger_conditions=list(request.trigger_conditions),
        inputs={
            "document_id": "string",
            "goal": "string",
            "review_scope": "project | session | app",
        },
        procedure=list(request.procedure_steps),
        success_signals=[
            "user approves the candidate skill",
            "draft output accepted with low correction rate",
            "source document remains current during review",
        ],
        failure_modes=[
            "document instructions are stale",
            "source provenance is insufficient",
            "procedure requests external effects before approval",
        ],
        risk_level=request.risk_level,
        maturity_level=2,
        execution_mode=ExecutionMode.DRAFT_ONLY,
        requires_confirmation_before=[
            "promotion",
            "external_effect",
            "procedure_change",
            "source_deletion",
        ],
        status=MemoryStatus.CANDIDATE,
    )
    return DocumentSkillDerivationResult(
        derivation_id=f"derive_{skill_id}",
        skill=skill,
        source_refs=source_refs,
        policy_refs=(DOCUMENT_SKILL_DERIVATION_POLICY_REF,),
        requires_user_confirmation=True,
        approval_actions=[
            "skill.review_candidate",
            "skill.approve_draft_only",
        ],
        rollback_actions=[
            "skill.rollback_to_observed_pattern",
            "skill.mark_source_stale",
        ],
        deletion_actions=[
            "skill.delete_candidate",
            "memory.forget_source_refs",
        ],
        blocked_actions=[
            "promote_without_user_confirmation",
            "execute_external_effect",
            "copy_document_content_to_audit",
        ],
    )


def _candidate_from_group(scene_type: str, scenes: list[Scene]) -> SkillRecord:
    learned_from = [scene.scene_id for scene in scenes]
    apps = sorted({app for scene in scenes for app in scene.apps})
    entities = sorted({entity for scene in scenes for entity in scene.entities})

    return SkillRecord(
        skill_id=f"skill_{scene_type}_candidate_v1",
        name=_skill_name(scene_type),
        description=_description(scene_type, apps),
        learned_from=learned_from,
        trigger_conditions=_trigger_conditions(scene_type, entities),
        inputs={
            "goal": "string",
            "active_project": "string",
            "depth": "quick | normal | deep",
        },
        procedure=_procedure(scene_type),
        success_signals=[
            "user accepts draft",
            "low correction rate",
            "task outcome marked success",
        ],
        failure_modes=[
            "too much irrelevant context",
            "missing source refs",
            "action attempted beyond approved scope",
        ],
        risk_level=_risk_level(scene_type),
        maturity_level=2,
        execution_mode=ExecutionMode.DRAFT_ONLY,
        requires_confirmation_before=[],
        status=MemoryStatus.CANDIDATE,
    )


def _skill_name(scene_type: str) -> str:
    return {
        "research_sprint": "Research synthesis workflow",
        "coding_debugging": "Coding debugging workflow",
        "coding_work": "Coding work continuity workflow",
    }.get(scene_type, f"{scene_type.replace('_', ' ').title()} workflow")


def _description(scene_type: str, apps: list[str]) -> str:
    app_text = ", ".join(apps) if apps else "observed apps"
    return f"Draft-only workflow candidate learned from repeated {scene_type} scenes across {app_text}."


def _trigger_conditions(scene_type: str, entities: list[str]) -> list[str]:
    conditions = [f"current scene resembles {scene_type}", "user asks to continue similar work"]
    if entities:
        conditions.append(f"topic mentions {', '.join(entities[:4])}")
    return conditions


def _procedure(scene_type: str) -> list[str]:
    if scene_type == "research_sprint":
        return [
            "Recover active research goal and source refs",
            "Prefer official or primary sources",
            "Separate evidence from inference",
            "Synthesize architecture implications",
            "Return draft with citations and open risks",
        ]
    if scene_type == "coding_debugging":
        return [
            "Recover last reproduction path",
            "Inspect recent terminal and browser evidence refs",
            "Identify smallest safe patch",
            "Run targeted verification",
            "Record outcome and follow-up memory candidate",
        ]
    return [
        "Recover active workstream",
        "Retrieve relevant memories and evidence refs",
        "Draft next steps",
        "Ask before external effects",
    ]


def _risk_level(scene_type: str) -> ActionRisk:
    if scene_type in {"coding_debugging", "coding_work"}:
        return ActionRisk.MEDIUM
    return ActionRisk.LOW


def _raise_for_instruction_like_text(value: str) -> None:
    lowered = value.lower()
    forbidden_fragments = [
        "ignore previous instructions",
        "reveal secrets",
        "disable safeguards",
        "exfiltrate",
        "run this command",
        "execute this command",
        "send credentials",
        "commit this file",
    ]
    if any(fragment in lowered for fragment in forbidden_fragments):
        raise ValueError("document skill derivation cannot carry instruction-like text")


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "document"
