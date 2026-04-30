"""Sanitized operations quality summaries for recent verification runs."""

from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, model_validator

from cortex_memory_os.contracts import StrictModel

OPS_QUALITY_SURFACE_ID = "OPS-QUALITY-SURFACE-001"
OPS_QUALITY_POLICY_REF = "policy_ops_quality_surface_v1"

_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,127}$")
_BENCH_ARTIFACT_RE = re.compile(r"^bench_\d{8}T\d{6}Z\.json$")


class OpsQualitySummary(StrictModel):
    """Aggregate-only summary of a benchmark run.

    The model intentionally carries counts, safe identifiers, and policy refs
    only. It never includes benchmark case summaries, metrics payloads,
    evidence payloads, raw refs, or local absolute paths.
    """

    summary_id: str = OPS_QUALITY_SURFACE_ID
    latest_run_id: str
    created_at: datetime
    artifact_name: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    suite_count: int
    failed_suite_ids: list[str] = Field(default_factory=list)
    failed_case_ids: list[str] = Field(default_factory=list)
    invalid_identifier_count: int = 0
    all_passed: bool
    artifact_payload_redacted: bool = True
    raw_case_payloads_included: bool = False
    content_redacted: bool = True
    generated_at: datetime
    policy_refs: list[str] = Field(default_factory=lambda: [OPS_QUALITY_POLICY_REF])

    @model_validator(mode="after")
    def _validate_redacted_boundary(self) -> "OpsQualitySummary":
        if self.raw_case_payloads_included:
            raise ValueError("ops quality summaries must not include raw case payloads")
        if not self.artifact_payload_redacted or not self.content_redacted:
            raise ValueError("ops quality summaries must stay redacted")
        if OPS_QUALITY_POLICY_REF not in self.policy_refs:
            raise ValueError("ops quality summary must reference its policy")
        if self.total_cases != self.passed_cases + self.failed_cases:
            raise ValueError("case counts must add up")
        if self.failed_cases == 0 and (self.failed_case_ids or self.failed_suite_ids):
            raise ValueError("failed identifiers require failed cases")
        return self


def load_latest_ops_quality_summary(
    run_dir: Path,
    *,
    now: datetime | None = None,
) -> OpsQualitySummary:
    """Load the newest benchmark artifact and return an aggregate-only summary."""

    paths = sorted(run_dir.glob("bench_*.json"))
    if not paths:
        raise FileNotFoundError(f"no benchmark artifacts found in {run_dir}")
    return summarize_ops_quality_artifact(paths[-1], now=now)


def summarize_ops_quality_artifact(
    path: Path,
    *,
    now: datetime | None = None,
) -> OpsQualitySummary:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return summarize_ops_quality_payload(
        payload,
        artifact_name=path.name,
        now=now,
    )


def summarize_ops_quality_payload(
    payload: dict[str, Any],
    *,
    artifact_name: str,
    now: datetime | None = None,
) -> OpsQualitySummary:
    cases = payload.get("case_results", [])
    if not isinstance(cases, list):
        cases = []

    safe_suites: set[str] = set()
    failed_suites: set[str] = set()
    failed_cases: list[str] = []
    invalid_identifier_count = 0
    passed_cases = 0
    failed_case_count = 0

    for raw_case in cases:
        if not isinstance(raw_case, dict):
            invalid_identifier_count += 1
            failed_case_count += 1
            failed_cases.append("invalid_case_payload")
            failed_suites.add("invalid_suite_id")
            safe_suites.add("invalid_suite_id")
            continue

        suite_id, suite_invalid = _safe_identifier(raw_case.get("suite"), "invalid_suite_id")
        case_id, case_invalid = _safe_identifier(raw_case.get("case_id"), "invalid_case_id")
        invalid_identifier_count += int(suite_invalid) + int(case_invalid)
        safe_suites.add(suite_id)

        if raw_case.get("passed") is True:
            passed_cases += 1
        else:
            failed_case_count += 1
            failed_suites.add(suite_id)
            failed_cases.append(case_id)

    total_cases = len(cases)
    run_id, run_id_invalid = _safe_identifier(payload.get("run_id"), "invalid_run_id")
    invalid_identifier_count += int(run_id_invalid)
    created_at = _parse_datetime(payload.get("created_at"))

    return OpsQualitySummary(
        latest_run_id=run_id,
        created_at=created_at,
        artifact_name=_safe_artifact_name(artifact_name),
        total_cases=total_cases,
        passed_cases=passed_cases,
        failed_cases=failed_case_count,
        suite_count=len(safe_suites),
        failed_suite_ids=sorted(failed_suites),
        failed_case_ids=sorted(failed_cases),
        invalid_identifier_count=invalid_identifier_count,
        all_passed=total_cases > 0 and failed_case_count == 0,
        generated_at=now or datetime.now(UTC),
    )


def ops_quality_report(run_dir: Path, output_format: Literal["markdown", "json"]) -> str:
    summary = load_latest_ops_quality_summary(run_dir)
    if output_format == "markdown":
        return render_ops_quality_markdown(summary)
    if output_format == "json":
        return json.dumps(summary.model_dump(mode="json"), indent=2, sort_keys=True) + "\n"
    raise ValueError(f"unsupported ops quality format: {output_format}")


def render_ops_quality_markdown(summary: OpsQualitySummary) -> str:
    lines = [
        "# Cortex Ops Quality",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Run | `{summary.latest_run_id}` |",
        f"| Created | `{summary.created_at.isoformat()}` |",
        f"| Artifact | `{summary.artifact_name}` |",
        f"| Cases | `{summary.passed_cases}/{summary.total_cases}` passed |",
        f"| Suites | `{summary.suite_count}` |",
        f"| Failed cases | `{summary.failed_cases}` |",
        f"| Invalid identifiers sanitized | `{summary.invalid_identifier_count}` |",
        f"| Raw case payloads included | `{str(summary.raw_case_payloads_included).lower()}` |",
        f"| Artifact payload redacted | `{str(summary.artifact_payload_redacted).lower()}` |",
        "",
    ]
    if summary.failed_case_ids:
        lines.extend(["## Failed Safe Identifiers", ""])
        for case_id in summary.failed_case_ids:
            lines.append(f"- `{case_id}`")
        lines.append("")
    lines.extend(
        [
            "## Policy",
            "",
            f"- `{OPS_QUALITY_POLICY_REF}`",
        ]
    )
    return "\n".join(lines) + "\n"


def _safe_identifier(value: Any, fallback: str) -> tuple[str, bool]:
    if not isinstance(value, str):
        return fallback, True
    stripped = value.strip()
    if _SAFE_ID_RE.fullmatch(stripped):
        return stripped, False
    return fallback, True


def _safe_artifact_name(value: str) -> str:
    if _BENCH_ARTIFACT_RE.fullmatch(value):
        return value
    return "benchmark_artifact.json"


def _parse_datetime(value: Any) -> datetime:
    if not isinstance(value, str):
        return datetime.fromtimestamp(0, tz=UTC)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return datetime.fromtimestamp(0, tz=UTC)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render a sanitized aggregate Cortex ops quality summary."
    )
    parser.add_argument("--run-dir", type=Path, default=Path("benchmarks/runs"))
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format.",
    )
    args = parser.parse_args(argv)

    print(ops_quality_report(args.run_dir, args.format), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
