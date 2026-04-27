# Memory Lifecycle

Last updated: 2026-04-27

Code gate: `src/cortex_memory_os/memory_lifecycle.py`

## Purpose

Cortex memories are not loose notes. Every durable memory must carry provenance, confidence, validity, scope, influence limits, and a status that controls recall.

The lifecycle is the safety rail between evidence and future agent behavior.

## Required Primitives

Every `MemoryRecord` must include:

| Field | Purpose |
| --- | --- |
| `memory_id` | Stable identity for correction, deletion, audit, and source refs. |
| `type` | Episodic, semantic, procedural, preference, project, relationship, affective, self-lesson, or policy. |
| `content` | Human-readable memory content, not raw evidence. |
| `source_refs` | Scene, evidence, conversation, prior memory, or project refs that justify the memory. |
| `evidence_type` | User-confirmed, observed, inferred, observed-and-inferred, or external evidence. |
| `confidence` | Numeric confidence used by promotion and retrieval scoring. |
| `status` | Lifecycle state that controls recall and mutation. |
| `valid_from` / `valid_to` | Temporal truth window. |
| `sensitivity` | Privacy classification. |
| `scope` | Personal, work, project, app, agent, session, ephemeral, or never-store boundary. |
| `influence_level` | Whether memory can only be queried, personalize, plan, affect tools, or trigger autonomy. |
| `allowed_influence` / `forbidden_influence` | Explicit behavior boundaries. |
| `decay_policy` | Review or expiry hint. |
| `user_visible` | Whether Memory Palace can show it. |

## Lifecycle States

| State | Meaning | Recall behavior |
| --- | --- | --- |
| `candidate` | Proposed memory awaiting enough confidence or review. | Eligible only if scope and influence allow; lower retrieval score. |
| `active` | Current memory allowed to influence within its explicit limits. | Eligible if scope, privacy, validity, and retrieval score allow. |
| `deprecated` | Older memory that may still explain history but should be downranked. | Eligible with penalty. |
| `superseded` | Replaced by a newer memory. | Not retrievable for context packs. |
| `revoked` | Disabled by policy or consent change. | Not retrievable; terminal. |
| `deleted` | User or policy deletion tombstone. | Not retrievable; terminal. |
| `quarantined` | Unsafe, hostile, or untrusted memory-like content. | Not retrievable; cannot activate in MVP. |

## Promotion Rules

- A memory can activate only when it is not deleted, revoked, superseded, or quarantined.
- External evidence cannot activate directly.
- Secret memory cannot activate or be recalled.
- Observed or observed-and-inferred memory needs confidence `>= 0.75`.
- Inferred memory needs explicit user approval and confidence `>= 0.90`.
- Any memory requiring confirmation needs user approval before activation.
- Tool-action or autonomous influence requires user approval before activation.

## Blocking Rules

Statuses that block recall:

- `deleted`
- `revoked`
- `superseded`
- `quarantined`

These statuses set `influence_level` to `stored_only`, clear `allowed_influence`, and set `valid_to` when applied.

## Deletion, Revocation, and Supersession

Deletion and revocation are terminal. They preserve a tombstone so indexes and future stores can prove the memory should not reappear.

Supersession requires a replacement memory ID. The old memory becomes non-retrievable, and the replacement should reference the old memory in `source_refs`.

## Recall Policy

Recall requires:

- status is not recall-blocking;
- influence is not `stored_only`;
- scope matches the retrieval request;
- sensitivity is not `secret`;
- validity window has not expired;
- retrieval score is positive.

Retrieval scoring then weighs relevance, confidence, source trust, recency, privacy penalties, status penalties, and staleness.

## Benchmark Hook

`MEM-LIFECYCLE-001` verifies:

- safe candidate memory can activate;
- low-confidence, external, inferred-without-approval, secret, deleted, superseded, revoked, and quarantined memories cannot influence recall;
- deletion and supersession strip influence and set lifecycle bounds.
