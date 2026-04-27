# Debug Journal

Last updated: 2026-04-27

Use this file for failures that teach us something. Keep entries reproducible, concise, and privacy-aware.

## Active Issues

| ID | Status | Symptom | Owner | Next step |
| --- | --- | --- | --- | --- |
| _None_ |  |  |  |  |

## Resolved Issues

| ID | Date resolved | Root cause | Fix | Verification |
| --- | --- | --- | --- | --- |
| _None_ |  |  |  |  |

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
