# Cortex Browser Adapter

This is a dormant Manifest V3 browser-extension scaffold for
`LIVE-BROWSER-TERMINAL-ADAPTERS-001`.

Safety defaults:

- The extension is click-gated through the browser action.
- `cortexEnabled` is `false` unless a local user explicitly enables it in
  extension storage.
- Only localhost Cortex endpoints are allowed.
- Browser page text is always `external_untrusted` and `third_party_content`.
- The adapter sends no raw DOM reference and does not mark browser content as
  memory eligible.

The current repo smoke test reads these files statically and runs synthetic
handoffs through the Python firewall/evidence chain. Do not install this into a
daily browser profile until the native consent UI and local endpoint are ready.
