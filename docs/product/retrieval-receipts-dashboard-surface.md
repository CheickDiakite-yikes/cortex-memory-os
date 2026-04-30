# Retrieval Receipts Dashboard Surface

`RETRIEVAL-RECEIPTS-DASHBOARD-SURFACE-001` makes context retrieval decisions
visible in the dashboard without exposing memory content, source refs, or
hostile text.

## Surface

The dashboard now carries a `retrieval_debug` view model with
`RetrievalReceiptCard` entries derived from `RetrievalExplanationReceipt`
objects.

Each card may show:

- memory ID;
- decision: included, evidence-only, or excluded;
- rank when included;
- score;
- reason tags;
- source reference count.

It must not show memory content, source refs, webpage text, terminal text,
prompt-injection strings, or raw evidence refs.

## Safety Rules

Required markers:

- `content_redacted: true`
- `source_refs_redacted: true`
- `hostile_text_included: false`
- `policy_retrieval_receipts_dashboard_v1`
- `policy_retrieval_explanation_receipts_v1`

This surface explains retrieval. It does not change ranking, expand retrieval
scope, promote external evidence, or convert evidence-only text into agent
instructions.

## UI Behavior

The dashboard receipt rail includes a `Retrieval Receipts` section next to safe
receipts and gateway action receipts. It renders decision status and counts, not
the source material behind those decisions.
