# Cortex Dashboard Shell

Last updated: 2026-05-15

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

Live tutor benchmark: `LIVE-TUTOR-OVERLAY-001`

Live tutor policy: `policy_live_tutor_overlay_v1`

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

The Live Tutor Overlay refinement turns the Clicky-inspired product lesson into
a safe localhost creative-tool demo. The dashboard exposes the command and
receipt summary, while the actual demo lives near the work surface with a blue
secondary cursor, target highlight, and instruction bubble. It stays
display-only and controlled-state-only: no screen capture, microphone capture,
Accessibility observer, clicks, typing, raw refs, memory writes, exports, or
external effects.

The 2026-05-15 agentic run refinement makes the Agentic OS panel consume the
token-protected localhost bridge instead of only generated dashboard data. The
visible `Run local turn` action posts a controlled pointer intent, refreshes
latest run receipts, and redraws the card from redacted local receipt state.
The dashboard remains the review surface: the product moment is the
pointer-side card, while the dashboard answers what happened and what stayed
blocked.

The 2026-05-16 user shell reset moves the default dashboard away from an
engineering console. The primary nav is now only `Chats`, `Memories`, `Voice`,
and `Settings`. Conversations show recent helper sessions and memory/voice
shortcuts; Memories is the Memory Book; Voice holds assistant style and reply
mode; Settings explains privacy and app boundaries. Developer receipts, routing,
benchmarks, and capture controls remain available from Settings, but they are no
longer the main user path.

The 2026-05-04 child-readable home refinement makes the Overview a plain
control pad instead of an ops wall. The first screen uses words a new user can
understand quickly: Cortex is ready, ask the helper, start cursor, memory book,
things learned, safety lock, helper cursor, screen saving, memory, and secrets.
Deeper benchmark receipts, encrypted index metadata, capture readiness, live
adapter counts, status strips, and policy detail move behind Help, Log, and
Safe tabs.

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
- a child-readable home that exposes plain-language actions before operational
  receipts.
- a user shell whose primary tabs are Chats, Memories, Voice, and Settings, with
  Developer detail reachable but not part of the default nav.

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
- `LiveTutorDashboardPanel`
- `AgenticOSDashboardPanel`, with optional live localhost receipts from
  `/api/agentic/turn`, `/api/agentic/latest`, and `/api/agentic/receipts`

The generated `ui/cortex-dashboard/dashboard-data.js` contains synthetic,
redacted, deterministic view-model data. It must contain no raw private memory,
screenshots, databases, API responses, logs, vector stores, or secret-like
tokens.

## UI Contract

The static app in `ui/cortex-dashboard/` must render:

- `DASHBOARD-USER-CONVERSATIONS-001`, the default user surface for past helper
  sessions, saved-memory shortcuts, voice choices, and a simple search box;
- `DASHBOARD-VOICE-SETTINGS-001`, a gated voice preference surface for assistant
  style and reply mode while microphone access remains off;
- `DASHBOARD-USER-SETTINGS-001`, a plain settings surface for memory review,
  helper pointer behavior, screen-capture state, and developer access;
- a simplified child-readable home for `DASHBOARD-USER-HOME-001`, with "Ask the
  helper", "Start cursor", "Memory book", "Things learned", "Safety lock", and
  plain safety lights for helper cursor, screen saving, memory, and secrets;
- the status strip in deeper operations views, not on the default Overview;
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
- `Live Tutor Overlay` for `LIVE-TUTOR-OVERLAY-001`, linking to
  `uv run cortex-live-tutor-demo` and showing display-only cue, controlled
  surface, memory-off, raw-ref-free, and blocked-effect state;
- an Agentic OS current-run card that can call the local bridge, show a live
  localhost receipt, and keep click, type, raw ref, external effect, and
  unreviewed memory writes blocked;
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
button calls localhost-only fixed endpoints with `CAPTURE-CONTROL-TOKEN-001`
and `CAPTURE-CONTROL-ORIGIN-CSRF-001` protections, then starts only the
display-only native Shadow Clicker. `DASHBOARD-SCREEN-PROBE-001` adds a
`Screen Probe` control that uses the tokenized `screen-probe` endpoint for
metadata-only real capture receipts. When opened as static `file://` HTML, the
button emits a local receipt with the native command and permission state. The
native Shadow Clicker follows the system cursor without clicks, typing, raw
payloads, durable memory writes, arbitrary shell commands, or screen storage.

## Live Desktop Proof

`COMPUTER-DASHBOARD-LIVE-PROOF-001` validates this shell in a real Chrome
window through Computer Use while storing only sanitized proof facts. The proof
records the local dashboard origin, required visible terms, the clicked
`Pause Observation` control, and the local preview receipt. It does not store a
raw screenshot, raw accessibility tree, tab titles, private browser text,
secrets, raw refs, durable memory writes, gateway mutations, or external
effects.

## Agentic OS Kernel

`AGENTIC-OS-PLANNER-001` adds the first OS-level planning spine behind the
dashboard. It maps a pointer-first user goal into capability lanes, safe tool
routes, approval gates, redacted runtime tracing, and reviewed memory
proposals. This is the bridge between the AI Pointer product direction and a
proper Cortex agentic OS: maintain flow, show and tell at the pointer, resolve
“this” and “that”, and turn pixels into structured entities before any tool
action is allowed.

The dashboard panel stays deliberately conservative. It is display-only,
content-redacted, source-ref-redacted, and blocks autonomous clicks, typing,
exports, raw evidence storage, and unreviewed memory writes.

The panel now includes a current-run card rather than only static capability
counts. That card shows the pointed target, selected route, gateway tool,
confidence, approval state, and memory-write state in plain language. The
pointer-side copy remains the product surface; the dashboard is the receipt and
review surface.

The current safe run is covered by:

- `AGENTIC-TURN-ROUTER-001`
- `AGENTIC-LIVE-TUTOR-BRIDGE-001`
- `AGENTIC-POINTER-CARD-001`
- `AGENTIC-RUNTIME-TRACE-001`

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
- the visible shell includes `Capture Readiness Ladder` for
  `CAPTURE-READINESS-LADDER-001`, tied to
  `policy_capture_readiness_ladder_v1`;
- the visible shell includes `Live Tutor Overlay` for
  `LIVE-TUTOR-OVERLAY-001`, tied to `policy_live_tutor_overlay_v1`;
- the visible shell includes `Agentic OS Kernel` for
  `AGENTIC-OS-PLANNER-001`, tied to `policy_agentic_os_planner_v1`;
- dashboard docs, task board, benchmark plan, and benchmark registry name the
  slice;
- local browser proof confirms the first viewport renders without overlapping
  primary UI.

`COMPUTER-DASHBOARD-LIVE-PROOF-001` additionally passes only when the live
proof observes a local browser origin, all required visible dashboard terms, a
local preview receipt, and no durable memory write or raw live artifacts.
