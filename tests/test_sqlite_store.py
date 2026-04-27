from datetime import UTC, datetime

from cortex_memory_os.contracts import AuditEvent, InfluenceLevel, MemoryRecord, MemoryStatus
from cortex_memory_os.fixtures import load_json
from cortex_memory_os.memory_compiler import compile_scene_memory
from cortex_memory_os.sqlite_store import SQLiteMemoryGraphStore
from cortex_memory_os.temporal_graph import compile_temporal_edge


def _memory() -> MemoryRecord:
    return MemoryRecord.model_validate(load_json("tests/fixtures/memory_preference.json"))


def test_sqlite_store_persists_memory_across_instances(tmp_path):
    db_path = tmp_path / "cortex.sqlite3"
    store = SQLiteMemoryGraphStore(db_path)
    memory = _memory()

    store.add_memory(memory)
    reopened = SQLiteMemoryGraphStore(db_path)

    assert reopened.get_memory(memory.memory_id) == memory
    matches = reopened.search_memories("primary sources synthesis")
    assert [match.memory_id for match in matches] == [memory.memory_id]


def test_sqlite_forget_persists_tombstone_and_blocks_retrieval(tmp_path):
    store = SQLiteMemoryGraphStore(tmp_path / "cortex.sqlite3")
    memory = _memory()
    store.add_memory(memory)

    deleted = store.forget_memory(memory.memory_id)
    reopened = SQLiteMemoryGraphStore(tmp_path / "cortex.sqlite3")

    assert deleted.status == MemoryStatus.DELETED
    assert deleted.influence_level == InfluenceLevel.STORED_ONLY
    assert reopened.get_memory(memory.memory_id).status == MemoryStatus.DELETED
    assert reopened.search_memories("primary sources synthesis") == []


def test_sqlite_temporal_edges_round_trip_by_subject(tmp_path):
    store = SQLiteMemoryGraphStore(tmp_path / "cortex.sqlite3")
    memory = _memory()
    edge = compile_temporal_edge(memory)

    store.add_memory(memory)
    store.add_edge(edge)

    assert store.get_edge(edge.edge_id) == edge
    assert store.edges_for_subject("user") == [edge]


def test_sqlite_store_accepts_compiled_scene_memory_and_edge(tmp_path):
    scene_payload = load_json("tests/fixtures/scene_research.json")
    from cortex_memory_os.contracts import Scene

    scene = Scene.model_validate(scene_payload)
    memory = compile_scene_memory(scene)
    edge = compile_temporal_edge(memory)
    store = SQLiteMemoryGraphStore(tmp_path / "cortex.sqlite3")

    store.add_memory(memory)
    store.add_edge(edge)

    assert store.search_memories("screen based memory systems")[0].memory_id == memory.memory_id
    assert store.edges_for_subject("user")[0].predicate == "worked_on"


def test_sqlite_audit_events_round_trip_by_target(tmp_path):
    db_path = tmp_path / "cortex.sqlite3"
    store = SQLiteMemoryGraphStore(db_path)
    event = AuditEvent(
        audit_event_id="audit_memory_delete_mem_001",
        timestamp=datetime(2026, 4, 27, 19, 25, tzinfo=UTC),
        actor="user",
        action="delete_memory",
        target_ref="mem_001",
        policy_refs=["policy_memory_palace_user_control_v1"],
        result="deleted",
        human_visible=True,
        redacted_summary="Memory was deleted from active recall.",
    )

    store.add_audit_event(event)
    reopened = SQLiteMemoryGraphStore(db_path)

    assert reopened.get_audit_event(event.audit_event_id) == event
    assert reopened.audit_for_target("mem_001") == [event]
