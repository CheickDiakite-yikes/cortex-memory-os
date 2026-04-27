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
