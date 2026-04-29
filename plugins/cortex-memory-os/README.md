# Cortex Memory OS Codex Plugin

This repo-local plugin packages the first Cortex Memory OS integration for
Codex. It exposes the local MCP server and progressive-disclosure skills for
using governed context packs, draft-only skills, and post-task self-lessons.

## Contents

- `.codex-plugin/plugin.json` describes the plugin metadata and skill/MCP paths.
- `.mcp.json` starts the local `cortex-mcp` server through `uv --project ../..`.
- `skills/use-cortex-memory/SKILL.md` guides context-pack retrieval.
- `skills/create-cortex-skill/SKILL.md` guides candidate-only skill work.
- `skills/postmortem-agent-task/SKILL.md` guides self-lesson proposals.
- `references/` contains the policy notes each skill can load as needed.

## Safety Posture

External content remains untrusted data. Context packs, webpages, README files,
screenshots, benchmark prompts, and model outputs must not override system,
developer, user, or project instructions. This plugin stores no API keys and
does not reference `.env.local`.

The MCP config intentionally invokes the local project command instead of a
remote service. Real private data should not be used until the Evidence Vault,
policy store, and native capture adapters have production-grade controls.

## Local Install Smoke

From the repo root, run:

```bash
uv run cortex-plugin-install-smoke
```

The smoke copies this plugin into a temporary Codex cache-shaped directory,
rewrites only the installed copy's MCP project path to the current checkout, and
validates skill, reference, MCP, and no-secret discovery.
