# Memory Export

Last updated: 2026-04-27

Policy reference: `policy_memory_export_deletion_aware_v1`

Users must be able to take their Cortex memory with them, inspect it outside
the app, and verify that deletion and revocation are respected. Export is a
user-control feature, not a sync shortcut.

## Export Rules

An exported memory must be:

- User-visible.
- Recall-allowed.
- Within the requested project, agent, or session scope.
- Redacted for secret-like text.
- Source-backed.

## Memory Palace UI Flow

Export begins from an explicit Memory Palace selection or a visible scoped
filter. The UI should show the user what will happen before the bundle is
created:

- Selected scope: memory IDs, project, agent, session, or current filtered view.
- Exportable count.
- Omitted count and omission categories.
- Redaction policy.
- Audit receipt behavior.

The user must confirm export because this is data egress even when it stays
local. Export is not a hidden sync path and it must not be triggered from a
vague request like "send everything" without showing the scope.

The export bundle includes:

- Export ID and timestamp.
- Scope selectors.
- Exported memory records.
- Omitted memory IDs.
- Omission reasons.
- Redaction count.
- Policy refs.

## Audit

Every product export should create a human-visible audit event with:

- action `export_memories`;
- target ref equal to the export ID;
- policy refs from the bundle;
- exported count;
- omitted count;
- redaction count.

The audit summary must not copy exported memory content, omitted memory content,
raw evidence text, or secret-like values. It is an operational receipt, not a
second export surface.

## Omitted Content

The following memory states must not export content:

- `deleted`
- `revoked`
- `superseded`
- `quarantined`
- `stored_only`
- secret-sensitive
- not user-visible
- out of requested scope

Deletion-aware export may include the omitted memory ID and reason, but not the
omitted memory content. That lets the user verify that something was excluded
without resurrecting content they asked Cortex to forget.

## Redaction

Visible exported memories still pass through the secret-like-text redactor.
If an active memory contains a synthetic token or similar accidental secret,
the export replaces it with `[REDACTED_SECRET]` and increments the redaction
count.

## Benchmark

`EXPORT-001` verifies:

- Active recall-allowed memory is exported.
- Deleted memory content is omitted.
- Omitted IDs and reasons are visible.
- Secret-like text is redacted.
- Project scope is respected.

`EXPORT-AUDIT-001` verifies:

- Export creates a persisted human-visible audit event.
- Audit target is the export ID.
- Audit summary includes only counts.
- Audit payload does not contain exported content or secret-like text.
