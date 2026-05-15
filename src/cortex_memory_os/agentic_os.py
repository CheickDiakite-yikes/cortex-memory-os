"""Agentic OS planner contracts for pointer-first Cortex runs."""

from __future__ import annotations

import argparse
from enum import Enum

from pydantic import Field, model_validator

from cortex_memory_os.contracts import (
    ActionRisk,
    ExecutionMode,
    ScopeLevel,
    SourceTrust,
    StrictModel,
)
from cortex_memory_os.runtime_trace import RuntimeEffect

AGENTIC_OS_PLANNER_ID = "AGENTIC-OS-PLANNER-001"
AGENTIC_OS_POLICY_REF = "policy_agentic_os_planner_v1"

AI_POINTER_PRINCIPLES = [
    "maintain_flow_across_apps",
    "show_and_tell_at_the_pointer",
    "resolve_this_and_that_from_shared_context",
    "turn_pixels_into_actionable_entities",
]

BLOCKED_AGENTIC_EFFECTS = [
    "start_screen_capture",
    "start_microphone_capture",
    "move_system_cursor",
    "execute_click",
    "type_text",
    "send_message",
    "purchase",
    "delete_user_data",
    "write_memory_without_review",
    "store_raw_evidence",
    "export_payload",
]


class AgenticCapability(str, Enum):
    POINTER_CONTEXT = "pointer_context"
    VOICE_INTENT = "voice_intent"
    MEMORY_CONTEXT = "memory_context"
    SKILL_DRAFT = "skill_draft"
    TOOL_ROUTING = "tool_routing"
    APPROVAL_GATE = "approval_gate"
    OUTCOME_TRACE = "outcome_trace"
    MEMORY_PROPOSAL = "memory_proposal"


class AgenticPlanStage(str, Enum):
    UNDERSTAND = "understand"
    CONTEXT = "context"
    PLAN = "plan"
    APPROVE = "approve"
    ACT = "act"
    VERIFY = "verify"
    LEARN = "learn"


class AgenticToolRoute(StrictModel):
    route_id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    capability: AgenticCapability
    gateway_tool: str = Field(min_length=1)
    execution_mode: ExecutionMode
    risk_level: ActionRisk
    allowed_effects: list[RuntimeEffect] = Field(default_factory=list)
    blocked_effects: list[str] = Field(default_factory=list)
    requires_confirmation: bool = False
    external_effect: bool = False
    content_redacted: bool = True
    source_refs_redacted: bool = True

    @model_validator(mode="after")
    def enforce_route_boundary(self) -> AgenticToolRoute:
        if not self.content_redacted or not self.source_refs_redacted:
            raise ValueError("agentic routes must be redacted")
        if self.external_effect and not self.requires_confirmation:
            raise ValueError("external-effect routes require confirmation")
        if self.execution_mode in {
            ExecutionMode.BOUNDED_AUTONOMY,
            ExecutionMode.RECURRING_AUTOMATION,
        }:
            raise ValueError("agentic OS planner starts with draft/assistive routes only")
        if self.risk_level in {ActionRisk.HIGH, ActionRisk.CRITICAL}:
            raise ValueError("high and critical routes are not enabled in the planner spine")
        if self.risk_level == ActionRisk.MEDIUM and not self.requires_confirmation:
            raise ValueError("medium-risk routes require confirmation")
        if "raw://" in self.gateway_tool or "encrypted_blob://" in self.gateway_tool:
            raise ValueError("raw refs cannot become tool routes")
        return self


class AgenticPlanStep(StrictModel):
    step_id: str = Field(min_length=1)
    stage: AgenticPlanStage
    label: str = Field(min_length=1)
    user_visible_prompt: str = Field(min_length=1)
    capability: AgenticCapability
    route_id: str | None = None
    risk_level: ActionRisk = ActionRisk.LOW
    requires_confirmation: bool = False
    status: str = Field(min_length=1)
    safety_note: str = Field(min_length=1)

    @model_validator(mode="after")
    def enforce_step_boundary(self) -> AgenticPlanStep:
        if "ignore previous" in self.label.lower() or "ignore previous" in self.user_visible_prompt.lower():
            raise ValueError("agentic steps cannot echo prompt injection text")
        if self.risk_level in {ActionRisk.HIGH, ActionRisk.CRITICAL}:
            raise ValueError("high and critical steps are blocked in the planner spine")
        if self.risk_level == ActionRisk.MEDIUM and not self.requires_confirmation:
            raise ValueError("medium-risk steps require confirmation")
        return self


class AgenticOSPlan(StrictModel):
    plan_id: str = AGENTIC_OS_PLANNER_ID
    policy_ref: str = AGENTIC_OS_POLICY_REF
    title: str = "Agentic OS Plan"
    goal: str = Field(min_length=1)
    user_phrase: str = Field(min_length=1)
    active_project: str = Field(min_length=1)
    scope_level: ScopeLevel = ScopeLevel.PROJECT_SPECIFIC
    source_trust: SourceTrust = SourceTrust.USER_CONFIRMED
    principles: list[str] = Field(default_factory=lambda: list(AI_POINTER_PRINCIPLES))
    capabilities: list[AgenticCapability] = Field(default_factory=list)
    routes: list[AgenticToolRoute] = Field(default_factory=list)
    steps: list[AgenticPlanStep] = Field(default_factory=list)
    next_best_action: str = Field(min_length=1)
    user_can_interrupt: bool = True
    display_only_pointer: bool = True
    real_screen_capture_started: bool = False
    voice_capture_started: bool = False
    memory_write_allowed: bool = False
    raw_ref_retained: bool = False
    external_effect_enabled: bool = False
    content_redacted: bool = True
    source_refs_redacted: bool = True
    blocked_effects: list[str] = Field(default_factory=lambda: list(BLOCKED_AGENTIC_EFFECTS))

    @model_validator(mode="after")
    def enforce_plan_boundary(self) -> AgenticOSPlan:
        if self.policy_ref != AGENTIC_OS_POLICY_REF:
            raise ValueError("agentic OS plan requires policy ref")
        if set(self.principles) != set(AI_POINTER_PRINCIPLES):
            raise ValueError("agentic OS plan must preserve pointer interaction principles")
        if not self.display_only_pointer:
            raise ValueError("agentic OS pointer starts display-only")
        if self.real_screen_capture_started or self.voice_capture_started:
            raise ValueError("planner smoke cannot start capture or voice")
        if self.memory_write_allowed or self.raw_ref_retained or self.external_effect_enabled:
            raise ValueError("planner smoke cannot write memory, retain raw refs, or act externally")
        if not self.content_redacted or not self.source_refs_redacted:
            raise ValueError("agentic OS plan must be redacted")
        if not self.routes or not self.steps:
            raise ValueError("agentic OS plan requires routes and steps")
        route_ids = {route.route_id for route in self.routes}
        for step in self.steps:
            if step.route_id and step.route_id not in route_ids:
                raise ValueError("agentic step route_id must reference a route")
        for required in BLOCKED_AGENTIC_EFFECTS:
            if required not in self.blocked_effects:
                raise ValueError(f"missing blocked effect: {required}")
        serialized = self.model_dump_json()
        for marker in ("raw://", "encrypted_blob://", "OPENAI_API_KEY", "sk-"):
            if marker in serialized:
                raise ValueError("agentic OS plan cannot contain raw refs or secrets")
        return self


class AgenticOSSmokeResult(StrictModel):
    benchmark_id: str = AGENTIC_OS_PLANNER_ID
    policy_ref: str = AGENTIC_OS_POLICY_REF
    passed: bool
    plan: AgenticOSPlan
    route_count: int = Field(ge=0)
    step_count: int = Field(ge=0)
    confirmation_gate_count: int = Field(ge=0)
    blocked_effect_count: int = Field(ge=0)


def build_agentic_os_plan(
    *,
    goal: str = "Help me understand this and decide the next safe action.",
    user_phrase: str = "What should I do with this?",
    active_project: str = "cortex-memory-os",
) -> AgenticOSPlan:
    routes = [
        AgenticToolRoute(
            route_id="route_pointer_context",
            label="Resolve what this points at",
            capability=AgenticCapability.POINTER_CONTEXT,
            gateway_tool="pointer.resolve_display_context",
            execution_mode=ExecutionMode.DRAFT_ONLY,
            risk_level=ActionRisk.LOW,
            allowed_effects=[RuntimeEffect.LOCAL_READ],
            blocked_effects=["move_system_cursor", "execute_click", "start_screen_capture"],
        ),
        AgenticToolRoute(
            route_id="route_memory_context",
            label="Ask Cortex memory for project context",
            capability=AgenticCapability.MEMORY_CONTEXT,
            gateway_tool="memory.get_context_pack",
            execution_mode=ExecutionMode.DRAFT_ONLY,
            risk_level=ActionRisk.LOW,
            allowed_effects=[RuntimeEffect.LOCAL_READ],
            blocked_effects=["write_memory", "export_payload"],
        ),
        AgenticToolRoute(
            route_id="route_skill_draft",
            label="Draft a skill-backed next step",
            capability=AgenticCapability.SKILL_DRAFT,
            gateway_tool="skill.execute_draft",
            execution_mode=ExecutionMode.DRAFT_ONLY,
            risk_level=ActionRisk.MEDIUM,
            allowed_effects=[RuntimeEffect.LOCAL_READ],
            blocked_effects=["external_action", "data_egress", "execute_click"],
            requires_confirmation=True,
        ),
        AgenticToolRoute(
            route_id="route_runtime_trace",
            label="Record a redacted run trace",
            capability=AgenticCapability.OUTCOME_TRACE,
            gateway_tool="runtime_trace.record",
            execution_mode=ExecutionMode.ASSISTIVE,
            risk_level=ActionRisk.LOW,
            allowed_effects=[RuntimeEffect.LOCAL_WRITE],
            blocked_effects=["raw_payload", "secret_echo"],
        ),
        AgenticToolRoute(
            route_id="route_memory_proposal",
            label="Propose a memory only after review",
            capability=AgenticCapability.MEMORY_PROPOSAL,
            gateway_tool="memory.propose",
            execution_mode=ExecutionMode.DRAFT_ONLY,
            risk_level=ActionRisk.MEDIUM,
            allowed_effects=[RuntimeEffect.LOCAL_READ],
            blocked_effects=["write_memory_without_review", "autonomous_trigger"],
            requires_confirmation=True,
        ),
    ]
    steps = [
        AgenticPlanStep(
            step_id="step_understand_pointer",
            stage=AgenticPlanStage.UNDERSTAND,
            label="Understand this",
            user_visible_prompt="I will look at the selected target and explain what it seems to be.",
            capability=AgenticCapability.POINTER_CONTEXT,
            route_id="route_pointer_context",
            status="ready",
            safety_note="Display-only pointer context; no click, typing, or capture starts.",
        ),
        AgenticPlanStep(
            step_id="step_fetch_memory",
            stage=AgenticPlanStage.CONTEXT,
            label="Get the right memory",
            user_visible_prompt="I will pull only project-scoped helper context.",
            capability=AgenticCapability.MEMORY_CONTEXT,
            route_id="route_memory_context",
            status="ready",
            safety_note="Read-only context pack; no memory mutation.",
        ),
        AgenticPlanStep(
            step_id="step_choose_tool",
            stage=AgenticPlanStage.PLAN,
            label="Choose the safest tool lane",
            user_visible_prompt="I will prefer direct APIs, then scripts, then guided display-only UI.",
            capability=AgenticCapability.TOOL_ROUTING,
            status="ready",
            safety_note="The planner does not execute tools by itself.",
        ),
        AgenticPlanStep(
            step_id="step_review_draft",
            stage=AgenticPlanStage.APPROVE,
            label="Ask before doing anything with effects",
            user_visible_prompt="I will show the draft action before anything can affect files or apps.",
            capability=AgenticCapability.APPROVAL_GATE,
            route_id="route_skill_draft",
            risk_level=ActionRisk.MEDIUM,
            requires_confirmation=True,
            status="needs_review",
            safety_note="Medium-risk draft route is gated by confirmation.",
        ),
        AgenticPlanStep(
            step_id="step_record_outcome",
            stage=AgenticPlanStage.VERIFY,
            label="Check the outcome",
            user_visible_prompt="I will record whether the result worked using a redacted trace.",
            capability=AgenticCapability.OUTCOME_TRACE,
            route_id="route_runtime_trace",
            status="ready",
            safety_note="Trace metadata is redacted and content-free by default.",
        ),
        AgenticPlanStep(
            step_id="step_propose_memory",
            stage=AgenticPlanStage.LEARN,
            label="Offer a memory, do not silently save it",
            user_visible_prompt="I can suggest a memory, and you decide whether it belongs in the Memory Book.",
            capability=AgenticCapability.MEMORY_PROPOSAL,
            route_id="route_memory_proposal",
            risk_level=ActionRisk.MEDIUM,
            requires_confirmation=True,
            status="needs_review",
            safety_note="Learning is proposal-only until the user confirms.",
        ),
    ]
    return AgenticOSPlan(
        goal=goal,
        user_phrase=user_phrase,
        active_project=active_project,
        capabilities=list(AgenticCapability),
        routes=routes,
        steps=steps,
        next_best_action="Run the pointer-first plan in controlled demo mode, then promote only reviewed routes.",
    )


def run_agentic_os_smoke() -> AgenticOSSmokeResult:
    plan = build_agentic_os_plan()
    confirmation_gate_count = sum(1 for step in plan.steps if step.requires_confirmation)
    return AgenticOSSmokeResult(
        passed=True,
        plan=plan,
        route_count=len(plan.routes),
        step_count=len(plan.steps),
        confirmation_gate_count=confirmation_gate_count,
        blocked_effect_count=len(plan.blocked_effects),
    )


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    result = run_agentic_os_smoke()
    if args.json:
        print(result.model_dump_json(indent=2))
    else:
        print(
            f"{result.benchmark_id}: passed={result.passed} "
            f"routes={result.route_count} steps={result.step_count}"
        )
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
