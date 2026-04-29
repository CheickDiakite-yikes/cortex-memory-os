# Product Traceability Report

Last updated: 2026-04-29

`PRODUCT-TRACEABILITY-REPORT-001` summarizes where Cortex Memory OS stands
against the original roadmap, benchmark coverage, and current task board.

Source documents:

- `docs/product/vision.md`
- `docs/product/build-roadmap.md`
- `docs/product/original-goal-coverage.md`
- `docs/product/memory-palace-dashboard.md`
- `docs/architecture/context-pack-templates.md`
- `docs/architecture/document-to-skill-derivation.md`
- `docs/architecture/agent-runtime-trace.md`
- `docs/architecture/shadow-pointer-pointing.md`
- `docs/architecture/system-blueprint.md`
- `docs/ops/task-board.md`
- `docs/ops/benchmark-registry.md`
- `docs/ops/benchmark-plan.md`

## Current Build Readout

| Area | Status | Evidence | Gap |
| --- | --- | --- | --- |
| Engineering control plane | Validated | Task board, benchmark registry, research safety ledger, ADRs | Keep reports current after each slice. |
| Contract layer | Validated | Typed contracts, fixtures, `tests/test_contracts.py` | Add migration/versioning policy as schemas evolve. |
| Privacy + Safety Firewall | Validated | `SEC-INJECT-001`, `SEC-PII-001`, `CTX-HOSTILE-001` | Expand from synthetic text to app/browser/source classifiers. |
| Evidence Vault | Validated skeleton | `VAULT-RETENTION-001`, `VAULT-ENCRYPT-001`, `EVIDENCE-ELIGIBILITY-HANDOFF-001` | Replace dev cipher with production key management before real private data. |
| Scene, memory, and graph pipeline | Validated skeleton | `SCENE-SEGMENT-001`, `MEM-COMPILE-001`, `GRAPH-EDGE-001` | Add richer multimodal segmentation and contradiction handling. |
| Retrieval and context packs | Validated budgeted skeleton | `RETRIEVAL-SCORE-001`, `CONTEXT-PACK-001`, `CONTEXT-BUDGET-001`, scoped self-lesson suites | Add vector/sparse/graph fusion behind stable interfaces. |
| Memory Palace | Validated dashboard contract | `MEMORY-PALACE-001`, `PALACE-FLOW-001`, `MEMORY-PALACE-DASHBOARD-001`, self-lesson review flows | Build real dashboard UI shell over the safe view model. |
| Skill Forge | Validated skeleton plus document derivation | `SKILL-FORGE-002`, `SKILL-DOC-DERIVATION-001`, `SKILL-GATE-001`, `SKILL-EXECUTION-001` | Add candidate UI, workflow clustering, and skill success metrics. |
| Agent Gateway | Validated skeleton | `GATEWAY-CTX-001`, `GATEWAY-PALACE-001`, self-lesson and skill tools | Package Codex plugin and bridge additional clients. |
| Agent Runtime Trace | Validated contract | `RUNTIME-TRACE-001`, `docs/architecture/agent-runtime-trace.md`, runtime trace fixture | Persist real agent traces through the gateway and outcome engine. |
| Shadow Pointer | Partial with controls and pointing contract | `SHADOW-POINTER-001`, `SHADOW-POINTER-CONTROLS-001`, `POINTER-PROPOSAL-001`, static UI prototype | Build native overlay with live permissions and wire controls/proposals to real capture adapters. |
| Native Perception Bus | Envelope, firewall handoff, and evidence eligibility handoff validated; adapters not started | `PERCEPTION-EVENT-ENVELOPE-001`, `PERCEPTION-FIREWALL-HANDOFF-001`, `EVIDENCE-ELIGIBILITY-HANDOFF-001`, roadmap, and ADR | Add consented macOS app/window, accessibility, terminal, and browser adapters. |
| Robot readiness | Safety contract only | `ROBOT-SAFE-001`, initial threat model | Add simulation-first capability gates before physical integrations. |

## Coverage Snapshot

The current benchmark suite validates the original brain loop:

```text
Perception -> Evidence -> Memory -> Skill -> Agent Action -> Outcome -> Self-Improvement
```

`PRODUCT-GOAL-COVERAGE-001` checks that this loop, the rejected
`screen recording -> summary -> vector DB` anti-pattern, and the four
user-facing pillars remain visible in product and ops docs.

User-facing pillars:

- Shadow Pointer: partial prototype, state contract, native-ready control
  receipts, and display-only model pointing proposals.
- Memory Palace: validated inspect, explain, correct, delete, export,
  dashboard cards, export previews, action plans, and self-lesson review flows.
- Skill Forge: validated repeated-workflow detector, document-to-skill candidate
  derivation, maturity gates, rollback, audits, and draft-only execution.
- Agent Gateway: validated budgeted context packs, scoped actions, audit
  receipts, review queues, and draft skill execution.
- Agent Runtime Trace: validated tool calls, shell actions, browser actions,
  artifacts, approvals, retries, blocked hostile content, and outcome checks.

## Next Product Gaps

The next useful slices should move from contract depth into product surface and
capture realism:

1. Skill Forge candidate list using repeated-workflow, document-derivation, and
   maturity gates.
2. Codex plugin packaging for the MCP gateway and core skills.
3. Browser/terminal adapters with source-trust and redaction checks.
4. Shadow Pointer native overlay proof wired to live pause/delete/app-ignore
   commands and display-only pointing proposals.
5. Persist real agent runtime traces through the gateway and outcome engine.

## Update Rule

After each meaningful product slice:

- update `docs/ops/task-board.md`;
- update `docs/ops/benchmark-registry.md` with the latest artifact;
- add or adjust benchmark coverage before claiming a surface is validated;
- keep any partial or not-started product surface visible instead of hiding it
  inside prose.
