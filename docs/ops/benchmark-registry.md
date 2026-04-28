# Benchmark Registry

Last updated: 2026-04-28

Benchmarks should become runnable as soon as implementation begins. Until then, this registry defines what must be measurable.

## Benchmark Suites

| ID | Suite | Purpose | Primary metrics | Initial gate |
| --- | --- | --- | --- | --- |
| MEM-RECALL-001 | Controlled recall | Verify that stored memories can be retrieved under explicit user intent | precision, recall, citation/provenance accuracy, latency | TBD after first storage design |
| MEM-FORGET-001 | Deletion and revocation | Verify deleted or revoked memories are not recalled or exported | deletion success, leakage rate, audit completeness | zero known deleted-memory recall |
| SEC-INJECT-001 | Prompt-injection resistance | Ensure untrusted memory/source text cannot override policy or tool boundaries | attack success rate, refusal accuracy, false positives | zero critical policy escapes |
| SEC-PII-001 | Sensitive-data handling | Detect accidental logging, committing, or surfacing of secrets and PII | leakage count, redaction accuracy | zero committed secrets |
| PERF-LAT-001 | Memory operation latency | Track read/write/retrieval speed under realistic local loads | p50, p95, p99 latency, throughput | TBD after storage engine choice |
| ROBOT-SAFE-001 | Embodied action gating | Ensure memory-triggered physical actions require explicit capability and approval | unauthorized action rate, approval trace completeness | zero unauthorized actions |

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
