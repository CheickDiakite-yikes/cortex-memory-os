# Self-Improvement Engine

Last updated: 2026-04-28

Code contract: `src/cortex_memory_os/self_lessons.py`

The Self-Improvement Engine can improve Cortex methods. It cannot silently
change user values, permissions, boundaries, scopes, or autonomy.

## Allowed Change Lanes

Self-lessons may update:

- retrieval rules;
- context templates;
- failure checklists;
- tool choice policy;
- skill procedure notes;
- safety filters.

These are method updates. They help the agent ask for better context, choose
better checks, and avoid repeated mistakes.

## Forbidden Change Lanes

Self-lessons must not:

- grant or expand permissions;
- broaden project, app, session, or agent scope;
- increase autonomy;
- disable approval gates;
- rewrite user values;
- use secrets or production credentials;
- send messages, make purchases, deploy, or delete automatically.

Prompt-injection-like content is also rejected. External content can be evidence
for a failure, but it cannot become a self-lesson instruction.

## Lifecycle

1. Propose a candidate lesson from an outcome, failure, or user correction.
2. Check that the change lane is method-only.
3. Require confidence of at least `0.75`.
4. Require user confirmation before promotion.
5. Promote only to active method guidance.
6. Roll back to `revoked` if the lesson causes noise, bad retrieval, or user
   rejection.

Rollback preserves the lesson record and evidence trail. It stops future use
without erasing why the system became more conservative.

## Audit Receipts

Self-lesson promotion and rollback decisions create human-visible audit
receipts.

The receipt may contain:

- lesson ID;
- action;
- actor;
- target status;
- allowed / denied;
- reason code;
- policy refs.

The receipt must not copy lesson content, change summaries, source task IDs, or
rollback trigger text. These receipts prove governance decisions without turning
the audit log into another memory leak.

## Persistence

Self-lessons persist separately from ordinary memories.

Candidate lessons can be stored durably after proposal, but they must not enter
context packs until promotion makes them active. Context packs read active
self-lessons only, so proposal storage cannot silently become behavior change.

## Recall Scope

Durable self-lessons can be global, project-specific, agent-specific, or
session-only. Non-global lessons must carry matching provenance tags in
`learned_from`, such as `project:cortex`, `agent:codex`, or `session:debug-42`.
Ephemeral and never-store scopes are rejected for stored self-lessons; transient
guidance should stay outside the durable self-lesson registry.

Context packs apply the same retrieval scope vocabulary used for memories, but
project-scoped self-lessons are stricter than ordinary project memories: a
missing project tag blocks recall. This prevents a debugging lesson learned in
one project, agent, or session from silently shaping another.

## Benchmark

`SELF-LESSON-001` verifies:

- proposal creates a candidate self-lesson;
- promotion requires confidence and user confirmation;
- method-only changes can become active;
- permission, boundary, autonomy, and prompt-injection changes are rejected;
- rollback revokes the lesson and records a reason reference.

`SELF-LESSON-AUDIT-001` verifies:

- promotion creates a persisted human-visible audit receipt;
- rollback creates a persisted human-visible audit receipt;
- audit receipts contain reason codes and policy refs;
- audit receipts omit lesson content, change summaries, and source task IDs.

`GATEWAY-SELF-LESSON-001` verifies:

- gateway proposal tools create candidate lessons only;
- candidate proposals still require user confirmation;
- candidate proposals are not routed into context packs as active guidance;
- hostile or permission-expanding proposal text is rejected.

`SELF-LESSON-STORE-001` verifies:

- candidate and active self-lessons round-trip through SQLite;
- gateway proposals persist as candidate lessons;
- candidate lessons stay out of context packs;
- active lessons from SQLite can enter the self-lesson context lane.

`GATEWAY-SELF-LESSON-PROMOTE-001` verifies:

- gateway promotion requires explicit confirmation;
- denied promotion creates a reason-coded audit receipt without activation;
- confirmed promotion persists an active lesson;
- rollback revokes an active lesson and removes it from context packs;
- promotion and rollback decisions persist redacted audit receipts.

`GATEWAY-SELF-LESSON-LIST-001` verifies:

- gateway listing returns candidate, active, and revoked lessons for inspection;
- status filters preserve the requested lesson lifecycle state;
- listed lessons expose whether they are context-eligible;
- candidate and revoked lessons remain inspectable without entering context packs.

`GATEWAY-SELF-LESSON-EXPLAIN-001` verifies:

- gateway explanation returns lesson status, source refs, scope, and rollback rules;
- explanations include redacted audit receipts for prior decisions;
- explanation does not copy lesson content into audit receipts;
- explaining a candidate lesson does not activate it or add it to context packs.

`GATEWAY-SELF-LESSON-CORRECT-001` verifies:

- gateway correction supersedes the old self-lesson;
- the corrected guidance is stored as a candidate replacement only;
- the replacement records the old lesson as provenance;
- correction creates a redacted audit receipt without copying lesson content;
- neither the superseded old lesson nor the candidate replacement enters context packs.

`GATEWAY-SELF-LESSON-DELETE-001` verifies:

- gateway deletion requires explicit confirmation;
- denied deletion attempts leave the lesson unchanged while recording a receipt;
- confirmed deletion marks the lesson deleted and preserves the reason reference;
- deletion creates a redacted audit receipt without copying lesson content;
- deleted self-lessons are excluded from context packs.

`SELF-LESSON-AUDIT-LIST-001` verifies:

- gateway audit listing is anchored to an exact lesson ID;
- audit listing returns redacted receipts, not lesson content;
- source task IDs and lesson text do not leak through audit summaries;
- listing receipts does not activate or restore any self-lesson in context packs.

`SELF-LESSON-RECALL-SCOPE-001` verifies:

- scoped self-lessons require matching provenance tags;
- project-scoped lessons do not appear without a matching active project;
- agent-scoped lessons do not appear for the wrong agent;
- session-scoped lessons do not appear outside the matching session.

`GATEWAY-SELF-LESSON-SCOPE-PROPOSE-001` verifies:

- gateway proposals can create scoped candidate lessons when provenance tags
  match the declared scope;
- missing scope tags are rejected before storage;
- rejection messages do not echo submitted evidence or validation payloads;
- scoped candidates do not enter context packs before promotion;
- ephemeral and never-store scopes are not exposed as durable proposal options.

`SELF-LESSON-SCOPE-INSPECTION-001` verifies:

- list and explanation surfaces expose scope eligibility metadata;
- active scoped lessons are marked as requiring a scope match instead of global
  context eligibility;
- matching context-pack requests can still retrieve the scoped active lesson.

`SELF-LESSON-SCOPE-CORRECTION-001` verifies:

- correcting a scoped self-lesson preserves the original scope on the candidate
  replacement;
- scoped provenance tags remain attached to the replacement alongside the
  `corrected_from` source reference;
- superseded old lessons and candidate replacements both stay out of context
  packs until the replacement is explicitly promoted.

`SELF-LESSON-SCOPE-AUDIT-001` verifies:

- audit listing responses expose the target lesson status, scope, and context
  eligibility metadata;
- each returned audit receipt carries the same scope/status metadata for Memory
  Palace rendering;
- audit responses do not copy lesson content or scoped provenance tags.

`CONTEXT-PACK-SELF-LESSON-EXCLUSION-001` verifies:

- context packs include redacted metadata for active self-lessons excluded by
  project, agent, or session scope;
- exclusion records carry lesson ID, scope, status, required context, and reason
  tags only;
- exclusion records do not copy lesson content or scoped provenance refs.

`SELF-LESSON-SCOPE-EXPORT-001` verifies:

- self-lesson review lists preserve status, risk, applies-to tags, scope, and
  context eligibility without returning lesson content by default;
- self-lesson exports preserve the same scope metadata while redacting content,
  learned-from refs, and rollback conditions by default;
- export audit receipts summarize counts and redactions without copying lesson
  content or scoped provenance.

`SELF-LESSON-SCOPE-RETENTION-001` verifies:

- active scoped self-lessons with missing or stale validation dates are marked
  `review_required` in review surfaces;
- stale scoped lessons are excluded from context packs until reviewed again;
- exclusion metadata names the review requirement without copying lesson content
  or scoped provenance refs.

`SELF-LESSON-SCOPE-REFRESH-001` verifies:

- refreshing a scoped self-lesson requires explicit user confirmation;
- denied and accepted refresh attempts both create redacted audit receipts;
- a confirmed refresh updates validation state so matching scoped context packs
  can use the lesson again.

`SELF-LESSON-SCOPE-STALE-EXPORT-001` verifies:

- default self-lesson exports include explicit IDs and counts for stale scoped
  lessons that require review;
- exported stale scoped lessons carry review-state and context-eligibility
  metadata;
- export markers do not reveal lesson content, learned-from refs, rollback
  conditions, or scoped provenance tags.

`GATEWAY-SELF-LESSON-REVIEW-QUEUE-001` verifies:

- the gateway exposes a dedicated redacted queue for self-lessons requiring
  review;
- current scoped lessons, global lessons, and non-review-required lessons stay
  out of the queue;
- queued items include review state and safe actions without lesson content,
  learned-from refs, rollback conditions, or scoped provenance tags.

`CONTEXT-PACK-SELF-LESSON-REVIEW-SUMMARY-001` verifies:

- context packs include aggregate counts for review-required self-lessons;
- summary metadata groups review-required lessons by reason and scope;
- summaries point agents toward the review queue tool without exposing lesson
  content, learned-from refs, or scoped provenance tags.

`CONTEXT-PACK-SELF-LESSON-REVIEW-FLOW-HINT-001` verifies:

- context-pack review summaries point aggregate review to
  `self_lesson.review_queue`;
- the same summaries point exact lesson review to `self_lesson.review_flow`;
- exact review flow hints require a lesson ID and do not expose lesson content,
  learned-from refs, or scoped provenance tags.

`SELF-LESSON-REVIEW-FLOW-SAFETY-SUMMARY-001` verifies:

- exact review flow responses summarize read-only and mutation tools separately;
- mutation tools require confirmation and allow no external effects from the
  review card itself;
- the safety summary preserves redaction boundaries for lesson content,
  learned-from refs, rollback text, and scoped provenance.

`SELF-LESSON-REVIEW-FLOW-AUDIT-PREVIEW-001` verifies:

- exact review flow responses preview mutation audit receipts before execution;
- audit previews name refresh, correction, and deletion receipt shapes without
  running the mutation tools;
- previews preserve the same no-content and no-scoped-provenance boundary as the
  review flow itself.

`SELF-LESSON-REVIEW-FLOW-AUDIT-CONSISTENCY-001` verifies:

- self-lesson mutation responses expose the same audit shape ID previewed by the
  review flow;
- refresh, correction, and deletion responses keep policy refs aligned with
  their preview entries;
- real audit responses remain redacted and do not copy lesson content or scoped
  provenance.

`CONTEXT-PACK-REVIEW-FLOW-AUDIT-HINT-001` verifies:

- context-pack review summaries tell agents that exact review flows include an
  audit preview;
- the hint points to the preview's audit shape ID without copying the preview
  or any lesson content;
- the hint keeps the exact-lesson-ID requirement visible before audit preview
  retrieval.

`GATEWAY-REVIEW-QUEUE-AUDIT-PREVIEW-001` verifies:

- review queue entries point to exact-card audit previews without embedding
  those previews;
- queue entries include the audit shape ID and exact lesson ID needed to fetch
  the review flow;
- queue-level routing stays redacted and does not copy lesson content or scoped
  provenance.

`GATEWAY-REVIEW-QUEUE-AUDIT-CONSISTENCY-001` verifies:

- review queue hints and exact review-flow audit previews use the same audit
  shape ID;
- queue hints anchor to the same lesson ID passed to the review flow;
- consistency metadata stays redacted and never embeds preview entries.

`GATEWAY-REVIEW-QUEUE-SAFETY-SUMMARY-001` verifies:

- review queues summarize read-only, mutation, confirmation-required, and
  audit-preview-hint counts before an agent or UI renders the queue;
- queue-level safety summaries keep mutation tools confirmation-gated and mark
  external effects as unavailable from the aggregate queue;
- summaries stay redacted and do not copy lesson content, learned-from refs,
  rollback text, or scoped provenance.

`GATEWAY-REVIEW-QUEUE-EMPTY-SAFETY-001` verifies:

- empty review queues still return a zeroed, redacted safety summary;
- empty summaries keep the same no-external-effects and policy boundary markers
  as non-empty queues;
- current non-review lessons do not leak through empty queue summaries.

`GATEWAY-REVIEW-QUEUE-LIMIT-SAFETY-001` verifies:

- review queues expose the applied limit, returned count, total review-required
  count, and truncation state;
- safety-summary action counts apply to the returned queue slice only;
- omitted review-required lesson content and scoped provenance stay redacted.

`GATEWAY-REVIEW-QUEUE-ORDERING-001` verifies:

- review queues sort missing validation dates first, then oldest validation
  date, then `lesson_id` ascending;
- ordering is applied before the queue limit trims returned lessons;
- queue and safety-summary ordering metadata does not expose lesson content or
  scoped provenance.

`GATEWAY-REVIEW-QUEUE-PAGING-CURSOR-001` verifies:

- limited review queues expose `has_more`, `next_cursor`, `page_start`, and
  `page_end` metadata;
- cursors encode only cursor version, ordering contract, and numeric offset;
- following a cursor returns the next ordered page without repeating lessons or
  exposing content/provenance.

`GATEWAY-REVIEW-QUEUE-INVALID-CURSOR-001` verifies:

- malformed review queue cursors fail with a fixed redacted error;
- cursor parse errors do not echo hostile cursor text or scoped provenance;
- invalid cursor text is treated as untrusted data and never as instructions.
