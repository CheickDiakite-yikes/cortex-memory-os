# Product Traceability Report

Last updated: 2026-04-30

`PRODUCT-TRACEABILITY-REPORT-001` summarizes where Cortex Memory OS stands
against the original roadmap, benchmark coverage, and current task board.

Source documents:

- `docs/product/vision.md`
- `docs/product/build-roadmap.md`
- `docs/product/original-goal-coverage.md`
- `docs/product/memory-palace-dashboard.md`
- `docs/product/skill-forge-candidate-list.md`
- `docs/product/cortex-dashboard-shell.md`
- `docs/research/frontier-agent-plugin-lessons-2026-04-29.md`
- `docs/ops/plugin-install-smoke.md`
- `docs/architecture/native-shadow-pointer-overlay.md`
- `docs/architecture/live-browser-terminal-adapters.md`
- `docs/architecture/local-adapter-endpoint.md`
- `docs/architecture/manual-adapter-proof.md`
- `docs/architecture/macos-perception-adapter-contracts.md`
- `docs/architecture/browser-terminal-adapter-contracts.md`
- `docs/architecture/context-pack-templates.md`
- `docs/architecture/document-to-skill-derivation.md`
- `docs/architecture/swarm-governance.md`
- `docs/architecture/robot-spatial-safety.md`
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
| Memory Palace | Validated dashboard contract plus static UI shell | `MEMORY-PALACE-001`, `PALACE-FLOW-001`, `MEMORY-PALACE-DASHBOARD-001`, `MEMORY-PALACE-SKILL-FORGE-UI-001`, self-lesson review flows | Wire cards to live gateway-backed review actions after consent and audit paths are visible. |
| Skill Forge | Validated skeleton plus candidate list and static UI shell | `SKILL-FORGE-002`, `SKILL-DOC-DERIVATION-001`, `SKILL-FORGE-LIST-001`, `MEMORY-PALACE-SKILL-FORGE-UI-001`, `SKILL-GATE-001`, `SKILL-EXECUTION-001` | Add workflow clustering, skill success metrics, and live draft-only execution previews. |
| Agent Gateway | Validated skeleton plus install-smoked Codex plugin package | `GATEWAY-CTX-001`, `GATEWAY-PALACE-001`, self-lesson and skill tools, `CODEX-PLUGIN-001`, `PLUGIN-INSTALL-SMOKE-001`, `plugins/cortex-memory-os` | Bridge additional clients and validate real user-approved plugin enable flows. |
| Agent Runtime Trace | Validated contract | `RUNTIME-TRACE-001`, `docs/architecture/agent-runtime-trace.md`, runtime trace fixture | Persist real agent traces through the gateway and outcome engine. |
| Swarm Governance | Validated contract | `SWARM-GOVERNANCE-001`, `docs/adr/0005-swarm-governance-boundary.md` | Wire future parallel agents through governed gateway execution instead of direct delegation. |
| Shadow Pointer | Validated native proof plus static prototype | `SHADOW-POINTER-001`, `SHADOW-POINTER-CONTROLS-001`, `POINTER-PROPOSAL-001`, `SHADOW-POINTER-NATIVE-001`, static UI prototype, `native/macos-shadow-pointer` | Wire native overlay to live permissions and real capture adapters. |
| Native Perception Bus | Envelope, firewall handoff, evidence eligibility, browser/terminal contracts, macOS app/window and Accessibility contracts, live adapter smoke artifacts, local adapter endpoint, and manual browser/terminal proof validated | `PERCEPTION-EVENT-ENVELOPE-001`, `PERCEPTION-FIREWALL-HANDOFF-001`, `EVIDENCE-ELIGIBILITY-HANDOFF-001`, `MACOS-PERCEPTION-ADAPTERS-001`, `BROWSER-TERMINAL-ADAPTERS-001`, `LIVE-BROWSER-TERMINAL-ADAPTERS-001`, `LOCAL-ADAPTER-ENDPOINT-001`, `MANUAL-ADAPTER-PROOF-001`, roadmap, and ADR | Wire macOS receipts into Shadow Pointer status before enabling real capture. |
| Robot readiness | Spatial safety contract validated | `ROBOT-SAFE-001`, `docs/architecture/robot-spatial-safety.md`, initial threat model | Keep physical integrations blocked until real simulation, capability, emergency-stop, and audit adapters exist. |
| Production autonomy and real capture | Not started | No production capture daemon, no autonomous skill runner, and no robot executor are enabled | Keep disabled until consent UI, local endpoint, audit, rollback, and emergency-stop boundaries exist. |

## Coverage Snapshot

The current benchmark suite validates the original brain loop:

```text
Perception -> Evidence -> Memory -> Skill -> Agent Action -> Outcome -> Self-Improvement
```

`PRODUCT-GOAL-COVERAGE-001` checks that this loop, the rejected
`screen recording -> summary -> vector DB` anti-pattern, and the four
user-facing pillars remain visible in product and ops docs.

User-facing pillars:

- Shadow Pointer: static prototype, state contract, native-ready control
  receipts, display-only model pointing proposals, and SwiftPM native overlay
  proof.
- Memory Palace: validated inspect, explain, correct, delete, export,
  dashboard cards, export previews, action plans, self-lesson review flows, and
  the Real Memory Palace and Skill Forge UI shell using the safe dashboard view
  models.
- Skill Forge: validated repeated-workflow detector, document-to-skill candidate
  derivation, candidate-list cards, maturity gates, rollback, audits, and
  draft-only execution, plus the shared dashboard shell.
- Agent Gateway: validated budgeted context packs, scoped actions, audit
  receipts, review queues, draft skill execution, and repo-local Codex plugin
  packaging plus temporary cache-shaped plugin install/discovery smoke.
- Agent Runtime Trace: validated tool calls, shell actions, browser actions,
  artifacts, approvals, retries, blocked hostile content, and outcome checks.
- Swarm Governance: validated source isolation, disjoint write scopes, budget
  enforcement, cancellation receipts, and non-autonomous task ceilings.
- Robot readiness: validated capability refs, workspace bounds, affordances,
  material constraints, spatial hazards, simulation status, emergency stop,
  approval, and bounded force/speed metadata for future embodied actions.
- Native Perception Bus: validated terminal/browser and macOS app/window plus
  Accessibility adapter contracts that preserve consent, source trust,
  prompt-injection flags, redaction, firewall handoff, Evidence Vault
  eligibility, live smoke artifacts, local adapter endpoint, and manual
  browser/terminal proof before real capture exists.

## Next Product Gaps

The next useful slices should move from contract depth into product surface and
capture realism:

1. Real browser/terminal adapters now have validated local endpoint support and
   manual browser/terminal proof. Live browser/terminal adapter smoke artifacts
   and consented macOS app/window plus Accessibility contracts are also in
   place; next is wiring visible capture receipts.
2. Wire the Shadow Pointer native overlay proof to live permissions and capture
   adapter receipts.
3. Live gateway-backed dashboard interactions for the static Memory Palace and
   Skill Forge UI shell.
4. User-approved real Codex plugin enable/rollback path beyond temp smoke.
5. Persist real agent runtime traces through the gateway and outcome engine.

## Update Rule

After each meaningful product slice:

- update `docs/ops/task-board.md`;
- update `docs/ops/benchmark-registry.md` with the latest artifact;
- add or adjust benchmark coverage before claiming a surface is validated;
- keep any partial or not-started product surface visible instead of hiding it
  inside prose.
