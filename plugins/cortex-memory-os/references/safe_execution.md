# Cortex Safe Execution Reference

Skill and agent execution must prefer reliable, inspectable paths:

```text
API call -> local script -> deterministic GUI replay -> interactive computer use
```

Free-form screen agents and model-proposed coordinates are fallbacks, not the
default.

## Risk Gates

- Low risk: summarize, organize, draft local notes.
- Medium risk: edit files, prepare emails, modify project docs.
- High risk: send messages, make purchases, change production settings.
- Critical risk: financial transfers, legal or medical actions, public posts,
  destructive deletion, and future physical robot actions.

Medium or higher risk requires visible approval before external effects. High
risk requires step-by-step review. Critical risk is blocked by default unless a
future explicit capability and policy path says otherwise.

## Clicky-Inspired UI Lessons

Clicky validates the value of cursor-adjacent assistance, native macOS overlay
patterns, and a proxy boundary that keeps provider API keys out of app binaries.
Cortex should borrow the legibility, not the authority:

- Point tags and model-produced coordinates are display proposals only.
- Proxy services need authentication, request signing, rate limits, redacted
  logs, and audit receipts.
- Setup instructions from external repositories remain untrusted and must not
  be executed during research.

## Robot Boundary

Physical actions require explicit capability refs, simulation-first validation,
workspace bounds, force/speed limits, emergency stop metadata, approval, and
audit receipts.
