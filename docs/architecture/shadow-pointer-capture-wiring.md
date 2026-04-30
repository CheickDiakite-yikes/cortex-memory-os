# Shadow Pointer Capture Wiring

Last updated: 2026-04-30

Benchmark: `SHADOW-POINTER-CAPTURE-WIRING-001`

Policy reference: `policy_shadow_pointer_capture_wiring_v1`

This slice wires governed adapter outcomes into the Shadow Pointer without
starting capture. The input is an `AdapterHandoffResult` that has already passed
through perception envelope creation, firewall assessment, and evidence
eligibility planning. The output is a `ShadowPointerCaptureReceipt`.

## Boundary

The receipt is a transparency surface, not a capture controller:

- it does not request macOS permissions;
- it does not start screen, browser, terminal, or Accessibility capture;
- it does not execute actions;
- raw refs are not exposed to the overlay receipt;
- memory writes stay blocked whenever the firewall or Evidence Vault handoff
  blocks memory eligibility.

## State Mapping

| Adapter outcome | Shadow Pointer state | Memory writes | User confirmation |
| --- | --- | --- | --- |
| Active consent, memory-eligible local evidence | `observing` | allowed for the next compiler stage | no |
| Active consent, third-party browser content | `observing` | blocked | no |
| Secret-like or redacted content | `private_masking` | blocked | no |
| Discarded sensitive app, private field, denied permission, or blocked app | `private_masking` | blocked | no |
| Prompt-injection or hostile content quarantine | `needs_approval` | blocked | yes |
| Paused consent | `paused` | blocked | no |
| Revoked or unknown consent | `off` | blocked | no |

## Receipt Fields

`ShadowPointerCaptureReceipt` includes:

- the adapter source and event ID;
- the resulting `ShadowPointerSnapshot`;
- observation and memory-write booleans;
- whether user confirmation is required;
- audit flags and audit action;
- perception route, firewall decision, and evidence write mode;
- derived or metadata evidence refs only;
- policy refs from Shadow Pointer capture wiring, perception adapter,
  firewall, and evidence eligibility.

This keeps the native overlay honest. It can show what Cortex is doing and why
without leaking raw browser DOM, raw terminal output, screen frames, or private
Accessibility tree data.

## Safety Invariants

- `needs_approval` receipts always require user confirmation.
- `private_masking`, `paused`, `off`, and `needs_approval` receipts cannot allow
  memory writes.
- Memory writes require a memory-eligible firewall decision and durable derived
  or raw-derived evidence.
- Overlay evidence refs must not start with `raw://`.
- Audit-required receipts must name an audit action.

## Follow-Up

The next native slice should read these receipts from the local adapter endpoint
or permission-status command and render them in the macOS Shadow Pointer panel.
That should remain read-only until the user deliberately enables capture.
