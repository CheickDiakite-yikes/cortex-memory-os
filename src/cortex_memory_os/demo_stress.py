"""Bounded live stress demo receipt for Cortex Memory OS."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from pydantic import Field, model_validator

from cortex_memory_os.contracts import StrictModel
from cortex_memory_os.dashboard_live_gateway import execute_dashboard_gateway_receipts
from cortex_memory_os.demo_readiness import (
    DEMO_BLOCKED_EFFECTS,
    DEMO_READINESS_POLICY_REF,
    run_demo_readiness,
)
from cortex_memory_os.live_adapters import REPO_ROOT
from cortex_memory_os.live_readiness import inspect_env_local_hygiene
from cortex_memory_os.screen_injection_stress import (
    SCREEN_INJECTION_STRESS_POLICY_REF,
    run_screen_injection_stress,
)
from cortex_memory_os.synthetic_capture_ladder import SYNTHETIC_CAPTURE_LADDER_POLICY_REF

DEMO_STRESS_ID = "DEMO-STRESS-001"
DEMO_STRESS_POLICY_REF = "policy_demo_stress_v1"
DEMO_STRESS_DEFAULT_ITERATIONS = 12
DEMO_STRESS_MAX_ITERATIONS = 50

_PROHIBITED_MARKERS = [
    "CORTEX_FAKE_TOKEN",
    "OPENAI_API_KEY=",
    "api_key=",
    "sk-",
    "Bearer ",
    "raw://",
    "encrypted_blob://",
    "Ignore previous instructions",
    "Demo sealed context memory uses auth callback verification",
    "scene_demo_private_trace",
    "OAuth callback route mismatch",
]


class DemoStressIteration(StrictModel):
    iteration: int = Field(ge=1)
    readiness_passed: bool
    screen_injection_passed: bool
    gateway_executed_count: int = Field(ge=0)
    gateway_blocked_count: int = Field(ge=0)
    gateway_failed_count: int = Field(ge=0)
    gateway_raw_payload_count: int = Field(ge=0)
    gateway_external_effect_count: int = Field(ge=0)
    readiness_prohibited_marker_count: int = Field(ge=0)
    screen_quarantine_count: int = Field(ge=0)
    screen_redaction_count: int = Field(ge=0)
    generated_at: datetime
    content_redacted: bool = True
    source_refs_redacted: bool = True
    procedure_redacted: bool = True

    @model_validator(mode="after")
    def keep_iteration_safe(self) -> DemoStressIteration:
        if self.gateway_failed_count:
            raise ValueError("stress iteration cannot have gateway failures")
        if self.gateway_raw_payload_count:
            raise ValueError("stress iteration cannot return raw payloads")
        if self.gateway_external_effect_count:
            raise ValueError("stress iteration cannot have external effects")
        if self.readiness_prohibited_marker_count:
            raise ValueError("stress iteration cannot include prohibited markers")
        if not self.readiness_passed or not self.screen_injection_passed:
            raise ValueError("stress iteration failed a safety receipt")
        if not self.content_redacted or not self.source_refs_redacted or not self.procedure_redacted:
            raise ValueError("stress iteration must stay redacted")
        return self


class DemoStressReceipt(StrictModel):
    benchmark_id: str = DEMO_STRESS_ID
    policy_ref: str = DEMO_STRESS_POLICY_REF
    passed: bool
    stress_ready: bool
    safe_to_show_publicly: bool
    generated_at: datetime
    iterations_requested: int = Field(ge=1, le=DEMO_STRESS_MAX_ITERATIONS)
    iterations_completed: int = Field(ge=0, le=DEMO_STRESS_MAX_ITERATIONS)
    readiness_passed_count: int = Field(ge=0)
    screen_injection_passed_count: int = Field(ge=0)
    gateway_executed_count: int = Field(ge=0)
    gateway_blocked_count: int = Field(ge=0)
    gateway_failed_count: int = Field(ge=0)
    gateway_raw_payload_count: int = Field(ge=0)
    gateway_external_effect_count: int = Field(ge=0)
    prohibited_marker_count: int = Field(ge=0)
    synthetic_only: bool = True
    localhost_only: bool = True
    real_screen_capture_started: bool = False
    durable_raw_screen_storage_enabled: bool = False
    raw_private_refs_returned: bool = False
    secret_values_read: bool = False
    model_secret_echo_attempted: bool = False
    mutation_export_or_draft_enabled: bool = False
    external_effect_enabled: bool = False
    content_redacted: bool = True
    source_refs_redacted: bool = True
    procedure_redacted: bool = True
    env_local_ignored_by_git: bool
    env_local_tracked_by_git: bool
    blocked_effects: list[str] = Field(default_factory=lambda: list(DEMO_BLOCKED_EFFECTS))
    required_commands: list[str] = Field(default_factory=list)
    iterations: list[DemoStressIteration] = Field(default_factory=list)
    safety_failures: list[str] = Field(default_factory=list)
    policy_refs: list[str] = Field(default_factory=lambda: [DEMO_STRESS_POLICY_REF])

    @model_validator(mode="after")
    def keep_stress_demo_safe(self) -> DemoStressReceipt:
        if self.iterations_completed != len(self.iterations):
            raise ValueError("iterations_completed must match iteration receipt count")
        if self.iterations_completed != self.iterations_requested:
            raise ValueError("stress demo must complete requested iterations")
        if not self.synthetic_only:
            raise ValueError("stress demo must stay synthetic-only")
        if not self.localhost_only:
            raise ValueError("stress demo must stay localhost-only")
        if self.real_screen_capture_started:
            raise ValueError("stress demo cannot start real screen capture")
        if self.durable_raw_screen_storage_enabled:
            raise ValueError("stress demo cannot enable durable raw screen storage")
        if self.raw_private_refs_returned:
            raise ValueError("stress demo cannot return raw private refs")
        if self.secret_values_read:
            raise ValueError("stress demo cannot read secret values")
        if self.model_secret_echo_attempted:
            raise ValueError("stress demo cannot attempt model secret echo")
        if self.mutation_export_or_draft_enabled:
            raise ValueError("stress demo cannot enable mutation/export/draft execution")
        if self.external_effect_enabled:
            raise ValueError("stress demo cannot enable external effects")
        if self.gateway_failed_count or self.gateway_raw_payload_count or self.gateway_external_effect_count:
            raise ValueError("stress demo gateway aggregates must stay safe")
        if self.prohibited_marker_count:
            raise ValueError("stress demo cannot include prohibited markers")
        if self.env_local_tracked_by_git:
            raise ValueError(".env.local cannot be tracked by git")
        if not self.env_local_ignored_by_git:
            raise ValueError(".env.local must be ignored by git")
        if not self.content_redacted or not self.source_refs_redacted or not self.procedure_redacted:
            raise ValueError("stress demo receipt must stay redacted")
        if DEMO_STRESS_POLICY_REF not in self.policy_refs:
            raise ValueError("stress demo requires policy ref")
        missing_effects = sorted(set(DEMO_BLOCKED_EFFECTS) - set(self.blocked_effects))
        if missing_effects:
            raise ValueError(f"stress demo missing blocked effects: {missing_effects}")
        return self


def run_demo_stress(
    *,
    iterations: int = DEMO_STRESS_DEFAULT_ITERATIONS,
    now: datetime | None = None,
    repo_root: Path = REPO_ROOT,
) -> DemoStressReceipt:
    if iterations < 1 or iterations > DEMO_STRESS_MAX_ITERATIONS:
        raise ValueError(f"iterations must be between 1 and {DEMO_STRESS_MAX_ITERATIONS}")

    timestamp = _ensure_utc(now or datetime.now(UTC))
    iteration_receipts: list[DemoStressIteration] = []
    for index in range(iterations):
        iteration_time = timestamp + timedelta(seconds=index)
        readiness = run_demo_readiness(now=iteration_time, repo_root=repo_root)
        screen_stress = run_screen_injection_stress(now=iteration_time)
        gateway = execute_dashboard_gateway_receipts(now=iteration_time)
        iteration_receipts.append(
            DemoStressIteration(
                iteration=index + 1,
                readiness_passed=readiness.passed,
                screen_injection_passed=screen_stress.passed,
                gateway_executed_count=gateway.executed_count,
                gateway_blocked_count=gateway.blocked_count,
                gateway_failed_count=gateway.failed_count,
                gateway_raw_payload_count=gateway.raw_payload_count,
                gateway_external_effect_count=gateway.external_effect_count,
                readiness_prohibited_marker_count=readiness.prohibited_marker_count,
                screen_quarantine_count=screen_stress.quarantine_count,
                screen_redaction_count=screen_stress.redaction_count,
                generated_at=iteration_time,
            )
        )

    hygiene = inspect_env_local_hygiene(repo_root=repo_root, env_file=repo_root / ".env.local")
    raw_receipt = {
        "benchmark_id": DEMO_STRESS_ID,
        "iteration_count": len(iteration_receipts),
        "iterations": [item.model_dump(mode="json") for item in iteration_receipts],
        "blocked_effects": DEMO_BLOCKED_EFFECTS,
        "policy_refs": [
            DEMO_STRESS_POLICY_REF,
            DEMO_READINESS_POLICY_REF,
            SCREEN_INJECTION_STRESS_POLICY_REF,
            SYNTHETIC_CAPTURE_LADDER_POLICY_REF,
        ],
    }
    prohibited_marker_count = _count_prohibited_markers(json.dumps(raw_receipt, sort_keys=True))
    safety_failures = _safety_failures(
        iteration_receipts,
        env_ignored=hygiene.ignored_by_git,
        env_tracked=hygiene.tracked_by_git,
        prohibited_marker_count=prohibited_marker_count,
    )
    return DemoStressReceipt(
        passed=not safety_failures,
        stress_ready=not safety_failures,
        safe_to_show_publicly=not safety_failures,
        generated_at=timestamp,
        iterations_requested=iterations,
        iterations_completed=len(iteration_receipts),
        readiness_passed_count=sum(int(item.readiness_passed) for item in iteration_receipts),
        screen_injection_passed_count=sum(
            int(item.screen_injection_passed) for item in iteration_receipts
        ),
        gateway_executed_count=sum(item.gateway_executed_count for item in iteration_receipts),
        gateway_blocked_count=sum(item.gateway_blocked_count for item in iteration_receipts),
        gateway_failed_count=sum(item.gateway_failed_count for item in iteration_receipts),
        gateway_raw_payload_count=sum(item.gateway_raw_payload_count for item in iteration_receipts),
        gateway_external_effect_count=sum(
            item.gateway_external_effect_count for item in iteration_receipts
        ),
        prohibited_marker_count=prohibited_marker_count,
        env_local_ignored_by_git=hygiene.ignored_by_git,
        env_local_tracked_by_git=hygiene.tracked_by_git,
        required_commands=[
            "uv run cortex-demo-stress --iterations 12 --json",
            "uv run cortex-demo --json",
            "uv run cortex-dashboard-live-gateway --json",
            "uv run cortex-dashboard-shell --smoke --json",
            "python3 -m http.server 8793 --bind 127.0.0.1",
        ],
        iterations=iteration_receipts,
        safety_failures=safety_failures,
        policy_refs=[
            DEMO_STRESS_POLICY_REF,
            DEMO_READINESS_POLICY_REF,
            SCREEN_INJECTION_STRESS_POLICY_REF,
            SYNTHETIC_CAPTURE_LADDER_POLICY_REF,
        ],
    )


def _safety_failures(
    iterations: list[DemoStressIteration],
    *,
    env_ignored: bool,
    env_tracked: bool,
    prohibited_marker_count: int,
) -> list[str]:
    failures: list[str] = []
    if any(not item.readiness_passed for item in iterations):
        failures.append("demo_readiness_failed")
    if any(not item.screen_injection_passed for item in iterations):
        failures.append("screen_injection_stress_failed")
    if any(item.gateway_failed_count for item in iterations):
        failures.append("dashboard_gateway_failed")
    if any(item.gateway_raw_payload_count for item in iterations):
        failures.append("dashboard_gateway_raw_payload")
    if any(item.gateway_external_effect_count for item in iterations):
        failures.append("dashboard_gateway_external_effect")
    if prohibited_marker_count:
        failures.append("prohibited_marker_detected")
    if not env_ignored:
        failures.append("env_local_not_ignored")
    if env_tracked:
        failures.append("env_local_tracked")
    return failures


def _count_prohibited_markers(text: str) -> int:
    return sum(1 for marker in _PROHIBITED_MARKERS if marker in text)


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--iterations",
        type=int,
        default=DEMO_STRESS_DEFAULT_ITERATIONS,
        help=f"Number of synthetic stress iterations, 1-{DEMO_STRESS_MAX_ITERATIONS}.",
    )
    args = parser.parse_args(argv)

    result = run_demo_stress(iterations=args.iterations)
    if args.json:
        print(json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True))
    else:
        status = "ready" if result.stress_ready else "not ready"
        print(
            f"{DEMO_STRESS_ID}: {status}; "
            f"iterations={result.iterations_completed}/{result.iterations_requested}; "
            f"readiness={result.readiness_passed_count}; "
            f"screen_stress={result.screen_injection_passed_count}; "
            f"gateway_failed={result.gateway_failed_count}"
        )
        if result.safety_failures:
            print("failures: " + ", ".join(result.safety_failures))
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
