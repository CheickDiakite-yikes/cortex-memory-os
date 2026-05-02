# Cortex Dashboard Shell

Last updated: 2026-05-02

Benchmark: `MEMORY-PALACE-SKILL-FORGE-UI-001`

Policy reference: `policy_cortex_dashboard_shell_v1`

Focus inspector benchmark: `DASHBOARD-FOCUS-INSPECTOR-001`

Focus inspector policy: `policy_dashboard_focus_inspector_v1`

Demo readiness benchmark: `DEMO-READINESS-001`

Demo readiness policy: `policy_demo_readiness_v1`

Stress demo benchmark: `DEMO-STRESS-001`

Stress demo policy: `policy_demo_stress_v1`

Shadow Pointer live receipt benchmark: `SHADOW-POINTER-LIVE-RECEIPT-001`

Shadow Pointer live receipt policy: `policy_shadow_pointer_live_receipt_v1`

Consent-first onboarding benchmark: `CONSENT-FIRST-ONBOARDING-001`

Consent-first onboarding policy: `policy_consent_first_onboarding_v1`

Encrypted index dashboard benchmark: `ENCRYPTED-INDEX-DASHBOARD-LIVE-001`

Encrypted index dashboard policy: `policy_encrypted_index_dashboard_live_v1`

Native live feed benchmark: `NATIVE-SHADOW-POINTER-LIVE-FEED-001`

Native live feed policy: `policy_native_shadow_pointer_live_feed_v1`

Clicky UX companion benchmark: `CLICKY-UX-COMPANION-001`

Clicky UX companion policy: `policy_clicky_ux_companion_v1`

Live data adapter benchmark: `DASHBOARD-LIVE-DATA-ADAPTER-001`

Live data adapter policy: `policy_dashboard_live_data_adapter_v1`

Live dashboard receipts benchmark: `LIVE-DASHBOARD-RECEIPTS-001`

Live dashboard receipts policy: `policy_live_dashboard_receipts_v1`

This slice turns the generated dashboard concept into a local, static,
inspectable dashboard shell over safe view models. The goal is a usable product
surface for Memory Palace and Skill Forge without introducing live capture,
private memory fixtures, or gateway side effects.

The 2026-05-01 refresh uses a quieter generated dashboard concept as the visual
anchor, then pares it down further after live visual review: primary work queues
stay central, guardrails become a short summary strip, and default lists show a
small focus queue with counts preserved. The next refinement adds a sparse
Focus Inspector so selected memory/skill detail moves into one quiet band
instead of making every card carry detail. The demo-readiness refinement adds a
compact Safe Demo Path rail so a local walkthrough can show the synthetic
capture ladder, encrypted index, context pack, and safety off-switches without
adding a distracting third queue.

The 2026-05-02 navigation refinement makes the sidebar real tab views instead
of a static highlight. The default screen is now a simplified overview showing
only system status, the Safe Demo Path, and guardrail health. Memory Palace,
Skill Forge, Agent Gateway, Audit, and Policies each reveal their own focused
surface so the dashboard can be read one job at a time.

The Shadow Pointer live receipt refinement moves the most important live trust
facts out of the crowded review queues and into a compact receipt rail:
`trust`, `memory`, `raw_refs`, and `policy`. This is the dashboard counterpart
to the cursor-adjacent Shadow Pointer. It makes the current observation state
readable without exposing raw browser text, OCR, Accessibility content, source
refs, or raw evidence refs.
External public-page observations are shown as `external_untrusted`,
memory-ineligible, raw-ref-free receipts with derived-only evidence policy.

The Clicky UX refinement keeps the live surface cursor-adjacent and compact
instead of dashboard-first. Clicky was studied as an untrusted primary
repository reference; external repo code was not executed. Cortex borrows the
usable pattern, not the trust boundary: a small `Cursor Companion`, a compact
receipt panel, display-only pointing, and onboarding by demonstration. The
dashboard now shows the companion beside `Encrypted Index Receipts` so live
status and encrypted retrieval health are visible without adding another dense
queue.

The live data adapter refinement replaces static backbone assumptions with a
local read-only adapter over safe receipts. The dashboard reads count-only
gateway, context-pack, skill-review, ops-quality, encrypted-index, native-feed,
retrieval, and skill-metric receipts. The live safe receipts panel refreshes
from those adapters without write paths, raw payloads, source refs, or private
memory content.

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
- a Safe Demo Path rail for the localhost synthetic demo sequence;
- a Shadow Pointer live receipt rail for compact observation trust state;
- a Cursor Companion rail inspired by Clicky UX lessons;
- an Encrypted Index Receipts rail for metadata-only `memory.search_index`
  health;
- real tab views for Overview, Memory Palace, Skill Forge, Agent Gateway,
  Audit, and Policies;
- active tab semantics and Focus Inspector defaults that switch with the
  selected view, so Memory Palace opens on a memory and Skill Forge opens on a
  skill rather than making both tabs feel identical;
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
- `ShadowPointerLiveReceipt`
- `ConsentFirstOnboardingPlan`
- `KeyManagementPlan`
- `DashboardEncryptedIndexPanel`
- `NativeShadowPointerLiveFeedReceipt`
- `DurableSyntheticMemoryReceipt`
- `ClickyUxCompanionPanel`
- `DashboardLiveDataAdapterSnapshot`
- `LiveDashboardReceiptsPanel`

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
- a Focus Inspector for selected memory or skill detail, with content, source
  refs, and procedure text redacted;
- a Safe Demo Path for `DEMO-READINESS-001`, showing the dashboard, Synthetic
  capture ladder, encrypted index, and context pack steps;
- a Shadow Pointer live receipt for `SHADOW-POINTER-LIVE-RECEIPT-001`, showing
  trust class, memory eligibility, raw-ref policy, and firewall/evidence
  decision;
- a `Cursor Companion` for `CLICKY-UX-COMPANION-001`, showing the current
  display-only state, trust, memory eligibility, and raw-ref status without
  enabling capture or memory writes;
- `Encrypted Index Receipts` for `ENCRYPTED-INDEX-DASHBOARD-LIVE-001`, showing
  write/search/open counts for `memory.search_index` while query text, token
  text, key material, source refs, and memory content stay redacted;
- `Live Receipt Backbone` for `DASHBOARD-LIVE-BACKBONE-001`, tying key
  management, encrypted index receipts, native live feed, and durable synthetic
  memory receipts together as redacted operational proof;
- `Live Safe Receipts` for `LIVE-DASHBOARD-RECEIPTS-001`, showing retrieval,
  encrypted index, ops quality, skill metric, and gateway runtime counts from
  the local read-only adapter;
- `DASHBOARD-LIVE-DATA-ADAPTER-001`, proving that dashboard panels can refresh
  from local read-only adapters while write paths and raw payloads stay off;
- Consent-first Onboarding for `CONSENT-FIRST-ONBOARDING-001`, showing the
  synthetic-only first-run path before real capture;
- real tab views that hide unrelated panels when the user moves between
  Memory Palace, Skill Forge, Agent Gateway, Audit, and Policies;
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

## Demo Path

The Safe Demo Path is a small horizontal rail, not another dashboard panel. It
exists so the product can be demoed coherently:

1. Open the localhost dashboard.
2. Run `uv run cortex-synthetic-capture-ladder --json`.
3. Show metadata-only `memory.search_index` results over encrypted memory.
4. Show `memory.get_context_pack` policy refs and redacted diagnostics.

The corresponding command receipt is `uv run cortex-demo --json`. That receipt
keeps real screen capture, durable raw screen storage, raw private refs, secret
echo, mutation, export, draft execution, and external effects off.

The same rail also exposes a bounded stress receipt:

```bash
uv run cortex-demo-stress --iterations 12 --json
```

That command repeats the safe demo readiness path, screen injection stress, and
read-only dashboard gateway receipts while staying synthetic-only and
localhost-only. It keeps No real screen capture, No durable raw screen storage,
No secret echo, and No mutation, export, or draft execution.

## Capture Control

`DASHBOARD-CAPTURE-CONTROL-001` adds a compact Capture Control rail for the
next real-observation milestone. It shows `Turn On Cortex`, native Shadow
Clicker readiness, Screen Recording and Accessibility readiness, and the
`cortex-shadow-clicker` command.

The dashboard does not claim that static HTML can launch a native process.
When served by `uv run cortex-capture-control-server --port 8799`, the same
button calls localhost-only fixed endpoints and starts only the display-only
native Shadow Clicker. When opened as static `file://` HTML, the button emits a
local receipt with the native command and permission state. The native Shadow
Clicker follows the system cursor without clicks, typing, raw payloads, durable
memory writes, arbitrary shell commands, or screen storage.

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
- the visible shell includes the `Focus Inspector` tied to
  `policy_dashboard_focus_inspector_v1`;
- the visible shell includes the `Safe Demo Path` tied to
  `policy_demo_readiness_v1`;
- the visible shell includes the `DEMO-STRESS-001` command tied to
  `policy_demo_stress_v1`;
- the visible shell includes the `Shadow Pointer Live Receipt` tied to
  `policy_shadow_pointer_live_receipt_v1`;
- the visible shell includes `Consent-first Onboarding` tied to
  `policy_consent_first_onboarding_v1`;
- the visible shell includes `Cursor Companion` tied to
  `policy_clicky_ux_companion_v1`;
- the visible shell includes `Encrypted Index Receipts` tied to
  `policy_encrypted_index_dashboard_live_v1`;
- the visible shell includes `Live Receipt Backbone` tied to
  `policy_dashboard_live_backbone_v1`;
- the visible shell includes `Capture Control` and `Turn On Cortex` tied to
  `policy_dashboard_capture_control_v1`;
- dashboard docs, task board, benchmark plan, and benchmark registry name the
  slice;
- local browser proof confirms the first viewport renders without overlapping
  primary UI.

`COMPUTER-DASHBOARD-LIVE-PROOF-001` additionally passes only when the live
proof observes a local browser origin, all required visible dashboard terms, a
local preview receipt, and no durable memory write or raw live artifacts.
