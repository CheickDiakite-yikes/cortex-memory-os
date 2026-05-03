import json

from cortex_memory_os.live_adapters import (
    DEFAULT_BROWSER_EXTENSION_ROOT,
    DEFAULT_TERMINAL_HOOK_PATH,
    LIVE_ADAPTER_POLICY_REF,
    REPO_ROOT,
    main,
    run_live_adapter_smoke,
)


def test_live_adapter_smoke_passes_without_raw_web_memory_or_terminal_secret():
    result = run_live_adapter_smoke()

    assert result.passed
    assert result.policy_ref == LIVE_ADAPTER_POLICY_REF
    assert result.missing_paths == []
    assert result.missing_terms == []
    assert result.blocked_host_permissions == []
    assert result.browser_memory_eligible is False
    assert result.browser_raw_ref_retained is False
    assert result.browser_attack_discarded is True
    assert result.terminal_secret_retained is False
    assert result.terminal_raw_ref_retained is False


def test_browser_manifest_is_click_gated_and_localhost_only():
    manifest = json.loads(
        (DEFAULT_BROWSER_EXTENSION_ROOT / "manifest.json").read_text(encoding="utf-8")
    )
    service_worker = (DEFAULT_BROWSER_EXTENSION_ROOT / "service-worker.js").read_text(
        encoding="utf-8"
    )

    assert manifest["manifest_version"] == 3
    assert manifest["permissions"] == ["activeTab", "scripting", "storage"]
    assert manifest["host_permissions"] == ["http://127.0.0.1/*", "http://localhost/*"]
    assert manifest["commands"]["_execute_action"]["suggested_key"]["mac"] == "Alt+Shift+C"
    assert "chrome.action.onClicked" in service_worker
    assert "cortexEnabled: true" in service_worker
    assert "endpointAllowed" in service_worker
    assert "source_trust: \"external_untrusted\"" in service_worker
    assert "raw_ref: null" in service_worker


def test_browser_content_script_draws_visible_shadow_pointer_receipt():
    content_script = (DEFAULT_BROWSER_EXTENSION_ROOT / "content-script.js").read_text(
        encoding="utf-8"
    )

    assert "Cortex Shadow Pointer" in content_script
    assert "Shadow Pointer Live Receipt" in content_script
    assert "cortex-cursor-svg" in content_script
    assert "cortex-click-ring" in content_script
    assert "cortex-pointer-chip" in content_script
    assert "pointermove" in content_script
    assert "shadow_pointer_visible" in content_script
    assert "eligible_for_memory" in content_script
    assert "raw_ref_retained" in content_script
    assert "data-cortex-policy" in content_script


def test_terminal_hook_is_opt_in_local_only_and_redacting():
    hook_text = DEFAULT_TERMINAL_HOOK_PATH.read_text(encoding="utf-8")

    assert "CORTEX_TERMINAL_OBSERVER=1" in hook_text
    assert "http://127.0.0.1:*" in hook_text
    assert "http://localhost:*" in hook_text
    assert "cortex_terminal_redact" in hook_text
    assert "[REDACTED_SECRET]" in hook_text
    assert '"raw_ref": None' in hook_text
    assert "add-zsh-hook preexec" in hook_text
    assert "add-zsh-hook precmd" in hook_text


def test_live_adapter_smoke_cli_returns_success(capsys):
    exit_code = main([])
    captured = capsys.readouterr().out

    assert exit_code == 0
    assert '"passed": true' in captured
    assert "CORTEX_FAKE_TOKEN" not in captured
    assert str(REPO_ROOT) not in captured
