import pytest
from pydantic import ValidationError

from cortex_memory_os.contracts import ActionRisk, ExecutionMode, SourceTrust
from cortex_memory_os.swarm_governance import (
    SWARM_GOVERNANCE_POLICY_REF,
    SwarmPlan,
    SwarmTaskBudget,
    SwarmTaskRole,
    SwarmTaskSpec,
    cancel_swarm_plan,
    evaluate_swarm_plan,
    evaluate_swarm_source_access,
)


def _task(task_id: str, **updates) -> SwarmTaskSpec:
    payload = {
        "task_id": task_id,
        "agent_id": f"agent_{task_id}",
        "role": SwarmTaskRole.WORKER,
        "goal": "Inspect scoped source refs and draft a result.",
        "source_trust": SourceTrust.LOCAL_OBSERVED,
        "allowed_source_refs": [f"source:{task_id}"],
        "blocked_source_refs": ["external:hostile_page"],
        "read_scope_refs": [f"repo:{task_id}:read"],
        "write_scope_refs": [f"repo:{task_id}:write"],
        "cancellation_token": "cancel_swarm_001",
    }
    payload.update(updates)
    return SwarmTaskSpec(**payload)


def _plan(*tasks: SwarmTaskSpec, **updates) -> SwarmPlan:
    payload = {
        "plan_id": "swarm_plan_001",
        "coordinator_agent_id": "agent_coord",
        "tasks": list(tasks),
        "shared_context_refs": ["ctx:swarm_brief"],
        "cancellation_token": "cancel_swarm_001",
    }
    payload.update(updates)
    return SwarmPlan(**payload)


def test_swarm_plan_allows_disjoint_budgeted_source_isolated_tasks():
    first = _task("one")
    second = _task("two", depends_on=["one"])
    plan = _plan(first, second)

    decision = evaluate_swarm_plan(plan)
    access = evaluate_swarm_source_access(first, "source:one")
    blocked = evaluate_swarm_source_access(first, "source:two")
    cancellation = cancel_swarm_plan(
        plan,
        requested_by="user",
        reason="user paused swarm work",
    )

    assert decision.allowed is True
    assert decision.allowed_task_ids == ["one", "two"]
    assert decision.source_isolation_required is True
    assert decision.audit_required is True
    assert SWARM_GOVERNANCE_POLICY_REF in decision.policy_refs
    assert access.allowed is True
    assert blocked.allowed is False
    assert blocked.reason == "source_outside_task_isolation"
    assert cancellation.cancelled_task_ids == ["one", "two"]
    assert cancellation.external_effects_allowed_after_cancel is False
    assert len(cancellation.preserved_audit_refs) == 2


def test_swarm_governance_denies_aggregate_budget_overflow():
    task = _task(
        "wide",
        budget=SwarmTaskBudget(max_prompt_tokens=3000, max_tool_calls=7),
    )
    plan = _plan(
        task,
        max_total_prompt_tokens=2000,
        max_total_tool_calls=4,
    )

    decision = evaluate_swarm_plan(plan)

    assert decision.allowed is False
    assert decision.blocked_task_ids == ["wide"]
    assert "prompt_budget_exceeded" in decision.reason
    assert "tool_budget_exceeded" in decision.reason


def test_swarm_plan_rejects_overlapping_write_scopes():
    first = _task("one", write_scope_refs=["repo:shared:file"])
    second = _task("two", write_scope_refs=["repo:shared:file"])

    with pytest.raises(ValidationError, match="write scopes"):
        _plan(first, second)


def test_swarm_task_rejects_unscoped_or_autonomous_work():
    with pytest.raises(ValidationError, match="explicit source refs"):
        _task("wildcard", allowed_source_refs=["*"])

    with pytest.raises(ValidationError, match="autonomous execution"):
        SwarmTaskBudget(autonomy_ceiling=ExecutionMode.BOUNDED_AUTONOMY)

    with pytest.raises(ValidationError, match="high or critical risk"):
        SwarmTaskBudget(max_action_risk=ActionRisk.HIGH)


def test_reviewer_and_observer_tasks_cannot_write():
    with pytest.raises(ValidationError, match="cannot write"):
        _task("review", role=SwarmTaskRole.REVIEWER, write_scope_refs=["repo:x"])

    with pytest.raises(ValidationError, match="cannot write"):
        _task("observe", role=SwarmTaskRole.OBSERVER, write_scope_refs=["repo:x"])
