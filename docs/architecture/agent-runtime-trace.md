# Agent Runtime Trace

Benchmark: `RUNTIME-TRACE-001`
Gateway persistence benchmark: `GATEWAY-TRACE-PERSISTENCE-001`

An agent runtime trace records what an agent did during a task. It is evidence
for memory compilation, skill improvement, debugging, and audit. It is not a
raw transcript dump and it is not an instruction channel.

## Purpose

The trace captures:

- tool calls;
- shell actions;
- browser actions;
- artifacts created;
- approval requests and grants;
- retries and failures;
- outcome checks.

This gives Cortex a durable way to answer:

- What did the agent touch?
- What was approved?
- Which evidence proved success or failure?
- Which retry fixed the issue?
- Which artifacts were produced?
- Did untrusted browser or external content stay quarantined as data?

## Event Contract

Every runtime event has:

- stable `event_id`;
- monotonic sequence and timestamp;
- kind and status;
- actor;
- redacted summary;
- source trust class;
- risk level;
- effects such as local read, local write, network call, data egress, or
  destructive action;
- evidence refs and artifact refs;
- policy refs.

Medium-risk, high-risk, critical, data-egress, destructive, and external-effect
events require an approval reference unless they are blocked or are the approval
event itself.

Browser and shell actions use refs such as `browser:local-route-redacted` and
`shell:pytest-onboarding` instead of embedding raw command output or page text.

## Trace Contract

The full trace verifies:

- event IDs are unique;
- sequence numbers are strictly ordered;
- timestamps are monotonic and bounded by trace start/end;
- retries reference existing events;
- approval refs point to prior approval-granted events;
- artifacts reference existing creator events;
- successful traces include a succeeded outcome check.

## Safety

External or hostile content can appear only as redacted evidence refs. Runtime
summaries cannot echo prompt-injection phrases such as "ignore previous".

The trace can be used by memory and skill systems as evidence, but the event
summaries, external refs, browser refs, and artifact refs must never be promoted
as instructions without a separate trust decision.

## Gateway Persistence

`GATEWAY-TRACE-PERSISTENCE-001` persists validated `AgentRuntimeTrace` objects
through the local gateway and SQLite store under
`policy_gateway_runtime_trace_persistence_v1`.

The gateway tools are:

- `runtime_trace.record`: validates and stores a redacted trace, then returns a
  persistence receipt;
- `runtime_trace.get`: returns safe metadata for one stored trace;
- `runtime_trace.list`: returns safe metadata for stored traces filtered by
  agent or task.

The returned metadata includes IDs, counts, risk/outcome status, event kinds,
event statuses, artifact IDs, evidence refs, and policy refs. It intentionally
does not return event summary text by default. The receipt allows only
`persist_redacted_runtime_trace` and blocks summary-text return, unredacted
hostile content storage, and promotion of external text into instructions.

## Validation

`RUNTIME-TRACE-001` validates:

- the fixture includes tool, shell, browser, artifact, approval, retry, blocked
  hostile, and outcome-check events;
- unapproved medium-risk or data-egress events fail validation;
- unredacted hostile browser content fails validation;
- retry, ordering, artifact, and outcome consistency are enforced;
- gateway record/get/list tools persist and return safe metadata without event
  summary text;
- benchmark and product traceability docs keep this surface visible.
