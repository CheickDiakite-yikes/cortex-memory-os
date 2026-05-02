# Durable Synthetic Memory Receipts

Benchmark: `DURABLE-SYNTHETIC-MEMORY-RECEIPTS-001`

Policy: `policy_durable_synthetic_memory_receipts_v1`

This slice promotes the synthetic capture ladder from "local test DB write" to
"encrypted durable write receipt" without touching private real activity.

## Contract

The receipt proves:

- `synthetic_only: true`
- `encrypted_store_used: true`
- `durable_synthetic_memory_written: true`
- `durable_private_memory_written: false`
- `real_screen_capture_started: false`
- `raw_ref_retained: false`
- `raw_payload_included: false`
- human-visible audit receipt exists

The write path uses `EncryptedMemoryStore` through
`UnifiedEncryptedGraphIndex`. The database may contain sealed payload bytes,
HMAC token digests, counts, and redacted metadata. It must not contain memory
content, source refs, query text, raw refs, or secret-like markers.

## Why This Exists

Before consented real screen capture, Cortex needs one safe full loop:

```text
synthetic event -> encrypted durable memory -> redacted index -> search receipt
```

That loop gives the dashboard and benchmarks something real to inspect while
keeping private data, raw screenshots, and external effects off.
