from datetime import UTC, date, datetime

import pytest

from cortex_memory_os.contracts import (
    EvidenceType,
    InfluenceLevel,
    MemoryRecord,
    MemoryStatus,
    MemoryType,
    ScopeLevel,
    Sensitivity,
)
from cortex_memory_os.memory_encryption import (
    EncryptedMemoryStore,
    MEMORY_ENCRYPTION_DEFAULT_POLICY_REF,
    MemoryEncryptionRequiredError,
    assess_memory_encryption_default,
)


class _ToyAuthenticatedCipher:
    name = "toy-memory-aead-test"
    authenticated_encryption = True

    def seal(self, plaintext: bytes) -> bytes:
        return b"sealed-memory:" + plaintext[::-1]

    def open(self, ciphertext: bytes) -> bytes:
        if not ciphertext.startswith(b"sealed-memory:"):
            raise ValueError("missing toy memory seal")
        return ciphertext.removeprefix(b"sealed-memory:")[::-1]


def _memory(**updates) -> MemoryRecord:
    fields = {
        "memory_id": "mem_private_durable_default",
        "type": MemoryType.PREFERENCE,
        "content": "User prefers sensitive durable memory to be sealed before storage.",
        "source_refs": ["scene_private_memory_encryption"],
        "evidence_type": EvidenceType.OBSERVED_AND_INFERRED,
        "confidence": 0.91,
        "status": MemoryStatus.ACTIVE,
        "created_at": datetime(2026, 5, 1, 12, 0, tzinfo=UTC),
        "valid_from": date(2026, 5, 1),
        "valid_to": None,
        "sensitivity": Sensitivity.PRIVATE_WORK,
        "scope": ScopeLevel.PROJECT_SPECIFIC,
        "influence_level": InfluenceLevel.PLANNING,
        "allowed_influence": ["storage_policy"],
        "forbidden_influence": ["external_export"],
        "decay_policy": "review_after_90_days",
        "contradicts": [],
        "user_visible": True,
        "requires_user_confirmation": False,
    }
    fields.update(updates)
    return MemoryRecord(**fields)


def test_durable_memory_write_rejects_noop_cipher_by_default(tmp_path):
    memory = _memory()
    store = EncryptedMemoryStore(tmp_path / "memory.sqlite3")

    with pytest.raises(
        MemoryEncryptionRequiredError,
        match="authenticated_encryption_required_for_durable_memory",
    ) as error:
        store.add_memory(memory)

    decision = error.value.decision
    assert decision.allowed is False
    assert decision.durable_write is True
    assert decision.sensitive_durable is True
    assert decision.content_redacted is True
    assert decision.source_refs_redacted is True
    assert "write_plaintext_memory_payload" in decision.blocked_effects
    assert MEMORY_ENCRYPTION_DEFAULT_POLICY_REF in decision.policy_refs
    assert memory.content not in str(error.value)
    assert memory.source_refs[0] not in str(error.value)
    assert store.get_memory(memory.memory_id) is None


def test_authenticated_cipher_seals_and_round_trips_durable_memory(tmp_path):
    memory = _memory(
        memory_id="mem_private_durable_sealed",
        content="Sensitive durable auth-debug preference should not appear in sqlite bytes.",
        source_refs=["scene_private_auth_debug_trace"],
    )
    db_path = tmp_path / "memory.sqlite3"
    store = EncryptedMemoryStore(db_path, cipher=_ToyAuthenticatedCipher())

    receipt = store.add_memory(memory)
    restored = store.get_memory(memory.memory_id)
    raw_db = db_path.read_bytes()

    assert receipt.decision.allowed is True
    assert receipt.decision.reason == "durable_memory_authenticated_encryption_satisfied"
    assert receipt.decision.cipher_authenticated is True
    assert receipt.decision.content_redacted is True
    assert receipt.decision.source_refs_redacted is True
    assert receipt.cipher_name == _ToyAuthenticatedCipher.name
    assert restored == memory
    assert b"Sensitive durable auth-debug preference" not in raw_db
    assert b"scene_private_auth_debug_trace" not in raw_db
    assert b"payload_json" not in raw_db


def test_non_durable_memory_cannot_enter_durable_encrypted_store(tmp_path):
    memory = _memory(
        memory_id="mem_session_only",
        scope=ScopeLevel.SESSION_ONLY,
        sensitivity=Sensitivity.LOW,
        influence_level=InfluenceLevel.DIRECT_QUERY,
    )
    store = EncryptedMemoryStore(tmp_path / "memory.sqlite3", cipher=_ToyAuthenticatedCipher())

    with pytest.raises(MemoryEncryptionRequiredError) as error:
        store.add_memory(memory)

    assert error.value.decision.allowed is False
    assert error.value.decision.reason == "non_durable_scope_cannot_write_to_encrypted_store"
    assert "write_durable_memory_record" in error.value.decision.blocked_effects


def test_deleted_or_quarantined_memory_content_is_not_rewritten_to_secure_store(tmp_path):
    store = EncryptedMemoryStore(tmp_path / "memory.sqlite3", cipher=_ToyAuthenticatedCipher())

    for status in (MemoryStatus.DELETED, MemoryStatus.REVOKED, MemoryStatus.QUARANTINED):
        memory = _memory(
            memory_id=f"mem_{status.value}",
            status=status,
            influence_level=InfluenceLevel.STORED_ONLY,
        )
        decision = assess_memory_encryption_default(memory, _ToyAuthenticatedCipher())

        assert decision.allowed is False
        assert decision.reason == "memory_status_cannot_write_content_to_durable_store"
        with pytest.raises(MemoryEncryptionRequiredError):
            store.add_memory(memory)


def test_encrypted_store_searches_only_after_authorized_open(tmp_path):
    memory = _memory(
        memory_id="mem_searchable_after_open",
        content="Validated context packs should retrieve encrypted memory after authorized open.",
        source_refs=["scene_context_pack_encryption"],
    )
    store = EncryptedMemoryStore(tmp_path / "memory.sqlite3", cipher=_ToyAuthenticatedCipher())

    store.add_memory(memory)
    hits = store.search_memories("context packs encrypted memory", limit=3)

    assert [hit.memory_id for hit in hits] == [memory.memory_id]
