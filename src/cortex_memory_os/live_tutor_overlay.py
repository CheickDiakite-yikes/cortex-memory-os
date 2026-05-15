"""Safe local live tutor overlay contracts and demo decision layer."""

from __future__ import annotations

import argparse
import http.client
import json
import mimetypes
import secrets
import threading
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlparse

from pydantic import Field, ValidationError, field_validator, model_validator

from cortex_memory_os.contracts import StrictModel
from cortex_memory_os.realtime_voice_pointer import (
    DEFAULT_REALTIME_MODEL,
    REALTIME_COST_GUARD_ID,
    REALTIME_VOICE_POLICY_REF,
    VoiceGestureType,
    VoiceOutputMode,
    build_pointer_gesture,
    route_voice_output,
)

LIVE_TUTOR_OVERLAY_ID = "LIVE-TUTOR-OVERLAY-001"
LIVE_TUTOR_OVERLAY_POLICY_REF = "policy_live_tutor_overlay_v1"
LIVE_TUTOR_BROWSER_PROOF_ID = "LIVE-TUTOR-BROWSER-PROOF-001"
LIVE_TUTOR_BROWSER_PROOF_POLICY_REF = "policy_live_tutor_browser_proof_v1"
DEFAULT_LIVE_TUTOR_HOST = "127.0.0.1"
DEFAULT_LIVE_TUTOR_PORT = 8797
LIVE_TUTOR_TOKEN_HEADER = "X-Cortex-Live-Tutor-Token"
LIVE_TUTOR_TOKEN_PLACEHOLDER = "__CORTEX_LIVE_TUTOR_TOKEN__"
REPO_ROOT = Path(__file__).resolve().parents[2]
UI_ROOT = REPO_ROOT / "ui" / "live-tutor-demo"
LIVE_TUTOR_SECURITY_HEADERS = {
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self'; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "base-uri 'none'; "
        "frame-ancestors 'none'"
    ),
}

LIVE_TUTOR_ALLOWED_EFFECTS = {
    "read_controlled_demo_state",
    "render_shadow_tutor_cursor",
    "render_target_highlight",
    "render_instruction_bubble",
    "write_safe_demo_receipt",
}

LIVE_TUTOR_REQUIRED_BLOCKED_EFFECTS = {
    "execute_click",
    "type_text",
    "start_screen_capture",
    "start_microphone_capture",
    "start_accessibility_observer",
    "write_memory",
    "store_raw_evidence",
    "retain_raw_ref",
    "export_payload",
    "external_effect",
}

_PROHIBITED_MARKERS = [
    "OPENAI_API_KEY=",
    "CORTEX_FAKE_TOKEN",
    "sk-",
    "raw://",
    "encrypted_blob://",
    "Ignore previous instructions",
    "BEGIN " + "PRIVATE KEY",
]


class DemoTarget(StrictModel):
    target_id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    role: str = Field(min_length=1)
    region: str = Field(min_length=1)
    plain_description: str = Field(default="", max_length=180)
    x: float = Field(ge=0)
    y: float = Field(ge=0)
    width: float = Field(gt=0)
    height: float = Field(gt=0)
    state: str = "idle"

    @model_validator(mode="after")
    def keep_target_in_viewport(self) -> DemoTarget:
        if self.x + self.width > 1440 or self.y + self.height > 960:
            raise ValueError("demo target must fit within the controlled viewport")
        return self

    @property
    def center_x(self) -> float:
        return self.x + self.width / 2

    @property
    def center_y(self) -> float:
        return self.y + self.height / 2


class SafeCreativeDemoSurface(StrictModel):
    surface_id: str = "safe_creative_tool_demo_surface_v1"
    app_label: str = "Cortex Resolve Studio"
    viewport_width: int = Field(default=1440, ge=320, le=3840)
    viewport_height: int = Field(default=960, ge=320, le=2160)
    active_page: str = "edit"
    selected_clip: str = "Interview_A_cam_001"
    target_count: int = Field(ge=1)
    targets: list[DemoTarget] = Field(min_length=1)
    read_only: bool = True
    controlled_surface: bool = True
    real_screen_capture_started: bool = False
    raw_payload_included: bool = False
    raw_ref_retained: bool = False
    external_content_loaded: bool = False
    policy_refs: list[str] = Field(
        default_factory=lambda: [LIVE_TUTOR_OVERLAY_POLICY_REF, REALTIME_VOICE_POLICY_REF]
    )

    @model_validator(mode="after")
    def keep_surface_controlled_and_safe(self) -> SafeCreativeDemoSurface:
        if self.target_count != len(self.targets):
            raise ValueError("target_count must match targets")
        if not self.read_only or not self.controlled_surface:
            raise ValueError("live tutor demo surface must be read-only and controlled")
        if self.real_screen_capture_started or self.raw_payload_included or self.raw_ref_retained:
            raise ValueError("live tutor demo surface cannot include live capture or raw refs")
        if self.external_content_loaded:
            raise ValueError("live tutor demo surface cannot load external content")
        if LIVE_TUTOR_OVERLAY_POLICY_REF not in self.policy_refs:
            raise ValueError("live tutor demo surface requires policy ref")
        for target in self.targets:
            if (
                target.x + target.width > self.viewport_width
                or target.y + target.height > self.viewport_height
            ):
                raise ValueError("demo target exceeds surface viewport")
        return self

    def target_by_id(self, target_id: str) -> DemoTarget:
        for target in self.targets:
            if target.target_id == target_id:
                return target
        raise KeyError(target_id)


class SpatialTutorCue(StrictModel):
    cue_id: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    target_label: str = Field(min_length=1)
    x: float = Field(ge=0)
    y: float = Field(ge=0)
    viewport_width: int = Field(default=1440, ge=320, le=3840)
    viewport_height: int = Field(default=960, ge=320, le=2160)
    coordinate_space: Literal["viewport_css_pixels"] = "viewport_css_pixels"
    pointer_style: Literal["blue_secondary_cursor"] = "blue_secondary_cursor"
    highlight_shape: Literal["rounded_rect", "circle"] = "rounded_rect"
    display_only: bool = True
    allowed_effects: list[str] = Field(default_factory=list)
    blocked_effects: list[str] = Field(default_factory=list)
    policy_refs: list[str] = Field(
        default_factory=lambda: [LIVE_TUTOR_OVERLAY_POLICY_REF, REALTIME_VOICE_POLICY_REF]
    )

    @model_validator(mode="after")
    def keep_cue_display_only(self) -> SpatialTutorCue:
        if not self.display_only:
            raise ValueError("spatial tutor cue must be display-only")
        if self.x > self.viewport_width or self.y > self.viewport_height:
            raise ValueError("spatial tutor cue coordinates exceed viewport")
        if set(self.allowed_effects) - LIVE_TUTOR_ALLOWED_EFFECTS:
            raise ValueError("spatial tutor cue allowed effects are too broad")
        if missing := sorted(LIVE_TUTOR_REQUIRED_BLOCKED_EFFECTS.difference(self.blocked_effects)):
            raise ValueError(f"spatial tutor cue missing blocked effects: {missing}")
        if LIVE_TUTOR_OVERLAY_POLICY_REF not in self.policy_refs:
            raise ValueError("spatial tutor cue requires policy ref")
        return self


class LiveTutorPointerState(StrictModel):
    current_target_id: str | None = None
    previous_target_id: str | None = None
    selected_target_ids: list[str] = Field(default_factory=list, max_length=4)
    pointer_x: float | None = Field(default=None, ge=0, le=1440)
    pointer_y: float | None = Field(default=None, ge=0, le=960)
    referent_phrase: Literal["this", "that", "these", "none"] = "none"

    @field_validator("current_target_id", "previous_target_id")
    @classmethod
    def reject_prohibited_target_markers(cls, value: str | None) -> str | None:
        if value is not None and any(marker in value for marker in _PROHIBITED_MARKERS):
            raise ValueError("pointer target cannot carry secret/raw/prompt-injection markers")
        return value

    @field_validator("selected_target_ids")
    @classmethod
    def keep_selected_targets_safe(cls, value: list[str]) -> list[str]:
        for target_id in value:
            if any(marker in target_id for marker in _PROHIBITED_MARKERS):
                raise ValueError("selected target cannot carry secret/raw/prompt-injection markers")
        return value


class LiveTutorNormalizedPointer(StrictModel):
    source_coordinate_space: Literal["canonical_surface", "client_surface_css"]
    pointer_x: float = Field(ge=0, le=1440)
    pointer_y: float = Field(ge=0, le=960)
    client_surface_width: float | None = Field(default=None, ge=1, le=10000)
    client_surface_height: float | None = Field(default=None, ge=1, le=10000)
    canonical_surface_width: int = Field(default=1440, ge=320, le=3840)
    canonical_surface_height: int = Field(default=960, ge=320, le=2160)
    client_pointer_was_clamped: bool = False
    display_only: bool = True
    policy_refs: list[str] = Field(
        default_factory=lambda: [LIVE_TUTOR_OVERLAY_POLICY_REF, LIVE_TUTOR_BROWSER_PROOF_POLICY_REF]
    )

    @model_validator(mode="after")
    def keep_pointer_display_only(self) -> LiveTutorNormalizedPointer:
        if not self.display_only:
            raise ValueError("normalized pointer must remain display-only")
        if LIVE_TUTOR_OVERLAY_POLICY_REF not in self.policy_refs:
            raise ValueError("normalized pointer requires live tutor policy ref")
        if LIVE_TUTOR_BROWSER_PROOF_POLICY_REF not in self.policy_refs:
            raise ValueError("normalized pointer requires browser proof policy ref")
        return self


class ManualMemoryProposal(StrictModel):
    proposal_id: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    target_label: str = Field(min_length=1)
    content_preview: str = Field(min_length=1, max_length=220)
    status: Literal["needs_user_confirmation"] = "needs_user_confirmation"
    scope: Literal["manual_memory_book"] = "manual_memory_book"
    durable_write_performed: bool = False
    user_confirmation_required: bool = True
    policy_refs: list[str] = Field(
        default_factory=lambda: [LIVE_TUTOR_OVERLAY_POLICY_REF, REALTIME_VOICE_POLICY_REF]
    )

    @field_validator("content_preview")
    @classmethod
    def reject_prohibited_content(cls, value: str) -> str:
        if any(marker in value for marker in _PROHIBITED_MARKERS):
            raise ValueError("manual memory proposal cannot carry secret/raw markers")
        return value

    @model_validator(mode="after")
    def keep_proposal_manual_only(self) -> ManualMemoryProposal:
        if self.durable_write_performed:
            raise ValueError("live tutor cannot perform durable memory writes")
        if not self.user_confirmation_required:
            raise ValueError("manual memory proposal requires user confirmation")
        if LIVE_TUTOR_OVERLAY_POLICY_REF not in self.policy_refs:
            raise ValueError("manual memory proposal requires policy ref")
        return self


class LiveTutorCompanionState(StrictModel):
    mode: Literal["tracking", "answering", "review_required"] = "answering"
    label: str = Field(min_length=1, max_length=80)
    safety_caption: str = Field(min_length=1, max_length=140)
    display_only: bool = True
    answer_anchor: Literal["beside_pointer"] = "beside_pointer"
    policy_refs: list[str] = Field(
        default_factory=lambda: [LIVE_TUTOR_OVERLAY_POLICY_REF, REALTIME_VOICE_POLICY_REF]
    )

    @field_validator("label", "safety_caption")
    @classmethod
    def reject_prohibited_text(cls, value: str) -> str:
        if any(marker in value for marker in _PROHIBITED_MARKERS):
            raise ValueError("companion state cannot carry secret/raw markers")
        return value

    @model_validator(mode="after")
    def keep_companion_display_only(self) -> LiveTutorCompanionState:
        if not self.display_only:
            raise ValueError("live tutor companion state must be display-only")
        if LIVE_TUTOR_OVERLAY_POLICY_REF not in self.policy_refs:
            raise ValueError("live tutor companion state requires policy ref")
        return self


class LiveTutorTurn(StrictModel):
    turn_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    user_utterance: str = Field(min_length=1, max_length=240)
    app_surface: str = Field(min_length=1)
    screen_state_ref: str = Field(pattern=r"^controlled_dom://")
    intent_label: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    target_label: str = Field(min_length=1)
    referenced_target_ids: list[str] = Field(default_factory=list, min_length=1, max_length=4)
    pointer_referent: Literal["this", "that", "these", "none"] = "none"
    target_coordinates: SpatialTutorCue
    assistant_response: str = Field(min_length=1, max_length=420)
    micro_steps: list[str] = Field(default_factory=list, min_length=1, max_length=3)
    user_readable_receipt: str = Field(min_length=1, max_length=260)
    companion_state: LiveTutorCompanionState
    confidence: float = Field(ge=0, le=1)
    next_user_action: str = Field(min_length=1)
    manual_memory_proposal: ManualMemoryProposal | None = None
    safety_flags: list[str] = Field(default_factory=list)
    ai_assist_mode: Literal["local", "openai_dry_run"] = "local"
    ai_model: str | None = None
    ai_store_false: bool = True
    ai_prompt_char_count: int | None = Field(default=None, ge=1, le=2400)
    voice_gesture_type: VoiceGestureType = "single_click_context"
    voice_output_mode: VoiceOutputMode = "text_chip"
    voice_route_reason: str = Field(default="Typed question uses text beside the pointer.", max_length=220)
    realtime_voice_model: str = DEFAULT_REALTIME_MODEL
    realtime_voice_ready: bool = True
    voice_cost_guard_id: str = REALTIME_COST_GUARD_ID
    voice_transcript_source: Literal["typed_or_synthetic", "synthetic_voice"] = "typed_or_synthetic"
    spoken_output_seconds_budgeted: int = Field(default=0, ge=0, le=60)
    no_voice_back: bool = True
    display_only: bool = True
    memory_write_allowed: bool = False
    raw_ref_retained: bool = False
    external_effect_executed: bool = False
    real_screen_capture_started: bool = False
    voice_capture_enabled: bool = False
    policy_refs: list[str] = Field(
        default_factory=lambda: [LIVE_TUTOR_OVERLAY_POLICY_REF, REALTIME_VOICE_POLICY_REF]
    )

    @field_validator("user_utterance", "assistant_response", "next_user_action")
    @classmethod
    def reject_prohibited_markers(cls, value: str) -> str:
        if any(marker in value for marker in _PROHIBITED_MARKERS):
            raise ValueError("live tutor turn cannot carry secret/raw/prompt-injection markers")
        return value

    @field_validator("voice_route_reason")
    @classmethod
    def reject_prohibited_voice_reason(cls, value: str) -> str:
        if any(marker in value for marker in _PROHIBITED_MARKERS):
            raise ValueError("live tutor voice reason cannot carry secret/raw markers")
        return value

    @field_validator("micro_steps")
    @classmethod
    def reject_prohibited_micro_steps(cls, value: list[str]) -> list[str]:
        for step in value:
            if any(marker in step for marker in _PROHIBITED_MARKERS):
                raise ValueError("live tutor micro steps cannot carry secret/raw markers")
        return value

    @model_validator(mode="after")
    def keep_turn_non_mutating(self) -> LiveTutorTurn:
        if not self.display_only:
            raise ValueError("live tutor turn must be display-only")
        if self.memory_write_allowed:
            raise ValueError("live tutor turn cannot write memory")
        if self.raw_ref_retained:
            raise ValueError("live tutor turn cannot retain raw refs")
        if self.external_effect_executed:
            raise ValueError("live tutor turn cannot execute external effects")
        if self.real_screen_capture_started or self.voice_capture_enabled:
            raise ValueError("live tutor turn cannot start screen or voice capture")
        if self.target_coordinates.target_id != self.target_id:
            raise ValueError("live tutor turn target and cue target must match")
        if self.target_id not in self.referenced_target_ids:
            raise ValueError("live tutor turn must reference its primary target")
        if self.manual_memory_proposal and self.memory_write_allowed:
            raise ValueError("memory proposal cannot authorize a memory write")
        if self.ai_assist_mode == "openai_dry_run":
            if not self.ai_model or not self.ai_prompt_char_count:
                raise ValueError("OpenAI dry-run tutor turns require model and prompt metadata")
            if not self.ai_store_false:
                raise ValueError("OpenAI dry-run tutor turns require store:false")
        if self.realtime_voice_model != DEFAULT_REALTIME_MODEL:
            raise ValueError("live tutor realtime voice route must use gpt-realtime-2")
        if self.voice_output_mode in {"silent_visual", "text_chip", "memory_review"}:
            if not self.no_voice_back:
                raise ValueError("non-spoken voice routes must mark no_voice_back")
            if self.spoken_output_seconds_budgeted != 0:
                raise ValueError("non-spoken voice routes cannot budget spoken output")
        if self.voice_output_mode in {"spoken_brief", "spoken_detail"}:
            if self.no_voice_back or self.spoken_output_seconds_budgeted <= 0:
                raise ValueError("spoken voice routes require an audio-output budget")
        if REALTIME_VOICE_POLICY_REF not in self.policy_refs:
            raise ValueError("live tutor turn requires realtime voice policy ref")
        if LIVE_TUTOR_OVERLAY_POLICY_REF not in self.policy_refs:
            raise ValueError("live tutor turn requires policy ref")
        return self


class LiveTutorTurnReceipt(StrictModel):
    receipt_id: str = Field(min_length=1)
    turn_id: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    target_label: str = Field(min_length=1)
    intent_label: str = Field(min_length=1)
    pointer_referent: Literal["this", "that", "these", "none"]
    confidence: float = Field(ge=0, le=1)
    voice_gesture_type: VoiceGestureType
    voice_output_mode: VoiceOutputMode
    ai_assist_mode: Literal["local", "openai_dry_run"]
    user_visible_summary: str = Field(min_length=1, max_length=260)
    display_only: bool = True
    memory_write_allowed: bool = False
    raw_ref_retained: bool = False
    external_effect_executed: bool = False
    real_screen_capture_started: bool = False
    voice_capture_enabled: bool = False
    raw_payload_included: bool = False
    contains_user_utterance: bool = False
    contains_assistant_response: bool = False
    blocked_effects: list[str] = Field(default_factory=list)
    safety_flags: list[str] = Field(default_factory=list)
    policy_refs: list[str] = Field(
        default_factory=lambda: [
            LIVE_TUTOR_OVERLAY_POLICY_REF,
            REALTIME_VOICE_POLICY_REF,
            LIVE_TUTOR_BROWSER_PROOF_POLICY_REF,
        ]
    )

    @field_validator("user_visible_summary")
    @classmethod
    def reject_prohibited_summary(cls, value: str) -> str:
        if any(marker in value for marker in _PROHIBITED_MARKERS):
            raise ValueError("live tutor receipt cannot carry secret/raw markers")
        return value

    @model_validator(mode="after")
    def keep_receipt_redacted_and_non_mutating(self) -> LiveTutorTurnReceipt:
        if not self.display_only:
            raise ValueError("live tutor receipt must stay display-only")
        if self.memory_write_allowed or self.raw_ref_retained or self.external_effect_executed:
            raise ValueError("live tutor receipt cannot authorize writes, raw refs, or effects")
        if self.real_screen_capture_started or self.voice_capture_enabled:
            raise ValueError("live tutor receipt cannot start capture")
        if self.raw_payload_included or self.contains_user_utterance or self.contains_assistant_response:
            raise ValueError("live tutor receipt must be redacted")
        if missing := sorted(LIVE_TUTOR_REQUIRED_BLOCKED_EFFECTS.difference(self.blocked_effects)):
            raise ValueError(f"live tutor receipt missing blocked effects: {missing}")
        if LIVE_TUTOR_OVERLAY_POLICY_REF not in self.policy_refs:
            raise ValueError("live tutor receipt requires live tutor policy ref")
        if REALTIME_VOICE_POLICY_REF not in self.policy_refs:
            raise ValueError("live tutor receipt requires realtime voice policy ref")
        if LIVE_TUTOR_BROWSER_PROOF_POLICY_REF not in self.policy_refs:
            raise ValueError("live tutor receipt requires browser proof policy ref")
        return self


class LiveTutorReceiptReport(StrictModel):
    proof_id: str = LIVE_TUTOR_BROWSER_PROOF_ID
    policy_ref: str = LIVE_TUTOR_BROWSER_PROOF_POLICY_REF
    passed: bool
    generated_at: datetime
    turn_count: int = Field(ge=0)
    receipt_count: int = Field(ge=0)
    latest_target_label: str | None = None
    receipts: list[LiveTutorTurnReceipt] = Field(default_factory=list)
    memory_write_count: int = Field(ge=0)
    raw_ref_retained_count: int = Field(ge=0)
    external_effect_count: int = Field(ge=0)
    real_screen_capture_started: bool = False
    voice_capture_enabled: bool = False
    raw_payload_included: bool = False
    contains_user_utterances: bool = False
    contains_assistant_responses: bool = False
    blocked_effects: list[str] = Field(default_factory=list)
    safety_failures: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def keep_report_safe(self) -> LiveTutorReceiptReport:
        if self.receipt_count != len(self.receipts):
            raise ValueError("receipt_count must match receipts")
        if self.memory_write_count or self.raw_ref_retained_count or self.external_effect_count:
            raise ValueError("live tutor receipt report cannot include mutating effects")
        if self.real_screen_capture_started or self.voice_capture_enabled:
            raise ValueError("live tutor receipt report cannot include live capture")
        if self.raw_payload_included or self.contains_user_utterances or self.contains_assistant_responses:
            raise ValueError("live tutor receipt report must stay redacted")
        if missing := sorted(LIVE_TUTOR_REQUIRED_BLOCKED_EFFECTS.difference(self.blocked_effects)):
            raise ValueError(f"live tutor receipt report missing blocked effects: {missing}")
        return self


class LiveTutorDemoResult(StrictModel):
    proof_id: str = LIVE_TUTOR_OVERLAY_ID
    policy_ref: str = LIVE_TUTOR_OVERLAY_POLICY_REF
    passed: bool
    generated_at: datetime
    turn_count: int = Field(ge=0)
    target_ids: list[str] = Field(default_factory=list)
    cue_count: int = Field(ge=0)
    controlled_surface: bool
    display_only: bool
    memory_write_count: int = Field(ge=0)
    manual_memory_proposal_count: int = Field(default=0, ge=0)
    raw_ref_retained_count: int = Field(ge=0)
    external_effect_count: int = Field(ge=0)
    real_screen_capture_started: bool = False
    voice_capture_enabled: bool = False
    openai_draft_turn_count: int = Field(default=0, ge=0)
    openai_store_false: bool = True
    realtime_voice_turn_count: int = Field(default=0, ge=0)
    spoken_output_turn_count: int = Field(default=0, ge=0)
    text_only_voice_turn_count: int = Field(default=0, ge=0)
    action_only_voice_turn_count: int = Field(default=0, ge=0)
    selection_voice_turn_count: int = Field(default=0, ge=0)
    no_voice_back_count: int = Field(default=0, ge=0)
    prohibited_marker_count: int = Field(ge=0)
    safety_failures: list[str] = Field(default_factory=list)


class LiveTutorDashboardPanel(StrictModel):
    panel_id: str = LIVE_TUTOR_OVERLAY_ID
    title: str = "Live Tutor Overlay"
    summary: str = Field(min_length=1)
    demo_url: str = "http://127.0.0.1:8797/"
    smoke_command: str = "uv run cortex-live-tutor-demo --server-smoke --json"
    browser_replay_smoke_command: str = (
        "uv run cortex-live-tutor-demo --browser-replay-smoke --json"
    )
    receipt_endpoint: str = "/tutor/receipts"
    latest_targets: list[str] = Field(default_factory=list)
    turn_count: int = Field(ge=0)
    cue_count: int = Field(ge=0)
    manual_memory_proposal_count: int = Field(default=0, ge=0)
    display_only: bool = True
    controlled_surface: bool = True
    memory_write_allowed: bool = False
    raw_ref_retained: bool = False
    external_effect_enabled: bool = False
    real_screen_capture_started: bool = False
    voice_capture_enabled: bool = False
    openai_draft_ready: bool = True
    openai_draft_turn_count: int = Field(default=0, ge=0)
    openai_store_false: bool = True
    realtime_voice_ready: bool = True
    realtime_voice_model: str = DEFAULT_REALTIME_MODEL
    voice_default_output: str = "text unless gesture asks for voice"
    voice_gestures: list[str] = Field(default_factory=list)
    voice_output_modes: list[str] = Field(default_factory=list)
    no_voice_back_count: int = Field(default=0, ge=0)
    raw_payload_included: bool = False
    blocked_effects: list[str] = Field(default_factory=list)
    policy_refs: list[str] = Field(
        default_factory=lambda: [LIVE_TUTOR_OVERLAY_POLICY_REF, REALTIME_VOICE_POLICY_REF]
    )

    @model_validator(mode="after")
    def keep_dashboard_panel_safe(self) -> LiveTutorDashboardPanel:
        if not self.display_only or not self.controlled_surface:
            raise ValueError("live tutor dashboard panel must be controlled and display-only")
        if self.memory_write_allowed or self.raw_ref_retained or self.external_effect_enabled:
            raise ValueError("live tutor dashboard panel cannot enable memory/raw/external effects")
        if self.real_screen_capture_started or self.voice_capture_enabled:
            raise ValueError("live tutor dashboard panel cannot enable screen or voice capture")
        if not self.openai_draft_ready or not self.openai_store_false:
            raise ValueError("live tutor OpenAI draft panel must stay safe and store:false")
        if not self.realtime_voice_ready or self.realtime_voice_model != DEFAULT_REALTIME_MODEL:
            raise ValueError("live tutor realtime voice panel must stay on gpt-realtime-2")
        if self.raw_payload_included:
            raise ValueError("live tutor dashboard panel cannot include raw payloads")
        if missing := sorted(LIVE_TUTOR_REQUIRED_BLOCKED_EFFECTS.difference(self.blocked_effects)):
            raise ValueError(f"live tutor dashboard panel missing blocked effects: {missing}")
        if LIVE_TUTOR_OVERLAY_POLICY_REF not in self.policy_refs:
            raise ValueError("live tutor dashboard panel requires policy ref")
        return self


class LiveTutorQuestionInput(StrictModel):
    user_utterance: str = Field(min_length=1, max_length=240)
    active_page: str = Field(default="edit", min_length=1, max_length=40)
    ai_mode: Literal["local", "openai_dry_run"] = "local"
    voice_gesture_type: VoiceGestureType = "single_click_context"
    pointed_target_id: str | None = None
    previous_target_id: str | None = None
    selected_target_ids: list[str] = Field(default_factory=list, max_length=4)
    pointer_coordinate_space: Literal["canonical_surface", "client_surface_css"] = (
        "canonical_surface"
    )
    pointer_x: float | None = Field(default=None, ge=0, le=10000)
    pointer_y: float | None = Field(default=None, ge=0, le=10000)
    client_surface_width: float | None = Field(default=None, ge=1, le=10000)
    client_surface_height: float | None = Field(default=None, ge=1, le=10000)

    @field_validator("user_utterance")
    @classmethod
    def reject_prohibited_markers(cls, value: str) -> str:
        if any(marker in value for marker in _PROHIBITED_MARKERS):
            raise ValueError("live tutor question cannot carry secret/raw/prompt-injection markers")
        return value

    @model_validator(mode="after")
    def keep_pointer_coordinate_space_complete(self) -> LiveTutorQuestionInput:
        if self.pointer_coordinate_space == "client_surface_css" and (
            self.pointer_x is not None or self.pointer_y is not None
        ):
            if self.client_surface_width is None or self.client_surface_height is None:
                raise ValueError("client pointer coordinates require client surface dimensions")
        return self


class LiveTutorDemoRejected(ValueError):
    def __init__(self, *, error: str, status: HTTPStatus, message: str) -> None:
        self.error = error
        self.status = status
        self.message = message
        super().__init__(message)


class LiveTutorDemoSession:
    """Thread-safe turn store for the controlled localhost tutor demo."""

    def __init__(self) -> None:
        self._turns: list[LiveTutorTurn] = []
        self._lock = threading.Lock()
        self.rejected_turn_count = 0

    def answer(self, payload: Mapping[str, Any]) -> LiveTutorTurn:
        question = LiveTutorQuestionInput.model_validate(payload)
        surface = build_safe_creative_demo_surface(active_page=question.active_page)
        pointer_state, normalized_pointer = _pointer_state_from_question(question, surface=surface)
        with self._lock:
            sequence = len(self._turns) + 1
            turn = resolve_live_tutor_turn(
                question.user_utterance,
                surface=surface,
                pointer_state=pointer_state,
                sequence=sequence,
                ai_mode=question.ai_mode,
                voice_gesture_type=question.voice_gesture_type,
            )
            if normalized_pointer is not None:
                turn = _append_pointer_normalization_flags(turn, normalized_pointer)
            self._turns.append(turn)
            return turn

    def record_rejection(self) -> None:
        with self._lock:
            self.rejected_turn_count += 1

    def result(self) -> LiveTutorDemoResult:
        with self._lock:
            turns = list(self._turns)
        return _result_from_turns(turns, require_core_targets=False)

    def receipts(self) -> LiveTutorReceiptReport:
        with self._lock:
            turns = list(self._turns)
        return _receipt_report_from_turns(turns)


class LiveTutorDemoHandler(BaseHTTPRequestHandler):
    server_version = "CortexLiveTutorDemo/0.1"

    def do_GET(self) -> None:  # noqa: N802
        if not self._request_is_loopback():
            self._write_error(
                "non_loopback_request",
                HTTPStatus.FORBIDDEN,
                "live tutor demo serves localhost requests only",
            )
            return
        path = urlparse(self.path).path
        if path == "/":
            path = "/index.html"
        if path == "/results":
            self._write_json(self._session().result().model_dump(mode="json"))
            return
        if path == "/tutor/receipts":
            error = self._receipt_request_error()
            if error is not None:
                code, status, message = error
                self._write_error(code, status, message)
                return
            self._write_json(self._session().receipts().model_dump(mode="json"))
            return
        static_path = (UI_ROOT / path.removeprefix("/")).resolve()
        if not static_path.is_file() or UI_ROOT.resolve() not in static_path.parents:
            self.send_error(HTTPStatus.NOT_FOUND, "not found")
            return
        content_type = mimetypes.guess_type(static_path.name)[0] or "application/octet-stream"
        data = self._static_bytes(static_path)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self._write_security_headers()
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self) -> None:  # noqa: N802
        if urlparse(self.path).path != "/tutor/turn":
            self.send_error(HTTPStatus.NOT_FOUND, "not found")
            return
        error = self._turn_request_error()
        if error is not None:
            code, status, message = error
            self._session().record_rejection()
            self._write_error(code, status, message)
            return
        content_length = int(self.headers.get("Content-Length", "0") or "0")
        if content_length > 32 * 1024:
            self._session().record_rejection()
            self._write_error(
                "payload_too_large",
                HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                "live tutor request payload is too large",
            )
            return
        try:
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("payload must be object")
            turn = self._session().answer(payload)
        except (ValueError, ValidationError, json.JSONDecodeError, UnicodeDecodeError) as error:
            self._session().record_rejection()
            self._write_error("invalid_tutor_turn", HTTPStatus.UNPROCESSABLE_ENTITY, str(error))
            return
        self._write_json(turn.model_dump(mode="json"))

    def log_message(self, _format: str, *_args: Any) -> None:
        return

    def _session(self) -> LiveTutorDemoSession:
        if not isinstance(self.server, LiveTutorDemoHTTPServer):
            raise RuntimeError("live tutor demo server missing session")
        return self.server.session

    def _server(self) -> "LiveTutorDemoHTTPServer":
        if not isinstance(self.server, LiveTutorDemoHTTPServer):
            raise RuntimeError("live tutor demo server missing typed server")
        return self.server

    def _static_bytes(self, static_path: Path) -> bytes:
        text_suffixes = {".html", ".js", ".css"}
        if static_path.suffix not in text_suffixes:
            return static_path.read_bytes()
        text = static_path.read_text(encoding="utf-8")
        if static_path.name == "index.html":
            text = text.replace(LIVE_TUTOR_TOKEN_PLACEHOLDER, self._server().demo_token)
        return text.encode("utf-8")

    def _request_is_loopback(self) -> bool:
        client_host = self.client_address[0] if self.client_address else ""
        host_header = self.headers.get("Host", "")
        return _is_loopback_host(client_host) and _is_loopback_host(_header_hostname(host_header))

    def _turn_request_error(self) -> tuple[str, HTTPStatus, str] | None:
        if not self._request_is_loopback():
            return (
                "non_loopback_request",
                HTTPStatus.FORBIDDEN,
                "live tutor demo accepts localhost requests only",
            )
        content_type = self.headers.get("Content-Type", "")
        if content_type.split(";", 1)[0].strip().lower() != "application/json":
            return (
                "unsupported_content_type",
                HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
                "live tutor turns must be application/json",
            )
        origin = self.headers.get("Origin")
        if not origin or not _is_local_url(origin):
            return (
                "invalid_origin",
                HTTPStatus.FORBIDDEN,
                "live tutor turns require a localhost origin",
            )
        token = self.headers.get(LIVE_TUTOR_TOKEN_HEADER, "")
        if not secrets.compare_digest(token, self._server().demo_token):
            return (
                "invalid_demo_token",
                HTTPStatus.FORBIDDEN,
                "live tutor token is missing or invalid",
            )
        return None

    def _receipt_request_error(self) -> tuple[str, HTTPStatus, str] | None:
        if not self._request_is_loopback():
            return (
                "non_loopback_request",
                HTTPStatus.FORBIDDEN,
                "live tutor receipts accept localhost requests only",
            )
        token = self.headers.get(LIVE_TUTOR_TOKEN_HEADER, "")
        if not secrets.compare_digest(token, self._server().demo_token):
            return (
                "invalid_demo_token",
                HTTPStatus.FORBIDDEN,
                "live tutor receipt token is missing or invalid",
            )
        return None

    def _write_json(
        self,
        payload: Mapping[str, Any],
        *,
        status: HTTPStatus = HTTPStatus.OK,
    ) -> None:
        data = json.dumps(payload, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self._write_security_headers()
        self.end_headers()
        self.wfile.write(data)

    def _write_error(self, error: str, status: HTTPStatus, message: str) -> None:
        self._write_json(
            {
                "error": error,
                "message": message,
                "policy_ref": LIVE_TUTOR_OVERLAY_POLICY_REF,
            },
            status=status,
        )

    def _write_security_headers(self) -> None:
        for name, value in LIVE_TUTOR_SECURITY_HEADERS.items():
            self.send_header(name, value)


class LiveTutorDemoHTTPServer(ThreadingHTTPServer):
    def __init__(
        self,
        server_address: tuple[str, int],
        session: LiveTutorDemoSession,
        demo_token: str,
    ) -> None:
        super().__init__(server_address, LiveTutorDemoHandler)
        self.session = session
        self.demo_token = demo_token


@dataclass
class RunningLiveTutorDemo:
    server: LiveTutorDemoHTTPServer
    thread: threading.Thread

    @property
    def base_url(self) -> str:
        host, port = self.server.server_address
        return f"http://{host}:{port}"

    def stop(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def result(self) -> LiveTutorDemoResult:
        return self.server.session.result()


def build_safe_creative_demo_surface(
    *,
    active_page: str = "edit",
) -> SafeCreativeDemoSurface:
    targets = [
        DemoTarget(
            target_id="media_bin",
            label="Media Bin",
            role="asset_library",
            region="left rail",
            plain_description="Project clips, audio, and assets live here before they are added to the timeline.",
            x=28,
            y=118,
            width=250,
            height=318,
        ),
        DemoTarget(
            target_id="timeline",
            label="Timeline",
            role="timeline",
            region="bottom rail",
            plain_description="The sequence of clips and audio the editor is currently assembling.",
            x=312,
            y=676,
            width=928,
            height=188,
        ),
        DemoTarget(
            target_id="color_page_button",
            label="Color Page",
            role="workspace_switcher",
            region="bottom navigation",
            plain_description="The workspace switcher that opens color grading tools.",
            x=646,
            y=902,
            width=72,
            height=42,
            state="selected" if active_page == "color" else "idle",
        ),
        DemoTarget(
            target_id="node_graph",
            label="Node Graph",
            role="color_workspace",
            region="upper right",
            plain_description="A visual chain of color-correction nodes for the selected clip.",
            x=1028,
            y=142,
            width=340,
            height=238,
        ),
        DemoTarget(
            target_id="lut_menu",
            label="LUT Menu",
            role="color_tool_menu",
            region="right inspector",
            plain_description="A menu for previewing and applying look presets. It should be reviewed before use.",
            x=1178,
            y=424,
            width=172,
            height=48,
        ),
        DemoTarget(
            target_id="inspector",
            label="Inspector",
            role="settings_panel",
            region="right rail",
            plain_description="A settings panel for checking and adjusting the selected clip.",
            x=1118,
            y=494,
            width=250,
            height=250,
        ),
    ]
    return SafeCreativeDemoSurface(
        active_page=active_page,
        target_count=len(targets),
        targets=targets,
    )


def normalize_client_pointer_to_surface(
    *,
    pointer_x: float | None,
    pointer_y: float | None,
    surface: SafeCreativeDemoSurface | None = None,
    coordinate_space: Literal["canonical_surface", "client_surface_css"] = "canonical_surface",
    client_surface_width: float | None = None,
    client_surface_height: float | None = None,
) -> LiveTutorNormalizedPointer | None:
    if pointer_x is None or pointer_y is None:
        return None
    surface = surface or build_safe_creative_demo_surface()
    if coordinate_space == "client_surface_css":
        if client_surface_width is None or client_surface_height is None:
            raise ValueError("client pointer coordinates require client surface dimensions")
        clamped_source_x = min(max(pointer_x, 0), client_surface_width)
        clamped_source_y = min(max(pointer_y, 0), client_surface_height)
        canonical_x = (clamped_source_x / client_surface_width) * surface.viewport_width
        canonical_y = (clamped_source_y / client_surface_height) * surface.viewport_height
        was_clamped = clamped_source_x != pointer_x or clamped_source_y != pointer_y
    else:
        canonical_x = min(max(pointer_x, 0), surface.viewport_width)
        canonical_y = min(max(pointer_y, 0), surface.viewport_height)
        was_clamped = canonical_x != pointer_x or canonical_y != pointer_y

    canonical_x = min(max(canonical_x, 0), surface.viewport_width)
    canonical_y = min(max(canonical_y, 0), surface.viewport_height)
    return LiveTutorNormalizedPointer(
        source_coordinate_space=coordinate_space,
        pointer_x=round(canonical_x, 2),
        pointer_y=round(canonical_y, 2),
        client_surface_width=client_surface_width,
        client_surface_height=client_surface_height,
        canonical_surface_width=surface.viewport_width,
        canonical_surface_height=surface.viewport_height,
        client_pointer_was_clamped=was_clamped,
    )


def resolve_live_tutor_turn(
    user_utterance: str,
    *,
    surface: SafeCreativeDemoSurface | None = None,
    pointer_state: LiveTutorPointerState | None = None,
    session_id: str = "live_tutor_demo_session",
    sequence: int = 1,
    ai_mode: Literal["local", "openai_dry_run"] = "local",
    voice_gesture_type: VoiceGestureType = "single_click_context",
) -> LiveTutorTurn:
    surface = surface or build_safe_creative_demo_surface()
    pointer_state = pointer_state or LiveTutorPointerState()
    target_id, intent_label, response, next_action, confidence, referent, referenced_ids = _resolve_intent(
        user_utterance,
        surface=surface,
        pointer_state=pointer_state,
    )
    target = surface.target_by_id(target_id)
    proposal = (
        _build_manual_memory_proposal(target, sequence=sequence)
        if intent_label == "propose_manual_memory"
        else None
    )
    cue = SpatialTutorCue(
        cue_id=f"cue_live_tutor_{sequence:03d}",
        target_id=target.target_id,
        target_label=target.label,
        x=target.center_x,
        y=target.center_y,
        viewport_width=surface.viewport_width,
        viewport_height=surface.viewport_height,
        allowed_effects=[
            "read_controlled_demo_state",
            "render_shadow_tutor_cursor",
            "render_target_highlight",
            "render_instruction_bubble",
            "write_safe_demo_receipt",
        ],
        blocked_effects=sorted(LIVE_TUTOR_REQUIRED_BLOCKED_EFFECTS),
    )
    companion_state = _companion_state_for_intent(intent_label, target=target)
    turn = LiveTutorTurn(
        turn_id=f"live_tutor_turn_{sequence:03d}",
        session_id=session_id,
        user_utterance=user_utterance,
        app_surface=surface.app_label,
        screen_state_ref=f"controlled_dom://live-tutor-demo/{surface.surface_id}",
        intent_label=intent_label,
        target_id=target.target_id,
        target_label=target.label,
        referenced_target_ids=referenced_ids,
        pointer_referent=referent,
        target_coordinates=cue,
        assistant_response=response,
        micro_steps=_micro_steps_for_intent(intent_label, target=target, surface=surface),
        user_readable_receipt=_user_readable_receipt(
            intent_label=intent_label,
            target=target,
            proposal_created=proposal is not None,
        ),
        companion_state=companion_state,
        confidence=confidence,
        next_user_action=next_action,
        manual_memory_proposal=proposal,
        safety_flags=[
            "controlled_demo_surface",
            "display_only_pointer",
            "pointer_target_context",
            "no_real_screen_capture",
            "no_voice_capture",
            "no_memory_write",
            "no_external_effects",
        ],
    )
    turn = _apply_voice_pointer_route_to_turn(
        turn,
        user_utterance=user_utterance,
        target=target,
        pointer_state=pointer_state,
        referenced_ids=referenced_ids,
        voice_gesture_type=voice_gesture_type,
    )
    if ai_mode == "openai_dry_run":
        return _apply_openai_dry_run_to_turn(
            turn,
            user_utterance=user_utterance,
            target=target,
            surface=surface,
        )
    return turn


def _apply_voice_pointer_route_to_turn(
    turn: LiveTutorTurn,
    *,
    user_utterance: str,
    target: DemoTarget,
    pointer_state: LiveTutorPointerState,
    referenced_ids: list[str],
    voice_gesture_type: VoiceGestureType,
) -> LiveTutorTurn:
    gesture = build_pointer_gesture(
        gesture_type=voice_gesture_type,
        target_id=target.target_id,
        target_label=target.label,
        pointer_x=pointer_state.pointer_x if pointer_state.pointer_x is not None else target.center_x,
        pointer_y=pointer_state.pointer_y if pointer_state.pointer_y is not None else target.center_y,
        transcript_preview=user_utterance,
        selected_target_ids=referenced_ids,
    )
    decision = route_voice_output(gesture)
    payload = turn.model_dump(mode="python")
    payload.update(
        {
            "voice_gesture_type": gesture.gesture_type,
            "voice_output_mode": decision.output_mode,
            "voice_route_reason": decision.reason,
            "realtime_voice_model": DEFAULT_REALTIME_MODEL,
            "realtime_voice_ready": True,
            "voice_cost_guard_id": REALTIME_COST_GUARD_ID,
            "voice_transcript_source": (
                "synthetic_voice"
                if gesture.gesture_type
                in {
                    "triple_click_voice_dialogue",
                    "press_hold_text_reply",
                    "press_hold_action_only",
                }
                else "typed_or_synthetic"
            ),
            "spoken_output_seconds_budgeted": decision.spoken_output_seconds_budgeted,
            "no_voice_back": decision.no_voice_back,
            "safety_flags": [
                *turn.safety_flags,
                "gpt_realtime_2_ready",
                "ephemeral_client_secret_required",
                f"voice_gesture:{gesture.gesture_type}",
                f"voice_output:{decision.output_mode}",
                "voice_default_text_unless_gesture_requests_speech",
                "cost_guard_active",
                "no_live_mic_in_safe_demo",
            ],
        }
    )
    if decision.output_mode == "spoken_brief":
        payload.update(
            {
                "companion_state": LiveTutorCompanionState(
                    mode=turn.companion_state.mode,
                    label=f"Voice ready for {target.label}",
                    safety_caption="Triple-click route: brief spoken answer, gated by cost guard.",
                ),
                "user_readable_receipt": (
                    f"Saw {target.label}, routed triple-click voice to a brief spoken answer, "
                    "and opened no mic in this safe demo."
                ),
            }
        )
    elif decision.output_mode == "text_chip":
        payload.update(
            {
                "companion_state": LiveTutorCompanionState(
                    mode=turn.companion_state.mode,
                    label=f"Text reply for {target.label}",
                    safety_caption="Voice-in, text-out route. No voice back.",
                ),
            }
        )
    elif decision.output_mode == "silent_visual":
        payload.update(
            {
                "companion_state": LiveTutorCompanionState(
                    mode=turn.companion_state.mode,
                    label=f"Silent cue for {target.label}",
                    safety_caption="Action-only route: visual pointer cue, no voice back.",
                ),
                "user_readable_receipt": (
                    f"Saw {target.label}, showed the pointer cue, and stayed silent."
                ),
            }
        )
    elif decision.output_mode == "memory_review":
        payload.update(
            {
                "companion_state": LiveTutorCompanionState(
                    mode="review_required",
                    label=f"Review memory for {target.label}",
                    safety_caption="Memory route stays review-only; nothing is saved.",
                ),
            }
        )
    return LiveTutorTurn.model_validate(payload)


def _apply_openai_dry_run_to_turn(
    turn: LiveTutorTurn,
    *,
    user_utterance: str,
    target: DemoTarget,
    surface: SafeCreativeDemoSurface,
) -> LiveTutorTurn:
    from cortex_memory_os.live_openai_tutor import (
        dry_run_openai_tutor_draft,
        openai_tutor_request_from_target,
    )

    request = openai_tutor_request_from_target(
        user_utterance=user_utterance,
        target=target,
        active_page=surface.active_page,
    )
    draft = dry_run_openai_tutor_draft(request)
    payload = turn.model_dump(mode="python")
    payload.update(
        {
            "assistant_response": draft.assistant_response,
            "micro_steps": draft.micro_steps,
            "confidence": min(max(draft.confidence, turn.confidence - 0.04), 0.92),
            "user_readable_receipt": (
                "AI draft used controlled target facts only; no click, capture, raw ref, "
                "or memory write happened."
            ),
            "companion_state": LiveTutorCompanionState(
                mode=turn.companion_state.mode,
                label=f"AI draft for {target.label}",
                safety_caption="OpenAI dry-run: store:false, controlled facts only.",
            ),
            "next_user_action": "Review the AI draft, then click the real app yourself.",
            "safety_flags": [
                *turn.safety_flags,
                "openai_dry_run",
                "store_false",
                "controlled_target_facts_only",
                "no_screenshots_sent",
                "no_microphone_sent",
            ],
            "ai_assist_mode": "openai_dry_run",
            "ai_model": draft.model,
            "ai_store_false": draft.store_false,
            "ai_prompt_char_count": draft.prompt_char_count,
        }
    )
    return LiveTutorTurn.model_validate(payload)


def run_live_tutor_demo_smoke() -> LiveTutorDemoResult:
    surface = build_safe_creative_demo_surface()
    requests: list[tuple[str, LiveTutorPointerState | None, VoiceGestureType]] = [
        ("How do I start color grading?", None, "triple_click_voice_dialogue"),
        ("Where is the node graph?", None, "press_hold_text_reply"),
        ("How do I add a LUT?", None, "press_hold_action_only"),
        (
            "Explain this",
            LiveTutorPointerState(current_target_id="lut_menu", referent_phrase="this"),
            "single_click_context",
        ),
        (
            "Remember this",
            LiveTutorPointerState(
                current_target_id="node_graph",
                previous_target_id="lut_menu",
                selected_target_ids=["lut_menu", "node_graph"],
                referent_phrase="this",
            ),
            "drag_select_targets",
        ),
    ]
    turns = [
        resolve_live_tutor_turn(
            utterance,
            surface=surface,
            pointer_state=pointer_state,
            sequence=index,
            voice_gesture_type=voice_gesture_type,
        )
        for index, (utterance, pointer_state, voice_gesture_type) in enumerate(requests, start=1)
    ]
    return _result_from_turns(turns, require_core_targets=True)


def run_live_tutor_server_smoke() -> LiveTutorDemoResult:
    demo = start_live_tutor_demo(port=0)
    try:
        index_status, _, index_body = _http_demo_request(demo.base_url, "GET", "/")
        token = _extract_demo_token(index_body)
        for sequence, utterance in enumerate(
            [
                "How do I start color grading?",
                "Where is the node graph?",
                "How do I add a LUT?",
            ],
            start=1,
        ):
            status, _, _ = _http_demo_request(
                demo.base_url,
                "POST",
                "/tutor/turn",
                body=json.dumps(
                    {
                        "user_utterance": utterance,
                        "active_page": "color" if sequence > 1 else "edit",
                        "pointed_target_id": "lut_menu" if "LUT" in utterance else None,
                        "ai_mode": "openai_dry_run" if sequence == 3 else "local",
                        "voice_gesture_type": (
                            "triple_click_voice_dialogue"
                            if sequence == 1
                            else "press_hold_text_reply"
                            if sequence == 2
                            else "press_hold_action_only"
                        ),
                    }
                ),
                headers={
                    "Content-Type": "application/json",
                    "Origin": demo.base_url,
                    LIVE_TUTOR_TOKEN_HEADER: token,
                },
            )
            if status != HTTPStatus.OK:
                raise LiveTutorDemoRejected(
                    error="server_smoke_failed",
                    status=HTTPStatus(status),
                    message=f"live tutor server smoke turn failed with {status}",
                )
        result_status, _, result_body = _http_demo_request(demo.base_url, "GET", "/results")
        if index_status != HTTPStatus.OK or result_status != HTTPStatus.OK:
            raise LiveTutorDemoRejected(
                error="server_smoke_failed",
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
                message="live tutor server smoke failed to load index or results",
            )
        return LiveTutorDemoResult.model_validate_json(result_body)
    finally:
        demo.stop()


def run_live_tutor_browser_replay_smoke() -> LiveTutorReceiptReport:
    demo = start_live_tutor_demo(port=0)
    try:
        index_status, _, index_body = _http_demo_request(demo.base_url, "GET", "/")
        token = _extract_demo_token(index_body)
        if index_status != HTTPStatus.OK:
            raise LiveTutorDemoRejected(
                error="browser_replay_smoke_failed",
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
                message="live tutor browser replay smoke failed to load index",
            )
        requests = [
            {
                "user_utterance": "How do I start color grading?",
                "active_page": "edit",
                "voice_gesture_type": "triple_click_voice_dialogue",
                "pointer_coordinate_space": "client_surface_css",
                "pointer_x": 406,
                "pointer_y": 1120,
                "client_surface_width": 1100,
                "client_surface_height": 1200,
            },
            {
                "user_utterance": "Tell me what this does, but text only.",
                "active_page": "color",
                "pointed_target_id": "node_graph",
                "previous_target_id": "color_page_button",
                "voice_gesture_type": "press_hold_text_reply",
                "pointer_coordinate_space": "client_surface_css",
                "pointer_x": 1016,
                "pointer_y": 318,
                "client_surface_width": 1100,
                "client_surface_height": 1200,
            },
            {
                "user_utterance": "Show me the next action, no voice back.",
                "active_page": "color",
                "pointed_target_id": "lut_menu",
                "previous_target_id": "node_graph",
                "voice_gesture_type": "press_hold_action_only",
                "pointer_coordinate_space": "client_surface_css",
                "pointer_x": 9999,
                "pointer_y": 9999,
                "client_surface_width": 1100,
                "client_surface_height": 1200,
            },
        ]
        for payload in requests:
            status, _, body = _http_demo_request(
                demo.base_url,
                "POST",
                "/tutor/turn",
                body=json.dumps(payload),
                headers={
                    "Content-Type": "application/json",
                    "Origin": demo.base_url,
                    LIVE_TUTOR_TOKEN_HEADER: token,
                },
            )
            if status != HTTPStatus.OK:
                raise LiveTutorDemoRejected(
                    error="browser_replay_smoke_failed",
                    status=HTTPStatus(status),
                    message=f"live tutor browser replay smoke failed: {body}",
                )
        receipt_status, _, receipt_body = _http_demo_request(
            demo.base_url,
            "GET",
            "/tutor/receipts",
            headers={LIVE_TUTOR_TOKEN_HEADER: token},
        )
        if receipt_status != HTTPStatus.OK:
            raise LiveTutorDemoRejected(
                error="browser_replay_smoke_failed",
                status=HTTPStatus(receipt_status),
                message=f"live tutor receipt endpoint failed: {receipt_body}",
            )
        return LiveTutorReceiptReport.model_validate_json(receipt_body)
    finally:
        demo.stop()


def build_live_tutor_dashboard_panel(
    result: LiveTutorDemoResult | None = None,
) -> LiveTutorDashboardPanel:
    result = result or run_live_tutor_demo_smoke()
    return LiveTutorDashboardPanel(
        summary=(
            "Pointer-first tutor demo: Cortex follows the user's pointer, resolves "
            "the current target behind 'this' or 'that', answers beside the work, "
            "and keeps memory as a reviewed proposal instead of an automatic write."
        ),
        latest_targets=result.target_ids[-3:],
        turn_count=result.turn_count,
        cue_count=result.cue_count,
        manual_memory_proposal_count=result.manual_memory_proposal_count,
        openai_draft_turn_count=result.openai_draft_turn_count,
        openai_store_false=result.openai_store_false,
        realtime_voice_ready=result.realtime_voice_turn_count == result.turn_count,
        realtime_voice_model=DEFAULT_REALTIME_MODEL,
        voice_gestures=[
            "triple_click_voice_dialogue",
            "press_hold_text_reply",
            "press_hold_action_only",
            "drag_select_targets",
        ],
        voice_output_modes=["spoken_brief", "text_chip", "silent_visual", "memory_review"],
        no_voice_back_count=result.no_voice_back_count,
        display_only=result.display_only,
        controlled_surface=result.controlled_surface,
        memory_write_allowed=result.memory_write_count > 0,
        raw_ref_retained=result.raw_ref_retained_count > 0,
        external_effect_enabled=result.external_effect_count > 0,
        real_screen_capture_started=result.real_screen_capture_started,
        voice_capture_enabled=result.voice_capture_enabled,
        blocked_effects=sorted(LIVE_TUTOR_REQUIRED_BLOCKED_EFFECTS),
    )


def start_live_tutor_demo(
    *,
    host: str = DEFAULT_LIVE_TUTOR_HOST,
    port: int = DEFAULT_LIVE_TUTOR_PORT,
) -> RunningLiveTutorDemo:
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("live tutor demo must bind localhost")
    session = LiveTutorDemoSession()
    server = LiveTutorDemoHTTPServer(
        (host, port),
        session,
        demo_token=secrets.token_urlsafe(24),
    )
    thread = threading.Thread(target=server.serve_forever, name="cortex-live-tutor-demo")
    thread.daemon = True
    thread.start()
    return RunningLiveTutorDemo(server=server, thread=thread)


def live_tutor_payload_is_safe(payload: Mapping[str, Any] | str) -> bool:
    text = payload if isinstance(payload, str) else json.dumps(payload, sort_keys=True)
    return not any(marker in text for marker in _PROHIBITED_MARKERS)


def _result_from_turns(
    turns: list[LiveTutorTurn],
    *,
    require_core_targets: bool,
) -> LiveTutorDemoResult:
    payload = "\n".join(turn.model_dump_json() for turn in turns)
    prohibited_marker_count = sum(1 for marker in _PROHIBITED_MARKERS if marker in payload)
    checks = {
        "turn_count": len(turns) >= 3,
        "controlled_surface": bool(turns),
        "display_only": all(turn.display_only and turn.target_coordinates.display_only for turn in turns),
        "known_targets": (
            {turn.target_id for turn in turns} >= {"color_page_button", "node_graph", "lut_menu"}
            if require_core_targets
            else all(turn.target_id for turn in turns)
        ),
        "pointer_referents": any(turn.pointer_referent in {"this", "that", "these"} for turn in turns),
        "no_memory_writes": all(not turn.memory_write_allowed for turn in turns),
        "no_raw_refs": all(not turn.raw_ref_retained for turn in turns),
        "no_external_effects": all(not turn.external_effect_executed for turn in turns),
        "no_live_capture": all(
            not turn.real_screen_capture_started and not turn.voice_capture_enabled
            for turn in turns
        ),
        "openai_store_false": all(turn.ai_store_false for turn in turns),
        "realtime_voice_ready": all(
            turn.realtime_voice_ready
            and turn.realtime_voice_model == DEFAULT_REALTIME_MODEL
            and turn.voice_cost_guard_id == REALTIME_COST_GUARD_ID
            for turn in turns
        ),
        "voice_output_routes": (
            {"text_chip", "memory_review"}.issubset({turn.voice_output_mode for turn in turns})
            if require_core_targets
            else all(turn.voice_output_mode for turn in turns)
        ),
        "manual_memory_review": all(
            proposal.durable_write_performed is False
            and proposal.user_confirmation_required is True
            for turn in turns
            for proposal in ([turn.manual_memory_proposal] if turn.manual_memory_proposal else [])
        ),
        "no_prohibited_markers": prohibited_marker_count == 0,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return LiveTutorDemoResult(
        passed=not failures,
        generated_at=datetime.now(UTC),
        turn_count=len(turns),
        target_ids=[turn.target_id for turn in turns],
        cue_count=sum(int(turn.target_coordinates.display_only) for turn in turns),
        controlled_surface=checks["controlled_surface"],
        display_only=checks["display_only"],
        memory_write_count=sum(int(turn.memory_write_allowed) for turn in turns),
        manual_memory_proposal_count=sum(int(bool(turn.manual_memory_proposal)) for turn in turns),
        raw_ref_retained_count=sum(int(turn.raw_ref_retained) for turn in turns),
        external_effect_count=sum(int(turn.external_effect_executed) for turn in turns),
        real_screen_capture_started=any(turn.real_screen_capture_started for turn in turns),
        voice_capture_enabled=any(turn.voice_capture_enabled for turn in turns),
        openai_draft_turn_count=sum(
            int(turn.ai_assist_mode == "openai_dry_run") for turn in turns
        ),
        openai_store_false=all(turn.ai_store_false for turn in turns),
        realtime_voice_turn_count=sum(int(turn.realtime_voice_ready) for turn in turns),
        spoken_output_turn_count=sum(
            int(turn.voice_output_mode in {"spoken_brief", "spoken_detail"}) for turn in turns
        ),
        text_only_voice_turn_count=sum(int(turn.voice_output_mode == "text_chip") for turn in turns),
        action_only_voice_turn_count=sum(
            int(turn.voice_output_mode == "silent_visual") for turn in turns
        ),
        selection_voice_turn_count=sum(
            int(turn.voice_gesture_type == "drag_select_targets") for turn in turns
        ),
        no_voice_back_count=sum(int(turn.no_voice_back) for turn in turns),
        prohibited_marker_count=prohibited_marker_count,
        safety_failures=failures,
    )


def _receipt_from_turn(turn: LiveTutorTurn) -> LiveTutorTurnReceipt:
    return LiveTutorTurnReceipt(
        receipt_id=f"receipt_{turn.turn_id}",
        turn_id=turn.turn_id,
        target_id=turn.target_id,
        target_label=turn.target_label,
        intent_label=turn.intent_label,
        pointer_referent=turn.pointer_referent,
        confidence=turn.confidence,
        voice_gesture_type=turn.voice_gesture_type,
        voice_output_mode=turn.voice_output_mode,
        ai_assist_mode=turn.ai_assist_mode,
        user_visible_summary=turn.user_readable_receipt,
        display_only=turn.display_only and turn.target_coordinates.display_only,
        memory_write_allowed=turn.memory_write_allowed,
        raw_ref_retained=turn.raw_ref_retained,
        external_effect_executed=turn.external_effect_executed,
        real_screen_capture_started=turn.real_screen_capture_started,
        voice_capture_enabled=turn.voice_capture_enabled,
        blocked_effects=sorted(set(turn.target_coordinates.blocked_effects)),
        safety_flags=sorted(set(turn.safety_flags)),
    )


def _receipt_report_from_turns(turns: list[LiveTutorTurn]) -> LiveTutorReceiptReport:
    receipts = [_receipt_from_turn(turn) for turn in turns]
    failures: list[str] = []
    if len(receipts) != len(turns):
        failures.append("missing_receipts")
    if any(receipt.memory_write_allowed for receipt in receipts):
        failures.append("memory_write_allowed")
    if any(receipt.raw_ref_retained for receipt in receipts):
        failures.append("raw_ref_retained")
    if any(receipt.external_effect_executed for receipt in receipts):
        failures.append("external_effect_executed")
    if any(receipt.real_screen_capture_started or receipt.voice_capture_enabled for receipt in receipts):
        failures.append("live_capture_started")
    if any(
        receipt.raw_payload_included
        or receipt.contains_user_utterance
        or receipt.contains_assistant_response
        for receipt in receipts
    ):
        failures.append("unredacted_receipt")
    return LiveTutorReceiptReport(
        passed=not failures,
        generated_at=datetime.now(UTC),
        turn_count=len(turns),
        receipt_count=len(receipts),
        latest_target_label=receipts[-1].target_label if receipts else None,
        receipts=receipts,
        memory_write_count=sum(int(receipt.memory_write_allowed) for receipt in receipts),
        raw_ref_retained_count=sum(int(receipt.raw_ref_retained) for receipt in receipts),
        external_effect_count=sum(int(receipt.external_effect_executed) for receipt in receipts),
        real_screen_capture_started=any(
            receipt.real_screen_capture_started for receipt in receipts
        ),
        voice_capture_enabled=any(receipt.voice_capture_enabled for receipt in receipts),
        blocked_effects=sorted(LIVE_TUTOR_REQUIRED_BLOCKED_EFFECTS),
        safety_failures=failures,
    )


def _append_pointer_normalization_flags(
    turn: LiveTutorTurn,
    normalized_pointer: LiveTutorNormalizedPointer,
) -> LiveTutorTurn:
    flags = [
        *turn.safety_flags,
        f"pointer_coordinate_space:{normalized_pointer.source_coordinate_space}",
        "client_pointer_normalized",
    ]
    if normalized_pointer.client_pointer_was_clamped:
        flags.append("client_pointer_clamped")
    payload = turn.model_dump(mode="python")
    payload["safety_flags"] = flags
    return LiveTutorTurn.model_validate(payload)


def _resolve_intent(
    user_utterance: str,
    *,
    surface: SafeCreativeDemoSurface,
    pointer_state: LiveTutorPointerState,
) -> tuple[str, str, str, str, float, Literal["this", "that", "these", "none"], list[str]]:
    normalized = user_utterance.lower()
    pointer_target_id = _resolve_pointer_target(normalized, pointer_state=pointer_state)
    pointer_target = surface.target_by_id(pointer_target_id) if pointer_target_id else None
    referent = _referent_from_utterance(normalized, pointer_state)
    referenced_ids = _referenced_target_ids(pointer_state, pointer_target_id)

    if "remember" in normalized and pointer_target:
        return (
            pointer_target.target_id,
            "propose_manual_memory",
            (
                f"I can prepare a Memory Book card for {pointer_target.label}. "
                "Nothing is saved until you confirm it."
            ),
            "Review the memory proposal before saving.",
            0.86,
            referent,
            referenced_ids,
        )
    if "these" in normalized and referenced_ids:
        primary = referenced_ids[-1]
        labels = [surface.target_by_id(target_id).label for target_id in referenced_ids]
        return (
            primary,
            "multi_target_reference",
            (
                f"I understand these as: {', '.join(labels)}. "
                "For now I can explain the relationship, not perform a combined action."
            ),
            "Confirm any combined workflow before Cortex turns it into a skill.",
            0.78,
            "these",
            referenced_ids,
        )
    if ("explain" in normalized or "what is" in normalized or "what's" in normalized) and pointer_target:
        return (
            pointer_target.target_id,
            "explain_pointed_target",
            (
                f"{pointer_target.label}: {pointer_target.plain_description} "
                "I am only explaining it; I did not click or change anything."
            ),
            "Use the explanation, then decide the next step yourself.",
            0.88,
            referent,
            referenced_ids,
        )
    if "lut" in normalized:
        return (
            "lut_menu",
            "add_lut",
            "Use the LUT menu on the right inspector. I can point to it, but you stay in control of the click.",
            "Open the LUT menu yourself if that matches your footage.",
            0.9,
            referent,
            ["lut_menu"],
        )
    if "node" in normalized:
        return (
            "node_graph",
            "find_node_graph",
            "The node graph is in the upper-right part of the color workspace.",
            "Look at the highlighted node graph area before changing grades.",
            0.88,
            referent,
            ["node_graph"],
        )
    if "color" in normalized or "grade" in normalized:
        return (
            "color_page_button",
            "start_color_grading",
            "Start by switching to the Color Page. I am pointing at the workspace switcher.",
            "Click the Color Page button yourself to enter the color workspace.",
            0.92,
            referent,
            ["color_page_button"],
        )
    if "next" in normalized:
        if surface.active_page == "color":
            target_id = pointer_target.target_id if pointer_target else "node_graph"
            target = surface.target_by_id(target_id)
            return (
                target_id,
                "next_step_color_workspace",
                (
                    f"Because you are in Color, use {target.label} as the next anchor. "
                    "I will keep pointing, not acting."
                ),
                "Inspect the highlighted area yourself before changing grades.",
                0.82,
                referent,
                referenced_ids if pointer_target else ["node_graph"],
            )
        return (
            "color_page_button",
            "next_step_enter_color",
            "The next safe step is to switch to the Color Page before touching LUT controls.",
            "Click the Color Page button yourself.",
            0.8,
            referent,
            ["color_page_button"],
        )
    return (
        pointer_target.target_id if pointer_target else "inspector",
        "general_orientation",
        (
            f"I am oriented on {pointer_target.label}. {pointer_target.plain_description}"
            if pointer_target
            else "I found the inspector, which is a safe place to inspect settings before acting."
        ),
        "Review the highlighted setting area; no action was taken for you.",
        0.62,
        referent,
        referenced_ids if pointer_target else ["inspector"],
    )


def _pointer_state_from_question(
    question: LiveTutorQuestionInput,
    *,
    surface: SafeCreativeDemoSurface,
) -> tuple[LiveTutorPointerState, LiveTutorNormalizedPointer | None]:
    known_target_ids = {target.target_id for target in surface.targets}
    selected_ids = [target_id for target_id in question.selected_target_ids if target_id in known_target_ids]
    current_target = question.pointed_target_id if question.pointed_target_id in known_target_ids else None
    previous_target = question.previous_target_id if question.previous_target_id in known_target_ids else None
    normalized_pointer = normalize_client_pointer_to_surface(
        pointer_x=question.pointer_x,
        pointer_y=question.pointer_y,
        surface=surface,
        coordinate_space=question.pointer_coordinate_space,
        client_surface_width=question.client_surface_width,
        client_surface_height=question.client_surface_height,
    )
    return (
        LiveTutorPointerState(
            current_target_id=current_target,
            previous_target_id=previous_target,
            selected_target_ids=selected_ids,
            pointer_x=normalized_pointer.pointer_x if normalized_pointer else None,
            pointer_y=normalized_pointer.pointer_y if normalized_pointer else None,
            referent_phrase="this" if current_target else "none",
        ),
        normalized_pointer,
    )


def _resolve_pointer_target(
    normalized_utterance: str,
    *,
    pointer_state: LiveTutorPointerState,
) -> str | None:
    if "that" in normalized_utterance and pointer_state.previous_target_id:
        return pointer_state.previous_target_id
    if "these" in normalized_utterance and pointer_state.selected_target_ids:
        return pointer_state.selected_target_ids[-1]
    if "this" in normalized_utterance and pointer_state.current_target_id:
        return pointer_state.current_target_id
    if pointer_state.current_target_id and (
        "explain" in normalized_utterance
        or "remember" in normalized_utterance
        or "next" in normalized_utterance
    ):
        return pointer_state.current_target_id
    return None


def _referent_from_utterance(
    normalized_utterance: str,
    pointer_state: LiveTutorPointerState,
) -> Literal["this", "that", "these", "none"]:
    if "these" in normalized_utterance and pointer_state.selected_target_ids:
        return "these"
    if "that" in normalized_utterance and pointer_state.previous_target_id:
        return "that"
    if ("this" in normalized_utterance or pointer_state.current_target_id) and pointer_state.current_target_id:
        return "this"
    return "none"


def _referenced_target_ids(
    pointer_state: LiveTutorPointerState,
    primary_target_id: str | None,
) -> list[str]:
    ids: list[str] = []
    for target_id in [
        *pointer_state.selected_target_ids,
        pointer_state.previous_target_id,
        pointer_state.current_target_id,
        primary_target_id,
    ]:
        if target_id and target_id not in ids:
            ids.append(target_id)
    return ids or ([primary_target_id] if primary_target_id else [])


def _build_manual_memory_proposal(
    target: DemoTarget,
    *,
    sequence: int,
) -> ManualMemoryProposal:
    return ManualMemoryProposal(
        proposal_id=f"manual_memory_proposal_{sequence:03d}",
        target_id=target.target_id,
        target_label=target.label,
        content_preview=(
            f"Remember that {target.label} is {target.plain_description.lower()}"
        ),
    )


def _companion_state_for_intent(
    intent_label: str,
    *,
    target: DemoTarget,
) -> LiveTutorCompanionState:
    if intent_label == "propose_manual_memory":
        return LiveTutorCompanionState(
            mode="review_required",
            label=f"Review memory for {target.label}",
            safety_caption="Nothing is saved until you approve the Memory Book card.",
        )
    return LiveTutorCompanionState(
        mode="answering",
        label=f"Pointing at {target.label}",
        safety_caption="Display only. No clicks, capture, mic, or memory write.",
    )


def _micro_steps_for_intent(
    intent_label: str,
    *,
    target: DemoTarget,
    surface: SafeCreativeDemoSurface,
) -> list[str]:
    if intent_label == "start_color_grading":
        return [
            "Look at the highlighted Color button.",
            "Click it yourself to switch workspaces.",
            "Then ask what to inspect next.",
        ]
    if intent_label == "next_step_color_workspace":
        return [
            f"Use {target.label} as the next visual anchor.",
            "Inspect before changing any grade.",
            "Ask Cortex to explain this target if needed.",
        ]
    if intent_label == "add_lut":
        return [
            "Open the LUT menu only if you want a look preset.",
            "Preview before applying anything.",
            "Ask Cortex to remember the workflow only after review.",
        ]
    if intent_label == "find_node_graph":
        return [
            "Look at the highlighted node graph.",
            "Treat each node as one step in the color chain.",
            "Ask about this node area before changing it.",
        ]
    if intent_label == "propose_manual_memory":
        return [
            f"Review the proposed card for {target.label}.",
            "Save it manually in Memory Book later.",
            "Dismiss it if the context is not useful.",
        ]
    if intent_label == "multi_target_reference":
        return [
            "Cortex grouped your recent pointer targets.",
            "Review the relationship before turning it into a workflow.",
            "No combined action was executed.",
        ]
    if intent_label == "explain_pointed_target":
        return [
            f"Use {target.label} as the current reference.",
            "Ask 'what next' when you are ready.",
            f"Cortex sees this inside the {surface.app_label} demo only.",
        ]
    return [
        f"Start from {target.label}.",
        "Ask a narrower question if needed.",
        "Cortex will keep the action display-only.",
    ]


def _user_readable_receipt(
    *,
    intent_label: str,
    target: DemoTarget,
    proposal_created: bool,
) -> str:
    if proposal_created:
        return (
            f"Saw {target.label}, drafted a memory card for review, and saved nothing."
        )
    return (
        f"Saw {target.label}, answered beside the pointer, and did not click, record, or save."
    )


def _is_local_url(url: str) -> bool:
    parsed = urlparse(url if "://" in url else f"http://{url}")
    return parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "localhost", "::1"}


def _is_loopback_host(host: str | None) -> bool:
    return host in {"127.0.0.1", "localhost", "::1"}


def _header_hostname(value: str) -> str:
    if not value:
        return ""
    return urlparse(f"//{value}").hostname or ""


def _http_demo_request(
    base_url: str,
    method: str,
    path: str,
    *,
    body: str | None = None,
    headers: Mapping[str, str] | None = None,
) -> tuple[int, dict[str, str], str]:
    parsed = urlparse(base_url)
    conn = http.client.HTTPConnection(parsed.hostname or "127.0.0.1", parsed.port or 80)
    try:
        conn.request(method, path, body=body, headers=dict(headers or {}))
        response = conn.getresponse()
        data = response.read().decode("utf-8")
        return response.status, {key: value for key, value in response.getheaders()}, data
    finally:
        conn.close()


def _extract_demo_token(html: str) -> str:
    marker = 'name="cortex-live-tutor-token" content="'
    start = html.find(marker)
    if start < 0:
        raise ValueError("live tutor token missing from demo page")
    start += len(marker)
    end = html.find('"', start)
    if end < 0:
        raise ValueError("live tutor token malformed")
    return html[start:end]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--server-smoke", action="store_true")
    parser.add_argument("--browser-replay-smoke", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--ask", default=None)
    parser.add_argument("--host", default=DEFAULT_LIVE_TUTOR_HOST)
    parser.add_argument("--port", default=DEFAULT_LIVE_TUTOR_PORT, type=int)
    args = parser.parse_args(argv)

    if args.smoke:
        result = run_live_tutor_demo_smoke()
        payload = result.model_dump(mode="json")
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(
                "live tutor overlay "
                f"{'passed' if result.passed else 'failed'}: "
                f"{result.turn_count} turns, {result.cue_count} cues"
            )
        return 0 if result.passed else 1

    if args.server_smoke:
        result = run_live_tutor_server_smoke()
        payload = result.model_dump(mode="json")
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(
                "live tutor server "
                f"{'passed' if result.passed else 'failed'}: "
                f"{result.turn_count} turns, {result.cue_count} cues"
            )
        return 0 if result.passed else 1

    if args.browser_replay_smoke:
        result = run_live_tutor_browser_replay_smoke()
        payload = result.model_dump(mode="json")
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(
                "live tutor browser replay "
                f"{'passed' if result.passed else 'failed'}: "
                f"{result.receipt_count} redacted receipts"
            )
        return 0 if result.passed else 1

    if args.ask:
        turn = resolve_live_tutor_turn(args.ask)
        payload = turn.model_dump(mode="json")
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"{turn.target_label}: {turn.assistant_response}")
        return 0

    demo = start_live_tutor_demo(host=args.host, port=args.port)
    try:
        print(
            json.dumps(
                {
                    "url": demo.base_url,
                    "proof_id": LIVE_TUTOR_OVERLAY_ID,
                    "policy_ref": LIVE_TUTOR_OVERLAY_POLICY_REF,
                    "localhost_only": True,
                    "real_screen_capture_started": False,
                    "memory_write_allowed": False,
                },
                sort_keys=True,
            )
        )
        demo.thread.join()
    except KeyboardInterrupt:
        demo.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
