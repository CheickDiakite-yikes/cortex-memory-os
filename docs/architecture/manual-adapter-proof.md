# Manual Adapter Proof

Last updated: 2026-04-30

`MANUAL-ADAPTER-PROOF-001` proves the live adapter artifacts against the local
adapter endpoint without installing into a daily browser profile or recording
private data.

The proof command is:

```bash
uv run cortex-manual-adapter-proof --json
```

## What The Proof Does

The command starts the real local endpoint on `127.0.0.1:0`, then performs two
synthetic artifact-shaped checks:

1. Sources `adapters/terminal-shell/cortex-terminal-hook.zsh` in a temporary
   zsh subprocess with `CORTEX_TERMINAL_OBSERVER=1` and calls
   `cortex_terminal_emit_event`.
2. Posts browser-extension-shaped visible-page payloads to
   `POST /adapter/browser`, including a prompt-injection page.

The terminal command contains a fake secret marker, but the hook redacts command
text before emission and the proof output never prints the marker.

## Acceptance Gates

- terminal hook returns successfully;
- local endpoint observes a terminal event;
- terminal secret marker is not retained;
- terminal raw refs are not retained;
- browser payload is accepted but not memory eligible;
- browser raw refs are not retained;
- browser prompt-injection payload is discarded;
- service worker still restricts endpoints to localhost;
- content script still contains visible-text redaction and `dom_ref: null`;
- stdout and stderr stay redacted.

Policy reference: `policy_manual_adapter_proof_v1`.
