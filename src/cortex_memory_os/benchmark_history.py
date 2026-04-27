"""Utilities for comparing benchmark latency history."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

PERF_LATENCY_SUITE = "PERF-LAT-001"


@dataclass(frozen=True)
class LatencyHistoryEntry:
    run_id: str
    created_at: datetime
    artifact_path: str
    write_p50_ms: float
    write_p95_ms: float
    search_p50_ms: float
    search_p95_ms: float


@dataclass(frozen=True)
class LatencyHistorySummary:
    entries: tuple[LatencyHistoryEntry, ...]
    latest: LatencyHistoryEntry | None
    previous: LatencyHistoryEntry | None
    search_p95_delta_ms: float | None
    write_p95_delta_ms: float | None
    regression_detected: bool


def load_latency_history(run_dir: Path) -> LatencyHistorySummary:
    paths = sorted(run_dir.glob("bench_*.json"))
    return summarize_latency_history(paths)


def summarize_latency_history(paths: list[Path]) -> LatencyHistorySummary:
    entries = sorted(
        [
            entry
            for path in paths
            for entry in _entries_from_artifact(path)
        ],
        key=lambda entry: (entry.created_at, entry.run_id),
    )
    latest = entries[-1] if entries else None
    previous = entries[-2] if len(entries) >= 2 else None
    search_delta = (
        latest.search_p95_ms - previous.search_p95_ms
        if latest is not None and previous is not None
        else None
    )
    write_delta = (
        latest.write_p95_ms - previous.write_p95_ms
        if latest is not None and previous is not None
        else None
    )
    regression = bool(
        latest is not None
        and previous is not None
        and (
            _is_regression(latest.search_p95_ms, previous.search_p95_ms)
            or _is_regression(latest.write_p95_ms, previous.write_p95_ms)
        )
    )
    return LatencyHistorySummary(
        entries=tuple(entries),
        latest=latest,
        previous=previous,
        search_p95_delta_ms=search_delta,
        write_p95_delta_ms=write_delta,
        regression_detected=regression,
    )


def render_latency_history_markdown(summary: LatencyHistorySummary) -> str:
    lines = [
        "# Benchmark Latency History",
        "",
        "| Run | Created | Write p95 ms | Search p95 ms | Artifact |",
        "| --- | --- | --- | --- | --- |",
    ]
    for entry in summary.entries:
        lines.append(
            "| "
            f"{entry.run_id} | "
            f"{entry.created_at.isoformat()} | "
            f"{entry.write_p95_ms:.4f} | "
            f"{entry.search_p95_ms:.4f} | "
            f"{entry.artifact_path} |"
        )
    if summary.latest is not None and summary.previous is not None:
        lines.extend(
            [
                "",
                "## Latest Delta",
                "",
                f"- Write p95 delta: {summary.write_p95_delta_ms:.4f} ms",
                f"- Search p95 delta: {summary.search_p95_delta_ms:.4f} ms",
                f"- Regression detected: {str(summary.regression_detected).lower()}",
            ]
        )
    return "\n".join(lines) + "\n"


def latency_history_report(run_dir: Path, output_format: str = "markdown") -> str:
    summary = load_latency_history(run_dir)
    if output_format == "markdown":
        return render_latency_history_markdown(summary)
    if output_format == "json":
        return json.dumps(
            latency_history_summary_dict(summary),
            indent=2,
            sort_keys=True,
        ) + "\n"
    raise ValueError(f"unsupported latency history format: {output_format}")


def latency_history_summary_dict(summary: LatencyHistorySummary) -> dict[str, Any]:
    return {
        "entry_count": len(summary.entries),
        "latest_run_id": summary.latest.run_id if summary.latest else None,
        "previous_run_id": summary.previous.run_id if summary.previous else None,
        "search_p95_delta_ms": summary.search_p95_delta_ms,
        "write_p95_delta_ms": summary.write_p95_delta_ms,
        "regression_detected": summary.regression_detected,
        "entries": [
            {
                "run_id": entry.run_id,
                "created_at": entry.created_at.isoformat(),
                "artifact_path": entry.artifact_path,
                "write_p50_ms": entry.write_p50_ms,
                "write_p95_ms": entry.write_p95_ms,
                "search_p50_ms": entry.search_p50_ms,
                "search_p95_ms": entry.search_p95_ms,
            }
            for entry in summary.entries
        ],
    }


def _entries_from_artifact(path: Path) -> list[LatencyHistoryEntry]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    run_id = str(payload["run_id"])
    created_at = datetime.fromisoformat(str(payload["created_at"]).replace("Z", "+00:00"))
    entries: list[LatencyHistoryEntry] = []
    for case in payload.get("case_results", []):
        if case.get("suite") != PERF_LATENCY_SUITE:
            continue
        metrics: dict[str, Any] = case.get("metrics", {})
        entries.append(
            LatencyHistoryEntry(
                run_id=run_id,
                created_at=created_at,
                artifact_path=str(path),
                write_p50_ms=float(metrics["write_p50_ms"]),
                write_p95_ms=float(metrics["write_p95_ms"]),
                search_p50_ms=float(metrics["search_p50_ms"]),
                search_p95_ms=float(metrics["search_p95_ms"]),
            )
        )
    return entries


def _is_regression(latest: float, previous: float) -> bool:
    if latest <= previous:
        return False
    return latest - previous > max(10.0, previous * 0.5)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render sanitized Cortex benchmark latency history."
    )
    parser.add_argument("--run-dir", type=Path, default=Path("benchmarks/runs"))
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format.",
    )
    parser.add_argument(
        "--fail-on-regression",
        action="store_true",
        help="Return a non-zero status if the latest latency run regressed.",
    )
    args = parser.parse_args(argv)

    summary = load_latency_history(args.run_dir)
    print(latency_history_report(args.run_dir, args.format), end="")
    if args.fail_on_regression and summary.regression_detected:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
