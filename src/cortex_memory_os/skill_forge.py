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
WORKFLOW_CLUSTERING_ID = "WORKFLOW-CLUSTERING-001"
WORKFLOW_CLUSTERING_POLICY_REF = "policy_workflow_clustering_v1"


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


class WorkflowTrace(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    trace_id: str = Field(min_length=1)
    workflow_label: str = Field(min_length=1, max_length=120)
    source_trust: SourceTrust = SourceTrust.LOCAL_OBSERVED
    apps: list[str] = Field(min_length=1, max_length=8)
    action_kinds: list[str] = Field(min_length=2, max_length=16)
    outcome: str = Field(min_length=1, max_length=80)
    evidence_refs: list[str] = Field(min_length=1, max_length=12)
    external_effect_count: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("workflow_label")
    @classmethod
    def reject_instruction_like_workflow_label(cls, value: str) -> str:
        _raise_for_instruction_like_text(value)
        return value

    @field_validator("action_kinds")
    @classmethod
    def reject_instruction_like_actions(cls, values: list[str]) -> list[str]:
        for value in values:
            _raise_for_instruction_like_text(value)
        return values

    @model_validator(mode="after")
    def keep_trace_clusterable(self) -> "WorkflowTrace":
        if self.source_trust == SourceTrust.HOSTILE_UNTIL_SAFE:
            raise ValueError("hostile workflow traces cannot be clustered into skills")
        if self.external_effect_count:
            raise ValueError("workflow clustering requires traces without external effects")
        return self


class WorkflowCluster(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cluster_id: str = Field(min_length=1)
    workflow_label: str = Field(min_length=1)
    signature: str = Field(min_length=1)
    trace_ids: list[str] = Field(min_length=1)
    app_count: int = Field(ge=0)
    action_count: int = Field(ge=0)
    success_count: int = Field(ge=0)
    evidence_ref_count: int = Field(ge=0)
    candidate_skill: SkillRecord | None = None
    candidate_only: bool = True
    draft_preview_available: bool = True
    content_redacted: bool = True
    source_refs_redacted: bool = True
    policy_refs: tuple[str, ...] = Field(default=(WORKFLOW_CLUSTERING_POLICY_REF,))

    @model_validator(mode="after")
    def enforce_candidate_only_cluster(self) -> "WorkflowCluster":
        if WORKFLOW_CLUSTERING_POLICY_REF not in self.policy_refs:
            raise ValueError("workflow clusters require policy ref")
        if not self.candidate_only:
            raise ValueError("workflow clusters must remain candidate-only")
        if not self.content_redacted or not self.source_refs_redacted:
            raise ValueError("workflow clusters must stay redacted")
        if self.candidate_skill is not None:
            if self.candidate_skill.status != MemoryStatus.CANDIDATE:
                raise ValueError("cluster skills must remain candidates")
            if self.candidate_skill.execution_mode != ExecutionMode.DRAFT_ONLY:
                raise ValueError("cluster skills must remain draft-only")
        return self


class WorkflowClusteringResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    result_id: str = WORKFLOW_CLUSTERING_ID
    generated_at: datetime
    trace_count: int = Field(ge=0)
    cluster_count: int = Field(ge=0)
    candidate_count: int = Field(ge=0)
    min_traces_for_candidate: int = MIN_SCENES_FOR_SKILL
    clusters: list[WorkflowCluster]
    candidate_only: bool = True
    external_effect_count: int = 0
    policy_refs: tuple[str, ...] = Field(default=(WORKFLOW_CLUSTERING_POLICY_REF,))

    @model_validator(mode="after")
    def enforce_safe_clustering_result(self) -> "WorkflowClusteringResult":
        if WORKFLOW_CLUSTERING_POLICY_REF not in self.policy_refs:
            raise ValueError("workflow clustering result requires policy ref")
        if not self.candidate_only:
            raise ValueError("workflow clustering result must remain candidate-only")
        if self.external_effect_count:
            raise ValueError("workflow clustering cannot include external effects")
        if self.cluster_count != len(self.clusters):
            raise ValueError("workflow clustering cluster_count mismatch")
        if self.candidate_count != sum(1 for cluster in self.clusters if cluster.candidate_skill):
            raise ValueError("workflow clustering candidate_count mismatch")
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


def cluster_workflow_traces(
    traces: list[WorkflowTrace],
    *,
    now: datetime | None = None,
) -> WorkflowClusteringResult:
    grouped: dict[str, list[WorkflowTrace]] = defaultdict(list)
    for trace in traces:
        grouped[_workflow_signature(trace)].append(trace)

    clusters: list[WorkflowCluster] = []
    for signature, group in sorted(grouped.items()):
        candidate = _candidate_from_trace_group(signature, group) if len(group) >= MIN_SCENES_FOR_SKILL else None
        clusters.append(_cluster_from_trace_group(signature, group, candidate))
    return WorkflowClusteringResult(
        generated_at=now or datetime.now(UTC),
        trace_count=len(traces),
        cluster_count=len(clusters),
        candidate_count=sum(1 for cluster in clusters if cluster.candidate_skill),
        clusters=clusters,
    )


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


def _cluster_from_trace_group(
    signature: str,
    traces: list[WorkflowTrace],
    candidate: SkillRecord | None,
) -> WorkflowCluster:
    apps = sorted({app for trace in traces for app in trace.apps})
    action_kinds = sorted({action for trace in traces for action in trace.action_kinds})
    evidence_refs = sorted({ref for trace in traces for ref in trace.evidence_refs})
    label = traces[0].workflow_label
    return WorkflowCluster(
        cluster_id=f"cluster_{_slug(signature)}",
        workflow_label=label,
        signature=signature,
        trace_ids=[trace.trace_id for trace in traces],
        app_count=len(apps),
        action_count=len(action_kinds),
        success_count=sum(int(trace.outcome == "success") for trace in traces),
        evidence_ref_count=len(evidence_refs),
        candidate_skill=candidate,
    )


def _candidate_from_trace_group(signature: str, traces: list[WorkflowTrace]) -> SkillRecord:
    label = traces[0].workflow_label
    apps = sorted({app for trace in traces for app in trace.apps})
    action_sequence = _common_action_prefix([trace.action_kinds for trace in traces])
    learned_from = [trace.trace_id for trace in traces]
    return SkillRecord(
        skill_id=f"skill_workflow_{_slug(signature)}_candidate_v1",
        name=f"{label} workflow",
        description=(
            "Draft-only workflow candidate clustered from repeated local/session traces "
            f"across {', '.join(apps)}."
        ),
        learned_from=learned_from,
        trigger_conditions=[
            f"user starts {label.lower()}",
            f"active apps include {', '.join(apps[:3])}",
        ],
        inputs={
            "goal": "string",
            "active_project": "string",
            "review_scope": "session | project",
        },
        procedure=[_procedure_label(action) for action in action_sequence[:6]],
        success_signals=[
            "clustered traces ended successfully",
            "user accepts draft preview",
            "low correction rate after candidate review",
        ],
        failure_modes=[
            "trace sequence is too sparse",
            "workflow source refs are stale",
            "draft attempts external effects before approval",
        ],
        risk_level=ActionRisk.MEDIUM if any("edit" in action for action in action_sequence) else ActionRisk.LOW,
        maturity_level=2,
        execution_mode=ExecutionMode.DRAFT_ONLY,
        requires_confirmation_before=["promotion", "external_effect", "procedure_change"],
        status=MemoryStatus.CANDIDATE,
    )


def _workflow_signature(trace: WorkflowTrace) -> str:
    apps = ",".join(sorted(app.lower() for app in trace.apps[:4]))
    actions = ">".join(action.lower().replace(" ", "_") for action in trace.action_kinds[:8])
    return f"{_slug(trace.workflow_label)}::{apps}::{actions}"


def _common_action_prefix(sequences: list[list[str]]) -> list[str]:
    if not sequences:
        return []
    prefix: list[str] = []
    for values in zip(*sequences, strict=False):
        normalized = {value.lower().strip() for value in values}
        if len(normalized) != 1:
            break
        prefix.append(values[0])
    return prefix or sequences[0]


def _procedure_label(action: str) -> str:
    label = action.replace("_", " ").strip()
    return f"Draft step: {label}"


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
