"""Agentic OS planner contracts for pointer-first Cortex runs."""

from __future__ import annotations

import argparse
from enum import Enum
from typing import Any, Literal

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
AGENTIC_TURN_ROUTER_ID = "AGENTIC-TURN-ROUTER-001"
AGENTIC_OS_POLICY_REF = "policy_agentic_os_planner_v1"
AGENTIC_TURN_POLICY_REF = "policy_agentic_turn_router_v1"

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

_PROHIBITED_MARKERS = (
    "OPENAI_API_KEY",
    "CORTEX_FAKE_TOKEN",
    "sk-",
    "raw://",
    "encrypted_blob://",
    "Ignore previous instructions",
    "BEGIN " + "PRIVATE KEY",
)


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


class AgenticRouteKind(str, Enum):
    ANSWER_ONLY = "answer_only"
    DRAFT_ONLY = "draft_only"
    ASSISTIVE_WITH_APPROVAL = "assistive_with_approval"
    BLOCKED = "blocked"


class PointerIntentEvent(StrictModel):
    event_id: str = Field(min_length=1)
    user_phrase: str = Field(min_length=1, max_length=240)
    target_id: str = Field(min_length=1, max_length=120)
    target_label: str = Field(min_length=1, max_length=120)
    target_role: str = Field(default="controlled_ui_target", min_length=1, max_length=80)
    app_surface: str = Field(default="controlled_demo_surface", min_length=1, max_length=120)
    screen_state_ref: str = Field(default="controlled_dom://agentic-turn", pattern=r"^controlled_dom://")
    pointer_referent: Literal["this", "that", "these", "none"] = "this"
    referenced_target_ids: list[str] = Field(default_factory=list, min_length=1, max_length=4)
    pointer_x: float = Field(ge=0)
    pointer_y: float = Field(ge=0)
    viewport_width: int = Field(default=1440, ge=320, le=3840)
    viewport_height: int = Field(default=960, ge=320, le=2160)
    source_trust: SourceTrust = SourceTrust.LOCAL_OBSERVED
    confidence: float = Field(ge=0, le=1)
    display_only: bool = True
    real_screen_capture_started: bool = False
    voice_capture_started: bool = False
    raw_ref_retained: bool = False
    external_content_loaded: bool = False
    policy_refs: list[str] = Field(
        default_factory=lambda: [AGENTIC_TURN_POLICY_REF, AGENTIC_OS_POLICY_REF]
    )

    @model_validator(mode="after")
    def enforce_pointer_intent_boundary(self) -> "PointerIntentEvent":
        if not self.display_only:
            raise ValueError("pointer intent must remain display-only")
        if self.pointer_x > self.viewport_width or self.pointer_y > self.viewport_height:
            raise ValueError("pointer intent coordinates exceed viewport")
        if self.target_id not in self.referenced_target_ids:
            raise ValueError("pointer intent must reference its primary target")
        if (
            self.real_screen_capture_started
            or self.voice_capture_started
            or self.raw_ref_retained
            or self.external_content_loaded
        ):
            raise ValueError("pointer intent cannot start capture, retain raw refs, or load external content")
        if self.source_trust in {
            SourceTrust.EXTERNAL_UNTRUSTED,
            SourceTrust.HOSTILE_UNTIL_SAFE,
        } and self.confidence > 0.7:
            raise ValueError("untrusted pointer intent confidence is capped before review")
        if AGENTIC_TURN_POLICY_REF not in self.policy_refs:
            raise ValueError("pointer intent requires agentic turn policy ref")
        serialized = self.model_dump_json()
        if any(marker in serialized for marker in _PROHIBITED_MARKERS):
            raise ValueError("pointer intent cannot contain secret/raw/prompt-injection markers")
        return self


class AgenticRouteDecision(StrictModel):
    decision_id: str = Field(min_length=1)
    route_kind: AgenticRouteKind
    selected_route_id: str | None = None
    gateway_tool: str = Field(min_length=1)
    user_visible_label: str = Field(min_length=1, max_length=120)
    user_visible_rationale: str = Field(min_length=1, max_length=220)
    execution_mode: ExecutionMode
    risk_level: ActionRisk
    allowed_effects: list[RuntimeEffect] = Field(default_factory=list)
    blocked_effects: list[str] = Field(default_factory=list)
    requires_confirmation: bool = False
    approval_reason: str | None = Field(default=None, max_length=180)
    memory_proposal_allowed: bool = False
    durable_memory_write_allowed: bool = False
    real_cursor_movement_allowed: bool = False
    external_effect_allowed: bool = False
    raw_ref_allowed: bool = False
    content_redacted: bool = True
    source_refs_redacted: bool = True
    policy_refs: list[str] = Field(
        default_factory=lambda: [AGENTIC_TURN_POLICY_REF, AGENTIC_OS_POLICY_REF]
    )

    @model_validator(mode="after")
    def enforce_route_decision_boundary(self) -> "AgenticRouteDecision":
        if not self.content_redacted or not self.source_refs_redacted:
            raise ValueError("agentic route decisions must stay redacted")
        if self.durable_memory_write_allowed or self.real_cursor_movement_allowed:
            raise ValueError("agentic route decisions cannot enable memory writes or cursor movement")
        if self.raw_ref_allowed or self.external_effect_allowed:
            raise ValueError("agentic route decisions cannot allow raw refs or external effects")
        if self.route_kind == AgenticRouteKind.BLOCKED:
            if self.execution_mode != ExecutionMode.DRAFT_ONLY:
                raise ValueError("blocked route decisions must stay draft-only")
            if not self.requires_confirmation:
                raise ValueError("blocked route decisions require review")
        if self.route_kind == AgenticRouteKind.ANSWER_ONLY and self.risk_level != ActionRisk.LOW:
            raise ValueError("answer-only route decisions must be low risk")
        if self.route_kind in {
            AgenticRouteKind.DRAFT_ONLY,
            AgenticRouteKind.ASSISTIVE_WITH_APPROVAL,
        } and self.risk_level == ActionRisk.MEDIUM and not self.requires_confirmation:
            raise ValueError("medium-risk route decisions require confirmation")
        if self.route_kind == AgenticRouteKind.ASSISTIVE_WITH_APPROVAL:
            if not self.requires_confirmation or self.execution_mode != ExecutionMode.ASSISTIVE:
                raise ValueError("assistive routes require confirmation and assistive mode")
        if self.risk_level in {ActionRisk.HIGH, ActionRisk.CRITICAL} and self.route_kind != AgenticRouteKind.BLOCKED:
            raise ValueError("high and critical route decisions must be blocked")
        if missing := sorted(set(BLOCKED_AGENTIC_EFFECTS).difference(self.blocked_effects)):
            raise ValueError(f"agentic route decision missing blocked effects: {missing}")
        if AGENTIC_TURN_POLICY_REF not in self.policy_refs:
            raise ValueError("agentic route decision requires turn policy ref")
        serialized = self.model_dump_json()
        if any(marker in serialized for marker in _PROHIBITED_MARKERS):
            raise ValueError("agentic route decision cannot contain secret/raw/prompt-injection markers")
        return self


class AgenticApprovalRequest(StrictModel):
    approval_id: str = Field(min_length=1)
    decision_id: str = Field(min_length=1)
    reason: str = Field(min_length=1, max_length=180)
    required_before_effects: bool = True
    user_can_reject: bool = True
    approved: bool = False
    policy_refs: list[str] = Field(default_factory=lambda: [AGENTIC_TURN_POLICY_REF])

    @model_validator(mode="after")
    def keep_approval_explicit(self) -> "AgenticApprovalRequest":
        if not self.required_before_effects or not self.user_can_reject:
            raise ValueError("agentic approval must be explicit and rejectable")
        if self.approved:
            raise ValueError("agentic turn smoke cannot pre-approve an action")
        if AGENTIC_TURN_POLICY_REF not in self.policy_refs:
            raise ValueError("agentic approval requires turn policy ref")
        return self


class AgenticRunReceipt(StrictModel):
    receipt_id: str = Field(min_length=1)
    turn_id: str = Field(min_length=1)
    target_label: str = Field(min_length=1)
    route_kind: AgenticRouteKind
    gateway_tool: str = Field(min_length=1)
    confidence: float = Field(ge=0, le=1)
    approval_required: bool
    memory_proposal_created: bool = False
    durable_memory_write_performed: bool = False
    runtime_trace_recorded: bool = True
    raw_payload_included: bool = False
    contains_user_phrase: bool = False
    contains_assistant_response: bool = False
    display_only_pointer: bool = True
    blocked_effects: list[str] = Field(default_factory=list)
    user_visible_summary: str = Field(min_length=1, max_length=260)
    policy_refs: list[str] = Field(default_factory=lambda: [AGENTIC_TURN_POLICY_REF])

    @model_validator(mode="after")
    def keep_receipt_redacted(self) -> "AgenticRunReceipt":
        if not self.display_only_pointer:
            raise ValueError("agentic run receipt must keep the pointer display-only")
        if self.durable_memory_write_performed:
            raise ValueError("agentic run receipt cannot include durable memory writes")
        if self.raw_payload_included or self.contains_user_phrase or self.contains_assistant_response:
            raise ValueError("agentic run receipt must stay redacted")
        if missing := sorted(set(BLOCKED_AGENTIC_EFFECTS).difference(self.blocked_effects)):
            raise ValueError(f"agentic run receipt missing blocked effects: {missing}")
        if AGENTIC_TURN_POLICY_REF not in self.policy_refs:
            raise ValueError("agentic run receipt requires turn policy ref")
        serialized = self.model_dump_json()
        if any(marker in serialized for marker in _PROHIBITED_MARKERS):
            raise ValueError("agentic run receipt cannot contain secret/raw/prompt-injection markers")
        return self


class AgenticTurn(StrictModel):
    turn_id: str = Field(min_length=1)
    goal: str = Field(min_length=1, max_length=220)
    pointer_event: PointerIntentEvent
    plan: AgenticOSPlan
    route_decision: AgenticRouteDecision
    approval_request: AgenticApprovalRequest | None = None
    receipt: AgenticRunReceipt
    pointer_card_title: str = Field(min_length=1, max_length=80)
    pointer_card_body: str = Field(min_length=1, max_length=220)
    pointer_card_primary_action: str = Field(min_length=1, max_length=80)
    context_pack_requested: bool = True
    runtime_trace_recorded: bool = True
    memory_proposal_review_required: bool = False
    display_only_pointer: bool = True
    policy_refs: list[str] = Field(
        default_factory=lambda: [AGENTIC_TURN_POLICY_REF, AGENTIC_OS_POLICY_REF]
    )

    @model_validator(mode="after")
    def enforce_turn_boundary(self) -> "AgenticTurn":
        if not self.display_only_pointer:
            raise ValueError("agentic turn pointer must remain display-only")
        if self.route_decision.requires_confirmation and self.approval_request is None:
            raise ValueError("confirmation routes require an approval request")
        if self.approval_request and self.approval_request.decision_id != self.route_decision.decision_id:
            raise ValueError("approval request must match route decision")
        if self.receipt.turn_id != self.turn_id:
            raise ValueError("agentic receipt must reference the turn")
        if self.receipt.route_kind != self.route_decision.route_kind:
            raise ValueError("agentic receipt route kind must match decision")
        if self.memory_proposal_review_required and not self.route_decision.memory_proposal_allowed:
            raise ValueError("memory proposal review requires a memory proposal route")
        if AGENTIC_TURN_POLICY_REF not in self.policy_refs:
            raise ValueError("agentic turn requires turn policy ref")
        serialized = self.model_dump_json()
        if any(marker in serialized for marker in _PROHIBITED_MARKERS):
            raise ValueError("agentic turn cannot contain secret/raw/prompt-injection markers")
        return self


class AgenticTurnSmokeResult(StrictModel):
    benchmark_id: str = AGENTIC_TURN_ROUTER_ID
    policy_ref: str = AGENTIC_TURN_POLICY_REF
    passed: bool
    turn: AgenticTurn
    route_kind: AgenticRouteKind
    approval_required: bool
    blocked_effect_count: int = Field(ge=0)


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


class AgenticOSDashboardPanel(StrictModel):
    panel_id: str = AGENTIC_OS_PLANNER_ID
    policy_ref: str = AGENTIC_OS_POLICY_REF
    title: str = "Agentic OS Kernel"
    summary: str = Field(min_length=1)
    route_count: int = Field(ge=0)
    step_count: int = Field(ge=0)
    confirmation_gate_count: int = Field(ge=0)
    next_best_action: str = Field(min_length=1)
    principles: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    ready_routes: list[str] = Field(default_factory=list)
    review_steps: list[str] = Field(default_factory=list)
    latest_turn_target_label: str = Field(default="Color Page", min_length=1)
    latest_turn_route_kind: AgenticRouteKind = AgenticRouteKind.DRAFT_ONLY
    latest_turn_gateway_tool: str = Field(default="skill.execute_draft", min_length=1)
    latest_turn_confidence: float = Field(default=0.88, ge=0, le=1)
    latest_turn_approval_required: bool = True
    latest_turn_memory_proposal_created: bool = False
    pointer_card_title: str = Field(default="Draft the next steps", min_length=1)
    pointer_card_body: str = Field(
        default="I see Color Page. I can draft the next safe steps.",
        min_length=1,
    )
    pointer_card_primary_action: str = Field(default="Show steps", min_length=1)
    smoke_command: str = "uv run cortex-agentic-os --smoke --json"
    turn_smoke_command: str = "uv run cortex-agentic-os --turn-smoke --json"
    display_only_pointer: bool = True
    memory_write_allowed: bool = False
    external_effect_enabled: bool = False
    raw_ref_retained: bool = False
    blocked_effects: list[str] = Field(default_factory=list)
    content_redacted: bool = True
    source_refs_redacted: bool = True

    @model_validator(mode="after")
    def enforce_dashboard_boundary(self) -> AgenticOSDashboardPanel:
        if not self.display_only_pointer:
            raise ValueError("agentic dashboard panel requires display-only pointer")
        if self.latest_turn_route_kind in {
            AgenticRouteKind.DRAFT_ONLY,
            AgenticRouteKind.ASSISTIVE_WITH_APPROVAL,
            AgenticRouteKind.BLOCKED,
        } and not self.latest_turn_approval_required:
            raise ValueError("reviewable agentic dashboard turns require approval state")
        if self.memory_write_allowed or self.external_effect_enabled or self.raw_ref_retained:
            raise ValueError("agentic dashboard panel cannot enable writes/effects/raw refs")
        if not self.content_redacted or not self.source_refs_redacted:
            raise ValueError("agentic dashboard panel must stay redacted")
        for required in ("execute_click", "write_memory_without_review", "store_raw_evidence"):
            if required not in self.blocked_effects:
                raise ValueError(f"agentic dashboard panel missing blocked effect {required}")
        return self


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


def build_agentic_os_dashboard_panel(
    plan: AgenticOSPlan | None = None,
    turn: AgenticTurn | None = None,
) -> AgenticOSDashboardPanel:
    plan = plan or build_agentic_os_plan()
    turn = turn or build_agentic_turn(
        pointer_event=build_pointer_intent_event(user_phrase="What should I click next?")
    )
    return AgenticOSDashboardPanel(
        summary="Goal -> pointer context -> memory context -> tool route -> approval -> outcome -> reviewed learning.",
        route_count=len(plan.routes),
        step_count=len(plan.steps),
        confirmation_gate_count=sum(1 for step in plan.steps if step.requires_confirmation),
        next_best_action=plan.next_best_action,
        principles=plan.principles,
        capabilities=[capability.value for capability in plan.capabilities],
        ready_routes=[route.gateway_tool for route in plan.routes[:4]],
        review_steps=[step.label for step in plan.steps if step.requires_confirmation],
        latest_turn_target_label=turn.receipt.target_label,
        latest_turn_route_kind=turn.route_decision.route_kind,
        latest_turn_gateway_tool=turn.route_decision.gateway_tool,
        latest_turn_confidence=turn.pointer_event.confidence,
        latest_turn_approval_required=turn.route_decision.requires_confirmation,
        latest_turn_memory_proposal_created=turn.receipt.memory_proposal_created,
        pointer_card_title=turn.pointer_card_title,
        pointer_card_body=turn.pointer_card_body,
        pointer_card_primary_action=turn.pointer_card_primary_action,
        display_only_pointer=plan.display_only_pointer,
        memory_write_allowed=plan.memory_write_allowed,
        external_effect_enabled=plan.external_effect_enabled,
        raw_ref_retained=plan.raw_ref_retained,
        blocked_effects=plan.blocked_effects,
    )


def build_pointer_intent_event(
    *,
    user_phrase: str = "What should I do with this?",
    target_id: str = "color_page_button",
    target_label: str = "Color Page",
    target_role: str = "navigation_button",
    app_surface: str = "Cortex Resolve Studio",
    screen_state_ref: str = "controlled_dom://safe_creative_tool_demo_surface_v1",
    pointer_referent: Literal["this", "that", "these", "none"] = "this",
    referenced_target_ids: list[str] | None = None,
    pointer_x: float = 1260,
    pointer_y: float = 884,
    confidence: float = 0.86,
    source_trust: SourceTrust = SourceTrust.LOCAL_OBSERVED,
) -> PointerIntentEvent:
    return PointerIntentEvent(
        event_id="pointer_intent_001",
        user_phrase=user_phrase,
        target_id=target_id,
        target_label=target_label,
        target_role=target_role,
        app_surface=app_surface,
        screen_state_ref=screen_state_ref,
        pointer_referent=pointer_referent,
        referenced_target_ids=referenced_target_ids or [target_id],
        pointer_x=pointer_x,
        pointer_y=pointer_y,
        source_trust=source_trust,
        confidence=confidence,
    )


def resolve_agentic_route(
    pointer_event: PointerIntentEvent,
    *,
    plan: AgenticOSPlan | None = None,
) -> AgenticRouteDecision:
    plan = plan or build_agentic_os_plan(user_phrase=pointer_event.user_phrase)
    phrase = pointer_event.user_phrase.lower()
    blocked_requested = any(
        marker in phrase
        for marker in (
            "click it",
            "click this",
            "type ",
            "send ",
            "delete ",
            "purchase",
            "export",
            "record screen",
            "start screen",
            "microphone",
            "move my cursor",
            "control my mouse",
        )
    )
    wants_memory = any(marker in phrase for marker in ("remember", "save this", "learn this"))
    wants_draft = any(
        marker in phrase
        for marker in ("draft", "plan", "what next", "what should i click next", "steps")
    )
    wants_assistive = any(marker in phrase for marker in ("fix", "change", "apply"))

    if blocked_requested:
        return AgenticRouteDecision(
            decision_id="route_decision_blocked_001",
            route_kind=AgenticRouteKind.BLOCKED,
            selected_route_id=None,
            gateway_tool="policy.block_unsafe_effect",
            user_visible_label="I cannot do that yet",
            user_visible_rationale=(
                "This asks for real cursor, capture, external, destructive, or unreviewed effects."
            ),
            execution_mode=ExecutionMode.DRAFT_ONLY,
            risk_level=ActionRisk.HIGH,
            allowed_effects=[],
            blocked_effects=list(BLOCKED_AGENTIC_EFFECTS),
            requires_confirmation=True,
            approval_reason="Unsafe effect requested; Cortex can only explain or draft in safe mode.",
        )

    if wants_memory:
        route = _route_by_id(plan, "route_memory_proposal")
        return AgenticRouteDecision(
            decision_id="route_decision_memory_001",
            route_kind=AgenticRouteKind.DRAFT_ONLY,
            selected_route_id=route.route_id,
            gateway_tool=route.gateway_tool,
            user_visible_label="Draft a memory card",
            user_visible_rationale="Cortex can propose a Memory Book card for your review.",
            execution_mode=route.execution_mode,
            risk_level=route.risk_level,
            allowed_effects=route.allowed_effects,
            blocked_effects=list(BLOCKED_AGENTIC_EFFECTS),
            requires_confirmation=True,
            approval_reason="Saving memory is a user-reviewed action.",
            memory_proposal_allowed=True,
        )

    if wants_assistive:
        route = _route_by_id(plan, "route_skill_draft")
        return AgenticRouteDecision(
            decision_id="route_decision_assistive_001",
            route_kind=AgenticRouteKind.ASSISTIVE_WITH_APPROVAL,
            selected_route_id=route.route_id,
            gateway_tool=route.gateway_tool,
            user_visible_label="Prepare a reviewed assistive action",
            user_visible_rationale="Cortex can draft the local action but must ask before effects.",
            execution_mode=ExecutionMode.ASSISTIVE,
            risk_level=ActionRisk.MEDIUM,
            allowed_effects=[RuntimeEffect.LOCAL_READ],
            blocked_effects=list(BLOCKED_AGENTIC_EFFECTS),
            requires_confirmation=True,
            approval_reason="Assistive changes require explicit confirmation.",
        )

    if wants_draft:
        route = _route_by_id(plan, "route_skill_draft")
        return AgenticRouteDecision(
            decision_id="route_decision_draft_001",
            route_kind=AgenticRouteKind.DRAFT_ONLY,
            selected_route_id=route.route_id,
            gateway_tool=route.gateway_tool,
            user_visible_label="Draft the next steps",
            user_visible_rationale="Cortex can show the safest next step beside the pointer.",
            execution_mode=route.execution_mode,
            risk_level=route.risk_level,
            allowed_effects=route.allowed_effects,
            blocked_effects=list(BLOCKED_AGENTIC_EFFECTS),
            requires_confirmation=True,
            approval_reason="Drafted steps can influence action, so review stays visible.",
        )

    route = _route_by_id(plan, "route_pointer_context")
    return AgenticRouteDecision(
        decision_id="route_decision_answer_001",
        route_kind=AgenticRouteKind.ANSWER_ONLY,
        selected_route_id=route.route_id,
        gateway_tool=route.gateway_tool,
        user_visible_label=f"Explain {pointer_event.target_label}",
        user_visible_rationale="Cortex can answer from the controlled pointer target only.",
        execution_mode=route.execution_mode,
        risk_level=ActionRisk.LOW,
        allowed_effects=route.allowed_effects,
        blocked_effects=list(BLOCKED_AGENTIC_EFFECTS),
    )


def build_agentic_turn(
    *,
    pointer_event: PointerIntentEvent | None = None,
    goal: str = "Answer the user's pointer-first question safely.",
    active_project: str = "cortex-memory-os",
) -> AgenticTurn:
    pointer_event = pointer_event or build_pointer_intent_event()
    plan = build_agentic_os_plan(
        goal=goal,
        user_phrase=pointer_event.user_phrase,
        active_project=active_project,
    )
    decision = resolve_agentic_route(pointer_event, plan=plan)
    approval = None
    if decision.requires_confirmation:
        approval = AgenticApprovalRequest(
            approval_id=f"approval_{decision.decision_id}",
            decision_id=decision.decision_id,
            reason=decision.approval_reason or "Review is required before this route can proceed.",
        )
    memory_review = decision.memory_proposal_allowed
    receipt = AgenticRunReceipt(
        receipt_id="agentic_run_receipt_001",
        turn_id="agentic_turn_001",
        target_label=pointer_event.target_label,
        route_kind=decision.route_kind,
        gateway_tool=decision.gateway_tool,
        confidence=pointer_event.confidence,
        approval_required=decision.requires_confirmation,
        memory_proposal_created=memory_review,
        blocked_effects=list(BLOCKED_AGENTIC_EFFECTS),
        user_visible_summary=_receipt_summary(pointer_event, decision),
    )
    return AgenticTurn(
        turn_id="agentic_turn_001",
        goal=goal,
        pointer_event=pointer_event,
        plan=plan,
        route_decision=decision,
        approval_request=approval,
        receipt=receipt,
        pointer_card_title=decision.user_visible_label,
        pointer_card_body=_pointer_card_body(pointer_event, decision),
        pointer_card_primary_action=_primary_action(decision),
        memory_proposal_review_required=memory_review,
    )


def agentic_turn_from_live_tutor_turn(live_turn: Any) -> AgenticTurn:
    pointer_event = build_pointer_intent_event(
        user_phrase=live_turn.user_utterance,
        target_id=live_turn.target_id,
        target_label=live_turn.target_label,
        target_role="controlled_demo_target",
        app_surface=live_turn.app_surface,
        screen_state_ref=live_turn.screen_state_ref,
        pointer_referent=live_turn.pointer_referent,
        referenced_target_ids=list(live_turn.referenced_target_ids),
        pointer_x=live_turn.target_coordinates.x,
        pointer_y=live_turn.target_coordinates.y,
        confidence=live_turn.confidence,
    )
    return build_agentic_turn(
        pointer_event=pointer_event,
        goal="Route the live tutor turn through the Agentic OS safety spine.",
    )


def run_agentic_turn_smoke() -> AgenticTurnSmokeResult:
    turn = build_agentic_turn(
        pointer_event=build_pointer_intent_event(
            user_phrase="What should I click next?",
            target_id="color_page_button",
            target_label="Color Page",
            target_role="navigation_button",
            pointer_x=1260,
            pointer_y=884,
            confidence=0.88,
        )
    )
    return AgenticTurnSmokeResult(
        passed=(
            turn.route_decision.route_kind == AgenticRouteKind.DRAFT_ONLY
            and turn.route_decision.requires_confirmation
            and turn.receipt.runtime_trace_recorded
            and not turn.receipt.durable_memory_write_performed
            and not turn.receipt.raw_payload_included
        ),
        turn=turn,
        route_kind=turn.route_decision.route_kind,
        approval_required=turn.route_decision.requires_confirmation,
        blocked_effect_count=len(turn.receipt.blocked_effects),
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


def _route_by_id(plan: AgenticOSPlan, route_id: str) -> AgenticToolRoute:
    for route in plan.routes:
        if route.route_id == route_id:
            return route
    raise ValueError(f"missing route: {route_id}")


def _pointer_card_body(
    pointer_event: PointerIntentEvent,
    decision: AgenticRouteDecision,
) -> str:
    if decision.route_kind == AgenticRouteKind.BLOCKED:
        return "I can explain this safely, but I will not click, type, capture, export, or save."
    if decision.memory_proposal_allowed:
        return f"I see {pointer_event.target_label}. I can draft a memory card for review."
    if decision.route_kind == AgenticRouteKind.DRAFT_ONLY:
        return f"I see {pointer_event.target_label}. I can draft the next safe steps."
    if decision.route_kind == AgenticRouteKind.ASSISTIVE_WITH_APPROVAL:
        return f"I see {pointer_event.target_label}. I can prepare a reviewed local action."
    return f"I see {pointer_event.target_label}. I can explain it without touching your system."


def _primary_action(decision: AgenticRouteDecision) -> str:
    if decision.route_kind == AgenticRouteKind.BLOCKED:
        return "Explain only"
    if decision.memory_proposal_allowed:
        return "Review memory"
    if decision.route_kind == AgenticRouteKind.DRAFT_ONLY:
        return "Show steps"
    if decision.route_kind == AgenticRouteKind.ASSISTIVE_WITH_APPROVAL:
        return "Review action"
    return "Explain this"


def _receipt_summary(
    pointer_event: PointerIntentEvent,
    decision: AgenticRouteDecision,
) -> str:
    return (
        f"Cortex saw {pointer_event.target_label}, chose {decision.route_kind.value}, "
        "and kept click, type, capture, raw refs, external effects, and memory writes blocked."
    )


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--turn-smoke", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.turn_smoke:
        turn_result = run_agentic_turn_smoke()
        if args.json:
            print(turn_result.model_dump_json(indent=2))
        else:
            print(
                f"{turn_result.benchmark_id}: passed={turn_result.passed} "
                f"route={turn_result.route_kind.value} approval={turn_result.approval_required}"
            )
        return 0 if turn_result.passed else 1
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
