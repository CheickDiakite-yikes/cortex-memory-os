# Retrieval Explanation Receipts

Last updated: 2026-04-30

Suite: `RETRIEVAL-EXPLANATION-RECEIPTS-001`  
Policy: `policy_retrieval_explanation_receipts_v1`

## Purpose

Retrieval explanation receipts make context-pack selection inspectable without
copying hidden memory content, raw evidence, or source refs into an explanation
surface.

The receipt answers:

```text
Was this memory included, cited as evidence only, or excluded?
Which safe scoring/policy reasons explain that decision?
How much provenance exists, without exposing the provenance itself?
```

It does not answer by showing the memory text.

## Receipt Shape

Each `RetrievalExplanationReceipt` includes:

- memory ID;
- decision: `included`, `evidence_only`, or `excluded`;
- rank for included memories;
- retrieval score;
- reason tags;
- source ref count;
- content redacted marker;
- source refs redacted marker;
- policy refs.

The receipt forbids content inclusion and requires source refs redacted. This is
deliberate because source refs can themselves reveal private project names,
third-party URLs, local paths, or evidence handles.

## Included Receipts

Included memories receive safe positive reason tags such as:

- `query_overlap`;
- `confidence`;
- `source_trust`;
- `recency`.

These tags explain why the memory was useful without reproducing the memory.

## Evidence-Only And Excluded Receipts

Untrusted external memories can be marked `evidence_only` when Cortex may cite
their evidence refs separately but must not promote their text into memory or
agent instructions.

Blocked memories can be marked `excluded` with policy reason tags. Examples:

- `external_evidence_only`;
- `secret_blocked`;
- retrieval scope mismatch tags;
- lifecycle status tags.

All of these remain content redacted and source refs redacted.

## Context-Pack Integration

`memory.get_context_pack` now includes `retrieval_explanation_receipts`
alongside `retrieval_scores`.

Receipts are for inspection, UI display, debugging, and audit trails. They are
not instructions to the agent and do not authorize broader access to memory.

## Verification

`RETRIEVAL-EXPLANATION-RECEIPTS-001` checks that:

- included context memories receive ranked receipts;
- external evidence receives an `evidence_only` receipt;
- hostile text is not echoed into receipt payloads;
- source refs are counted but not revealed;
- content stays redacted;
- `policy_retrieval_explanation_receipts_v1` is present in context policy refs.
