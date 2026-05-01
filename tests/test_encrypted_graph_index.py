from datetime import UTC, date, datetime
import json

import pytest

from cortex_memory_os.contracts import (
    EvidenceType,
    InfluenceLevel,
    MemoryRecord,
    MemoryStatus,
    MemoryType,
    ScopeLevel,
    Sensitivity,
    TemporalEdge,
)
from cortex_memory_os.encrypted_graph_index import (
    UNIFIED_ENCRYPTED_GRAPH_INDEX_POLICY_REF,
    UnifiedEncryptedGraphIndex,
)
from cortex_memory_os.retrieval import RetrievalScope


class _ToyAuthenticatedCipher:
    name = "toy-unified-index-aead-test"
    authenticated_encryption = True

    def seal(self, plaintext: bytes) -> bytes:
        return b"sealed-unified-index:" + plaintext[::-1]

    def open(self, ciphertext: bytes) -> bytes:
        if not ciphertext.startswith(b"sealed-unified-index:"):
            raise ValueError("missing toy unified index seal")
        return ciphertext.removeprefix(b"sealed-unified-index:")[::-1]


class _NoopCipher:
    name = "noop-test"
    authenticated_encryption = False

    def seal(self, plaintext: bytes) -> bytes:
        return plaintext

    def open(self, ciphertext: bytes) -> bytes:
        return ciphertext


def _memory(**updates) -> MemoryRecord:
    fields = {
        "memory_id": "mem_unified_index_case",
        "type": MemoryType.PROCEDURAL,
        "content": "Auth callback debugging uses smallest safe route checks and local tests.",
        "source_refs": ["project:cortex-memory-os", "scene_private_auth_debug_trace"],
        "evidence_type": EvidenceType.OBSERVED_AND_INFERRED,
        "confidence": 0.93,
        "status": MemoryStatus.ACTIVE,
        "created_at": datetime(2026, 5, 1, 14, 0, tzinfo=UTC),
        "valid_from": date(2026, 5, 1),
        "valid_to": None,
        "sensitivity": Sensitivity.PRIVATE_WORK,
        "scope": ScopeLevel.PROJECT_SPECIFIC,
        "influence_level": InfluenceLevel.PLANNING,
        "allowed_influence": ["debugging_plan"],
        "forbidden_influence": ["production_credentials"],
        "decay_policy": "review_after_90_days",
        "contradicts": [],
        "user_visible": True,
        "requires_user_confirmation": False,
    }
    fields.update(updates)
    return MemoryRecord(**fields)


def _edge(**updates) -> TemporalEdge:
    fields = {
        "edge_id": "edge_unified_index_case",
        "subject": "user",
        "predicate": "debugs",
        "object": "OAuth callback route mismatch",
        "valid_from": date(2026, 5, 1),
        "valid_to": None,
        "confidence": 0.86,
        "source_refs": ["scene_private_auth_debug_trace"],
        "status": MemoryStatus.ACTIVE,
        "supersedes": [],
    }
    fields.update(updates)
    return TemporalEdge(**fields)


def _index(tmp_path) -> UnifiedEncryptedGraphIndex:
    return UnifiedEncryptedGraphIndex(
        tmp_path / "unified.sqlite3",
        cipher=_ToyAuthenticatedCipher(),
        index_key=b"cortex-test-index-key-32-bytes",
    )


def test_requires_authenticated_cipher_for_unified_index(tmp_path):
    with pytest.raises(ValueError, match="authenticated_encryption_required"):
        UnifiedEncryptedGraphIndex(
            tmp_path / "unified.sqlite3",
            cipher=_NoopCipher(),
            index_key=b"cortex-test-index-key-32-bytes",
        )


def test_sealed_payloads_and_redacted_hmac_index_do_not_store_plaintext(tmp_path):
    memory = _memory()
    edge = _edge()
    index = _index(tmp_path)

    write_receipt = index.add_memory(memory)
    graph_receipt = index.add_edge(edge, related_memory_ids=[memory.memory_id])
    db_bytes = (tmp_path / "unified.sqlite3").read_bytes()
    search = index.search_index(
        "auth callback route debugging",
        scope=RetrievalScope(active_project="cortex-memory-os"),
    )

    assert write_receipt.token_digest_count > 0
    assert write_receipt.content_redacted is True
    assert write_receipt.source_refs_redacted is True
    assert graph_receipt.graph_token_digest_count > 0
    assert graph_receipt.graph_terms_redacted is True
    assert search.hits[0].memory_id == memory.memory_id
    assert search.hits[0].graph_boosted is True
    assert search.hits[0].content_redacted is True
    assert search.hits[0].source_refs_redacted is True
    assert search.receipt.query_redacted is True
    assert search.receipt.candidate_open_count == 1
    assert UNIFIED_ENCRYPTED_GRAPH_INDEX_POLICY_REF in search.policy_refs
    assert b"Auth callback debugging" not in db_bytes
    assert b"scene_private_auth_debug_trace" not in db_bytes
    assert b"OAuth callback route mismatch" not in db_bytes
    assert b"auth" not in db_bytes.lower()
    assert b"callback" not in db_bytes.lower()
    assert index.get_memory(memory.memory_id) == memory


def test_scope_policy_still_applies_after_index_match(tmp_path):
    allowed = _memory(memory_id="mem_project_allowed")
    blocked = _memory(
        memory_id="mem_project_blocked",
        source_refs=["project:other", "scene_private_auth_debug_trace"],
    )
    index = _index(tmp_path)
    index.add_memory(allowed)
    index.add_memory(blocked)

    result = index.search_index(
        "auth callback debugging",
        scope=RetrievalScope(active_project="cortex-memory-os"),
    )

    assert [hit.memory_id for hit in result.hits] == ["mem_project_allowed"]
    assert result.receipt.considered_index_rows == 2
    assert result.receipt.candidate_open_count == 2


def test_context_rank_uses_index_before_authorized_payload_open(tmp_path):
    memory = _memory()
    index = _index(tmp_path)
    index.add_memory(memory)

    ranked = index.rank(
        "smallest safe auth callback tests",
        scope=RetrievalScope(active_project="cortex-memory-os"),
    )
    payload = json.dumps(index.search_index("smallest safe auth callback").model_dump(mode="json"))

    assert [item.memory.memory_id for item in ranked] == [memory.memory_id]
    assert ranked[0].score.eligible is True
    assert "Auth callback debugging" not in payload
    assert "scene_private_auth_debug_trace" not in payload
