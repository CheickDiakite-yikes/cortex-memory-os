# Evidence Eligibility Handoff

Last updated: 2026-04-29

`EVIDENCE-ELIGIBILITY-HANDOFF-001` defines how a
`FirewallDecisionRecord` becomes an Evidence Vault write plan.

The handoff exists so the vault does not infer safety from raw capture state.
The Privacy + Safety Firewall decides whether content is discard, quarantine,
masked, ephemeral, or memory eligible. The Evidence Eligibility Handoff turns
that decision into a narrow `EvidenceEligibilityPlan` with explicit raw-write,
metadata-write, retention, derived-ref, and memory-eligibility fields.

## Write Modes

| Mode | Raw blob write | Derived refs | Memory eligible | Default use |
| --- | --- | --- | --- | --- |
| `discard` | No | No | No | Discarded or quarantined observations. |
| `metadata_only` | No | No | No | Receipts for unsafe or ref-less observations. |
| `derived_only` | No | Yes | Usually no | Masked text or ephemeral third-party content. |
| `raw_and_derived` | Yes | Optional | Yes | Benign local/user-confirmed observations after firewall approval. |

## Handoff Rules

- `memory_eligible` firewall decisions may write raw only when the perception
  envelope still has an active raw ref.
- `mask` decisions must drop raw refs and can keep only a redacted derived ref.
- `ephemeral_only` decisions must drop raw refs, preserve derived refs only for
  ephemeral handling, and stay non-memory-eligible.
- `discard` and `quarantine` decisions must drop raw and derived refs and use
  discard retention.
- Secret sensitivity blocks memory eligibility and raw writes even if another
  field is mis-set upstream.
- Third-party content blocks memory eligibility and raw writes even when the
  source text looks benign.
- `eligible_for_model_training` is always false in the MVP.
- Policy refs from the envelope, firewall, and handoff are deduplicated and
  preserved for audits.

## Evidence Vault Boundary

The handoff does not write bytes by itself. It produces a plan:

- raw-allowed plans can call `EvidenceVault.store(...)`;
- non-raw plans must call `EvidenceVault.store_metadata_only(...)`;
- consumers should never pass a raw payload to the vault when
  `raw_blob_write_allowed` is false.

This keeps the vault boring and auditable: it stores exactly what the plan says
is allowed, instead of reclassifying observed content.

## Benchmark Contract

`EVIDENCE-ELIGIBILITY-HANDOFF-001` verifies that:

- benign local observations become raw-and-derived evidence plans;
- secret-masked observations drop raw refs and keep only redacted derived refs;
- prompt-injection quarantine drops raw and derived refs;
- third-party content remains derived-only or metadata-only and cannot become
  memory eligible;
- metadata-only vault writes never create raw blobs.
