"""Realtime voice pointer UX contracts for Cortex."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import Field, field_validator, model_validator

from cortex_memory_os.contracts import StrictModel

REALTIME_VOICE_CONTRACT_ID = "REALTIME-VOICE-CONTRACT-001"
POINTER_GESTURE_GRAMMAR_ID = "POINTER-GESTURE-GRAMMAR-001"
VOICE_OUTPUT_ROUTER_ID = "VOICE-OUTPUT-ROUTER-001"
REALTIME_COST_GUARD_ID = "REALTIME-COST-GUARD-001"
SYNTHETIC_VOICE_TURN_LOOP_ID = "SYNTHETIC-VOICE-TURN-LOOP-001"
REALTIME_CLIENT_SECRET_CONTRACT_ID = "REALTIME-CLIENT-SECRET-CONTRACT-001"
LIVE_TUTOR_VOICE_UX_ID = "LIVE-TUTOR-VOICE-UX-001"
SELECTION_UX_CONTRACT_ID = "SELECTION-UX-CONTRACT-001"
DASHBOARD_VOICE_POINTER_PANEL_ID = "DASHBOARD-VOICE-POINTER-PANEL-001"
REALTIME_VOICE_BENCH_DOCS_ID = "REALTIME-VOICE-BENCH-DOCS-001"
REALTIME_VOICE_POLICY_REF = "policy_realtime_voice_pointer_v1"

DEFAULT_REALTIME_MODEL = "gpt-realtime-2"
DEFAULT_REALTIME_TRANSPORT = "webrtc"
REALTIME_CLIENT_SECRET_ENDPOINT = "https://api.openai.com/v1/realtime/client_secrets"

VoiceGestureType = Literal[
    "triple_click_voice_dialogue",
    "press_hold_text_reply",
    "press_hold_action_only",
    "drag_select_targets",
    "single_click_context",
    "escape_cancel",
]
VoiceOutputMode = Literal[
    "silent_visual",
    "text_chip",
    "spoken_brief",
    "spoken_detail",
    "memory_review",
    "blocked",
]

_PROHIBITED_MARKERS = [
    "OPENAI_API_KEY=",
    "CORTEX_FAKE_TOKEN",
    "sk-",
    "raw://",
    "encrypted_blob://",
    "Ignore previous instructions",
    "BEGIN " + "PRIVATE KEY",
]

_GESTURE_DEFAULTS: dict[VoiceGestureType, dict[str, str]] = {
    "triple_click_voice_dialogue": {
        "label": "Triple click voice",
        "intent": "start a voice back-and-forth beside the pointer",
    },
    "press_hold_text_reply": {
        "label": "Press and hold",
        "intent": "ask by voice but get text back",
    },
    "press_hold_action_only": {
        "label": "Hold for action",
        "intent": "show the next action without a spoken reply",
    },
    "drag_select_targets": {
        "label": "Drag select",
        "intent": "group several pointed items",
    },
    "single_click_context": {
        "label": "Context click",
        "intent": "anchor Cortex on the pointed target",
    },
    "escape_cancel": {
        "label": "Cancel",
        "intent": "stop listening and hide transient output",
    },
}


class RealtimeVoiceBudget(StrictModel):
    budget_id: str = "realtime_voice_budget_demo_v1"
    max_session_seconds: int = Field(default=45, ge=5, le=300)
    max_input_audio_seconds: int = Field(default=18, ge=0, le=180)
    max_output_audio_seconds: int = Field(default=8, ge=0, le=60)
    max_response_count: int = Field(default=6, ge=1, le=40)
    max_text_output_tokens: int = Field(default=180, ge=16, le=1200)
    max_estimated_cost_usd: float = Field(default=0.12, ge=0, le=5)
    reasoning_effort: Literal["low"] = "low"
    truncation_retention_ratio: float = Field(default=0.8, ge=0.5, le=1.0)
    truncation_post_instructions_tokens: int = Field(default=1200, ge=200, le=12000)
    default_voice_output: Literal["off_until_user_gesture"] = "off_until_user_gesture"
    auto_stop_on_idle_seconds: int = Field(default=8, ge=3, le=60)
    raw_audio_retention: Literal["none"] = "none"
    policy_refs: list[str] = Field(default_factory=lambda: [REALTIME_VOICE_POLICY_REF])

    @model_validator(mode="after")
    def keep_budget_small_and_gated(self) -> RealtimeVoiceBudget:
        if self.max_output_audio_seconds > self.max_session_seconds:
            raise ValueError("output audio budget cannot exceed session budget")
        if self.max_input_audio_seconds > self.max_session_seconds:
            raise ValueError("input audio budget cannot exceed session budget")
        if REALTIME_VOICE_POLICY_REF not in self.policy_refs:
            raise ValueError("realtime voice budget requires policy ref")
        return self


class RealtimeVoiceSessionContract(StrictModel):
    contract_id: str = REALTIME_VOICE_CONTRACT_ID
    model: Literal["gpt-realtime-2"] = DEFAULT_REALTIME_MODEL
    transport: Literal["webrtc", "websocket"] = DEFAULT_REALTIME_TRANSPORT
    session_type: Literal["voice_agent"] = "voice_agent"
    input_modalities: list[Literal["audio", "text"]] = Field(
        default_factory=lambda: ["audio", "text"],
        min_length=1,
        max_length=2,
    )
    default_output_modalities: list[Literal["text"]] = Field(
        default_factory=lambda: ["text"],
        min_length=1,
        max_length=1,
    )
    audio_output_policy: Literal["gesture_or_explicit_request_only"] = (
        "gesture_or_explicit_request_only"
    )
    requires_ephemeral_client_secret: bool = True
    requires_explicit_mic_consent: bool = True
    mic_opens_by_default: bool = False
    screen_capture_enabled: bool = False
    raw_audio_retained: bool = False
    memory_write_allowed: bool = False
    reasoning_effort: Literal["low"] = "low"
    budget: RealtimeVoiceBudget = Field(default_factory=RealtimeVoiceBudget)
    official_docs: list[str] = Field(
        default_factory=lambda: [
            "https://developers.openai.com/api/docs/guides/realtime",
            "https://developers.openai.com/api/docs/guides/voice-agents",
            "https://developers.openai.com/api/docs/guides/realtime-costs",
            "https://developers.openai.com/api/docs/models/gpt-realtime-2",
        ]
    )
    policy_refs: list[str] = Field(default_factory=lambda: [REALTIME_VOICE_POLICY_REF])

    @model_validator(mode="after")
    def keep_realtime_contract_safe(self) -> RealtimeVoiceSessionContract:
        if not self.requires_ephemeral_client_secret:
            raise ValueError("browser/mobile realtime sessions require ephemeral client secrets")
        if not self.requires_explicit_mic_consent:
            raise ValueError("voice pointer requires explicit mic consent")
        if self.mic_opens_by_default:
            raise ValueError("voice pointer cannot open the mic by default")
        if self.screen_capture_enabled or self.raw_audio_retained or self.memory_write_allowed:
            raise ValueError("voice pointer contract cannot enable capture, raw audio, or memory writes")
        if self.default_output_modalities != ["text"]:
            raise ValueError("default realtime output must be text-only until a gesture asks for voice")
        if REALTIME_VOICE_POLICY_REF not in self.policy_refs:
            raise ValueError("realtime voice contract requires policy ref")
        return self


class PointerGesture(StrictModel):
    gesture_id: str = Field(min_length=1)
    gesture_type: VoiceGestureType
    target_id: str = Field(min_length=1)
    target_label: str = Field(min_length=1)
    pointer_x: float = Field(ge=0, le=1440)
    pointer_y: float = Field(ge=0, le=960)
    hold_ms: int = Field(default=0, ge=0, le=10000)
    click_count: int = Field(default=1, ge=0, le=5)
    selected_target_ids: list[str] = Field(default_factory=list, max_length=6)
    transcript_preview: str = Field(default="", max_length=240)
    source: Literal["synthetic_demo", "user_pointer_event"] = "synthetic_demo"
    starts_microphone: bool = False
    starts_screen_capture: bool = False
    executes_click: bool = False
    policy_refs: list[str] = Field(default_factory=lambda: [REALTIME_VOICE_POLICY_REF])

    @field_validator("target_id", "target_label", "transcript_preview")
    @classmethod
    def reject_prohibited_markers(cls, value: str) -> str:
        if any(marker in value for marker in _PROHIBITED_MARKERS):
            raise ValueError("voice pointer gesture cannot carry secret/raw/prompt markers")
        return value

    @model_validator(mode="after")
    def keep_gesture_non_mutating(self) -> PointerGesture:
        if self.starts_microphone or self.starts_screen_capture or self.executes_click:
            raise ValueError("voice pointer gesture cannot directly start mic, capture, or clicks")
        if self.gesture_type == "triple_click_voice_dialogue" and self.click_count < 3:
            raise ValueError("triple-click voice dialogue requires at least three clicks")
        if self.gesture_type in {"press_hold_text_reply", "press_hold_action_only"} and self.hold_ms < 450:
            raise ValueError("press-and-hold voice gestures require a real hold duration")
        if self.gesture_type == "drag_select_targets" and len(self.selected_target_ids) < 2:
            raise ValueError("selection gesture requires at least two selected targets")
        if REALTIME_VOICE_POLICY_REF not in self.policy_refs:
            raise ValueError("voice pointer gesture requires policy ref")
        return self


class VoiceOutputDecision(StrictModel):
    decision_id: str = Field(min_length=1)
    gesture_type: VoiceGestureType
    output_mode: VoiceOutputMode
    reason: str = Field(min_length=1, max_length=220)
    spoken_output_seconds_budgeted: int = Field(default=0, ge=0, le=60)
    text_output_tokens_budgeted: int = Field(default=0, ge=0, le=1200)
    no_voice_back: bool = False
    requires_user_confirmation: bool = False
    blocked: bool = False
    policy_refs: list[str] = Field(default_factory=lambda: [REALTIME_VOICE_POLICY_REF])

    @field_validator("reason")
    @classmethod
    def reject_prohibited_reason(cls, value: str) -> str:
        if any(marker in value for marker in _PROHIBITED_MARKERS):
            raise ValueError("voice output decision cannot carry secret/raw markers")
        return value

    @model_validator(mode="after")
    def keep_output_budget_consistent(self) -> VoiceOutputDecision:
        if self.output_mode in {"spoken_brief", "spoken_detail"}:
            if self.no_voice_back or self.spoken_output_seconds_budgeted <= 0:
                raise ValueError("spoken voice modes require voice output budget")
        if self.output_mode in {"silent_visual", "text_chip", "memory_review"}:
            if self.spoken_output_seconds_budgeted != 0:
                raise ValueError("non-spoken modes cannot reserve audio output seconds")
        if self.output_mode == "blocked" and not self.blocked:
            raise ValueError("blocked output mode requires blocked flag")
        if REALTIME_VOICE_POLICY_REF not in self.policy_refs:
            raise ValueError("voice output decision requires policy ref")
        return self


class RealtimeClientSecretPlan(StrictModel):
    plan_id: str = REALTIME_CLIENT_SECRET_CONTRACT_ID
    method: Literal["POST"] = "POST"
    endpoint: str = REALTIME_CLIENT_SECRET_ENDPOINT
    model: Literal["gpt-realtime-2"] = DEFAULT_REALTIME_MODEL
    transport: Literal["webrtc"] = DEFAULT_REALTIME_TRANSPORT
    server_side_only: bool = True
    returns_ephemeral_secret_to_browser: bool = True
    raw_api_key_exposed: bool = False
    client_secret_value_included: bool = False
    safety_identifier_required: bool = True
    session_payload: dict[str, Any]
    policy_refs: list[str] = Field(default_factory=lambda: [REALTIME_VOICE_POLICY_REF])

    @model_validator(mode="after")
    def keep_client_secret_plan_sanitized(self) -> RealtimeClientSecretPlan:
        serialized = json.dumps(self.session_payload, sort_keys=True)
        if any(marker in serialized for marker in _PROHIBITED_MARKERS):
            raise ValueError("realtime client secret plan cannot include secrets or raw refs")
        if not self.server_side_only or self.raw_api_key_exposed or self.client_secret_value_included:
            raise ValueError("realtime client secret plan must hide raw API and client secrets")
        if not self.safety_identifier_required:
            raise ValueError("realtime client secret plan requires a safety identifier")
        if REALTIME_VOICE_POLICY_REF not in self.policy_refs:
            raise ValueError("realtime client secret plan requires policy ref")
        return self


class SyntheticVoicePointerTurn(StrictModel):
    turn_id: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    target_label: str = Field(min_length=1)
    gesture: PointerGesture
    output_decision: VoiceOutputDecision
    transcript_preview: str = Field(min_length=1, max_length=240)
    user_visible_summary: str = Field(min_length=1, max_length=260)
    selected_target_ids: list[str] = Field(default_factory=list, max_length=6)
    model: Literal["gpt-realtime-2"] = DEFAULT_REALTIME_MODEL
    capture_mode: Literal["synthetic_transcript_only"] = "synthetic_transcript_only"
    mic_capture_enabled: bool = False
    raw_audio_retained: bool = False
    screen_capture_started: bool = False
    memory_write_allowed: bool = False
    external_effect_executed: bool = False
    estimated_cost_usd: float = Field(default=0, ge=0, le=1)
    cost_guard_triggered: bool = False
    policy_refs: list[str] = Field(default_factory=lambda: [REALTIME_VOICE_POLICY_REF])

    @field_validator("transcript_preview", "user_visible_summary")
    @classmethod
    def reject_prohibited_turn_text(cls, value: str) -> str:
        if any(marker in value for marker in _PROHIBITED_MARKERS):
            raise ValueError("synthetic voice turn cannot carry secret/raw markers")
        return value

    @model_validator(mode="after")
    def keep_synthetic_turn_safe(self) -> SyntheticVoicePointerTurn:
        if self.mic_capture_enabled or self.raw_audio_retained or self.screen_capture_started:
            raise ValueError("synthetic voice turn cannot enable live capture or raw audio")
        if self.memory_write_allowed or self.external_effect_executed:
            raise ValueError("synthetic voice turn cannot write memory or execute external effects")
        if self.gesture.target_id != self.target_id:
            raise ValueError("voice turn and gesture target must match")
        if REALTIME_VOICE_POLICY_REF not in self.policy_refs:
            raise ValueError("synthetic voice turn requires policy ref")
        return self


class RealtimeVoicePointerResult(StrictModel):
    proof_id: str = REALTIME_VOICE_CONTRACT_ID
    policy_ref: str = REALTIME_VOICE_POLICY_REF
    generated_at: datetime
    passed: bool
    turn_count: int = Field(ge=0)
    gesture_types: list[str] = Field(default_factory=list)
    output_modes: list[str] = Field(default_factory=list)
    selected_target_count: int = Field(ge=0)
    realtime_model: str = DEFAULT_REALTIME_MODEL
    client_secret_plan_ready: bool = True
    mic_capture_enabled: bool = False
    raw_audio_retained_count: int = Field(ge=0)
    screen_capture_started: bool = False
    memory_write_count: int = Field(ge=0)
    external_effect_count: int = Field(ge=0)
    estimated_cost_usd: float = Field(ge=0)
    cost_guard_triggered_count: int = Field(ge=0)
    prohibited_marker_count: int = Field(ge=0)
    safety_failures: list[str] = Field(default_factory=list)


class VoicePointerDashboardPanel(StrictModel):
    panel_id: str = DASHBOARD_VOICE_POINTER_PANEL_ID
    title: str = "Voice Pointer"
    summary: str = Field(min_length=1)
    model: str = DEFAULT_REALTIME_MODEL
    default_output: str = "text unless the gesture asks for voice"
    gestures: list[str] = Field(default_factory=list)
    output_modes: list[str] = Field(default_factory=list)
    cost_guard: dict[str, Any]
    mic_capture_enabled: bool = False
    raw_audio_retained: bool = False
    memory_write_allowed: bool = False
    policy_refs: list[str] = Field(default_factory=lambda: [REALTIME_VOICE_POLICY_REF])

    @model_validator(mode="after")
    def keep_panel_safe(self) -> VoicePointerDashboardPanel:
        if self.mic_capture_enabled or self.raw_audio_retained or self.memory_write_allowed:
            raise ValueError("voice pointer dashboard panel cannot enable capture or memory writes")
        if REALTIME_VOICE_POLICY_REF not in self.policy_refs:
            raise ValueError("voice pointer dashboard panel requires policy ref")
        return self


def build_realtime_voice_contract(
    *,
    budget: RealtimeVoiceBudget | None = None,
) -> RealtimeVoiceSessionContract:
    return RealtimeVoiceSessionContract(budget=budget or RealtimeVoiceBudget())


def build_realtime_client_secret_plan(
    *,
    budget: RealtimeVoiceBudget | None = None,
) -> RealtimeClientSecretPlan:
    budget = budget or RealtimeVoiceBudget()
    payload = {
        "session": {
            "type": "realtime",
            "model": DEFAULT_REALTIME_MODEL,
            "instructions": (
                "You are Cortex Pointer. Use voice input to decide where to point, "
                "but default to text output unless the current gesture explicitly asks "
                "for a brief spoken reply."
            ),
            "reasoning": {"effort": budget.reasoning_effort},
            "audio": {
                "output": {
                    "voice": "alloy",
                    "enabled": False,
                    "policy": "gesture_or_explicit_request_only",
                }
            },
            "truncation": {
                "type": "retention_ratio",
                "retention_ratio": budget.truncation_retention_ratio,
                "token_limits": {
                    "post_instructions": budget.truncation_post_instructions_tokens,
                },
            },
            "metadata": {
                "cortex_policy_ref": REALTIME_VOICE_POLICY_REF,
                "raw_audio_retention": budget.raw_audio_retention,
                "max_session_seconds": budget.max_session_seconds,
            },
        }
    }
    return RealtimeClientSecretPlan(session_payload=payload)


def route_voice_output(
    gesture: PointerGesture,
    *,
    budget: RealtimeVoiceBudget | None = None,
    wants_memory_review: bool = False,
) -> VoiceOutputDecision:
    budget = budget or RealtimeVoiceBudget()
    decision_id = f"voice_output_{gesture.gesture_id}"
    if gesture.gesture_type == "escape_cancel":
        return VoiceOutputDecision(
            decision_id=decision_id,
            gesture_type=gesture.gesture_type,
            output_mode="silent_visual",
            reason="User cancelled the transient voice pointer state.",
            no_voice_back=True,
        )
    if wants_memory_review or "remember" in gesture.transcript_preview.lower():
        return VoiceOutputDecision(
            decision_id=decision_id,
            gesture_type=gesture.gesture_type,
            output_mode="memory_review",
            reason="Memory intent routes to review UI instead of a spoken or durable write.",
            text_output_tokens_budgeted=min(120, budget.max_text_output_tokens),
            no_voice_back=True,
            requires_user_confirmation=True,
        )
    if gesture.gesture_type == "triple_click_voice_dialogue":
        if budget.max_output_audio_seconds <= 0:
            return VoiceOutputDecision(
                decision_id=decision_id,
                gesture_type=gesture.gesture_type,
                output_mode="text_chip",
                reason="Spoken output is disabled by the current cost guard.",
                text_output_tokens_budgeted=min(120, budget.max_text_output_tokens),
                no_voice_back=True,
            )
        return VoiceOutputDecision(
            decision_id=decision_id,
            gesture_type=gesture.gesture_type,
            output_mode="spoken_brief",
            reason="Triple click explicitly asks Cortex for a short voice back-and-forth.",
            spoken_output_seconds_budgeted=min(4, budget.max_output_audio_seconds),
            text_output_tokens_budgeted=min(100, budget.max_text_output_tokens),
        )
    if gesture.gesture_type == "press_hold_text_reply":
        return VoiceOutputDecision(
            decision_id=decision_id,
            gesture_type=gesture.gesture_type,
            output_mode="text_chip",
            reason="Press-and-hold asks by voice but wants the answer silently as text.",
            text_output_tokens_budgeted=min(140, budget.max_text_output_tokens),
            no_voice_back=True,
        )
    if gesture.gesture_type == "press_hold_action_only":
        return VoiceOutputDecision(
            decision_id=decision_id,
            gesture_type=gesture.gesture_type,
            output_mode="silent_visual",
            reason="Action-only hold routes to visual pointer cues without voice output.",
            no_voice_back=True,
        )
    if gesture.gesture_type == "drag_select_targets":
        return VoiceOutputDecision(
            decision_id=decision_id,
            gesture_type=gesture.gesture_type,
            output_mode="text_chip",
            reason="Selection gestures summarize the selected target stack as text.",
            text_output_tokens_budgeted=min(160, budget.max_text_output_tokens),
            no_voice_back=True,
        )
    return VoiceOutputDecision(
        decision_id=decision_id,
        gesture_type=gesture.gesture_type,
        output_mode="text_chip",
        reason="Single pointer context uses a small text chip by default.",
        text_output_tokens_budgeted=min(80, budget.max_text_output_tokens),
        no_voice_back=True,
    )


def build_pointer_gesture(
    *,
    gesture_type: VoiceGestureType,
    target_id: str,
    target_label: str,
    pointer_x: float = 720,
    pointer_y: float = 480,
    transcript_preview: str = "What is this?",
    selected_target_ids: list[str] | None = None,
) -> PointerGesture:
    click_count = 3 if gesture_type == "triple_click_voice_dialogue" else 1
    hold_ms = 720 if gesture_type in {"press_hold_text_reply", "press_hold_action_only"} else 0
    selected = selected_target_ids or []
    if gesture_type == "drag_select_targets" and len(selected) < 2:
        selected = [target_id, "node_graph" if target_id != "node_graph" else "lut_menu"]
    return PointerGesture(
        gesture_id=f"gesture_{gesture_type}_{target_id}",
        gesture_type=gesture_type,
        target_id=target_id,
        target_label=target_label,
        pointer_x=pointer_x,
        pointer_y=pointer_y,
        hold_ms=hold_ms,
        click_count=click_count,
        selected_target_ids=selected,
        transcript_preview=transcript_preview,
    )


def resolve_synthetic_voice_turn(
    *,
    gesture: PointerGesture,
    budget: RealtimeVoiceBudget | None = None,
    sequence: int = 1,
) -> SyntheticVoicePointerTurn:
    decision = route_voice_output(gesture, budget=budget)
    summary = _summary_for_decision(gesture, decision)
    return SyntheticVoicePointerTurn(
        turn_id=f"synthetic_voice_turn_{sequence:03d}",
        target_id=gesture.target_id,
        target_label=gesture.target_label,
        gesture=gesture,
        output_decision=decision,
        transcript_preview=gesture.transcript_preview or _GESTURE_DEFAULTS[gesture.gesture_type]["intent"],
        user_visible_summary=summary,
        selected_target_ids=gesture.selected_target_ids,
    )


def run_realtime_voice_pointer_smoke() -> RealtimeVoicePointerResult:
    budget = RealtimeVoiceBudget()
    contract = build_realtime_voice_contract(budget=budget)
    plan = build_realtime_client_secret_plan(budget=budget)
    gestures = [
        build_pointer_gesture(
            gesture_type="triple_click_voice_dialogue",
            target_id="node_graph",
            target_label="Node Graph",
            transcript_preview="Can you talk me through this?",
        ),
        build_pointer_gesture(
            gesture_type="press_hold_text_reply",
            target_id="lut_menu",
            target_label="LUT Menu",
            transcript_preview="Tell me what this does, but text only.",
        ),
        build_pointer_gesture(
            gesture_type="press_hold_action_only",
            target_id="color_page_button",
            target_label="Color Page",
            transcript_preview="Show me the next action, no voice back.",
        ),
        build_pointer_gesture(
            gesture_type="drag_select_targets",
            target_id="lut_menu",
            target_label="LUT Menu",
            selected_target_ids=["node_graph", "lut_menu", "inspector"],
            transcript_preview="Compare these.",
        ),
        build_pointer_gesture(
            gesture_type="single_click_context",
            target_id="inspector",
            target_label="Inspector",
            transcript_preview="Remember this after I review it.",
        ),
    ]
    turns = [
        resolve_synthetic_voice_turn(gesture=gesture, budget=budget, sequence=index)
        for index, gesture in enumerate(gestures, start=1)
    ]
    serialized = "\n".join(
        [
            contract.model_dump_json(),
            plan.model_dump_json(),
            *[turn.model_dump_json() for turn in turns],
        ]
    )
    prohibited_marker_count = sum(1 for marker in _PROHIBITED_MARKERS if marker in serialized)
    checks = {
        "contract_safe": (
            contract.model == DEFAULT_REALTIME_MODEL
            and contract.transport == DEFAULT_REALTIME_TRANSPORT
            and contract.default_output_modalities == ["text"]
            and not contract.mic_opens_by_default
            and not contract.memory_write_allowed
        ),
        "client_secret_plan": (
            plan.endpoint == REALTIME_CLIENT_SECRET_ENDPOINT
            and plan.server_side_only
            and not plan.raw_api_key_exposed
            and not plan.client_secret_value_included
        ),
        "gesture_coverage": {
            turn.gesture.gesture_type for turn in turns
        }
        >= {
            "triple_click_voice_dialogue",
            "press_hold_text_reply",
            "press_hold_action_only",
            "drag_select_targets",
        },
        "output_coverage": {turn.output_decision.output_mode for turn in turns}
        >= {"spoken_brief", "text_chip", "silent_visual", "memory_review"},
        "safe_turns": all(
            not turn.mic_capture_enabled
            and not turn.raw_audio_retained
            and not turn.screen_capture_started
            and not turn.memory_write_allowed
            and not turn.external_effect_executed
            for turn in turns
        ),
        "selection_present": any(len(turn.selected_target_ids) >= 2 for turn in turns),
        "cost_safe": sum(turn.estimated_cost_usd for turn in turns) <= budget.max_estimated_cost_usd,
        "no_prohibited_markers": prohibited_marker_count == 0,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return RealtimeVoicePointerResult(
        generated_at=datetime.now(UTC),
        passed=not failures,
        turn_count=len(turns),
        gesture_types=[turn.gesture.gesture_type for turn in turns],
        output_modes=[turn.output_decision.output_mode for turn in turns],
        selected_target_count=max(len(turn.selected_target_ids) for turn in turns),
        realtime_model=contract.model,
        client_secret_plan_ready=checks["client_secret_plan"],
        mic_capture_enabled=any(turn.mic_capture_enabled for turn in turns),
        raw_audio_retained_count=sum(int(turn.raw_audio_retained) for turn in turns),
        screen_capture_started=any(turn.screen_capture_started for turn in turns),
        memory_write_count=sum(int(turn.memory_write_allowed) for turn in turns),
        external_effect_count=sum(int(turn.external_effect_executed) for turn in turns),
        estimated_cost_usd=sum(turn.estimated_cost_usd for turn in turns),
        cost_guard_triggered_count=sum(int(turn.cost_guard_triggered) for turn in turns),
        prohibited_marker_count=prohibited_marker_count,
        safety_failures=failures,
    )


def build_voice_pointer_dashboard_panel(
    result: RealtimeVoicePointerResult | None = None,
) -> VoicePointerDashboardPanel:
    result = result or run_realtime_voice_pointer_smoke()
    budget = RealtimeVoiceBudget()
    return VoicePointerDashboardPanel(
        summary=(
            "Triple click starts a short voice back-and-forth; click-and-hold can "
            "ask by voice while returning text or only moving the guide pointer."
        ),
        gestures=result.gesture_types,
        output_modes=result.output_modes,
        cost_guard={
            "max_session_seconds": budget.max_session_seconds,
            "max_input_audio_seconds": budget.max_input_audio_seconds,
            "max_output_audio_seconds": budget.max_output_audio_seconds,
            "max_response_count": budget.max_response_count,
            "max_estimated_cost_usd": budget.max_estimated_cost_usd,
            "reasoning_effort": budget.reasoning_effort,
            "default_voice_output": budget.default_voice_output,
        },
    )


def _summary_for_decision(gesture: PointerGesture, decision: VoiceOutputDecision) -> str:
    if decision.output_mode == "spoken_brief":
        return f"Cortex would briefly speak about {gesture.target_label}, then stay beside it."
    if decision.output_mode == "text_chip":
        return f"Cortex would answer as text beside {gesture.target_label} with no voice back."
    if decision.output_mode == "silent_visual":
        return f"Cortex would point at {gesture.target_label} and stay silent."
    if decision.output_mode == "memory_review":
        return f"Cortex would prepare a review card for {gesture.target_label}; nothing is saved."
    return "Cortex blocked the requested voice pointer output."


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--client-secret-plan", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.client_secret_plan:
        payload = build_realtime_client_secret_plan().model_dump(mode="json")
        print(json.dumps(payload, indent=2, sort_keys=True) if args.json else payload)
        return 0

    result = run_realtime_voice_pointer_smoke()
    if args.json or args.smoke:
        print(json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True))
    else:
        print(
            "realtime voice pointer "
            f"{'passed' if result.passed else 'failed'}: "
            f"{result.turn_count} synthetic turns"
        )
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
