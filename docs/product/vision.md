# Cortex Memory OS Vision

Last updated: 2026-04-27

## Product Thesis

Cortex Memory OS is a private memory brain for AI agents.

It is not "memory for agents" and it is not "an AI screen recorder." It is a multimodal brain layer that watches work with consent, turns activity into structured memory, turns repeated activity into skills, gives agents the right context at the right time, and improves itself from outcomes.

Canonical loop:

```text
Perception -> Evidence -> Memory -> Skill -> Agent Action -> Outcome -> Self-Improvement
```

Anti-pattern:

```text
screen recording -> summary -> vector DB
```

The anti-pattern can demo well but does not create a trustworthy long-term memory substrate.

## First Body And Long-Term Body

The first embodiment is a local laptop system for coding and research workflows with Codex, Claude Code, and similar agents.

The long-term architecture should remain embodiment-neutral:

| Laptop concept | Robot equivalent |
| --- | --- |
| screen frame | camera/depth frame |
| cursor action | motor action |
| app/window | room/object/tool state |
| file/document | physical object/location |
| terminal output | sensor feedback |
| workflow | physical routine |
| GUI skill | manipulation skill |

The MVP must therefore be built as a perception-action-memory system whose first body is a laptop, not as a narrow recorder.

## User-Visible Pillars

| Pillar | Promise |
| --- | --- |
| Shadow Pointer | Shows when observation, memory, context, learning, or agent action is active. |
| Memory Palace | Lets the user inspect, correct, delete, scope, pin, and expire memories. |
| Skill Forge | Shows repeated workflows Cortex has learned and proposes safe reusable skills. |
| Agent Gateway | Lets Codex, Claude, Cursor, custom agents, and future planners request context and approved skills. |

## Design Principles

- Consent is a product feature, not a settings page.
- Raw evidence is not memory. Raw evidence is temporary proof behind governed memory.
- Every durable memory needs provenance, confidence, status, valid time, and influence scope.
- Evidence and inference must remain distinguishable.
- External content is untrusted. It may be evidence, but it must not become instructions by default.
- Memory-to-skill compilation is the core leverage loop.
- Skills mature gradually from observation to suggestion to draft-only execution to bounded autonomy.
- APIs beat scripts. Scripts beat GUI replay. GUI replay beats free-form computer use.
- Self-improvement may tune methods, retrieval, templates, skills, and safety filters. It must not silently rewrite values, permissions, or user boundaries.
- Future robot actions require stricter physical-world capability gates, simulation-first validation, and emergency-stop design.

## Non-Goals

- Hidden surveillance.
- Raw life logging as the product.
- A vector database with a chat UI.
- Autonomous agent action without explicit scope and audit.
- Storing private screen evidence forever.
- Treating model inferences as facts.
- Letting webpages, PDFs, emails, or screenshots issue instructions to the system.
- Fine-tuning or rewriting behavior secretly from private user activity.

## First Sharp Domain

Start with coding and research workflows:

- active project and repo context
- terminal commands and test output
- browser research context
- IDE/app/window context
- agent actions and outcomes
- task postmortems

Do not start by capturing all of the user's life.

