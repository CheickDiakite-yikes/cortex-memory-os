# Benchmark Plan

Last updated: 2026-05-02

This plan defines the minimum quality gates for Cortex Memory OS slices. The
benchmark runner is intentionally synthetic-first so it can run locally without
private user data.

## Standard Commands

Use these commands as the default verification ladder:

```bash
uv run pytest
uv run cortex-bench --no-write
uv run cortex-bench
python3 -m compileall src
uv run cortex-mcp --smoke
uv run cortex-plugin-install-smoke
uv run cortex-demo --json
uv run cortex-demo-stress --iterations 12 --json
uv run cortex-capture-control-server --smoke --json
uv run cortex-native-cursor-follow --json
```

Use `uv run cortex-bench --no-write` for quick local checks. Use
`uv run cortex-bench` when a slice should leave a sanitized run artifact under
`benchmarks/runs/`.

## Current Runnable Suites

| Suite | Gate | Release blocker |
| --- | --- | --- |
| `MEM-RECALL-001` | Benign memory recall returns the intended memory with provenance. | Relevant user-approved memory cannot be recalled. |
| `RETRIEVAL-SCORE-001` | Ranking favors trusted, recent, task-relevant memories. | Deleted or untrusted memory outranks safe active memory. |
| `SCOPE-POLICY-001` | Project, agent, and session boundaries filter retrieval. | Memory crosses a mismatched project, agent, or session scope. |
| `RETRIEVAL-SCOPE-STRESS-001` | Retrieval scope boundaries hold across project, agent, session, global, lifecycle, and sensitivity pressure. | Scoped search/context leaks cross-scope, deleted, revoked, superseded, quarantined, stored-only, secret, never-store, or global-excluded memories. |
| `CONTEXT-FUSION-INDEX-STUB-001` | Hybrid context fusion combines semantic, sparse, graph, recency, and trust signals with prompt-risk exclusions. | Risky or raw-ref candidates enter context, or fusion results expose content instead of redacted diagnostics. |
| `PERF-LAT-001` | Synthetic local memory writes and searches report p50/p95 latency. | Local p95 latency crosses the initial synthetic gate. |
| `PERF-HISTORY-001` | Benchmark latency artifacts can be compared across runs. | Large p95 regression is not flagged. |
| `GATEWAY-HISTORY-001` | Local ops command renders sanitized latency-history reports. | History command leaks non-latency payloads or lacks regression failure mode. |
| `OPS-QUALITY-SURFACE-001` | Local ops command renders an aggregate-only latest verification summary. | Ops quality output leaks benchmark summaries, metrics, evidence payloads, raw refs, hostile text, secrets, or absolute private paths. |
| `MEM-LIFECYCLE-001` | Activation, deletion, revocation, quarantine, and supersession obey lifecycle policy. | Secret, external, or low-confidence memory becomes active. |
| `MEM-FORGET-001` | Deleted memories are omitted from recall. | Deleted memory appears in search or a context pack. |
| `SEC-INJECT-001` | External prompt injection is quarantined. | Hostile text becomes memory, skill, or agent instruction. |
| `SCREEN-INJECTION-STRESS-001` | Synthetic OCR, screenshot, browser DOM, and Accessibility prompt-injection fixtures quarantine and redact before context use. | Hostile visual context becomes relevant memory, fake secrets leak, or raw refs enter context. |
| `SEC-PII-001` | Secret-like text is redacted before storage. | Fake or real secret appears in stored output or benchmark artifact. |
| `SEC-POLICY-001` | Local secret/PII policy is referenced by code and gitignore. | Required local-data ignore patterns are missing. |
| `DBG-TRACE-001` | Debug traces redact secret-like text. | Trace output contains secret-like text. |
| `VAULT-RETENTION-001` | Short-retention raw evidence expires while metadata remains. | Expired raw evidence is still readable. |
| `RAW-EVIDENCE-EXPIRY-HARDENING-001` | Raw evidence expiry works after vault restart and emits redacted receipts. | Restarted vault keeps readable raw bytes, raw refs, or blobs after expiry. |
| `VAULT-ENCRYPT-001` | Production vault mode rejects no-op ciphers. | Raw evidence can be stored in production with `noop-dev`. |
| `MEMORY-ENCRYPTION-DEFAULT-001` | Durable memory content writes require authenticated encryption and persist sealed payloads. | A no-op cipher writes durable memory, SQLite bytes contain memory content/source refs, or storage receipts include hidden content. |
| `UNIFIED-ENCRYPTED-GRAPH-INDEX-001` | Encrypted memory payloads can be searched through redacted HMAC index metadata and encrypted graph edge payloads. | Index storage contains memory content, source refs, graph terms, raw refs, or query text; context packs omit `policy_unified_encrypted_graph_index_v1` when using the encrypted index. |
| `KEY-MANAGEMENT-PLAN-001` | Production key lifecycle covers `memory_payload`, `graph_edge_payload`, `hmac_index`, and `evidence_blob` classes without key material. | Key material appears in docs/receipts, production allows no-op ciphers, rotation/delete/audit controls are missing, or key classes share one boundary. |
| `DURABLE-SYNTHETIC-MEMORY-RECEIPTS-001` | Synthetic memory writes pass through encrypted durable storage and redacted index receipts before private real capture. | Synthetic receipts leak content/source refs, write private real memory, retain raw refs, skip audit, or omit encrypted store proof. |
| `ENCRYPTED-INDEX-DASHBOARD-LIVE-001` | Dashboard renders metadata-only `Encrypted Index Receipts` for `memory.search_index` health. | Dashboard exposes query text, token text, source refs, memory content, raw refs, or key material. |
| `RECEIPT-LEAK-STRESS-001` | Operational backbone receipts stay redacted across key, index, native feed, and durable synthetic write payloads. | Combined receipt payloads leak prohibited markers, raw refs, key material, source refs, or synthetic memory content. |
| `GATEWAY-CTX-001` | Gateway returns task-scoped context packs with warnings. | Context pack lacks scope warnings or source refs. |
| `CONTEXT-PACK-001` | Context packs include retrieval score summaries. | Scores do not align with returned memories. |
| `SOURCE-ROUTER-CONTEXT-PACK-001` | Context packs expose metadata-only route hints for better direct sources. | Route hints leak source refs/content or mark raw/external hostile sources directly fetchable. |
| `RETRIEVAL-EXPLANATION-RECEIPTS-001` | Context packs expose redacted receipts for included, evidence-only, and excluded retrieval decisions. | Explanations leak memory content, source refs, hostile text, or omit decision reason tags. |
| `RETRIEVAL-RECEIPTS-DASHBOARD-SURFACE-001` | Dashboard renders redacted retrieval receipt cards for context/debug review. | Dashboard receipts expose memory content, source refs, hostile text, raw refs, or change retrieval scope. |
| `REAL-VECTOR-INDEX-ADAPTER-001` | Local semantic, sparse, and graph adapters feed the hybrid fusion interface without dependencies. | Adapters leak content, accept raw refs, miss prompt-risk exclusions, or require network/model dependencies in the default runner. |
| `HYBRID-FUSION-CONTEXT-PACK-INTEGRATION-001` | Context packs expose metadata-only hybrid fusion diagnostics from local adapters. | Diagnostics leak memory content, source refs, hostile text, raw refs, or override retrieval scope and hostile-source policy. |
| `CONTEXT-FUSION-STRESS-001` | Hybrid fusion diagnostics stay deterministic and redacted under larger mixed candidate sets. | Stress diagnostics leak content/source refs/hostile text/raw refs, miss hostile/secret exclusions, accept raw refs, or become order-dependent. |
| `CONTEXT-BUDGET-001` | Context packs expose token, time, tool, artifact, memory, self-lesson, risk, and autonomy budgets. | Requested budgets expand beyond template ceilings, high-risk/autonomous budgets appear, or estimated tokens exceed budget. |
| `CTX-HOSTILE-001` | External evidence is cited separately from trusted memory. | Hostile external text becomes memory, guidance, or instructions. |
| `CONTEXT-TEMPLATE-001` | Context pack templates select compact task lanes without widening scope. | Template ignores scope, requests secrets, or expands memory budget. |
| `GATEWAY-PALACE-001` | Gateway exposes explain, correct, and forget tools with audits. | Mutation tool omits an audit event. |
| `GATEWAY-EXPORT-001` | Gateway exports exact memory IDs with scope controls and audit receipt. | Gateway export lacks memory ID anchors, scope, or audit ID. |
| `SHADOW-POINTER-001` | Shadow Pointer states carry trust context. | User cannot tell when observation or approval is active. |
| `SHADOW-POINTER-CONTROLS-001` | Shadow Pointer controls return native-ready receipts for pause, resume, status, delete-recent, and app-ignore. | User controls lack confirmation, audit metadata, or memory-write blocking semantics. |
| `POINTER-PROPOSAL-001` | Model-proposed Shadow Pointer coordinates stay display-only. | Coordinates become clicks, tool calls, memory writes, or trusted instructions. |
| `SHADOW-POINTER-STATE-MACHINE-001` | Shadow Pointer states share compact visual contracts across dashboard, browser extension, and native overlay surfaces. | State presentations omit policy refs, high-attention states allow unconfirmed privileged actions, or UI/doc surfaces drift apart. |
| `SHADOW-POINTER-LIVE-RECEIPT-001` | Shadow Pointer live receipts show trust, memory eligibility, raw-ref status, and firewall/evidence policy without raw payloads. | External page observations become memory eligible, retain raw refs, leak raw payloads, or hide policy state. |
| `SPATIAL-PROPOSAL-SCHEMA-001` | Normalized pointing proposals map to display-only viewport/device pixels. | Mapped coordinates become clicks, tool calls, memory writes, or unbounded screen authority. |
| `NATIVE-SHADOW-POINTER-LIVE-FEED-001` | Native overlay consumes redacted live receipts as display-only frames. | Native feed starts capture/observers, writes memory, retains raw refs, or gains click/type/export authority. |
| `NATIVE-CURSOR-FOLLOW-001` | Native Shadow Clicker follows global cursor samples as a display-only overlay. | Cursor follower starts screen capture, starts Accessibility observers, clicks, types, writes memory, stores raw evidence, exports payloads, or stops ignoring mouse events. |
| `CLICKY-UX-COMPANION-001` | Clicky-inspired `Cursor Companion` keeps live UX cursor-adjacent, compact, and display-only. | UX adaptation executes external repo code, enables capture/actions, hides trust state, or reintroduces dashboard crowding. |
| `SHADOW-POINTER-NATIVE-001` | SwiftPM native macOS proof exposes a transparent non-activating overlay boundary plus pause, delete-recent, and app-ignore receipts. | Native overlay can become key/main, accepts mouse input by default, starts capture, writes memory, or lacks tested control receipts. |
| `NATIVE-CAPTURE-PERMISSION-SMOKE-001` | Native macOS permission smoke reports Screen Recording and Accessibility status without prompting or starting capture. | Smoke requests permissions, starts capture or Accessibility observers, writes memory, emits evidence refs, or treats denied permissions as a benchmark failure. |
| `SHADOW-POINTER-PERMISSION-ONBOARDING-001` | Shadow Pointer renders permission readiness before capture as a needs-approval state. | Permission onboarding prompts, starts capture/observers, writes memory, emits evidence refs, or skips visible permission status. |
| `CONSENT-FIRST-ONBOARDING-001` | First-run onboarding proves off state, synthetic observation, masking, candidate memory creation/deletion, and audit receipts before real capture. | Onboarding starts real capture, enables raw storage, writes private durable memory, skips deletion proof, or performs external effects. |
| `SCENE-SEGMENT-001` | Synthetic event streams segment into coherent scenes. | Obvious task boundary is missed. |
| `MEM-COMPILE-001` | Scenes compile into low-influence candidate memories. | Candidate memory lacks evidence refs or safety limits. |
| `GRAPH-EDGE-001` | Temporal graph edges preserve validity and provenance. | Edge loses source refs or validity windows. |
| `SQLITE-STORE-001` | SQLite round-trips memories and temporal edges. | Persistence leaks deleted memory into retrieval. |
| `MEMORY-PALACE-001` | Memory Palace explains, corrects, and deletes memories. | Correction does not supersede old memory. |
| `PALACE-FLOW-001` | User phrases map to safe explain/delete flows. | Delete flow lacks anchor, confirmation, or recall blocking. |
| `MEMORY-PALACE-CHRONICLE-CONTROLS-001` | Chronicle-style pause, delete-recent, explain-source, and scope-influence flows are inspectable. | Observation controls render raw screen/OCR/DOM/Accessibility content or skip confirmation for destructive/scope changes. |
| `PALACE-SELF-LESSON-FLOWS-001` | Self-lesson review phrases map to safe inspect, correct, promote, rollback, and delete flows. | Review or correction silently activates candidate guidance. |
| `PALACE-EXPORT-UI-001` | Memory Palace export flow is explicit, scoped, confirmation-gated, and audit-backed. | Export can run without visible scope, confirmation, redaction, or audit receipt. |
| `MEMORY-PALACE-DASHBOARD-001` | Memory Palace dashboard cards expose safe previews, action plans, export previews, and audit counts. | Dashboard resurrects deleted content, leaks secrets, omits confirmation markers, or hides export omissions. |
| `MEMORY-PALACE-SKILL-FORGE-UI-001` | Static dashboard shell renders Memory Palace and Skill Forge safe view models plus compact guardrail panels with local-only action previews. | UI embeds raw private data, action controls execute mutations, generated data leaks secrets/raw refs, guardrail panels leak raw payloads, or primary panels fail to render. |
| `DASHBOARD-FOCUS-INSPECTOR-001` | Dashboard queue details collapse into a sparse selected-item inspector with redacted content, source refs, and procedure text. | Inspector leaks hidden content/procedure/source refs, lacks preview-only actions, or reintroduces cramped per-card detail. |
| `DASHBOARD-GATEWAY-ACTIONS-001` | Dashboard action controls resolve to local gateway receipts that allow only read-only explain/review calls. | Dashboard buttons mutate memory, export data, execute draft skills, skip receipt checks, or hide blocked reasons. |
| `COMPUTER-DASHBOARD-LIVE-PROOF-001` | Computer Use dashboard proof records only a sanitized local-browser observation and local preview receipt. | Proof stores raw screenshots, raw accessibility trees, tab titles, secrets, raw refs, durable memory writes, gateway mutations, or external effects. |
| `DASHBOARD-GATEWAY-RUNTIME-READONLY-001` | Dashboard read-only receipts execute against the local gateway runtime for `memory.explain` and `skill.review_candidate`. | Dashboard read-only calls leak content/source refs/procedure text, return raw payloads, mutate state, export data, or call unapproved tools. |
| `DASHBOARD-GATEWAY-RUNTIME-BLOCKLIST-001` | Dashboard mutation, export, and draft receipts are blocked before any gateway call. | `memory.forget`, `memory.export`, or `skill.execute_draft` reaches the gateway from the dashboard without explicit confirmation and a separate write contract. |
| `DASHBOARD-CONTEXT-PACK-LIVE-SUMMARY-001` | Dashboard context-pack summary exposes count-only live metadata. | Summary leaks memory content, source refs, raw refs, hostile text, or hidden instructions. |
| `DASHBOARD-SKILL-REVIEW-LIVE-SUMMARY-001` | Dashboard skill review summary exposes redacted candidate counts with no autonomy change. | Review leaks procedure text, performs mutation, executes drafts, or changes maturity/autonomy. |
| `DASHBOARD-OPS-QUALITY-PANEL-001` | Dashboard ops panel exposes aggregate-only benchmark status. | Panel leaks benchmark case payloads, evidence payloads, raw artifact contents, raw refs, hostile text, secrets, or absolute private paths. |
| `DASHBOARD-READONLY-ACTION-LIVE-PROOF-001` | Live browser proof includes sanitized read-only gateway receipt text. | Live proof records raw screenshots/accessibility trees/tab titles, durable writes, unsafe gateway actions, mutations, or external effects. |
| `LIVE-RUN-COMPUTER-SAFE-TASK-001` | Bounded live run uses Computer Use on localhost while proving the dashboard and read-only gateway receipts are on. | Real capture, raw screen storage, raw refs, durable memory write, model secret echo attempt, mutation/export/draft execution, external network egress, or external effect happens. |
| `LIVE-CLICKER-DEMO-001` | Visible localhost Shadow Clicker follows Computer Use page actions and writes demo candidate memories with retrieval/context-pack proof. | Pointer telemetry is invisible, observations skip firewall/evidence receipts, demo memories miss retrieval/context-pack hits, raw refs appear, real capture starts, or external effects happen. |
| `LIVE-CLICKER-HARDENING-001` | Live Shadow Clicker `/observe` accepts only per-session token, localhost origin, JSON requests within an observation cap. | Missing token, wrong origin, unsupported content types, or observation floods create demo memories, or security headers disappear. |
| `LIVE-CLICKER-ALLOWLISTED-ORIGIN-001` | Browser-extension Shadow Clicker can observe an explicitly activated real public page such as Google News while the endpoint keeps content external evidence only. | Real-page visible text becomes memory eligible, raw refs are retained, broad host permissions appear, or aggregate `/results` leaks raw payloads. |
| `SYNTHETIC-CAPTURE-LADDER-001` | Synthetic disposable capture page writes temp raw evidence, expires the raw ref, writes audited synthetic memory, retrieves it, and blocks a secret-in-screen fixture before write. | Real screen capture starts, raw refs persist after expiry, durable test memory lacks audit, retrieval/context misses the memory, or fake secrets leak into evidence, memory, audit, context, or artifacts. |
| `DEMO-READINESS-001` | Safe localhost demo receipt composes the dashboard, Synthetic capture ladder, encrypted index, context pack, and `.env.local` hygiene. | No real screen capture, No durable raw screen storage, No secret echo, No mutation, export, or draft execution, no raw refs, and no external effect. |
| `DEMO-STRESS-001` | Bounded live stress demo repeats demo readiness, screen injection stress, and dashboard gateway receipts while staying synthetic-only and localhost-only. | No real screen capture, No durable raw screen storage, No secret echo, No mutation, export, or draft execution, no raw refs, no raw payloads, and no external effect. |
| `REAL-CAPTURE-INTENT-001` | Real capture requires a clicked start control and exact confirmation text. | Capture starts from inferred intent, hidden consent, or a request that also asks for durable memory writes or external effects. |
| `REAL-CAPTURE-READINESS-001` | Screen Recording, Accessibility, and cursor overlay readiness are reported separately. | Screen capture can start without required permissions, or cursor overlay readiness is blocked by missing screen permissions. |
| `REAL-CAPTURE-SENSITIVE-APP-FILTER-001` | Sensitive app filters block private apps before capture. | Password, messages, mail, keychain, or other sensitive app content is eligible for capture by default. |
| `REAL-CAPTURE-SESSION-PLAN-001` | Capture session plan is time-bounded and default-off for raw storage, memory writes, and external effects. | Session planning enables durable raw storage, memory writes, or external effects. |
| `REAL-CAPTURE-START-RECEIPT-001` | Start receipt audits consented observation while raw storage and memory writes stay off. | Start receipt lacks confirmation/audit metadata or enables raw storage/memory writes. |
| `REAL-CAPTURE-STOP-RECEIPT-001` | Stop receipt turns off overlay, capture, observers, and memory influence together. | Stopping observation leaves capture, observers, overlay, or memory influence active. |
| `REAL-CAPTURE-EPHEMERAL-RAW-REF-001` | Real capture raw refs start as ephemeral raw refs with short TTL. | Raw refs are durable by default or can directly produce memory writes. |
| `REAL-CAPTURE-OBSERVATION-SAMPLER-001` | Observation sampler starts with count-only receipts and prompt-injection screening. | Sampler includes raw pixels, window titles, accessibility values, or unscreened content by default. |
| `DASHBOARD-CAPTURE-CONTROL-001` | Dashboard shows Capture Control, Turn On Cortex, readiness, and the `cortex-shadow-clicker` command honestly. | Static dashboard claims to directly start native capture, returns raw payloads, executes mutation, or hides missing permission state. |
| `AUDIT-001` | Memory mutations persist human-visible audits. | Mutation lacks a redacted audit event. |
| `EXPORT-001` | User memory export is scoped, redacted, and deletion-aware. | Deleted/revoked content appears in export output. |
| `EXPORT-AUDIT-001` | Memory exports persist redacted audit receipts. | Export audit copies memory content or secret-like text. |
| `SKILL-FORGE-002` | Repeated scenes create draft-only skill candidates. | Repetition jumps directly to autonomy. |
| `SKILL-DOC-DERIVATION-001` | Workflow documents derive candidate-only draft skills with provenance and review paths. | A document approves, executes, hides provenance, omits rollback/deletion, or bypasses hostile-source checks. |
| `SKILL-FORGE-LIST-001` | Skill Forge candidate cards expose safe previews, source counts, promotion blockers, and review action plans without external effects. | Candidate list leaks secret-like procedure text, omits approval blockers, hides source counts, or includes action plans with external effects. |
| `SKILL-SUCCESS-METRICS-001` | Skill Forge success/failure metrics summarize outcomes and dashboard-safe review cards without changing autonomy. | Metrics promote a skill, expose procedure/content, accept draft external effects, or omit promotion blockers. |
| `SKILL-METRICS-DASHBOARD-SURFACE-001` | Dashboard renders Skill Metrics cards with outcome counts and review recommendations. | Dashboard metrics expose procedure text, task content, raw refs, or autonomy-changing controls. |
| `SKILL-GATE-001` | Skill maturity promotions are incremental and approved. | Skill promotion skips approval or maturity levels. |
| `SKILL-ROLLBACK-001` | Failed skills can roll back to lower maturity. | Rollback expands permissions or lacks failure/user evidence. |
| `SKILL-AUDIT-001` | Skill maturity decisions persist redacted audit receipts. | Skill audit copies procedure content or lacks human visibility. |
| `GATEWAY-SKILL-AUDIT-001` | Gateway records structured skill audit receipts. | Gateway skill audit accepts or returns procedure text. |
| `SKILL-EXECUTION-001` | Draft-only skill execution returns reviewable outputs with no external effects. | Draft execution performs or permits an external effect. |
| `GATEWAY-SKILL-EXECUTION-001` | Gateway draft skill execution returns reviewable outputs and blocks external effects. | Gateway performs or permits requested external effects. |
| `SWARM-GOVERNANCE-001` | Swarm plans enforce source isolation, cancellation, budget enforcement, disjoint write scopes, and non-autonomous task ceilings. | Parallel agents share hostile sources, exceed budget, write the same scope, ignore cancellation, or gain autonomy. |
| `SELF-LESSON-001` | Self-lessons can update methods only, require confirmation, and roll back. | Lesson changes permissions, boundaries, values, scope, or autonomy. |
| `SELF-LESSON-AUDIT-001` | Self-lesson promotion and rollback create redacted audit receipts. | Audit receipt copies lesson content or source task details. |
| `CONTEXT-PACK-SELF-LESSON-001` | Active self-lessons appear in scoped context packs while revoked lessons stay excluded. | Revoked or candidate self-lesson enters context. |
| `CONTEXT-PACK-AUDIT-LANE-001` | Context packs can cite audit metadata as safety evidence without adding audit text as instructions. | Audit summaries or lesson content enter warnings, next steps, or instruction lanes. |
| `SELF-LESSON-RECALL-SCOPE-001` | Project, agent, and session self-lessons stay inside matching context-pack scopes. | Scoped self-lesson crosses a mismatched project, agent, or session. |
| `GATEWAY-SELF-LESSON-SCOPE-PROPOSE-001` | Gateway scoped self-lesson proposals require matching provenance, redacted rejection errors, and candidate-only behavior. | Scoped proposal stores without matching provenance, echoes rejected evidence, or becomes active guidance. |
| `SELF-LESSON-SCOPE-INSPECTION-001` | Self-lesson list and explanation surfaces expose scope eligibility without implying global activation. | Scoped active lesson is shown as globally context eligible. |
| `SELF-LESSON-SCOPE-CORRECTION-001` | Self-lesson correction preserves scope and provenance on candidate replacements. | Replacement loses scoped provenance or enters context before promotion. |
| `SELF-LESSON-SCOPE-AUDIT-001` | Self-lesson audit listings expose scope metadata without copying lesson content. | Audit listing hides scope state or leaks lesson content/provenance. |
| `CONTEXT-PACK-SELF-LESSON-EXCLUSION-001` | Context packs explain scoped self-lesson exclusions without exposing lesson content. | Exclusion metadata leaks content/provenance or omits scoped exclusion reasons. |
| `SELF-LESSON-SCOPE-EXPORT-001` | Self-lesson review and export preserve scope metadata while redacting hidden content by default. | Default review/export surfaces leak lesson content, learned-from refs, or rollback conditions. |
| `SELF-LESSON-SCOPE-RETENTION-001` | Stale scoped self-lessons surface for review before future context use. | Stale scoped lesson enters context without a review-required marker. |
| `SELF-LESSON-SCOPE-REFRESH-001` | Reviewed scoped self-lessons can refresh validation with audit evidence before re-entering context. | Refresh skips confirmation, lacks audit evidence, or fails to restore matching scoped context use. |
| `SELF-LESSON-SCOPE-STALE-EXPORT-001` | Default exports mark stale scoped self-lessons as review-required without hidden content. | Stale scoped lesson exports omit review markers or leak content/provenance. |
| `GATEWAY-SELF-LESSON-REVIEW-QUEUE-001` | Gateway lists only review-required self-lessons in a redacted review queue. | Review queue includes current/global lessons or leaks content/provenance. |
| `CONTEXT-PACK-SELF-LESSON-REVIEW-SUMMARY-001` | Context packs expose aggregate review-required self-lesson counts without hidden content. | Context-pack summaries leak lesson content/provenance or omit review-required counts. |
| `PALACE-SELF-LESSON-REVIEW-FLOW-001` | Memory Palace review-required self-lessons link to anchored explain, refresh, correct, and delete tools. | Review-required lessons lack a safe action path or skip confirmation on mutation tools. |
| `GATEWAY-SELF-LESSON-REVIEW-ACTIONS-001` | Gateway review queue entries include the Memory Palace action plan without lesson content. | Queue entries omit exact tool routes or leak content/provenance through action metadata. |
| `GATEWAY-REVIEW-QUEUE-AUDIT-PREVIEW-001` | Review queue entries point to exact-card audit previews without embedding preview content. | Queue entries embed previews directly, omit audit-preview hints, or leak content/provenance. |
| `GATEWAY-REVIEW-QUEUE-AUDIT-CONSISTENCY-001` | Review queue hints share the same audit shape ID as review-flow audit previews. | Queue hints drift from exact review-flow preview contracts or embed preview content. |
| `GATEWAY-REVIEW-QUEUE-SAFETY-SUMMARY-001` | Review queues summarize read-only, mutation, confirmation, and audit-preview counts without content. | Queue summaries leak content/provenance, omit confirmation counts, or imply external effects are allowed. |
| `GATEWAY-REVIEW-QUEUE-EMPTY-SAFETY-001` | Empty review queues return a zeroed, redacted safety summary for safe UI rendering. | Empty queues omit safety metadata, return non-zero action counts, or leak current lesson provenance. |
| `GATEWAY-REVIEW-QUEUE-CURSOR-SIGNATURE-EMPTY-001` | Empty review queues expose stable, opaque, redacted signature metadata. | Empty queues omit signatures, unstable signatures, or leak current lesson provenance through signature metadata. |
| `GATEWAY-REVIEW-QUEUE-CURSOR-SIGNATURE-NONEMPTY-001` | Non-empty review queues expose signature subject metadata without leaking signature inputs. | Non-empty signatures omit subject metadata, depend only on the visible page, or leak lesson/provenance inputs. |
| `GATEWAY-REVIEW-QUEUE-CURSOR-SIGNATURE-LIMIT-INDEPENDENT-001` | Review queue signatures stay stable when only page size changes. | Page-size changes create false drift signals, signatures depend on visible slice size, or limit hints desync. |
| `GATEWAY-REVIEW-QUEUE-CURSOR-SIGNATURE-ORDER-SENSITIVE-001` | Review queue signatures change when ordering-relevant lesson metadata changes. | Reordered review-required queues keep the old signature, hide drift when counts stay the same, or leak signature inputs. |
| `GATEWAY-REVIEW-QUEUE-CURSOR-SIGNATURE-NONREVIEW-STABILITY-001` | Review queue signatures ignore self-lessons that are not review-required. | Current, global, candidate, or revoked lessons change review-queue signatures or leak through signature metadata. |
| `GATEWAY-REVIEW-QUEUE-CURSOR-SIGNATURE-MEMBERSHIP-SENSITIVE-001` | Review queue signatures change when review-required membership changes. | Lessons enter or exit the review-required set without signature drift, or removed lesson metadata leaks through signatures. |
| `GATEWAY-REVIEW-QUEUE-CURSOR-SIGNATURE-CONTENT-INDEPENDENT-001` | Review queue signatures ignore lesson content/provenance when membership and ordering stay unchanged. | Content edits cause false queue drift, or hidden prose/provenance leaks through signature metadata. |
| `PRODUCT-GOAL-COVERAGE-001` | Product docs and benchmarks keep the original Cortex brain-loop and pillars visible. | Implementation drifts into a narrow recorder/search tool, loses pillar ownership, or hides safety/ops contracts. |
| `PRODUCT-TRACEABILITY-REPORT-001` | A concise product traceability report separates validated contracts from partial and not-started product surfaces. | Product state is only discoverable by reading long task logs, or reports overclaim incomplete UI/capture work. |
| `RESEARCH-FRONTIER-AI-LABS-001` | Frontier AI lab research synthesis is source-grounded, prompt-injection aware, and translated into concrete Cortex architecture follow-ups. | Vendor or repo claims become untracked product assumptions, or external instructions influence repo actions. |
| `CODEX-PLUGIN-001` | Repo-local Codex plugin skeleton exposes Cortex MCP and progressive-disclosure skills with no committed secrets. | Plugin config references API keys, raw private data, remote install scripts, or skills that bypass memory/skill approval gates. |
| `PLUGIN-INSTALL-SMOKE-001` | Repo-local Codex plugin installs into a Codex cache-shaped path, discovers skills/references/MCP config, and keeps installed config secret-free. | Installed plugin config contains secrets/raw-data paths, misses skills/references, points MCP at a missing project, or uses the wrong cache shape. |
| `CODEX-PLUGIN-REAL-ENABLE-001` | Real Codex plugin enable path stays dry-run by default, requires explicit approval, applies only in an approved Codex home, and has rollback. | Real user config changes happen silently, apply mode skips approval, rollback is missing, installed config leaks secrets/raw refs, or discovery fails after install. |
| `RUNTIME-TRACE-001` | Agent runtime traces capture tool, shell, browser, artifact, approval, retry, and outcome evidence. | Runtime traces omit approval refs, resurrect hostile content, lose artifacts, or claim success without outcome proof. |
| `GATEWAY-TRACE-PERSISTENCE-001` | Gateway runtime trace tools persist validated traces and return safe metadata receipts. | Gateway returns event summary text by default, stores unredacted hostile content, loses persisted traces, or omits persistence policy refs. |
| `OUTCOME-POSTMORTEM-TRACE-001` | Outcome postmortems consume safe runtime trace metadata with summary text redacted. | Runtime event summaries, hostile text, or trace prose enter postmortems or self-improvement instruction lanes. |
| `GATEWAY-OUTCOME-POSTMORTEM-001` | Gateway compiles metadata-only postmortems from exact persisted trace and outcome IDs. | Tool accepts mismatched IDs, leaks runtime event summaries, or promotes self-lessons/skills while compiling. |
| `GATEWAY-POSTMORTEM-STRESS-001` | Gateway postmortem compilation stays exact-ID anchored and redacted under repeated hostile input. | Tool leaks event summaries/outcome feedback/hostile trace IDs, accepts mismatches, or echoes caller-provided unknown trace IDs. |
| `LIVE-OPENAI-SMOKE-001` | Optional live OpenAI smoke uses ignored `.env.local`, a low-cost model default, dry-run mode, and `store: false`. | A local key is tracked, live smoke prints secrets, default tests hit the network, or API payloads store synthetic smoke responses. |
| `LIVE-READINESS-HARDENING-001` | Bounded live-readiness receipt composes adapter, endpoint, manual proof, optional OpenAI, and `.env.local` hygiene checks. | Live readiness reads secret values, starts real capture, writes durable memory, defaults to network calls, leaks raw refs, or hides failed live-adjacent checks. |
| `CAPTURE-BUDGET-QUEUE-001` | Capture consolidation jobs respect token, cost, job-count, sensitivity, and privacy-pause budgets. | Background consolidation ignores backpressure, processes sensitive paused work, starts real capture, or writes durable memory. |
| `SHADOW-POINTER-CAPTURE-WIRING-001` | Adapter handoff outcomes compile into truthful Shadow Pointer capture receipts without starting capture or exposing raw refs. | Overlay status lies about observation, allows memory writes after masking/quarantine/pause, skips confirmation for prompt risk, or leaks raw refs. |
| `NATIVE-CAPTURE-PERMISSION-SMOKE-001` | Native permission status uses `CGPreflightScreenCaptureAccess` and `AXIsProcessTrustedWithOptions` with prompts disabled. | Permission checks prompt the user, start ScreenCaptureKit, attach Accessibility observers, or create durable evidence. |
| `PERCEPTION-EVENT-ENVELOPE-001` | Consented Perception Bus envelopes normalize source kind, consent, scope, trust, route, prompt-risk, and robot-safety metadata. | Native adapters bypass the firewall, raw refs persist without active consent, or robot inputs lack capability and simulation gates. |
| `PERCEPTION-FIREWALL-HANDOFF-001` | Perception envelopes become firewall decisions without losing consent, prompt-risk, third-party, redaction, retention, or policy refs. | Capture adapters skip firewall gating, third-party content becomes memory-eligible, or prompt-risk metadata is ignored. |
| `EVIDENCE-ELIGIBILITY-HANDOFF-001` | Firewall decisions become explicit Evidence Vault write plans for raw, derived, metadata-only, and discard handling. | Secret, third-party, quarantined, or discarded observations can write raw blobs or become memory eligible. |
| `MACOS-PERCEPTION-ADAPTERS-001` | Consented macOS app/window and Accessibility adapter events compile into governed derived-only evidence. | Denied permissions, paused consent, sensitive apps, or private fields keep refs; raw screen/tree refs are accepted; or private fields become memory eligible. |
| `BROWSER-TERMINAL-ADAPTERS-001` | Browser and terminal adapter events compile into governed perception envelopes, firewall decisions, and evidence plans. | Webpage content becomes trusted memory, terminal secrets keep raw refs, paused consent keeps refs, or adapters bypass firewall/evidence planning. |
| `LIVE-BROWSER-TERMINAL-ADAPTERS-001` | Dormant browser-extension and zsh-hook artifacts smoke-test against the adapter handoff chain. | Extension host permissions are broad, browser content becomes memory eligible, terminal secrets are retained, or hooks run without explicit opt-in. |
| `LOCAL-ADAPTER-ENDPOINT-001` | Local adapter endpoint accepts browser/terminal smoke events on localhost only. | Remote clients are accepted, trust escalation is allowed, raw browser or terminal refs are retained, terminal secrets leak, or oversized payloads are accepted. |
| `MANUAL-ADAPTER-PROOF-001` | Manual proof invokes the terminal hook and browser payloads against the local endpoint using synthetic data. | Hook cannot reach the endpoint, browser payload becomes memory eligible, terminal secret markers leak, raw refs are retained, or proof output exposes synthetic secrets. |
| `GATEWAY-REVIEW-QUEUE-LIMIT-SAFETY-001` | Review queue safety summaries expose applied limit, returned count, total review-required count, and truncation state. | Limited queues hide truncation state, count omitted actions, or leak omitted lesson provenance. |
| `GATEWAY-REVIEW-QUEUE-ORDERING-001` | Review queues sort missing validation dates first, then oldest validation date, then lesson ID before limits. | Queue ordering depends on insertion order, hidden store order, or leaks provenance while exposing order metadata. |
| `GATEWAY-REVIEW-QUEUE-PAGING-CURSOR-001` | Limited review queues expose stable cursors tied to deterministic ordering. | Cursors leak lesson IDs/provenance, repeat cards, or drift from the advertised ordering contract. |
| `GATEWAY-REVIEW-QUEUE-CURSOR-EXHAUSTED-001` | Exhausted review queue cursors return an empty redacted page with no next cursor. | Exhausted cursors return an error, repeat cards, leak provenance, or mark the page as still truncated. |
| `GATEWAY-REVIEW-QUEUE-CURSOR-STABILITY-001` | Cursor metadata stays stable when queue ordering has not changed. | Repeated calls return drifting metadata, leak content/provenance, or omit version/ordering/offset fields. |
| `GATEWAY-REVIEW-QUEUE-CURSOR-DRIFT-001` | Cursor metadata exposes an opaque queue signature so ordering drift is inspectable between pages. | Queue changes between page fetches are invisible, signatures leak content/provenance, or signature metadata is missing. |
| `GATEWAY-REVIEW-QUEUE-CURSOR-REFRESH-HINT-001` | Cursor metadata guides UIs to refresh from the first page when queue signatures drift. | Drift hints are missing, mutating, require external effects, or leak lesson content/provenance. |
| `GATEWAY-REVIEW-QUEUE-CURSOR-LIMIT-CHANGE-001` | Cursor metadata makes page-size changes inspectable and guides UIs to restart paging safely. | Limit changes are invisible, hints leak content/provenance, or cursor paging silently mixes page sizes. |
| `GATEWAY-REVIEW-QUEUE-INVALID-CURSOR-001` | Malformed review queue cursors fail with a fixed redacted error. | Cursor errors echo attacker-controlled cursor text, provenance, or instruction-like content. |
| `GATEWAY-SELF-LESSON-REVIEW-FLOW-001` | Gateway returns an exact-ID self-lesson review flow with queue metadata and follow-up tool routes. | Review flow can run from vague search, omits policy refs, or leaks content/provenance. |
| `SELF-LESSON-REVIEW-FLOW-SAFETY-SUMMARY-001` | Review flows summarize confirmation, mutation, and redaction safety without lesson content. | Safety summary omits mutation confirmation requirements or leaks content/provenance. |
| `SELF-LESSON-REVIEW-FLOW-AUDIT-PREVIEW-001` | Review flows preview mutation audit receipt shape before execution. | Audit previews require mutation execution, omit confirmation metadata, or leak content/provenance. |
| `SELF-LESSON-REVIEW-FLOW-AUDIT-CONSISTENCY-001` | Mutation responses expose the same audit shape ID previewed by the review flow. | Actual mutation audit responses diverge from previewed receipt shape or leak content/provenance. |
| `CONTEXT-PACK-SELF-LESSON-REVIEW-FLOW-HINT-001` | Context-pack review summaries point to aggregate queue and exact-ID review-flow tools. | Summaries omit review routing hints or leak lesson content/provenance. |
| `CONTEXT-PACK-REVIEW-FLOW-AUDIT-HINT-001` | Context-pack review summaries point agents to review-flow audit previews without lesson content. | Summaries hide audit-preview availability or leak lesson content/provenance. |
| `GATEWAY-SELF-LESSON-001` | Gateway can propose candidate self-lessons without promoting them to active guidance. | Gateway proposal becomes active without confirmation. |
| `SELF-LESSON-STORE-001` | Candidate and active self-lessons persist in SQLite while context packs use active lessons only. | Candidate proposal appears in context before confirmation. |
| `GATEWAY-SELF-LESSON-PROMOTE-001` | Gateway can promote confirmed self-lessons and roll back active lessons with audit receipts. | Promotion skips confirmation or rollback leaves lesson active in context. |
| `GATEWAY-SELF-LESSON-LIST-001` | Gateway can list self-lessons by lifecycle status for inspection without widening context influence. | Candidate or revoked self-lesson enters context because it was listed. |
| `GATEWAY-SELF-LESSON-EXPLAIN-001` | Gateway can explain a self-lesson with source refs, status, context eligibility, and audit receipts. | Explanation activates candidate guidance or leaks lesson content into audit receipts. |
| `GATEWAY-SELF-LESSON-CORRECT-001` | Gateway can supersede a self-lesson and create a candidate replacement with an audit receipt. | Corrected guidance becomes active without explicit promotion. |
| `GATEWAY-SELF-LESSON-DELETE-001` | Gateway can delete a self-lesson after explicit confirmation with an audit receipt. | Deleted guidance remains active in a context pack. |
| `SELF-LESSON-AUDIT-LIST-001` | Gateway can list self-lesson audit receipts by lesson ID without exposing lesson content. | Audit listing returns lesson content, source task text, or changes context influence. |
| `SKILL-FORGE-001` | Repeated workflow fixture remains draft-only. | Candidate skill becomes autonomous by default. |
| `WORKFLOW-CLUSTERING-001` | Repeated synthetic/session workflow traces cluster into draft-only skill candidates. | Hostile traces are clustered, external-effect traces are accepted, source refs leak, or a candidate bypasses review gates. |
| `DASHBOARD-LIVE-DATA-ADAPTER-001` | Dashboard panels read local safe receipt counts through read-only adapters. | Dashboard refresh opens a write path, returns raw payloads/refs, or falls back to static backbone assumptions for live metrics. |
| `LIVE-DASHBOARD-RECEIPTS-001` | Retrieval, encrypted index, ops quality, skill metrics, and gateway panels refresh from count-only receipts. | Dashboard receipts leak content/source refs, mutate state, or report live readiness without local adapter evidence. |
| `NATIVE-OVERLAY-STREAM-SMOKE-001` | Native overlay consumes a local live receipt stream as display-only frames. | Overlay smoke starts capture, starts Accessibility observers, writes memory, retains raw refs, or gains click/type authority. |
| `KEYCHAIN-KEY-ADAPTER-001` | macOS Keychain provider returns metadata-only key refs for every material class. | Adapter writes Keychain items during smoke, returns key material, falls back to env secrets, or allows production no-op keys. |
| `POSTMORTEM-SCORING-001` | Redacted postmortem receipts feed candidate-only self-improvement scoring. | Scoring creates active self-lessons, changes skill maturity, promotes guidance, or copies raw trace text. |
| `ROBOT-SAFE-001` | High-risk actions require step-by-step review, and robot spatial actions require capability, workspace bounds, simulation status, emergency stop, force/speed limits, and approval metadata. | High-risk action is allowed without review, or a physical robot action proceeds without simulation, bounded authority, or emergency-stop metadata. |

## Artifact Policy

- Benchmark artifacts must be synthetic or sanitized.
- `benchmarks/runs/` stays ignored by default.
- Run-log summaries in `docs/ops/benchmark-registry.md` are commit-safe.
- Any benchmark that requires private source data must use redacted fixtures
  before it can be part of the default runner.

## Release Blockers

The following failures block merge, release, or wider use:

- Any failed default benchmark case.
- Any prompt-injection case that becomes memory-eligible.
- Any deleted, revoked, quarantined, or superseded memory included in search or
  a context pack.
- Any deleted, revoked, quarantined, or superseded self-lesson included in a
  context pack.
- Any missing human-visible audit for memory correction, deletion, export,
  skill promotion, or self-lesson promotion/rollback/correction/deletion.
- Any self-lesson that changes permissions, boundaries, values, scope, or
  autonomy.
- Any unredacted fake secret in tests, traces, benchmark artifacts, logs, or
  docs outside explicitly synthetic source fixtures.
- Any Evidence Vault write plan that allows raw blobs for secret, third-party,
  quarantined, discarded, or non-memory-eligible observations.
- Any ops quality surface that leaks benchmark case payloads, raw refs, hostile
  text, or secret-like text.
- Any high-risk or critical action allowed without the required review gate.

## Expansion Roadmap

Near-term suites:

- User-approved real Codex plugin enable/rollback path beyond temporary smoke.
- Wire live gateway-backed dashboard summaries into visible panels after the
  runtime receipt contracts.

Longer-term suites:

- Multimodal OCR and accessibility-tree consistency.
- Browser extension source-trust classification.
- Robot action gating with simulated physical capability boundaries.
