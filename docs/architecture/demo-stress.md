# Bounded Live Stress Demo

Benchmark: `DEMO-STRESS-001`

Policy reference: `policy_demo_stress_v1`

This slice adds a bounded live stress demo for Cortex Memory OS. It is live in
the sense that it repeatedly runs the current localhost-safe demo surfaces and
runtime receipts. It is not live capture.

The command is:

```bash
uv run cortex-demo-stress --iterations 12 --json
```

## Loop

Each iteration composes three existing safe lanes:

1. `DEMO-READINESS-001` verifies the dashboard smoke, synthetic capture ladder,
   encrypted index, context pack, and `.env.local` git hygiene.
2. `SCREEN-INJECTION-STRESS-001` sends hostile OCR, screenshot, browser DOM,
   and Accessibility fixtures through the firewall and context-pack boundary.
3. Dashboard gateway receipts execute only read-only local calls and block
   mutation, export, and draft execution before the gateway.

The default loop uses 12 iterations and caps at 50 iterations so the demo can
stress the contracts without turning into a runaway background job.

## Safety Boundary

The receipt must prove:

- synthetic-only;
- localhost-only;
- No real screen capture;
- No durable raw screen storage;
- No raw private refs;
- No secret echo;
- No model secret echo attempt;
- No mutation, export, or draft execution;
- no external effect;
- no raw payloads returned from dashboard gateway receipts;
- no prohibited markers in the stress receipt.

The stress demo reads only `.env.local` git hygiene metadata through the
existing live-readiness helper. It does not read local secret values.

## Why This Exists

`DEMO-READINESS-001` proves one clean demo pass. `DEMO-STRESS-001` proves the
same path can be repeated under pressure while preserving the safety boundary.
That gives us a better pre-demo check before we ever consider consented real
screen capture.
