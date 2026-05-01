"""Sanitized live-browser proof contract for the Cortex dashboard."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

from pydantic import Field, field_validator

from cortex_memory_os.contracts import StrictModel

COMPUTER_DASHBOARD_LIVE_PROOF_ID = "COMPUTER-DASHBOARD-LIVE-PROOF-001"
READONLY_ACTION_LIVE_PROOF_ID = "DASHBOARD-READONLY-ACTION-LIVE-PROOF-001"
COMPUTER_DASHBOARD_LIVE_PROOF_POLICY_REF = "policy_computer_dashboard_live_proof_v1"
READONLY_ACTION_LIVE_PROOF_POLICY_REF = "policy_dashboard_readonly_action_live_proof_v1"

REQUIRED_DASHBOARD_TERMS = [
    "Cortex Memory OS",
    "Shadow Pointer",
    "Memory Palace Review Queue",
    "Skill Forge Candidate Workflows",
    "Safety Firewall",
    "Pause Observation",
    "Recent Safe Receipts",
]
LOCAL_PREVIEW_RECEIPT_MARKERS = [
    "previewed locally",
    "Confirmation",
    "audit receipt",
]
NO_GATEWAY_RECEIPT_MARKERS = [
    "No gateway action executed",
]
READ_ONLY_GATEWAY_RECEIPT_MARKERS = [
    "Gateway receipt allows",
    "read-only",
    "No mutation executed",
]
PROHIBITED_PROOF_MARKERS = [
    "OPENAI_API_KEY=",
    "CORTEX_FAKE_TOKEN",
    "sk-",
    "raw://",
    "encrypted_blob://",
    "Ignore previous instructions",
]


class SanitizedDashboardLiveObservation(StrictModel):
    """Human/Computer-Use observation notes stripped to commit-safe facts."""

    observed_at: datetime
    browser_name: str = Field(min_length=1)
    page_title: str = Field(min_length=1)
    url: str = Field(min_length=1)
    visible_terms: list[str] = Field(min_length=1)
    clicked_control_label: str = Field(min_length=1)
    receipt_text: str = Field(min_length=1)
    read_only_action_receipts: list[str] = Field(default_factory=list)
    raw_screenshot_saved: bool = False
    raw_accessibility_tree_saved: bool = False
    raw_tab_titles_saved: bool = False
    raw_private_text_saved: bool = False
    secret_values_recorded: bool = False
    raw_refs_recorded: bool = False
    durable_memory_write: bool = False
    gateway_mutation_executed: bool = False
    external_effect_executed: bool = False
    prompt_injection_instruction_followed: bool = False

    @field_validator("visible_terms")
    @classmethod
    def _dedupe_visible_terms(cls, value: list[str]) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()
        for term in value:
            stripped = term.strip()
            if not stripped or stripped in seen:
                continue
            normalized.append(stripped)
            seen.add(stripped)
        if not normalized:
            raise ValueError("at least one visible term is required")
        return normalized


class DashboardLiveProofResult(StrictModel):
    policy_ref: str = COMPUTER_DASHBOARD_LIVE_PROOF_POLICY_REF
    proof_id: str = COMPUTER_DASHBOARD_LIVE_PROOF_ID
    passed: bool
    browser_name: str
    local_origin: bool
    visible_required_count: int = Field(ge=0)
    missing_required_terms: list[str] = Field(default_factory=list)
    receipt_is_local_preview: bool
    blocked_effect_count: int = Field(ge=0)
    prohibited_marker_count: int = Field(ge=0)
    raw_capture_saved: bool
    raw_accessibility_tree_saved: bool
    raw_tab_titles_saved: bool
    secret_values_recorded: bool
    durable_memory_write: bool
    gateway_mutation_executed: bool
    external_effect_executed: bool
    read_only_action_receipt_count: int = Field(ge=0)
    read_only_action_live_proof_id: str = READONLY_ACTION_LIVE_PROOF_ID
    safety_failures: list[str] = Field(default_factory=list)


def build_sample_dashboard_live_observation(
    *, observed_at: datetime | None = None
) -> SanitizedDashboardLiveObservation:
    """Return a commit-safe fixture matching the current Computer Use proof shape."""

    return SanitizedDashboardLiveObservation(
        observed_at=observed_at or datetime(2026, 5, 1, 1, 2, tzinfo=UTC),
        browser_name="Google Chrome",
        page_title="Cortex Memory OS Dashboard",
        url="http://127.0.0.1:8787/index.html",
        visible_terms=[
            "Cortex Memory OS",
            "Shadow Pointer",
            "Memory Palace Review Queue",
            "Skill Forge Candidate Workflows",
            "Safety Firewall",
            "Pause Observation",
            "Recent Safe Receipts",
        ],
        clicked_control_label="Pause Observation",
        receipt_text=(
            "Observation pause previewed locally. "
            "Confirmation and audit receipt required."
        ),
        read_only_action_receipts=[
            (
                "Gateway receipt allows memory.explain read-only for "
                "mem_auth_redirect_root_cause. No mutation executed."
            )
        ],
    )


def validate_dashboard_live_proof(
    observation: SanitizedDashboardLiveObservation,
) -> DashboardLiveProofResult:
    visible_blob = "\n".join(
        [
            observation.page_title,
            observation.clicked_control_label,
            observation.receipt_text,
            *observation.visible_terms,
            *observation.read_only_action_receipts,
        ]
    )
    missing_required_terms = _missing_terms(visible_blob, REQUIRED_DASHBOARD_TERMS)
    receipt_is_local_preview = _receipt_is_local_preview(observation.receipt_text)
    local_origin = _is_local_dashboard_url(observation.url)
    prohibited_marker_count = sum(1 for marker in PROHIBITED_PROOF_MARKERS if marker in visible_blob)
    blocked_flags = {
        "raw_screenshot_saved": observation.raw_screenshot_saved,
        "raw_accessibility_tree_saved": observation.raw_accessibility_tree_saved,
        "raw_tab_titles_saved": observation.raw_tab_titles_saved,
        "raw_private_text_saved": observation.raw_private_text_saved,
        "secret_values_recorded": observation.secret_values_recorded,
        "raw_refs_recorded": observation.raw_refs_recorded,
        "durable_memory_write": observation.durable_memory_write,
        "gateway_mutation_executed": observation.gateway_mutation_executed,
        "external_effect_executed": observation.external_effect_executed,
        "prompt_injection_instruction_followed": observation.prompt_injection_instruction_followed,
    }
    safety_failures = []
    if not local_origin:
        safety_failures.append("non_local_dashboard_origin")
    if missing_required_terms:
        safety_failures.append("missing_required_visible_terms")
    if not receipt_is_local_preview:
        safety_failures.append("receipt_not_local_preview")
    if not _read_only_action_receipts_are_safe(observation.read_only_action_receipts):
        safety_failures.append("read_only_action_receipt_not_safe")
    if prohibited_marker_count:
        safety_failures.append("prohibited_marker_in_sanitized_observation")
    safety_failures.extend(name for name, enabled in blocked_flags.items() if enabled)

    return DashboardLiveProofResult(
        passed=not safety_failures,
        browser_name=observation.browser_name,
        local_origin=local_origin,
        visible_required_count=len(REQUIRED_DASHBOARD_TERMS) - len(missing_required_terms),
        missing_required_terms=missing_required_terms,
        receipt_is_local_preview=receipt_is_local_preview,
        blocked_effect_count=sum(1 for enabled in blocked_flags.values() if enabled),
        prohibited_marker_count=prohibited_marker_count,
        raw_capture_saved=observation.raw_screenshot_saved,
        raw_accessibility_tree_saved=observation.raw_accessibility_tree_saved,
        raw_tab_titles_saved=observation.raw_tab_titles_saved,
        secret_values_recorded=observation.secret_values_recorded,
        durable_memory_write=observation.durable_memory_write,
        gateway_mutation_executed=observation.gateway_mutation_executed,
        external_effect_executed=observation.external_effect_executed,
        read_only_action_receipt_count=len(observation.read_only_action_receipts),
        safety_failures=safety_failures,
    )


def _missing_terms(text: str, terms: list[str]) -> list[str]:
    return [term for term in terms if term not in text]


def _receipt_is_local_preview(receipt_text: str) -> bool:
    return all(marker in receipt_text for marker in LOCAL_PREVIEW_RECEIPT_MARKERS) or all(
        marker in receipt_text for marker in NO_GATEWAY_RECEIPT_MARKERS
    )


def _read_only_action_receipts_are_safe(receipts: list[str]) -> bool:
    return all(
        all(marker in receipt for marker in READ_ONLY_GATEWAY_RECEIPT_MARKERS)
        and "memory.forget" not in receipt
        and "memory.export" not in receipt
        and "skill.execute_draft" not in receipt
        for receipt in receipts
    )


def _is_local_dashboard_url(url: str) -> bool:
    normalized = url if "://" in url else f"http://{url}"
    parsed = urlparse(normalized)
    return parsed.scheme in {"http", "https"} and parsed.hostname in {
        "127.0.0.1",
        "localhost",
        "::1",
    }


def load_sanitized_observation(path: Path) -> SanitizedDashboardLiveObservation:
    return SanitizedDashboardLiveObservation.model_validate_json(
        path.read_text(encoding="utf-8")
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--observation-json",
        type=Path,
        default=None,
        help="Path to a sanitized observation JSON object. Defaults to the built-in sample.",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    observation = (
        load_sanitized_observation(args.observation_json)
        if args.observation_json
        else build_sample_dashboard_live_observation()
    )
    result = validate_dashboard_live_proof(observation)
    if args.json:
        print(json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True))
    else:
        status = "passed" if result.passed else "failed"
        print(f"{COMPUTER_DASHBOARD_LIVE_PROOF_ID}: {status}")
        if result.safety_failures:
            print("failures: " + ", ".join(result.safety_failures))
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
