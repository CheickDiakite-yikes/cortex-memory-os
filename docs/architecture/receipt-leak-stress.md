# Receipt Leak Stress

Benchmark: `RECEIPT-LEAK-STRESS-001`

Policy: `policy_receipt_leak_stress_v1`

This stress check serializes the operational dashboard backbone:

- `KEY-MANAGEMENT-PLAN-001`
- `ENCRYPTED-INDEX-DASHBOARD-LIVE-001`
- `NATIVE-SHADOW-POINTER-LIVE-FEED-001`
- `DURABLE-SYNTHETIC-MEMORY-RECEIPTS-001`
- `DASHBOARD-LIVE-BACKBONE-001`

It then checks the combined receipt payloads for prohibited markers, including
secret-like strings, hostile instructions, raw refs, encrypted blob refs, source
ref values, and synthetic memory content.

The acceptance gate is:

- `prohibited_marker_count == 0`
- content redacted
- source refs redacted
- key material hidden
- raw private data not retained
