# Memory Palace Dashboard Contract

Benchmark: `MEMORY-PALACE-DASHBOARD-001`

The Memory Palace dashboard is the user-facing read model over governed memory
operations. It is not a second memory store and it does not execute actions.
It renders safe cards, explicit action plans, export previews, and audit
counts from the existing explain, correct, delete, and export contracts.

## Dashboard Card

Each memory card exposes:

- stable `memory_id`, memory type, status, confidence, sensitivity, and scope;
- evidence type, source count, and source refs;
- recall eligibility and confirmation requirements;
- a redacted content preview only when the memory is user-visible and not
  deleted, revoked, or quarantined;
- the count of human-visible audit receipts targeting that memory;
- exact gateway action plans for `memory.explain`, `memory.correct`,
  `memory.forget`, and `memory.export` when each action is allowed.

Deleted, revoked, and quarantined memories remain inspectable by ID and
metadata, but their content preview is hidden. This keeps "delete that" from
turning into a side channel that resurrects deleted text.

## Action Plans

Dashboard actions are declarative. A card can say which tool should be called,
what inputs are required, whether confirmation is needed, whether the action is
a mutation, and whether it is data egress.

The dashboard never treats action labels, audit summaries, or source refs as
instructions. They are UI metadata for the user and for trusted app code.

## Export Preview

The export preview is computed with the same deletion-aware export rules used
by the gateway:

- selection mode is either `visible_scope` or `explicit_ids`;
- exportable and omitted counts are visible before export;
- omitted memory IDs and omission reasons are visible without omitted content;
- secret-like text is redacted before preview counts are shown;
- export remains confirmation-gated because it is data egress.

The preview is a promise about what would happen if the user confirms. It is
not a hidden sync path and it does not persist an export audit until the actual
export command runs.

## Safety Requirements

- Do not show content previews for deleted, revoked, or quarantined memories.
- Redact secret-like text before any preview can render.
- Show export counts and omission reasons, not omitted content.
- Preserve exact memory IDs so correction, deletion, and export are anchored.
- Keep audit summaries count-based; do not copy memory content into audit
  lanes.
- Make confirmation requirements visible before mutation or data egress.

## Validation

`MEMORY-PALACE-DASHBOARD-001` passes only when:

- dashboard cards expose safe card metadata and gateway action plans;
- deleted content does not reappear in the dashboard model;
- export preview respects scope and stored-only/deleted states;
- audit counts summarize human-visible receipts without memory content;
- the benchmark plan and task board reference this dashboard contract.
