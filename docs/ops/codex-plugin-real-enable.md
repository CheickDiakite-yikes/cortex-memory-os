# Codex Plugin Real Enable Path

Last updated: 2026-04-30

Benchmark: `CODEX-PLUGIN-REAL-ENABLE-001`

Policy reference: `policy_codex_plugin_real_enable_v1`

This slice validates the real Codex plugin enable path without silently
modifying the user's actual `~/.codex` tree. The default command is a dry run.
Apply mode requires the exact approval phrase:

```text
ENABLE CORTEX CODEX PLUGIN
```

## Command Surface

```bash
uv run cortex-plugin-enable-plan --json
uv run cortex-plugin-enable-plan --apply --approval-phrase "ENABLE CORTEX CODEX PLUGIN" --codex-home <approved-codex-home> --json
```

The tests use a temporary Codex home. Real user config changes must remain
deliberate and visible. Real user config changes must remain deliberate.

## Preflight Checks

The plan verifies:

- repo-local plugin root exists;
- `.codex-plugin/plugin.json` exists;
- `.mcp.json` exists;
- repo root exists;
- target install root is inside the selected Codex home;
- source manifest and MCP config contain no blocked secret, raw-ref, or
  benchmark-artifact terms.

The source `.mcp.json` stays relative. Only the installed copy rewrites
`--project` to the current checkout.

## Install Shape

Apply mode copies the plugin into:

```text
<codex-home>/plugins/cache/local/cortex-memory-os/0.1.0/
```

The installed plugin is then rediscovered with the existing
`PLUGIN-INSTALL-SMOKE-001` discovery contract.

## Rollback

The rollback path is explicit:

```bash
rm -rf <codex-home>/plugins/cache/local/cortex-memory-os/0.1.0
```

Then rediscover installed plugins to confirm the Cortex plugin is absent.
Rollback must not touch repo-local plugin files, `.env.local`, API keys, raw
private memories, local databases, benchmark artifacts, or user settings.

## Safety Boundary

This does not enable autonomous memory writes or capture. It only validates that
the Codex plugin package can be deliberately installed, discovered, and removed
through an approval-gated path.
