# Hybrid Context Fusion Index

Last updated: 2026-04-30

Suite: `CONTEXT-FUSION-INDEX-STUB-001`  
Policy: `policy_hybrid_context_fusion_index_v1`

## Purpose

The hybrid context fusion index is the stable dependency-free seam between
retrieval backends and context-pack compilation. It lets Cortex combine
semantic, sparse, graph, recency, and trust signals before we add heavier
vector, keyword, or temporal graph index dependencies.

This is an interface and safety contract first, not a production retrieval
engine. The current implementation does not call the network, create
embeddings, run external index code, or store raw content.

## Inputs

`HybridIndexCandidate` accepts already-governed memory candidates with:

- memory ID;
- optional safe internal preview;
- semantic, sparse, graph, recency, and trust scores;
- source refs;
- privacy risk;
- prompt_injection_risk;
- staleness and contradiction penalties;
- required policy refs.

Candidates reject `raw://` refs and must include
`policy_hybrid_context_fusion_index_v1`.

## Fusion Rule

The fusion stub computes a weighted score:

```text
weighted semantic/sparse/graph/recency/trust
- privacy risk penalty
- prompt-injection risk penalty
- staleness penalty
- contradiction penalty
```

Candidates above the score threshold can be included only if they do not cross
the high-risk gates. Prompt-risk and high-privacy candidates are returned as
excluded diagnostics, not context instructions.

## Outputs

`HybridFusionResult` returns:

- memory ID;
- score;
- component scores;
- included/excluded status;
- excluded reason tags;
- source refs;
- policy refs.

Result payloads keep content redacted. They do not return candidate previews or
raw evidence text. This makes the interface safe to expose in future retrieval
explanation receipts.

## Boundaries

- External text remains untrusted data.
- Fusion results are not memory writes.
- Fusion results are not instructions.
- Raw evidence refs are not accepted.
- Excluded candidates stay available only as redacted diagnostics.
- Real vector, sparse, and graph adapters must feed this contract rather than
  bypassing it.

## Verification

`CONTEXT-FUSION-INDEX-STUB-001` checks that:

- trusted graph-relevant memory can outrank semantically similar risky memory;
- prompt_injection_risk excludes otherwise similar candidates;
- raw refs are rejected;
- result content stays redacted;
- deterministic tie ordering is stable;
- docs, benchmark registry, task board, and traceability report mention the
  suite and policy ref.
