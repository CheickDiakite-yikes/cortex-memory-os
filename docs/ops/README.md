# Engineering Operations

This folder is the project control plane. Keep it boring, current, and useful.

## Files

- `task-board.md`: canonical task status, next work, and evidence.
- `research-safety.md`: source rules, prompt-injection defenses, and research ledger.
- `benchmark-registry.md`: benchmark inventory, gates, and run log.
- `benchmark-plan.md`: runnable benchmark commands, release blockers, and expansion roadmap.
- `debug-journal.md`: reproducible failures, root causes, and fixes.
- `../adr/`: architecture decision records.

## Standard Slice Flow

1. Pick one task from `task-board.md` or add a new one.
2. Define the proof: test, benchmark, review, or manual verification.
3. Make the smallest coherent change.
4. Run the proof.
5. Update the task with evidence and follow-ups.

## Status Values

- `Backlog`: useful, not selected.
- `Next`: ready to work soon.
- `Active`: currently being worked.
- `Blocked`: cannot move without a decision, asset, or external dependency.
- `Done`: completed with evidence.
- `Dropped`: intentionally abandoned with a reason.

## Evidence Standard

Every `Done` task should name at least one of:

- File or doc added.
- Command or benchmark run.
- Manual verification performed.
- Decision record created.
- Follow-up task filed.
