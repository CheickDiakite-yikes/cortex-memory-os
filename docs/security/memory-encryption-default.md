# Memory Encryption Default

Last updated: 2026-05-01

Benchmark: `MEMORY-ENCRYPTION-DEFAULT-001`

Policy reference: `policy_memory_encryption_default_v1`

Cortex treats durable memory content as more sensitive than ordinary local
application state. Raw evidence can expire, but durable memories are designed
to influence future agents. They therefore need an encrypted storage boundary
before real private memories are allowed.

## Contract

`EncryptedMemoryStore` is the first durable-memory storage boundary. It stores
only redacted index metadata in SQLite and seals the full `MemoryRecord` JSON
payload behind a cipher before writing it to disk.

The store blocks:

- durable memory writes when the cipher is `noop-dev`;
- session-only, ephemeral, or never-store memory writes to the durable store;
- deleted, revoked, or quarantined memory content rewrites;
- plaintext `payload_json`, raw source refs, and unencrypted export effects.

The receipt returned by the store includes the memory ID, cipher name, payload
hash, sealed byte count, policy reference, and redaction flags. It never
includes memory content or source refs.

## Relationship To Evidence Vault

The Evidence Vault already rejects `noop-dev` in production mode. This memory
slice is stricter: durable memory content must use authenticated encryption
even in local development paths that call `EncryptedMemoryStore`.

The existing plaintext `SQLiteMemoryGraphStore` remains useful for synthetic
fixtures, legacy tests, and non-production graph iteration. New sensitive
durable-memory write paths should use `EncryptedMemoryStore` until a unified
encrypted graph/index store replaces both paths.

## Benchmark

`MEMORY-ENCRYPTION-DEFAULT-001` verifies:

- a durable private-work memory write is rejected with the default no-op cipher;
- rejection errors redact memory content and source refs;
- an authenticated test cipher can seal and round-trip the memory;
- the SQLite bytes do not contain the memory content or source ref;
- the dashboard exposes `Encryption Default` as a visible guardrail panel.
