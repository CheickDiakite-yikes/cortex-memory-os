# Key Management Plan

Benchmark: `KEY-MANAGEMENT-PLAN-001`

Policy: `policy_key_management_plan_v1`

This plan defines the production key lifecycle required before Cortex stores
private real memory or raw evidence. It is a contract only: it contains key
references, lifecycle steps, and audit requirements, never key material.

## Key Classes

| Class | Purpose | Production boundary |
| --- | --- | --- |
| `memory_payload` | Seal durable `MemoryRecord` payload JSON. | OS-backed keychain or managed KMS/HSM key ref. |
| `graph_edge_payload` | Seal temporal graph edge payload JSON. | Separate wrapped key ref from memory payloads. |
| `hmac_index` | Derive redacted token digests for search. | Separate HMAC key ref, rotated independently. |
| `evidence_blob` | Seal short-retention raw evidence blobs. | Separate evidence key ref with expiry/delete receipts. |

## Lifecycle

Required steps:

1. `generate_wrapped_key`
2. `activate_key_version`
3. `rotate_key_version`
4. `revoke_key_version`
5. `delete_key_version`

Required audit events:

- `key.created`
- `key.activated`
- `key.rotated`
- `key.revoked`
- `key.deleted`

## Gates

- Production cannot use `noop-dev` ciphers.
- `.env.local` cannot hold production key material.
- Key material cannot appear in dashboard payloads, benchmark artifacts, logs,
  commits, or receipts.
- Memory payload, graph edge, HMAC index, and evidence blob keys cannot be reused
  across material classes.
- Deleting a key version must leave a redacted tombstone audit without a
  decryptable payload.

## macOS Keychain Adapter

`KEYCHAIN-KEY-ADAPTER-001` adds the first macOS Keychain provider contract.
The smoke is read-only: it detects the native backend, returns metadata-only
key refs for each key class, and does not create Keychain items.

Required safety behavior:

- no raw key material is returned;
- no `.env` secret fallback is allowed;
- no production no-op cipher is allowed;
- key refs remain separated across `memory_payload`, `graph_edge_payload`,
  `hmac_index`, and `evidence_blob`;
- blocked effects include `create_keychain_item`, `read_keychain_secret`,
  `export_unwrapped_key`, and `fallback_to_env_secret`.

Policy: `policy_keychain_key_adapter_v1`.
