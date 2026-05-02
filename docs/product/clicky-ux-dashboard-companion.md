# Clicky-Inspired Cursor Companion

Benchmarks:

- `CLICKY-UX-LESSONS-001`
- `CLICKY-UX-COMPANION-001`

Policies:

- `policy_clicky_ux_lessons_v1`
- `policy_clicky_ux_companion_v1`

Source studied read-only: https://github.com/farzaa/clicky

Clicky reinforced an important UX lesson for Cortex: the live assistant should
feel cursor-adjacent, not dashboard-first. The dashboard remains a review and
correction surface; the Shadow Pointer is the live trust surface.

## Adapted Patterns

- Cursor-adjacent presence: show a tiny, readable companion state near the task.
- Compact receipt panel: expose state, trust, memory eligibility, and raw-ref
  status in one short surface.
- Visible spatial pointing: point/highlight proposals must be display-only until
  policy and consent authorize anything else.
- Onboarding by demonstration: teach safety through synthetic observe, mask,
  candidate memory, delete, and audit steps.

## Not Borrowed

- No raw transcript analytics.
- No direct text-to-click actions.
- No hardcoded remote proxy for privileged memory flows.
- No external repo code, setup command, package install, Xcode build, API call,
  or worker deployment was executed.

## UI Contract

The dashboard shows `Cursor Companion` inside the live rail and keeps the copy
short:

```text
State | Trust | Memory | Raw refs
```

The companion can render the cursor-adjacent receipt or open a compact receipt
panel. It cannot start screen capture, start microphone capture, execute clicks,
type text, write memory, export payloads, or send data to a remote proxy.
