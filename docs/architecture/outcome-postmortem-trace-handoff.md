# Outcome Postmortem Trace Handoff

`OUTCOME-POSTMORTEM-TRACE-001` connects persisted agent runtime traces to
outcome postmortems without turning trace prose into new instructions.

## Contract

The compiler accepts:

- a validated `AgentRuntimeTrace`;
- a matching `OutcomeRecord`;
- optional creation time for deterministic tests.

It emits an `OutcomePostmortem` that includes safe trace metadata only:

- counts for events, tool calls, shell actions, browser actions, artifacts,
  approvals, retries, and external effects;
- highest observed risk;
- evidence reference counts;
- fixed safe finding tags such as `retry_observed` and `high_risk_observed`;
- follow-up task IDs for human review.

It does not emit runtime event summaries, trace goal text, tool arguments, raw
artifact refs, private memory, model output, terminal output, browser text, or
new self-lesson content.

## Safety Boundary

The postmortem is a review artifact, not an autonomous improvement primitive.
It can point at follow-up tasks, but it cannot promote memories, create active
self-lessons, change Skill Forge maturity, or expand permissions.

Required markers:

- `summary_text_redacted: true`
- `event_summaries_included: false`
- `content_redacted: true`
- `policy_outcome_postmortem_trace_v1`

The implementation rejects mismatched trace/outcome task or agent IDs so one
agent's trace cannot be attached to another agent's outcome.

## Product Use

This is the handoff between Agent Runtime Trace and the Self-Improvement Engine.
It gives Cortex enough structured evidence to ask, "what should we inspect
next?" while keeping hostile browser pages, terminal logs, and event summaries
out of agent instruction lanes.
