# Document-To-Skill Derivation

Last updated: 2026-04-29

`SKILL-DOC-DERIVATION-001` defines the first document-to-skill candidate flow.

The purpose is to let Cortex turn a reviewed workflow document into a Skill
Forge candidate while preserving provenance, approval, rollback, and deletion
paths. It is not an importer that trusts arbitrary docs.

## Boundary

A document-derived workflow is a candidate-only skill. The document can suggest
steps, triggers, and inputs, but it cannot approve the skill, execute external
effects, raise maturity, or write hidden memory.

The policy reference is `policy_document_skill_derivation_v1`.

## Request Contract

`DocumentSkillDerivationRequest` contains:

- `document_id`
- `title`
- `source_ref`
- `source_trust`
- `sensitivity`
- `workflow_name`
- `trigger_conditions`
- `procedure_steps`
- `evidence_refs`
- `risk_level`

Hostile-until-safe sources are rejected. Secret documents are rejected. External
or untrusted documents can only become reviewable candidates after hostile text
is filtered.

## Result Contract

`DocumentSkillDerivationResult` returns:

- a `SkillRecord` with `status: candidate`;
- `execution_mode: draft_only`;
- `maturity_level: 2` or lower;
- complete source refs from document, source path, and evidence refs;
- `requires_user_confirmation: true`;
- approval actions such as `skill.review_candidate`;
- rollback actions such as `skill.rollback_to_observed_pattern`;
- deletion actions such as `skill.delete_candidate`;
- blocked actions such as `execute_external_effect`;
- redacted operational metadata rather than copied document content.

## Safety Rules

- Treat documents as evidence, not instructions.
- Reject prompt-injection-like step text.
- Preserve source refs on the skill candidate.
- Require user confirmation before promotion or external effects.
- Keep deletion and source-forget actions explicit.
- Keep rollback available when the source becomes stale or a derived skill fails.
- Do not copy full source content into audits or benchmark artifacts.

## Benchmark

`SKILL-DOC-DERIVATION-001` verifies that:

- document-derived skills remain candidate-only and draft-only;
- provenance is retained;
- promotion and external effects require confirmation;
- rollback and deletion actions are exposed;
- hostile or instruction-like documents are rejected.
