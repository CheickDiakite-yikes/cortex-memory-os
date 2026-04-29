# Skill Forge Candidate List

Last updated: 2026-04-29

`SKILL-FORGE-LIST-001` defines the first dashboard-facing Skill Forge candidate
list contract. It is not the final UI. It is the safe view model a future UI
can render to make learned workflows inspectable before any approval,
promotion, or execution path.

## Purpose

Skill Forge turns repeated scenes and governed documents into draft-only skill
candidates. The candidate list makes those candidates reviewable without
treating discovery as permission.

Each card exposes:

- skill ID and name;
- lifecycle status;
- risk level;
- maturity level;
- execution mode;
- source count and bounded source refs;
- trigger count;
- procedure step count and truncated procedure preview;
- success and failure signal counts;
- required confirmation gates;
- promotion blockers;
- review action plans.

## Safety Rules

- Candidate cards are review surfaces, not execution permission.
- Only candidate skills appear in the list.
- Active, deleted, revoked, or rejected skills can be counted, but are not shown
  as candidate cards.
- Procedure previews are truncated and redacted before rendering.
- Action plans point to gateway tools but do not run them.
- Candidate-list action plans must not include external effects.
- Promotion blockers must remain visible, especially `user_approval_required`
  and insufficient evidence reasons.
- Approve, edit, and reject actions require confirmation and audit.

Policy ref: `policy_skill_forge_candidate_list_v1`.

## Expected Actions

The first action set is intentionally conservative:

- `skill.review_candidate`
- `skill.execute_draft`
- `skill.approve_draft_only`
- `skill.edit_candidate`
- `skill.need_more_data`
- `skill.reject_candidate`

`skill.execute_draft` is still draft-only and cannot perform external effects.
Promotion beyond draft-only remains governed by Skill Forge maturity gates.

## Benchmark Contract

`SKILL-FORGE-LIST-001` verifies that:

- repeated-scene and document-derived candidates render as candidate cards;
- status, risk, maturity, execution mode, source counts, procedure counts, and
  confirmation gates are visible;
- secret-like text is redacted from previews;
- action plans do not contain external effects;
- active skills are counted but omitted from candidate cards;
- this product doc, task board, benchmark plan, and benchmark registry name the
  contract.
