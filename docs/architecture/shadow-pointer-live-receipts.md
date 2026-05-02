# Shadow Pointer Live Receipts

Last updated: 2026-05-02

`SHADOW-POINTER-STATE-MACHINE-001`,
`SHADOW-POINTER-LIVE-RECEIPT-001`, and
`CONSENT-FIRST-ONBOARDING-001` turn the Shadow Pointer into the primary live
trust surface.

## State Machine

`policy_shadow_pointer_state_machine_v1` defines a compact visual contract for
every Shadow Pointer state:

- label and compact label;
- icon and tone;
- pointer shape;
- peripheral cue;
- allowed visual effects;
- blocked privileged effects.

The key UX rule is simple: a user should know whether Cortex is off, observing,
masking, remembering, contexting, paused, or waiting for approval without
opening the full dashboard.

Initial compact state names:

- Off
- Observing
- Private Masking
- Segmenting
- Remembering
- Learning Skill
- Agent Contexting
- Agent Acting
- Needs Approval
- Paused

## Live Receipt

`ShadowPointerLiveReceipt` is the small receipt that should appear in the
cursor-adjacent panel and dashboard rail. It contains only:

- trust class;
- memory eligibility;
- raw-ref status;
- firewall decision;
- evidence write mode;
- policy references.

External browser/OCR/page content remains `external_untrusted`,
memory-ineligible, raw-ref-free, and raw-payload-free. The receipt can say what
happened without copying what the page said. The current synthetic browser path
uses `ephemeral_only` plus `derived_only` evidence handling.

## Consent-First Onboarding

`ConsentFirstOnboardingPlan` starts with a synthetic-only path:

1. show Cortex off;
2. invoke disposable synthetic observation;
3. prove masking/redaction;
4. create a synthetic memory candidate;
5. delete the candidate;
6. show an audit receipt.

This path must not start real screen capture, enable raw storage, write private
durable memory, or perform external effects. It teaches control before asking
for deeper observation.
