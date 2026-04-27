from datetime import UTC, datetime

from cortex_memory_os.contracts import InfluenceLevel, MemoryRecord, MemoryStatus
from cortex_memory_os.fixtures import load_json
from cortex_memory_os.memory_export import (
    MEMORY_EXPORT_POLICY_REF,
    export_memories,
    export_memories_with_audit,
)
from cortex_memory_os.memory_lifecycle import transition_memory
from cortex_memory_os.retrieval import RetrievalScope
from cortex_memory_os.sensitive_data_policy import REDACTED_SECRET_PLACEHOLDER
from cortex_memory_os.sqlite_store import SQLiteMemoryGraphStore


def _memory() -> MemoryRecord:
    return MemoryRecord.model_validate(load_json("tests/fixtures/memory_preference.json"))


def test_export_includes_active_memory_and_omits_deleted_content():
    active = _memory()
    deleted = transition_memory(
        active.model_copy(
            update={
                "memory_id": "mem_deleted_export",
                "content": "Deleted-only export content must not reappear.",
            }
        ),
        MemoryStatus.DELETED,
    )

    bundle = export_memories(
        [active, deleted],
        now=datetime(2026, 4, 27, 21, 0, tzinfo=UTC),
    )

    assert [memory.memory_id for memory in bundle.memories] == [active.memory_id]
    assert bundle.omitted_memory_ids == [deleted.memory_id]
    assert bundle.omission_reasons[deleted.memory_id] == ["not_recall_allowed"]
    assert deleted.content not in bundle.model_dump_json()
    assert MEMORY_EXPORT_POLICY_REF in bundle.policy_refs


def test_export_redacts_secret_like_text_in_visible_memory():
    secret = "CORTEX_FAKE_TOKEN_exportSECRET123"
    memory = _memory().model_copy(
        update={
            "memory_id": "mem_export_secret_like",
            "content": f"Use local fixture token={secret} only for synthetic tests.",
        }
    )

    bundle = export_memories([memory])

    assert bundle.redaction_count == 1
    assert secret not in bundle.model_dump_json()
    assert REDACTED_SECRET_PLACEHOLDER in bundle.memories[0].content


def test_export_respects_project_scope_and_stored_only_state():
    active = _memory().model_copy(
        update={
            "memory_id": "mem_project_alpha",
            "source_refs": ["project:alpha", "scene_alpha"],
        }
    )
    wrong_project = _memory().model_copy(
        update={
            "memory_id": "mem_project_beta",
            "source_refs": ["project:beta", "scene_beta"],
        }
    )
    stored_only = _memory().model_copy(
        update={
            "memory_id": "mem_stored_only",
            "influence_level": InfluenceLevel.STORED_ONLY,
            "allowed_influence": [],
        }
    )

    bundle = export_memories(
        [wrong_project, active, stored_only],
        scope=RetrievalScope(active_project="alpha"),
    )

    assert [memory.memory_id for memory in bundle.memories] == [active.memory_id]
    assert set(bundle.omitted_memory_ids) == {
        wrong_project.memory_id,
        stored_only.memory_id,
    }
    assert bundle.omission_reasons[wrong_project.memory_id] == ["project_scope_mismatch"]
    assert bundle.omission_reasons[stored_only.memory_id] == ["not_recall_allowed"]


def test_export_with_audit_persists_summary_without_exported_content(tmp_path):
    secret = "CORTEX_FAKE_TOKEN_exportAuditSECRET123"
    memory = _memory().model_copy(
        update={
            "memory_id": "mem_export_audit",
            "content": f"Synthetic export audit fixture token={secret}.",
        }
    )
    store = SQLiteMemoryGraphStore(tmp_path / "cortex.sqlite3")
    exported_at = datetime(2026, 4, 27, 21, 20, tzinfo=UTC)

    result = export_memories_with_audit(
        store,
        [memory],
        actor="tester",
        now=exported_at,
    )
    audit_events = store.audit_for_target(result.bundle.export_id)
    serialized_audit = audit_events[0].model_dump_json()

    assert audit_events == [result.audit_event]
    assert result.audit_event.action == "export_memories"
    assert result.audit_event.actor == "tester"
    assert result.audit_event.human_visible is True
    assert result.audit_event.target_ref == result.bundle.export_id
    assert result.audit_event.redacted_summary == (
        "Memory export created with 1 memories, 0 omitted, 1 redactions."
    )
    assert secret not in serialized_audit
    assert "Synthetic export audit fixture" not in serialized_audit
    assert MEMORY_EXPORT_POLICY_REF in result.audit_event.policy_refs
