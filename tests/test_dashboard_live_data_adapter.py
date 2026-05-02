from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from cortex_memory_os.dashboard_encrypted_index import build_dashboard_operational_backbone
from cortex_memory_os.dashboard_gateway_actions import build_dashboard_gateway_action_receipts
from cortex_memory_os.dashboard_live_data_adapter import (
    DASHBOARD_LIVE_DATA_ADAPTER_ID,
    DASHBOARD_LIVE_DATA_ADAPTER_POLICY_REF,
    LIVE_DASHBOARD_RECEIPTS_ID,
    DashboardLiveDataAdapterSnapshot,
    build_dashboard_live_data_adapter_snapshot,
    build_live_dashboard_receipts_panel,
)
from cortex_memory_os.dashboard_live_gateway import build_dashboard_live_gateway_panel
from cortex_memory_os.memory_palace_dashboard import build_memory_palace_dashboard
from cortex_memory_os.retrieval import RetrievalScope
from cortex_memory_os.retrieval_receipts_dashboard import build_retrieval_receipts_dashboard
from cortex_memory_os.dashboard_shell import (
    _sample_audit_events,
    _sample_memories,
    _sample_retrieval_receipts,
    _sample_skill_outcome_events,
    _sample_skills,
    _redact_dashboard_skill_procedures,
)
from cortex_memory_os.skill_forge_dashboard import build_skill_forge_candidate_list
from cortex_memory_os.skill_metrics_dashboard import build_skill_metrics_dashboard


NOW = datetime(2026, 5, 2, 16, 0, tzinfo=UTC)


def _snapshot():
    memories = _sample_memories(NOW)
    memory_dashboard = build_memory_palace_dashboard(
        memories,
        audit_events=_sample_audit_events(NOW),
        scope=RetrievalScope(active_project="cortex-memory-os"),
        now=NOW,
    )
    skills = _sample_skills()
    skill_list = _redact_dashboard_skill_procedures(
        build_skill_forge_candidate_list(skills, now=NOW)
    )
    gateway_receipts = build_dashboard_gateway_action_receipts(
        memory_dashboard,
        skill_list,
        now=NOW,
    )
    live_gateway = build_dashboard_live_gateway_panel(
        gateway_action_receipts=gateway_receipts,
        now=NOW,
    )
    return build_dashboard_live_data_adapter_snapshot(
        live_gateway_panel=live_gateway,
        operational_backbone=build_dashboard_operational_backbone(now=NOW),
        skill_metrics=build_skill_metrics_dashboard(
            skills,
            _sample_skill_outcome_events(skills, NOW),
            now=NOW,
        ),
        retrieval_debug=build_retrieval_receipts_dashboard(
            _sample_retrieval_receipts(memories, NOW),
            now=NOW,
        ),
        now=NOW,
    )


def test_dashboard_live_data_adapter_reads_local_receipts_without_write_paths():
    snapshot = _snapshot()
    payload = snapshot.model_dump_json()

    assert snapshot.snapshot_id == DASHBOARD_LIVE_DATA_ADAPTER_ID
    assert DASHBOARD_LIVE_DATA_ADAPTER_POLICY_REF in snapshot.policy_refs
    assert snapshot.read_only is True
    assert snapshot.local_only is True
    assert snapshot.gateway_executed_count > 0
    assert snapshot.gateway_blocked_count > 0
    assert snapshot.context_pack_memory_count > 0
    assert snapshot.skill_review_count > 0
    assert snapshot.retrieval_receipt_count > 0
    assert snapshot.ops_passed_cases > 0
    assert snapshot.write_path_enabled is False
    assert snapshot.mutation_enabled is False
    assert snapshot.raw_payload_returned is False
    assert snapshot.raw_ref_retained is False
    assert "raw://" not in payload
    assert "encrypted_blob://" not in payload


def test_live_dashboard_receipts_panel_refreshes_from_adapter_counts_only():
    snapshot = _snapshot()
    panel = build_live_dashboard_receipts_panel(snapshot)
    payload = panel.model_dump_json()

    assert panel.panel_id == LIVE_DASHBOARD_RECEIPTS_ID
    assert panel.gateway_executed_count == snapshot.gateway_executed_count
    assert panel.retrieval_receipt_count == snapshot.retrieval_receipt_count
    assert panel.skill_metric_run_count == snapshot.skill_metric_run_count
    assert panel.refresh_mode == "read_only_receipts"
    assert panel.content_redacted is True
    assert panel.source_refs_redacted is True
    assert panel.raw_payload_returned is False
    assert panel.mutation_enabled is False
    assert "User consistently asks" not in payload


def test_dashboard_live_data_adapter_rejects_writes_or_raw_payloads():
    snapshot = _snapshot()

    with pytest.raises(ValidationError, match="writes or mutations"):
        DashboardLiveDataAdapterSnapshot.model_validate(
            snapshot.model_dump() | {"write_path_enabled": True}
        )

    with pytest.raises(ValidationError, match="raw payloads or refs"):
        DashboardLiveDataAdapterSnapshot.model_validate(
            snapshot.model_dump() | {"raw_payload_returned": True}
        )
