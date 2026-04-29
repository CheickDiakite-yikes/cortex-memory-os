"""Local Codex plugin install and discovery smoke test."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from pydantic import Field

from cortex_memory_os.contracts import StrictModel

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PLUGIN_ROOT = REPO_ROOT / "plugins" / "cortex-memory-os"
PLUGIN_INSTALL_POLICY_REF = "policy_codex_plugin_install_smoke_v1"
LOCAL_PLUGIN_CACHE_NAMESPACE = "local"

BLOCKED_CONFIG_TERMS = (
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "ASSEMBLYAI_API_KEY",
    "ELEVENLABS_API_KEY",
    "sk-",
    "ghp_",
    "gho_",
    ".env.local",
    "raw://",
    "encrypted_blob://",
    "benchmarks/runs",
    "private_key",
    "password=",
)


class PluginInstallDiscovery(StrictModel):
    policy_ref: str = PLUGIN_INSTALL_POLICY_REF
    codex_home: str
    installed_root: str
    manifest_path: str
    mcp_path: str
    plugin_name: str
    plugin_version: str
    skill_names: list[str] = Field(default_factory=list)
    reference_files: list[str] = Field(default_factory=list)
    mcp_server_names: list[str] = Field(default_factory=list)
    mcp_command: str | None = None
    mcp_args: list[str] = Field(default_factory=list)
    mcp_project_path: str | None = None
    blocked_config_hits: list[str] = Field(default_factory=list)
    missing_paths: list[str] = Field(default_factory=list)
    install_path_shape_ok: bool
    mcp_project_path_exists: bool
    temporary_install: bool
    passed: bool
    notes: list[str] = Field(default_factory=list)


def codex_cache_install_root(
    codex_home: Path,
    *,
    plugin_name: str = "cortex-memory-os",
    version: str = "0.1.0",
) -> Path:
    return (
        codex_home
        / "plugins"
        / "cache"
        / LOCAL_PLUGIN_CACHE_NAMESPACE
        / plugin_name
        / version
    )


def install_plugin_copy(
    *,
    plugin_root: Path = DEFAULT_PLUGIN_ROOT,
    codex_home: Path,
    repo_root: Path = REPO_ROOT,
    version: str = "0.1.0",
    replace: bool = True,
) -> Path:
    manifest = _load_json(plugin_root / ".codex-plugin" / "plugin.json")
    plugin_name = str(manifest.get("name", "cortex-memory-os"))
    installed_root = codex_cache_install_root(
        codex_home,
        plugin_name=plugin_name,
        version=version,
    )
    _assert_within(installed_root, codex_home)
    if replace and installed_root.exists():
        shutil.rmtree(installed_root)
    shutil.copytree(
        plugin_root,
        installed_root,
        ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"),
    )
    _rewrite_installed_mcp_project_path(installed_root, repo_root)
    return installed_root


def discover_installed_plugin(
    installed_root: Path,
    *,
    codex_home: Path,
) -> PluginInstallDiscovery:
    manifest_path = installed_root / ".codex-plugin" / "plugin.json"
    manifest = _load_json(manifest_path) if manifest_path.exists() else {}
    plugin_name = str(manifest.get("name", ""))
    plugin_version = str(manifest.get("version", ""))

    skills_path = _resolve_manifest_path(installed_root, manifest.get("skills"))
    mcp_path = _resolve_manifest_path(installed_root, manifest.get("mcpServers"))
    references_path = installed_root / "references"

    missing_paths = [
        str(path.relative_to(installed_root))
        for path in [manifest_path, skills_path, mcp_path, references_path]
        if not path.exists()
    ]

    skill_names = _discover_skill_names(skills_path) if skills_path.exists() else []
    reference_files = (
        sorted(path.name for path in references_path.glob("*.md"))
        if references_path.exists()
        else []
    )
    mcp_config = _load_json(mcp_path) if mcp_path.exists() else {}
    mcp_servers = mcp_config.get("mcpServers", {})
    mcp_server_names = sorted(mcp_servers)
    cortex_server = mcp_servers.get("cortex-memory-os", {})
    mcp_command = cortex_server.get("command")
    mcp_args = [str(arg) for arg in cortex_server.get("args", [])]
    mcp_project_path = _mcp_project_path(mcp_args)

    config_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [manifest_path, mcp_path]
        if path.exists()
    )
    blocked_config_hits = [
        term for term in BLOCKED_CONFIG_TERMS if term.lower() in config_text.lower()
    ]
    install_path_shape_ok = _is_cache_shaped_install(installed_root, codex_home)
    mcp_project_path_exists = bool(
        mcp_project_path and Path(mcp_project_path).expanduser().exists()
    )

    notes = []
    if install_path_shape_ok:
        notes.append("installed under plugins/cache/local/<name>/<version>")
    if mcp_project_path_exists:
        notes.append("installed MCP config points to an existing local project")
    if not blocked_config_hits:
        notes.append("manifest and MCP config contain no blocked secret/raw-data terms")

    passed = (
        plugin_name == "cortex-memory-os"
        and bool(plugin_version)
        and not missing_paths
        and set(skill_names)
        == {"create-cortex-skill", "postmortem-agent-task", "use-cortex-memory"}
        and set(reference_files) == {"memory_policy.md", "safe_execution.md"}
        and mcp_server_names == ["cortex-memory-os"]
        and mcp_command == "uv"
        and mcp_args[-2:] == ["run", "cortex-mcp"]
        and mcp_project_path_exists
        and not blocked_config_hits
        and install_path_shape_ok
    )
    return PluginInstallDiscovery(
        codex_home=str(codex_home),
        installed_root=str(installed_root),
        manifest_path=str(manifest_path),
        mcp_path=str(mcp_path),
        plugin_name=plugin_name,
        plugin_version=plugin_version,
        skill_names=skill_names,
        reference_files=reference_files,
        mcp_server_names=mcp_server_names,
        mcp_command=mcp_command,
        mcp_args=mcp_args,
        mcp_project_path=mcp_project_path,
        blocked_config_hits=blocked_config_hits,
        missing_paths=missing_paths,
        install_path_shape_ok=install_path_shape_ok,
        mcp_project_path_exists=mcp_project_path_exists,
        temporary_install=False,
        passed=passed,
        notes=notes,
    )


def run_plugin_install_smoke(
    *,
    plugin_root: Path = DEFAULT_PLUGIN_ROOT,
    repo_root: Path = REPO_ROOT,
    codex_home: Path | None = None,
    version: str = "0.1.0",
) -> PluginInstallDiscovery:
    if codex_home is None:
        with TemporaryDirectory(prefix="cortex-codex-home-") as tmpdir:
            result = _install_and_discover(
                plugin_root=plugin_root,
                repo_root=repo_root,
                codex_home=Path(tmpdir),
                version=version,
            )
            return result.model_copy(update={"temporary_install": True})
    return _install_and_discover(
        plugin_root=plugin_root,
        repo_root=repo_root,
        codex_home=codex_home,
        version=version,
    )


def _install_and_discover(
    *,
    plugin_root: Path,
    repo_root: Path,
    codex_home: Path,
    version: str,
) -> PluginInstallDiscovery:
    installed_root = install_plugin_copy(
        plugin_root=plugin_root,
        codex_home=codex_home,
        repo_root=repo_root,
        version=version,
    )
    return discover_installed_plugin(installed_root, codex_home=codex_home)


def _rewrite_installed_mcp_project_path(installed_root: Path, repo_root: Path) -> None:
    mcp_path = installed_root / ".mcp.json"
    mcp_config = _load_json(mcp_path)
    for server in mcp_config.get("mcpServers", {}).values():
        args = [str(arg) for arg in server.get("args", [])]
        if "--project" in args:
            project_index = args.index("--project") + 1
            if project_index < len(args):
                args[project_index] = str(repo_root)
        elif server.get("command") == "uv":
            args = ["--project", str(repo_root), *args]
        server["args"] = args
    mcp_path.write_text(json.dumps(mcp_config, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _discover_skill_names(skills_path: Path) -> list[str]:
    names = []
    for skill_file in sorted(skills_path.glob("*/SKILL.md")):
        explicit_name = _frontmatter_name(skill_file)
        names.append(explicit_name or skill_file.parent.name)
    return names


def _frontmatter_name(skill_file: Path) -> str | None:
    lines = skill_file.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            return None
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip()
    return None


def _resolve_manifest_path(installed_root: Path, value: Any) -> Path:
    if not isinstance(value, str) or not value:
        return installed_root / "__missing_manifest_path__"
    path = Path(value)
    return path if path.is_absolute() else installed_root / path


def _mcp_project_path(args: list[str]) -> str | None:
    if "--project" not in args:
        return None
    project_index = args.index("--project") + 1
    if project_index >= len(args):
        return None
    return args[project_index]


def _is_cache_shaped_install(installed_root: Path, codex_home: Path) -> bool:
    try:
        rel_parts = installed_root.relative_to(codex_home).parts
    except ValueError:
        return False
    return (
        len(rel_parts) == 5
        and rel_parts[0] == "plugins"
        and rel_parts[1] == "cache"
        and rel_parts[2] == LOCAL_PLUGIN_CACHE_NAMESPACE
    )


def _assert_within(path: Path, parent: Path) -> None:
    path.resolve().relative_to(parent.resolve())


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plugin-root", type=Path, default=DEFAULT_PLUGIN_ROOT)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--codex-home", type=Path)
    parser.add_argument("--version", default="0.1.0")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    result = run_plugin_install_smoke(
        plugin_root=args.plugin_root,
        repo_root=args.repo_root,
        codex_home=args.codex_home,
        version=args.version,
    )
    if args.json:
        print(result.model_dump_json(indent=2))
    else:
        status = "passed" if result.passed else "failed"
        print(f"Cortex plugin install smoke {status}")
        print(f"installed_root={result.installed_root}")
        print(f"skills={', '.join(result.skill_names)}")
        print(f"mcp_project_path={result.mcp_project_path}")
        if result.blocked_config_hits:
            print(f"blocked_config_hits={', '.join(result.blocked_config_hits)}")
        if result.missing_paths:
            print(f"missing_paths={', '.join(result.missing_paths)}")
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
