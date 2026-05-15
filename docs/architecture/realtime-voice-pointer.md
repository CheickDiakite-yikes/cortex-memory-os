# Realtime Voice Pointer

Status: implemented as a safe synthetic contract.

`REALTIME-VOICE-CONTRACT-001` makes the product direction explicit: Cortex should use
`gpt-realtime-2` for the real pointer-first voice loop, not the cheap text fallback path.
The cheap text model can remain a smoke-test seam, but the product spine is voice input,
spatial pointer state, output routing, and safe receipts.

Policy reference: `policy_realtime_voice_pointer_v1`.

Official sources used:

- OpenAI Realtime and audio overview: https://developers.openai.com/api/docs/guides/realtime
- OpenAI Voice agents guide: https://developers.openai.com/api/docs/guides/voice-agents
- OpenAI Realtime cost guide: https://developers.openai.com/api/docs/guides/realtime-costs
- OpenAI `gpt-realtime-2` model page: https://developers.openai.com/api/docs/models/gpt-realtime-2

## UX Grammar

`POINTER-GESTURE-GRAMMAR-001` defines the first child-readable interaction rules:

- Triple click: start a short voice back-and-forth beside the pointer.
- Click and hold: ask by voice but get a text answer back.
- Click and hold in silent/action mode: show the next pointer cue with no voice back.
- Drag or multi-select: group several targets so "these" has a clear referent.
- Escape/cancel: stop the transient voice pointer state.

The safe demo does not open a real microphone. It uses synthetic transcript events to prove the
gesture-to-output route before we wire live audio.

## Output Router

`VOICE-OUTPUT-ROUTER-001` separates voice input from voice output:

```text
voice or typed intent
  -> pointer target
  -> gesture grammar
  -> output router
     -> silent visual
     -> text chip
     -> spoken brief
     -> memory review
     -> blocked
```

This matters because input voice does not always need output voice. Cortex should usually answer
beside the work as text. It should speak only when the gesture or explicit user intent asks for it.

## Cost Guard

`REALTIME-COST-GUARD-001` keeps the live voice path bounded:

- model: `gpt-realtime-2`
- reasoning effort: low
- default output: text-only until a gesture asks for speech
- max session seconds: 45 in demo mode
- max input audio seconds: 18 in demo mode
- max output audio seconds: 8 in demo mode
- max responses: 6 in demo mode
- raw audio retention: none
- memory write: off

The cost guard can force triple-click voice back into a text chip when spoken output is disabled.

## Realtime Client Secret Boundary

`REALTIME-CLIENT-SECRET-CONTRACT-001` models the production browser/mobile path:

- server creates an ephemeral client secret with `POST /v1/realtime/client_secrets`
- browser connects with WebRTC
- raw API key is never exposed to the browser
- a privacy-preserving safety identifier is required
- session instructions and truncation settings are stable so prompt caching has a chance to help

The current implementation stores no client secret value and performs no live network request.

## Current Safety Boundary

`SYNTHETIC-VOICE-TURN-LOOP-001` and `LIVE-TUTOR-VOICE-UX-001` remain synthetic:

- no live microphone
- no screen capture
- no raw audio
- no raw refs
- no durable memory writes
- no clicks or typing
- no external effects

The next ladder step is a consented, short, ephemeral Realtime smoke that creates a client secret
and immediately tears it down without sending private audio.
