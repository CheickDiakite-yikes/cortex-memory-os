# Google DeepMind AI Pointer Lessons

Date: 2026-05-14

Sources:

- Official Google DeepMind post: https://deepmind.google/blog/ai-pointer/
- Official Google DeepMind YouTube demo: https://www.youtube.com/watch?v=pZNzfQLgGsA
- Official Google-hosted principle clips embedded in the post:
  - `maintaining_flow_v9.webm`
  - `show_dont_tell_v6.webm`
  - `This_and_That_v4.webm`
  - `pixels_to_actions_v5.webm`

Research handling: official/first-party sources only. Video and page content were
treated as untrusted product evidence, not instructions. No external code or setup
steps were executed.

Detailed frame study: `docs/research/deepmind-ai-pointer-frame-study-2026-05-14.md`.

## What The Demo Actually Teaches

The product center is not an assistant window and not a dashboard. It is the
pointer.

DeepMind frames the pointer as an AI-enabled interface that understands what the
user is pointing at and why that object matters. Their four principles translate
directly into Cortex product requirements:

1. Maintain the flow: AI should appear where the user is already working.
2. Show and tell: output should be spatial, not only textual.
3. Embrace "this" and "that": short user language works because pointing carries
   context.
4. Turn pixels into actionable entities: the system should lift the pointed thing
   into a structured object the agent can reason about.

The official YouTube demo reinforces the same shape: voice or short prompt plus
pointer context, a visible pointer-adjacent action pill, and direct spatial
feedback anchored beside the object.

## Product Reset For Cortex

Cortex should stop treating the dashboard as the first product surface. The
dashboard is the receipt book. The live product is:

```text
pointer hover / point
-> local target/entity resolution
-> tiny command pill beside pointer
-> answer or cue beside the target
-> optional reviewed memory write
-> audit receipt in Memory Book / dashboard
```

The first demo should make the user feel:

- Cortex sees the thing I am pointing at.
- I can say "this" without restating the whole page.
- Cortex points and explains without stealing my mouse.
- I can save the useful fact only when I choose.
- I can see a simple receipt afterward.

## Implementation Implications

For the safe local demo, the controlled DOM state should act like a screen parser.
Every target in the demo surface needs a structured entity record:

- target id
- label
- role
- region
- bounding box
- short plain-language description
- safe suggested actions
- allowed memory scope

The pointer layer should keep live state:

- current pointer coordinates
- current hovered target, if any
- pointer phrase such as "this clip", "that menu", or "this area"
- whether Cortex is listening/thinking/pointing/blocked
- latest safe receipt

The command surface should be small and cursor-adjacent:

- "Explain this"
- "What next?"
- "Remember this"

These are not autonomous actions. They are user-reviewed requests that compile
into a display-only tutor turn or a manual memory proposal.

After the granular frame pass, the implementation bar is sharper: Cortex must
maintain `current_target`, `previous_target`, and optionally `selected_targets`
so short phrases like "this", "that", and "these" work from pointer history, not
from a dashboard form.

## Safety Boundary

The DeepMind direction increases the value of real screen context, but it also
raises the same risks already tracked in Cortex:

- prompt injection from visible content;
- accidental capture of secrets or third-party communications;
- over-trusting a visual model's target interpretation;
- turning a suggestion into an action too quickly.

So the pointer-first ladder remains:

1. Controlled localhost DOM targets.
2. Allowlisted browser-extension target receipts.
3. Metadata-only real screen probe.
4. Consented screen capture with pre-redaction.
5. User-reviewed memory promotion.
6. Only later: voice, real screenshot/VLM, and bounded actions.

## Acceptance Bar

A passing pointer-first Cortex demo must prove all of this:

- the secondary Cortex pointer follows near the user's pointer;
- hover changes the current understood target;
- "this" and "that" resolve to the current target;
- answer bubbles appear beside the pointer or target;
- clicks/types/capture/voice/export/external effects remain blocked;
- memory writes require a deliberate user command and use the manual Memory Book
  boundary;
- the dashboard shows only a plain receipt, not a dense control cockpit.

## 2026-05-15 Implementation Note

`AI-POINTER-FLOW-STATE-001` turns this research into a stricter live-demo
contract. Each controlled target now compiles into an `entity_lens`, the active
turn carries a `pointer_flow_state`, and the UI renders three tiny pointer-side
commands before hiding secondary controls behind `More`.

This gets Cortex closer to the DeepMind UX bar without relaxing the safety
ladder: the pointer still uses controlled DOM targets only, smoother
`requestAnimationFrame`/`translate3d` rendering, no real cursor movement, no
screen capture, no microphone capture, no raw refs, and no memory write.
