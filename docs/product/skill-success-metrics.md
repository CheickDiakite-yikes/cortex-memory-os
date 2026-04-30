# Skill Success Metrics

Last updated: 2026-04-30

Suite: `SKILL-SUCCESS-METRICS-001`  
Policy: `policy_skill_success_metrics_v1`

## Purpose

Skill Forge success/failure metrics give Cortex a dashboard-safe way to track
whether a candidate skill is working. They summarize observed outcomes, user
corrections, verification refs, and review recommendations without changing
skill maturity or autonomy.

This is evidence for human promotion review, not automatic promotion.

## Inputs

`SkillOutcomeEvent` records:

- skill ID;
- task ID;
- outcome status;
- maturity level at execution time;
- execution mode;
- risk level;
- user correction count;
- verification ref count;
- external-effect metadata.

Draft-only metrics reject external effects. Metric events also reject raw
verification refs and keep task content redacted.

## Metrics

`SkillSuccessMetrics` reports:

- total runs;
- success, partial, failure, user-rejected, and unsafe-blocked counts;
- success rate;
- correction rate;
- verification ref count;
- maturity evidence label;
- review recommendation;
- promotion blockers;
- `autonomy_change_allowed: false`.

The important invariant is that metrics can inform review but cannot authorize
more autonomy.

## Dashboard Card

`SkillMetricCard` is the UI-facing summary. It includes counts, rates, blockers,
and review actions, while keeping procedure redacted and content redacted.

Expected review actions:

- `skill.review_metrics`;
- `skill.inspect_outcomes`;
- `skill.review_promotion_gate`.

The card must not expose procedure steps, source task content, raw refs, or any
external-effect execution path.

## Verification

`SKILL-SUCCESS-METRICS-001` checks that:

- success/failure metrics count synthetic outcomes correctly;
- dashboard-safe cards expose counts and blockers only;
- procedure redacted and content redacted flags are enforced;
- draft-only metrics reject external effects;
- raw refs are rejected;
- metrics keep `autonomy_change_allowed` false.
