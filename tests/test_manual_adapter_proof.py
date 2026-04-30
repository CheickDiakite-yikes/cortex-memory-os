from cortex_memory_os.manual_adapter_proof import (
    MANUAL_ADAPTER_PROOF_POLICY_REF,
    main,
    run_manual_adapter_proof,
)


def test_manual_adapter_proof_runs_terminal_hook_and_browser_payloads():
    result = run_manual_adapter_proof()

    assert result.passed
    assert result.policy_ref == MANUAL_ADAPTER_PROOF_POLICY_REF
    assert result.terminal_hook_return_code == 0
    assert result.terminal_event_observed is True
    assert result.terminal_secret_retained is False
    assert result.terminal_raw_ref_retained is False
    assert result.browser_extension_paths_checked is True
    assert result.browser_payload_status_code == 200
    assert result.browser_memory_eligible is False
    assert result.browser_raw_ref_retained is False
    assert result.browser_attack_status_code == 200
    assert result.browser_attack_discarded is True
    assert result.service_worker_localhost_only is True
    assert result.content_script_redaction_present is True
    assert result.stdout_redacted is True
    assert result.stderr_redacted is True


def test_manual_adapter_proof_cli_is_redacted(capsys):
    exit_code = main([])
    captured = capsys.readouterr().out

    assert exit_code == 0
    assert '"passed": true' in captured
    assert "CORTEX_FAKE_TOKEN" not in captured
