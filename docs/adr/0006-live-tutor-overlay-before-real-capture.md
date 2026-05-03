# ADR 0006: Live Tutor Overlay Before Real Capture

Date: 2026-05-03

Status: Accepted

## Context

The Clicky/Buddy reference showed that the strongest experience is not a
dashboard-first memory system. It is a spatial tutor that can see task context,
answer in plain language, and point at the relevant UI with a secondary cursor
while leaving the user's real cursor and clicks alone.

Cortex still has a stricter safety boundary than that product demo. Real screen
capture, microphone capture, Accessibility observation, raw refs, and durable
private memory writes must not become default behaviors.

## Decision

Build the first live tutor milestone as a controlled localhost creative-tool
demo:

- read only controlled DOM/state;
- resolve a small set of contextual tutor intents;
- render a blue secondary cursor, target highlight, and instruction bubble;
- persist only safe turn receipts in memory for the running demo process;
- expose dashboard-safe aggregate state;
- block click, type, capture, voice, raw-ref, memory-write, export, and
  external-effect authority.

## Consequences

This creates a real product-shaped demo without widening capture authority. It
also gives later real-capture work a concrete receipt shape to preserve.

The next acceptable step is not continuous capture. The next step is an
allowlisted, consented source that emits the same display-only pointing receipt
shape under the existing firewall and evidence eligibility gates.
