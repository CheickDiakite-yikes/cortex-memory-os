# Dashboard Live Proof

Last updated: 2026-05-01

Benchmarks:

- `COMPUTER-DASHBOARD-LIVE-PROOF-001`
- `DASHBOARD-READONLY-ACTION-LIVE-PROOF-001`

Policy references:

- `policy_computer_dashboard_live_proof_v1`
- `policy_dashboard_readonly_action_live_proof_v1`

This slice adds a safe proof boundary for using Computer Use to validate the
local Cortex dashboard in a real desktop browser.

The proof is deliberately not a screenshot archive and not a raw Accessibility
dump. Computer Use can inspect the real Chrome window, but the repo stores only
a `SanitizedDashboardLiveObservation`: local URL, page title, required visible
dashboard terms, clicked control label, and the resulting local preview receipt.

## Required Visible Terms

The proof must confirm that the real browser surface shows:

- `Cortex Memory OS`
- `Shadow Pointer`
- `Memory Palace Review Queue`
- `Skill Forge Candidate Workflows`
- `Safety Firewall`
- `Pause Observation`
- `Recent Safe Receipts`

This keeps the proof tied to the product surface the user sees, not only to a
backend smoke test.

## Action Receipt Gate

At least one visible action must be clicked in the real browser. For the current
proof, Computer Use clicked `Pause Observation` and the page showed:

```text
Observation pause previewed locally. Confirmation and audit receipt required.
```

That is a local preview receipt. It is not a memory mutation, not a durable
write, not a capture-start command, not a gateway mutation, and not an external
effect.

## Read-Only Gateway Action Receipt

`DASHBOARD-READONLY-ACTION-LIVE-PROOF-001` extends the proof with a sanitized
read-only gateway receipt. The browser proof may record only sanitized receipt
text such as:

```text
Gateway receipt allows memory.explain read-only for mem_auth_redirect_root_cause. No mutation executed.
```

The receipt must include `Gateway receipt allows`, `read-only`, and
`No mutation executed`. It must not mention `memory.forget`, `memory.export`,
`skill.execute_draft`, raw refs, screenshots, secrets, durable writes, gateway
mutations, or external effects.

## Redaction Boundary

The proof fails if sanitized observations report any of these:

- raw screenshot saved;
- raw accessibility tree saved;
- raw tab titles saved;
- raw private text saved;
- secret values recorded;
- raw refs recorded;
- durable memory write;
- gateway mutation;
- external effect;
- prompt-injection instruction followed.

The proof also rejects secret-like and hostile markers such as
`OPENAI_API_KEY=`, `sk-`, `raw://`, `encrypted_blob://`, and
`Ignore previous instructions`.

## Locality Boundary

The proof accepts only `localhost`, `127.0.0.1`, or `::1` dashboard origins.
External pages, screenshots, READMEs, emails, and web content remain untrusted
evidence. They cannot supply approval to click, mutate, export, send data, or
write memory.

## Runner

The repeatable runner is:

```bash
uv run cortex-dashboard-live-proof --json
```

By default it validates a commit-safe sample observation matching the current
Computer Use proof shape. A future operator can pass `--observation-json` with
a manually redacted observation object after a new live browser check.

The runner must never call Computer Use directly, read browser profiles, store
screenshots, echo local tabs, read `.env.local`, start real capture, or write
durable memory.
