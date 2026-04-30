# Local Adapter Endpoint

Last updated: 2026-04-30

`LOCAL-ADAPTER-ENDPOINT-001` adds the first local HTTP ingest endpoint for the
live browser-extension and terminal-hook artifacts.

The endpoint is intentionally narrow:

- binds to `127.0.0.1` by default;
- rejects non-local client hosts with `client_host_not_allowed`;
- accepts only `POST /adapter/browser` and `POST /adapter/terminal`;
- limits request bodies to `MAX_ADAPTER_PAYLOAD_BYTES`;
- suppresses default HTTP request logging so payload text is not copied into
  local logs;
- returns redacted decision metadata, not raw page or terminal text.

## Browser Path

`POST /adapter/browser` accepts the visible-page payload emitted by
`adapters/browser-extension`.

Safety rules:

- browser payloads must stay `external_untrusted`;
- browser payloads must stay `third_party_content`;
- `dom_ref` and `raw_ref` are forbidden for live browser ingest;
- prompt-injection text is quarantined before evidence storage;
- browser content cannot become memory eligible through this endpoint.

## Terminal Path

`POST /adapter/terminal` accepts the command payload emitted by
`adapters/terminal-shell`.

Safety rules:

- terminal payloads must stay `local_observed`;
- `raw_ref` is forbidden for live terminal ingest;
- secret-like text is masked by the firewall handoff;
- endpoint responses never echo the command text.

## Smoke Command

```bash
uv run cortex-adapter-endpoint --smoke --json
```

The smoke starts a local server on `127.0.0.1:0`, posts synthetic browser,
browser-injection, and terminal-secret events, and checks:

- browser memory eligibility is false;
- browser raw refs are not retained;
- browser injection is discarded;
- terminal secrets are not retained;
- terminal raw refs are not retained;
- non-local client simulation is rejected;
- browser trust escalation is rejected;
- oversized payloads are rejected.

Policy reference: `policy_local_adapter_endpoint_v1`.
