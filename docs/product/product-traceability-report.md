# Product Traceability Report

Last updated: 2026-05-02

`PRODUCT-TRACEABILITY-REPORT-001` summarizes where Cortex Memory OS stands
against the original roadmap, benchmark coverage, and current task board.

Source documents:

- `docs/product/vision.md`
- `docs/product/build-roadmap.md`
- `docs/product/original-goal-coverage.md`
- `docs/product/memory-palace-dashboard.md`
- `docs/product/skill-forge-candidate-list.md`
- `docs/product/skill-success-metrics.md`
- `docs/product/skill-metrics-dashboard-surface.md`
- `docs/product/retrieval-receipts-dashboard-surface.md`
- `docs/product/cortex-dashboard-shell.md`
- `docs/product/dashboard-gateway-actions.md`
- `docs/architecture/dashboard-live-proof.md`
- `docs/architecture/dashboard-live-gateway-runtime.md`
- `docs/architecture/live-run-computer-safe-task.md`
- `docs/architecture/live-clicker-demo.md`
- `docs/architecture/synthetic-capture-ladder.md`
- `docs/architecture/demo-readiness.md`
- `docs/architecture/chronicle-hardening-slices.md`
- `docs/architecture/unified-encrypted-graph-index.md`
- `docs/security/memory-encryption-default.md`
- `docs/research/codex-chronicle-lessons-2026-05-01.md`
- `docs/research/frontier-agent-plugin-lessons-2026-04-29.md`
- `docs/ops/plugin-install-smoke.md`
- `docs/ops/codex-plugin-real-enable.md`
- `docs/architecture/native-shadow-pointer-overlay.md`
- `docs/architecture/native-capture-permission-smoke.md`
- `docs/architecture/shadow-pointer-capture-wiring.md`
- `docs/architecture/live-browser-terminal-adapters.md`
- `docs/architecture/local-adapter-endpoint.md`
- `docs/architecture/manual-adapter-proof.md`
- `docs/architecture/live-readiness-hardening.md`
- `docs/architecture/macos-perception-adapter-contracts.md`
- `docs/architecture/browser-terminal-adapter-contracts.md`
- `docs/architecture/context-pack-templates.md`
- `docs/architecture/retrieval-scope-stress.md`
- `docs/architecture/hybrid-context-fusion-index.md`
- `docs/architecture/local-fusion-adapters.md`
- `docs/architecture/retrieval-explanation-receipts.md`
- `docs/architecture/context-fusion-stress.md`
- `docs/architecture/document-to-skill-derivation.md`
- `docs/architecture/swarm-governance.md`
- `docs/architecture/robot-spatial-safety.md`
- `docs/architecture/agent-runtime-trace.md`
- `docs/architecture/outcome-postmortem-trace-handoff.md`
- `docs/architecture/gateway-postmortem-stress.md`
- `docs/architecture/ops-quality-surface.md`
- `docs/architecture/shadow-pointer-pointing.md`
- `docs/architecture/system-blueprint.md`
- `docs/ops/task-board.md`
- `docs/ops/benchmark-registry.md`
- `docs/ops/benchmark-plan.md`

## Current Build Readout

| Area | Status | Evidence | Gap |
| --- | --- | --- | --- |
| Engineering control plane | Validated | Task board, benchmark registry, research safety ledger, ADRs | Keep reports current after each slice. |
| Safe local demo path | Validated synthetic-only demo receipt plus dashboard demo rail | `DEMO-READINESS-001`, `docs/architecture/demo-readiness.md`, `uv run cortex-demo --json`, Safe Demo Path in `docs/product/cortex-dashboard-shell.md` | Consented real screen capture remains later behind explicit approval and separate capture tests. |
| Ops Quality Surface | Validated aggregate status receipt plus dashboard aggregate panel contract and visible compact guardrail panel | `OPS-QUALITY-SURFACE-001`, `DASHBOARD-OPS-QUALITY-PANEL-001`, `MEMORY-PALACE-SKILL-FORGE-UI-001`, `uv run cortex-ops-quality`, `docs/architecture/ops-quality-surface.md`, `docs/architecture/dashboard-live-gateway-runtime.md` | Feed latest aggregate status dynamically instead of static synthetic dashboard data. |
| Contract layer | Validated | Typed contracts, fixtures, `tests/test_contracts.py` | Add migration/versioning policy as schemas evolve. |
| Privacy + Safety Firewall | Validated plus synthetic screen-context injection stress | `SEC-INJECT-001`, `SCREEN-INJECTION-STRESS-001`, `SEC-PII-001`, `CTX-HOSTILE-001` | Expand from synthetic text to app/browser/source classifiers. |
| Evidence Vault | Validated skeleton plus synthetic temp raw-ref expiry ladder, restart-safe raw expiry receipts, and durable-memory encryption default | `VAULT-RETENTION-001`, `RAW-EVIDENCE-EXPIRY-HARDENING-001`, `VAULT-ENCRYPT-001`, `MEMORY-ENCRYPTION-DEFAULT-001`, `EVIDENCE-ELIGIBILITY-HANDOFF-001`, `SYNTHETIC-CAPTURE-LADDER-001` | Replace dev cipher with production key management before real private data. |
| Scene, memory, and graph pipeline | Validated skeleton plus synthetic capture-to-memory write/retrieval ladder, visible live clicker demo memory writes, live clicker request hardening, encrypted durable-memory store boundary, and unified encrypted graph/index prototype | `SCENE-SEGMENT-001`, `MEM-COMPILE-001`, `GRAPH-EDGE-001`, `MEMORY-ENCRYPTION-DEFAULT-001`, `UNIFIED-ENCRYPTED-GRAPH-INDEX-001`, `SYNTHETIC-CAPTURE-LADDER-001`, `LIVE-CLICKER-DEMO-001`, `LIVE-CLICKER-HARDENING-001` | Add richer multimodal segmentation and contradiction handling on top of encrypted graph/index storage. |
| Retrieval and context packs | Validated budgeted skeleton plus scope stress coverage, source-router hints, hybrid fusion interface, local fusion adapters, metadata-only context-pack fusion diagnostics, context-fusion stress coverage, redacted explanation receipts, encrypted graph/index search receipts, dashboard receipt surface, and live count-only context-pack summary | `RETRIEVAL-SCORE-001`, `SCOPE-POLICY-001`, `RETRIEVAL-SCOPE-STRESS-001`, `UNIFIED-ENCRYPTED-GRAPH-INDEX-001`, `SOURCE-ROUTER-CONTEXT-PACK-001`, `CONTEXT-FUSION-INDEX-STUB-001`, `REAL-VECTOR-INDEX-ADAPTER-001`, `HYBRID-FUSION-CONTEXT-PACK-INTEGRATION-001`, `CONTEXT-FUSION-STRESS-001`, `RETRIEVAL-EXPLANATION-RECEIPTS-001`, `RETRIEVAL-RECEIPTS-DASHBOARD-SURFACE-001`, `DASHBOARD-CONTEXT-PACK-LIVE-SUMMARY-001`, `CONTEXT-PACK-001`, `CONTEXT-BUDGET-001`, scoped self-lesson suites | Wire encrypted-index-backed context metadata into visible dashboard context/debug panels. |
| Memory Palace | Validated dashboard contract, Chronicle-style observation controls, static UI shell, sparse Focus Inspector, Safe Demo Path, compact Shadow Pointer Live Receipt rail, consent-first onboarding path, read-only gateway action receipts, live gateway runtime explain calls, sanitized read-only action live proof, bounded Computer Use safe-task live run, visible Shadow Clicker memory demo, live clicker request hardening, and sanitized Computer Use browser proof | `MEMORY-PALACE-001`, `PALACE-FLOW-001`, `MEMORY-PALACE-CHRONICLE-CONTROLS-001`, `MEMORY-PALACE-DASHBOARD-001`, `MEMORY-PALACE-SKILL-FORGE-UI-001`, `DASHBOARD-FOCUS-INSPECTOR-001`, `SHADOW-POINTER-LIVE-RECEIPT-001`, `CONSENT-FIRST-ONBOARDING-001`, `DEMO-READINESS-001`, `DASHBOARD-GATEWAY-ACTIONS-001`, `DASHBOARD-GATEWAY-RUNTIME-READONLY-001`, `DASHBOARD-GATEWAY-RUNTIME-BLOCKLIST-001`, `DASHBOARD-READONLY-ACTION-LIVE-PROOF-001`, `LIVE-RUN-COMPUTER-SAFE-TASK-001`, `LIVE-CLICKER-DEMO-001`, `LIVE-CLICKER-HARDENING-001`, `COMPUTER-DASHBOARD-LIVE-PROOF-001`, self-lesson review flows | Keep correction/delete/export confirmation-gated and wire safe live receipts into native overlay streams. |
| Skill Forge | Validated skeleton plus candidate list, success metrics, dashboard metrics surface, static UI shell, sparse Focus Inspector, read-only review receipts, live gateway-backed candidate review summaries, and sanitized Computer Use browser proof | `SKILL-FORGE-002`, `SKILL-DOC-DERIVATION-001`, `SKILL-FORGE-LIST-001`, `SKILL-SUCCESS-METRICS-001`, `SKILL-METRICS-DASHBOARD-SURFACE-001`, `DASHBOARD-SKILL-REVIEW-LIVE-SUMMARY-001`, `MEMORY-PALACE-SKILL-FORGE-UI-001`, `DASHBOARD-FOCUS-INSPECTOR-001`, `DASHBOARD-GATEWAY-ACTIONS-001`, `COMPUTER-DASHBOARD-LIVE-PROOF-001`, `SKILL-GATE-001`, `SKILL-EXECUTION-001` | Add workflow clustering and live draft-only execution previews behind receipts. |
| Agent Gateway | Validated skeleton plus install-smoked Codex plugin, approval-gated plugin package, encrypted graph/index search receipts, dashboard read-only runtime with unsafe action blocklist, and bounded local Computer Use live-run proof | `GATEWAY-CTX-001`, `GATEWAY-PALACE-001`, `UNIFIED-ENCRYPTED-GRAPH-INDEX-001`, `DASHBOARD-GATEWAY-RUNTIME-READONLY-001`, `DASHBOARD-GATEWAY-RUNTIME-BLOCKLIST-001`, `LIVE-RUN-COMPUTER-SAFE-TASK-001`, self-lesson and skill tools, `CODEX-PLUGIN-001`, `PLUGIN-INSTALL-SMOKE-001`, `CODEX-PLUGIN-REAL-ENABLE-001`, `plugins/cortex-memory-os` | Bridge additional clients and keep real user config changes explicit. |
| Agent Runtime Trace | Validated contract, gateway persistence receipts, safe postmortem handoff, gateway postmortem compilation, and gateway postmortem stress coverage | `RUNTIME-TRACE-001`, `GATEWAY-TRACE-PERSISTENCE-001`, `OUTCOME-POSTMORTEM-TRACE-001`, `GATEWAY-OUTCOME-POSTMORTEM-001`, `GATEWAY-POSTMORTEM-STRESS-001`, `docs/architecture/agent-runtime-trace.md`, `docs/architecture/outcome-postmortem-trace-handoff.md`, `docs/architecture/gateway-outcome-postmortem.md`, `docs/architecture/gateway-postmortem-stress.md`, runtime trace fixture, SQLite persistence, `runtime_trace.record`, `runtime_trace.get`, `runtime_trace.list`, `outcome.postmortem` | Connect postmortem receipts to self-improvement scoring without automatic promotion. |
| Swarm Governance | Validated contract | `SWARM-GOVERNANCE-001`, `docs/adr/0005-swarm-governance-boundary.md` | Wire future parallel agents through governed gateway execution instead of direct delegation. |
| Shadow Pointer | Validated native proof, static prototype, state-machine presentation contract, live receipt contract, spatial proposal schema, permission onboarding, consent-first onboarding, capture receipt wiring, visible live clicker demo with request hardening, real-page browser-extension Shadow Pointer boundary, and read-only permission status smoke | `SHADOW-POINTER-001`, `SHADOW-POINTER-CONTROLS-001`, `SHADOW-POINTER-STATE-MACHINE-001`, `SHADOW-POINTER-LIVE-RECEIPT-001`, `SPATIAL-PROPOSAL-SCHEMA-001`, `CONSENT-FIRST-ONBOARDING-001`, `SHADOW-POINTER-PERMISSION-ONBOARDING-001`, `POINTER-PROPOSAL-001`, `SHADOW-POINTER-NATIVE-001`, `NATIVE-CAPTURE-PERMISSION-SMOKE-001`, `SHADOW-POINTER-CAPTURE-WIRING-001`, `LIVE-CLICKER-DEMO-001`, `LIVE-CLICKER-HARDENING-001`, `LIVE-CLICKER-ALLOWLISTED-ORIGIN-001`, static UI prototype, `native/macos-shadow-pointer` | Feed consent onboarding and local endpoint live receipts into the native overlay panel. |
| Native Perception Bus | Envelope, firewall handoff, evidence eligibility, browser/terminal contracts, macOS app/window and Accessibility contracts, screen-injection stress, capture budget queue, live adapter smoke artifacts, real-page browser-extension Shadow Pointer Live Receipt boundary, local adapter endpoint, manual browser/terminal proof, live-readiness hardening receipt, Shadow Pointer capture receipt wiring, and native permission-status smoke validated | `PERCEPTION-EVENT-ENVELOPE-001`, `PERCEPTION-FIREWALL-HANDOFF-001`, `SCREEN-INJECTION-STRESS-001`, `CAPTURE-BUDGET-QUEUE-001`, `EVIDENCE-ELIGIBILITY-HANDOFF-001`, `NATIVE-CAPTURE-PERMISSION-SMOKE-001`, `SHADOW-POINTER-CAPTURE-WIRING-001`, `MACOS-PERCEPTION-ADAPTERS-001`, `BROWSER-TERMINAL-ADAPTERS-001`, `LIVE-BROWSER-TERMINAL-ADAPTERS-001`, `LIVE-CLICKER-ALLOWLISTED-ORIGIN-001`, `LOCAL-ADAPTER-ENDPOINT-001`, `MANUAL-ADAPTER-PROOF-001`, `LIVE-READINESS-HARDENING-001`, roadmap, and ADR | Move toward native live receipt streaming before any consented real screen capture. |
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

Retrieval scope stress:

- `RETRIEVAL-SCOPE-STRESS-001` validates project, agent, session, global,
  lifecycle, secret, and never-store boundaries across rank, gateway search,
  and context packs.

User-facing pillars:

- Shadow Pointer: static prototype, state contract, shared state-machine visual
  contracts, compact live receipts, consent-first onboarding, native-ready
  control receipts, display-only model pointing proposals with spatial viewport
  mapping, and SwiftPM native overlay proof, plus adapter-to-overlay capture
  receipts and read-only native permission-status receipts.
- Memory Palace: validated inspect, explain, correct, delete, export,
  dashboard cards, export previews, action plans, self-lesson review flows, and
  the Real Memory Palace and Skill Forge UI shell using the safe dashboard view
  models, plus read-only dashboard gateway receipts, live gateway runtime
  explain calls, unsafe action blocklist, sanitized read-only action receipt
  proof, sanitized Computer Use browser proof, and real tab views that hide
  unrelated panels so Memory Palace can be read as one focused queue.
- Skill Forge: validated repeated-workflow detector, document-to-skill candidate
  derivation, candidate-list cards, success/failure metrics, maturity gates,
  dashboard metric cards, rollback, audits, and draft-only execution, plus the
  shared dashboard shell with a focused Skill Forge tab view.
- Agent Gateway: validated budgeted context packs, scoped actions, audit
  receipts, retrieval explanation receipts, review queues, draft skill
  execution, and repo-local Codex plugin packaging plus temporary cache-shaped
  plugin install/discovery smoke and approval-gated real enable/rollback plan.
- Dashboard Live Proof: validated `COMPUTER-DASHBOARD-LIVE-PROOF-001` so live
  Computer Use observations become commit-safe visible-term and local-preview
  receipts without raw screenshots, raw accessibility trees, tab titles,
  secrets, raw refs, durable memory writes, gateway mutations, or external
  effects. `DASHBOARD-READONLY-ACTION-LIVE-PROOF-001` adds sanitized
  read-only gateway action receipt text without allowing mutation, export,
  draft execution, durable writes, or external effects.
- Live Run Safe Task: validated `LIVE-RUN-COMPUTER-SAFE-TASK-001` so a safe
  localhost task can be exercised with Computer Use while proving the dashboard
  and read-only gateway receipts are on, and real capture, durable memory
  writes, raw screen storage, raw refs, model secret echo attempts, mutations,
  exports, draft execution, and external effects are off.
- Live Shadow Clicker Demo: validated `LIVE-CLICKER-DEMO-001` so Computer Use
  page actions on a disposable localhost safe site visibly move the Cortex
  Shadow Clicker, produce governed observation receipts, write demo candidate
  memories to a temp store, and prove retrieval and context-pack hits while raw
  screen capture, raw refs, private durable memory, and external effects remain
  off. `LIVE-CLICKER-HARDENING-001` adds per-session token, localhost origin,
  unsupported content type, observation cap, and security-header checks so
  rejected requests do not create demo memories.
- Real-Page Shadow Clicker Boundary: validated
  `LIVE-CLICKER-ALLOWLISTED-ORIGIN-001` at the contract level so the browser
  extension can draw a visible Shadow Clicker on an explicitly activated real
  public page such as Google News, post visible-page evidence to localhost, and
  keep it `external_untrusted`, memory-ineligible, raw-ref-free, and
  aggregate-only through `/results`. The user-confirmed live Google News run
  activated Cortex through Chrome's Extensions menu and produced 3 accepted
  browser observations with 0 memory-eligible writes and 0 retained raw refs.
- Synthetic Capture Ladder: validated `SYNTHETIC-CAPTURE-LADDER-001` so a
  synthetic disposable capture page only path can create an ephemeral raw ref in
  temp storage, auto-delete it, write a durable synthetic memory to a local test
  DB with audit, retrieve that memory in search and context packs, and run a
  secret-in-screen negative test proving redaction before any write. Consented
  real screen capture stays later.
- Demo Readiness: validated `DEMO-READINESS-001` so the current system can be
  shown through a synthetic-only, localhost-only Safe Demo Path. The receipt
  composes the dashboard, Synthetic capture ladder, encrypted index,
  context pack policy refs, and `.env.local` hygiene while proving No real
  screen capture, No durable raw screen storage, No secret echo, and No
  mutation, export, or draft execution.
- Live Stress Demo: validated `DEMO-STRESS-001` so the safe demo path can be
  repeated as a bounded live stress demo over demo readiness, screen injection
  stress, and dashboard gateway receipts while staying synthetic-only and
  localhost-only. It preserves No real screen capture, No durable raw screen
  storage, No secret echo, and No mutation, export, or draft execution.
- Codex Chronicle Research: `docs/research/codex-chronicle-lessons-2026-05-01.md`
  validates that screen context can reduce restated context and identify better
  primary sources, while also confirming the need for Cortex-specific
  encryption, pre-write firewalling, visible observation state, scoped memory
  influence, rate-limit backpressure, and prompt-injection stress tests.
- Chronicle Hardening Slices: validated
  `SHADOW-POINTER-PERMISSION-ONBOARDING-001`,
  `SCREEN-INJECTION-STRESS-001`, `SOURCE-ROUTER-CONTEXT-PACK-001`,
  `CAPTURE-BUDGET-QUEUE-001`, `RAW-EVIDENCE-EXPIRY-HARDENING-001`, and
  `MEMORY-PALACE-CHRONICLE-CONTROLS-001` so Chronicle-style screen-context
  value is represented through visible permission state, adversarial visual
  stress tests, redacted direct-source hints, budget backpressure, restart-safe
  raw expiry receipts, and user-facing observation controls without enabling
  real capture.
- Dashboard Live Gateway Runtime: validated
  `DASHBOARD-GATEWAY-RUNTIME-READONLY-001`,
  `DASHBOARD-GATEWAY-RUNTIME-BLOCKLIST-001`,
  `DASHBOARD-CONTEXT-PACK-LIVE-SUMMARY-001`,
  `DASHBOARD-SKILL-REVIEW-LIVE-SUMMARY-001`, and
  `DASHBOARD-OPS-QUALITY-PANEL-001` so local dashboard panels can use gateway
  summaries, blocked-action receipts, context-pack counts, skill-review counts,
  and aggregate ops status without content, procedure text, source refs, raw
  payloads, memory writes, or external effects.
- Retrieval Fusion: validated dependency-free semantic, sparse, and graph
  adapters under `REAL-VECTOR-INDEX-ADAPTER-001` that feed redacted hybrid
  fusion candidates without model services or network calls, plus
  `HYBRID-FUSION-CONTEXT-PACK-INTEGRATION-001` metadata-only context-pack
  diagnostics that expose component scores while keeping content and source refs
  redacted, plus `CONTEXT-FUSION-STRESS-001` deterministic mixed-candidate
  stress coverage for hostile, secret, and raw-ref boundaries.
- Retrieval Receipts Dashboard: validated receipt cards under
  `RETRIEVAL-RECEIPTS-DASHBOARD-SURFACE-001` so users can inspect included,
  evidence-only, and excluded decisions without content or source refs.
- Agent Runtime Trace: validated tool calls, shell actions, browser actions,
  artifacts, approvals, retries, blocked hostile content, outcome checks, and
  gateway persistence receipts that return metadata without event summary text,
  plus `OUTCOME-POSTMORTEM-TRACE-001` postmortems that preserve safe trace
  metadata and `GATEWAY-OUTCOME-POSTMORTEM-001` gateway compilation that keeps
  event summaries out of self-improvement instruction lanes, with
  `GATEWAY-POSTMORTEM-STRESS-001` covering repeated hostile-feedback and
  unknown-trace error redaction.
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
   place; capture receipts, native permission-status smoke, and permission
   onboarding are wired at contract level.
2. Wire the Shadow Pointer native overlay proof to the permission onboarding
   receipt and local endpoint receipt streams.
3. Wire the live gateway runtime summaries into visible dashboard panels without
   adding raw payloads or write paths.
4. Connect gateway postmortem receipts to self-improvement scoring without
   automatic lesson or skill promotion.
5. Feed metadata-only hybrid fusion diagnostics into live dashboard context/debug
   panels without adding content or source refs.
6. Extend `RETRIEVAL-RECEIPTS-DASHBOARD-SURFACE-001` from static synthetic data
   to live gateway-backed context/debug panels without adding memory content or
   source refs.
7. Extend `SKILL-METRICS-DASHBOARD-SURFACE-001` from static synthetic data to
   live gateway-backed Skill Forge metrics without changing autonomy.
8. Additional client bridges after the Codex plugin path is user-approved in a
   real environment.

## Update Rule

After each meaningful product slice:

- update `docs/ops/task-board.md`;
- update `docs/ops/benchmark-registry.md` with the latest artifact;
- add or adjust benchmark coverage before claiming a surface is validated;
- keep any partial or not-started product surface visible instead of hiding it
  inside prose.
