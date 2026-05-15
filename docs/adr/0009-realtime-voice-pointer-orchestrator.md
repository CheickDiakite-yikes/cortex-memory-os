# ADR 0009: Realtime Voice Pointer Orchestrator

Status: accepted.

## Context

Cortex must become pointer-first, not dashboard-first. The desired product feel is a spatial
assistant that stays near the user's cursor, understands "this", "that", and "these", and lets the
user talk naturally without forcing spoken output on every turn.

OpenAI's current official guidance points to `gpt-realtime-2` for low-latency voice agents, WebRTC
for browser/mobile audio, ephemeral client secrets for client connection, low reasoning effort as a
starting point, and explicit cost management for multi-turn Realtime sessions.

## Decision

Implement a Realtime voice pointer orchestrator as a separate contract layer before enabling live
microphone capture.

The first implemented slice includes:

- `REALTIME-VOICE-CONTRACT-001`
- `POINTER-GESTURE-GRAMMAR-001`
- `VOICE-OUTPUT-ROUTER-001`
- `REALTIME-COST-GUARD-001`
- `SYNTHETIC-VOICE-TURN-LOOP-001`
- `REALTIME-CLIENT-SECRET-CONTRACT-001`
- `LIVE-TUTOR-VOICE-UX-001`
- `SELECTION-UX-CONTRACT-001`
- `DASHBOARD-VOICE-POINTER-PANEL-001`
- `REALTIME-VOICE-BENCH-DOCS-001`

## UX Rules

Triple click means voice dialogue: Cortex may speak briefly.

Click and hold means voice-in, text-out: Cortex listens to the intent but answers as a compact text
chip.

Click and hold in silent/action mode means no voice back: Cortex moves the guide pointer or target
highlight only.

Selection means grouped context: Cortex can answer about "these" before proposing a memory or skill.

## Safety Rules

This ADR does not authorize live microphone capture. The implemented path is synthetic and
display-only.

Live Realtime work must continue to require:

- explicit microphone consent
- ephemeral client secret
- no raw API key in browser code
- low reasoning effort by default
- cost guard
- no raw audio retention
- no automatic memory write
- no screen capture escalation
- no click/type/export/external effect authority

## Consequences

The live tutor demo now begins to match the intended product feel: pointer, voice gesture, output
mode, receipt. The dashboard should describe this loop simply, while engineering receipts stay behind
debug views.

The next live step is not full screen capture. It is a short consented Realtime client-secret smoke,
then a disposable mic/transcript test with no private audio, no raw retention, and hard session
limits.
