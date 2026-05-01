# Synthetic Capture Ladder

Last updated: 2026-05-01

Suite:

- `SYNTHETIC-CAPTURE-LADDER-001`

Policy:

- `policy_synthetic_capture_ladder_v1`

This slice moves beyond the previous control-plane click test without enabling
real screen capture. It proves the first safe end-to-end memory ladder using
only synthetic data and temporary local storage.

## Ladder Rungs

1. Synthetic disposable capture page only.
2. Ephemeral raw ref in temp storage, auto-deleted.
3. Durable synthetic memory write to local test DB with audit.
4. Retrieval/context pack from synthetic memory.
5. Secret-in-screen negative test proving redaction before any write.
6. Consented real screen capture later.

The first five rungs are implemented by
`uv run cortex-synthetic-capture-ladder --json`. The sixth rung remains
explicitly out of scope for this slice.

## What Runs

The runner creates a temporary HTML page containing a synthetic onboarding debug
fixture. That page is treated as a disposable capture source, passed through the
firewall, written to the test Evidence Vault, read once before expiry, and then
expired so the raw ref is removed.

The runner then writes a derived synthetic memory into a local temporary SQLite
database and records a human-visible audit event. It retrieves the memory using
the store search path and asks the local MCP-shaped context-pack compiler for a
context pack that includes the synthetic memory.

No raw payload, local path, screenshot, Accessibility tree, browser tab title,
private file, or real user activity is committed.

## Secret Negative

The runner also creates a synthetic page containing a fake secret marker. The
secret page must be masked by the firewall and blocked before raw evidence or
memory write. The only persisted record for that branch is a redacted audit
summary saying the synthetic secret was replaced with `[REDACTED_SECRET]`.

The contract fails if any of these markers appear after redaction:

- `api_key=`
- `CORTEX_FAKE_TOKEN`
- `sk-`
- `Bearer `
- `raw://`
- `encrypted_blob://`
- `Ignore previous instructions`

## Explicit Non-Goals

This is not a production capture daemon. The valid proof requires:

- real screen capture is off;
- consented real screen capture later;
- raw screen storage is not used;
- raw Accessibility tree storage is not used;
- durable memory is written only to a local temporary test database;
- the raw ref is a vault ref, not a `raw://` ref;
- the raw ref is readable before expiry and deleted after expiry;
- the secret-in-screen branch does not write raw payloads or memory.

The next safe product step is to connect this ladder to permission-status
onboarding and visible Shadow Pointer state, still without enabling real screen
capture by default.
