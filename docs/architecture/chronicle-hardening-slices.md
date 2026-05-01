# Chronicle Hardening Slices

Last updated: 2026-05-01

This note translates the Codex Chronicle lessons into Cortex contracts without
enabling real capture. The slices below keep screen context useful while making
consent, prompt-injection handling, source routing, budget pressure, retention,
and Memory Palace controls explicit.

## Slice Summary

| Slice | Policy | Contract | Default effect |
| --- | --- | --- | --- |
| `SHADOW-POINTER-PERMISSION-ONBOARDING-001` | `policy_shadow_pointer_permission_onboarding_v1` | Shadow Pointer renders Screen Recording and Accessibility readiness from the native permission smoke result. | Read permission status and render needs-approval state only. No prompts, capture, observers, evidence refs, or memory writes. |
| `SCREEN-INJECTION-STRESS-001` | `policy_screen_injection_stress_v1` | Synthetic OCR, screenshot, browser DOM, and Accessibility text containing hostile instructions plus a fake token must quarantine and redact before any memory or context use. | Hostile visual context is evidence only or quarantined; it never becomes agent instruction. |
| `SOURCE-ROUTER-CONTEXT-PACK-001` | `policy_source_router_context_pack_v1` | Context packs can say a better direct source exists, such as a file, dashboard, doc, thread, or PR, without exposing the source ref or content. | Agents get metadata-only route hints; external and raw-evidence refs are not directly fetchable by default. |
| `CAPTURE-BUDGET-QUEUE-001` | `policy_capture_budget_queue_v1` | Capture consolidation jobs must fit explicit token, cost, job-count, and privacy-pause budgets. | Backpressure defers work; sensitive or paused jobs are skipped before model consolidation. |
| `RAW-EVIDENCE-EXPIRY-HARDENING-001` | `policy_raw_evidence_expiry_hardening_v1` | Raw evidence expiry must work after reopening the vault and return redacted receipts. | Raw refs and blobs are removed; metadata remains for audit/debug. |
| `MEMORY-PALACE-CHRONICLE-CONTROLS-001` | Memory Palace flow contract | Chronicle-style controls cover pause, delete recent observation, explain observation source, and scope observation-derived influence. | Users can inspect and reduce observation influence without rendering raw screen, OCR, DOM, or Accessibility content. |

Control audit action names include `pause_observation`,
`delete_recent_observation`, `explain_observation_source`, and
`scope_observation_memory_influence`.

## Operating Boundaries

- These slices are synthetic and contract-level. They do not enable consented
  real screen capture.
- Permission onboarding stops at `needs_approval` even when permissions are
  already available.
- Screen content is untrusted input. Strings such as "ignore previous
  instructions" can be stored as hostile fixtures in tests, but cannot become
  memory guidance or agent instructions.
- Source routing is metadata-only. It may recommend a direct connector/source
  type, but target refs and content stay redacted inside the route hint.
- Capture consolidation is budgeted before model calls. Privacy pause blocks
  the queue before any background consolidation.
- Raw evidence expiry receipts prove deletion without copying raw bytes into
  logs, benchmarks, context packs, or docs.

## Next Gate Before Real Capture

Before consented real screen capture, Cortex still needs:

- a visible native onboarding panel fed by
  `SHADOW-POINTER-PERMISSION-ONBOARDING-001`;
- a production cipher/key-management path for sensitive durable memory;
- user-facing Memory Palace controls wired to the live dashboard and gateway;
- a consent dialog that names retention, source classes, pause/delete controls,
  and prompt-injection risk in plain language;
- a default-off real capture daemon with audit receipts and rollback.
