# Debug Journal

Last updated: 2026-04-29

Use this file for failures that teach us something. Keep entries reproducible, concise, and privacy-aware.

## Active Issues

| ID | Status | Symptom | Owner | Next step |
| --- | --- | --- | --- | --- |
| _None_ |  |  |  |  |

## Resolved Issues

| ID | Date resolved | Root cause | Fix | Verification |
| --- | --- | --- | --- | --- |
| DBG-001 | 2026-04-28 | Vault tests and benchmark fixture reads used wall-clock `now`, so synthetic evidence from 2026-04-27 expired when run on 2026-04-28. | Pass fixture timestamps into raw reads that are intended to verify storage/cipher behavior rather than retention expiry. | `uv run pytest tests/test_evidence_vault.py tests/test_mcp_server.py tests/test_benchmarks.py tests/test_contracts.py` -> 62 passed; `uv run pytest` -> 152 passed; `uv run cortex-bench` -> 60/60 passed. |
| DBG-002 | 2026-04-29 | Product traceability benchmark still required the exact phrase "Shadow Pointer native overlay" after the roadmap wording was updated. | Restored the expected phrase while keeping the new next-step order. | `uv run pytest tests/test_shadow_pointer.py tests/test_benchmarks.py` -> 12 passed; `uv run cortex-bench --no-write` -> 101/101 passed. |
| DBG-003 | 2026-04-29 | `POINTER-PROPOSAL-001` initially failed because the benchmark looked for the exact phrase "not privileged actions" and the docs line wrapped between words. | Reworded the architecture doc to keep the safety boundary phrase contiguous. | `uv run pytest tests/test_shadow_pointer.py tests/test_benchmarks.py` -> 16 passed; `uv run cortex-bench --no-write` -> 106/106 passed. |
| DBG-004 | 2026-04-29 | Two parallel `uv run` commands raced while installing the newly added `cortex-plugin-install-smoke` console script, causing a transient dist-info removal error. | Avoid parallel `uv run` invocations immediately after adding or changing project scripts; rerun focused checks sequentially. | `uv run pytest` -> 246 passed; `uv run cortex-bench` -> 113/113 passed; `uv run cortex-plugin-install-smoke` passed. |

## Incident Template

### DBG-000: Short Symptom

- Date opened:
- Status: Active / Blocked / Resolved
- Trigger:
- Expected:
- Actual:
- Reproduction:
- Logs or artifacts:
- Suspected layer:
- Root cause:
- Fix:
- Verification:
- Follow-ups:
- Privacy note:

## Debugging Rules

- Reproduce before refactoring.
- Preserve failing fixtures when safe and synthetic.
- Redact secrets and personal memory from logs before committing.
- Prefer structured traces over giant raw prompts.
- Convert repeated bugs into benchmark cases.

## Structured Trace Contract

Code-level trace support lives in `src/cortex_memory_os/debug_trace.py`.

Trace records are designed for reproduction without raw private payloads:

```json
{
  "trace_id": "dbg_20260427T201000Z_gateway_context_pack_failed",
  "timestamp": "2026-04-27T20:10:00Z",
  "layer": "gateway",
  "event": "context_pack_failed",
  "status": "error",
  "summary": "Failed while token=[REDACTED_SECRET]",
  "details": {
    "case_id": "GATEWAY-CTX-001/context_pack"
  },
  "artifact_refs": ["benchmarks/runs/synthetic.json"],
  "redaction_count": 1,
  "policy_refs": ["policy_secret_pii_local_data_v1"]
}
```

Rules:

- `summary`, `details`, and `artifact_refs` must not contain unredacted secret-like text.
- Trace IDs may include layer and event names, but never raw user content.
- `artifact_refs` point to sanitized artifacts only.
- A bug that needs raw private evidence must stay local, encrypted, and referenced by evidence ID rather than copied into the journal.
