# Dashboard Gateway Actions

Last updated: 2026-04-30

Benchmark: `DASHBOARD-GATEWAY-ACTIONS-001`

Policy reference: `policy_dashboard_gateway_actions_v1`

This slice connects the static Cortex dashboard action controls to local
gateway action receipts. It is still a preview layer. The dashboard can prepare
read-only gateway calls, but it does not execute mutations, exports, draft skill
runs, capture changes, or external effects.

## Enabled Read-Only Tools

Only these tools may be marked `allowed_gateway_call`:

- `memory.explain`
- `skill.review_candidate`

All other dashboard actions return receipt previews with blocked reasons.

## Blocked By Default

The following classes stay preview-only:

- memory correction;
- memory deletion;
- memory export;
- skill approval;
- skill editing;
- skill rejection;
- draft skill execution;
- any action requiring confirmation;
- any action that mutates state, exports data, or has external effects.

## Receipt Contract

`DashboardGatewayActionReceipt` records:

- dashboard source (`memory_palace` or `skill_forge`);
- gateway tool and target reference;
- required input names and redacted payload preview;
- whether the call is allowed;
- read-only, mutation, data-egress, external-effect, and confirmation flags;
- blocked reasons;
- audit action;
- policy refs and safety notes.

Payload previews are ID-shaped. They do not include memory content, skill
procedure text, raw refs, screenshots, local database data, API responses, or
secret-like values.

## UI Behavior

Buttons in `ui/cortex-dashboard` look up the matching receipt by
`gateway_tool:target_ref`. Allowed read-only actions show a prepared gateway
receipt. Blocked actions show the exact blocked reasons. Both paths say that no
mutation executed.

This gives the product a realistic Agent Gateway surface without quietly adding
write authority.
