# ADR 0001: Engineering Control Plane

Status: Accepted

Date: 2026-04-27

## Context

Cortex Memory OS is starting as a new workspace for a security-sensitive memory substrate for AI agents and later robots. The project needs durable reminders for prompt-injection resistance, safe research, progress tracking, benchmarks, and debugging before implementation begins.

## Decision

Use a lightweight markdown control plane:

- `AGENTS.md` for persistent agent instructions and safety posture.
- `docs/ops/task-board.md` for task status and evidence.
- `docs/ops/research-safety.md` for trusted-source rules and source logging.
- `docs/ops/benchmark-registry.md` for planned and completed benchmarks.
- `docs/ops/debug-journal.md` for reproducible failures and fixes.
- `docs/adr/` for architecture decisions.

## Consequences

- Progress remains inspectable without requiring a task database or external SaaS.
- Future agents can recover context quickly.
- Safety and benchmarking stay part of normal development rather than an afterthought.
- The system is intentionally manual until real workflow needs justify automation.

## Alternatives Considered

- External issue tracker: too early and less local-first.
- Single large planning document: simpler, but it becomes hard to scan and update.
- Code-first scaffold: premature before ingesting the user's plans and skeletons.

## Verification Plan

- Keep `task-board.md` current at the start and end of each work slice.
- Convert repeated failures into entries in `debug-journal.md` and then benchmark cases.
- Add ADRs whenever a design choice affects storage, safety, trust boundaries, or robot-facing behavior.

