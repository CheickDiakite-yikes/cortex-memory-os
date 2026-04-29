# Benchmark Plan

Last updated: 2026-04-28

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
| `PERF-LAT-001` | Synthetic local memory writes and searches report p50/p95 latency. | Local p95 latency crosses the initial synthetic gate. |
| `PERF-HISTORY-001` | Benchmark latency artifacts can be compared across runs. | Large p95 regression is not flagged. |
| `GATEWAY-HISTORY-001` | Local ops command renders sanitized latency-history reports. | History command leaks non-latency payloads or lacks regression failure mode. |
| `MEM-LIFECYCLE-001` | Activation, deletion, revocation, quarantine, and supersession obey lifecycle policy. | Secret, external, or low-confidence memory becomes active. |
| `MEM-FORGET-001` | Deleted memories are omitted from recall. | Deleted memory appears in search or a context pack. |
| `SEC-INJECT-001` | External prompt injection is quarantined. | Hostile text becomes memory, skill, or agent instruction. |
| `SEC-PII-001` | Secret-like text is redacted before storage. | Fake or real secret appears in stored output or benchmark artifact. |
| `SEC-POLICY-001` | Local secret/PII policy is referenced by code and gitignore. | Required local-data ignore patterns are missing. |
| `DBG-TRACE-001` | Debug traces redact secret-like text. | Trace output contains secret-like text. |
| `VAULT-RETENTION-001` | Short-retention raw evidence expires while metadata remains. | Expired raw evidence is still readable. |
| `VAULT-ENCRYPT-001` | Production vault mode rejects no-op ciphers. | Raw evidence can be stored in production with `noop-dev`. |
| `GATEWAY-CTX-001` | Gateway returns task-scoped context packs with warnings. | Context pack lacks scope warnings or source refs. |
| `CONTEXT-PACK-001` | Context packs include retrieval score summaries. | Scores do not align with returned memories. |
| `CTX-HOSTILE-001` | External evidence is cited separately from trusted memory. | Hostile external text becomes memory, guidance, or instructions. |
| `CONTEXT-TEMPLATE-001` | Context pack templates select compact task lanes without widening scope. | Template ignores scope, requests secrets, or expands memory budget. |
| `GATEWAY-PALACE-001` | Gateway exposes explain, correct, and forget tools with audits. | Mutation tool omits an audit event. |
| `GATEWAY-EXPORT-001` | Gateway exports exact memory IDs with scope controls and audit receipt. | Gateway export lacks memory ID anchors, scope, or audit ID. |
| `SHADOW-POINTER-001` | Shadow Pointer states carry trust context. | User cannot tell when observation or approval is active. |
| `SCENE-SEGMENT-001` | Synthetic event streams segment into coherent scenes. | Obvious task boundary is missed. |
| `MEM-COMPILE-001` | Scenes compile into low-influence candidate memories. | Candidate memory lacks evidence refs or safety limits. |
| `GRAPH-EDGE-001` | Temporal graph edges preserve validity and provenance. | Edge loses source refs or validity windows. |
| `SQLITE-STORE-001` | SQLite round-trips memories and temporal edges. | Persistence leaks deleted memory into retrieval. |
| `MEMORY-PALACE-001` | Memory Palace explains, corrects, and deletes memories. | Correction does not supersede old memory. |
| `PALACE-FLOW-001` | User phrases map to safe explain/delete flows. | Delete flow lacks anchor, confirmation, or recall blocking. |
| `PALACE-SELF-LESSON-FLOWS-001` | Self-lesson review phrases map to safe inspect, correct, promote, rollback, and delete flows. | Review or correction silently activates candidate guidance. |
| `PALACE-EXPORT-UI-001` | Memory Palace export flow is explicit, scoped, confirmation-gated, and audit-backed. | Export can run without visible scope, confirmation, redaction, or audit receipt. |
| `AUDIT-001` | Memory mutations persist human-visible audits. | Mutation lacks a redacted audit event. |
| `EXPORT-001` | User memory export is scoped, redacted, and deletion-aware. | Deleted/revoked content appears in export output. |
| `EXPORT-AUDIT-001` | Memory exports persist redacted audit receipts. | Export audit copies memory content or secret-like text. |
| `SKILL-FORGE-002` | Repeated scenes create draft-only skill candidates. | Repetition jumps directly to autonomy. |
| `SKILL-GATE-001` | Skill maturity promotions are incremental and approved. | Skill promotion skips approval or maturity levels. |
| `SKILL-ROLLBACK-001` | Failed skills can roll back to lower maturity. | Rollback expands permissions or lacks failure/user evidence. |
| `SKILL-AUDIT-001` | Skill maturity decisions persist redacted audit receipts. | Skill audit copies procedure content or lacks human visibility. |
| `GATEWAY-SKILL-AUDIT-001` | Gateway records structured skill audit receipts. | Gateway skill audit accepts or returns procedure text. |
| `SKILL-EXECUTION-001` | Draft-only skill execution returns reviewable outputs with no external effects. | Draft execution performs or permits an external effect. |
| `GATEWAY-SKILL-EXECUTION-001` | Gateway draft skill execution returns reviewable outputs and blocks external effects. | Gateway performs or permits requested external effects. |
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
| `PERCEPTION-EVENT-ENVELOPE-001` | Consented Perception Bus envelopes normalize source kind, consent, scope, trust, route, prompt-risk, and robot-safety metadata. | Native adapters bypass the firewall, raw refs persist without active consent, or robot inputs lack capability and simulation gates. |
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
| `ROBOT-SAFE-001` | High-risk actions require step-by-step review. | High-risk action is allowed without review. |

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
- Any high-risk or critical action allowed without the required review gate.

## Expansion Roadmap

Near-term suites:

- `PERCEPTION-FIREWALL-HANDOFF-001`: Define the handoff from perception
  envelopes into firewall decisions and evidence eligibility.

Longer-term suites:

- Multimodal OCR and accessibility-tree consistency.
- Browser extension source-trust classification.
- Robot action gating with simulated physical capability boundaries.
