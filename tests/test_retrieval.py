from datetime import UTC, datetime, timedelta

from cortex_memory_os.contracts import (
    EvidenceType,
    InfluenceLevel,
    MemoryRecord,
    MemoryStatus,
    ScopeLevel,
    Sensitivity,
)
from cortex_memory_os.fixtures import load_json
from cortex_memory_os.retrieval import RetrievalScope, rank_memories, score_memory, tokenize


def _memory() -> MemoryRecord:
    return MemoryRecord.model_validate(load_json("tests/fixtures/memory_preference.json"))


def test_tokenizer_splits_hyphenated_source_terms():
    assert {"primary", "source"} <= tokenize("primary-source research")


def test_retrieval_ranks_trusted_current_memory_over_stale_inferred_memory():
    now = datetime(2026, 4, 27, 20, 0, tzinfo=UTC)
    trusted = _memory().model_copy(
        update={
            "memory_id": "mem_trusted",
            "evidence_type": EvidenceType.USER_CONFIRMED,
            "confidence": 0.86,
            "created_at": now - timedelta(days=1),
        }
    )
    stale = _memory().model_copy(
        update={
            "memory_id": "mem_stale",
            "evidence_type": EvidenceType.INFERRED,
            "confidence": 0.99,
            "created_at": now - timedelta(days=400),
            "requires_user_confirmation": False,
        }
    )

    ranked = rank_memories([stale, trusted], "primary source synthesis", now=now)

    assert [item.memory.memory_id for item in ranked] == ["mem_trusted", "mem_stale"]
    assert ranked[0].score.source_trust_component > ranked[1].score.source_trust_component
    assert ranked[0].score.staleness_penalty < ranked[1].score.staleness_penalty


def test_non_retrievable_or_stored_only_memory_is_ineligible():
    deleted = _memory().model_copy(
        update={
            "status": MemoryStatus.DELETED,
            "influence_level": InfluenceLevel.STORED_ONLY,
            "allowed_influence": [],
        }
    )

    score = score_memory(deleted, "primary source synthesis")

    assert score.eligible is False
    assert "status_deleted" in score.reasons
    assert "stored_only" in score.reasons


def test_privacy_penalty_lowers_score_for_confidential_memory():
    public = _memory().model_copy(
        update={"memory_id": "mem_public", "sensitivity": Sensitivity.PUBLIC}
    )
    confidential = _memory().model_copy(
        update={"memory_id": "mem_confidential", "sensitivity": Sensitivity.CONFIDENTIAL}
    )
    now = datetime(2026, 4, 27, 20, 0, tzinfo=UTC)

    ranked = rank_memories([confidential, public], "primary source synthesis", now=now)

    assert [item.memory.memory_id for item in ranked] == ["mem_public", "mem_confidential"]
    assert ranked[0].score.privacy_penalty < ranked[1].score.privacy_penalty


def test_project_scope_blocks_mismatched_project_memory():
    alpha = _memory().model_copy(
        update={
            "memory_id": "mem_alpha",
            "source_refs": ["project:alpha", "scene_alpha"],
        }
    )
    beta = _memory().model_copy(
        update={
            "memory_id": "mem_beta",
            "source_refs": ["project:beta", "scene_beta"],
        }
    )

    ranked = rank_memories(
        [beta, alpha],
        "primary source synthesis",
        scope=RetrievalScope(active_project="alpha"),
    )
    beta_score = score_memory(
        beta,
        "primary source synthesis",
        scope=RetrievalScope(active_project="alpha"),
    )

    assert [item.memory.memory_id for item in ranked] == ["mem_alpha"]
    assert beta_score.eligible is False
    assert "project_scope_mismatch" in beta_score.reasons


def test_agent_and_session_scopes_require_matching_ids():
    agent_memory = _memory().model_copy(
        update={
            "memory_id": "mem_agent_codex",
            "scope": ScopeLevel.AGENT_SPECIFIC,
            "source_refs": ["agent:codex", "scene_agent"],
        }
    )
    session_memory = _memory().model_copy(
        update={
            "memory_id": "mem_session_1",
            "scope": ScopeLevel.SESSION_ONLY,
            "source_refs": ["session:session_1", "scene_session"],
        }
    )

    ranked = rank_memories(
        [agent_memory, session_memory],
        "primary source synthesis",
        scope=RetrievalScope(agent_id="codex", session_id="session_1"),
    )
    wrong_agent_score = score_memory(
        agent_memory,
        "primary source synthesis",
        scope=RetrievalScope(agent_id="claude", session_id="session_1"),
    )
    missing_session_score = score_memory(
        session_memory,
        "primary source synthesis",
        scope=RetrievalScope(agent_id="codex"),
    )

    assert {item.memory.memory_id for item in ranked} == {"mem_agent_codex", "mem_session_1"}
    assert wrong_agent_score.eligible is False
    assert "agent_scope_mismatch" in wrong_agent_score.reasons
    assert missing_session_score.eligible is False
    assert "session_scope_missing" in missing_session_score.reasons
