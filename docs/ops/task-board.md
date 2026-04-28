# Cortex Memory OS Task Board

Last updated: 2026-04-28

## Active

| ID | Task | Owner | Proof / Evidence | Notes |
| --- | --- | --- | --- | --- |
| SELF-LESSON-SCOPE-REFRESH-001 | Refresh reviewed scoped self-lessons | Codex | Refresh/audit contract and benchmark case | Reviewed scoped lessons should re-enter context only with audit evidence. |

## Next

| ID | Task | Owner | Proof / Evidence | Notes |
| --- | --- | --- | --- | --- |
| _None_ |  |  |  |  |

## Backlog

| ID | Task | Owner | Proof / Evidence | Notes |
| --- | --- | --- | --- | --- |
| _None_ |  |  |  |  |

## Done

| ID | Task | Owner | Proof / Evidence | Notes |
| --- | --- | --- | --- | --- |
| OPS-001 | Install project engineering control plane | Codex | `AGENTS.md`, `docs/ops/*`, `docs/adr/0001-engineering-control-plane.md`, `.gitignore` | Created before product implementation. |
| INTAKE-001 | Ingest user-provided plans and skeletons | Codex | `docs/product/vision.md`, `docs/architecture/system-blueprint.md`, `docs/contracts/core-schemas.md`, `docs/product/build-roadmap.md` | Converted first-pass architecture into durable project docs. |
| SEC-001 | Draft initial threat model for agent and robot memory | Codex | `docs/security/initial-threat-model.md` | Covers injection, memory poisoning, over-capture, deletion, MCP/tool risk, self-improvement drift, and robot safety. |
| ADR-002 | Accept evidence-first memory loop | Codex | `docs/adr/0002-evidence-first-memory-loop.md` | Rejects shallow screen-summary-vector pattern. |
| RSRCH-001 | Build official-source research map | Codex | `docs/ops/research-safety.md` source ledger | Verified first-pass cited sources from official/primary pages. |
| ADR-003 | Decide first runtime shell and local service shape | Codex | `docs/adr/0003-runtime-shell-and-local-service.md` | Accepted SwiftUI/AppKit native shell plus Python local engine. |
| CONTRACT-001 | Convert core schemas into typed code and synthetic fixtures | Codex | `src/cortex_memory_os/contracts.py`, `tests/fixtures/*.json`, `uv run pytest` -> 22 passed | Python contract layer created with safety validators. |
| BENCH-002 | Build first runnable benchmark harness | Codex | `uv run cortex-bench` -> 14/14 passed, artifact under `benchmarks/runs/` | Includes recall, deletion, injection, redaction, vault retention, gateway context, Shadow Pointer, scene segmentation, memory compilation, temporal edge compilation, SQLite persistence, Skill Forge, skill maturity, and high-risk action fixtures. |
| FIREWALL-001 | Prototype privacy and prompt-injection firewall | Codex | `src/cortex_memory_os/firewall.py`, `tests/test_benchmarks.py`, `uv run pytest` -> 24 passed | External injection quarantined; fake terminal token masked before storage. |
| VAULT-001 | Prototype evidence vault skeleton | Codex | `src/cortex_memory_os/evidence_vault.py`, `uv run pytest` -> 27 passed, `uv run cortex-bench` -> 7/7 passed | SQLite metadata, checksum raw reads, raw expiry, no-op dev cipher boundary. |
| GATEWAY-001 | Prototype Cortex MCP server skeleton | Codex | `src/cortex_memory_os/mcp_server.py`, `uv run cortex-mcp --smoke`, `uv run pytest` -> 32 passed | MCP-shaped JSON-RPC handlers for tool list, memory search, and scoped context packs. |
| UI-001 | Prototype minimal Shadow Pointer states | Codex | `ui/shadow-pointer/*`, `src/cortex_memory_os/shadow_pointer.py`, `uv run pytest` -> 37 passed, browser desktop/mobile check, `uv run cortex-bench` -> 9/9 passed | Static prototype served at `http://127.0.0.1:8765/ui/shadow-pointer/index.html`. |
| MEM-002 | Prototype scene segmenter from synthetic event streams | Codex | `src/cortex_memory_os/scene_segmenter.py`, `uv run pytest` -> 40 passed, `uv run cortex-bench` -> 10/10 passed | Deterministic project/time/topic/app segmentation seam. |
| MEM-003 | Prototype memory compiler from scenes | Codex | `src/cortex_memory_os/memory_compiler.py`, `uv run pytest` -> 43 passed, `uv run cortex-bench` -> 11/11 passed | Scene-derived memories are candidate, source-backed, user-visible, and low influence. |
| GRAPH-001 | Prototype temporal edge compiler from memory candidates | Codex | `src/cortex_memory_os/temporal_graph.py`, `uv run pytest` -> 45 passed, `uv run cortex-bench` -> 12/12 passed | Memory-derived graph edges preserve validity, confidence, status, and source refs. |
| STORE-001 | Persist memory records and temporal edges in SQLite | Codex | `src/cortex_memory_os/sqlite_store.py`, `uv run pytest` -> 49 passed, `uv run cortex-bench` -> 13/13 passed | SQLite store round-trips typed contracts and persists deletion tombstones. |
| SKILL-002 | Prototype Skill Forge pattern detector | Codex | `src/cortex_memory_os/skill_forge.py`, `uv run pytest` -> 52 passed, `uv run cortex-bench` -> 14/14 passed | Three repeated scenes produce draft-only candidate skill. |
| PALACE-002 | Prototype Memory Palace correction/delete service | Codex | `src/cortex_memory_os/memory_palace.py`, `uv run pytest` -> 56 passed, `uv run cortex-bench` -> 15/15 passed | Explain returns source refs/influence limits; correction supersedes old memory; deletion blocks recall. |
| AUDIT-001 | Persist audit events for memory corrections/deletions | Codex | `src/cortex_memory_os/sqlite_store.py`, `src/cortex_memory_os/memory_palace.py`, `uv run pytest` -> 57 passed, `uv run cortex-bench` -> 16/16 passed | Mutation audits are human-visible, persisted, target-queryable, and summary-redacted. |
| GATEWAY-002 | Expose Memory Palace correction/delete through gateway tools | Codex | `src/cortex_memory_os/mcp_server.py`, `uv run pytest` -> 59 passed, `uv run cortex-mcp --smoke`, `uv run cortex-bench` -> 17/17 passed | Gateway tools require explicit memory IDs and return audit events. |
| RETRIEVAL-001 | Add retrieval scoring object with trust, recency, status, and privacy penalties | Codex | `src/cortex_memory_os/retrieval.py`, `uv run pytest` focused -> 18 passed, `uv run cortex-bench` -> 18/18 passed | Store search now uses shared deterministic ranking before future graph/vector fusion. |
| POLICY-001 | Add scope-aware retrieval filters for project, agent, and session boundaries | Codex | `src/cortex_memory_os/retrieval.py`, `uv run pytest` focused -> 15 passed, `uv run cortex-bench` -> 19/19 passed | Retrieval scope blocks mismatched project, agent, and session-scoped memories. |
| CONTEXT-002 | Route context-pack compilation through scored retrieval | Codex | `src/cortex_memory_os/mcp_server.py`, `src/cortex_memory_os/contracts.py`, `uv run pytest` focused -> 37 passed, `uv run cortex-bench` -> 20/20 passed | Context packs include compact score summaries aligned with relevant memories. |
| SEC-002 | Define secret, PII, and local-data handling policy | Codex | `docs/security/secret-pii-local-data-policy.md`, `src/cortex_memory_os/sensitive_data_policy.py`, `uv run pytest` focused -> 28 passed, `uv run cortex-bench` -> 21/21 passed | Firewall decisions carry policy refs; `.gitignore` covers required local secret/data patterns. |
| DBG-001 | Decide logging and trace format for development | Codex | `src/cortex_memory_os/debug_trace.py`, `docs/ops/debug-journal.md`, `uv run pytest` focused -> 9 passed, `uv run cortex-bench` -> 22/22 passed | Structured debug traces redact secret-like text and preserve sanitized reproduction refs. |
| SKILL-001 | Specify Skill Forge maturity and approval gates in code-facing detail | Codex | `docs/architecture/skill-forge-lifecycle.md`, `src/cortex_memory_os/skill_policy.py`, `uv run pytest` focused -> 9 passed, `uv run cortex-bench` -> 23/23 passed | Promotion gate prevents autonomy jumps and requires approval plus success evidence. |
| MEM-001 | Define first memory primitives and lifecycle states | Codex | `docs/architecture/memory-lifecycle.md`, `src/cortex_memory_os/memory_lifecycle.py`, `uv run pytest` focused -> 17 passed, `uv run cortex-bench` -> 24/24 passed | Lifecycle policy gates activation, deletion, revocation, quarantine, supersession, and recall eligibility. |
| PALACE-001 | Specify Memory Palace correction/delete flows | Codex | `docs/product/memory-palace-flows.md`, `src/cortex_memory_os/memory_palace_flows.py`, `uv run pytest` focused -> 17 passed, `uv run cortex-bench` -> 25/25 passed | User questions like "why did you think that?" and "delete that." now map to explicit explain/delete contracts. |
| BENCH-001 | Create first benchmark harness plan | Codex | `docs/ops/benchmark-plan.md`, `README.md`, `docs/ops/README.md`, `uv run pytest tests/test_benchmarks.py` -> 2 passed, `uv run cortex-bench` -> 26/26 passed | Benchmark plan defines runnable commands, release blockers, artifact policy, and expansion roadmap. |
| CTX-003 | Specify hostile-source context-pack rules | Codex | `docs/security/hostile-context-pack-policy.md`, `src/cortex_memory_os/context_policy.py`, `uv run pytest` focused -> 10 passed, `uv run cortex-bench` -> 27/27 passed | External evidence is cited in a separate lane and never returned as trusted memory or instructions. |
| VAULT-002 | Specify encrypted evidence vault boundary | Codex | `docs/security/evidence-vault-encryption-boundary.md`, `src/cortex_memory_os/evidence_vault.py`, `uv run pytest` focused -> 7 passed, `uv run cortex-bench` -> 28/28 passed | Production vault mode rejects `noop-dev` and requires an authenticated cipher boundary. |
| PERF-001 | Add local memory operation latency benchmark | Codex | `src/cortex_memory_os/benchmarks.py`, `docs/ops/benchmark-plan.md`, `uv run pytest tests/test_benchmarks.py` -> 2 passed, `uv run cortex-bench` -> 29/29 passed | Synthetic SQLite memory write/search p95 latencies are tracked under `PERF-LAT-001`. |
| EXPORT-001 | Specify user memory export and deletion-aware archive | Codex | `docs/product/memory-export.md`, `src/cortex_memory_os/memory_export.py`, `uv run pytest` focused -> 5 passed, `uv run cortex-bench` -> 30/30 passed | Export includes scoped recall-allowed memories, omits deleted content, and redacts secret-like text. |
| SKILL-ROLLBACK-001 | Specify failed skill rollback path | Codex | `docs/architecture/skill-forge-lifecycle.md`, `src/cortex_memory_os/skill_policy.py`, `uv run pytest` focused -> 8 passed, `uv run cortex-bench` -> 31/31 passed | Failed skills can roll back to lower maturity without expanding permissions. |
| EXPORT-AUDIT-001 | Persist audit events for memory exports | Codex | `src/cortex_memory_os/memory_export.py`, `docs/product/memory-export.md`, `uv run pytest` focused -> 6 passed, `uv run cortex-bench` -> 32/32 passed | Export audits are persisted human-visible receipts and do not copy exported content. |
| SKILL-AUDIT-001 | Persist audit events for skill promotion and rollback | Codex | `src/cortex_memory_os/skill_audit.py`, `docs/architecture/skill-forge-lifecycle.md`, `uv run pytest` focused -> 10 passed, `uv run cortex-bench` -> 33/33 passed | Skill maturity decisions persist human-visible audit receipts without copying skill procedure text. |
| PERF-HISTORY-001 | Track benchmark latency history across runs | Codex | `src/cortex_memory_os/benchmark_history.py`, `docs/ops/performance-history.md`, `uv run pytest` focused -> 4 passed, `uv run cortex-bench` -> 34/34 passed | Latency history parser compares benchmark artifacts and flags large p95 regressions. |
| GATEWAY-EXPORT-001 | Expose memory export through gateway tool | Codex | `src/cortex_memory_os/mcp_server.py`, `uv run pytest` focused -> 11 passed, `uv run cortex-bench` -> 35/35 passed | Gateway export is exact-memory-ID scoped and returns a redacted audit receipt. |
| GATEWAY-SKILL-AUDIT-001 | Expose skill audit receipts through gateway tools | Codex | `src/cortex_memory_os/mcp_server.py`, `src/cortex_memory_os/skill_audit.py`, `uv run pytest` focused -> 15 passed, `uv run cortex-bench` -> 36/36 passed | Gateway skill audit receipts are structured and never accept or return procedure text. |
| PALACE-EXPORT-UI-001 | Specify Memory Palace export UI flow | Codex | `docs/product/memory-palace-flows.md`, `docs/product/memory-export.md`, `uv run pytest` focused -> 6 passed, `uv run cortex-bench` -> 37/37 passed | Export is explicit, scoped, confirmation-gated, data-egress marked, and audit-backed. |
| GATEWAY-HISTORY-001 | Expose benchmark latency history through local ops command | Codex | `src/cortex_memory_os/benchmark_history.py`, `pyproject.toml`, `uv run cortex-bench-history --format json`, `uv run cortex-bench` -> 38/38 passed | Local latency-history command renders sanitized Markdown/JSON and can fail on regressions. |
| SKILL-EXECUTION-001 | Specify draft-only skill execution result contract | Codex | `src/cortex_memory_os/skill_execution.py`, `docs/architecture/skill-forge-lifecycle.md`, `uv run pytest` focused -> 11 passed, `uv run cortex-bench` -> 39/39 passed | Draft-only execution returns review-required outputs and blocks external effects. |
| SELF-LESSON-001 | Specify self-lesson proposal and rollback contract | Codex | `src/cortex_memory_os/self_lessons.py`, `docs/architecture/self-improvement-engine.md`, `uv run pytest` focused -> 7 passed, `uv run cortex-bench` -> 40/40 passed | Self-lessons can update methods only, require confirmation, reject hostile/permission changes, and roll back to revoked. |
| CONTEXT-TEMPLATE-001 | Specify context pack template registry | Codex | `src/cortex_memory_os/context_templates.py`, `docs/architecture/context-pack-templates.md`, `uv run pytest` focused -> 17 passed, `uv run cortex-bench` -> 41/41 passed | Templates select compact coding/research/general lanes without widening retrieval scope. |
| GATEWAY-SKILL-EXECUTION-001 | Expose draft-only skill execution through gateway tool | Codex | `src/cortex_memory_os/mcp_server.py`, `docs/architecture/skill-forge-lifecycle.md`, `uv run pytest` focused -> 18 passed, `uv run cortex-bench` -> 42/42 passed | Gateway returns reviewable draft outputs and blocks requested external effects. |
| SELF-LESSON-AUDIT-001 | Persist self-lesson promotion and rollback audit receipts | Codex | `src/cortex_memory_os/self_lesson_audit.py`, `uv run pytest` -> 122 passed, `uv run cortex-bench` -> 43/43 passed | Audit receipts contain reason codes and policy refs, not lesson content. |
| CONTEXT-PACK-SELF-LESSON-001 | Route active self-lessons into context packs through templates | Codex | `src/cortex_memory_os/context_templates.py`, `src/cortex_memory_os/mcp_server.py`, `uv run pytest` -> 124 passed, `uv run cortex-bench` -> 44/44 passed | Active lessons use the template self-lesson lane; revoked lessons are excluded. |
| GATEWAY-SELF-LESSON-001 | Expose self-lesson proposal through gateway tool | Codex | `src/cortex_memory_os/mcp_server.py`, `uv run pytest` -> 126 passed, `uv run cortex-bench` -> 45/45 passed | Gateway proposals create candidate lessons only and reject hostile or permission-expanding text. |
| SELF-LESSON-STORE-001 | Persist candidate and active self-lessons in SQLite | Codex | `src/cortex_memory_os/sqlite_store.py`, `src/cortex_memory_os/mcp_server.py`, `uv run pytest` -> 129 passed, `uv run cortex-bench` -> 46/46 passed | Gateway proposals persist as candidates; context packs use active persisted lessons only. |
| GATEWAY-SELF-LESSON-PROMOTE-001 | Promote and roll back self-lessons through gateway with audit receipts | Codex | `src/cortex_memory_os/mcp_server.py`, `uv run pytest` -> 132 passed, `uv run cortex-bench` -> 47/47 passed | Promotion requires confirmation; rollback revokes active lessons and removes them from context. |
| GATEWAY-SELF-LESSON-LIST-001 | List self-lessons through gateway for inspectable Memory Palace flows | Codex | `src/cortex_memory_os/mcp_server.py`, `uv run pytest` -> 133 passed, `uv run cortex-bench` -> 48/48 passed | Listing preserves status filters and marks context eligibility without activating candidates. |
| GATEWAY-SELF-LESSON-EXPLAIN-001 | Explain self-lessons through gateway with source refs and audit receipts | Codex | `src/cortex_memory_os/mcp_server.py`, `uv run pytest` -> 134 passed, `uv run cortex-bench` -> 49/49 passed | Explanation is inspectable and does not promote candidate guidance into context. |
| PALACE-SELF-LESSON-FLOWS-001 | Specify Memory Palace self-lesson review and correction flows | Codex | `src/cortex_memory_os/memory_palace_flows.py`, `uv run pytest` -> 136 passed, `uv run cortex-bench` -> 50/50 passed | Candidate, active, and revoked self-lessons have safe visible review actions. |
| GATEWAY-SELF-LESSON-CORRECT-001 | Correct self-lessons through gateway with candidate replacement and audit receipt | Codex | `src/cortex_memory_os/mcp_server.py`, `uv run pytest` -> 139 passed, `uv run cortex-bench` -> 51/51 passed | Correction supersedes the old lesson and keeps replacement guidance candidate-only. |
| GATEWAY-SELF-LESSON-DELETE-001 | Delete or revoke self-lessons through gateway with audit receipt | Codex | `src/cortex_memory_os/mcp_server.py`, `uv run pytest` -> 141 passed, `uv run cortex-bench` -> 52/52 passed | Deletion requires confirmation and excludes deleted lessons from context packs. |
| SELF-LESSON-AUDIT-LIST-001 | List self-lesson audit receipts through gateway without exposing lesson content | Codex | `src/cortex_memory_os/mcp_server.py`, `uv run pytest` -> 142 passed, `uv run cortex-bench` -> 53/53 passed | Audit listing preserves redacted receipts without copying lesson text. |
| CONTEXT-PACK-AUDIT-LANE-001 | Add context-pack audit metadata lane without treating audit text as instructions | Codex | `uv run pytest` -> 143 passed, `uv run cortex-bench` -> 54/54 passed, `uv run cortex-mcp --smoke` | Audit metadata enters context packs without audit summaries or instruction text. |
| SELF-LESSON-RECALL-SCOPE-001 | Add scoped self-lesson recall boundaries | Codex | `uv run pytest` -> 147 passed, `uv run cortex-bench` -> 55/55 passed, `uv run cortex-mcp --smoke` | Project, agent, and session self-lessons do not cross context-pack boundaries. |
| GATEWAY-SELF-LESSON-SCOPE-PROPOSE-001 | Add scoped self-lesson proposal gateway checks | Codex | `uv run pytest` -> 148 passed, `uv run cortex-bench` -> 56/56 passed, `uv run cortex-mcp --smoke` | Scoped candidate lessons need matching provenance tags, redacted rejection errors, and no context activation. |
| SELF-LESSON-SCOPE-INSPECTION-001 | Add self-lesson scope inspection metadata | Codex | `uv run pytest` -> 149 passed, `uv run cortex-bench` -> 57/57 passed, `uv run cortex-mcp --smoke` | List/explain surfaces distinguish global eligibility from scope-required lessons. |
| SELF-LESSON-SCOPE-CORRECTION-001 | Preserve scope during self-lesson correction | Codex | `uv run pytest` -> 151 passed, `uv run cortex-bench` -> 58/58 passed, `uv run cortex-mcp --smoke` | Candidate replacements keep scoped provenance and stay out of context until promotion. |
| SELF-LESSON-SCOPE-AUDIT-001 | Add self-lesson audit scope metadata | Codex | `uv run pytest` -> 152 passed, `uv run cortex-bench` -> 59/59 passed, `uv run cortex-mcp --smoke` | Audit listings expose scope metadata without copying lesson content or provenance. |
| CONTEXT-PACK-SELF-LESSON-EXCLUSION-001 | Explain scoped self-lesson exclusions | Codex | `uv run pytest` -> 152 passed, `uv run cortex-bench` -> 60/60 passed, `uv run cortex-mcp --smoke` | Context packs explain scoped self-lesson exclusions without exposing lesson content. |
| SELF-LESSON-SCOPE-EXPORT-001 | Preserve scope in self-lesson export/review | Codex | `uv run pytest` -> 153 passed, `uv run cortex-bench` -> 61/61 passed, `uv run cortex-mcp --smoke` | Review/export surfaces preserve scope metadata without hidden content by default. |
| SELF-LESSON-SCOPE-RETENTION-001 | Review stale scoped self-lessons | Codex | `uv run pytest` -> 154 passed, `uv run cortex-bench` -> 62/62 passed, `uv run cortex-mcp --smoke` | Stale scoped lessons surface for review before future context use. |

## Dropped

| ID | Task | Owner | Reason | Notes |
| --- | --- | --- | --- | --- |
| _None_ |  |  |  |  |

## Task Template

| ID | Task | Owner | Proof / Evidence | Notes |
| --- | --- | --- | --- | --- |
| AREA-000 | Verb-first task title | Person/agent | Command, file, benchmark, or review proof | Constraints and follow-ups. |
