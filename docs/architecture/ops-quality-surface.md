# Ops Quality Surface

Last updated: 2026-04-30

`OPS-QUALITY-SURFACE-001` adds a local, aggregate-only status surface for the
latest verification run. It exists so the engineering loop can answer "what was
last proven?" without opening raw benchmark artifacts or copying case payloads
into docs, dashboards, or agent context.

## Contract

`uv run cortex-ops-quality` reads the newest ignored benchmark artifact under
`benchmarks/runs/` and returns:

- run ID;
- artifact file name, not an absolute local path;
- total, passed, and failed case counts;
- suite count;
- failed case/suite identifiers after strict identifier sanitization;
- a redaction boundary receipt.

It never returns:

- benchmark case summaries;
- metrics payloads;
- evidence payloads;
- raw refs;
- fake or real secrets;
- hostile prompt text;
- private local absolute paths.

## Safety Boundary

Policy ref: `policy_ops_quality_surface_v1`.

The output model keeps `raw_case_payloads_included=false`,
`artifact_payload_redacted=true`, and `content_redacted=true`. If a poisoned
artifact tries to put hostile text into a case ID or suite ID, the surface
replaces that identifier with a fixed safe placeholder instead of echoing it.

This surface is intentionally narrower than the benchmark artifact. It is a
status receipt, not a debugging transcript.
