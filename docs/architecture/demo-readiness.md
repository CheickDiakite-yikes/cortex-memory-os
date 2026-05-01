# Safe Local Demo Readiness

Last updated: 2026-05-01

Benchmark: `DEMO-READINESS-001`

Policy reference: `policy_demo_readiness_v1`

This slice turns the current Cortex prototype into a safe, repeatable demo. The
demo shows the brain loop without observing the user's real screen, storing raw
private refs, echoing secrets, mutating memory, exporting data, executing draft
skills, or performing external effects.

## Demo Contract

The one-command receipt is:

```bash
uv run cortex-demo --json
```

It composes these safe proof surfaces:

- dashboard smoke for the local Memory Palace, Skill Forge, Focus Inspector,
  guardrails, and receipts;
- Synthetic capture ladder using a disposable page, temporary raw evidence,
  audited synthetic memory, retrieval, context pack, and secret negative test;
- encrypted index search through `memory.search_index`;
- context pack policy refs through `memory.get_context_pack`;
- `.env.local` git hygiene without reading secret values.

## Safe Demo Path

The dashboard renders a compact `Safe Demo Path` rail:

1. Open the localhost dashboard.
2. Run the Synthetic capture ladder.
3. Show encrypted index retrieval.
4. Show the context pack policy and redacted diagnostics.

The UI is intentionally a narration path, not a new work queue. It should stay
calm and small enough to explain the system during a live walkthrough.

## Hard Off Switches

`DEMO-READINESS-001` passes only when all of these remain true:

- No real screen capture.
- No durable raw screen storage.
- No raw private refs returned.
- No secret echo.
- No mutation, export, or draft execution.
- No external effect.
- No OpenAI or other network call by default.

## What This Demo Proves

The demo proves that Cortex can show its intended product loop safely:

```text
synthetic observation -> firewall/redaction -> temporary evidence -> durable
synthetic memory -> encrypted index -> context pack -> dashboard receipts
```

It does not prove consented real capture. That remains a later milestone behind
explicit user approval, native permission status, pre-write firewall checks, and
separate live-capture tests.
