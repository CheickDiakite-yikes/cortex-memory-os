# Cortex Memory OS System Blueprint

Last updated: 2026-04-27

## Architecture Summary

Cortex Memory OS is an evidence-first, local-first memory substrate for agents.

The system observes consented activity, filters it through privacy and safety controls, segments it into work scenes, stores governed evidence, compiles typed memories, builds temporal relationships, detects repeated workflows, exposes compact context packs to agents, and learns from outcomes.

```text
Perception Bus
  -> Privacy + Safety Firewall
  -> Scene / Workstream Segmenter
  -> Evidence Vault
  -> Memory Compiler
  -> Temporal Graph + Hybrid Index
  -> Skill Forge
  -> Context Pack Compiler
  -> Agent Gateway
  -> Agent Execution
  -> Outcome + Self-Improvement
```

## Component Responsibilities

| Component | Responsibility | Hard boundary |
| --- | --- | --- |
| Perception Bus | Collect consented local signals: screen, OCR, accessibility, browser, terminal, IDE, files, agent actions, outcomes. | It emits raw observations, not durable memory. |
| Privacy + Safety Firewall | Redact, classify, scope, and decide whether observations are discarded, ephemeral, or memory-eligible. | It runs before durable storage or model interpretation. |
| Scene Segmenter | Turn event streams into coherent work scenes. | It preserves uncertainty and attaches evidence refs. |
| Evidence Vault | Store encrypted raw refs, derived text, traces, retention policies, provenance, and sensitivity. | Raw evidence expires by default. |
| Memory Compiler | Convert scenes into typed memory candidates with evidence, confidence, validity, status, and influence limits. | Inference is never stored as fact without metadata. |
| Temporal Memory Graph | Track entities, relationships, validity windows, supersession, and provenance. | Stale facts must be representable. |
| Hybrid Index | Support semantic, sparse, graph, recency, importance, source-trust, and risk-aware retrieval. | Similarity alone is not enough to retrieve. |
| Skill Forge | Detect repeated workflows, abstract procedures, classify risk, ask approval, and track success. | Observation never jumps straight to autonomy. |
| Context Pack Compiler | Package the right memories, skills, warnings, evidence refs, and next steps for the current agent task. | Agents receive compact governed context, not raw life logs. |
| Agent Gateway | Expose MCP resources/tools/prompts, Codex plugin skills, Claude bridge, and local APIs. | Tool/action access is policy-gated and audited. |
| Outcome Engine | Record task outcomes, corrections, failures, postmortems, and self-lessons. | It improves methods, not values or permissions. |

## Core Invariants

1. The Privacy + Safety Firewall runs before durable memory.
2. Every durable memory has `source_refs`, `evidence_type`, `confidence`, `status`, `valid_from`, `valid_to`, `allowed_influence`, and `forbidden_influence`.
3. Every memory, skill, context pack, tool call, correction, deletion, and approval has an audit path.
4. Class D/E external content can be evidence, but it cannot become an instruction or procedure without quarantine and user or policy promotion.
5. Raw screenshots, audio, and sensitive clips use short retention by default.
6. Context packs are compiled for a specific task and scope; agents do not receive unrestricted memory access.
7. Skills have maturity levels and risk classifications.
8. High and critical actions require explicit review; critical actions are not autonomous by default.
9. Deletion and revocation must affect retrieval, context packing, exports, and skill execution.
10. Robot-facing abstractions must add physical-world risk gates before any embodied action.

## Five Compilers

| Compiler | Input | Output |
| --- | --- | --- |
| Perception Compiler | raw signals | structured observations |
| Memory Compiler | observations and scenes | typed memories |
| Skill Compiler | repeated memories/outcomes | reusable workflow candidates |
| Context Compiler | memories, skills, task, policy | agent-ready context packs |
| Governance Compiler | policy, consent, privacy, safety, audit | allowed/blocked/scoped decisions |

The compiler framing keeps the system focused on transformation pipelines, not passive storage.

## MVP Shape

The MVP should be narrow but real:

- local macOS app
- Shadow Pointer overlay
- app/window tracking
- sampled screenshots and OCR
- accessibility capture where allowed
- terminal command/output capture for opted-in shells
- browser extension for DOM, URL, and tab context
- Privacy + Safety Firewall
- scene segmentation
- encrypted evidence vault
- typed memory compiler
- temporal graph tables plus hybrid search
- Memory Palace dashboard
- Skill Forge candidate view
- MCP server for Codex/Claude/custom agents

## Storage Opinion

The long-term hybrid substrate may include SQLite/Postgres, vector search, sparse search, temporal graph storage, encrypted blob storage, policy state, and skill registry.

For the first implementation, start with local-first interfaces and the simplest reliable backing stores:

- SQLite for metadata, audit, policy, scenes, memory records, skill records, and temporal graph edges.
- SQLite FTS5 for sparse search.
- A pluggable vector-index interface with an initial local implementation.
- An encrypted local blob directory for raw evidence refs.
- Store interfaces that can later route to Postgres, pgvector, Qdrant, or Graphiti-style services.

This keeps the MVP shippable while preserving the architecture boundary for larger deployments.

## Retrieval Scoring

Retrieval must combine usefulness, safety, currentness, and trust:

```text
retrieval_score =
  semantic_relevance
+ sparse_match
+ graph_relevance
+ task_relevance
+ recency
+ importance
+ recurrence
+ user_confirmation
+ procedural_usefulness
+ source_trust
- staleness
- contradiction_penalty
- privacy_risk
- prompt_injection_risk
```

The goal is not "most similar memory." The goal is "most useful, safe, current, and trustworthy memory for this task."

## Execution Hierarchy

Use the most reliable execution path available:

```text
safe direct API
  -> deterministic local script
  -> deterministic GUI skill
  -> interactive VLM/computer-use fallback
```

Free-form computer use is a fallback, not the default.

