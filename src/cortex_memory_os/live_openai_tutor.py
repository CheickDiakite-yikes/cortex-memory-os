"""Cheap-model OpenAI draft path for the controlled live tutor demo."""

from __future__ import annotations

import argparse
import json
import urllib.error
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, ValidationError, field_validator, model_validator

from cortex_memory_os.contracts import StrictModel
from cortex_memory_os.live_openai_smoke import (
    DEFAULT_OPENAI_MODEL,
    call_responses_api,
    extract_output_text,
    load_live_openai_config,
)
from cortex_memory_os.live_tutor_overlay import (
    DemoTarget,
    build_safe_creative_demo_surface,
)

OPENAI_TUTOR_SMOKE_ID = "OPENAI-TUTOR-SAFE-DRAFT-001"
OPENAI_TUTOR_POLICY_REF = "policy_openai_tutor_safe_draft_v1"
DEFAULT_OPENAI_TUTOR_MAX_OUTPUT_TOKENS = 180
DEFAULT_OPENAI_TUTOR_REASONING_EFFORT = "minimal"

_PROHIBITED_MARKERS = [
    "OPENAI_API_KEY=",
    "CORTEX_FAKE_TOKEN",
    "sk-",
    "raw://",
    "encrypted_blob://",
    "Ignore previous instructions",
    "BEGIN " + "PRIVATE KEY",
]


class OpenAITutorRequest(StrictModel):
    user_utterance: str = Field(min_length=1, max_length=220)
    target_id: str = Field(min_length=1)
    target_label: str = Field(min_length=1, max_length=80)
    target_description: str = Field(min_length=1, max_length=220)
    active_page: str = Field(default="edit", min_length=1, max_length=40)
    controlled_surface: bool = True
    real_screen_capture_started: bool = False
    raw_ref_retained: bool = False
    memory_write_allowed: bool = False
    policy_refs: list[str] = Field(default_factory=lambda: [OPENAI_TUTOR_POLICY_REF])

    @field_validator("user_utterance", "target_id", "target_label", "target_description")
    @classmethod
    def reject_prohibited_text(cls, value: str) -> str:
        if any(marker in value for marker in _PROHIBITED_MARKERS):
            raise ValueError("OpenAI tutor request cannot carry secret/raw/injection markers")
        return value

    @model_validator(mode="after")
    def keep_request_controlled(self) -> OpenAITutorRequest:
        if not self.controlled_surface:
            raise ValueError("OpenAI tutor request must come from controlled demo state")
        if self.real_screen_capture_started or self.raw_ref_retained or self.memory_write_allowed:
            raise ValueError("OpenAI tutor request cannot include capture/raw/memory effects")
        if OPENAI_TUTOR_POLICY_REF not in self.policy_refs:
            raise ValueError("OpenAI tutor request requires policy ref")
        return self


class OpenAITutorDraft(StrictModel):
    mode: Literal["dry_run", "live"]
    model: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    target_label: str = Field(min_length=1)
    assistant_response: str = Field(min_length=1, max_length=360)
    micro_steps: list[str] = Field(default_factory=list, min_length=1, max_length=3)
    confidence: float = Field(ge=0, le=1)
    response_id: str | None = None
    store_false: bool = True
    max_output_tokens: int = Field(ge=32, le=320)
    reasoning_effort: str | None = DEFAULT_OPENAI_TUTOR_REASONING_EFFORT
    prompt_char_count: int = Field(ge=1, le=2400)
    usage_summary: dict[str, int] = Field(default_factory=dict)
    memory_write_count: int = 0
    raw_ref_retained_count: int = 0
    external_effect_count: int = 0
    policy_refs: list[str] = Field(default_factory=lambda: [OPENAI_TUTOR_POLICY_REF])

    @field_validator("assistant_response")
    @classmethod
    def reject_prohibited_response(cls, value: str) -> str:
        if any(marker in value for marker in _PROHIBITED_MARKERS):
            raise ValueError("OpenAI tutor draft cannot carry secret/raw markers")
        return value

    @field_validator("micro_steps")
    @classmethod
    def reject_prohibited_steps(cls, value: list[str]) -> list[str]:
        for step in value:
            if any(marker in step for marker in _PROHIBITED_MARKERS):
                raise ValueError("OpenAI tutor draft steps cannot carry secret/raw markers")
        return value

    @model_validator(mode="after")
    def keep_draft_safe(self) -> OpenAITutorDraft:
        if not self.store_false:
            raise ValueError("OpenAI tutor draft requires store:false")
        if self.memory_write_count or self.raw_ref_retained_count or self.external_effect_count:
            raise ValueError("OpenAI tutor draft cannot create memory/raw/external effects")
        if OPENAI_TUTOR_POLICY_REF not in self.policy_refs:
            raise ValueError("OpenAI tutor draft requires policy ref")
        return self


class OpenAITutorSmokeResult(StrictModel):
    proof_id: str = OPENAI_TUTOR_SMOKE_ID
    policy_ref: str = OPENAI_TUTOR_POLICY_REF
    passed: bool
    generated_at: datetime
    live: bool
    model: str
    target_id: str
    prompt_char_count: int = Field(ge=1)
    store_false: bool
    memory_write_count: int = 0
    raw_ref_retained_count: int = 0
    external_effect_count: int = 0
    real_screen_capture_started: bool = False
    prohibited_marker_count: int = 0
    safety_failures: list[str] = Field(default_factory=list)


def build_default_tutor_request(
    *,
    target_id: str = "node_graph",
    user_utterance: str = "Explain this and suggest one safe next step.",
    active_page: str = "color",
) -> OpenAITutorRequest:
    surface = build_safe_creative_demo_surface(active_page=active_page)
    target = surface.target_by_id(target_id)
    return openai_tutor_request_from_target(
        user_utterance=user_utterance,
        target=target,
        active_page=active_page,
    )


def openai_tutor_request_from_target(
    *,
    user_utterance: str,
    target: DemoTarget,
    active_page: str = "edit",
) -> OpenAITutorRequest:
    return OpenAITutorRequest(
        user_utterance=user_utterance,
        target_id=target.target_id,
        target_label=target.label,
        target_description=target.plain_description,
        active_page=active_page,
    )


def build_openai_tutor_prompt(request: OpenAITutorRequest) -> str:
    return "\n".join(
        [
            "You are Cortex Pointer inside a controlled localhost demo surface.",
            "Use only the structured target facts below.",
            "Do not claim to see the real screen, microphone, files, tabs, clipboard, or user secrets.",
            "Do not click, type, export, save memory, or instruct the system to start capture.",
            "Return compact JSON only with keys: assistant_response, micro_steps, confidence.",
            "assistant_response must be one short sentence near the pointer.",
            "micro_steps must contain 1 to 3 short user-controlled steps.",
            "",
            f"user_utterance: {request.user_utterance}",
            f"active_page: {request.active_page}",
            f"target_id: {request.target_id}",
            f"target_label: {request.target_label}",
            f"target_description: {request.target_description}",
        ]
    )


def build_openai_tutor_payload(
    request: OpenAITutorRequest,
    *,
    model: str = DEFAULT_OPENAI_MODEL,
    max_output_tokens: int = DEFAULT_OPENAI_TUTOR_MAX_OUTPUT_TOKENS,
    reasoning_effort: str | None = DEFAULT_OPENAI_TUTOR_REASONING_EFFORT,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": model,
        "input": build_openai_tutor_prompt(request),
        "max_output_tokens": max_output_tokens,
        "store": False,
    }
    if reasoning_effort:
        payload["reasoning"] = {"effort": reasoning_effort}
    return payload


def dry_run_openai_tutor_draft(
    request: OpenAITutorRequest,
    *,
    model: str = DEFAULT_OPENAI_MODEL,
    max_output_tokens: int = DEFAULT_OPENAI_TUTOR_MAX_OUTPUT_TOKENS,
    reasoning_effort: str | None = DEFAULT_OPENAI_TUTOR_REASONING_EFFORT,
) -> OpenAITutorDraft:
    prompt = build_openai_tutor_prompt(request)
    return OpenAITutorDraft(
        mode="dry_run",
        model=model,
        target_id=request.target_id,
        target_label=request.target_label,
        assistant_response=(
            f"{request.target_label}: I can explain this controlled target without acting."
        ),
        micro_steps=[
            "Review the highlighted target.",
            "Choose the next step yourself.",
            "Save a memory only after manual review.",
        ],
        confidence=0.74,
        store_false=True,
        max_output_tokens=max_output_tokens,
        reasoning_effort=reasoning_effort,
        prompt_char_count=len(prompt),
    )


def live_openai_tutor_draft(
    request: OpenAITutorRequest,
    *,
    env_file: Path,
    model: str | None = None,
    max_output_tokens: int = DEFAULT_OPENAI_TUTOR_MAX_OUTPUT_TOKENS,
    reasoning_effort: str | None = DEFAULT_OPENAI_TUTOR_REASONING_EFFORT,
) -> OpenAITutorDraft:
    prompt = build_openai_tutor_prompt(request)
    config = load_live_openai_config(
        env_file=env_file,
        model=model,
        prompt=prompt,
        max_output_tokens=max_output_tokens,
        reasoning_effort=reasoning_effort,
    )
    response = call_responses_api(config)
    parsed = _parse_tutor_response_text(extract_output_text(response))
    return OpenAITutorDraft(
        mode="live",
        model=config.model,
        target_id=request.target_id,
        target_label=request.target_label,
        assistant_response=parsed["assistant_response"],
        micro_steps=parsed["micro_steps"],
        confidence=parsed["confidence"],
        response_id=response.get("id"),
        store_false=True,
        max_output_tokens=max_output_tokens,
        reasoning_effort=reasoning_effort,
        prompt_char_count=len(prompt),
        usage_summary=_usage_summary(response.get("usage")),
    )


def run_openai_tutor_smoke(
    *,
    env_file: Path = Path(".env.local"),
    live: bool = False,
    model: str | None = None,
) -> OpenAITutorSmokeResult:
    request = build_default_tutor_request()
    try:
        draft = (
            live_openai_tutor_draft(request, env_file=env_file, model=model)
            if live
            else dry_run_openai_tutor_draft(request, model=model or DEFAULT_OPENAI_MODEL)
        )
        payload = "\n".join(
            [
                request.model_dump_json(),
                draft.model_dump_json(),
                json.dumps(build_openai_tutor_payload(request, model=draft.model), sort_keys=True),
            ]
        )
        prohibited_marker_count = sum(1 for marker in _PROHIBITED_MARKERS if marker in payload)
        failures = []
        if not draft.store_false:
            failures.append("store_not_false")
        if draft.memory_write_count or draft.raw_ref_retained_count or draft.external_effect_count:
            failures.append("unsafe_effect")
        if prohibited_marker_count:
            failures.append("prohibited_marker")
        return OpenAITutorSmokeResult(
            passed=not failures,
            generated_at=datetime.now(UTC),
            live=live,
            model=draft.model,
            target_id=draft.target_id,
            prompt_char_count=draft.prompt_char_count,
            store_false=draft.store_false,
            memory_write_count=draft.memory_write_count,
            raw_ref_retained_count=draft.raw_ref_retained_count,
            external_effect_count=draft.external_effect_count,
            prohibited_marker_count=prohibited_marker_count,
            safety_failures=failures,
        )
    except (RuntimeError, ValidationError, urllib.error.HTTPError, urllib.error.URLError, ValueError) as exc:
        return OpenAITutorSmokeResult(
            passed=False,
            generated_at=datetime.now(UTC),
            live=live,
            model=model or DEFAULT_OPENAI_MODEL,
            target_id=request.target_id,
            prompt_char_count=len(build_openai_tutor_prompt(request)),
            store_false=True,
            safety_failures=[_safe_error_label(exc)],
        )


def _parse_tutor_response_text(text: str) -> dict[str, Any]:
    candidate = text.strip()
    if candidate.startswith("```"):
        candidate = candidate.strip("`").strip()
        if candidate.lower().startswith("json"):
            candidate = candidate[4:].strip()
    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError:
        parsed = {
            "assistant_response": candidate[:320] or "I can explain this controlled target safely.",
            "micro_steps": ["Review the highlighted target.", "Choose the next step yourself."],
            "confidence": 0.55,
        }
    if not isinstance(parsed, dict):
        parsed = {
            "assistant_response": "I can explain this controlled target safely.",
            "micro_steps": ["Review the highlighted target."],
            "confidence": 0.55,
        }
    steps = parsed.get("micro_steps")
    if not isinstance(steps, list) or not steps:
        steps = ["Review the highlighted target."]
    return {
        "assistant_response": str(parsed.get("assistant_response", "")).strip()
        or "I can explain this controlled target safely.",
        "micro_steps": [str(step).strip() for step in steps if str(step).strip()][:3],
        "confidence": _coerce_confidence(parsed.get("confidence")),
    }


def _coerce_confidence(value: Any) -> float:
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        return 0.55
    return max(0.0, min(1.0, confidence))


def _usage_summary(value: Any) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    summary: dict[str, int] = {}
    for key in ("input_tokens", "output_tokens", "total_tokens"):
        token_value = value.get(key)
        if isinstance(token_value, int):
            summary[key] = token_value
    return summary


def _safe_error_label(exc: Exception) -> str:
    if isinstance(exc, urllib.error.HTTPError):
        return f"http_error_{exc.code}"
    if isinstance(exc, urllib.error.URLError):
        return "network_error"
    if isinstance(exc, RuntimeError):
        return "missing_or_invalid_openai_key"
    return exc.__class__.__name__


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", default=".env.local")
    parser.add_argument("--model", default=None)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    result = run_openai_tutor_smoke(
        env_file=Path(args.env_file),
        live=args.live,
        model=args.model,
    )
    payload = result.model_dump(mode="json")
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(
            "openai tutor "
            f"{'passed' if result.passed else 'failed'}: "
            f"{'live' if result.live else 'dry-run'} {result.model}"
        )
    return 0 if result.passed else 1


__all__ = [
    "DEFAULT_OPENAI_TUTOR_MAX_OUTPUT_TOKENS",
    "OPENAI_TUTOR_POLICY_REF",
    "OPENAI_TUTOR_SMOKE_ID",
    "OpenAITutorDraft",
    "OpenAITutorRequest",
    "OpenAITutorSmokeResult",
    "build_openai_tutor_payload",
    "build_openai_tutor_prompt",
    "dry_run_openai_tutor_draft",
    "live_openai_tutor_draft",
    "openai_tutor_request_from_target",
    "run_openai_tutor_smoke",
]


if __name__ == "__main__":
    raise SystemExit(main())
