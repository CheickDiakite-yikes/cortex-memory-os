# Live Clicker Demo

Last updated: 2026-05-02

`LIVE-CLICKER-DEMO-001` is the first visible end-to-end demo shaped like the
user-requested experience:

```text
Computer Use browser action
-> visible Cortex Shadow Clicker follows the pointer
-> page-local observation event
-> perception envelope
-> firewall and evidence eligibility
-> Shadow Pointer capture receipt
-> demo candidate memory
-> retrieval and context-pack hits
```

The runnable command is:

```bash
uv run cortex-live-clicker-demo
```

The smoke command is:

```bash
uv run cortex-live-clicker-demo --smoke --json
```

## Scope

The demo serves a disposable safe site from localhost. It is intentionally not a
production capture daemon and it does not observe arbitrary real browsing yet.

The browser page includes a subtle **Cortex Shadow Clicker** overlay. Pointer
movement and safe button/input actions move the visible overlay and send a
small JSON observation to the local `/observe` endpoint. The dashboard panel on
the same page shows:

- observation state;
- firewall decision;
- evidence write mode;
- demo candidate memory write state;
- retrieval and context-pack hits;
- raw-ref retention state.

## Safety Contract

The policy reference is `policy_live_clicker_demo_v1`.

The demo must preserve these boundaries:

- localhost-only page and endpoint;
- Computer Use actions only on the disposable safe site;
- candidate memories use the demo temp store, not private production memory;
- retrieval and context-pack hits are proved from the demo memory store;
- no raw screen capture;
- no raw screen storage;
- no raw Accessibility tree storage;
- no raw refs in receipts;
- no external effects;
- no mutation/export/draft execution;
- no model secret echo attempts.

The page-local observation is closer to the desired product experience than the
earlier static dashboard proof because the user can see the pointer telemetry
and the memory-system result update together. It is still deliberately safer
than real screen capture. The next step toward arbitrary safe sites is a
consented browser-extension path that emits the same receipt shape from an
explicit allowlisted origin.

## Known Gaps

The live proof intentionally stops short of the final product:

- the Shadow Clicker is a browser-page overlay, not the native macOS overlay;
- observations are page-local synthetic events, not arbitrary screen capture;
- candidate memories use a temp demo store, not durable private memory;
- the safe site is localhost, not a user-approved allowlisted external origin;
- the demo does not yet capture real Accessibility trees, screenshots, OCR, or
  raw evidence refs.

These gaps are product boundaries, not failures. The next live ladder should
reuse the same receipt shape from an allowlisted browser-extension origin before
moving to consented real screen capture.

## Request Hardening

`LIVE-CLICKER-HARDENING-001` closes the first demo-server gaps without widening
capture:

- `/observe` requires a per-session token injected into the served page;
- `/observe` requires a localhost origin and loopback client/host;
- `/observe` rejects unsupported content types before reading observation JSON;
- the demo session enforces an observation cap to prevent floods;
- rejected requests increment a redacted rejection count but do not create demo
  memories;
- rejected requests render as blocked in every status field so stale memory
  results are not left visible after a failed write;
- responses include no-store, nosniff, no-referrer, and restrictive
  Content-Security-Policy headers.

## Verification

Automated coverage:

- `tests/test_live_clicker_demo.py`;
- `uv run cortex-live-clicker-demo --smoke --json`;
- `LIVE-CLICKER-DEMO-001/visible_shadow_clicker_memory_loop` in
  `uv run cortex-bench`.

Manual/live proof:

1. Start `uv run cortex-live-clicker-demo`.
2. Open the printed localhost URL in Chrome.
3. Use Computer Use to click the safe-site controls and type a harmless note.
4. Confirm the Cortex Shadow Clicker visibly follows pointer/click positions.
5. Confirm the observation panel reports candidate memory writes, retrieval
   hits, context-pack hits, and `Raw refs: none`.

2026-05-02 live proof: Computer Use clicked `Open research note`,
`Compare source`, and `Record conclusion` on `http://127.0.0.1:8795/`.
The visible Shadow Clicker moved to each clicked control. The local `/results`
receipt passed with 4 observations, 4 demo candidate memories, 4 retrieval
hits, 4 context-pack hits, 0 raw refs, and 0 external effects. A regression
test keeps target-specific retrieval visible after the session grows beyond the
default result limit.

2026-05-02 hardening proof: restarting the server invalidated the old page
token, and the stale page received `invalid_demo_token` without a memory write.
After reload, the same Computer Use click path passed with 4 valid observations,
4 demo memories, 4 retrieval/context hits, 1 rejected stale-token request, 0 raw
refs, and 0 external effects. Automated hardening smoke also rejects missing
token, wrong origin, wrong content type, and over-cap observations before memory
write.
