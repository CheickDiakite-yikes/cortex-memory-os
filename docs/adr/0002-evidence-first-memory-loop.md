# ADR 0002: Evidence-First Memory Loop

Status: Accepted

Date: 2026-04-27

## Context

The project goal is not a screen recorder or vector memory demo. Cortex Memory OS is intended to become a multimodal brain layer for agents and future robots. It must observe work with consent, transform activity into structured memory, compile repeated activity into skills, expose task-scoped context to agents, and improve from outcomes.

Current ecosystem signals support pieces of the direction: screen context for coding agents, MCP as an integration layer, temporal graph memory, and client-controlled persistent memory. These also increase the risk of prompt injection, over-capture, stale memory, and unsafe tool access.

## Decision

Adopt the following canonical architecture:

```text
Perception -> Privacy/Safety Firewall -> Scene -> Evidence -> Memory
  -> Temporal Graph/Hybrid Index -> Skill -> Context Pack
  -> Agent Gateway -> Outcome -> Self-Improvement
```

The first implementation domain is local coding and research workflows. The first embodiment is a laptop. The abstractions must remain compatible with phone and robot embodiments later.

## Consequences

- Raw observations never directly become memory.
- The Privacy + Safety Firewall is part of the core data path, not a later add-on.
- Evidence remains distinct from memory and inference.
- Typed memory, temporal validity, source refs, and influence scopes are required fields.
- Retrieval must be risk-aware and task-aware, not just similarity search.
- Skills mature through explicit levels and approval gates.
- The Agent Gateway exposes context packs and approved skills, not unrestricted stores.
- Self-improvement can update methods, checklists, retrieval rules, and skills, but not silently change permissions or user boundaries.

## Alternatives Considered

- Screen capture plus summaries plus vector DB: faster demo, but unsafe and too shallow for a durable memory OS.
- Agent memory files only: useful for persistence, but insufficient for multimodal evidence, workflow detection, temporal truth, and skills.
- Swarm-first architecture: unnecessary before a strong single memory substrate, governance layer, and context compiler exist.

## Verification Plan

- First benchmark harness must include prompt-injection, deletion, recall, and sensitive-data fixtures.
- First MCP response must be a scoped context pack with source refs and warnings.
- First memory candidate must include evidence refs, confidence, validity, and influence limits.
- First skill candidate must remain draft-only until approved.

