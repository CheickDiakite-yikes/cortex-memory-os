# Context Fusion Stress

Last updated: 2026-04-30

`CONTEXT-FUSION-STRESS-001` hardens the hybrid context-fusion path with a
larger synthetic mix of safe, hostile, secret, and malformed candidates.

## Contract

The stress suite verifies that `build_context_fusion_diagnostics`:

- produces deterministic diagnostics when input order changes;
- caps included diagnostics by the requested limit;
- excludes hostile candidates with `prompt_injection_risk`;
- excludes secret candidates with `privacy_risk`;
- rejects raw source refs before diagnostics are created;
- keeps all returned diagnostics metadata-only.

## Redaction Gate

Diagnostics may expose memory IDs, bounded scores, component score labels,
reason tags, source-ref counts, and policy refs. They must not expose memory
content, hostile prompt text, `.env.local`, external URLs, raw refs, or source
refs.

This stress test is deliberately synthetic and local-only. It adds pressure to
the retrieval-debugging surface without widening context-pack scope or adding a
second memory-content lane.
