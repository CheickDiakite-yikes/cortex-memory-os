from datetime import UTC, datetime

from cortex_memory_os.clicky_ux import CLICKY_UX_COMPANION_POLICY_REF
from cortex_memory_os.dashboard_encrypted_index import (
    DASHBOARD_LIVE_BACKBONE_POLICY_REF,
    ENCRYPTED_INDEX_DASHBOARD_LIVE_ID,
    ENCRYPTED_INDEX_DASHBOARD_LIVE_POLICY_REF,
    build_dashboard_operational_backbone,
    panel_payload_is_redacted,
)
from cortex_memory_os.durable_synthetic_memory_receipts import (
    DURABLE_SYNTHETIC_MEMORY_RECEIPTS_POLICY_REF,
)
from cortex_memory_os.key_management import KEY_MANAGEMENT_PLAN_POLICY_REF
from cortex_memory_os.shadow_pointer_native_live_feed import (
    NATIVE_SHADOW_POINTER_LIVE_FEED_POLICY_REF,
)


def test_dashboard_operational_backbone_is_metadata_only_and_ready():
    backbone = build_dashboard_operational_backbone(
        now=datetime(2026, 5, 2, 12, 0, tzinfo=UTC)
    )
    payload = backbone.model_dump_json()

    assert backbone.encrypted_index_panel.panel_id == ENCRYPTED_INDEX_DASHBOARD_LIVE_ID
    assert ENCRYPTED_INDEX_DASHBOARD_LIVE_POLICY_REF in backbone.encrypted_index_panel.policy_refs
    assert KEY_MANAGEMENT_PLAN_POLICY_REF in backbone.live_backbone_panel.policy_refs
    assert NATIVE_SHADOW_POINTER_LIVE_FEED_POLICY_REF in backbone.live_backbone_panel.policy_refs
    assert DURABLE_SYNTHETIC_MEMORY_RECEIPTS_POLICY_REF in backbone.live_backbone_panel.policy_refs
    assert DASHBOARD_LIVE_BACKBONE_POLICY_REF in backbone.live_backbone_panel.policy_refs
    assert backbone.encrypted_index_panel.write_receipt_count == 1
    assert backbone.encrypted_index_panel.search_result_count >= 1
    assert backbone.encrypted_index_panel.candidate_open_count >= 1
    assert backbone.encrypted_index_panel.content_redacted
    assert backbone.encrypted_index_panel.source_refs_redacted
    assert backbone.encrypted_index_panel.query_redacted
    assert backbone.encrypted_index_panel.token_text_redacted
    assert not backbone.encrypted_index_panel.key_material_visible
    assert not backbone.live_backbone_panel.raw_private_data_retained
    assert "raw://" not in payload
    assert "encrypted_blob://" not in payload
    assert panel_payload_is_redacted(backbone)


def test_dashboard_backbone_policy_refs_include_clicky_companion_when_shell_adds_it():
    # The panel module does not build the companion itself, but this guards the
    # public policy ref expected by the shell contract.
    assert CLICKY_UX_COMPANION_POLICY_REF == "policy_clicky_ux_companion_v1"
