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

LIVE_TUTOR_OVERLAY_ID = "LIVE-TUTOR-OVERLAY-001"
LIVE_TUTOR_OVERLAY_POLICY_REF = "policy_live_tutor_overlay_v1"
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
    policy_refs: list[str] = Field(default_factory=lambda: [LIVE_TUTOR_OVERLAY_POLICY_REF])

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
    policy_refs: list[str] = Field(default_factory=lambda: [LIVE_TUTOR_OVERLAY_POLICY_REF])

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


class LiveTutorTurn(StrictModel):
    turn_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    user_utterance: str = Field(min_length=1, max_length=240)
    app_surface: str = Field(min_length=1)
    screen_state_ref: str = Field(pattern=r"^controlled_dom://")
    intent_label: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    target_label: str = Field(min_length=1)
    target_coordinates: SpatialTutorCue
    assistant_response: str = Field(min_length=1, max_length=420)
    confidence: float = Field(ge=0, le=1)
    next_user_action: str = Field(min_length=1)
    safety_flags: list[str] = Field(default_factory=list)
    display_only: bool = True
    memory_write_allowed: bool = False
    raw_ref_retained: bool = False
    external_effect_executed: bool = False
    real_screen_capture_started: bool = False
    voice_capture_enabled: bool = False
    policy_refs: list[str] = Field(default_factory=lambda: [LIVE_TUTOR_OVERLAY_POLICY_REF])

    @field_validator("user_utterance", "assistant_response", "next_user_action")
    @classmethod
    def reject_prohibited_markers(cls, value: str) -> str:
        if any(marker in value for marker in _PROHIBITED_MARKERS):
            raise ValueError("live tutor turn cannot carry secret/raw/prompt-injection markers")
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
        if LIVE_TUTOR_OVERLAY_POLICY_REF not in self.policy_refs:
            raise ValueError("live tutor turn requires policy ref")
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
    raw_ref_retained_count: int = Field(ge=0)
    external_effect_count: int = Field(ge=0)
    real_screen_capture_started: bool = False
    voice_capture_enabled: bool = False
    prohibited_marker_count: int = Field(ge=0)
    safety_failures: list[str] = Field(default_factory=list)


class LiveTutorDashboardPanel(StrictModel):
    panel_id: str = LIVE_TUTOR_OVERLAY_ID
    title: str = "Live Tutor Overlay"
    summary: str = Field(min_length=1)
    demo_url: str = "http://127.0.0.1:8797/"
    smoke_command: str = "uv run cortex-live-tutor-demo --server-smoke --json"
    latest_targets: list[str] = Field(default_factory=list)
    turn_count: int = Field(ge=0)
    cue_count: int = Field(ge=0)
    display_only: bool = True
    controlled_surface: bool = True
    memory_write_allowed: bool = False
    raw_ref_retained: bool = False
    external_effect_enabled: bool = False
    real_screen_capture_started: bool = False
    voice_capture_enabled: bool = False
    raw_payload_included: bool = False
    blocked_effects: list[str] = Field(default_factory=list)
    policy_refs: list[str] = Field(default_factory=lambda: [LIVE_TUTOR_OVERLAY_POLICY_REF])

    @model_validator(mode="after")
    def keep_dashboard_panel_safe(self) -> LiveTutorDashboardPanel:
        if not self.display_only or not self.controlled_surface:
            raise ValueError("live tutor dashboard panel must be controlled and display-only")
        if self.memory_write_allowed or self.raw_ref_retained or self.external_effect_enabled:
            raise ValueError("live tutor dashboard panel cannot enable memory/raw/external effects")
        if self.real_screen_capture_started or self.voice_capture_enabled:
            raise ValueError("live tutor dashboard panel cannot enable screen or voice capture")
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

    @field_validator("user_utterance")
    @classmethod
    def reject_prohibited_markers(cls, value: str) -> str:
        if any(marker in value for marker in _PROHIBITED_MARKERS):
            raise ValueError("live tutor question cannot carry secret/raw/prompt-injection markers")
        return value


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
        with self._lock:
            sequence = len(self._turns) + 1
            turn = resolve_live_tutor_turn(
                question.user_utterance,
                surface=build_safe_creative_demo_surface(active_page=question.active_page),
                sequence=sequence,
            )
            self._turns.append(turn)
            return turn

    def record_rejection(self) -> None:
        with self._lock:
            self.rejected_turn_count += 1

    def result(self) -> LiveTutorDemoResult:
        with self._lock:
            turns = list(self._turns)
        return _result_from_turns(turns)


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


def resolve_live_tutor_turn(
    user_utterance: str,
    *,
    surface: SafeCreativeDemoSurface | None = None,
    session_id: str = "live_tutor_demo_session",
    sequence: int = 1,
) -> LiveTutorTurn:
    surface = surface or build_safe_creative_demo_surface()
    target_id, intent_label, response, next_action, confidence = _resolve_intent(
        user_utterance,
        surface=surface,
    )
    target = surface.target_by_id(target_id)
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
    return LiveTutorTurn(
        turn_id=f"live_tutor_turn_{sequence:03d}",
        session_id=session_id,
        user_utterance=user_utterance,
        app_surface=surface.app_label,
        screen_state_ref=f"controlled_dom://live-tutor-demo/{surface.surface_id}",
        intent_label=intent_label,
        target_id=target.target_id,
        target_label=target.label,
        target_coordinates=cue,
        assistant_response=response,
        confidence=confidence,
        next_user_action=next_action,
        safety_flags=[
            "controlled_demo_surface",
            "display_only_pointer",
            "no_real_screen_capture",
            "no_voice_capture",
            "no_memory_write",
            "no_external_effects",
        ],
    )


def run_live_tutor_demo_smoke() -> LiveTutorDemoResult:
    surface = build_safe_creative_demo_surface()
    utterances = [
        "How do I start color grading?",
        "Where is the node graph?",
        "How do I add a LUT?",
        "What should I click next?",
    ]
    turns = [
        resolve_live_tutor_turn(utterance, surface=surface, sequence=index)
        for index, utterance in enumerate(utterances, start=1)
    ]
    return _result_from_turns(turns)


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


def build_live_tutor_dashboard_panel(
    result: LiveTutorDemoResult | None = None,
) -> LiveTutorDashboardPanel:
    result = result or run_live_tutor_demo_smoke()
    return LiveTutorDashboardPanel(
        summary=(
            "Controlled creative-tool tutor demo: Cortex answers contextual questions "
            "with a secondary blue cursor and receipt panel, without clicks, capture, "
            "voice, raw refs, durable memory, or external effects."
        ),
        latest_targets=result.target_ids[-3:],
        turn_count=result.turn_count,
        cue_count=result.cue_count,
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


def _result_from_turns(turns: list[LiveTutorTurn]) -> LiveTutorDemoResult:
    payload = "\n".join(turn.model_dump_json() for turn in turns)
    prohibited_marker_count = sum(1 for marker in _PROHIBITED_MARKERS if marker in payload)
    checks = {
        "turn_count": len(turns) >= 3,
        "controlled_surface": bool(turns),
        "display_only": all(turn.display_only and turn.target_coordinates.display_only for turn in turns),
        "known_targets": {turn.target_id for turn in turns}
        >= {"color_page_button", "node_graph", "lut_menu"},
        "no_memory_writes": all(not turn.memory_write_allowed for turn in turns),
        "no_raw_refs": all(not turn.raw_ref_retained for turn in turns),
        "no_external_effects": all(not turn.external_effect_executed for turn in turns),
        "no_live_capture": all(
            not turn.real_screen_capture_started and not turn.voice_capture_enabled
            for turn in turns
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
        raw_ref_retained_count=sum(int(turn.raw_ref_retained) for turn in turns),
        external_effect_count=sum(int(turn.external_effect_executed) for turn in turns),
        real_screen_capture_started=any(turn.real_screen_capture_started for turn in turns),
        voice_capture_enabled=any(turn.voice_capture_enabled for turn in turns),
        prohibited_marker_count=prohibited_marker_count,
        safety_failures=failures,
    )


def _resolve_intent(
    user_utterance: str,
    *,
    surface: SafeCreativeDemoSurface,
) -> tuple[str, str, str, str, float]:
    normalized = user_utterance.lower()
    if "lut" in normalized:
        return (
            "lut_menu",
            "add_lut",
            "Use the LUT menu on the right inspector. I can point to it, but you stay in control of the click.",
            "Open the LUT menu yourself if that matches your footage.",
            0.9,
        )
    if "node" in normalized:
        return (
            "node_graph",
            "find_node_graph",
            "The node graph is in the upper-right part of the color workspace.",
            "Look at the highlighted node graph area before changing grades.",
            0.88,
        )
    if "color" in normalized or "grade" in normalized:
        return (
            "color_page_button",
            "start_color_grading",
            "Start by switching to the Color Page. I am pointing at the workspace switcher.",
            "Click the Color Page button yourself to enter the color workspace.",
            0.92,
        )
    if "next" in normalized:
        if surface.active_page == "color":
            return (
                "node_graph",
                "next_step_color_workspace",
                "You are already in the color workspace; the node graph is the safest next anchor.",
                "Select or inspect the first correction node yourself.",
                0.82,
            )
        return (
            "color_page_button",
            "next_step_enter_color",
            "The next safe step is to switch to the Color Page before touching LUT controls.",
            "Click the Color Page button yourself.",
            0.8,
        )
    return (
        "inspector",
        "general_orientation",
        "I found the inspector, which is a safe place to inspect settings before acting.",
        "Review the highlighted setting area; no action was taken for you.",
        0.62,
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
