# Gateway Outcome Postmortem

Task: `GATEWAY-OUTCOME-POSTMORTEM-001`

## Decision

The local gateway exposes `outcome.postmortem` as a metadata-only bridge from a
persisted runtime trace to an outcome postmortem.

The tool requires:

- exact `trace_id`
- exact `outcome_id`
- structured `outcome` payload

The provided `outcome_id` must match the `outcome.outcome_id`, and the outcome
payload must match the persisted trace task and agent through the existing
postmortem compiler.

## Returned Shape

The tool returns the existing redacted postmortem contract plus gateway metadata:

- `content_redacted: true`
- policy refs including `policy_gateway_outcome_postmortem_v1` and
  `policy_outcome_postmortem_trace_v1`
- allowed effect: `compile_redacted_outcome_postmortem`
- blocked effects including `copy_runtime_event_summary_text`,
  `promote_trace_text_to_instruction`, `change_skill_maturity`, and
  `create_active_self_lesson`

## Safety Boundary

The gateway does not return runtime event summary text. It does not promote
self-lessons, update Skill Forge maturity, rewrite policy, or turn trace text
into instructions. Follow-up task IDs remain review-only metadata.

## Verification

The benchmark checks that `outcome.postmortem`:

- compiles from a stored trace
- requires exact trace and outcome IDs
- preserves `summary_text_redacted`
- excludes event summaries and hostile text
- returns policy refs and blocked effects
