# Google DeepMind AI Pointer Frame Study

Date: 2026-05-14

Sources:

- Official Google DeepMind post: https://deepmind.google/blog/ai-pointer/
- Official YouTube demo: https://www.youtube.com/watch?v=pZNzfQLgGsA
- Official Google-hosted embedded clips from the DeepMind post.

Method:

- Extracted one frame per second from the four official embedded `.webm` clips.
- Extracted the official YouTube storyboard at the 320x180 level, giving roughly
  one frame every two seconds for the 168 second video.
- Kept generated frame/contact-sheet artifacts outside the repo under `/tmp` to
  avoid committing third-party visual assets.

Temporary frame artifacts from this pass:

- `/tmp/cortex-ai-pointer-granular/maintain-flow-contact.jpg`
- `/tmp/cortex-ai-pointer-granular/show-dont-tell-contact.jpg`
- `/tmp/cortex-ai-pointer-granular/this-that-contact.jpg`
- `/tmp/cortex-ai-pointer-granular/pixels-actions-contact.jpg`
- `/tmp/cortex-youtube-storyboard/full-youtube-storyboard-contact.jpg`
- `/tmp/cortex-youtube-storyboard/selected-moments-contact.jpg`

## Frame-Level UX Observations

### 1. The Pointer Is A Moving Intent Handle

The pointer does not just mark an x/y coordinate. It marks the user's active
intent. The visual grammar is:

```text
real pointer near object
-> soft blue glow / target affinity
-> compact pill appears beside the pointer
-> command uses short speech: "Add this", "Move this", "Merge these"
```

For Cortex, this means the pointer state must carry:

- current coordinates;
- current target entity;
- current target confidence;
- short referent phrase like `this`, `that`, or `these`;
- current command mode.

### 2. The Pill Is The Product Surface

The important UI is a small rounded action pill anchored beside the pointer, not
a large assistant panel. In the frames, the pill often contains:

- a small audio/AI glyph;
- a short command phrase;
- a blue border and pale blue fill;
- enough width to read the action without covering the target.

For Cortex, the live surface should be a cursor-adjacent command chip with
three plain actions:

- `Explain this`
- `What next?`
- `Remember this`

The full dashboard should not appear unless the user asks for the receipt book.

### 3. "This/That/These" Depends On Target History

The "Maintain the flow" and "This and That" clips show multi-step references:
the user can point to one ingredient, then another, then ask for a combined
operation. The system keeps a short target history so "and this" or "merge
these" has meaning.

For Cortex, the live state should keep a tiny target stack:

```text
current_target
previous_target
selected_targets[]
```

This is the missing bridge between a cursor follower and a usable AI pointer.

### 4. Output Appears Where It Will Be Used

The demo repeatedly places output adjacent to the relevant object:

- ingredients are added into the shopping list card;
- selected document rows are merged in place;
- a restaurant/time card appears beside the video frame;
- generated image edits appear in the canvas, not in a remote chat window.

For Cortex, the answer bubble should anchor to the target, but receipts should
stay small:

```text
target cue near work
plain answer near pointer
tiny "saved/blocked" receipt
Memory Book later
```

### 5. Some Actions Are Transactional, So Safety Needs A Review Layer

The booking example turns a paused video frame into a restaurant card with time
choices. This is exactly where Cortex must be stricter than the demo: an entity
card can be displayed, but booking/sending/buying/deleting remains blocked until
explicit review.

For Cortex, generated entity cards need two categories:

- safe display cards: explain, summarize, compare, identify, remember;
- gated action cards: book, send, buy, post, delete, change settings.

### 6. The System Hides Complexity Until Needed

The frames do not show a permanent dense control dashboard. Technical state is
mostly invisible until a small status/pill appears. Cortex should expose safety
state, but in a calmer way:

- pointer color/state;
- tiny lock label when capture/memory/action is blocked;
- one-line receipt after a turn;
- detailed logs only in developer view.

## Implementation Requirements For Cortex

The next live demo should implement these product behaviors before more
dashboard work:

1. Pointer follows near the user's pointer inside the controlled surface.
2. Hovering a UI object changes the understood target immediately.
3. A cursor-adjacent action chip updates to the current target.
4. "Explain this" resolves against the hovered target without the user typing
   the target name.
5. "What next?" uses the target plus current demo state.
6. "Remember this" creates a manual-memory proposal, not an automatic write.
7. The answer appears beside the target and the pointer.
8. The receipt is one child-readable line: what Cortex saw, what it did, what it
   did not do.
9. No clicks, typing, real screen capture, voice capture, raw refs, exports, or
   external effects occur in this safe local demo.

## Product Bar

If a user moves their cursor over `LUT Menu`, they should see Cortex visibly
understand:

```text
Cortex sees: LUT Menu
[Explain this] [What next?] [Remember this]
```

Clicking `Explain this` should produce:

```text
This opens look presets. I can explain it, but I will not click it for you.
Receipt: saw LUT Menu, answered safely, blocked click/capture/memory.
```

That is the product spine. Everything else is back office.
