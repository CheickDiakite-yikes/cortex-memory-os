# Cortex Dashboard Shell

Last updated: 2026-04-30

Benchmark: `MEMORY-PALACE-SKILL-FORGE-UI-001`

Policy reference: `policy_cortex_dashboard_shell_v1`

This slice turns the generated dashboard concept into a local, static,
inspectable dashboard shell over safe view models. The goal is a usable product
surface for Memory Palace and Skill Forge without introducing live capture,
private memory fixtures, or gateway side effects.

The 2026-05-01 refresh uses a quieter generated dashboard concept as the visual
anchor, then pares it down further after live visual review: primary work queues
stay central, guardrails become a short summary strip, and default lists show a
small focus queue with counts preserved.

## Design Source

The generated dashboard concept established the first visual direction:

- left navigation for Overview, Memory Palace, Skill Forge, Agent Gateway,
  Audit, and Policies;
- top status strip for Shadow Pointer, active project, consent scope, and
  Safety Firewall;
- two primary work areas for Memory Palace Review Queue and Skill Forge
  Candidate Workflows;
- compact guardrail summaries for Context Pack Health, Privacy Firewall,
  Evidence Vault, Encryption Default, and Ops Quality;
- bottom rail for Recent Safe Receipts;
- restrained local-ops palette with green, blue, amber, and red status
  accents;
- dense but readable operational UI, not a landing page.

## Data Boundary

The shell uses `src/cortex_memory_os/dashboard_shell.py` to compose existing
safe view models:

- `MemoryPalaceDashboard`
- `SkillForgeCandidateList`
- `SkillMetricsDashboard`
- `RetrievalReceiptsDashboard`

The generated `ui/cortex-dashboard/dashboard-data.js` contains synthetic,
redacted, deterministic view-model data. It must contain no raw private memory,
screenshots, databases, API responses, logs, vector stores, or secret-like
tokens.

## UI Contract

The static app in `ui/cortex-dashboard/` must render:

- the status strip;
- Memory Palace review cards with status, confidence, source count, recall
  state, and exact gateway action plans;
- Skill Forge candidate cards with observed refs, risk, maturity, promotion
  blockers, and draft-only actions;
- Skill Metrics strips with run count, success rate, correction rate, and
  review recommendation;
- Retrieval Receipts that show included/evidence-only/excluded decisions without
  memory content or source refs;
- guardrail insight summaries that expose aggregate safety and ops status without
  raw case payloads, raw refs, source refs, or private memory content;
- shortened default queues that keep the screen calm while preserving full
  counts in the view model;
- local filter controls for both lists;
- icon-first action controls that update local UI state;
- Recent Safe Receipts with redacted targets.
- Gateway Action Receipts that distinguish read-only prepared calls from
  blocked mutation, export, and draft-execution previews.
- Encryption Default status showing that durable memory content requires
  authenticated encryption.

All actions are receipt-gated previews. Only read-only explain/review actions
may become prepared gateway calls in this slice. They do not mutate memory,
execute skills, export data, or perform external effects.

## Live Desktop Proof

`COMPUTER-DASHBOARD-LIVE-PROOF-001` validates this shell in a real Chrome
window through Computer Use while storing only sanitized proof facts. The proof
records the local dashboard origin, required visible terms, the clicked
`Pause Observation` control, and the local preview receipt. It does not store a
raw screenshot, raw accessibility tree, tab titles, private browser text,
secrets, raw refs, durable memory writes, gateway mutations, or external
effects.

The required receipt class is a local preview receipt, such as:

```text
Observation pause previewed locally. Confirmation and audit receipt required.
```

## Safety Gates

`MEMORY-PALACE-SKILL-FORGE-UI-001` passes only when:

- UI files are present and reference `window.CORTEX_DASHBOARD_DATA`;
- Memory Palace and Skill Forge cards render from safe view models;
- action plans are visible but inert;
- `DASHBOARD-GATEWAY-ACTIONS-001` receipts are present for exact gateway tools;
- generated fixture data has no secret markers or raw refs;
- generated Skill Metrics data has no procedure text, task content, or
  autonomy-changing controls;
- generated Retrieval Receipts have no memory content, source refs, hostile
  text, or raw evidence refs;
- the visible shell includes the `Encryption Default` guardrail tied to
  `policy_memory_encryption_default_v1`;
- dashboard docs, task board, benchmark plan, and benchmark registry name the
  slice;
- local browser proof confirms the first viewport renders without overlapping
  primary UI.

`COMPUTER-DASHBOARD-LIVE-PROOF-001` additionally passes only when the live
proof observes a local browser origin, all required visible dashboard terms, a
local preview receipt, and no durable memory write or raw live artifacts.
