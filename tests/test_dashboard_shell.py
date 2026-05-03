from datetime import UTC, datetime
from pathlib import Path

from cortex_memory_os.dashboard_shell import (
    DASHBOARD_DEMO_PATH_POLICY_REF,
    DASHBOARD_FOCUS_INSPECTOR_POLICY_REF,
    DASHBOARD_SHELL_ID,
    DASHBOARD_SHELL_POLICY_REF,
    build_dashboard_shell,
    render_dashboard_data_js,
    run_dashboard_shell_smoke,
)
from cortex_memory_os.capture_readiness_ladder import (
    CAPTURE_READINESS_LADDER_ID,
    CAPTURE_READINESS_LADDER_POLICY_REF,
)
from cortex_memory_os.clicky_ux import (
    CLICKY_UX_COMPANION_POLICY_REF,
    CLICKY_UX_LESSONS_POLICY_REF,
)
from cortex_memory_os.dashboard_encrypted_index import (
    DASHBOARD_LIVE_BACKBONE_POLICY_REF,
    ENCRYPTED_INDEX_DASHBOARD_LIVE_POLICY_REF,
)
from cortex_memory_os.dashboard_live_data_adapter import (
    DASHBOARD_LIVE_DATA_ADAPTER_POLICY_REF,
    LIVE_DASHBOARD_RECEIPTS_POLICY_REF,
)
from cortex_memory_os.durable_synthetic_memory_receipts import (
    DURABLE_SYNTHETIC_MEMORY_RECEIPTS_POLICY_REF,
)
from cortex_memory_os.key_management import KEY_MANAGEMENT_PLAN_POLICY_REF
from cortex_memory_os.shadow_pointer_native_live_feed import (
    NATIVE_SHADOW_POINTER_LIVE_FEED_POLICY_REF,
)
from cortex_memory_os.dashboard_gateway_actions import DASHBOARD_GATEWAY_ACTIONS_POLICY_REF
from cortex_memory_os.memory_palace_dashboard import MEMORY_PALACE_DASHBOARD_POLICY_REF
from cortex_memory_os.skill_forge_dashboard import SKILL_FORGE_CANDIDATE_LIST_POLICY_REF
from cortex_memory_os.skill_metrics_dashboard import SKILL_METRICS_DASHBOARD_POLICY_REF
from cortex_memory_os.retrieval_receipts_dashboard import (
    RETRIEVAL_RECEIPTS_DASHBOARD_POLICY_REF,
)
from cortex_memory_os.memory_encryption import MEMORY_ENCRYPTION_DEFAULT_POLICY_REF
from cortex_memory_os.shadow_pointer import (
    CONSENT_FIRST_ONBOARDING_POLICY_REF,
    SHADOW_POINTER_LIVE_RECEIPT_POLICY_REF,
    SHADOW_POINTER_STATE_MACHINE_POLICY_REF,
    ShadowPointerState,
)


def test_dashboard_shell_composes_safe_view_models():
    shell = build_dashboard_shell(now=datetime(2026, 4, 30, 11, 0, tzinfo=UTC))
    serialized = shell.model_dump_json()

    assert shell.shell_id == DASHBOARD_SHELL_ID
    assert DASHBOARD_SHELL_POLICY_REF in shell.policy_refs
    assert DASHBOARD_GATEWAY_ACTIONS_POLICY_REF in shell.policy_refs
    assert DASHBOARD_FOCUS_INSPECTOR_POLICY_REF in shell.policy_refs
    assert DASHBOARD_DEMO_PATH_POLICY_REF in shell.policy_refs
    assert MEMORY_PALACE_DASHBOARD_POLICY_REF in shell.policy_refs
    assert SKILL_FORGE_CANDIDATE_LIST_POLICY_REF in shell.policy_refs
    assert SKILL_METRICS_DASHBOARD_POLICY_REF in shell.policy_refs
    assert RETRIEVAL_RECEIPTS_DASHBOARD_POLICY_REF in shell.policy_refs
    assert MEMORY_ENCRYPTION_DEFAULT_POLICY_REF in shell.policy_refs
    assert SHADOW_POINTER_STATE_MACHINE_POLICY_REF in shell.policy_refs
    assert SHADOW_POINTER_LIVE_RECEIPT_POLICY_REF in shell.policy_refs
    assert CONSENT_FIRST_ONBOARDING_POLICY_REF in shell.policy_refs
    assert KEY_MANAGEMENT_PLAN_POLICY_REF in shell.policy_refs
    assert ENCRYPTED_INDEX_DASHBOARD_LIVE_POLICY_REF in shell.policy_refs
    assert NATIVE_SHADOW_POINTER_LIVE_FEED_POLICY_REF in shell.policy_refs
    assert DURABLE_SYNTHETIC_MEMORY_RECEIPTS_POLICY_REF in shell.policy_refs
    assert DASHBOARD_LIVE_BACKBONE_POLICY_REF in shell.policy_refs
    assert CLICKY_UX_LESSONS_POLICY_REF in shell.policy_refs
    assert CLICKY_UX_COMPANION_POLICY_REF in shell.policy_refs
    assert DASHBOARD_LIVE_DATA_ADAPTER_POLICY_REF in shell.policy_refs
    assert LIVE_DASHBOARD_RECEIPTS_POLICY_REF in shell.policy_refs
    assert CAPTURE_READINESS_LADDER_POLICY_REF in shell.policy_refs
    assert len(shell.status_strip) == 4
    assert shell.shadow_pointer_live_receipt.memory_eligible is False
    assert shell.shadow_pointer_live_receipt.raw_ref_retained is False
    assert shell.shadow_pointer_live_receipt.raw_payload_included is False
    assert shell.shadow_pointer_live_receipt.compact_fields["trust"] == "external_untrusted"
    assert {state.state for state in shell.shadow_pointer_states} == set(ShadowPointerState)
    assert shell.consent_onboarding.synthetic_only is True
    assert shell.consent_onboarding.real_capture_started is False
    assert shell.consent_onboarding.raw_storage_enabled is False
    assert shell.consent_onboarding.durable_private_memory_write_enabled is False
    assert shell.consent_onboarding.external_effect_enabled is False
    assert shell.key_management_plan.raw_key_material_included is False
    assert shell.key_management_plan.production_allows_noop_cipher is False
    assert shell.encrypted_index_panel.content_redacted is True
    assert shell.encrypted_index_panel.source_refs_redacted is True
    assert shell.encrypted_index_panel.query_redacted is True
    assert shell.encrypted_index_panel.token_text_redacted is True
    assert shell.encrypted_index_panel.key_material_visible is False
    assert shell.encrypted_index_panel.search_result_count >= 1
    assert shell.native_live_feed.display_only is True
    assert shell.native_live_feed.capture_started is False
    assert shell.native_live_feed.memory_write_allowed is False
    assert shell.native_live_feed.raw_ref_retained is False
    assert shell.durable_synthetic_memory_receipt.synthetic_only is True
    assert shell.durable_synthetic_memory_receipt.encrypted_store_used is True
    assert shell.durable_synthetic_memory_receipt.durable_synthetic_memory_written is True
    assert shell.durable_synthetic_memory_receipt.prohibited_leak_count == 0
    assert shell.live_backbone_panel.content_redacted is True
    assert shell.live_backbone_panel.raw_private_data_retained is False
    assert shell.clicky_ux_companion.title == "Cursor Companion"
    assert shell.clicky_ux_companion.display_only is True
    assert shell.clicky_ux_companion.voice_capture_enabled is False
    assert shell.clicky_ux_companion.memory_write_allowed is False
    assert shell.dashboard_live_data_adapter.read_only is True
    assert shell.dashboard_live_data_adapter.local_only is True
    assert shell.dashboard_live_data_adapter.gateway_executed_count > 0
    assert shell.dashboard_live_data_adapter.gateway_blocked_count > 0
    assert shell.dashboard_live_data_adapter.retrieval_receipt_count > 0
    assert shell.dashboard_live_data_adapter.skill_metric_run_count > 0
    assert shell.dashboard_live_data_adapter.write_path_enabled is False
    assert shell.dashboard_live_data_adapter.raw_payload_returned is False
    assert shell.live_dashboard_receipts.title == "Live Safe Receipts"
    assert shell.live_dashboard_receipts.refresh_mode == "read_only_receipts"
    assert shell.live_dashboard_receipts.gateway_executed_count > 0
    assert shell.live_dashboard_receipts.mutation_enabled is False
    assert shell.live_dashboard_receipts.raw_payload_returned is False
    assert shell.capture_readiness_ladder.ladder_id == CAPTURE_READINESS_LADDER_ID
    assert len(shell.capture_readiness_ladder.steps) == 10
    assert shell.capture_readiness_ladder.display_only is True
    assert shell.capture_readiness_ladder.memory_write_allowed is False
    assert shell.capture_readiness_ladder.raw_payloads_included is False
    assert shell.capture_readiness_ladder.raw_ref_retained is False
    assert shell.capture_readiness_ladder.external_effect_enabled is False
    assert "continuous_capture" in shell.capture_readiness_ladder.blocked_effects
    assert "durable_memory_write" in shell.capture_readiness_ladder.blocked_effects
    assert len(shell.insight_panels) >= 5
    assert any(panel.title == "Encryption Default" for panel in shell.insight_panels)
    assert all(panel.content_redacted for panel in shell.insight_panels)
    assert all(panel.source_refs_redacted for panel in shell.insight_panels)
    assert shell.focus_inspector.title == "Focus Inspector"
    assert shell.focus_inspector.content_redacted is True
    assert shell.focus_inspector.source_refs_redacted is True
    assert shell.focus_inspector.procedure_redacted is True
    assert DASHBOARD_FOCUS_INSPECTOR_POLICY_REF in shell.focus_inspector.policy_refs
    assert any(action.gateway_tool == "memory.explain" for action in shell.focus_inspector.actions)
    assert shell.demo_path.title == "Safe Demo Path"
    assert shell.demo_path.synthetic_only is True
    assert shell.demo_path.real_capture_started is False
    assert shell.demo_path.raw_storage_enabled is False
    assert shell.demo_path.mutation_enabled is False
    assert shell.demo_path.stress_command == "uv run cortex-demo-stress --iterations 12 --json"
    assert shell.demo_path.stress_iterations == 12
    assert DASHBOARD_DEMO_PATH_POLICY_REF in shell.demo_path.policy_refs
    assert len(shell.demo_path.steps) == 4
    assert "real_screen_capture" in shell.demo_path.blocked_effects
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
    assert "Synthetic durable memory receipt observed" not in serialized
    assert "synthetic://durable-memory-receipt/source" not in serialized


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
    assert "Shadow Pointer Live Receipt" in data_js
    assert "Consent-first Onboarding" not in data_js
    assert "consent_onboarding" in data_js
    assert "Safe Demo Path" in data_js
    assert "DEMO-READINESS-001" in data_js
    assert "cortex-demo-stress" in data_js
    assert "Cursor Companion" in data_js
    assert "Encrypted Index Receipts" in data_js
    assert "Live Receipt Backbone" in data_js
    assert "Live Safe Receipts" in data_js
    assert "DASHBOARD-LIVE-DATA-ADAPTER-001" in data_js
    assert "Capture Readiness Ladder" in data_js
    assert CAPTURE_READINESS_LADDER_ID in data_js
    assert "data-view-section" not in data_js
    assert "Search primary sources" not in data_js
    assert "external:https://example.invalid/attack" not in data_js


def test_dashboard_static_app_switches_focus_with_primary_views():
    app_js = Path("ui/cortex-dashboard/app.js").read_text()

    assert 'aria-pressed="${item.item_id === activeView ? "true" : "false"}"' in app_js
    assert "function ensureFocusForActiveView()" in app_js
    assert "activeView === \"memory_palace\"" in app_js
    assert "activeView === \"skill_forge\"" in app_js
    assert "selectedFocus = focusFromMemory(card)" in app_js
    assert "selectedFocus = focusFromSkill(card)" in app_js


def test_dashboard_static_app_refreshes_stale_capture_token():
    app_js = Path("ui/cortex-dashboard/app.js").read_text()

    assert "let captureControlConfig = window.CORTEX_CAPTURE_CONTROL || null;" in app_js
    assert "async function refreshCaptureControlConfig()" in app_js
    assert "capture-control-config.js?ts=" in app_js
    assert "missing_or_invalid_capture_token" in app_js
    assert "Capture bridge token refreshed. Retrying local command once." in app_js
    assert "callCaptureControlWithConfig(action, payload, { refreshed: true })" in app_js


def test_dashboard_static_app_renders_capture_readiness_ladder():
    app_js = Path("ui/cortex-dashboard/app.js").read_text()
    index_html = Path("ui/cortex-dashboard/index.html").read_text()

    assert "function renderCaptureReadinessLadder()" in app_js
    assert "capture-ladder-preflight" in app_js
    assert "capture-ladder-screen-probe" in app_js
    assert "capture-readiness-ladder" in index_html
    assert "CAPTURE-READINESS-LADDER-001" in index_html


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
    assert result.focus_inspector_present is True
    assert result.demo_path_present is True
    assert result.shadow_pointer_live_receipt_present is True
    assert result.consent_onboarding_present is True
    assert result.nav_view_switching_present is True
    assert result.key_management_plan_present is True
    assert result.encrypted_index_dashboard_present is True
    assert result.native_live_feed_present is True
    assert result.durable_synthetic_memory_receipt_present is True
    assert result.dashboard_live_backbone_present is True
    assert result.clicky_ux_companion_present is True
    assert result.dashboard_live_data_adapter_present is True
    assert result.live_dashboard_receipts_present is True
    assert result.capture_control_present is True
    assert result.capture_readiness_ladder_present is True
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
