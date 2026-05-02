# Skill Forge Lifecycle

Last updated: 2026-04-27

Code gate: `src/cortex_memory_os/skill_policy.py`
Document derivation gate: `src/cortex_memory_os/skill_forge.py`

## Principle

Skill Forge can discover repeated workflows, but discovery is not permission.

The lifecycle is intentionally incremental:

| Level | Name | Capability | Default execution mode |
| --- | --- | --- | --- |
| 0 | Observed pattern | Cortex notices repetition only | none |
| 1 | Suggested workflow | Cortex can show a proposed workflow | draft-only |
| 2 | Draft-only skill | Cortex can prepare outputs for review | draft-only |
| 3 | Assisted execution | Cortex can assist, with confirmations before external effects | assistive |
| 4 | Bounded autonomy | Cortex can act inside a sandboxed, approved scope | bounded autonomy |
| 5 | Trusted recurring automation | Cortex can run on schedule with audit and rollback | disabled in MVP |

## Promotion Gates

- Promotion must be incremental; a skill cannot jump from observation or draft to autonomy.
- Level 3 or higher requires explicit user approval.
- Level 3 or higher requires at least two successful observed outcomes.
- Level 4 requires low risk and at least five successful observed outcomes.
- Level 5 is disabled in the MVP.
- High-risk skills cannot become autonomous.
- Critical-risk skills cannot exceed draft-only maturity.
- Every promotion decision must be inspectable and benchmarked.

## Risk Behavior

| Risk | Promotion ceiling in MVP | Required behavior |
| --- | --- | --- |
| Low | Level 4 | Sandbox, audit, rollback path |
| Medium | Level 3 | Confirm before external effects |
| High | Level 3 | Step-by-step review, no autonomy |
| Critical | Level 2 | Draft-only by default |

## Failure Handling

Bad outcomes should update the skill's failure modes, not silently expand autonomy.

Repeated failures should produce:

- a debug trace;
- an outcome/postmortem ref;
- a candidate self-lesson;
- a benchmark if the failure can recur.

## Rollback Gates

Rollback is the inverse of promotion, but it is allowed to be faster because it
reduces capability.

Rules:

- Rollback must reduce maturity.
- Rollback requires either failure evidence or explicit user request.
- Rollback must never expand execution mode, confirmation gates, or autonomy.
- Rollback to Level 2 or lower returns the skill to candidate/draft behavior.
- Rollback should append an outcome or postmortem ref to failure modes.
- Critical-risk skills remain capped at draft-only behavior.

Rollback is not deletion. It preserves the skill record and evidence trail so
the user can inspect what failed and why the system became more conservative.

## Draft-Only Execution Contract

Code contract: `src/cortex_memory_os/skill_execution.py`
Gateway contract: `skill.execute_draft`

Draft-only execution is preparation, not action. A Level 2 skill may create
reviewable outputs, but it must not send messages, edit files, deploy code,
make purchases, change settings, or create any other external effect.

Draft-only execution results must include:

- execution ID;
- skill ID;
- policy refs;
- input summary;
- proposed outputs;
- required review actions;
- requested external effects;
- performed external effects.

Required behavior:

- `external_effects_performed` is always empty.
- Proposed outputs are review-required.
- Any requested external effect blocks the run with
  `draft_mode_blocks_external_effects`.
- Non-draft skills are rejected by the draft executor with
  `skill_not_draft_only`.

This lets Skill Forge become useful early without quietly crossing from
apprentice behavior into autonomy.

The gateway may expose draft execution through `skill.execute_draft`. That tool
must return the same draft execution contract and must not perform external
effects. If the caller requests an external effect, the result is `blocked` with
`draft_mode_blocks_external_effects`.

## Document-To-Skill Candidate Flow

`SKILL-DOC-DERIVATION-001` defines how a governed document can become a
document-to-skill candidate. Documents are evidence, not authority.

Required behavior:

- document-derived skills are candidate-only;
- execution mode is `draft_only`;
- maturity cannot exceed Level 2;
- source refs must include the document ID, source ref, and evidence refs;
- approval is required before promotion or external effects;
- rollback and deletion actions must remain visible;
- hostile, secret, or prompt-injection-like documents are rejected;
- audits and benchmarks use redacted metadata, not copied document content.

Policy ref: `policy_document_skill_derivation_v1`.

## Audit Trail

Skill maturity decisions must create human-visible audit receipts.

Audits are required for:

- promotion decisions;
- rollback decisions;
- future skill retirement or reactivation decisions.

Audit summaries may include the target maturity, whether the decision was
allowed, and the decision reason. They must not copy the skill description,
procedure steps, inputs, trigger conditions, or user data. A skill audit is an
operational receipt, not a hidden duplicate of the skill.

## Benchmark Hook

`SKILL-GATE-001` verifies:

- draft skills cannot jump to bounded autonomy;
- assisted execution requires approval and success evidence;
- high and critical risk skills do not gain autonomy.

`SKILL-ROLLBACK-001` verifies:

- rollback must reduce maturity;
- rollback requires failure evidence or explicit user request;
- rollback lowers execution mode;
- rollback preserves confirmation gates and records the failure ref.

`SKILL-AUDIT-001` verifies:

- promotion decisions persist human-visible audit events;
- rollback decisions persist human-visible audit events;
- audit payloads do not copy skill descriptions or procedure steps.

`SKILL-EXECUTION-001` verifies:

- draft-only execution returns reviewable outputs;
- external effects performed are empty;
- requested external effects are blocked;
- non-draft skills cannot be run through the draft executor.

`GATEWAY-SKILL-EXECUTION-001` verifies:

- gateway lists the draft execution tool;
- gateway returns reviewable draft outputs;
- gateway blocks requested external effects;
- gateway output reports zero performed external effects.

`SKILL-DOC-DERIVATION-001` verifies:

- document-derived skills remain candidate-only and draft-only;
- provenance is preserved;
- approval, rollback, and deletion paths are exposed;
- hostile or instruction-like source documents are rejected.

`WORKFLOW-CLUSTERING-001` adds workflow clustering over repeated synthetic or
session traces. It groups traces by normalized workflow label, apps, and action
sequence, then produces a candidate skill only after the repetition threshold is
met.

Required behavior:

- clustered skills stay candidate-only and draft-only;
- maturity cannot exceed Level 2;
- source details stay redacted in cluster receipts;
- hostile traces are rejected;
- traces with external effects are rejected;
- draft previews require review before promotion, procedure changes, or any
  external effect.

Policy ref: `policy_workflow_clustering_v1`.
