"""Bounded live-readiness hardening harness for Cortex local development."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from cortex_memory_os.adapter_endpoint import run_local_adapter_endpoint_smoke
from cortex_memory_os.live_adapters import REPO_ROOT, run_live_adapter_smoke
from cortex_memory_os.live_openai_smoke import run_smoke
from cortex_memory_os.manual_adapter_proof import run_manual_adapter_proof

LIVE_READINESS_HARDENING_ID = "LIVE-READINESS-HARDENING-001"
LIVE_READINESS_POLICY_REF = "policy_live_readiness_hardening_v1"


class EnvLocalHygiene(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    exists: bool
    ignored_by_git: bool
    tracked_by_git: bool
    secret_values_read: bool = False


class LiveReadinessCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    passed: bool
    live_effect: bool
    policy_refs: list[str] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)


class LiveReadinessResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    benchmark_id: str = LIVE_READINESS_HARDENING_ID
    policy_ref: str = LIVE_READINESS_POLICY_REF
    passed: bool
    secret_hygiene: EnvLocalHygiene
    checks: list[LiveReadinessCheck]
    safety_failures: list[str] = Field(default_factory=list)


def run_live_readiness(
    *,
    repo_root: Path = REPO_ROOT,
    env_file: Path | None = None,
    include_openai: bool = False,
    openai_live: bool = False,
) -> LiveReadinessResult:
    env_file = env_file or repo_root / ".env.local"
    if not env_file.is_absolute():
        env_file = repo_root / env_file
    secret_hygiene = inspect_env_local_hygiene(repo_root=repo_root, env_file=env_file)
    checks = [
        _secret_hygiene_check(secret_hygiene),
        _live_adapter_check(),
        _local_endpoint_check(),
        _manual_adapter_check(),
    ]
    if include_openai or openai_live:
        checks.append(_openai_check(env_file=env_file, live=openai_live))
    else:
        checks.append(
            LiveReadinessCheck(
                name="openai_live_smoke",
                passed=True,
                live_effect=False,
                policy_refs=["LIVE-OPENAI-SMOKE-001"],
                details={"status": "skipped", "reason": "not_requested"},
            )
        )

    safety_failures = [
        f"{check.name}:failed" for check in checks if not check.passed
    ]
    return LiveReadinessResult(
        passed=not safety_failures,
        secret_hygiene=secret_hygiene,
        checks=checks,
        safety_failures=safety_failures,
    )


def inspect_env_local_hygiene(
    *,
    repo_root: Path = REPO_ROOT,
    env_file: Path | None = None,
) -> EnvLocalHygiene:
    env_file = env_file or repo_root / ".env.local"
    path = env_file if env_file.is_absolute() else repo_root / env_file
    relative_path = _repo_relative(path, repo_root)
    return EnvLocalHygiene(
        path=relative_path,
        exists=path.exists(),
        ignored_by_git=_git_check(repo_root, ["check-ignore", "-q", relative_path]),
        tracked_by_git=_git_check(repo_root, ["ls-files", "--error-unmatch", relative_path]),
    )


def _secret_hygiene_check(hygiene: EnvLocalHygiene) -> LiveReadinessCheck:
    passed = hygiene.ignored_by_git and not hygiene.tracked_by_git and not hygiene.secret_values_read
    return LiveReadinessCheck(
        name="env_local_secret_hygiene",
        passed=passed,
        live_effect=False,
        policy_refs=[LIVE_READINESS_POLICY_REF, "policy_secret_pii_local_data_v1"],
        details={
            "exists": hygiene.exists,
            "ignored_by_git": hygiene.ignored_by_git,
            "tracked_by_git": hygiene.tracked_by_git,
            "secret_values_read": hygiene.secret_values_read,
        },
    )


def _live_adapter_check() -> LiveReadinessCheck:
    result = run_live_adapter_smoke()
    return LiveReadinessCheck(
        name="live_adapter_artifacts",
        passed=result.passed,
        live_effect=False,
        policy_refs=[result.policy_ref],
        details={
            "browser_memory_eligible": result.browser_memory_eligible,
            "browser_attack_discarded": result.browser_attack_discarded,
            "browser_raw_ref_retained": result.browser_raw_ref_retained,
            "terminal_secret_retained": result.terminal_secret_retained,
            "terminal_raw_ref_retained": result.terminal_raw_ref_retained,
            "blocked_host_permissions": len(result.blocked_host_permissions),
            "missing_paths": len(result.missing_paths),
            "missing_terms": len(result.missing_terms),
        },
    )


def _local_endpoint_check() -> LiveReadinessCheck:
    result = run_local_adapter_endpoint_smoke()
    return LiveReadinessCheck(
        name="local_adapter_endpoint",
        passed=result.passed,
        live_effect=True,
        policy_refs=[result.policy_ref],
        details={
            "bind_host": result.bind_host,
            "browser_memory_eligible": result.browser_memory_eligible,
            "browser_attack_discarded": result.browser_attack_discarded,
            "terminal_secret_retained": result.terminal_secret_retained,
            "terminal_raw_ref_retained": result.terminal_raw_ref_retained,
            "remote_rejected_status_code": result.remote_rejected_status_code,
            "trust_escalation_rejected_status_code": result.trust_escalation_rejected_status_code,
            "oversized_payload_status_code": result.oversized_payload_status_code,
        },
    )


def _manual_adapter_check() -> LiveReadinessCheck:
    result = run_manual_adapter_proof()
    return LiveReadinessCheck(
        name="manual_adapter_proof",
        passed=result.passed,
        live_effect=True,
        policy_refs=[result.policy_ref],
        details={
            "terminal_event_observed": result.terminal_event_observed,
            "terminal_hook_return_code": result.terminal_hook_return_code,
            "terminal_secret_retained": result.terminal_secret_retained,
            "terminal_raw_ref_retained": result.terminal_raw_ref_retained,
            "browser_memory_eligible": result.browser_memory_eligible,
            "browser_attack_discarded": result.browser_attack_discarded,
            "service_worker_localhost_only": result.service_worker_localhost_only,
            "stdout_redacted": result.stdout_redacted,
            "stderr_redacted": result.stderr_redacted,
        },
    )


def _openai_check(*, env_file: Path, live: bool) -> LiveReadinessCheck:
    try:
        result = run_smoke(
            env_file=env_file,
            dry_run=not live,
            assert_contains="CORTEX_LIVE_OK" if live else None,
        )
    except Exception as error:  # pragma: no cover - specific network errors vary.
        return LiveReadinessCheck(
            name="openai_live_smoke",
            passed=False,
            live_effect=live,
            policy_refs=["LIVE-OPENAI-SMOKE-001"],
            details={
                "status": "failed",
                "error_type": type(error).__name__,
            },
        )

    usage = result.get("usage") if isinstance(result.get("usage"), dict) else {}
    total_tokens = usage.get("total_tokens")
    return LiveReadinessCheck(
        name="openai_live_smoke",
        passed=bool(result.get("ok")),
        live_effect=live,
        policy_refs=["LIVE-OPENAI-SMOKE-001"],
        details={
            "status": "live" if live else "dry_run",
            "model": result.get("model"),
            "store_false": result.get("would_send_store_false", True),
            "response_id_present": bool(result.get("response_id")),
            "total_tokens": total_tokens if isinstance(total_tokens, int) else None,
        },
    )


def _repo_relative(path: Path, repo_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        return str(path)


def _git_check(repo_root: Path, args: list[str]) -> bool:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return completed.returncode == 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--env-file", default=".env.local")
    parser.add_argument(
        "--include-openai",
        action="store_true",
        help="Include the OpenAI smoke in dry-run mode.",
    )
    parser.add_argument(
        "--openai-live",
        action="store_true",
        help="Make the low-cost synthetic OpenAI call. Implies --include-openai.",
    )
    args = parser.parse_args(argv)

    result = run_live_readiness(
        env_file=Path(args.env_file),
        include_openai=args.include_openai or args.openai_live,
        openai_live=args.openai_live,
    )
    payload = result.model_dump(mode="json")
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(
            json.dumps(
                {
                    "passed": payload["passed"],
                    "benchmark_id": payload["benchmark_id"],
                    "policy_ref": payload["policy_ref"],
                    "checks": [
                        {"name": check["name"], "passed": check["passed"]}
                        for check in payload["checks"]
                    ],
                    "safety_failures": payload["safety_failures"],
                },
                indent=2,
                sort_keys=True,
            )
        )
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
