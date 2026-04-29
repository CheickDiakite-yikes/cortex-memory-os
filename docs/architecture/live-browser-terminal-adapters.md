# Live Browser And Terminal Adapter Smoke

Last updated: 2026-04-29

`LIVE-BROWSER-TERMINAL-ADAPTERS-001` turns the earlier browser/terminal adapter
contracts into dormant local adapter artifacts. This is still not a production
capture path. It is a safety-first bridge from contract to installable shape.

## Browser Extension Scaffold

The browser scaffold lives in `adapters/browser-extension` and uses Manifest V3.
It is intentionally click-gated:

- the browser action injects `content-script.js` only after a user click;
- `cortexEnabled` defaults to `false`;
- only `http://127.0.0.1/*` and `http://localhost/*` host permissions are
  present;
- the service worker refuses non-local endpoints;
- the content script sends visible text only, not raw DOM HTML;
- payloads are marked `external_untrusted` and `third_party_content`;
- `dom_ref` and `raw_ref` are `null` so web content cannot become raw memory.

## Terminal Shell Hook Scaffold

The terminal scaffold lives in `adapters/terminal-shell`.

It is intentionally opt-in:

- the zsh hook is inert unless `CORTEX_TERMINAL_OBSERVER=1`;
- events post only to localhost endpoints;
- command text is redacted before emission;
- `raw_ref` is always `null`;
- the hook emits a derived terminal command event after command completion with
  an exit code;
- failed local posts do not block shell usage.

## Smoke Contract

The Python smoke command is:

```bash
uv run cortex-live-adapter-smoke
```

The smoke validates adapter files and then runs synthetic events through:

```text
BrowserAdapterEvent / TerminalAdapterEvent
  -> PerceptionEventEnvelope
  -> FirewallDecisionRecord
  -> EvidenceEligibilityPlan
```

Acceptance requires:

- browser DOM remains external, third-party, raw-ref-free, and not memory
  eligible;
- browser prompt-injection text is quarantined before evidence storage;
- terminal secret text is masked and raw refs are dropped;
- terminal events require explicit opt-in and local endpoints;
- every artifact carries `policy_live_adapter_smoke_v1`.

This gives us a real adapter shape while preserving the original rule: external
content is evidence, not instructions or trusted memory.
