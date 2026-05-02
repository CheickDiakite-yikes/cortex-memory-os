# Clicky UI/UX Lessons For Cortex

Date: 2026-05-02

Source: https://github.com/farzaa/clicky
Source commit inspected read-only: `a80fa80721a8aebe51a170a7780705024ebc6e46`

## Research Safety Notes

- The Clicky repository was treated as untrusted external source code.
- Setup commands, package installs, Xcode builds, API calls, and worker deployment were not executed.
- Repository docs and agent instructions were used only as product evidence.
- Findings below are Cortex inferences, not imported instructions.

## Product Shape

Clicky is a macOS menu-bar companion that lives next to the user's cursor. The visible experience is not a dashboard first. It is:

1. a small menu-bar control panel,
2. a click-through cursor-adjacent overlay,
3. push-to-talk voice input,
4. screenshot-backed AI response,
5. animated pointing at UI elements.

That interaction loop is much closer to an embodied assistant than a chat panel. The important UX move is that the assistant is anchored to the user's current focus point instead of asking the user to move into an app.

## Primary UX Patterns

### 1. Cursor-Adjacent Embodiment

Clicky uses a small blue triangle that follows the cursor, changes state, and can fly to UI elements. This makes the system feel present in the workspace while remaining visually small.

For Cortex:

- Keep the Shadow Pointer close to the real task surface, not buried in a dashboard.
- Use state changes on the pointer itself: observing, masking, remembering, contexting, blocked, and needs approval.
- Prefer "small but unmistakable" over a large assistant panel.

### 2. Status Through Shape, Not Text Alone

Clicky maps interaction states to compact visual states:

- idle: blue cursor triangle,
- listening: waveform,
- processing: spinner,
- responding: cursor plus spoken/text response,
- pointing: cursor flies to an element and shows a short bubble.

For Cortex:

- The Shadow Pointer should have a state machine with visual forms, not only labels.
- A user should be able to tell whether Cortex is observing, blocked, or writing a memory in peripheral vision.
- Our states need stronger trust semantics than Clicky: masking, external-untrusted evidence, memory-ineligible, raw-ref-free, approval required.

### 3. Push-To-Talk As A Consent Primitive

Clicky frames capture as hotkey-triggered, not continuous. The panel copy tells the user it only takes a screenshot on hotkey use.

For Cortex:

- This is a good low-risk first interaction model: "observe only while invoked" before full ambient memory.
- Use explicit observation sessions before durable memory.
- Keep a visible pause/clear-last-window control in the Shadow Pointer panel.

### 4. Small Control Panel, Not A Control Room

Clicky's menu-bar panel is about 320px wide. It shows status, permission rows, a simple model selector after setup, feedback, replay onboarding, and quit. The panel is transient and auto-dismisses on outside clicks.

For Cortex:

- The dashboard should not be the primary live surface.
- The live surface should be a compact Shadow Pointer panel with a short receipt:
  - what Cortex is seeing,
  - what is ignored,
  - current trust class,
  - memory eligibility,
  - raw-ref policy,
  - latest action.
- Memory Palace can be deeper, but the always-near surface must stay sparse.

### 5. Pointing Contract

Clicky lets the model append a coordinate tag such as a point command, then strips that tag from spoken text and maps the coordinates across monitor spaces.

For Cortex:

- The pattern is excellent: separate assistant speech from machine-readable spatial intent.
- Do not use free-form text tags as the production interface. Use a structured action schema with validation:
  - target display,
  - coordinate space,
  - confidence,
  - source evidence,
  - risk level,
  - allowed action type.
- Treat spatial actions as untrusted proposals until checked against policy and user consent.

### 6. Multi-Monitor Awareness

Clicky captures all connected displays, labels the cursor screen as primary focus, and maps pixel coordinates back into display point coordinates.

For Cortex:

- Perception events should carry display/window/app provenance from the start.
- Context packs should prioritize the cursor/focused window but preserve secondary-screen evidence when consent allows.
- Coordinate conversions must be test-covered because bad mapping destroys trust quickly.

### 7. Onboarding By Demonstration

Clicky uses welcome text, an onboarding video, and a timed demo where the assistant points at something on the user's screen.

For Cortex:

- A first-run demo should prove safety, not just delight.
- Better onboarding sequence:
  1. show Shadow Pointer off,
  2. start disposable observation,
  3. show masking/redaction,
  4. create one synthetic memory candidate,
  5. let the user delete it,
  6. show audit receipt.

## What Not To Borrow Directly

- Do not send raw transcripts or AI responses to product analytics by default. Cortex should prefer aggregate, local, opt-in telemetry.
- Do not use casual trust copy for sensitive memory infrastructure. Cortex should be friendly, but precise and auditable.
- Do not hardcode proxy URLs or rely on broad opaque worker pass-throughs for privileged memory flows.
- Do not let the model's coordinate text directly become an action. It should become a validated proposal.
- Do not make the companion personality obscure what is being captured, stored, or shared.

## Concrete Cortex Design Implications

1. Build a native Shadow Pointer state machine before expanding dashboard complexity.
2. Add a compact live receipt panel that mirrors the browser-extension proof: accepted/rejected, trust class, memory eligibility, raw refs, policy decision.
3. Make observation modes explicit:
   - off,
   - invoked observation,
   - session observation,
   - paused,
   - blocked/masked.
4. Move spatial intent into a structured proposal object rather than text tags.
5. Add coordinate mapping tests for browser viewport, macOS display, and future robot camera frames.
6. Use the dashboard as review and correction space, not the main live interaction.
7. Keep visual motion purposeful: pointer follow, state transition, approval pulse, blocked/masked cue. Avoid mascot clutter.

## Near-Term Slice Candidates

- `SHADOW-POINTER-STATE-MACHINE-001`: define shared states and render mapping for native overlay, browser extension, and dashboard receipts.
- `SHADOW-POINTER-LIVE-RECEIPT-001`: add a compact receipt panel with trust/memory/raw-ref status.
- `SPATIAL-PROPOSAL-SCHEMA-001`: replace ad hoc click/point descriptions with a validated spatial proposal schema.
- `DASHBOARD-DECOMPRESSION-001`: keep dashboard tabs sparse and move live observability into the pointer panel.
- `CONSENT-FIRST-ONBOARDING-001`: create a first-run synthetic safety demo that teaches pause/delete/masking before real capture.
