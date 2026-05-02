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
