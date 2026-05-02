# Cortex Browser Adapter

This is a dormant Manifest V3 browser-extension scaffold for
`LIVE-BROWSER-TERMINAL-ADAPTERS-001`.

Safety defaults:

- The extension is click-gated through the browser action.
- The manifest declares `Alt+Shift+C` as the suggested browser-action shortcut
  for disposable live-test profiles. Chrome may still require the user to assign
  or approve the shortcut, so the Extensions menu remains the reliable manual
  activation path.
- `cortexEnabled` defaults to `true` for local development profiles, but the
  service worker still refuses non-localhost endpoints and non-HTTP tabs.
- Only localhost Cortex endpoints are allowed.
- Browser page text is always `external_untrusted` and `third_party_content`.
- The adapter sends no raw DOM reference and does not mark browser content as
  memory eligible.

The current repo smoke test reads these files statically and runs synthetic
handoffs through the Python firewall/evidence chain. Do not install this into a
daily browser profile until the native consent UI and local endpoint are ready.
