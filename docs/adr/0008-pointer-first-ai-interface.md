# ADR 0008: Pointer-First AI Interface

Date: 2026-05-14

Status: Accepted

## Context

The earlier Cortex dashboard and live tutor work proved many safety contracts,
but the product still felt like a control panel with a cursor animation. Google
DeepMind's official AI Pointer work clarifies the missing product center: the
pointer itself should be the AI interaction surface.

The user should be able to point at something, say "this" or "that", and see a
small AI response or command pill near the pointer without leaving the current
workflow.

## Decision

Cortex will treat the pointer as the primary live surface and the dashboard as a
secondary receipt/review surface.

The first pointer-first spine remains safe-local:

- controlled localhost DOM targets stand in for screen perception;
- the Cortex secondary pointer follows near the user's real pointer;
- the helper has an explicit wake moment before it starts tracking;
- hover resolves a structured target entity;
- short utterances such as "explain this", "what next", and "remember this"
  resolve against the current target;
- pointer-local commands render beside the cursor, not in a distant dashboard;
- responses, micro-steps, and reviewed memory proposals render beside the
  pointer or target;
- target pinning makes "these" visible before it becomes an agent reference;
- memory writes require an explicit user command and remain manual-memory-bound;
- click, type, real capture, microphone, Accessibility observation, export, and
  external effects remain blocked.

## Consequences

This narrows near-term product work. Dashboard polish is no longer the main
axis. The next demos must prove pointer feel, target understanding, safe memory
promotion, and simple receipts before adding broader real capture.

The live tutor demo becomes the product proving ground. A dashboard card is only
acceptable when it explains what happened in plain language after the pointer
interaction.
