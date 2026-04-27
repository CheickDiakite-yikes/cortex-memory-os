from datetime import UTC, datetime

import pytest

from cortex_memory_os.contracts import EvidenceType, MemoryRecord, MemoryStatus
from cortex_memory_os.fixtures import load_json
from cortex_memory_os.memory_palace import MemoryPalaceService
from cortex_memory_os.sqlite_store import SQLiteMemoryGraphStore


def _service(tmp_path):
    store = SQLiteMemoryGraphStore(tmp_path / "cortex.sqlite3")
    memory = MemoryRecord.model_validate(load_json("tests/fixtures/memory_preference.json"))
    store.add_memory(memory)
    return MemoryPalaceService(store), memory


def test_explain_memory_returns_source_refs_and_influence_limits(tmp_path):
    service, memory = _service(tmp_path)

    explanation = service.explain_memory(memory.memory_id)

    assert explanation.memory_id == memory.memory_id
    assert explanation.source_refs == memory.source_refs
    assert explanation.evidence_type == memory.evidence_type
    assert "medical_decisions" in explanation.forbidden_influence


def test_delete_memory_blocks_retrieval(tmp_path):
    service, memory = _service(tmp_path)
    deleted_at = datetime(2026, 4, 27, 19, 20, tzinfo=UTC)

    deleted = service.delete_memory(memory.memory_id, now=deleted_at)

    assert deleted.status == MemoryStatus.DELETED
    assert service.store.search_memories("primary sources synthesis") == []
    audit_events = service.store.audit_for_target(memory.memory_id)
    assert [event.action for event in audit_events] == ["delete_memory"]
    assert audit_events[0].human_visible is True
    assert audit_events[0].redacted_summary == "Memory was deleted from active recall."


def test_correct_memory_supersedes_old_and_retrieves_new(tmp_path):
    service, memory = _service(tmp_path)
    corrected_at = datetime(2026, 4, 27, 19, 5, tzinfo=UTC)

    correction = service.correct_memory(
        memory.memory_id,
        "User prefers official-source research with explicit risk notes.",
        now=corrected_at,
    )

    assert correction.old_memory.status == MemoryStatus.SUPERSEDED
    assert correction.corrected_memory.status == MemoryStatus.ACTIVE
    assert correction.corrected_memory.evidence_type == EvidenceType.USER_CONFIRMED
    assert correction.corrected_memory.confidence == 1.0
    assert correction.corrected_memory.source_refs[0] == memory.memory_id
    assert correction.audit_event.target_ref == memory.memory_id
    assert correction.audit_event.action == "correct_memory"
    assert "official-source" not in correction.audit_event.redacted_summary
    matches = service.store.search_memories("official source risk notes")
    assert [match.memory_id for match in matches] == [correction.corrected_memory.memory_id]
    assert service.store.search_memories("primary sources synthesis") == []
    assert service.store.audit_for_target(memory.memory_id) == [correction.audit_event]


def test_deleted_memory_cannot_be_corrected(tmp_path):
    service, memory = _service(tmp_path)
    service.delete_memory(memory.memory_id)

    with pytest.raises(ValueError, match="deleted or revoked"):
        service.correct_memory(memory.memory_id, "Corrected content")
