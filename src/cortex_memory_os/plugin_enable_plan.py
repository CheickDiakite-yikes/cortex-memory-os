"""Approval-gated Codex plugin enable plan."""

from __future__ import annotations

import argparse
import json
import shutil
from enum import Enum
from pathlib import Path

from pydantic import Field

from cortex_memory_os.contracts import StrictModel
from cortex_memory_os.plugin_install_smoke import (
    BLOCKED_CONFIG_TERMS,
    DEFAULT_PLUGIN_ROOT,
    LOCAL_PLUGIN_CACHE_NAMESPACE,
    PLUGIN_INSTALL_POLICY_REF,
    REPO_ROOT,
    PluginInstallDiscovery,
    codex_cache_install_root,
    discover_installed_plugin,
    install_plugin_copy,
)

CODEX_PLUGIN_REAL_ENABLE_POLICY_REF = "policy_codex_plugin_real_enable_v1"
CODEX_PLUGIN_ENABLE_APPROVAL_PHRASE = "ENABLE CORTEX CODEX PLUGIN"


class PluginEnableMode(str, Enum):
    DRY_RUN = "dry_run"
    APPLY = "apply"


class PluginEnablePlan(StrictModel):
    policy_ref: str = CODEX_PLUGIN_REAL_ENABLE_POLICY_REF
    install_policy_ref: str = PLUGIN_INSTALL_POLICY_REF
    mode: PluginEnableMode
    plugin_name: str
    plugin_version: str
    plugin_root: str
    repo_root: str
    codex_home: str
    target_install_root: str
    cache_namespace: str = LOCAL_PLUGIN_CACHE_NAMESPACE
    required_approval_phrase: str = CODEX_PLUGIN_ENABLE_APPROVAL_PHRASE
    user_confirmation_observed: bool
    would_modify_codex_home: bool
    applied: bool
    temporary_validation: bool
    preflight_checks: dict[str, bool] = Field(default_factory=dict)
    blocked_config_hits: list[str] = Field(default_factory=list)
    blocked_reasons: list[str] = Field(default_factory=list)
    install_steps: list[str] = Field(min_length=1)
    rollback_steps: list[str] = Field(min_length=1)
    discovery: PluginInstallDiscovery | None = None
    passed: bool
    notes: list[str] = Field(default_factory=list)


def build_plugin_enable_plan(
    *,
    plugin_root: Path = DEFAULT_PLUGIN_ROOT,
    repo_root: Path = REPO_ROOT,
    codex_home: Path | None = None,
    mode: PluginEnableMode = PluginEnableMode.DRY_RUN,
    user_confirmation: str | None = None,
    version: str = "0.1.0",
) -> PluginEnablePlan:
    codex_home = (codex_home or Path.home() / ".codex").expanduser()
    manifest_path = plugin_root / ".codex-plugin" / "plugin.json"
    mcp_path = plugin_root / ".mcp.json"
    manifest = _load_json(manifest_path) if manifest_path.exists() else {}
    plugin_name = str(manifest.get("name", "cortex-memory-os"))
    plugin_version = str(manifest.get("version", version))
    target_install_root = codex_cache_install_root(
        codex_home,
        plugin_name=plugin_name,
        version=version,
    )
    source_config_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [manifest_path, mcp_path]
        if path.exists()
    )
    blocked_config_hits = [
        term for term in BLOCKED_CONFIG_TERMS if term.lower() in source_config_text.lower()
    ]
    user_confirmation_observed = user_confirmation == CODEX_PLUGIN_ENABLE_APPROVAL_PHRASE
    preflight_checks = {
        "plugin_root_exists": plugin_root.exists(),
        "manifest_exists": manifest_path.exists(),
        "mcp_exists": mcp_path.exists(),
        "repo_root_exists": repo_root.exists(),
        "target_inside_codex_home": _is_within(target_install_root, codex_home),
        "source_config_secret_free": not blocked_config_hits,
    }
    blocked_reasons = [
        key for key, passed in preflight_checks.items() if not passed
    ]
    if mode == PluginEnableMode.APPLY and not user_confirmation_observed:
        blocked_reasons.append("user_confirmation_required")

    discovery: PluginInstallDiscovery | None = None
    applied = False
    if mode == PluginEnableMode.APPLY and not blocked_reasons:
        installed_root = install_plugin_copy(
            plugin_root=plugin_root,
            codex_home=codex_home,
            repo_root=repo_root,
            version=version,
        )
        discovery = discover_installed_plugin(installed_root, codex_home=codex_home)
        applied = discovery.passed
        if not discovery.passed:
            blocked_reasons.append("installed_plugin_discovery_failed")

    passed = not blocked_reasons and (
        mode == PluginEnableMode.DRY_RUN or (applied and discovery is not None)
    )
    return PluginEnablePlan(
        mode=mode,
        plugin_name=plugin_name,
        plugin_version=plugin_version,
        plugin_root=str(plugin_root),
        repo_root=str(repo_root),
        codex_home=str(codex_home),
        target_install_root=str(target_install_root),
        user_confirmation_observed=user_confirmation_observed,
        would_modify_codex_home=mode == PluginEnableMode.APPLY,
        applied=applied,
        temporary_validation=codex_home.name.startswith("cortex-codex-home-")
        or str(codex_home).startswith("/tmp/"),
        preflight_checks=preflight_checks,
        blocked_config_hits=blocked_config_hits,
        blocked_reasons=blocked_reasons,
        install_steps=[
            "Run preflight checks against the repo-local plugin manifest and MCP config.",
            "Require the exact approval phrase before writing to Codex home.",
            f"Copy plugin into {target_install_root}.",
            "Rewrite only the installed MCP config project path to this checkout.",
            "Discover installed skills, references, and MCP server metadata.",
        ],
        rollback_steps=[
            f"Remove {target_install_root}.",
            "Re-run plugin discovery to confirm the Cortex plugin is absent.",
            "Leave repo-local plugin files and user secrets untouched.",
        ],
        discovery=discovery,
        passed=passed,
        notes=_notes(mode, applied, user_confirmation_observed),
    )


def remove_enabled_plugin(
    *,
    codex_home: Path,
    plugin_name: str = "cortex-memory-os",
    version: str = "0.1.0",
) -> Path:
    target = codex_cache_install_root(codex_home, plugin_name=plugin_name, version=version)
    _is_within_or_raise(target, codex_home)
    if target.exists():
        shutil.rmtree(target)
    return target


def _notes(
    mode: PluginEnableMode,
    applied: bool,
    user_confirmation_observed: bool,
) -> list[str]:
    if mode == PluginEnableMode.DRY_RUN:
        return ["dry run only; no Codex home writes performed"]
    if not user_confirmation_observed:
        return ["apply mode blocked until exact approval phrase is supplied"]
    if applied:
        return ["plugin copied into Codex cache-shaped path and discovered"]
    return ["apply mode attempted but discovery did not pass"]


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def _is_within_or_raise(path: Path, parent: Path) -> None:
    path.resolve().relative_to(parent.resolve())


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plugin-root", type=Path, default=DEFAULT_PLUGIN_ROOT)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--codex-home", type=Path)
    parser.add_argument("--version", default="0.1.0")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--approval-phrase")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    result = build_plugin_enable_plan(
        plugin_root=args.plugin_root,
        repo_root=args.repo_root,
        codex_home=args.codex_home,
        mode=PluginEnableMode.APPLY if args.apply else PluginEnableMode.DRY_RUN,
        user_confirmation=args.approval_phrase,
        version=args.version,
    )
    if args.json:
        print(result.model_dump_json(indent=2))
    else:
        status = "passed" if result.passed else "blocked"
        print(f"Cortex plugin real-enable plan {status}")
        print(f"mode={result.mode.value}")
        print(f"target_install_root={result.target_install_root}")
        if result.blocked_reasons:
            print(f"blocked_reasons={', '.join(result.blocked_reasons)}")
        if result.notes:
            print(f"notes={'; '.join(result.notes)}")
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
