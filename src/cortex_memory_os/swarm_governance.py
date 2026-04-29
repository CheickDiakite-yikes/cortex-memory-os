"""Swarm orchestration governance contracts."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum

from pydantic import Field, model_validator

from cortex_memory_os.contracts import (
    ActionRisk,
    ExecutionMode,
    SourceTrust,
    StrictModel,
)


SWARM_GOVERNANCE_POLICY_REF = "policy_swarm_governance_v1"


class SwarmTaskRole(str, Enum):
    COORDINATOR = "coordinator"
    WORKER = "worker"
    REVIEWER = "reviewer"
    OBSERVER = "observer"


class SwarmTaskBudget(StrictModel):
    max_prompt_tokens: int = Field(default=1200, ge=1, le=200_000)
    max_tool_calls: int = Field(default=3, ge=0, le=100)
    max_wall_clock_ms: int = Field(default=300_000, ge=1, le=86_400_000)
    max_artifacts: int = Field(default=1, ge=0, le=100)
    max_action_risk: ActionRisk = ActionRisk.LOW
    autonomy_ceiling: ExecutionMode = ExecutionMode.DRAFT_ONLY

    @model_validator(mode="after")
    def enforce_swarm_budget_safety(self) -> SwarmTaskBudget:
        if self.max_action_risk in {ActionRisk.HIGH, ActionRisk.CRITICAL}:
            raise ValueError("swarm tasks cannot request high or critical risk budgets")
        if self.autonomy_ceiling in {
            ExecutionMode.BOUNDED_AUTONOMY,
            ExecutionMode.RECURRING_AUTOMATION,
        }:
            raise ValueError("swarm tasks cannot request autonomous execution")
        return self


class SwarmTaskSpec(StrictModel):
    task_id: str = Field(min_length=1)
    agent_id: str = Field(min_length=1)
    role: SwarmTaskRole
    goal: str = Field(min_length=1, max_length=280)
    source_trust: SourceTrust = SourceTrust.AGENT_INFERRED
    allowed_source_refs: list[str] = Field(min_length=1)
    blocked_source_refs: list[str] = Field(default_factory=list)
    read_scope_refs: list[str] = Field(default_factory=list)
    write_scope_refs: list[str] = Field(default_factory=list)
    depends_on: list[str] = Field(default_factory=list)
    budget: SwarmTaskBudget = Field(default_factory=SwarmTaskBudget)
    cancellation_token: str = Field(min_length=1)
    source_isolation_required: bool = True
    content_redacted: bool = True
    policy_refs: tuple[str, ...] = Field(
        default_factory=lambda: (SWARM_GOVERNANCE_POLICY_REF,),
        min_length=1,
    )

    @model_validator(mode="after")
    def enforce_task_isolation(self) -> SwarmTaskSpec:
        if not self.source_isolation_required:
            raise ValueError("swarm tasks require source isolation")
        if SWARM_GOVERNANCE_POLICY_REF not in self.policy_refs:
            raise ValueError("swarm tasks require governance policy reference")
        if any(ref in {"*", "all", "global"} for ref in self.allowed_source_refs):
            raise ValueError("swarm tasks require explicit source refs")
        if set(self.allowed_source_refs) & set(self.blocked_source_refs):
            raise ValueError("allowed and blocked source refs cannot overlap")
        if self.role in {SwarmTaskRole.REVIEWER, SwarmTaskRole.OBSERVER}:
            if self.write_scope_refs:
                raise ValueError("reviewer and observer swarm tasks cannot write")
        lowered_goal = self.goal.lower()
        if "ignore previous" in lowered_goal or "reveal secrets" in lowered_goal:
            raise ValueError("swarm task goals cannot carry prompt-injection text")
        if self.source_trust in {
            SourceTrust.EXTERNAL_UNTRUSTED,
            SourceTrust.HOSTILE_UNTIL_SAFE,
        } and not self.content_redacted:
            raise ValueError("external or hostile swarm task content must be redacted")
        return self


class SwarmPlan(StrictModel):
    plan_id: str = Field(min_length=1)
    coordinator_agent_id: str = Field(min_length=1)
    tasks: list[SwarmTaskSpec] = Field(min_length=1)
    shared_context_refs: list[str] = Field(default_factory=list)
    max_total_prompt_tokens: int = Field(default=6000, ge=1, le=500_000)
    max_total_tool_calls: int = Field(default=20, ge=0, le=1000)
    max_total_wall_clock_ms: int = Field(default=1_800_000, ge=1, le=86_400_000)
    cancellation_token: str = Field(min_length=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    policy_refs: tuple[str, ...] = Field(
        default_factory=lambda: (SWARM_GOVERNANCE_POLICY_REF,),
        min_length=1,
    )

    @model_validator(mode="after")
    def enforce_plan_invariants(self) -> SwarmPlan:
        if SWARM_GOVERNANCE_POLICY_REF not in self.policy_refs:
            raise ValueError("swarm plans require governance policy reference")

        task_ids = [task.task_id for task in self.tasks]
        if len(task_ids) != len(set(task_ids)):
            raise ValueError("swarm task IDs must be unique")
        task_id_set = set(task_ids)
        for task in self.tasks:
            if task.cancellation_token != self.cancellation_token:
                raise ValueError("swarm task cancellation token must match plan token")
            missing_dependencies = set(task.depends_on) - task_id_set
            if missing_dependencies:
                raise ValueError("swarm task dependencies must reference plan tasks")

        write_owner_by_ref: dict[str, str] = {}
        for task in self.tasks:
            for write_ref in task.write_scope_refs:
                owner = write_owner_by_ref.get(write_ref)
                if owner and owner != task.task_id:
                    raise ValueError("swarm write scopes must be disjoint")
                write_owner_by_ref[write_ref] = task.task_id
        return self


class SwarmGovernanceDecision(StrictModel):
    decision_id: str = Field(min_length=1)
    plan_id: str = Field(min_length=1)
    allowed: bool
    reason: str = Field(min_length=1)
    allowed_task_ids: list[str] = Field(default_factory=list)
    blocked_task_ids: list[str] = Field(default_factory=list)
    total_prompt_tokens: int = Field(ge=0)
    total_tool_calls: int = Field(ge=0)
    total_wall_clock_ms: int = Field(ge=0)
    source_isolation_required: bool
    cancellation_token: str = Field(min_length=1)
    audit_required: bool = True
    audit_action: str = "swarm_plan_governance"
    policy_refs: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def enforce_decision_shape(self) -> SwarmGovernanceDecision:
        if SWARM_GOVERNANCE_POLICY_REF not in self.policy_refs:
            raise ValueError("swarm decisions require governance policy reference")
        if self.allowed and self.blocked_task_ids:
            raise ValueError("allowed swarm decisions cannot include blocked tasks")
        if self.allowed and not self.allowed_task_ids:
            raise ValueError("allowed swarm decisions require task IDs")
        if not self.source_isolation_required:
            raise ValueError("swarm decisions require source isolation")
        return self


class SwarmSourceAccessDecision(StrictModel):
    task_id: str = Field(min_length=1)
    source_ref: str = Field(min_length=1)
    allowed: bool
    reason: str = Field(min_length=1)
    content_redacted: bool = True
    policy_refs: tuple[str, ...] = Field(
        default_factory=lambda: (SWARM_GOVERNANCE_POLICY_REF,),
        min_length=1,
    )


class SwarmCancellationReceipt(StrictModel):
    receipt_id: str = Field(min_length=1)
    plan_id: str = Field(min_length=1)
    cancellation_token: str = Field(min_length=1)
    requested_by: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    cancelled_task_ids: list[str] = Field(min_length=1)
    preserved_audit_refs: list[str] = Field(default_factory=list)
    external_effects_allowed_after_cancel: bool = False
    audit_required: bool = True
    audit_action: str = "swarm_cancel"
    policy_refs: tuple[str, ...] = Field(
        default_factory=lambda: (SWARM_GOVERNANCE_POLICY_REF,),
        min_length=1,
    )


def evaluate_swarm_plan(plan: SwarmPlan) -> SwarmGovernanceDecision:
    total_prompt_tokens = sum(task.budget.max_prompt_tokens for task in plan.tasks)
    total_tool_calls = sum(task.budget.max_tool_calls for task in plan.tasks)
    total_wall_clock_ms = sum(task.budget.max_wall_clock_ms for task in plan.tasks)
    blocked_reasons: list[str] = []
    if total_prompt_tokens > plan.max_total_prompt_tokens:
        blocked_reasons.append("prompt_budget_exceeded")
    if total_tool_calls > plan.max_total_tool_calls:
        blocked_reasons.append("tool_budget_exceeded")
    if total_wall_clock_ms > plan.max_total_wall_clock_ms:
        blocked_reasons.append("time_budget_exceeded")

    allowed = not blocked_reasons
    return SwarmGovernanceDecision(
        decision_id=f"swarm_decision_{plan.plan_id}",
        plan_id=plan.plan_id,
        allowed=allowed,
        reason="allowed" if allowed else ",".join(blocked_reasons),
        allowed_task_ids=[task.task_id for task in plan.tasks] if allowed else [],
        blocked_task_ids=[] if allowed else [task.task_id for task in plan.tasks],
        total_prompt_tokens=total_prompt_tokens,
        total_tool_calls=total_tool_calls,
        total_wall_clock_ms=total_wall_clock_ms,
        source_isolation_required=all(task.source_isolation_required for task in plan.tasks),
        cancellation_token=plan.cancellation_token,
        policy_refs=(SWARM_GOVERNANCE_POLICY_REF,),
    )


def evaluate_swarm_source_access(
    task: SwarmTaskSpec,
    source_ref: str,
) -> SwarmSourceAccessDecision:
    if source_ref in task.blocked_source_refs:
        return SwarmSourceAccessDecision(
            task_id=task.task_id,
            source_ref=source_ref,
            allowed=False,
            reason="source_explicitly_blocked",
        )
    if source_ref not in task.allowed_source_refs:
        return SwarmSourceAccessDecision(
            task_id=task.task_id,
            source_ref=source_ref,
            allowed=False,
            reason="source_outside_task_isolation",
        )
    return SwarmSourceAccessDecision(
        task_id=task.task_id,
        source_ref=source_ref,
        allowed=True,
        reason="source_in_task_scope",
    )


def cancel_swarm_plan(
    plan: SwarmPlan,
    *,
    requested_by: str,
    reason: str,
) -> SwarmCancellationReceipt:
    return SwarmCancellationReceipt(
        receipt_id=f"swarm_cancel_{plan.plan_id}",
        plan_id=plan.plan_id,
        cancellation_token=plan.cancellation_token,
        requested_by=requested_by,
        reason=reason,
        cancelled_task_ids=[task.task_id for task in plan.tasks],
        preserved_audit_refs=[f"audit:{task.task_id}" for task in plan.tasks],
    )
