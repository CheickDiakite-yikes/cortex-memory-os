# Live Tutor Overlay

Last updated: 2026-05-14

Benchmark: `LIVE-TUTOR-OVERLAY-001`

Policy reference: `policy_live_tutor_overlay_v1`

This slice turns the Clicky/Buddy product lesson into a controlled Cortex demo:

```text
user question
-> controlled creative-tool DOM/state adapter
-> intent and target resolution
-> display-only blue secondary cursor
-> target highlight and instruction bubble
-> safe turn receipt
```

After the AI Pointer frame study, this contract is pointer-first:

```text
pointer hover
-> current target entity
-> cursor-adjacent command chip
-> "this / that / these" resolution from target history
-> wakeable pointer helper state
-> answer, tiny next-step hints, or manual memory proposal beside the work
-> simple safe receipt
```

The runnable demo is:

```bash
uv run cortex-live-tutor-demo
```

The smoke gate is:

```bash
uv run cortex-live-tutor-demo --server-smoke --json
```

## Product Learning

The key lesson from Clicky is not "move the user's mouse." It is: keep the
assistant spatial, visible, and shoulder-to-shoulder with the task. Cortex
adapts that as a second cursor and small instruction bubble that point at UI
targets while the user remains in control of actual clicks.

The interaction must feel alive before the user asks a question. The demo keeps
a secondary cursor tracking beside the user's pointer on the controlled work
surface, leaves a fading cursor trace, and keeps a compact cursor-adjacent
"Ask Cortex" affordance available. Target answering is layered on top of that
continuous companion behavior, not substituted for it.

The cursor-adjacent affordance is now the primary UI. A simple wake card starts
the helper, then the pointer chip shows what Cortex currently sees and exposes
pointer-local commands:

- `Explain this`
- `What next?`
- `Pin`
- `Remember this`

`Pin` builds a small target stack so "these" has visible meaning. The stack is
local state only and is not a memory write.

`Remember this` creates a reviewed manual-memory proposal only. It does not
write durable memory. The in-canvas memory proposal card must say plainly that
nothing has been saved yet.

Each turn carries a child-readable receipt sentence and up to three micro-steps.
The UI renders the first micro-step in the pointer dock so the user does not
need to parse an engineering receipt to know what happened.

The dashboard remains a review and receipt surface. The live tutor belongs near
the work surface.

## Safety Boundary

The first implementation uses a localhost-only fake creative app called
`Cortex Resolve Studio`. The adapter reads only controlled page state and target
IDs. It does not read the real screen, microphone, Accessibility tree, browser
history, tabs, clipboard, files, or external web content.

In shorter benchmark language: no screen capture, no microphone capture, no
raw refs, and no durable memory.

Every `SpatialTutorCue` is display-only. Its blocked effects include:

- `execute_click`
- `type_text`
- `start_screen_capture`
- `start_microphone_capture`
- `start_accessibility_observer`
- `write_memory`
- `store_raw_evidence`
- `retain_raw_ref`
- `export_payload`
- `external_effect`

The localhost server requires a per-session token, localhost origin, loopback
client, JSON content type, and restrictive static-file headers. Rejected
requests do not create tutor turns.

## Demo Flows

The safe demo resolves these starter questions:

- "How do I start color grading?" -> `Color Page`
- "Where is the node graph?" -> `Node Graph`
- "How do I add a LUT?" -> `LUT Menu`
- "What should I click next?" -> `Color Page` or `Node Graph` depending on the
  controlled active page state

Receipts report target, intent, confidence, allowed display effects, and blocked
effect categories. They report `raw refs: none`.

Pointer-first receipts also report the referent (`this`, `that`, `these`, or
`none`), the pointer companion state, the user-readable receipt, and whether a
memory proposal needs review.

## Next Ladder

This slice is deliberately before real capture:

1. Controlled DOM/state tutor demo.
2. Browser-extension allowlisted public-page pointing receipts.
3. Metadata-only real screen probe with permission preflight.
4. Consented ScreenCaptureKit metadata stream.
5. Redaction and prompt-injection screen before any durable memory write.
6. User-reviewed memory/skill promotion.

The product should not skip from this demo to arbitrary screen capture.
