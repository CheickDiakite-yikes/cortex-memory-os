# Self-Improvement Engine

Last updated: 2026-04-27

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
