# Unified Encrypted Graph And Index Boundary

Status: accepted for local prototype

Date: 2026-05-01

Related task: `UNIFIED-ENCRYPTED-GRAPH-INDEX-001`

Policy reference: `policy_unified_encrypted_graph_index_v1`

## Problem

`EncryptedMemoryStore` now blocks plaintext durable memory payloads, but retrieval
still needs a searchable surface. A naive index can accidentally rebuild the same
risk under a different name by storing memory text, source refs, graph triples,
or raw evidence handles outside the encrypted payload.

## Boundary

Durable content has one default home:

```text
MemoryRecord JSON payload -> authenticated encryption -> sealed SQLite blob
```

Search and graph metadata use a separate redacted index:

```text
content terms      -> keyed HMAC digests
graph terms        -> keyed HMAC digests
memory/source refs -> counts or opaque IDs only
query text         -> keyed HMAC digests for matching, never persisted
```

The index may store:

- memory ID
- lifecycle status
- scope, sensitivity, and influence level
- source-ref count
- token digest counts
- keyed token digests
- graph association by explicit memory ID

The index must not store:

- memory content
- source refs
- raw refs
- browser/DOM/OCR text
- graph subject, predicate, or object text
- prompt-injection strings
- model prompts or user secrets

## Why HMAC Digests

Plain hashes of tokens are dictionary-attackable. The prototype therefore uses
keyed HMAC digests. The key is runtime configuration, not database content. This
does not replace encryption; it only gives a local-first search seam that avoids
persisting plaintext index terms while we design the production key lifecycle.

## Retrieval Flow

```text
query
  -> tokenize in memory
  -> HMAC query terms
  -> match redacted index rows
  -> open only candidate sealed payloads
  -> apply normal retrieval scope and lifecycle policy
  -> return context pack or redacted index receipt
```

Graph boosting follows the same rule: graph triples are sealed as payloads, and
only graph token digests plus explicit related memory IDs are stored in the
searchable table.

## Migration Plan

1. Keep `SQLiteMemoryGraphStore` as a legacy plaintext development store.
2. Add `UnifiedEncryptedGraphIndex` as the default durable-content direction.
3. Route new context-pack and gateway tests through the encrypted index store.
4. Convert fixtures and dashboards gradually to read from redacted receipts.
5. Later, replace toy test ciphers with OS-backed key management.

## Safety Invariant

An attacker who reads the local index database should see metadata and opaque
digests, not memory text, source refs, raw refs, graph triples, or executable
instructions.
