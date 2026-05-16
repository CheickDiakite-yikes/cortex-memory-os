# Live Tutor Engineer Runbook

Last updated: 2026-05-15

Benchmark: `LIVE-TUTOR-BROWSER-PROOF-001`

Policy reference: `policy_live_tutor_browser_proof_v1`

This runbook is the handoff for engineers continuing the pointer-first Cortex
demo. The product goal is simple: Cortex should feel like a second visible
helper cursor beside the user's work, while the current safe build remains a
controlled local demo.

## What To Run

Start the local tutor surface:

```bash
uv run cortex-live-tutor-demo
```

Open the printed local URL in the Browser plugin or a normal browser, usually:

```text
http://127.0.0.1:8797/
```

Run the replay proof:

```bash
uv run cortex-live-tutor-demo --browser-replay-smoke --json
```

The replay smoke posts browser CSS pixels with `client_surface_css`, including
an intentionally out-of-bounds pointer sample. The backend scales and clamps
that input into the canonical 1440x960 controlled surface before it is used for
spatial routing.

Inspect redacted receipts:

```text
GET /tutor/receipts
Header: X-Cortex-Live-Tutor-Token: <token from the page meta tag>
```

The receipt endpoint is token-protected and localhost-only. Receipts may include
target labels, intent labels, voice route labels, confidence, safety flags, and
blocked effects. They must not include raw user utterances, full assistant
responses, screenshots, raw refs, microphone data, Accessibility trees,
clipboard contents, file contents, exports, or durable memory writes.

## Browser Plugin Proof

Use the Browser plugin proof when validating frontend changes. The expected
manual sequence is:

1. Open `http://127.0.0.1:8797/`.
2. Click `Start pointer helper`.
3. Move over `Color Page`, `Node Graph`, and `LUT Menu`.
4. Confirm the blue secondary cursor follows beside the pointer and leaves a
   short visible trace.
5. Ask `Explain this` or use click-and-hold/triple-click gesture buttons.
6. Confirm the instruction bubble points at the correct safe demo target.
7. Confirm the latest redacted receipt reports no click, no capture, no raw
   ref, no memory write, and no external effect.

This is a Browser plugin proof, not a real screen-capture proof.

## Safety Boundary

Allowed in this slice:

- controlled DOM/state reads from Cortex Resolve Studio
- display-only secondary cursor
- target highlight
- instruction bubble
- redacted receipt writes
- synthetic voice gesture routing

Blocked in this slice:

- real screen capture
- microphone capture
- Accessibility observer
- real cursor movement
- clicks or typing
- durable memory writes
- raw refs or raw evidence retention
- exports
- external effects

## Next Engineering Moves

The next product gap is not more dashboard detail. It is making the pointer
loop feel alive and legible:

- keep pointer tracking smooth under resize and scroll
- keep wake-up calm: starting the helper should not auto-run a question or jump
  the pointer to an off-screen target
- expose `this`, `that`, and `these` as tiny target-history chips near the
  pointer
- show hover target affinity before the user asks a question
- show a short thinking/loading state and hold-progress feedback for voice
  gestures
- show a tiny receipt toast after a turn instead of forcing the user into logs
- add a guided tour that walks Color Page -> Node Graph -> LUT Menu ->
  Inspector using display-only cues
- show safety route and confidence in the pointer card, not only in receipts
- make memory proposals read like "idea, not saved" instead of an engineering
  receipt
- keep voice gesture affordances visible as tiny, learnable pills
- make voice gesture state visible before the user asks
- show the current target in plain language near the cursor
- keep receipts child-readable
- move toward consented Realtime voice only after the controlled pointer proof
  is stable

## Current UX State

The pointer card now has a calm safe-mode route chip, a confidence chip, target
history for `this`, `that`, and `these`, a tiny tour strip, loading feedback,
receipt toasts, and a guided tour. The review side now shows recent chats and a
simple agent voice preference preview before exposing engineering receipts. The
right side is organized as user-facing tabs: Chats, Memories, Voice, and Safety.
Memory ideas enter a review-only queue; the session summary counts chats and
memory ideas without implying anything has been durably saved.

The tour is intentionally display-only: it highlights controlled DOM targets,
moves the secondary cursor, and writes a redacted local receipt toast, but it
does not click, capture, speak, save memory, export, or call external services.
