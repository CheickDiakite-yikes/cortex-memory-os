# macOS Perception Adapter Contracts

Last updated: 2026-04-30

Benchmark: `MACOS-PERCEPTION-ADAPTERS-001`

Policy reference: `policy_macos_perception_adapter_contract_v1`

This slice specifies the first native macOS app/window and Accessibility
adapter boundary. It is a contract layer only: no live screen recording, no
Accessibility daemon, and no background capture are started by this repo.

## Adapter Surfaces

`MacOSAppWindowAdapterEvent` represents consented app/window metadata:

- app name and bundle id;
- optional redacted-safe window title;
- active project scope;
- Screen Recording permission state;
- app allowlist decision;
- derived text ref only.

`MacOSAccessibilityAdapterEvent` represents consented Accessibility metadata:

- focused role and optional label;
- optional value preview only for non-private fields;
- Accessibility permission state;
- app allowlist decision;
- derived text ref only.

Both adapters produce `PerceptionEventEnvelope` records and then pass through
the same Privacy and Safety Firewall plus `EvidenceEligibilityPlan` handoff as
browser and terminal events.

## Consent And Permission Gates

The adapter route is `firewall_required` only when all are true:

- consent state is `active`;
- the relevant macOS permission is `granted`;
- the app is explicitly allowed;
- the observation is not a sensitive app or private Accessibility field.

Otherwise the route is `discard`.

This keeps permission prompts, app allowlists, and private-field detection ahead
of durable evidence. A denied permission, paused consent, blocked app, sensitive
app, or secure text field cannot become memory-eligible.

## Raw Capture Boundary

Raw macOS capture is deliberately forbidden in these contracts:

- app/window events cannot carry `raw_ref`;
- Accessibility events cannot carry `raw_tree_ref`;
- sensitive apps cannot carry window titles;
- private Accessibility fields cannot carry value previews.

Allowed observations can become derived-only evidence. They do not write raw screen frames,
screenshots, raw Accessibility trees, raw private memory, local
databases, vector stores, or logs.

## Source Trust

macOS app/window and Accessibility adapter events are source-trust Class B
local observed data once consent and permissions pass. They are still not
instructions. They are evidence for scene segmentation, Memory Palace review,
and future Shadow Pointer status.

## Failure Behavior

The safe failure mode is quiet discard plus an inspectable receipt:

- no raw refs;
- no derived refs;
- no memory eligibility;
- no model-training eligibility;
- policy refs preserved for audit.

The follow-up slice is to connect these receipts to Shadow Pointer capture
wiring so users can see why Cortex is observing, masking, paused, or blocked.
