# Cortex Terminal Shell Adapter

This is an opt-in zsh hook scaffold for `LIVE-BROWSER-TERMINAL-ADAPTERS-001`.

Safety defaults:

- The hook does nothing unless `CORTEX_TERMINAL_OBSERVER=1`.
- Events post only to `http://127.0.0.1:*` or `http://localhost:*`.
- Command text is redacted before emission.
- `raw_ref` is always `null`; the local endpoint decides whether sanitized
  derived evidence can be stored after firewall review.
- Failed posts are ignored so shell work is not blocked by Cortex.

The hook is not installed automatically. The current smoke test validates the
file statically and uses synthetic terminal events through the Python handoff
chain.
