import json

from cortex_memory_os.live_readiness import (
    LIVE_READINESS_HARDENING_ID,
    inspect_env_local_hygiene,
    main,
    run_live_readiness,
)


def test_live_readiness_runs_bounded_hardening_checks():
    result = run_live_readiness()
    checks = {check.name: check for check in result.checks}

    assert result.benchmark_id == LIVE_READINESS_HARDENING_ID
    assert result.passed
    assert result.secret_hygiene.ignored_by_git
    assert not result.secret_hygiene.tracked_by_git
    assert not result.secret_hygiene.secret_values_read
    assert checks["env_local_secret_hygiene"].passed
    assert checks["live_adapter_artifacts"].passed
    assert checks["local_adapter_endpoint"].passed
    assert checks["manual_adapter_proof"].passed
    assert checks["openai_live_smoke"].passed
    assert checks["openai_live_smoke"].details["status"] == "skipped"


def test_live_readiness_openai_dry_run_does_not_return_secret(monkeypatch):
    monkeypatch.setenv("_".join(["OPENAI", "API", "KEY"]), "unit-test-key-redacted")

    result = run_live_readiness(include_openai=True)
    payload = result.model_dump_json()
    openai_check = next(check for check in result.checks if check.name == "openai_live_smoke")

    assert result.passed
    assert openai_check.passed
    assert openai_check.details["status"] == "dry_run"
    assert openai_check.details["store_false"] is True
    assert "unit-test-key-redacted" not in payload


def test_env_local_hygiene_never_reads_secret_values():
    hygiene = inspect_env_local_hygiene()

    assert hygiene.path == ".env.local"
    assert hygiene.ignored_by_git
    assert not hygiene.tracked_by_git
    assert not hygiene.secret_values_read


def test_live_readiness_cli_outputs_redacted_json(monkeypatch, capsys):
    monkeypatch.setenv("_".join(["OPENAI", "API", "KEY"]), "unit-test-key-redacted")

    exit_code = main(["--include-openai", "--json"])
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert exit_code == 0
    assert payload["passed"] is True
    assert "unit-test-key-redacted" not in output
    assert payload["benchmark_id"] == LIVE_READINESS_HARDENING_ID
