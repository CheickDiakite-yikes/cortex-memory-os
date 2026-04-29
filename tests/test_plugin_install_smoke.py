import json
from pathlib import Path

from cortex_memory_os.plugin_install_smoke import (
    BLOCKED_CONFIG_TERMS,
    PLUGIN_INSTALL_POLICY_REF,
    discover_installed_plugin,
    install_plugin_copy,
    run_plugin_install_smoke,
)


def test_plugin_install_smoke_discovers_installed_plugin(tmp_path: Path):
    result = run_plugin_install_smoke(codex_home=tmp_path)

    assert result.passed
    assert result.policy_ref == PLUGIN_INSTALL_POLICY_REF
    assert result.temporary_install is False
    assert result.install_path_shape_ok is True
    assert Path(result.installed_root).relative_to(tmp_path).parts[:4] == (
        "plugins",
        "cache",
        "local",
        "cortex-memory-os",
    )
    assert result.skill_names == [
        "create-cortex-skill",
        "postmortem-agent-task",
        "use-cortex-memory",
    ]
    assert result.reference_files == ["memory_policy.md", "safe_execution.md"]
    assert result.mcp_server_names == ["cortex-memory-os"]
    assert result.mcp_command == "uv"
    assert result.mcp_args[-2:] == ["run", "cortex-mcp"]
    assert result.mcp_project_path_exists is True
    assert result.blocked_config_hits == []
    assert result.missing_paths == []


def test_temporary_plugin_install_smoke_cleans_up_and_marks_temp():
    result = run_plugin_install_smoke()

    assert result.passed
    assert result.temporary_install is True
    assert not Path(result.codex_home).exists()


def test_installed_plugin_discovery_flags_secret_config(tmp_path: Path):
    installed_root = install_plugin_copy(codex_home=tmp_path)
    mcp_path = installed_root / ".mcp.json"
    mcp_config = json.loads(mcp_path.read_text(encoding="utf-8"))
    mcp_config["mcpServers"]["cortex-memory-os"]["env"]["OPENAI_API_KEY"] = "test-secret"
    mcp_path.write_text(json.dumps(mcp_config), encoding="utf-8")

    result = discover_installed_plugin(installed_root, codex_home=tmp_path)

    assert not result.passed
    assert result.blocked_config_hits == ["OPENAI_API_KEY"]
    assert "OPENAI_API_KEY" in BLOCKED_CONFIG_TERMS
