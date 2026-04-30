# Benchmark Registry

Last updated: 2026-04-30

Benchmarks should become runnable as soon as implementation begins. Until then, this registry defines what must be measurable.

## Benchmark Suites

| ID | Suite | Purpose | Primary metrics | Initial gate |
| --- | --- | --- | --- | --- |
| MEM-RECALL-001 | Controlled recall | Verify that stored memories can be retrieved under explicit user intent | precision, recall, citation/provenance accuracy, latency | TBD after first storage design |
| MEM-FORGET-001 | Deletion and revocation | Verify deleted or revoked memories are not recalled or exported | deletion success, leakage rate, audit completeness | zero known deleted-memory recall |
| SEC-INJECT-001 | Prompt-injection resistance | Ensure untrusted memory/source text cannot override policy or tool boundaries | attack success rate, refusal accuracy, false positives | zero critical policy escapes |
| SEC-PII-001 | Sensitive-data handling | Detect accidental logging, committing, or surfacing of secrets and PII | leakage count, redaction accuracy | zero committed secrets |
| PERF-LAT-001 | Memory operation latency | Track read/write/retrieval speed under realistic local loads | p50, p95, p99 latency, throughput | TBD after storage engine choice |
| CONTEXT-FUSION-INDEX-STUB-001 | Hybrid context fusion index | Verify semantic, sparse, graph, recency, and trust signals fuse behind a safe dependency-free contract | included count, excluded reason tags, top score, redaction checks | prompt-risk candidates excluded, raw refs rejected, result content redacted |
| CODEX-PLUGIN-001 | Codex plugin skeleton | Verify plugin manifest, local MCP config, progressive-disclosure skills, source-trust references, and no-secret gateway packaging | manifest coverage, skill coverage, blocked secret refs, research traceability | zero secret refs in plugin MCP config |
| PLUGIN-INSTALL-SMOKE-001 | Cortex plugin install/discovery smoke | Verify the repo-local plugin can install into a Codex cache-shaped path and discover skills, references, MCP config, and secret-free installed metadata | discovery pass rate, skill count, blocked config hits, missing path count | installed config has zero blocked secret/raw-data refs |
| CODEX-PLUGIN-REAL-ENABLE-001 | Real Codex plugin enable path | Verify dry-run default, exact approval phrase, temp-home apply/discovery, rollback path, and no real config mutation by default | dry-run write count, approval block count, discovery pass rate, rollback success, blocked secret refs | no writes without approval, temp-home install discovers, rollback removes plugin |
| SHADOW-POINTER-NATIVE-001 | Native Shadow Pointer overlay proof | Verify SwiftPM native macOS overlay boundary, display-only pointer behavior, and pause/delete/app-ignore receipt semantics | Swift build/test pass, overlay safety terms, control receipt coverage | non-activating overlay, no default mouse events, zero memory writes from blocked controls |
| NATIVE-CAPTURE-PERMISSION-SMOKE-001 | Native capture permission smoke | Verify macOS Screen Recording and Accessibility status can be inspected without prompting, capture, observers, memory writes, or evidence refs | status receipt pass, allowed effect count, blocked effect count, evidence ref count | only read permission status, zero prompts, zero capture/observer starts |
| SHADOW-POINTER-CAPTURE-WIRING-001 | Shadow Pointer capture wiring | Verify adapter handoff outcomes become truthful overlay receipts for observing, masking, approval, paused, and off states without raw refs | state mapping pass rate, blocked memory writes, confirmation gates, raw-ref exposure count | zero raw refs, no memory writes from masked/quarantined/paused outcomes |
| MACOS-PERCEPTION-ADAPTERS-001 | macOS app/window and Accessibility adapter contracts | Verify consent, macOS permission, app allowlist, private-field, no-raw-capture, and evidence eligibility gates | adapter pass rate, derived-only write rate, discarded private/denied events, raw-ref retention | derived-only allowed evidence, zero raw screen/tree refs, private fields discarded |
| BROWSER-TERMINAL-ADAPTERS-001 | Browser and terminal adapter contracts | Verify first capture adapters preserve consent, source trust, prompt-risk, redaction, and evidence eligibility rules | adapter pass rate, raw-ref drop count, memory eligibility by source trust | zero web memory eligibility and zero raw secret retention |
| LIVE-BROWSER-TERMINAL-ADAPTERS-001 | Live adapter artifact smoke | Verify dormant browser-extension and terminal-hook artifacts stay opt-in, localhost-scoped, raw-web-memory-free, and secret-redacted | artifact pass rate, host permission violations, memory eligibility by source, secret retention | zero broad host permissions, zero raw web refs, zero terminal secret retention |
| LOCAL-ADAPTER-ENDPOINT-001 | Local adapter endpoint smoke | Verify localhost-only browser/terminal ingest rejects remote clients, trust escalation, raw refs, oversized payloads, and secret retention | HTTP smoke pass rate, rejection status codes, raw-ref retention, memory eligibility | localhost-only, no raw refs, no terminal secret retention, rejected trust escalation |
| MANUAL-ADAPTER-PROOF-001 | Manual adapter proof | Verify real terminal hook invocation and browser-extension-shaped payloads against the local endpoint with synthetic data only | proof pass rate, hook event observation, redaction checks, memory eligibility, raw-ref retention | terminal hook observed, no fake secret output, no raw refs, browser injection discarded |
| MEMORY-PALACE-SKILL-FORGE-UI-001 | Cortex dashboard shell | Verify the local dashboard renders Memory Palace and Skill Forge safe view models with inert action previews and no raw private data | UI smoke pass rate, card counts, local action receipts, secret/raw-ref retention | primary panels render, action previews inert, zero secret/raw refs |
| DASHBOARD-GATEWAY-ACTIONS-001 | Dashboard gateway action receipts | Verify dashboard controls prepare local gateway receipts while allowing only read-only explain/review calls | receipt count, read-only allow count, blocked mutation/export/draft count, raw-ref exposure | only `memory.explain` and `skill.review_candidate` allowed, zero raw refs |
| RUNTIME-TRACE-001 | Agent runtime trace contract | Verify agent tool, shell, browser, artifact, approval, retry, blocked-hostile, and outcome events are ordered and redacted | event count, approval refs, retry refs, evidence refs, outcome check | successful traces require outcome checks and hostile content stays redacted |
| GATEWAY-TRACE-PERSISTENCE-001 | Gateway runtime trace persistence | Verify gateway record/get/list tools persist traces and return safe metadata receipts | persisted trace count, summary redaction, evidence refs, policy refs | zero event summary text returned by default, persistence policy ref present |
| ROBOT-SAFE-001 | Embodied action gating | Ensure memory-triggered physical actions require explicit capability, spatial metadata, simulation, emergency stop, and approval | unauthorized action rate, approval trace completeness, spatial metadata completeness | zero unauthorized actions |

## Run Log

| Date | Benchmark | Command / Method | Result | Evidence | Follow-up |
| --- | --- | --- | --- | --- | --- |
| 2026-04-27 | Registry initialized | Manual documentation pass | Not runnable yet | This file | Add runnable harness after first implementation skeleton. |
| 2026-04-27 | Architecture intake benchmark plan | Manual architecture pass | Not runnable yet | `docs/security/initial-threat-model.md`, `docs/product/build-roadmap.md` | Implement `BENCH-002` with synthetic fixtures. |
| 2026-04-27 | First synthetic safety/memory harness | `uv run cortex-bench` | 6/6 passed | `benchmarks/runs/bench_20260427T184527Z.json` | Add vault expiry and MCP context-pack cases next. |
| 2026-04-27 | Safety/memory/vault harness | `uv run cortex-bench` | 7/7 passed | `benchmarks/runs/bench_20260427T184648Z.json` | Add MCP context-pack cases next. |
| 2026-04-27 | Safety/memory/vault/gateway harness | `uv run cortex-bench` | 8/8 passed | `benchmarks/runs/bench_20260427T184759Z.json` | Add scene segmentation and Shadow Pointer state cases next. |
| 2026-04-27 | Safety/memory/vault/gateway/UI harness | `uv run cortex-bench` | 9/9 passed | `benchmarks/runs/bench_20260427T185055Z.json` | Add scene segmentation case next. |
| 2026-04-27 | Safety/memory/vault/gateway/UI/scene harness | `uv run cortex-bench` | 10/10 passed | `benchmarks/runs/bench_20260427T185207Z.json` | Add memory compiler case next. |
| 2026-04-27 | Safety/memory/vault/gateway/UI/scene/compiler harness | `uv run cortex-bench` | 11/11 passed | `benchmarks/runs/bench_20260427T185311Z.json` | Add temporal graph edge case next. |
| 2026-04-27 | Safety/memory/vault/gateway/UI/scene/compiler/graph harness | `uv run cortex-bench` | 12/12 passed | `benchmarks/runs/bench_20260427T185412Z.json` | Next benchmark: SQLite persistence. |
| 2026-04-27 | Persistence harness | `uv run cortex-bench` | 13/13 passed | `benchmarks/runs/bench_20260427T190003Z.json` | Next benchmark: Skill Forge detector. |
| 2026-04-27 | Skill Forge harness | `uv run cortex-bench` | 14/14 passed | `benchmarks/runs/bench_20260427T190124Z.json` | Next benchmark: Memory Palace correction/delete. |
| 2026-04-27 | Memory Palace harness | `uv run cortex-bench` | 15/15 passed | `benchmarks/runs/bench_20260427T190340Z.json` | Next benchmark: Memory Palace audit events. |
| 2026-04-27 | Memory Palace audit harness | `uv run cortex-bench` | 16/16 passed | `benchmarks/runs/bench_20260427T190513Z.json` | Next benchmark: gateway correction/delete tools. |
| 2026-04-27 | Gateway Memory Palace harness | `uv run cortex-bench` | 17/17 passed | `benchmarks/runs/bench_20260427T190709Z.json` | Next benchmark: deterministic retrieval scoring. |
| 2026-04-27 | Retrieval scoring harness | `uv run cortex-bench` | 18/18 passed | `benchmarks/runs/bench_20260427T190913Z.json` | Next benchmark: scope-aware retrieval policy. |
| 2026-04-27 | Scope retrieval policy harness | `uv run cortex-bench` | 19/19 passed | `benchmarks/runs/bench_20260427T191045Z.json` | Next benchmark: scored context-pack compilation. |
| 2026-04-27 | Scored context-pack harness | `uv run cortex-bench` | 20/20 passed | `benchmarks/runs/bench_20260427T191225Z.json` | Next benchmark: secret and PII handling policy. |
| 2026-04-27 | Secret/PII policy harness | `uv run cortex-bench` | 21/21 passed | `benchmarks/runs/bench_20260427T191409Z.json` | Next benchmark: debug trace redaction. |
| 2026-04-27 | Debug trace harness | `uv run cortex-bench` | 22/22 passed | `benchmarks/runs/bench_20260427T191538Z.json` | Next benchmark: Skill Forge maturity gates. |
| 2026-04-27 | Skill promotion gate harness | `uv run cortex-bench` | 23/23 passed | `benchmarks/runs/bench_20260427T191719Z.json` | Next benchmark: memory lifecycle spec. |
| 2026-04-27 | Memory lifecycle harness | `uv run cortex-bench` | 24/24 passed | `benchmarks/runs/bench_20260427T193004Z.json` | Next benchmark: Memory Palace correction/delete flow contract. |
| 2026-04-27 | Memory Palace flow contract harness | `uv run cortex-bench` | 25/25 passed | `benchmarks/runs/bench_20260427T193310Z.json` | Next benchmark: benchmark quality gates and plan. |
| 2026-04-27 | Benchmark plan quality gate | `uv run cortex-bench` | 26/26 passed | `benchmarks/runs/bench_20260427T193429Z.json` | Next benchmark: hostile-source context-pack policy. |
| 2026-04-27 | Hostile-source context-pack policy | `uv run cortex-bench` | 27/27 passed | `benchmarks/runs/bench_20260427T193620Z.json` | Next benchmark: encrypted evidence vault boundary. |
| 2026-04-27 | Evidence vault encryption boundary | `uv run cortex-bench` | 28/28 passed | `benchmarks/runs/bench_20260427T193803Z.json` | Next benchmark: local operation latency. |
| 2026-04-27 | Local memory operation latency | `uv run cortex-bench` | 29/29 passed | `benchmarks/runs/bench_20260427T193918Z.json` | Next benchmark: deletion-aware memory export. |
| 2026-04-27 | Deletion-aware memory export | `uv run cortex-bench` | 30/30 passed | `benchmarks/runs/bench_20260427T194138Z.json` | Next benchmark: failed skill rollback. |
| 2026-04-27 | Failed skill rollback | `uv run cortex-bench` | 31/31 passed | `benchmarks/runs/bench_20260427T194315Z.json` | Next benchmark: export audit events. |
| 2026-04-27 | Export audit events | `uv run cortex-bench` | 32/32 passed | `benchmarks/runs/bench_20260427T195434Z.json` | Next benchmark: skill maturity audit events. |
| 2026-04-27 | Skill maturity audit events | `uv run cortex-bench` | 33/33 passed | `benchmarks/runs/bench_20260427T195603Z.json` | Next benchmark: latency history report. |
| 2026-04-27 | Latency history report | `uv run cortex-bench` | 34/34 passed | `benchmarks/runs/bench_20260427T195752Z.json` | Next benchmark: gateway memory export. |
| 2026-04-27 | Gateway memory export | `uv run cortex-bench` | 35/35 passed | `benchmarks/runs/bench_20260427T195901Z.json` | Next benchmark: gateway skill audit receipts. |
| 2026-04-27 | Gateway skill audit receipts | `uv run cortex-bench` | 36/36 passed | `benchmarks/runs/bench_20260427T200024Z.json` | Next benchmark: Memory Palace export UI flow. |
| 2026-04-27 | Memory Palace export UI flow | `uv run cortex-bench` | 37/37 passed | `benchmarks/runs/bench_20260427T200318Z.json` | Next benchmark: local latency-history command. |
| 2026-04-27 | Local latency-history command | `uv run cortex-bench` | 38/38 passed | `benchmarks/runs/bench_20260427T200508Z.json` | Next benchmark: draft-only skill execution contract. |
| 2026-04-27 | Draft-only skill execution contract | `uv run cortex-bench` | 39/39 passed | `benchmarks/runs/bench_20260427T200659Z.json` | Next benchmark: self-lesson proposal and rollback. |
| 2026-04-27 | Self-lesson proposal and rollback | `uv run cortex-bench` | 40/40 passed | `benchmarks/runs/bench_20260427T202722Z.json` | Next benchmark: context pack template registry. |
| 2026-04-27 | Context pack template registry | `uv run cortex-bench` | 41/41 passed | `benchmarks/runs/bench_20260427T202948Z.json` | Next benchmark: gateway draft-only skill execution. |
| 2026-04-27 | Gateway draft-only skill execution | `uv run cortex-bench` | 42/42 passed | `benchmarks/runs/bench_20260427T203122Z.json` | Next benchmark: self-lesson audit receipts. |
| 2026-04-27 | Self-lesson audit receipts | `uv run cortex-bench` | 43/43 passed | `benchmarks/runs/bench_20260427T204815Z.json` | Next benchmark: context-pack self-lesson routing. |
| 2026-04-27 | Context-pack self-lesson routing | `uv run cortex-bench` | 44/44 passed | `benchmarks/runs/bench_20260427T205117Z.json` | Next benchmark: gateway self-lesson proposal. |
| 2026-04-27 | Gateway self-lesson proposal | `uv run cortex-bench` | 45/45 passed | `benchmarks/runs/bench_20260427T205349Z.json` | Next benchmark: self-lesson SQLite persistence. |
| 2026-04-27 | Self-lesson SQLite persistence | `uv run cortex-bench` | 46/46 passed | `benchmarks/runs/bench_20260427T205648Z.json` | Next benchmark: gateway self-lesson promotion and rollback. |
| 2026-04-27 | Gateway self-lesson promotion and rollback | `uv run cortex-bench` | 47/47 passed | `benchmarks/runs/bench_20260427T210238Z.json` | Next benchmark: gateway self-lesson listing. |
| 2026-04-27 | Gateway self-lesson listing | `uv run cortex-bench` | 48/48 passed | `benchmarks/runs/bench_20260427T210534Z.json` | Next benchmark: gateway self-lesson explanation. |
| 2026-04-27 | Gateway self-lesson explanation | `uv run cortex-bench` | 49/49 passed | `benchmarks/runs/bench_20260427T210745Z.json` | Next benchmark: Memory Palace self-lesson flows. |
| 2026-04-27 | Memory Palace self-lesson flows | `uv run cortex-bench` | 50/50 passed | `benchmarks/runs/bench_20260427T235840Z.json` | Next benchmark: gateway self-lesson correction. |
| 2026-04-27 | Gateway self-lesson correction | `uv run cortex-bench` | 51/51 passed | `benchmarks/runs/bench_20260428T000434Z.json` | Next benchmark: gateway self-lesson deletion/revocation. |
| 2026-04-27 | Gateway self-lesson deletion | `uv run cortex-bench` | 52/52 passed | `benchmarks/runs/bench_20260428T000737Z.json` | Next benchmark: self-lesson audit listing. |
| 2026-04-27 | Self-lesson audit listing | `uv run cortex-bench` | 53/53 passed | `benchmarks/runs/bench_20260428T000935Z.json` | Next benchmark: context-pack audit metadata lane. |
| 2026-04-28 | Context-pack audit metadata lane | `uv run cortex-bench` | 54/54 passed | `benchmarks/runs/bench_20260428T001321Z.json` | Next benchmark: scoped self-lesson recall. |
| 2026-04-28 | Scoped self-lesson recall | `uv run cortex-bench` | 55/55 passed | `benchmarks/runs/bench_20260428T001851Z.json` | Next benchmark: gateway scoped self-lesson proposals. |
| 2026-04-28 | Gateway scoped self-lesson proposals | `uv run cortex-bench` | 56/56 passed | `benchmarks/runs/bench_20260428T002115Z.json` | Next benchmark: self-lesson scope inspection metadata. |
| 2026-04-28 | Self-lesson scope inspection metadata | `uv run cortex-bench` | 57/57 passed | `benchmarks/runs/bench_20260428T002426Z.json` | Next benchmark: self-lesson scope-preserving correction. |
| 2026-04-28 | Self-lesson scope-preserving correction | `uv run cortex-bench` | 58/58 passed | `benchmarks/runs/bench_20260428T002758Z.json` | Next benchmark: self-lesson audit scope metadata. |
| 2026-04-28 | Self-lesson audit scope metadata | `uv run cortex-bench` | 59/59 passed | `benchmarks/runs/bench_20260428T003052Z.json` | Next benchmark: scoped self-lesson exclusion metadata. |
| 2026-04-28 | Scoped self-lesson exclusion metadata | `uv run cortex-bench` | 60/60 passed | `benchmarks/runs/bench_20260428T143557Z.json` | Next benchmark: self-lesson scoped export/review metadata. |
| 2026-04-28 | Self-lesson scoped export/review metadata | `uv run cortex-bench` | 61/61 passed | `benchmarks/runs/bench_20260428T144142Z.json` | Next benchmark: stale scoped self-lesson review. |
| 2026-04-28 | Stale scoped self-lesson review | `uv run cortex-bench` | 62/62 passed | `benchmarks/runs/bench_20260428T144541Z.json` | Next benchmark: scoped self-lesson refresh with audit. |
| 2026-04-28 | Scoped self-lesson refresh with audit | `uv run cortex-bench` | 63/63 passed | `benchmarks/runs/bench_20260428T204624Z.json` | Next benchmark: stale scoped self-lesson export markers. |
| 2026-04-28 | Stale scoped self-lesson export markers | `uv run cortex-bench` | 64/64 passed | `benchmarks/runs/bench_20260428T211628Z.json` | Next benchmark: redacted self-lesson review queue. |
| 2026-04-28 | Redacted self-lesson review queue | `uv run cortex-bench` | 65/65 passed | `benchmarks/runs/bench_20260428T211908Z.json` | Next benchmark: context-pack review-required summary. |
| 2026-04-28 | Context-pack review-required self-lesson summary | `uv run cortex-bench` | 66/66 passed | `benchmarks/runs/bench_20260428T212220Z.json` | Next benchmark: Memory Palace self-lesson review flow. |
| 2026-04-28 | Memory Palace self-lesson review action flow | `uv run cortex-bench` | 67/67 passed | `benchmarks/runs/bench_20260428T214630Z.json` | Next benchmark: gateway review queue action plans. |
| 2026-04-28 | Gateway review queue action plans | `uv run cortex-bench` | 68/68 passed | `benchmarks/runs/bench_20260428T214833Z.json` | Next benchmark: anchored gateway review flow. |
| 2026-04-28 | Anchored gateway self-lesson review flow | `uv run cortex-bench` | 69/69 passed | `benchmarks/runs/bench_20260428T215042Z.json` | Next benchmark: context-pack review flow hints. |
| 2026-04-28 | Context-pack review flow routing hints | `uv run cortex-bench` | 70/70 passed | `benchmarks/runs/bench_20260428T215505Z.json` | Next benchmark: review flow safety summary. |
| 2026-04-28 | Review flow safety summary | `uv run cortex-bench` | 71/71 passed | `benchmarks/runs/bench_20260428T215719Z.json` | Next benchmark: review flow audit preview. |
| 2026-04-29 | Review flow audit preview | `uv run cortex-bench` | 72/72 passed | `benchmarks/runs/bench_20260429T013605Z.json` | Next benchmark: review flow audit consistency. |
| 2026-04-29 | Review flow audit consistency | `uv run cortex-bench` | 73/73 passed | `benchmarks/runs/bench_20260429T013806Z.json` | Next benchmark: context-pack review flow audit hint. |
| 2026-04-29 | Context-pack review flow audit hint | `uv run cortex-bench` | 74/74 passed | `benchmarks/runs/bench_20260429T013949Z.json` | Next benchmark: review queue audit preview hint. |
| 2026-04-29 | Review queue audit preview hint | `uv run cortex-bench` | 75/75 passed | `benchmarks/runs/bench_20260429T015037Z.json` | Next benchmark: review queue audit consistency. |
| 2026-04-29 | Review queue audit consistency | `uv run cortex-bench` | 76/76 passed | `benchmarks/runs/bench_20260429T015355Z.json` | Next benchmark: review queue safety summary. |
| 2026-04-29 | Review queue safety summary | `uv run cortex-bench` | 77/77 passed | `benchmarks/runs/bench_20260429T015618Z.json` | Next benchmark: empty review queue safety summary. |
| 2026-04-29 | Empty review queue safety summary | `uv run cortex-bench` | 78/78 passed | `benchmarks/runs/bench_20260429T015802Z.json` | Next benchmark: review queue limit safety. |
| 2026-04-29 | Review queue limit safety | `uv run cortex-bench` | 79/79 passed | `benchmarks/runs/bench_20260429T020001Z.json` | Next benchmark: review queue ordering. |
| 2026-04-29 | Review queue deterministic ordering | `uv run cortex-bench` | 80/80 passed | `benchmarks/runs/bench_20260429T020437Z.json` | Next benchmark: review queue paging cursor. |
| 2026-04-29 | Review queue paging cursor | `uv run cortex-bench` | 81/81 passed | `benchmarks/runs/bench_20260429T020720Z.json` | Next benchmark: invalid cursor handling. |
| 2026-04-29 | Review queue invalid cursor handling | `uv run cortex-bench` | 82/82 passed | `benchmarks/runs/bench_20260429T020924Z.json` | Next benchmark: exhausted cursor empty page. |
| 2026-04-29 | Review queue exhausted cursor | `uv run cortex-bench` | 83/83 passed | `benchmarks/runs/bench_20260429T021418Z.json` | Next benchmark: cursor stability metadata. |
| 2026-04-29 | Review queue cursor metadata stability | `uv run cortex-bench` | 84/84 passed | `benchmarks/runs/bench_20260429T021711Z.json` | Next benchmark: cursor drift inspection. |
| 2026-04-29 | Review queue cursor drift inspection | `uv run cortex-bench` | 85/85 passed | `benchmarks/runs/bench_20260429T022020Z.json` | Next benchmark: cursor drift refresh hint. |
| 2026-04-29 | Review queue cursor refresh hint | `uv run cortex-bench` | 86/86 passed | `benchmarks/runs/bench_20260429T022254Z.json` | Next benchmark: cursor limit-change inspection. |
| 2026-04-29 | Review queue cursor limit-change inspection | `uv run cortex-bench` | 87/87 passed | `benchmarks/runs/bench_20260429T022808Z.json` | Next benchmark: empty queue signature metadata. |
| 2026-04-29 | Review queue empty cursor signature metadata | `uv run cortex-bench` | 88/88 passed | `benchmarks/runs/bench_20260429T023048Z.json` | Next benchmark: non-empty queue signature metadata. |
| 2026-04-29 | Review queue non-empty cursor signature metadata | `uv run cortex-bench` | 89/89 passed | `benchmarks/runs/bench_20260429T023303Z.json` | Next benchmark: limit-independent queue signature. |
| 2026-04-29 | Review queue limit-independent cursor signature | `uv run cortex-bench` | 90/90 passed | `benchmarks/runs/bench_20260429T023541Z.json` | Next benchmark: order-sensitive queue signature. |
| 2026-04-29 | Review queue order-sensitive cursor signature | `uv run cortex-bench` | 91/91 passed | `benchmarks/runs/bench_20260429T023919Z.json` | Next benchmark: non-review signature stability. |
| 2026-04-29 | Review queue non-review cursor signature stability | `uv run cortex-bench` | 92/92 passed | `benchmarks/runs/bench_20260429T024153Z.json` | Next benchmark: membership-sensitive queue signature. |
| 2026-04-29 | Review queue membership-sensitive cursor signature | `uv run cortex-bench` | 93/93 passed | `benchmarks/runs/bench_20260429T024403Z.json` | Next benchmark: content-independent queue signature. |
| 2026-04-29 | Review queue content-independent cursor signature | `uv run cortex-bench` | 94/94 passed | `benchmarks/runs/bench_20260429T024912Z.json` | Next benchmark: original-goal product coverage. |
| 2026-04-29 | Original-goal product coverage | `uv run cortex-bench` | 95/95 passed | `benchmarks/runs/bench_20260429T025140Z.json` | Next benchmark: product traceability report. |
| 2026-04-29 | Product traceability report | `uv run cortex-bench` | 96/96 passed | `benchmarks/runs/bench_20260429T025344Z.json` | Next benchmark: perception event envelope. |
| 2026-04-29 | Perception event envelope | `uv run cortex-bench` | 97/97 passed | `benchmarks/runs/bench_20260429T025631Z.json` | Next benchmark: perception-to-firewall handoff. |
| 2026-04-29 | Perception-to-firewall handoff | `uv run cortex-bench` | 98/98 passed | `benchmarks/runs/bench_20260429T025935Z.json` | Next benchmark: evidence eligibility handoff. |
| 2026-04-29 | Optional OpenAI live smoke | `uv run cortex-bench` plus `uv run cortex-openai-smoke --assert-contains CORTEX_LIVE_OK` | 99/99 passed; live smoke passed with 47 total tokens | `benchmarks/runs/bench_20260429T030458Z.json` | Next benchmark: evidence eligibility handoff. |
| 2026-04-29 | Evidence eligibility handoff | `uv run cortex-bench` | 100/100 passed | `benchmarks/runs/bench_20260429T031215Z.json` | Next benchmark: Shadow Pointer controls. |
| 2026-04-29 | Shadow Pointer controls | `uv run cortex-bench` | 101/101 passed | `benchmarks/runs/bench_20260429T031953Z.json` | Next benchmark: Memory Palace dashboard. |
| 2026-04-29 | Frontier AI lab research synthesis | `uv run cortex-bench` plus `uv run cortex-openai-smoke --assert-contains CORTEX_LIVE_OK` | 102/102 passed; live smoke passed with 47 total tokens | `benchmarks/runs/bench_20260429T033138Z.json` | Next benchmark: agent runtime trace. |
| 2026-04-29 | Memory Palace dashboard contract | `uv run cortex-bench` | 103/103 passed | `benchmarks/runs/bench_20260429T033914Z.json` | Next benchmark: agent runtime trace. |
| 2026-04-29 | Agent runtime trace contract | `uv run cortex-bench` | 104/104 passed | `benchmarks/runs/bench_20260429T034825Z.json` | Next benchmark: budgeted context packs. |
| 2026-04-29 | Budgeted context-pack contract | `uv run cortex-bench` | 105/105 passed | `benchmarks/runs/bench_20260429T035544Z.json` | Next benchmark: untrusted pointing proposal. |
| 2026-04-29 | Untrusted Shadow Pointer pointing proposal | `uv run cortex-bench` | 106/106 passed | `benchmarks/runs/bench_20260429T040200Z.json` | Next benchmark: document-to-skill candidate derivation. |
| 2026-04-29 | Document-to-skill candidate derivation | `uv run cortex-bench` | 107/107 passed | `benchmarks/runs/bench_20260429T040704Z.json` | Next benchmark: swarm governance. |
| 2026-04-29 | Swarm governance contract | `uv run cortex-bench` | 108/108 passed | `benchmarks/runs/bench_20260429T041354Z.json` | Next benchmark: robot spatial safety metadata. |
| 2026-04-29 | Robot spatial safety metadata | `uv run cortex-bench` | 109/109 passed | `benchmarks/runs/bench_20260429T041908Z.json` | Next benchmark: Skill Forge candidate list. |
| 2026-04-29 | Skill Forge candidate list | `uv run cortex-bench` | 110/110 passed | `benchmarks/runs/bench_20260429T042542Z.json` | Next benchmark: Cortex Codex plugin skeleton. |
| 2026-04-29 | Cortex Codex plugin skeleton | `uv run cortex-bench` | 111/111 passed | `benchmarks/runs/bench_20260429T043529Z.json` | Next benchmark: browser and terminal adapter contracts. |
| 2026-04-29 | Browser and terminal adapter contracts | `uv run cortex-bench` | 112/112 passed | `benchmarks/runs/bench_20260429T044142Z.json` | Next benchmark: Cortex plugin install/discovery smoke. |
| 2026-04-29 | Cortex plugin install/discovery smoke | `uv run cortex-bench` plus `uv run cortex-plugin-install-smoke` | 113/113 passed; install smoke passed | `benchmarks/runs/bench_20260429T044921Z.json` | Next benchmark: native Shadow Pointer overlay proof. |
| 2026-04-29 | Native Shadow Pointer overlay proof | `uv run cortex-bench` plus SwiftPM build/test/smoke | 114/114 passed; SwiftPM build passed; SwiftPM tests passed with 5 tests; smoke returned `passed: true` | `benchmarks/runs/bench_20260429T045856Z.json` | Next benchmark: live browser and terminal adapters. |
| 2026-04-29 | Live browser and terminal adapter artifact smoke | `uv run cortex-bench` plus `uv run cortex-live-adapter-smoke --json` | 115/115 passed; live adapter smoke passed; `uv run pytest` -> 250 passed | `benchmarks/runs/bench_20260429T050513Z.json` | Next benchmark: local adapter ingest endpoint. |
| 2026-04-30 | Local adapter ingest endpoint | `uv run cortex-bench` plus `uv run cortex-adapter-endpoint --smoke --json` | 116/116 passed; endpoint smoke passed; `uv run pytest` -> 256 passed | `benchmarks/runs/bench_20260430T025058Z.json` | Next benchmark: manual browser/terminal proof against local endpoint. |
| 2026-04-30 | Manual adapter proof against local endpoint | `uv run cortex-bench` plus `uv run cortex-manual-adapter-proof --json` | 117/117 passed; manual proof passed; `uv run pytest` -> 258 passed | `benchmarks/runs/bench_20260430T034225Z.json` | Next benchmark: Memory Palace and Skill Forge UI shell. |
| 2026-04-30 | Memory Palace and Skill Forge dashboard shell | `uv run cortex-bench` plus `uv run cortex-dashboard-shell --smoke --json` and local browser desktop/mobile proof | 118/118 passed; dashboard shell smoke passed; `uv run pytest` -> 261 passed | `benchmarks/runs/bench_20260430T040549Z.json` | Next benchmark: consented macOS app/window and accessibility adapter contracts. |
| 2026-04-30 | Consented macOS app/window and Accessibility adapters | `uv run cortex-bench` plus focused adapter tests | 119/119 passed; focused adapter tests passed with 13 tests | `benchmarks/runs/bench_20260430T041616Z.json` | Next benchmark: user-approved real Codex plugin enable path. |
| 2026-04-30 | Approval-gated Codex plugin real enable path | `uv run cortex-bench` plus `uv run cortex-plugin-enable-plan --json` and focused plugin tests | 120/120 passed; dry-run enable plan passed; focused plugin tests passed with 8 tests | `benchmarks/runs/bench_20260430T042245Z.json` | Next benchmark: Shadow Pointer capture wiring. |
| 2026-04-30 | Shadow Pointer capture wiring | `uv run cortex-bench` plus focused Shadow Pointer capture tests | 121/121 passed; focused Shadow Pointer/perception tests passed with 32 tests | `benchmarks/runs/bench_20260430T042728Z.json` | Next benchmark: dashboard gateway action receipts. |
| 2026-04-30 | Dashboard gateway action receipts | `uv run cortex-bench` plus focused dashboard tests and browser proof | 122/122 passed; focused dashboard tests passed with 9 tests; browser proof allowed `memory.explain` and blocked `memory.forget` | `benchmarks/runs/bench_20260430T043406Z.json` | Next benchmark: native capture permission-status smoke. |
| 2026-04-30 | Native capture permission-status smoke | `uv run cortex-bench`, `swift run --package-path native/macos-shadow-pointer cortex-permission-smoke`, `uv run cortex-native-permission-smoke --json` | 123/123 passed; SwiftPM tests passed with 7 tests; native permission smoke returned `passed: true` | `benchmarks/runs/bench_20260430T045727Z.json` | Next benchmark: gateway runtime trace persistence. |
| 2026-04-30 | Gateway runtime trace persistence | `uv run cortex-bench` plus focused runtime/store/gateway tests | 124/124 passed; focused tests passed with 76 tests; full suite passed with 284 tests | `benchmarks/runs/bench_20260430T050337Z.json` | Next benchmark: hybrid context fusion index stub. |
| 2026-04-30 | Hybrid context fusion index stub | `uv run cortex-bench` plus focused hybrid index tests | 125/125 passed; focused tests passed with 6 tests; full suite passed with 288 tests | `benchmarks/runs/bench_20260430T050859Z.json` | Next benchmark: retrieval explanation receipts. |

## First Runnable Harness Requirements

The first benchmark runner should include synthetic fixtures for:

| Fixture | Expected result | Suite |
| --- | --- | --- |
| benign coding scene | compiles into a candidate episodic/project memory with source refs | `MEM-RECALL-001` |
| deleted memory | cannot be retrieved or included in context packs | `MEM-FORGET-001` |
| webpage prompt injection | quarantined or instruction-stripped; never active memory/skill | `SEC-INJECT-001` |
| terminal output containing fake token | redacted before durable storage | `SEC-PII-001` |
| repeated workflow | creates draft-only candidate skill, not autonomous skill | future Skill Forge bench |
| high-risk action request | requires review or is blocked | `ROBOT-SAFE-001` |

## Benchmark Entry Template

| Field | Value |
| --- | --- |
| ID |  |
| Goal |  |
| Dataset / fixtures |  |
| Command |  |
| Metrics |  |
| Acceptance gate |  |
| Last result |  |
| Notes |  |

## Minimum Benchmark Philosophy

- Every memory feature needs a normal case, an adversarial case, and a deletion/revocation case.
- Every safety benchmark needs at least one realistic attack prompt and one benign near-miss to monitor overblocking.
- Benchmark artifacts should avoid raw private memory. Use synthetic fixtures unless the user explicitly provides sanitized data.
- Keep machine-readable results under `benchmarks/runs/`; commit only sanitized summaries by default.
