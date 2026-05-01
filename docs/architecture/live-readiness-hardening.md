# Live Readiness Hardening

Last updated: 2026-05-01

`LIVE-READINESS-HARDENING-001` adds one bounded receipt for live-adjacent
testing. It is a composition harness, not a production capture switch.

## Contract

`uv run cortex-live-readiness --json` verifies:

- `.env.local` is ignored by git and untracked;
- the harness does not read `.env.local` values while checking git hygiene;
- live browser and terminal adapter artifacts still use synthetic adapter payloads only;
- the local adapter endpoint rejects remote clients, trust escalation,
  oversized payloads, raw refs, prompt-injection browser text, and terminal
  secret retention;
- manual adapter proof can run the terminal hook and browser payloads against
  the localhost endpoint;
- no real screen capture starts;
- no durable memory writes happen.

## Optional OpenAI Smoke

`uv run cortex-live-readiness --include-openai --json` includes the existing
OpenAI smoke in dry-run mode. It checks request shape and `store: false`
without making a network call.

`uv run cortex-live-readiness --openai-live --json` performs the synthetic,
low-output OpenAI call and asserts the expected fixed marker. Use this only for
developer live checks, never as a default benchmark gate.

The readiness receipt redacts key material by construction. It returns whether
the OpenAI smoke was skipped, dry-run, or live; model name; whether a response
ID was present; and token count when available. It does not return the local key
or prompt-bearing private data.

Policy reference: `policy_live_readiness_hardening_v1`.
