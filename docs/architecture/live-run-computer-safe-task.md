# Live Run Computer Safe Task

Last updated: 2026-05-01

Suite:

- `LIVE-RUN-COMPUTER-SAFE-TASK-001`

Policy:

- `policy_live_run_computer_safe_task_v1`

This slice proves a bounded "Cortex is running" path without turning the
workspace into a real recorder. The operator may start the local dashboard,
serve it on localhost, and use Computer Use for a safe localhost task such as
clicking a read-only `memory.explain` dashboard action.

The proof is intentionally a receipt contract, not an autonomous capture loop.
Computer Use can inspect the Chrome window during the live test, but Cortex
stores only a sanitized receipt that says which local surface was exercised and
which risky systems stayed off.

## Allowed On Surfaces

- Local static dashboard server on `127.0.0.1`.
- Local dashboard gateway runtime receipts.
- Computer Use interaction with a safe localhost task.
- Read-only gateway calls for `memory.explain` and `skill.review_candidate`.
- Blocked receipts for mutation, export, draft execution, and external-effect
  controls.

## Required Off Surfaces

The safe live run is valid only when all of these are true:

- real capture off;
- durable memory write off;
- raw screen storage off;
- raw Accessibility tree storage off;
- raw evidence ref creation off;
- model secret echo attempts off;
- mutation/export/draft execution off;
- external network egress and external effects off.

This distinction matters for user trust. The dashboard can be "running" while
the privacy-sensitive product surfaces remain disabled. A valid live run proves
that the visible local control plane can be inspected without creating durable
private memory.

## Receipt Shape

The CLI runner is:

```bash
uv run cortex-live-run-safe-task --json
```

The default sample validates:

- localhost dashboard URL;
- sanitized dashboard live observation;
- Computer Use task observed flag;
- read-only gateway runtime execution count;
- blocked unsafe gateway receipt count;
- zero failed gateway calls;
- zero raw payloads;
- zero prohibited markers such as secret-looking values, raw refs, or injected
  instructions.

The runner must never call Computer Use directly, start ScreenCaptureKit,
attach an Accessibility observer, read browser profiles, call GPT with secret
values, save screenshots, save raw Accessibility trees, create evidence refs,
write durable memories, export memory, execute draft skills, or perform
external effects.

## Failure Modes

The proof fails closed if:

- the dashboard URL is not local;
- the static dashboard server was not running;
- the gateway runtime was not checked;
- Computer Use did not perform the safe local task;
- the dashboard live proof fails;
- no read-only gateway receipt executed;
- no unsafe receipt was blocked before gateway execution;
- any gateway result returns raw payloads;
- any mutation, export, draft execution, raw ref, real capture, durable memory
  write, model secret echo attempt, or external effect flag is enabled;
- the sanitized receipt includes secret-like, raw-ref, or prompt-injection
  markers.

## Product Boundary

This is a live-running proof for the control plane, not a claim that production
memory capture is enabled. Real screen capture, durable memory writes, raw refs,
and autonomous skill execution remain future work behind consent, encryption,
audit, revocation, and rollback gates.
