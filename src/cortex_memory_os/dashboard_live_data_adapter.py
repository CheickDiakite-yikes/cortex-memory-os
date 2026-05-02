"""Read-only live data adapter for the Cortex dashboard."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import Field, model_validator

from cortex_memory_os.contracts import StrictModel
from cortex_memory_os.dashboard_encrypted_index import (
    DashboardOperationalBackbone,
    ENCRYPTED_INDEX_DASHBOARD_LIVE_POLICY_REF,
)
from cortex_memory_os.dashboard_live_gateway import (
    DASHBOARD_CONTEXT_PACK_LIVE_SUMMARY_POLICY_REF,
    DASHBOARD_GATEWAY_RUNTIME_POLICY_REF,
    DASHBOARD_OPS_QUALITY_PANEL_POLICY_REF,
    DASHBOARD_SKILL_REVIEW_LIVE_SUMMARY_POLICY_REF,
    DashboardLiveGatewayPanel,
)
from cortex_memory_os.retrieval_receipts_dashboard import (
    RETRIEVAL_RECEIPTS_DASHBOARD_POLICY_REF,
    RetrievalReceiptsDashboard,
)
from cortex_memory_os.skill_metrics_dashboard import (
    SKILL_METRICS_DASHBOARD_POLICY_REF,
    SkillMetricsDashboard,
)

DASHBOARD_LIVE_DATA_ADAPTER_ID = "DASHBOARD-LIVE-DATA-ADAPTER-001"
DASHBOARD_LIVE_DATA_ADAPTER_POLICY_REF = "policy_dashboard_live_data_adapter_v1"
LIVE_DASHBOARD_RECEIPTS_ID = "LIVE-DASHBOARD-RECEIPTS-001"
LIVE_DASHBOARD_RECEIPTS_POLICY_REF = "policy_live_dashboard_receipts_v1"


class DashboardLiveDataAdapterSnapshot(StrictModel):
    snapshot_id: str = DASHBOARD_LIVE_DATA_ADAPTER_ID
    generated_at: datetime
    adapter_sources: list[str] = Field(min_length=4)
    read_only: bool = True
    local_only: bool = True
    gateway_executed_count: int = Field(ge=0)
    gateway_blocked_count: int = Field(ge=0)
    context_pack_memory_count: int = Field(ge=0)
    context_pack_warning_count: int = Field(ge=0)
    skill_review_count: int = Field(ge=0)
    skill_metric_run_count: int = Field(ge=0)
    retrieval_receipt_count: int = Field(ge=0)
    encrypted_index_search_result_count: int = Field(ge=0)
    encrypted_index_candidate_open_count: int = Field(ge=0)
    ops_total_cases: int = Field(ge=0)
    ops_passed_cases: int = Field(ge=0)
    native_receipt_count: int = Field(ge=0)
    durable_synthetic_write_count: int = Field(ge=0)
    write_path_enabled: bool = False
    mutation_enabled: bool = False
    raw_payload_returned: bool = False
    raw_ref_retained: bool = False
    content_redacted: bool = True
    source_refs_redacted: bool = True
    policy_refs: list[str] = Field(
        default_factory=lambda: [
            DASHBOARD_LIVE_DATA_ADAPTER_POLICY_REF,
            DASHBOARD_GATEWAY_RUNTIME_POLICY_REF,
            DASHBOARD_CONTEXT_PACK_LIVE_SUMMARY_POLICY_REF,
            DASHBOARD_SKILL_REVIEW_LIVE_SUMMARY_POLICY_REF,
            DASHBOARD_OPS_QUALITY_PANEL_POLICY_REF,
            ENCRYPTED_INDEX_DASHBOARD_LIVE_POLICY_REF,
            SKILL_METRICS_DASHBOARD_POLICY_REF,
            RETRIEVAL_RECEIPTS_DASHBOARD_POLICY_REF,
        ]
    )

    @model_validator(mode="after")
    def keep_adapter_read_only(self) -> "DashboardLiveDataAdapterSnapshot":
        if DASHBOARD_LIVE_DATA_ADAPTER_POLICY_REF not in self.policy_refs:
            raise ValueError("dashboard live data adapter requires policy ref")
        if not self.read_only or not self.local_only:
            raise ValueError("dashboard live data adapter must stay read-only and local")
        if self.write_path_enabled or self.mutation_enabled:
            raise ValueError("dashboard live data adapter cannot enable writes or mutations")
        if self.raw_payload_returned or self.raw_ref_retained:
            raise ValueError("dashboard live data adapter cannot return raw payloads or refs")
        if not self.content_redacted or not self.source_refs_redacted:
            raise ValueError("dashboard live data adapter must return redacted summaries")
        required_sources = {
            "dashboard_gateway_runtime",
            "context_pack_gateway",
            "skill_review_gateway",
            "ops_quality_reader",
            "encrypted_index_receipts",
            "native_shadow_pointer_feed",
        }
        if missing := sorted(required_sources.difference(self.adapter_sources)):
            raise ValueError(f"dashboard live data adapter missing sources: {missing}")
        return self


class LiveDashboardReceiptsPanel(StrictModel):
    panel_id: str = LIVE_DASHBOARD_RECEIPTS_ID
    title: str = "Live Safe Receipts"
    generated_at: datetime
    summary: str = Field(min_length=1)
    gateway_executed_count: int = Field(ge=0)
    gateway_blocked_count: int = Field(ge=0)
    retrieval_receipt_count: int = Field(ge=0)
    encrypted_index_search_result_count: int = Field(ge=0)
    ops_passed_cases: int = Field(ge=0)
    skill_metric_run_count: int = Field(ge=0)
    refresh_sources: list[str] = Field(min_length=4)
    refresh_mode: str = "read_only_receipts"
    content_redacted: bool = True
    source_refs_redacted: bool = True
    raw_payload_returned: bool = False
    mutation_enabled: bool = False
    policy_refs: list[str] = Field(
        default_factory=lambda: [
            LIVE_DASHBOARD_RECEIPTS_POLICY_REF,
            DASHBOARD_LIVE_DATA_ADAPTER_POLICY_REF,
        ]
    )

    @model_validator(mode="after")
    def keep_panel_refresh_safe(self) -> "LiveDashboardReceiptsPanel":
        if LIVE_DASHBOARD_RECEIPTS_POLICY_REF not in self.policy_refs:
            raise ValueError("live dashboard receipts panel requires policy ref")
        if self.refresh_mode != "read_only_receipts":
            raise ValueError("live dashboard receipts panel cannot use write refresh mode")
        if not self.content_redacted or not self.source_refs_redacted:
            raise ValueError("live dashboard receipts panel must stay redacted")
        if self.raw_payload_returned or self.mutation_enabled:
            raise ValueError("live dashboard receipts panel cannot return raw payloads or mutate")
        return self


def build_dashboard_live_data_adapter_snapshot(
    *,
    live_gateway_panel: DashboardLiveGatewayPanel,
    operational_backbone: DashboardOperationalBackbone,
    skill_metrics: SkillMetricsDashboard,
    retrieval_debug: RetrievalReceiptsDashboard,
    now: datetime | None = None,
) -> DashboardLiveDataAdapterSnapshot:
    timestamp = _timestamp(now)
    return DashboardLiveDataAdapterSnapshot(
        generated_at=timestamp,
        adapter_sources=[
            "dashboard_gateway_runtime",
            "context_pack_gateway",
            "skill_review_gateway",
            "ops_quality_reader",
            "encrypted_index_receipts",
            "native_shadow_pointer_feed",
            "durable_synthetic_receipts",
            "skill_metrics_reader",
            "retrieval_receipts_reader",
        ],
        gateway_executed_count=live_gateway_panel.runtime.executed_count,
        gateway_blocked_count=live_gateway_panel.runtime.blocked_count,
        context_pack_memory_count=live_gateway_panel.context_pack.relevant_memory_count,
        context_pack_warning_count=live_gateway_panel.context_pack.warning_count,
        skill_review_count=len(live_gateway_panel.skill_reviews),
        skill_metric_run_count=skill_metrics.total_run_count,
        retrieval_receipt_count=retrieval_debug.receipt_count,
        encrypted_index_search_result_count=(
            operational_backbone.encrypted_index_panel.search_result_count
        ),
        encrypted_index_candidate_open_count=(
            operational_backbone.encrypted_index_panel.candidate_open_count
        ),
        ops_total_cases=live_gateway_panel.ops_quality.total_cases,
        ops_passed_cases=live_gateway_panel.ops_quality.passed_cases,
        native_receipt_count=operational_backbone.native_live_feed.receipt_count,
        durable_synthetic_write_count=int(
            operational_backbone.durable_synthetic_memory_receipt.durable_synthetic_memory_written
        ),
    )


def build_live_dashboard_receipts_panel(
    snapshot: DashboardLiveDataAdapterSnapshot,
) -> LiveDashboardReceiptsPanel:
    return LiveDashboardReceiptsPanel(
        generated_at=snapshot.generated_at,
        summary=(
            "Retrieval, encrypted index, ops quality, skill metrics, and gateway "
            "receipts refresh from local read-only adapters."
        ),
        gateway_executed_count=snapshot.gateway_executed_count,
        gateway_blocked_count=snapshot.gateway_blocked_count,
        retrieval_receipt_count=snapshot.retrieval_receipt_count,
        encrypted_index_search_result_count=snapshot.encrypted_index_search_result_count,
        ops_passed_cases=snapshot.ops_passed_cases,
        skill_metric_run_count=snapshot.skill_metric_run_count,
        refresh_sources=[
            "gateway_runtime",
            "retrieval_receipts",
            "encrypted_index",
            "ops_quality",
            "skill_metrics",
        ],
    )


def _timestamp(now: datetime | None) -> datetime:
    timestamp = now or datetime.now(UTC)
    if timestamp.tzinfo is None:
        return timestamp.replace(tzinfo=UTC)
    return timestamp.astimezone(UTC)
