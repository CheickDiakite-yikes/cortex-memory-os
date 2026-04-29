# Perception To Firewall Handoff

Last updated: 2026-04-29

`PERCEPTION-FIREWALL-HANDOFF-001` defines how a validated
`PerceptionEventEnvelope` becomes a `FirewallDecisionRecord`.

The handoff exists so native capture adapters cannot accidentally skip consent,
redaction, quarantine, retention, or evidence eligibility checks.

## Handoff Rules

- `discard` route produces a discard firewall decision with no redacted text.
- `ephemeral_only` route produces an ephemeral firewall decision and is never
  memory eligible.
- `firewall_required` route sends extracted text through the existing text
  firewall.
- Envelope `prompt_injection_risk` upgrades the decision to quarantine even when
  text patterns do not match.
- Envelope `third_party_content` blocks direct memory eligibility by downgrading
  otherwise eligible content to ephemeral-only.
- Secret redactions remain non-memory-eligible and keep the secret redaction
  placeholder out of durable text.
- The returned decision keeps the event ID, audit ID shape, and policy refs from
  both the envelope and firewall layer.

## Boundary

The handoff still does not store evidence. It creates the decision consumed by
`EVIDENCE-ELIGIBILITY-HANDOFF-001`, which then decides Evidence Vault raw-write,
metadata-write, retention, and derived-ref eligibility.

## Benchmark Contract

`PERCEPTION-FIREWALL-HANDOFF-001` verifies that:

- secret-like text is redacted when routed from a perception envelope;
- envelope policy refs survive the handoff;
- prompt-injection risk is quarantined even without a text pattern match;
- third-party content remains ephemeral rather than memory eligible;
- this document and the benchmark plan name the handoff contract.
