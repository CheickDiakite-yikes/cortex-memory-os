# Gateway Postmortem Stress

Last updated: 2026-04-30

`GATEWAY-POSTMORTEM-STRESS-001` hardens the local `outcome.postmortem` gateway
tool under repeated trace/outcome compilation and adversarial caller input.

## Contract

The gateway must:

- compile postmortems only from an exact persisted `trace_id` plus matching
  `outcome_id`, `task_id`, and `agent_id`;
- return counts, safe findings, blocked effects, and policy refs;
- keep runtime event summaries, outcome feedback, and trace prose out of the
  response;
- reject mismatched outcomes without mutation;
- reject unknown trace IDs with a fixed redacted error.

## Redaction Gate

The stress test injects hostile-looking text into runtime event summaries,
outcome feedback, and an unknown trace ID. The output must not echo that text,
`.env.local`, synthetic token markers, or event summaries. Unknown trace errors
return `unknown trace_id` rather than interpolating caller-provided IDs.

This keeps postmortems useful for self-improvement scoring without creating a
new path for prompt injection or private trace text to enter agent context.
