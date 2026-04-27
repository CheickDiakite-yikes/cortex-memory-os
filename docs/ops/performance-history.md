# Performance History

Last updated: 2026-04-27

Code: `src/cortex_memory_os/benchmark_history.py`

The benchmark runner now emits `PERF-LAT-001` p50/p95 metrics for synthetic
SQLite memory writes and searches. Performance history compares those metrics
across sanitized benchmark artifacts so regressions are visible before the
system grows more complicated.

## What Is Tracked

- Write p50.
- Write p95.
- Search p50.
- Search p95.
- Latest delta from the previous run.
- Regression flag.

## Regression Rule

The initial rule is intentionally conservative:

- No regression if the latest p95 is lower than or equal to the previous p95.
- Regression if p95 increases by more than `max(10ms, previous_p95 * 0.5)`.

This avoids noise while the synthetic suite is still tiny.

## Usage

Use `load_latency_history(Path("benchmarks/runs"))` to parse local benchmark
artifacts and `render_latency_history_markdown(summary)` to produce a report.

The local ops command is:

```bash
uv run cortex-bench-history
uv run cortex-bench-history --format json
uv run cortex-bench-history --fail-on-regression
```

The command only renders `PERF-LAT-001` metrics and artifact metadata. It does
not copy arbitrary benchmark evidence payloads into the report.

`benchmarks/runs/` remains ignored because raw artifacts are local evidence.
Commit-safe summaries belong in `docs/ops/benchmark-registry.md`.

## Benchmark

`PERF-HISTORY-001` verifies:

- latency artifacts are parsed in chronological order;
- latest and previous runs are compared;
- p95 deltas are reported;
- large regressions are flagged;
- markdown reports do not require private data.

`GATEWAY-HISTORY-001` verifies:

- the local command is registered as `cortex-bench-history`;
- Markdown and JSON reports can be rendered from sanitized artifacts;
- non-latency payloads are omitted from reports;
- `--fail-on-regression` can make the command fail closed in automation.
