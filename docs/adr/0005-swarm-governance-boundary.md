# ADR 0005: Swarm Governance Boundary

Status: Accepted

Date: 2026-04-29

## Context

Cortex will eventually coordinate multiple agents. Parallel agents can improve
research, review, and implementation throughput, but they also multiply risk:
source contamination, duplicated writes, runaway tool use, hidden autonomy,
unclear cancellation, and audit gaps.

The frontier-agent research notes already point toward multi-agent systems, but
Cortex should not treat "more agents" as permission to widen memory access or
tool authority.

## Decision

Introduce `SWARM-GOVERNANCE-001` as a contract boundary before any real swarm
execution.

Every swarm plan must define:

- explicit task IDs and dependencies;
- explicit source isolation per task;
- budget enforcement for prompt tokens, tools, wall-clock time, and artifacts;
- non-autonomous task ceilings;
- disjoint write scopes;
- a shared cancellation token;
- audit-required governance and cancellation receipts.

The policy reference is `policy_swarm_governance_v1`.

## Consequences

- Parallel work can be planned without giving every agent global memory access.
- Source refs stay scoped to each task rather than leaking through shared prose.
- High-risk, critical, bounded-autonomy, and recurring-automation swarm work is
  blocked at the contract layer.
- A user cancellation can stop all planned tasks through one token and preserve
  audit refs for review.
- Workers cannot write the same scope in parallel unless a future merge protocol
  explicitly authorizes it.

## Alternatives Considered

- Let a coordinator prompt manage all constraints in natural language: rejected
  because prompt text is too brittle for safety-sensitive orchestration.
- Share one large context pack across all workers: rejected because it defeats
  source isolation and increases prompt-injection blast radius.
- Defer swarm governance until real agents exist: rejected because later
  hardening would be harder once workflows depend on loose coordination.

## Verification Plan

- `tests/test_swarm_governance.py` validates source access decisions, budget
  denial, cancellation receipts, write-scope conflicts, and autonomy rejection.
- `SWARM-GOVERNANCE-001` verifies the same boundary in the benchmark harness and
  checks that docs keep source isolation, cancellation, budget enforcement, and
  disjoint write scopes visible.
