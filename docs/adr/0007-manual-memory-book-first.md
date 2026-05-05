# ADR 0007: Manual Memory Book First

Date: 2026-05-05

Status: Accepted

## Context

Cortex has strong safety contracts, dashboard panels, and synthetic receipts,
but the first demo spine still needs to feel like a useful brain. The safest
product-shaped loop is not real screen capture. It is a user intentionally
telling Cortex what to remember, seeing that memory in plain language, finding
it later, fixing it, and forgetting it.

## Decision

Build the first durable memory loop as a manual Memory Book:

- user-confirmed text only;
- local localhost-only token-protected endpoints;
- encrypted durable storage through the existing unified memory boundary;
- child-readable cards that explain what Cortex remembers, why the memory
  exists, where it can be used, and whether it is safe;
- `direct-query` influence by default;
- explicit save, ask, find, explain-why, fix, forget, and undo-forget actions;
- a read-only snapshot for first-run guidance and safety lights;
- a direct-query-only helper context pack that lets agents answer from
  user-saved memories without gaining tool/action authority;
- redacted audit receipts for save, correct, and forget;
- rejection of secret-like and prompt-injection-like input before any write.

The policy anchor for this loop is `policy_manual_memory_book_v1`, and the
benchmark anchor is `MANUAL-MEMORY-BOOK-001`.

## Consequences

This gives the live cursor and future tutor overlays a real memory substrate to
plug into without widening observation authority. The helper context pack is
the first bridge from memory to agents: it can carry relevant user-confirmed
memory cards for a direct answer, but it still blocks screen capture, raw refs,
tool actions, autonomous workflows, exports, and external effects. It also
gives users a small trust-building flow before any capture, microphone, raw
ref, autonomous action, export, or external effect is introduced. The undo
window is intentionally short and local; it restores only a user-forgotten
manual memory and does not make forgotten memories searchable while they are
forgotten.

## Alternatives considered

- Continue polishing dense dashboard panels. This would improve appearances but
  still leave the product without a real user-readable memory loop.
- Start with real screen capture. This would be more impressive but too risky
  before the manual write, correction, revocation, and audit paths are proven.
- Store manual memories in plaintext Markdown. This is easier to inspect but
  violates the encrypted durable memory boundary already chosen for Cortex.

## Verification plan

- `uv run pytest tests/test_manual_memory_book.py -q`
- `uv run cortex-manual-memory-book --smoke --json`
- `uv run cortex-capture-control-server --smoke --json`
- `uv run cortex-bench --no-write`, including `MANUAL-MEMORY-BOOK-001`
- Browser proof against the localhost dashboard: save, ask, build the helper
  note, explain why, find, fix inline, confirm forget in-page, undo, forget
  again, and confirm forgotten memories no longer appear in retrieval.
