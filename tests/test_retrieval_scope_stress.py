from datetime import UTC, date, datetime

from cortex_memory_os.contracts import (
    EvidenceType,
    InfluenceLevel,
    MemoryRecord,
    MemoryStatus,
    MemoryType,
    ScopeLevel,
    Sensitivity,
)
from cortex_memory_os.mcp_server import CortexMCPServer
from cortex_memory_os.memory_store import InMemoryMemoryStore
from cortex_memory_os.retrieval import (
    RETRIEVAL_SCOPE_STRESS_ID,
    RetrievalScope,
    rank_memories,
    score_memory,
)


NOW = datetime(2026, 4, 30, 14, 0, tzinfo=UTC)
QUERY = "onboarding auth redirect scope stress"


def test_retrieval_scope_stress_blocks_cross_scope_status_and_secret_leaks():
    memories = _stress_memories()
    scope = RetrievalScope(
        active_project="alpha",
        agent_id="codex",
        session_id="debug",
    )

    ranked = rank_memories(memories, QUERY, scope=scope, now=NOW, limit=20)
    ranked_ids = {item.memory.memory_id for item in ranked}

    assert RETRIEVAL_SCOPE_STRESS_ID.endswith("001")
    assert ranked_ids == {
        "mem_scope_agent_codex",
        "mem_scope_global",
        "mem_scope_project_alpha",
        "mem_scope_session_debug",
    }
    assert "project_scope_mismatch" in _reasons("mem_scope_project_beta", memories, scope)
    assert "agent_scope_mismatch" in _reasons("mem_scope_agent_claude", memories, scope)
    assert "session_scope_mismatch" in _reasons("mem_scope_session_other", memories, scope)
    assert "status_deleted" in _reasons("mem_scope_deleted", memories, scope)
    assert "status_revoked" in _reasons("mem_scope_revoked", memories, scope)
    assert "status_superseded" in _reasons("mem_scope_superseded", memories, scope)
    assert "status_quarantined" in _reasons("mem_scope_quarantined", memories, scope)
    assert "stored_only" in _reasons("mem_scope_stored_only", memories, scope)
    assert "secret_sensitivity" in _reasons("mem_scope_secret", memories, scope)
    assert "scope_never_store" in _reasons("mem_scope_never_store", memories, scope)
    assert "global_scope_excluded" in _reasons(
        "mem_scope_global",
        memories,
        RetrievalScope(
            active_project="alpha",
            agent_id="codex",
            session_id="debug",
            include_global=False,
        ),
    )


def test_gateway_memory_search_and_context_pack_apply_retrieval_scope():
    memories = _stress_memories()
    server = CortexMCPServer(store=InMemoryMemoryStore(memories))

    search = server.call_tool(
        "memory.search",
        {
            "query": QUERY,
            "active_project": "alpha",
            "agent_id": "codex",
            "session_id": "debug",
            "include_global": False,
            "limit": 20,
        },
    )
    search_ids = {memory["memory_id"] for memory in search["memories"]}
    pack = server.call_tool(
        "memory.get_context_pack",
        {
            "goal": QUERY,
            "active_project": "alpha",
            "agent_id": "codex",
            "session_id": "debug",
            "include_global": False,
            "limit": 20,
        },
    )
    pack_ids = {memory["memory_id"] for memory in pack["relevant_memories"]}

    assert search_ids == {
        "mem_scope_agent_codex",
        "mem_scope_project_alpha",
        "mem_scope_session_debug",
    }
    assert pack_ids == search_ids
    assert "mem_scope_global" not in search_ids
    assert "mem_scope_project_beta" not in search_ids
    assert "mem_scope_agent_claude" not in search_ids
    assert "mem_scope_session_other" not in search_ids
    assert all(not memory_id.endswith(("deleted", "revoked")) for memory_id in search_ids)
    assert pack["active_project"] == "alpha"


def _stress_memories() -> list[MemoryRecord]:
    return [
        _memory("mem_scope_project_alpha", ScopeLevel.PROJECT_SPECIFIC, ["project:alpha"]),
        _memory("mem_scope_agent_codex", ScopeLevel.AGENT_SPECIFIC, ["agent:codex"]),
        _memory("mem_scope_session_debug", ScopeLevel.SESSION_ONLY, ["session:debug"]),
        _memory("mem_scope_global", ScopeLevel.WORK_GLOBAL, ["work:cortex"]),
        _memory("mem_scope_project_beta", ScopeLevel.PROJECT_SPECIFIC, ["project:beta"]),
        _memory("mem_scope_agent_claude", ScopeLevel.AGENT_SPECIFIC, ["agent:claude"]),
        _memory("mem_scope_session_other", ScopeLevel.SESSION_ONLY, ["session:other"]),
        _memory(
            "mem_scope_deleted",
            ScopeLevel.PROJECT_SPECIFIC,
            ["project:alpha"],
            status=MemoryStatus.DELETED,
            influence_level=InfluenceLevel.STORED_ONLY,
        ),
        _memory(
            "mem_scope_revoked",
            ScopeLevel.PROJECT_SPECIFIC,
            ["project:alpha"],
            status=MemoryStatus.REVOKED,
            influence_level=InfluenceLevel.STORED_ONLY,
        ),
        _memory(
            "mem_scope_superseded",
            ScopeLevel.PROJECT_SPECIFIC,
            ["project:alpha"],
            status=MemoryStatus.SUPERSEDED,
        ),
        _memory(
            "mem_scope_quarantined",
            ScopeLevel.PROJECT_SPECIFIC,
            ["project:alpha"],
            status=MemoryStatus.QUARANTINED,
        ),
        _memory(
            "mem_scope_stored_only",
            ScopeLevel.PROJECT_SPECIFIC,
            ["project:alpha"],
            influence_level=InfluenceLevel.STORED_ONLY,
        ),
        _memory(
            "mem_scope_secret",
            ScopeLevel.PROJECT_SPECIFIC,
            ["project:alpha"],
            sensitivity=Sensitivity.SECRET,
        ),
        _memory("mem_scope_never_store", ScopeLevel.NEVER_STORE, ["project:alpha"]),
    ]


def _memory(
    memory_id: str,
    scope: ScopeLevel,
    source_refs: list[str],
    *,
    status: MemoryStatus = MemoryStatus.ACTIVE,
    influence_level: InfluenceLevel = InfluenceLevel.DIRECT_QUERY,
    sensitivity: Sensitivity = Sensitivity.LOW,
) -> MemoryRecord:
    return MemoryRecord(
        memory_id=memory_id,
        type=MemoryType.PROJECT,
        content=f"Onboarding auth redirect scope stress memory for {memory_id}.",
        source_refs=[*source_refs, f"scene:{memory_id}"],
        evidence_type=EvidenceType.OBSERVED_AND_INFERRED,
        confidence=0.88,
        status=status,
        created_at=NOW,
        valid_from=date(2026, 4, 30),
        sensitivity=sensitivity,
        scope=scope,
        influence_level=influence_level,
        allowed_influence=["context_retrieval"],
    )


def _reasons(
    memory_id: str,
    memories: list[MemoryRecord],
    scope: RetrievalScope,
) -> tuple[str, ...]:
    memory = next(memory for memory in memories if memory.memory_id == memory_id)
    return score_memory(memory, QUERY, scope=scope, now=NOW).reasons
