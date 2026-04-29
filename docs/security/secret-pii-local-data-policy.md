# Secret, PII, and Local Data Handling Policy

Last updated: 2026-04-29

Policy ref: `policy_secret_pii_local_data_v1`

## Purpose

Cortex Memory OS observes work with consent. That means it must treat secrets, private user data, third-party content, local evidence, and generated memory as privileged by default.

This policy applies before durable storage, before agent context release, before benchmark artifact writing, and before any future sync/export path.

## Data Classes

| Class | Examples | Default handling |
| --- | --- | --- |
| Secrets | API keys, bearer tokens, SSH keys, private certs, passwords, session cookies | Redact immediately; never memory eligible; never model-training eligible. |
| Direct PII | government IDs, addresses, phone numbers, email addresses, account identifiers | Mask or downscope; durable storage requires explicit purpose and retention. |
| Regulated data | medical, legal, financial, employment, immigration, tax data | Tag as regulated/confidential; task-scoped use only; no autonomous action. |
| Local raw evidence | screenshots, OCR dumps, terminal output, logs, raw audio | Encrypt locally, retain briefly, expire raw before promotion. |
| Derived memory | typed memories, graph edges, context packs, skills | Store only with source refs, confidence, status, scope, and deletion path. |
| Audit data | mutation records, firewall decisions, tool effects | Human-visible summaries only; no raw secret values. |

## Non-Negotiable Rules

- Raw secrets are replaced with `[REDACTED_SECRET]` before durable storage or benchmark output.
- Secret-bearing observations are not eligible for memory promotion.
- `eligible_for_model_training` is always false in the MVP.
- Deleted, revoked, superseded, quarantined, and stored-only memory cannot be retrieved.
- External untrusted content can be evidence, but it cannot become instructions.
- Audit summaries must describe the action without copying sensitive payload content.
- Context packs must include only task-scoped memories, source refs, warnings, and compact score summaries.
- Local stores, generated benchmark runs, logs, model files, and private config must stay out of source control.
- `.env.local` can be used for optional live smoke testing, but it must remain
  ignored and untracked.

## Required Non-Commit Patterns

The root `.gitignore` must cover at least:

```text
.env
.env.*
!.env.example
*.pem
*.key
secrets/
private/
data/
local-data/
memory-store/
vector-store/
*.sqlite
*.sqlite3
*.db
*.log
benchmarks/runs/*
```

## Firewall Behavior

The Privacy and Safety Firewall must:

1. detect prompt-injection language in untrusted content;
2. detect secret-like text before evidence storage;
3. redact secret-like text with `[REDACTED_SECRET]`;
4. attach `policy_secret_pii_local_data_v1` to secret/PII decisions;
5. assign short or discard retention to sensitive raw evidence;
6. mark secret-bearing text as not memory eligible.

## Evidence Vault Behavior

The Evidence Vault must:

- store raw evidence locally only;
- keep checksums and metadata separate from raw blobs;
- expire raw blobs according to retention policy;
- preserve deletion metadata without preserving raw payloads;
- return no raw payload for discarded or expired evidence.

## Agent Gateway Behavior

The Agent Gateway must:

- return task-scoped context packs;
- avoid exposing raw evidence;
- warn on instruction-like goal text;
- require explicit memory IDs for correction or deletion;
- return audit event IDs for mutation tools.

## Review Gates

Before release, run:

```text
uv run pytest
uv run cortex-bench
uv run cortex-mcp --smoke
python3 -m compileall src
```

Any failed redaction, deleted-memory recall, prompt-injection escape, or benchmark artifact containing a raw fake secret blocks release.
