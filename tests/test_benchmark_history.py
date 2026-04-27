import json
from pathlib import Path

from cortex_memory_os.benchmark_history import (
    PERF_LATENCY_SUITE,
    latency_history_report,
    main as latency_history_main,
    render_latency_history_markdown,
    summarize_latency_history,
)


def _write_artifact(path: Path, run_id: str, created_at: str, write_p95: float, search_p95: float):
    path.write_text(
        json.dumps(
            {
                "run_id": run_id,
                "created_at": created_at,
                "passed": True,
                "case_results": [
                    {
                        "case_id": "PERF-LAT-001/sqlite_memory_write_search",
                        "suite": PERF_LATENCY_SUITE,
                        "passed": True,
                        "summary": "latency",
                        "metrics": {
                            "write_p50_ms": write_p95 / 2,
                            "write_p95_ms": write_p95,
                            "search_p50_ms": search_p95 / 2,
                            "search_p95_ms": search_p95,
                        },
                        "evidence": {},
                    },
                    {
                        "case_id": "PRIVATE-NON-LATENCY",
                        "suite": "PRIVATE-NON-LATENCY",
                        "passed": True,
                        "summary": "must not appear in history report",
                        "metrics": {},
                        "evidence": {
                            "raw_text": "CORTEX_FAKE_TOKEN_abc12345SECRET"
                        },
                    }
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_summarize_latency_history_compares_latest_to_previous(tmp_path):
    first = tmp_path / "bench_20260427T190000Z.json"
    second = tmp_path / "bench_20260427T191000Z.json"
    _write_artifact(first, "bench_old", "2026-04-27T19:00:00Z", 0.5, 0.8)
    _write_artifact(second, "bench_new", "2026-04-27T19:10:00Z", 0.75, 1.1)

    summary = summarize_latency_history([second, first])
    markdown = render_latency_history_markdown(summary)

    assert len(summary.entries) == 2
    assert summary.previous.run_id == "bench_old"
    assert summary.latest.run_id == "bench_new"
    assert summary.write_p95_delta_ms == 0.25
    assert summary.search_p95_delta_ms == 0.30000000000000004
    assert summary.regression_detected is False
    assert "bench_new" in markdown
    assert "Regression detected: false" in markdown


def test_summarize_latency_history_flags_large_regression(tmp_path):
    first = tmp_path / "bench_20260427T190000Z.json"
    second = tmp_path / "bench_20260427T191000Z.json"
    _write_artifact(first, "bench_old", "2026-04-27T19:00:00Z", 20.0, 20.0)
    _write_artifact(second, "bench_new", "2026-04-27T19:10:00Z", 35.0, 20.0)

    summary = summarize_latency_history([first, second])

    assert summary.regression_detected is True


def test_latency_history_report_omits_non_latency_artifact_payload(tmp_path):
    artifact = tmp_path / "bench_20260427T190000Z.json"
    _write_artifact(artifact, "bench_old", "2026-04-27T19:00:00Z", 0.5, 0.8)

    markdown = latency_history_report(tmp_path, output_format="markdown")
    json_report = latency_history_report(tmp_path, output_format="json")

    assert "bench_old" in markdown
    assert '"entry_count": 1' in json_report
    assert "CORTEX_FAKE_TOKEN_abc12345SECRET" not in markdown
    assert "CORTEX_FAKE_TOKEN_abc12345SECRET" not in json_report
    assert "PRIVATE-NON-LATENCY" not in json_report


def test_latency_history_cli_can_fail_on_regression(tmp_path, capsys):
    first = tmp_path / "bench_20260427T190000Z.json"
    second = tmp_path / "bench_20260427T191000Z.json"
    _write_artifact(first, "bench_old", "2026-04-27T19:00:00Z", 20.0, 20.0)
    _write_artifact(second, "bench_new", "2026-04-27T19:10:00Z", 35.0, 20.0)

    exit_code = latency_history_main(
        [
            "--run-dir",
            str(tmp_path),
            "--format",
            "json",
            "--fail-on-regression",
        ]
    )
    output = capsys.readouterr().out

    assert exit_code == 2
    assert '"regression_detected": true' in output
    assert "CORTEX_FAKE_TOKEN_abc12345SECRET" not in output
