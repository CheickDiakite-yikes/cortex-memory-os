# OpenAI Tutor Live Smoke

Last updated: 2026-05-14

`OPENAI-TUTOR-SAFE-DRAFT-001` is the safe OpenAI seam for the pointer-first
live tutor. It lets us use a cheap capable model for short spatial guidance
while keeping the product loop synthetic, bounded, and auditable.

Policy ref: `policy_openai_tutor_safe_draft_v1`.

## Boundary

- Uses the OpenAI Responses API with `store:false`.
- Defaults to `gpt-5-nano` and minimal reasoning for low-cost, low-latency checks.
- Sends only controlled target facts from the localhost creative-tool demo.
- Sends no screenshots, no microphone audio, no Accessibility tree, no clipboard,
  no local files, no raw refs, and no durable memory content.
- Allows only display text and micro-steps beside the secondary cursor.
- Blocks click, type, export, capture start, memory write, and external effects.

## Commands

Dry run, no API key and no network:

```bash
uv run cortex-openai-tutor-smoke --json
```

Optional live run with an ignored local key:

```bash
uv run cortex-openai-tutor-smoke --live --json
```

The live run reads `OPENAI_API_KEY` from the environment or `.env.local`, but
the result is sanitized and never echoes the key. `.env.local` remains ignored
by git.

## Product Role

This is not real screen understanding yet. It is the thin, safe rung before
that: the model drafts one short explanation from structured demo state, then
Cortex renders it at the pointer with clear receipts. Real capture, voice, raw
refs, and durable memory writes stay off until separate consented gates pass.
