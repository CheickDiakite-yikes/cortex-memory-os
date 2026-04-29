# Cortex Plugin Install Smoke

Last updated: 2026-04-29

`PLUGIN-INSTALL-SMOKE-001` validates that the repo-local Cortex Codex plugin can
be copied into a Codex plugin cache-shaped directory and discovered from the
installed location. The policy reference is
`policy_codex_plugin_install_smoke_v1`.

The smoke is local-first and does not modify the user's real `~/.codex` tree
unless a caller explicitly passes `--codex-home`.

## Install Shape

The smoke uses the same observed cache shape as installed Codex plugins:

```text
<codex-home>/plugins/cache/local/cortex-memory-os/0.1.0/
```

Inside that directory it expects:

- `.codex-plugin/plugin.json`
- `.mcp.json`
- `skills/*/SKILL.md`
- `references/*.md`

## MCP Rewrite

The source plugin keeps a repo-local `.mcp.json` with
`uv --project ../.. run cortex-mcp`. During the smoke, only the installed copy
is rewritten to point `--project` at the current checkout. This avoids
committing absolute local paths while proving the installed plugin can start the
local Cortex MCP command.

## Safety Checks

The smoke validates that:

- the manifest discovers the expected plugin name and version;
- the installed path matches `plugins/cache/local/<name>/<version>`;
- all three progressive-disclosure skills are discoverable;
- the memory and safe-execution references are present;
- the MCP server is named `cortex-memory-os` and runs `uv ... run cortex-mcp`;
- the installed MCP project path exists;
- manifest and MCP config contain no API-key, private-key, raw evidence, or
  benchmark-artifact path markers.

## Commands

```bash
uv run cortex-plugin-install-smoke
uv run cortex-plugin-install-smoke --json
```

The default command uses a temporary Codex home and cleans it up. Use
`--codex-home <path>` only for deliberate local install experiments.
