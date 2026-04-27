# Evidence Vault Encryption Boundary

Last updated: 2026-04-27

Policy reference: `policy_evidence_vault_encryption_v1`

The Evidence Vault stores raw or derived evidence behind a cipher interface.
The current local engine includes a development-only `noop-dev` cipher so the
storage, checksum, expiry, and metadata contracts can be built before native
Keychain integration exists. That cipher is not encryption and must never be
accepted in production mode.

## Runtime Modes

| Mode | Purpose | No-op cipher allowed |
| --- | --- | --- |
| `development` | Local contract iteration and synthetic fixtures. | Yes, with explicit `noop_dev_cipher_allowed_only_outside_production` reason. |
| `test` | Unit tests and deterministic benchmark fixtures. | Yes, with explicit test-only reason. |
| `production` | Packaged local app handling user evidence. | No. |

## Production Cipher Contract

A production cipher must:

- Advertise `authenticated_encryption = True`.
- Have a non-`noop-dev` cipher name.
- Seal raw bytes before they are written to disk.
- Open sealed bytes back to plaintext for authorized reads.
- Preserve checksum verification over plaintext.
- Work with raw expiry so deleting raw blobs removes sealed bytes too.

The first production implementation should be a native macOS shell-provided
cipher backed by Keychain-managed keys. The Python engine should receive only a
local cipher adapter, not long-lived raw key material.

## Required Failure

Starting `EvidenceVault(..., mode="production")` without a production cipher
must raise an error before any directory, database, or blob can be used for raw
evidence storage.

## Benchmark

`VAULT-ENCRYPT-001` verifies:

- `noop-dev` is rejected in production mode.
- A test authenticated cipher is accepted in production mode.
- Stored blob bytes differ from plaintext.
- `read_raw` restores the original plaintext through the cipher.
- Metadata records the cipher name.
