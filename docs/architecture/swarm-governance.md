# Swarm Governance

Last updated: 2026-04-29

`SWARM-GOVERNANCE-001` defines the first safe boundary for future multi-agent
orchestration.

The purpose is not to launch agents yet. The purpose is to make delegation
bounded before real parallel execution exists.

Policy ref: `policy_swarm_governance_v1`.

## Plan Contract

A `SwarmPlan` contains:

- coordinator agent ID;
- task specs;
- shared context refs;
- aggregate budget ceilings;
- cancellation token;
- policy refs.

Task IDs must be unique. Dependencies must point to tasks inside the same plan.
Every task uses the plan cancellation token.

## Task Contract

A `SwarmTaskSpec` contains:

- agent ID and role;
- task goal;
- source trust;
- allowed and blocked source refs;
- read and write scopes;
- per-task budget;
- cancellation token;
- source isolation marker;
- redaction marker.

Allowed source refs must be explicit. Wildcard, global, or all-source access is
rejected. Blocked source refs override allowed access. Reviewer and observer
roles cannot write.

## Budget Enforcement

Swarm task budgets include:

- prompt tokens;
- tool calls;
- wall-clock time;
- artifacts;
- max action risk;
- autonomy ceiling.

High-risk and critical task budgets are rejected. Bounded autonomy and recurring
automation are rejected. Aggregate plan evaluation blocks the whole swarm if
prompt, tool, or time ceilings are exceeded.

## Source Isolation

Source isolation means each worker receives only its own source refs and compact
shared refs. A worker cannot read a source ref merely because another worker can.

Access decisions return:

- `source_in_task_scope`;
- `source_explicitly_blocked`;
- `source_outside_task_isolation`.

This keeps untrusted pages, documents, benchmark prompts, and model outputs from
cross-contaminating unrelated tasks.

## Write Scope

Concurrent write scopes must be disjoint. This is intentionally conservative.
Future merge protocols may add coordination, but the MVP blocks overlapping
writes before execution.

## Cancellation

Cancellation is plan-wide. A `SwarmCancellationReceipt` lists cancelled task IDs,
preserved audit refs, and confirms that external effects are not allowed after
cancel.

## Benchmark

`SWARM-GOVERNANCE-001` verifies:

- source isolation;
- budget enforcement;
- disjoint write scopes;
- cancellation receipts;
- non-autonomous execution ceilings;
- audit policy refs.
