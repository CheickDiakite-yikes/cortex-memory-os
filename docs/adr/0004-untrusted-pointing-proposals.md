# ADR 0004: Untrusted Pointing Proposals Are Display-Only

Status: Accepted

Date: 2026-04-29

## Context

The Shadow Pointer will eventually show where an agent believes the user or a
workflow should look next. Recent agent UI systems make coordinate prediction
feel tempting: a model can propose screen points, element boxes, and cursor
targets. That same feature can become a privilege-escalation path if untrusted
text or model reasoning can smuggle in a click, drag, tool call, or memory write.

External webpages, screenshots, OCR, READMEs, PDFs, issue text, and benchmark
prompts may contain hostile instructions. Even local model output is only an
inference unless the user confirms it.

## Decision

Model-proposed coordinates enter Cortex as `ShadowPointerPointingProposal`.
They compile into `ShadowPointerPointingReceipt`, which is display-only.

The receipt may allow a visible overlay or highlight. It must block privileged
effects, including clicks, typing, drags, scrolling, URL opens, tool calls, and
direct memory writes.

The policy reference is `policy_shadow_pointer_pointing_proposal_v1`.

## Consequences

- Coordinate proposals can improve legibility without gaining input authority.
- Native overlays have one object to render and one set of effects to obey.
- Agent or webpage text cannot become an action merely by being near a pointer.
- Any future move from pointer hint to action requires a separate confirmation,
  risk gate, audit record, and action-specific tool contract.

## Alternatives Considered

- Let model coordinates drive synthetic clicks after confidence thresholds:
  rejected because confidence is not consent or authority.
- Store model target descriptions as memory candidates: rejected for this
  contract because pointing is UI evidence, not durable user memory.
- Drop coordinate proposals entirely: safer, but it would remove useful
  transparency from the Shadow Pointer overlay.

## Verification Plan

- `tests/test_shadow_pointer.py` validates display-only receipts, bounds checks,
  prompt-injection-like text rejection, and window-reference requirements.
- `POINTER-PROPOSAL-001` verifies docs, policy refs, blocked effects, and memory
  write blocking in the benchmark harness.
