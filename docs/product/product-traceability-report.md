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
- `docs/product/skill-success-metrics.md`
- `docs/product/cortex-dashboard-shell.md`
- `docs/product/dashboard-gateway-actions.md`
- `docs/research/frontier-agent-plugin-lessons-2026-04-29.md`
- `docs/ops/plugin-install-smoke.md`
- `docs/ops/codex-plugin-real-enable.md`
- `docs/architecture/native-shadow-pointer-overlay.md`
- `docs/architecture/native-capture-permission-smoke.md`
- `docs/architecture/shadow-pointer-capture-wiring.md`
- `docs/architecture/live-browser-terminal-adapters.md`
- `docs/architecture/local-adapter-endpoint.md`
- `docs/architecture/manual-adapter-proof.md`
- `docs/architecture/macos-perception-adapter-contracts.md`
- `docs/architecture/browser-terminal-adapter-contracts.md`
- `docs/architecture/context-pack-templates.md`
- `docs/architecture/hybrid-context-fusion-index.md`
- `docs/architecture/local-fusion-adapters.md`
- `docs/architecture/retrieval-explanation-receipts.md`
- `docs/architecture/document-to-skill-derivation.md`
- `docs/architecture/swarm-governance.md`
- `docs/architecture/robot-spatial-safety.md`
- `docs/architecture/agent-runtime-trace.md`
- `docs/architecture/outcome-postmortem-trace-handoff.md`
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
| Retrieval and context packs | Validated budgeted skeleton plus hybrid fusion interface, local fusion adapters, and redacted explanation receipts | `RETRIEVAL-SCORE-001`, `CONTEXT-FUSION-INDEX-STUB-001`, `REAL-VECTOR-INDEX-ADAPTER-001`, `RETRIEVAL-EXPLANATION-RECEIPTS-001`, `CONTEXT-PACK-001`, `CONTEXT-BUDGET-001`, scoped self-lesson suites | Wire local fusion adapter diagnostics into context packs and show receipts in the dashboard. |
| Memory Palace | Validated dashboard contract, static UI shell, and read-only gateway action receipts | `MEMORY-PALACE-001`, `PALACE-FLOW-001`, `MEMORY-PALACE-DASHBOARD-001`, `MEMORY-PALACE-SKILL-FORGE-UI-001`, `DASHBOARD-GATEWAY-ACTIONS-001`, self-lesson review flows | Wire safe read-only calls to the local gateway runtime; keep correction/delete/export confirmation-gated. |
| Skill Forge | Validated skeleton plus candidate list, success metrics, static UI shell, and read-only review receipts | `SKILL-FORGE-002`, `SKILL-DOC-DERIVATION-001`, `SKILL-FORGE-LIST-001`, `SKILL-SUCCESS-METRICS-001`, `MEMORY-PALACE-SKILL-FORGE-UI-001`, `DASHBOARD-GATEWAY-ACTIONS-001`, `SKILL-GATE-001`, `SKILL-EXECUTION-001` | Add workflow clustering and live draft-only execution previews behind receipts. |
| Agent Gateway | Validated skeleton plus install-smoked and approval-gated Codex plugin package | `GATEWAY-CTX-001`, `GATEWAY-PALACE-001`, self-lesson and skill tools, `CODEX-PLUGIN-001`, `PLUGIN-INSTALL-SMOKE-001`, `CODEX-PLUGIN-REAL-ENABLE-001`, `plugins/cortex-memory-os` | Bridge additional clients and keep real user config changes explicit. |
| Agent Runtime Trace | Validated contract, gateway persistence receipts, and safe postmortem handoff | `RUNTIME-TRACE-001`, `GATEWAY-TRACE-PERSISTENCE-001`, `OUTCOME-POSTMORTEM-TRACE-001`, `docs/architecture/agent-runtime-trace.md`, `docs/architecture/outcome-postmortem-trace-handoff.md`, runtime trace fixture, SQLite persistence, `runtime_trace.record`, `runtime_trace.get`, `runtime_trace.list` | Expose postmortem compilation through the gateway and connect it to self-improvement scoring. |
| Swarm Governance | Validated contract | `SWARM-GOVERNANCE-001`, `docs/adr/0005-swarm-governance-boundary.md` | Wire future parallel agents through governed gateway execution instead of direct delegation. |
| Shadow Pointer | Validated native proof, static prototype, capture receipt wiring, and read-only permission status smoke | `SHADOW-POINTER-001`, `SHADOW-POINTER-CONTROLS-001`, `POINTER-PROPOSAL-001`, `SHADOW-POINTER-NATIVE-001`, `NATIVE-CAPTURE-PERMISSION-SMOKE-001`, `SHADOW-POINTER-CAPTURE-WIRING-001`, static UI prototype, `native/macos-shadow-pointer` | Feed live local endpoint and permission-status receipts into the native overlay panel. |
| Native Perception Bus | Envelope, firewall handoff, evidence eligibility, browser/terminal contracts, macOS app/window and Accessibility contracts, live adapter smoke artifacts, local adapter endpoint, manual browser/terminal proof, Shadow Pointer capture receipt wiring, and native permission-status smoke validated | `PERCEPTION-EVENT-ENVELOPE-001`, `PERCEPTION-FIREWALL-HANDOFF-001`, `EVIDENCE-ELIGIBILITY-HANDOFF-001`, `NATIVE-CAPTURE-PERMISSION-SMOKE-001`, `SHADOW-POINTER-CAPTURE-WIRING-001`, `MACOS-PERCEPTION-ADAPTERS-001`, `BROWSER-TERMINAL-ADAPTERS-001`, `LIVE-BROWSER-TERMINAL-ADAPTERS-001`, `LOCAL-ADAPTER-ENDPOINT-001`, `MANUAL-ADAPTER-PROOF-001`, roadmap, and ADR | Wire the status receipt to onboarding and the Shadow Pointer without enabling real capture. |
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
  proof, plus adapter-to-overlay capture receipts and read-only native
  permission-status receipts.
- Memory Palace: validated inspect, explain, correct, delete, export,
  dashboard cards, export previews, action plans, self-lesson review flows, and
  the Real Memory Palace and Skill Forge UI shell using the safe dashboard view
  models, plus read-only dashboard gateway receipts.
- Skill Forge: validated repeated-workflow detector, document-to-skill candidate
  derivation, candidate-list cards, success/failure metrics, maturity gates,
  rollback, audits, and draft-only execution, plus the shared dashboard shell.
- Agent Gateway: validated budgeted context packs, scoped actions, audit
  receipts, retrieval explanation receipts, review queues, draft skill
  execution, and repo-local Codex plugin packaging plus temporary cache-shaped
  plugin install/discovery smoke and approval-gated real enable/rollback plan.
- Retrieval Fusion: validated dependency-free semantic, sparse, and graph
  adapters under `REAL-VECTOR-INDEX-ADAPTER-001` that feed redacted hybrid
  fusion candidates without model services or network calls.
- Agent Runtime Trace: validated tool calls, shell actions, browser actions,
  artifacts, approvals, retries, blocked hostile content, outcome checks, and
  gateway persistence receipts that return metadata without event summary text,
  plus `OUTCOME-POSTMORTEM-TRACE-001` postmortems that preserve safe trace
  metadata while keeping event summaries out of self-improvement instruction
  lanes.
- Swarm Governance: validated source isolation, disjoint write scopes, budget
  enforcement, cancellation receipts, and non-autonomous task ceilings.
- Robot readiness: validated capability refs, workspace bounds, affordances,
  material constraints, spatial hazards, simulation status, emergency stop,
  approval, and bounded force/speed metadata for future embodied actions.
- Native Perception Bus: validated terminal/browser and macOS app/window plus
  Accessibility adapter contracts that preserve consent, source trust,
  prompt-injection flags, redaction, firewall handoff, Evidence Vault
  eligibility, live smoke artifacts, local adapter endpoint, manual
  browser/terminal proof, Shadow Pointer capture receipt wiring, and native
  permission-status smoke before real capture exists.

## Next Product Gaps

The next useful slices should move from contract depth into product surface and
capture realism:

1. Real browser/terminal adapters now have validated local endpoint support and
   manual browser/terminal proof. Live browser/terminal adapter smoke artifacts
   and consented macOS app/window plus Accessibility contracts are also in
   place; capture receipts and native permission-status smoke are now wired.
   Next is permission-status onboarding without starting capture.
2. Wire the Shadow Pointer native overlay proof to live permission-status and
   local endpoint receipt streams.
3. Execute the read-only dashboard gateway receipts against the local gateway
   runtime, with browser proof and no mutation paths enabled.
4. Persist real agent runtime traces into outcome postmortems through the
   gateway and feed them into self-improvement scoring.
5. Wire local vector, sparse, and graph adapter diagnostics into context packs
   without changing the redacted result contract.
6. Surface `RETRIEVAL-EXPLANATION-RECEIPTS-001` in the dashboard context/debug
   panels without adding memory content or source refs.
7. Surface `SKILL-SUCCESS-METRICS-001` in Skill Forge dashboard cards and
   promotion-review flows without changing autonomy.
8. Additional client bridges after the Codex plugin path is user-approved in a
   real environment.

## Update Rule

After each meaningful product slice:

- update `docs/ops/task-board.md`;
- update `docs/ops/benchmark-registry.md` with the latest artifact;
- add or adjust benchmark coverage before claiming a surface is validated;
- keep any partial or not-started product surface visible instead of hiding it
  inside prose.
