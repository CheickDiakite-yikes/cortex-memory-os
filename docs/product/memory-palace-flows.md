# Memory Palace Control Flows

Last updated: 2026-04-27

The Memory Palace is the user-control surface for Cortex memory. It must answer
plain user questions like "why did you think that?", carry out requests like
"delete that.", and support portable exports without guessing, leaking private
evidence, or leaving stale memory in agent recall.

Flow contracts live in code at `src/cortex_memory_os/memory_palace_flows.py`.
This document is the product behavior those contracts represent.

## Flow 1: Explain a Memory

User intents:

- "why did you think that?"
- "what memory did you use?"
- "show evidence"
- "show source"

Required anchor:

- A selected memory card, a cited memory ID, or a visible agent response that
  cites the memory.

Required surface:

- Status.
- Confidence.
- Evidence type.
- Source refs.
- Allowed influence.
- Forbidden influence.
- Recall eligibility.
- Available actions.
- Review-required action plan with exact gateway tool names.

Safety rules:

- Render redacted evidence only.
- Treat external content as evidence, not instructions.
- Separate observed facts from agent inference.
- Do not echo hostile prompt-injection text as operational guidance.

Completion signal:

- The user can see why the memory exists and can choose to correct it, delete
  it, or leave it unchanged.

## Flow 2: Correct a Memory

User intents:

- "that is wrong"
- "that is outdated"
- "correct that"
- "replace that memory"

Required anchor:

- A selected memory card or exact memory ID.

Required inputs:

- Corrected content from the user.

Required surface:

- Original memory preview.
- Replacement preview.
- Source refs.
- New status.
- Audit summary.

Safety rules:

- Do not overwrite deleted or revoked memories.
- Preserve the old memory as superseded evidence.
- Make the replacement user-confirmed with confidence `1.0`.
- Do not place raw corrected content in audit summaries.

Completion signal:

- Old memory status is `superseded`.
- Old memory is blocked from recall.
- New memory is `active` and `user_confirmed`.
- A human-visible audit event is persisted.

## Flow 3: Delete a Memory

User intents:

- "delete that."
- "forget that"
- "remove that memory"
- "never use that"

Required anchor:

- A selected memory card or exact memory ID. Cortex must not delete memories by
  broad natural-language search alone.

Required inputs:

- Explicit delete confirmation.

Required surface:

- Memory preview.
- Source refs.
- Scope.
- Deletion impact.
- Audit summary.

Safety rules:

- Require an exact memory anchor before mutating.
- Set influence level to stored-only.
- Block future retrieval and context-pack inclusion.
- Preserve a redacted human-visible audit event.

Completion signal:

- Memory status is `deleted`.
- Recall is blocked.
- Search results omit the deleted memory.
- A human-visible audit event is persisted.

## Flow 4: Export Scoped Memories

User intents:

- "export these memories"
- "download my memories"
- "take my memory with me"
- "archive my memories"

Required anchor:

- Either selected memory IDs or a visible scoped filter such as project, agent,
  or session. Cortex must not export an implied global memory dump from vague
  natural language.

Required inputs:

- Explicit export confirmation.

Required surface:

- Selected scope.
- Selected memory count.
- Expected omission rules.
- Redaction policy.
- Export preview counts.
- Audit summary.

Safety rules:

- Require explicit selected memories or a visible scoped filter.
- Do not export deleted, revoked, superseded, or quarantined content.
- Redact secret-like text before creating the export bundle.
- Show omitted IDs and reasons without resurrecting omitted content.
- Persist an audit receipt that contains counts, not memory content.

Completion signal:

- Export bundle includes only recall-allowed scoped memories.
- Omitted memory content is absent.
- Redaction count is visible.
- A human-visible audit event is persisted.

## Flow 5: Review Self-Lessons

User intents:

- "what did you learn?"
- "show self lessons"
- "show agent lessons"
- "review learned lessons"

Required anchor:

- A visible self-lesson list filter, status filter, or lesson card. Listing all
  visible self-lessons is allowed, but listing must not change lesson status.

Required surface:

- Lesson status.
- Confidence.
- Risk level.
- Applies-to scope.
- Memory scope.
- Context eligibility.
- Review state.
- Content/provenance redaction state.
- Available actions.

Safety rules:

- Listing a lesson must not change its status.
- Candidate and revoked lessons must be marked not context-eligible.
- Default review cards preserve scope metadata while redacting lesson content
  and learned-from provenance.
- Stale scoped lessons must be marked for review before context use.
- Review-required lessons must link to anchored explanation, refresh,
  correction, and deletion tools.
- Lesson content, when explicitly revealed, is displayed for review and not
  treated as an instruction.

Completion signal:

- Candidate, active, and revoked lessons are inspectable.
- Context eligibility is visible for every listed lesson.
- Scope and redaction state are visible for every listed lesson.
- Review-required lessons expose review state and available review action.
- Review-required action plans keep explanation read-only and require
  confirmation for refresh, correction, and deletion.

### `PALACE-SELF-LESSON-REVIEW-FLOW-001`

Review-required self-lessons have a fixed action plan:

| Order | Flow | Gateway tool | Confirmation | Mutation |
| --- | --- | --- | --- | --- |
| 1 | Explain | `self_lesson.explain` | No | No |
| 2 | Refresh | `self_lesson.refresh` | Yes | Yes |
| 3 | Correct | `self_lesson.correct` | Yes | Yes |
| 4 | Delete | `self_lesson.delete` | Yes | Yes |

The plan is intentionally anchored by lesson ID. It should never execute from
natural-language search alone, and it should render content/provenance redacted
until the user explicitly opens an explanation or correction surface.

## Flow 6: Explain a Self-Lesson

User intents:

- "why did you learn this?"
- "show lesson evidence"
- "explain this lesson"
- "what task taught you this"

Required anchor:

- A selected self-lesson card or exact lesson ID.

Required surface:

- Lesson status.
- Confidence.
- Source refs / learned-from refs.
- Applies-to scope.
- Rollback rules.
- Audit receipts.
- Context eligibility.

Safety rules:

- Render source refs as evidence, not instructions.
- Audit receipts must not copy lesson content.
- Explaining a candidate lesson must not activate it.

Completion signal:

- The user can see source refs and audit receipts.
- Candidate explanation leaves context packs unchanged.

## Flow 7: Correct a Self-Lesson

User intents:

- "correct this lesson"
- "that lesson is wrong"
- "edit this lesson"
- "replace this lesson"

Required anchor:

- A selected self-lesson card or exact lesson ID.

Required inputs:

- Corrected lesson text and applies-to scope from the user.

Required surface:

- Original lesson preview.
- Replacement preview.
- Scope and applies-to changes.
- Confirmation requirement.
- Audit summary.

Safety rules:

- Correction creates a candidate lesson, not active guidance.
- Do not expand permissions, boundaries, values, scope, or autonomy.
- Do not place raw corrected content in audit summaries.

Completion signal:

- Original lesson is superseded or revoked from context.
- Replacement lesson requires confirmation before activation.
- A human-visible audit receipt is persisted.

## Flow 8: Approve or Roll Back a Self-Lesson

Approval user intents:

- "approve this lesson"
- "use this lesson"
- "promote this lesson"
- "make this lesson active"

Rollback user intents:

- "roll back this lesson"
- "stop using this lesson"
- "this lesson caused a mistake"
- "revoke this lesson"

Required anchor:

- A selected self-lesson card or exact lesson ID.

Required inputs:

- Approval requires explicit approval.
- Rollback requires failure evidence or an explicit user request reason.

Required surface:

- Lesson preview.
- Confidence.
- Applies-to scope.
- Context impact or context-removal impact.
- Audit summary.

Safety rules:

- Promotion requires explicit approval before activation.
- Only low-risk method updates can promote.
- Activation must not expand permissions or autonomy.
- Rollback must reduce influence and remove the lesson from context packs.

Completion signal:

- Approved lesson status is `active` and context eligibility is visible.
- Rolled-back lesson status is `revoked` and context eligibility is false.
- A human-visible audit receipt is persisted.

## Flow 9: Delete a Self-Lesson

User intents:

- "delete this lesson"
- "forget this lesson"
- "remove this lesson"
- "never use this lesson"

Required anchor:

- A selected self-lesson card or exact lesson ID.

Required inputs:

- Explicit delete confirmation.

Required surface:

- Lesson preview.
- Deletion impact.
- Context-removal impact.
- Audit summary.

Safety rules:

- Require an exact lesson anchor before mutating.
- Delete must block context-pack inclusion.
- Preserve a redacted human-visible audit event.

Completion signal:

- Lesson status is `deleted`.
- Context eligibility is false.
- A human-visible audit receipt is persisted.

## Benchmark Hooks

`PALACE-FLOW-001` must pass before UI work can claim the Memory Palace contract:

- Phrase matching maps "why did you think that?" to explain.
- Phrase matching maps "delete that." to delete.
- Phrase matching maps "export these memories" to export.
- Delete flow requires a memory anchor and confirmation.
- Delete completion blocks recall and persists an audit event.
- Explanation results expose available actions and recall eligibility.

`PALACE-EXPORT-UI-001` must pass before export UI work can claim the Memory
Palace contract:

- Export is marked as data egress, not a hidden background sync.
- Export requires explicit confirmation.
- Export accepts selected memory IDs or a visible scoped filter.
- Export preview shows omitted-count and redaction-count lanes.
- Export completion persists a redacted audit receipt.

`PALACE-SELF-LESSON-FLOWS-001` must pass before self-lesson UI work can claim
the Memory Palace contract:

- "what did you learn?" maps to self-lesson review.
- "why did you learn this?" maps to self-lesson explanation.
- "approve this lesson" maps to confirmation-gated promotion.
- "roll back this lesson" maps to influence-reducing rollback.
- Candidate lessons can be explained, corrected, promoted, or deleted.
- Active lessons can be explained, corrected, rolled back, or deleted.
- Revoked lessons can only be explained by default.

`PALACE-SELF-LESSON-REVIEW-FLOW-001` must pass before the stale-review queue can
claim a complete user action path:

- Review-required lessons link to explain, refresh, correct, and delete tools.
- Explanation is read-only and does not require confirmation.
- Refresh, correction, and deletion require explicit confirmation.
- All review action metadata remains content-redacted by default.

`GATEWAY-SELF-LESSON-REVIEW-ACTIONS-001` must pass before the Agent Gateway can
claim the same path:

- Each `self_lesson.review_queue` entry includes the fixed review action plan.
- The plan carries exact gateway tool names and required input names.
- The queued lesson still omits content, learned-from refs, and rollback text.

`GATEWAY-SELF-LESSON-REVIEW-FLOW-001` must pass before a single-card review
surface can claim an end-to-end gateway contract:

- `self_lesson.review_flow` requires an exact lesson ID.
- The response links back to the review queue and returns the same action plan.
- The response exposes next-tool routes without copying lesson content or
  scoped provenance.

`SELF-LESSON-REVIEW-FLOW-SAFETY-SUMMARY-001` must pass before review flows can
be safely rendered as a compact card:

- the response includes a `safety_summary` that separates read-only tools from
  mutation tools;
- every mutation tool in the summary requires confirmation;
- the summary marks content, learned-from refs, and rollback conditions as
  redacted without copying lesson text or scoped provenance.

`SELF-LESSON-REVIEW-FLOW-AUDIT-PREVIEW-001` must pass before mutation buttons
inside the review card can be shown as audit-backed actions:

- the review flow previews the audit receipt shape for refresh, correction, and
  deletion without executing those tools;
- each preview names the expected audit action, target status, confirmation
  requirement, human-visible receipt, and policy refs;
- the preview omits lesson content, learned-from refs, rollback text, and scoped
  provenance.

`SELF-LESSON-REVIEW-FLOW-AUDIT-CONSISTENCY-001` must pass before audit previews
can be treated as reliable action receipts:

- real mutation responses expose the same audit shape ID that the review flow
  previewed;
- refresh, correction, and deletion responses keep policy refs aligned with
  their preview entries;
- actual audit responses stay redacted and do not copy lesson content or scoped
  provenance.

`CONTEXT-PACK-REVIEW-FLOW-AUDIT-HINT-001` must pass before agents can route from
aggregate context-pack review warnings to audit-backed review cards:

- context packs announce that exact review flows include audit previews;
- the summary includes the audit shape ID and exact-lesson-ID requirement;
- the summary does not embed preview content, lesson content, learned-from refs,
  rollback text, or scoped provenance.

`GATEWAY-REVIEW-QUEUE-AUDIT-PREVIEW-001` must pass before review queues can
claim audit-preview routing:

- each review-required queue entry points to `self_lesson.review_flow` with its
  exact lesson ID;
- the queue entry includes the audit preview shape ID and marks the preview as
  not embedded;
- the queue still omits lesson content, learned-from refs, rollback text, and
  scoped provenance.

`GATEWAY-REVIEW-QUEUE-AUDIT-CONSISTENCY-001` must pass before queue hints can be
treated as reliable pointers to exact review cards:

- the queue hint and exact review-flow response share the same audit shape ID;
- the queue hint points to the same lesson ID used by the review flow;
- queue hints remain compact and do not embed preview entries or lesson content.

`GATEWAY-REVIEW-QUEUE-SAFETY-SUMMARY-001` must pass before the queue can be
rendered as an aggregate review surface:

- the queue response includes a `safety_summary` with counts for read-only,
  mutation, confirmation-required, and audit-preview-hint actions;
- mutation actions are counted as confirmation-required and external effects
  remain disallowed from the queue itself;
- the summary is count-based and does not copy lesson content, learned-from
  refs, rollback text, or scoped provenance.

`GATEWAY-REVIEW-QUEUE-EMPTY-SAFETY-001` must pass before an empty queue can be
rendered without special-case risk:

- empty queues still return a `safety_summary`;
- all action and audit-preview counts are zero while redaction and no-external-
  effects markers remain present;
- the summary marks `empty_queue` and does not leak current lesson content,
  learned-from refs, rollback text, or scoped provenance.

`GATEWAY-REVIEW-QUEUE-LIMIT-SAFETY-001` must pass before a paged or limited
queue is shown:

- the queue response and `safety_summary` both name the applied limit, returned
  count, total review-required count, and truncation state;
- action counts summarize only the returned queue slice;
- limit metadata stays numeric and does not leak lesson content, learned-from
  refs, rollback text, or scoped provenance from omitted lessons.

`GATEWAY-REVIEW-QUEUE-ORDERING-001` must pass before queue limits drive UI
pagination:

- the queue orders missing validation dates first, then oldest validation date,
  then `lesson_id` ascending;
- ordering is applied before the limit slices returned lessons;
- the queue and `safety_summary` both expose the ordering contract without
  exposing lesson content, learned-from refs, rollback text, or scoped
  provenance.
