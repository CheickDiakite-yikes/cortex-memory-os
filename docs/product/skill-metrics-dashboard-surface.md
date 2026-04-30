# Skill Metrics Dashboard Surface

`SKILL-METRICS-DASHBOARD-SURFACE-001` makes Skill Forge outcome metrics visible
in the dashboard without exposing procedure text or changing autonomy.

## Surface

The dashboard now carries a `skill_metrics` view model with one
`SkillMetricCard` per visible skill. Each card shows:

- total runs;
- success rate;
- correction rate;
- verification reference count;
- review recommendation;
- promotion blockers.

It does not include skill procedure steps, task content, raw verification refs,
or outcome prose.

## Safety Rules

Required redaction and control markers:

- `procedure_text_included: false`
- `task_content_included: false`
- `content_redacted: true`
- `autonomy_change_allowed: false`
- `policy_skill_metrics_dashboard_surface_v1`
- `policy_skill_success_metrics_v1`

Dashboard metrics are observational. They can tell a reviewer that a skill has
evidence, failures, corrections, or safety blocks, but they cannot approve a
skill, promote maturity, execute a draft, or enable autonomy.

## UI Behavior

Skill cards render a compact `Skill Metrics` strip with run counts, success
rate, correction rate, and review recommendation. The existing gateway action
receipt layer still controls all review and mutation paths.

For the static shell fixture, procedure previews are stripped before writing
`dashboard-data.js`; the dashboard keeps procedure counts and blockers, not the
workflow steps themselves.
