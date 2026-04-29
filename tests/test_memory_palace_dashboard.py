from datetime import UTC, datetime

import pytest

from cortex_memory_os.contracts import InfluenceLevel, MemoryRecord, MemoryStatus, ScopeLevel
from cortex_memory_os.fixtures import load_json
from cortex_memory_os.memory_lifecycle import transition_memory
from cortex_memory_os.memory_palace import MemoryPalaceService
from cortex_memory_os.memory_palace_dashboard import MEMORY_PALACE_DASHBOARD_POLICY_REF
from cortex_memory_os.retrieval import RetrievalScope
from cortex_memory_os.sensitive_data_policy import REDACTED_SECRET_PLACEHOLDER
from cortex_memory_os.sqlite_store import SQLiteMemoryGraphStore


def _memory() -> MemoryRecord:
    return MemoryRecord.model_validate(load_json("tests/fixtures/memory_preference.json"))


def _service_with_dashboard_memories(tmp_path):
    store = SQLiteMemoryGraphStore(tmp_path / "cortex.sqlite3")
    active = _memory().model_copy(
        update={
            "memory_id": "mem_active_alpha",
            "source_refs": ["project:alpha", "scene_active"],
        }
    )
    secret = _memory().model_copy(
        update={
            "memory_id": "mem_secret_preview",
            "content": "Use synthetic token=CORTEX_FAKE_TOKEN_dashboardSECRET123 only in tests.",
            "source_refs": ["project:alpha", "scene_secret"],
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
    deleted = transition_memory(
        _memory().model_copy(
            update={
                "memory_id": "mem_deleted_dashboard",
                "content": "Deleted dashboard content should stay hidden.",
            }
        ),
        MemoryStatus.DELETED,
        now=datetime(2026, 4, 28, 8, 0, tzinfo=UTC),
    )
    store.add_memories([active, secret, wrong_project, stored_only, deleted])
    service = MemoryPalaceService(store)
    service.delete_memory(active.memory_id, now=datetime(2026, 4, 28, 9, 0, tzinfo=UTC))
    corrected = service.correct_memory(
        secret.memory_id,
        "User wants synthetic dashboard previews to redact tokens.",
        now=datetime(2026, 4, 28, 9, 5, tzinfo=UTC),
    )
    return service, {
        "active": active,
        "secret": secret,
        "corrected": corrected.corrected_memory,
        "wrong_project": wrong_project,
        "stored_only": stored_only,
        "deleted": deleted,
    }


def test_memory_palace_dashboard_cards_are_safe_and_actionable(tmp_path):
    service, memories = _service_with_dashboard_memories(tmp_path)

    dashboard = service.dashboard(
        scope=RetrievalScope(active_project="alpha"),
        now=datetime(2026, 4, 28, 10, 0, tzinfo=UTC),
    )
    serialized = dashboard.model_dump_json()
    cards = {card.memory_id: card for card in dashboard.cards}
    corrected_card = cards[memories["corrected"].memory_id]
    active_card = cards[memories["active"].memory_id]
    deleted_card = cards[memories["deleted"].memory_id]

    assert MEMORY_PALACE_DASHBOARD_POLICY_REF in dashboard.policy_refs
    assert dashboard.audit_summary.counts_by_action == {
        "correct_memory": 1,
        "delete_memory": 1,
    }
    assert active_card.status == MemoryStatus.DELETED
    assert active_card.content_preview is None
    assert active_card.recall_eligible is False
    assert [action.gateway_tool for action in active_card.action_plans] == ["memory.explain"]
    assert deleted_card.content_preview is None
    assert deleted_card.content_redacted is True
    assert "Deleted dashboard content should stay hidden" not in serialized
    assert corrected_card.recall_eligible is True
    assert {action.gateway_tool for action in corrected_card.action_plans} == {
        "memory.explain",
        "memory.correct",
        "memory.forget",
        "memory.export",
    }
    assert any(action.requires_confirmation for action in corrected_card.action_plans)
    assert any(action.data_egress for action in corrected_card.action_plans)
    assert REDACTED_SECRET_PLACEHOLDER not in corrected_card.content_preview


def test_memory_palace_dashboard_export_preview_is_scoped_and_redacted(tmp_path):
    service, memories = _service_with_dashboard_memories(tmp_path)

    dashboard = service.dashboard(
        selected_memory_ids=[
            memories["corrected"].memory_id,
            memories["wrong_project"].memory_id,
            memories["stored_only"].memory_id,
            memories["active"].memory_id,
        ],
        scope=RetrievalScope(active_project="alpha"),
        now=datetime(2026, 4, 28, 10, 10, tzinfo=UTC),
    )
    preview = dashboard.export_preview

    assert preview.selection_mode == "explicit_ids"
    assert preview.selected_count == 4
    assert preview.exportable_count == 1
    assert preview.omitted_count == 3
    assert preview.requires_confirmation is True
    assert preview.data_egress is True
    assert preview.gateway_tool == "memory.export"
    assert preview.omission_reasons[memories["wrong_project"].memory_id] == [
        "project_scope_mismatch"
    ]
    assert preview.omission_reasons[memories["stored_only"].memory_id] == [
        "not_recall_allowed"
    ]
    assert preview.omission_reasons[memories["active"].memory_id] == [
        "not_recall_allowed"
    ]


def test_memory_palace_dashboard_rejects_unknown_explicit_selection(tmp_path):
    service, _ = _service_with_dashboard_memories(tmp_path)

    with pytest.raises(ValueError, match="unknown selected_memory_ids"):
        service.dashboard(selected_memory_ids=["mem_missing"])
