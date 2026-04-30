# Local Fusion Adapters

`REAL-VECTOR-INDEX-ADAPTER-001` adds dependency-free semantic, sparse, and graph
adapters behind the existing `CONTEXT-FUSION-INDEX-STUB-001` interface.

The name is intentionally forward-looking: this is the adapter seam a real
embedding/vector index, sparse text index, and graph store can replace later.
For now, the implementation is local, deterministic, and safe to run in the
default benchmark suite.

## Adapter Roles

- `LocalSemanticAdapter` scores lexical-semantic overlap across memory content,
  memory type, scope, and influence tags.
- `LocalSparseAdapter` scores exact-token overlap across content, source refs,
  and allowed influence tags.
- `LocalGraphAdapter` scores temporal graph neighborhoods from already-compiled
  `TemporalEdge` objects.

All three adapters feed `HybridIndexCandidate` objects and reuse
`policy_hybrid_context_fusion_index_v1`.

## Safety Boundary

The adapters do not call a network service, load model weights, add packages,
or persist an index. External content remains untrusted data. Prompt-injection
risk is detected from hostile phrases and external evidence type, then passed to
the fusion layer where high-risk candidates are excluded.

The adapters may inspect memory content internally to compute local scores, but
adapter scorecards are dashboard-safe:

- `content_redacted: true`
- no content previews;
- source reference counts only;
- `policy_local_fusion_adapters_v1`

Raw refs remain blocked by the existing `HybridIndexCandidate` validator.

## Upgrade Path

Future production adapters should keep this contract stable:

```text
MemoryRecord + TemporalEdge + LocalFusionQuery
  -> semantic_score / sparse_score / graph_score
  -> HybridIndexCandidate
  -> fuse_hybrid_candidates()
  -> redacted HybridFusionResult
```

Any remote vector database, embedding model, or graph service must preserve
consent, source-trust, raw-ref rejection, prompt-risk exclusion, and result
redaction before it can replace the local fallback.
