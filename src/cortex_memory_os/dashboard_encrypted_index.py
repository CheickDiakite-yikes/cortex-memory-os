"""Dashboard-safe panels for encrypted index and live receipt readiness."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from pydantic import Field, model_validator

from cortex_memory_os.contracts import SourceTrust, StrictModel
from cortex_memory_os.durable_synthetic_memory_receipts import (
    DURABLE_SYNTHETIC_MEMORY_RECEIPTS_POLICY_REF,
    DurableSyntheticMemoryReceipt,
    run_durable_synthetic_memory_receipts,
)
from cortex_memory_os.encrypted_graph_index import UNIFIED_ENCRYPTED_GRAPH_INDEX_POLICY_REF
from cortex_memory_os.key_management import (
    KEY_MANAGEMENT_PLAN_ID,
    KEY_MANAGEMENT_PLAN_POLICY_REF,
    KeyManagementPlan,
    build_default_key_management_plan,
)
from cortex_memory_os.memory_encryption import MEMORY_ENCRYPTION_DEFAULT_POLICY_REF
from cortex_memory_os.shadow_pointer import (
    ShadowPointerObservationMode,
    build_live_receipt,
    default_shadow_pointer_snapshot,
)
from cortex_memory_os.shadow_pointer_native_live_feed import (
    NATIVE_SHADOW_POINTER_LIVE_FEED_POLICY_REF,
    NativeShadowPointerLiveFeedReceipt,
    build_native_shadow_pointer_live_feed,
)

ENCRYPTED_INDEX_DASHBOARD_LIVE_ID = "ENCRYPTED-INDEX-DASHBOARD-LIVE-001"
ENCRYPTED_INDEX_DASHBOARD_LIVE_POLICY_REF = (
    "policy_encrypted_index_dashboard_live_v1"
)
DASHBOARD_LIVE_BACKBONE_ID = "DASHBOARD-LIVE-BACKBONE-001"
DASHBOARD_LIVE_BACKBONE_POLICY_REF = "policy_dashboard_live_backbone_v1"


class DashboardEncryptedIndexPanel(StrictModel):
    panel_id: str = ENCRYPTED_INDEX_DASHBOARD_LIVE_ID
    title: str = "Encrypted Index Receipts"
    summary: str = Field(min_length=1)
    key_plan_id: str = KEY_MANAGEMENT_PLAN_ID
    write_receipt_count: int = Field(ge=0)
    graph_receipt_count: int = Field(ge=0)
    search_result_count: int = Field(ge=0)
    candidate_open_count: int = Field(ge=0)
    token_digest_count: int = Field(ge=0)
    graph_token_digest_count: int = Field(ge=0)
    source_ref_count: int = Field(ge=0)
    gateway_tools: list[str] = Field(min_length=1)
    content_redacted: bool = True
    source_refs_redacted: bool = True
    query_redacted: bool = True
    token_text_redacted: bool = True
    key_material_visible: bool = False
    raw_private_data_retained: bool = False
    policy_refs: list[str] = Field(
        default_factory=lambda: [
            ENCRYPTED_INDEX_DASHBOARD_LIVE_POLICY_REF,
            UNIFIED_ENCRYPTED_GRAPH_INDEX_POLICY_REF,
            MEMORY_ENCRYPTION_DEFAULT_POLICY_REF,
            KEY_MANAGEMENT_PLAN_POLICY_REF,
        ]
    )

    @model_validator(mode="after")
    def keep_panel_metadata_only(self) -> DashboardEncryptedIndexPanel:
        if ENCRYPTED_INDEX_DASHBOARD_LIVE_POLICY_REF not in self.policy_refs:
            raise ValueError("encrypted index dashboard panel requires policy ref")
        if not (
            self.content_redacted
            and self.source_refs_redacted
            and self.query_redacted
            and self.token_text_redacted
        ):
            raise ValueError("encrypted index dashboard panel must redact sensitive fields")
        if self.key_material_visible:
            raise ValueError("encrypted index dashboard panel cannot show key material")
        if self.raw_private_data_retained:
            raise ValueError("encrypted index dashboard panel cannot retain raw private data")
        return self


class DashboardLiveBackbonePanel(StrictModel):
    panel_id: str = DASHBOARD_LIVE_BACKBONE_ID
    title: str = "Live Receipt Backbone"
    summary: str = Field(min_length=1)
    key_plan_id: str = KEY_MANAGEMENT_PLAN_ID
    encrypted_index_panel_id: str = ENCRYPTED_INDEX_DASHBOARD_LIVE_ID
    native_feed_id: str
    durable_receipt_id: str
    ready_components: list[str] = Field(min_length=4)
    blocked_effects: list[str] = Field(min_length=1)
    content_redacted: bool = True
    source_refs_redacted: bool = True
    key_material_visible: bool = False
    raw_private_data_retained: bool = False
    policy_refs: list[str] = Field(
        default_factory=lambda: [
            DASHBOARD_LIVE_BACKBONE_POLICY_REF,
            KEY_MANAGEMENT_PLAN_POLICY_REF,
            ENCRYPTED_INDEX_DASHBOARD_LIVE_POLICY_REF,
            NATIVE_SHADOW_POINTER_LIVE_FEED_POLICY_REF,
            DURABLE_SYNTHETIC_MEMORY_RECEIPTS_POLICY_REF,
        ]
    )

    @model_validator(mode="after")
    def keep_backbone_safe(self) -> DashboardLiveBackbonePanel:
        if DASHBOARD_LIVE_BACKBONE_POLICY_REF not in self.policy_refs:
            raise ValueError("dashboard live backbone requires policy ref")
        required_components = {
            "key_management_plan",
            "encrypted_index_panel",
            "native_live_feed",
            "durable_synthetic_receipt",
        }
        if missing := sorted(required_components.difference(self.ready_components)):
            raise ValueError(f"dashboard live backbone missing components: {missing}")
        if not self.content_redacted or not self.source_refs_redacted:
            raise ValueError("dashboard live backbone must redact content/source refs")
        if self.key_material_visible or self.raw_private_data_retained:
            raise ValueError("dashboard live backbone cannot show keys or raw private data")
        required_blocked = {
            "real_screen_capture",
            "durable_private_memory_write",
            "raw_ref_retention",
            "external_effect",
        }
        if missing := sorted(required_blocked.difference(self.blocked_effects)):
            raise ValueError(f"dashboard live backbone missing blocked effects: {missing}")
        return self


class DashboardOperationalBackbone(StrictModel):
    key_management_plan: KeyManagementPlan
    encrypted_index_panel: DashboardEncryptedIndexPanel
    native_live_feed: NativeShadowPointerLiveFeedReceipt
    durable_synthetic_memory_receipt: DurableSyntheticMemoryReceipt
    live_backbone_panel: DashboardLiveBackbonePanel


def build_encrypted_index_dashboard_panel(
    durable_receipt: DurableSyntheticMemoryReceipt,
    key_plan: KeyManagementPlan,
) -> DashboardEncryptedIndexPanel:
    return DashboardEncryptedIndexPanel(
        summary=(
            "Metadata-only encrypted index search is available; query text, token "
            "text, source refs, memory content, and key material stay hidden."
        ),
        key_plan_id=key_plan.plan_id,
        write_receipt_count=int(durable_receipt.durable_synthetic_memory_written),
        graph_receipt_count=1,
        search_result_count=durable_receipt.search_receipt.result_count,
        candidate_open_count=durable_receipt.search_receipt.candidate_open_count,
        token_digest_count=durable_receipt.index_write_receipt.token_digest_count,
        graph_token_digest_count=durable_receipt.graph_write_receipt.graph_token_digest_count,
        source_ref_count=durable_receipt.index_write_receipt.source_ref_count,
        gateway_tools=["memory.search_index", "memory.get_context_pack"],
    )


def build_dashboard_live_backbone_panel(
    *,
    key_plan: KeyManagementPlan,
    encrypted_index_panel: DashboardEncryptedIndexPanel,
    native_feed: NativeShadowPointerLiveFeedReceipt,
    durable_receipt: DurableSyntheticMemoryReceipt,
) -> DashboardLiveBackbonePanel:
    return DashboardLiveBackbonePanel(
        summary=(
            "Key lifecycle, encrypted index receipts, native overlay feed, and "
            "synthetic durable writes are wired as redacted receipts."
        ),
        key_plan_id=key_plan.plan_id,
        encrypted_index_panel_id=encrypted_index_panel.panel_id,
        native_feed_id=native_feed.feed_id,
        durable_receipt_id=durable_receipt.receipt_id,
        ready_components=[
            "key_management_plan",
            "encrypted_index_panel",
            "native_live_feed",
            "durable_synthetic_receipt",
        ],
        blocked_effects=[
            "real_screen_capture",
            "durable_private_memory_write",
            "raw_ref_retention",
            "external_effect",
        ],
    )


def build_dashboard_operational_backbone(
    *, now: datetime | None = None
) -> DashboardOperationalBackbone:
    timestamp = _ensure_utc(now or datetime.now(UTC))
    key_plan = build_default_key_management_plan()
    durable_receipt = run_durable_synthetic_memory_receipts(now=timestamp)
    live_receipt = build_live_receipt(
        default_shadow_pointer_snapshot(),
        observation_mode=ShadowPointerObservationMode.SESSION,
        source_trust=SourceTrust.EXTERNAL_UNTRUSTED,
        firewall_decision="ephemeral_only",
        evidence_write_mode="derived_only",
        memory_eligible=False,
        raw_ref_retained=False,
        latest_action="Dashboard operational backbone",
    )
    native_feed = build_native_shadow_pointer_live_feed([live_receipt], now=timestamp)
    encrypted_panel = build_encrypted_index_dashboard_panel(durable_receipt, key_plan)
    backbone_panel = build_dashboard_live_backbone_panel(
        key_plan=key_plan,
        encrypted_index_panel=encrypted_panel,
        native_feed=native_feed,
        durable_receipt=durable_receipt,
    )
    return DashboardOperationalBackbone(
        key_management_plan=key_plan,
        encrypted_index_panel=encrypted_panel,
        native_live_feed=native_feed,
        durable_synthetic_memory_receipt=durable_receipt,
        live_backbone_panel=backbone_panel,
    )


def panel_payload_is_redacted(panel: DashboardOperationalBackbone) -> bool:
    payload = json.dumps(panel.model_dump(mode="json"), sort_keys=True)
    prohibited_markers = [
        "CORTEX_FAKE_TOKEN",
        "OPENAI_API_KEY=",
        "sk-",
        "Bearer ",
        "raw://",
        "encrypted_blob://",
        "Ignore previous instructions",
        "Synthetic durable memory receipt observed",
        "synthetic://durable-memory-receipt/source",
    ]
    return not any(marker in payload for marker in prohibited_markers)


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
