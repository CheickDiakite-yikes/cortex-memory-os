from pathlib import Path

from cortex_memory_os.plugin_enable_plan import (
    CODEX_PLUGIN_ENABLE_APPROVAL_PHRASE,
    CODEX_PLUGIN_REAL_ENABLE_POLICY_REF,
    PluginEnableMode,
    build_plugin_enable_plan,
    remove_enabled_plugin,
)


def test_plugin_enable_plan_dry_run_does_not_write_codex_home(tmp_path: Path):
    result = build_plugin_enable_plan(codex_home=tmp_path)

    assert result.passed
    assert result.policy_ref == CODEX_PLUGIN_REAL_ENABLE_POLICY_REF
    assert result.mode == PluginEnableMode.DRY_RUN
    assert result.applied is False
    assert result.would_modify_codex_home is False
    assert result.user_confirmation_observed is False
    assert result.blocked_config_hits == []
    assert result.blocked_reasons == []
    assert not Path(result.target_install_root).exists()
    assert "dry run only" in result.notes[0]


def test_plugin_enable_plan_apply_requires_exact_user_confirmation(tmp_path: Path):
    result = build_plugin_enable_plan(
        codex_home=tmp_path,
        mode=PluginEnableMode.APPLY,
        user_confirmation="yes please",
    )

    assert result.passed is False
    assert result.applied is False
    assert result.would_modify_codex_home is True
    assert result.user_confirmation_observed is False
    assert "user_confirmation_required" in result.blocked_reasons
    assert not Path(result.target_install_root).exists()


def test_plugin_enable_plan_apply_discovers_and_rolls_back_temp_install(tmp_path: Path):
    result = build_plugin_enable_plan(
        codex_home=tmp_path,
        mode=PluginEnableMode.APPLY,
        user_confirmation=CODEX_PLUGIN_ENABLE_APPROVAL_PHRASE,
    )

    assert result.passed
    assert result.applied is True
    assert result.user_confirmation_observed is True
    assert result.discovery is not None
    assert result.discovery.passed
    assert result.discovery.skill_names == [
        "create-cortex-skill",
        "postmortem-agent-task",
        "use-cortex-memory",
    ]
    assert Path(result.target_install_root).exists()
    assert result.rollback_steps[0].startswith("Remove ")

    removed = remove_enabled_plugin(codex_home=tmp_path)

    assert removed == Path(result.target_install_root)
    assert not removed.exists()
