# Optional OpenAI Live Smoke

Last updated: 2026-04-29

`LIVE-OPENAI-SMOKE-001` adds an optional live validation command for local
development. It is intentionally outside the default benchmark gate because it
uses a real API key and network call.

## Secret Handling

- Put local credentials in `.env.local`.
- `.env.local` is ignored by `.gitignore` through `.env.*`.
- Commit only `.env.example`, never `.env.local`.
- The smoke command prints the key source, model, response ID, output text, and
  usage metadata, but never prints the API key.
- Requests set `store: false`.
- Requests default to minimal reasoning effort so the tiny sentinel prompt does
  not burn its whole output budget on reasoning tokens.

## Default Model

The default model is `gpt-5-nano`, chosen for low-cost live smoke testing. You
can override it locally:

```bash
CORTEX_LIVE_OPENAI_MODEL=gpt-5.4-nano
```

or with:

```bash
uv run cortex-openai-smoke --model gpt-5.4-nano --dry-run
```

## Commands

Dry run, no network:

```bash
uv run cortex-openai-smoke --dry-run
```

Live run:

```bash
uv run cortex-openai-smoke --assert-contains CORTEX_LIVE_OK
```

The live prompt is a tiny deterministic smoke prompt and should not include
private memories, raw observations, local files, terminal output, or user data.
