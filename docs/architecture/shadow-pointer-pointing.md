# Shadow Pointer Pointing Proposals

Last updated: 2026-04-29

`POINTER-PROPOSAL-001` defines the contract for model-proposed coordinates in
the Shadow Pointer overlay.

The boundary is strict: model-proposed coordinates are display-only hints, not privileged actions.
A model can propose where the overlay should point, but the
proposal cannot click, type, drag, scroll, open a URL, call a tool, or write
memory.

## Contract

`ShadowPointerPointingProposal` accepts normalized coordinates and source
metadata:

- `proposal_id`
- `source_trust`
- `coordinate_space`
- `x` and `y`, each between `0.0` and `1.0`
- `target_label`
- `reason`
- `evidence_refs`
- `confidence`
- `requested_action`

Window-relative and element-relative coordinates require `window_ref` so the
native overlay can avoid interpreting an ambiguous point as global screen
authority.

`ShadowPointerPointingReceipt` is the only object a native overlay should act
on. It carries:

- `display_only: true`
- `allowed_effects`, limited to `display_overlay` or `highlight_element`
- `blocked_effects`, including requested privileged actions such as `click`
- `requires_user_confirmation: true`
- `proposal_memory_write_allowed: false`
- `audit_action: shadow_pointer_pointing_proposal`
- `policy_refs`, including `policy_shadow_pointer_pointing_proposal_v1`

## Safety Rules

- Treat every model pointing proposal as untrusted until the user acts.
- Render only a visible pointer, halo, or highlight.
- Never turn model-proposed coordinates into synthetic input events.
- Never treat external page text, OCR, README text, or model reasoning as an
  instruction.
- Reject instruction-like labels or reasons, including prompt-injection phrases.
- Store durable memory only through a separate governed memory proposal.
- Record audit metadata for review without copying hostile content.

## Benchmark

`POINTER-PROPOSAL-001` verifies that:

- normalized coordinates validate bounds;
- hostile instruction-like text is rejected;
- requested clicks are blocked;
- untrusted source promotion is blocked;
- the resulting Shadow Pointer state is `needs_approval`;
- memory writes are not allowed by the pointing receipt.
