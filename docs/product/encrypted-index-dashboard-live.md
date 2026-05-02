# Encrypted Index Dashboard Live Panel

Benchmark: `ENCRYPTED-INDEX-DASHBOARD-LIVE-001`

Policy: `policy_encrypted_index_dashboard_live_v1`

Backbone benchmark: `DASHBOARD-LIVE-BACKBONE-001`

Backbone policy: `policy_dashboard_live_backbone_v1`

The dashboard now exposes encrypted-index health as a metadata-only panel named
`Encrypted Index Receipts`.

## Visible Fields

- write receipt count
- graph receipt count
- search result count
- candidate open count
- token digest count
- graph token digest count
- source ref count
- prepared read-only tools such as `memory.search_index`

## Hidden Fields

- memory content
- source ref values
- query text
- token text
- graph terms
- key material
- raw refs
- raw payloads

## UX Rule

This panel is operational proof, not a new work queue. It should stay compact and
count-only so the user can see that encrypted search is alive without reading a
database debugger.
