from datetime import UTC, datetime

from cortex_memory_os.dashboard_shell import (
    DASHBOARD_SHELL_ID,
    DASHBOARD_SHELL_POLICY_REF,
    build_dashboard_shell,
    render_dashboard_data_js,
    run_dashboard_shell_smoke,
)
from cortex_memory_os.dashboard_gateway_actions import DASHBOARD_GATEWAY_ACTIONS_POLICY_REF
from cortex_memory_os.memory_palace_dashboard import MEMORY_PALACE_DASHBOARD_POLICY_REF
from cortex_memory_os.skill_forge_dashboard import SKILL_FORGE_CANDIDATE_LIST_POLICY_REF
from cortex_memory_os.skill_metrics_dashboard import SKILL_METRICS_DASHBOARD_POLICY_REF
from cortex_memory_os.retrieval_receipts_dashboard import (
    RETRIEVAL_RECEIPTS_DASHBOARD_POLICY_REF,
)
from cortex_memory_os.memory_encryption import MEMORY_ENCRYPTION_DEFAULT_POLICY_REF


def test_dashboard_shell_composes_safe_view_models():
    shell = build_dashboard_shell(now=datetime(2026, 4, 30, 11, 0, tzinfo=UTC))
    serialized = shell.model_dump_json()

    assert shell.shell_id == DASHBOARD_SHELL_ID
    assert DASHBOARD_SHELL_POLICY_REF in shell.policy_refs
    assert DASHBOARD_GATEWAY_ACTIONS_POLICY_REF in shell.policy_refs
    assert MEMORY_PALACE_DASHBOARD_POLICY_REF in shell.policy_refs
    assert SKILL_FORGE_CANDIDATE_LIST_POLICY_REF in shell.policy_refs
    assert SKILL_METRICS_DASHBOARD_POLICY_REF in shell.policy_refs
    assert RETRIEVAL_RECEIPTS_DASHBOARD_POLICY_REF in shell.policy_refs
    assert MEMORY_ENCRYPTION_DEFAULT_POLICY_REF in shell.policy_refs
    assert len(shell.status_strip) == 4
    assert len(shell.insight_panels) >= 5
    assert any(panel.title == "Encryption Default" for panel in shell.insight_panels)
    assert all(panel.content_redacted for panel in shell.insight_panels)
    assert all(panel.source_refs_redacted for panel in shell.insight_panels)
    assert len(shell.memory_palace.cards) >= 4
    assert len(shell.skill_forge.cards) >= 3
    assert len(shell.skill_metrics.cards) >= 3
    assert shell.skill_metrics.total_run_count >= 5
    assert not shell.skill_metrics.procedure_text_included
    assert not shell.skill_metrics.autonomy_change_allowed
    assert shell.retrieval_debug.receipt_count >= 2
    assert shell.retrieval_debug.source_refs_redacted
    assert shell.retrieval_debug.content_redacted
    assert not shell.retrieval_debug.hostile_text_included
    assert shell.safe_receipts
    assert shell.gateway_action_receipts
    assert any(receipt.allowed_gateway_call for receipt in shell.gateway_action_receipts)
    assert any(not receipt.allowed_gateway_call for receipt in shell.gateway_action_receipts)
    assert any(card.action_plans for card in shell.memory_palace.cards)
    assert any(card.action_plans for card in shell.skill_forge.cards)
    assert "CORTEX_FAKE_TOKEN" not in serialized
    assert "raw://" not in serialized
    assert "encrypted_blob://" not in serialized
    assert "Search primary sources" not in serialized
    assert "Gather approved metrics" not in serialized
    assert "Reproduce the local login flow" not in serialized
    assert "Ignore previous instructions" not in serialized
    assert "external:https://example.invalid/attack" not in serialized


def test_dashboard_data_js_is_redacted_and_static_app_ready():
    shell = build_dashboard_shell(now=datetime(2026, 4, 30, 11, 0, tzinfo=UTC))
    data_js = render_dashboard_data_js(shell)

    assert data_js.startswith("window.CORTEX_DASHBOARD_DATA = ")
    assert DASHBOARD_SHELL_ID in data_js
    assert "MemoryPalaceDashboard" not in data_js
    assert "CORTEX_FAKE_TOKEN" not in data_js
    assert "OPENAI_API_KEY=" not in data_js
    assert "raw://" not in data_js
    assert "Skill Metrics" in data_js
    assert "Retrieval Receipts" in data_js
    assert "Search primary sources" not in data_js
    assert "external:https://example.invalid/attack" not in data_js


def test_dashboard_shell_smoke_contract_passes():
    result = run_dashboard_shell_smoke()

    assert result.passed
    assert result.policy_ref == DASHBOARD_SHELL_POLICY_REF
    assert result.ui_files_present is True
    assert result.memory_card_count >= 4
    assert result.skill_card_count >= 3
    assert result.skill_metric_card_count >= 3
    assert result.skill_metric_run_count >= 5
    assert result.retrieval_receipt_card_count >= 2
    assert result.safe_receipt_count >= 4
    assert result.insight_panel_count >= 5
    assert result.encryption_default_visible is True
    assert result.gateway_action_receipt_count > 0
    assert result.gateway_actions_present is True
    assert result.skill_metrics_present is True
    assert result.retrieval_receipts_present is True
    assert result.procedure_text_retained is False
    assert result.retrieval_source_refs_retained is False
    assert result.secret_retained is False
    assert result.raw_private_data_retained is False
    assert result.action_plans_present is True
    assert result.missing_ui_terms == []
    assert result.missing_doc_terms == []
