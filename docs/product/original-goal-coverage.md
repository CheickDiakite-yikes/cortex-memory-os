# Original Goal Coverage

Last updated: 2026-04-29

`PRODUCT-GOAL-COVERAGE-001` keeps the implementation tied to the original Cortex
Memory OS thesis:

```text
Perception -> Evidence -> Memory -> Skill -> Agent Action -> Outcome -> Self-Improvement
```

The benchmark should fail if the product drifts toward the rejected shallow
pattern:

```text
screen recording -> summary -> vector DB
```

## Canonical Loop Coverage

| Goal area | Current product contract | Proof path |
| --- | --- | --- |
| Perception | Consented local observations are modeled as structured events and envelopes, not durable memories. | `ObservationEvent`, `PerceptionEventEnvelope`, `PERCEPTION-EVENT-ENVELOPE-001`, `SCENE-SEGMENT-001`, `SHADOW-POINTER-001` |
| Evidence | Evidence remains distinct from memory, with retention, provenance, and vault boundaries. | `EvidenceRecord`, `VAULT-RETENTION-001`, `VAULT-ENCRYPT-001` |
| Memory | Memory records carry source refs, confidence, status, validity, influence limits, and deletion semantics. | `MemoryRecord`, `MEM-COMPILE-001`, `MEM-LIFECYCLE-001`, `MEM-FORGET-001` |
| Skill | Repeated work becomes draft-only skills first, with maturity gates and rollback. | `SkillRecord`, `SKILL-FORGE-002`, `SKILL-GATE-001`, `SKILL-ROLLBACK-001` |
| Agent Gateway | Agents receive scoped context packs and explicit tools, not unrestricted stores. | `ContextPack`, `GATEWAY-CTX-001`, `CONTEXT-PACK-001`, `GATEWAY-PALACE-001` |
| Outcome | Task outcomes and user corrections feed postmortems, audits, and self-lessons. | `OutcomeRecord`, `SELF-LESSON-001`, `SELF-LESSON-AUDIT-001` |
| Self-Improvement | Self-lessons can improve methods, retrieval, templates, skills, and checklists, but not values or permissions. | `SELF-LESSON-001`, `GATEWAY-SELF-LESSON-PROMOTE-001`, `GATEWAY-SELF-LESSON-REVIEW-QUEUE-001` |

## User-Facing Pillar Coverage

| Pillar | Current contract | Proof path |
| --- | --- | --- |
| Shadow Pointer | Shows observation, masking, memory, context, approval, action, and pause states. | `SHADOW-POINTER-001`, `ui/shadow-pointer/` |
| Memory Palace | Lets users inspect, explain, correct, delete, export, scope, and review memory and self-lessons. | `MEMORY-PALACE-001`, `PALACE-FLOW-001`, `PALACE-SELF-LESSON-FLOWS-001`, `PALACE-EXPORT-UI-001` |
| Skill Forge | Shows learned workflows as candidate skills before any autonomous execution. | `SKILL-FORGE-002`, `SKILL-EXECUTION-001`, `GATEWAY-SKILL-EXECUTION-001` |
| Agent Gateway | Exposes governed context, Memory Palace actions, skill execution, audit receipts, and review queues. | `GATEWAY-CTX-001`, `GATEWAY-SKILL-AUDIT-001`, `GATEWAY-SELF-LESSON-REVIEW-FLOW-001` |

## Safety And Operations Coverage

| Control | Current contract | Proof path |
| --- | --- | --- |
| Privacy + Safety Firewall | Runs before durable memory and blocks hostile or sensitive observations from becoming memory. | `SEC-INJECT-001`, `SEC-PII-001`, `CTX-HOSTILE-001` |
| Prompt-injection resistance | External content is evidence until promoted and cannot become agent instructions by default. | `docs/ops/research-safety.md`, `docs/security/hostile-context-pack-policy.md` |
| Auditability | Memory, skill, export, and self-lesson mutations produce redacted human-visible receipts. | `AUDIT-001`, `EXPORT-AUDIT-001`, `SKILL-AUDIT-001`, `SELF-LESSON-AUDIT-001` |
| Revocation and deletion | Deleted or revoked memory must stay out of retrieval, context packs, exports, and skill influence. | `MEM-FORGET-001`, `EXPORT-001`, `SELF-LESSON-AUDIT-LIST-001` |
| Robot readiness | High-risk and critical actions require explicit review and physical-world gates before future embodied use. | `ROBOT-SAFE-001`, `docs/security/initial-threat-model.md` |
| Operating loop | Work is tracked through task board, benchmark registry, debug journal, and ADRs. | `docs/ops/task-board.md`, `docs/ops/benchmark-registry.md`, `docs/ops/debug-journal.md`, `docs/adr/` |

## Benchmark Expectations

`PRODUCT-GOAL-COVERAGE-001` verifies that:

- the original canonical loop is present in product coverage docs;
- the anti-pattern remains named so future builders do not collapse the product
  into screen recording, summary, and vector search only;
- Shadow Pointer, Memory Palace, Skill Forge, and Agent Gateway each have a
  current contract and proof path;
- safety, prompt-injection handling, auditability, deletion, robot readiness,
  and ops tracking remain visible in the product trace;
- the benchmark plan names this suite so goal drift blocks future merges.
