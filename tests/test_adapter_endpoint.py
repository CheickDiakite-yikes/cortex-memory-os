from cortex_memory_os.adapter_endpoint import (
    ADAPTER_BROWSER_PATH,
    ADAPTER_TERMINAL_PATH,
    LOCAL_ADAPTER_ENDPOINT_POLICY_REF,
    _browser_payload,
    _post_json,
    _terminal_payload,
    client_host_allowed,
    ingest_adapter_payload,
    main,
    run_local_adapter_endpoint_smoke,
    start_local_adapter_endpoint,
)


def test_local_adapter_endpoint_smoke_passes():
    result = run_local_adapter_endpoint_smoke()

    assert result.passed
    assert result.policy_ref == LOCAL_ADAPTER_ENDPOINT_POLICY_REF
    assert result.bind_host == "127.0.0.1"
    assert result.browser_status_code == 200
    assert result.browser_memory_eligible is False
    assert result.browser_raw_ref_retained is False
    assert result.browser_attack_status_code == 200
    assert result.browser_attack_discarded is True
    assert result.terminal_status_code == 200
    assert result.terminal_secret_retained is False
    assert result.terminal_raw_ref_retained is False
    assert result.remote_rejected_status_code == 403
    assert result.trust_escalation_rejected_status_code == 422
    assert result.oversized_payload_status_code == 413


def test_endpoint_rejects_non_local_clients():
    result = ingest_adapter_payload(
        path=ADAPTER_BROWSER_PATH,
        payload=_browser_payload(),
        client_host="198.51.100.2",
    )

    assert result.accepted is False
    assert result.status_code == 403
    assert result.error_code == "client_host_not_allowed"


def test_browser_endpoint_rejects_trust_escalation_and_raw_refs():
    escalated = ingest_adapter_payload(
        path=ADAPTER_BROWSER_PATH,
        payload={**_browser_payload(), "source_trust": "local_observed"},
        client_host="127.0.0.1",
    )
    raw_ref = ingest_adapter_payload(
        path=ADAPTER_BROWSER_PATH,
        payload={**_browser_payload(), "dom_ref": "raw://browser/dom/leak"},
        client_host="127.0.0.1",
    )

    assert escalated.accepted is False
    assert escalated.status_code == 422
    assert escalated.error_code == "browser_source_trust_escalation"
    assert raw_ref.accepted is False
    assert raw_ref.status_code == 422
    assert raw_ref.error_code == "browser_raw_ref_forbidden"


def test_browser_endpoint_accepts_visible_shadow_clicker_metadata_without_memory():
    result = ingest_adapter_payload(
        path=ADAPTER_BROWSER_PATH,
        payload={
            **_browser_payload(),
            "action": "click",
            "target_label": "Google News headline",
            "pointer_x": 320,
            "pointer_y": 240,
            "shadow_pointer_visible": True,
        },
        client_host="127.0.0.1",
    )

    assert result.accepted is True
    assert result.status_code == 200
    assert result.adapter_source == "browser"
    assert result.eligible_for_memory is False
    assert result.raw_ref_retained is False


def test_terminal_endpoint_redacts_secrets_and_rejects_raw_refs():
    accepted = ingest_adapter_payload(
        path=ADAPTER_TERMINAL_PATH,
        payload=_terminal_payload(),
        client_host="127.0.0.1",
    )
    raw_ref = ingest_adapter_payload(
        path=ADAPTER_TERMINAL_PATH,
        payload={**_terminal_payload(), "raw_ref": "raw://terminal/leak"},
        client_host="127.0.0.1",
    )

    assert accepted.accepted is True
    assert accepted.firewall_decision == "mask"
    assert accepted.secret_retained is False
    assert accepted.raw_ref_retained is False
    assert raw_ref.accepted is False
    assert raw_ref.status_code == 422
    assert raw_ref.error_code == "terminal_raw_ref_forbidden"


def test_endpoint_cli_smoke_is_redacted(capsys):
    exit_code = main(["--smoke"])
    captured = capsys.readouterr().out

    assert exit_code == 0
    assert '"passed": true' in captured
    assert "CORTEX_FAKE_TOKEN" not in captured


def test_endpoint_results_are_aggregate_only_for_live_browser_proof():
    endpoint = start_local_adapter_endpoint(port=0)
    try:
        _post_json(f"{endpoint.base_url}{ADAPTER_BROWSER_PATH}", _browser_payload())
        results = endpoint.server.results()
    finally:
        endpoint.stop()

    assert results.accepted_count == 1
    assert results.browser_ingest_count == 1
    assert results.memory_eligible_count == 0
    assert results.raw_ref_retained_count == 0
    assert results.external_browser_evidence_only is True
    assert results.raw_payloads_included is False


def test_allowed_client_hosts_are_tight():
    assert client_host_allowed("127.0.0.1")
    assert client_host_allowed("::1")
    assert client_host_allowed("localhost")
    assert not client_host_allowed("0.0.0.0")
    assert not client_host_allowed("192.168.1.10")
