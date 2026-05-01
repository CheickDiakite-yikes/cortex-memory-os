# Dashboard Live Gateway Runtime

Last updated: 2026-05-01

Benchmarks:

- `DASHBOARD-GATEWAY-RUNTIME-READONLY-001`
- `DASHBOARD-GATEWAY-RUNTIME-BLOCKLIST-001`
- `DASHBOARD-CONTEXT-PACK-LIVE-SUMMARY-001`
- `DASHBOARD-SKILL-REVIEW-LIVE-SUMMARY-001`
- `DASHBOARD-OPS-QUALITY-PANEL-001`
- `DASHBOARD-READONLY-ACTION-LIVE-PROOF-001`

Policy references:

- `policy_dashboard_gateway_runtime_readonly_v1`
- `policy_dashboard_context_pack_summary_v1`
- `policy_dashboard_skill_review_summary_v1`
- `policy_dashboard_ops_quality_panel_v1`
- `policy_dashboard_readonly_action_live_proof_v1`

This slice moves the dashboard from local action previews to a bounded local
gateway runtime proof. The dashboard still does not get write authority. It may
execute only read-only summaries through the same gateway-shaped boundary that
agents will use.

## Read-Only Runtime

`DASHBOARD-GATEWAY-RUNTIME-READONLY-001` allows only:

- `memory.explain`
- `skill.review_candidate`

Both calls return metadata summaries. Memory content, source refs, skill
procedure text, raw refs, screenshots, local database contents, API responses,
and secrets stay redacted. The result is a read-only receipt with no mutation,
no export, no external effect, and no durable memory write.

## Blocklist Before Gateway

`DASHBOARD-GATEWAY-RUNTIME-BLOCKLIST-001` proves unsafe dashboard actions are
blocked before the gateway is called. The blocked tools include:

- `memory.forget`
- `memory.export`
- `skill.execute_draft`

Blocked receipts carry `blocked_before_gateway`, blocked reasons, and the
original risk flags. They do not become tool calls. This keeps delete, export,
draft execution, and future write paths confirmation-gated.

## Context Pack Summary

`DASHBOARD-CONTEXT-PACK-LIVE-SUMMARY-001` exposes a dashboard-safe live
context-pack summary. It is count-only: relevant memory count, retrieval receipt
count, fusion diagnostic count, warning count, blocked memory count, next-step
count, and estimated budget tokens.

The summary has no memory content and source refs redacted. It is meant for
status panels and context/debug lanes, not for injecting hidden context back into
the UI.

## Skill Review Summary

`DASHBOARD-SKILL-REVIEW-LIVE-SUMMARY-001` calls `skill.review_candidate` and
returns counts only: learned-from count, trigger count, procedure step count,
success signal count, failure mode count, confirmation count, risk, maturity,
and execution mode.

The review has no procedure text, performs no mutation, and causes no autonomy change.
Approval, editing, rejection, or draft execution stay separate
confirmation-gated flows.

## Ops Quality Panel

`DASHBOARD-OPS-QUALITY-PANEL-001` exposes benchmark status as aggregate-only
metadata: latest run ID, artifact name, total cases, passed cases, failed cases,
suite count, invalid identifier count, and all-passed state.

The panel includes no raw case payloads, no benchmark evidence payloads, no
artifact body, no hostile text, no raw refs, no secret-like values, and no local
absolute paths.

## Live Proof Receipt

`DASHBOARD-READONLY-ACTION-LIVE-PROOF-001` extends the live browser proof with
sanitized receipt text from a read-only gateway action. A valid live proof may
record text such as:

```text
Gateway receipt allows memory.explain read-only for mem_auth_redirect_root_cause. No mutation executed.
```

The proof stores only the local origin, required visible terms, clicked action
label, and sanitized receipt text. It stores no screenshot, no raw accessibility
tree, no tab titles, no private browser text, no secret values, no raw refs, no
durable memory write, no gateway mutation, and no external effect.

## Runtime Shape

The local proof server uses synthetic dashboard fixtures and an in-memory
gateway service backed by a temporary SQLite store. That keeps the slice
realistic enough to exercise the gateway contract while preserving the current
privacy boundary: no real capture, no private memory, no production database,
and no user secrets.
