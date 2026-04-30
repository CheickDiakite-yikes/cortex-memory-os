# Hybrid Fusion Context-Pack Integration

Task: `HYBRID-FUSION-CONTEXT-PACK-INTEGRATION-001`

## Decision

Context packs now include a metadata-only hybrid fusion diagnostic lane. The
lane is fed by the local semantic, sparse, and graph adapters, then fused by the
hybrid context fusion contract.

The diagnostic lane is for retrieval debugging, not for adding another memory
content channel.

## Contract

Each diagnostic contains:

- `memory_id`
- fused `score`
- `included`
- `excluded_reason_tags`
- bounded numeric `component_scores`
- `source_ref_count`
- `content_redacted: true`
- `source_refs_redacted: true`
- policy refs including `policy_hybrid_fusion_context_pack_diagnostics_v1`,
  `policy_local_fusion_adapters_v1`, and
  `policy_hybrid_context_fusion_index_v1`

It does not contain:

- memory content
- source refs
- raw refs
- source URLs
- hostile external text
- instructions for the agent

## Safety Boundary

Prompt-risk and external-evidence candidates can appear as excluded diagnostics
so operators can see why retrieval skipped them. They remain evidence-only or
excluded through the existing context policy. The fusion diagnostics do not
override retrieval scope, hostile-source policy, context templates, or memory
budgeting.

## Verification

The benchmark checks that:

- trusted local memories produce included diagnostics
- hostile external memories produce excluded diagnostics with
  `prompt_injection_risk`
- context packs include the diagnostic policy ref
- diagnostic payloads do not include content, source refs, hostile text, or raw
  refs
