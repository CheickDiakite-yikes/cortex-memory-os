"""Live local-gateway receipts for dashboard read-only actions."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Literal

from pydantic import Field, model_validator

from cortex_memory_os.contracts import StrictModel
from cortex_memory_os.dashboard_gateway_actions import DashboardGatewayActionReceipt
from cortex_memory_os.mcp_server import CortexMCPServer, JsonRpcError
from cortex_memory_os.memory_palace import MemoryPalaceService
from cortex_memory_os.ops_quality import OpsQualitySummary, summarize_ops_quality_payload
from cortex_memory_os.sqlite_store import SQLiteMemoryGraphStore

DASHBOARD_GATEWAY_RUNTIME_READONLY_ID = "DASHBOARD-GATEWAY-RUNTIME-READONLY-001"
DASHBOARD_GATEWAY_RUNTIME_BLOCKLIST_ID = "DASHBOARD-GATEWAY-RUNTIME-BLOCKLIST-001"
DASHBOARD_CONTEXT_PACK_LIVE_SUMMARY_ID = "DASHBOARD-CONTEXT-PACK-LIVE-SUMMARY-001"
DASHBOARD_SKILL_REVIEW_LIVE_SUMMARY_ID = "DASHBOARD-SKILL-REVIEW-LIVE-SUMMARY-001"
DASHBOARD_OPS_QUALITY_PANEL_ID = "DASHBOARD-OPS-QUALITY-PANEL-001"

DASHBOARD_GATEWAY_RUNTIME_POLICY_REF = "policy_dashboard_gateway_runtime_readonly_v1"
DASHBOARD_CONTEXT_PACK_LIVE_SUMMARY_POLICY_REF = "policy_dashboard_context_pack_summary_v1"
DASHBOARD_SKILL_REVIEW_LIVE_SUMMARY_POLICY_REF = "policy_dashboard_skill_review_summary_v1"
DASHBOARD_OPS_QUALITY_PANEL_POLICY_REF = "policy_dashboard_ops_quality_panel_v1"

GatewayRuntimeStatus = Literal["executed_read_only", "blocked_before_gateway", "failed"]

_READ_ONLY_GATEWAY_TOOLS = {"memory.explain", "skill.review_candidate"}
_PROHIBITED_RESULT_MARKERS = [
    "OPENAI_API_KEY=",
    "CORTEX_FAKE_TOKEN",
    "sk-",
    "raw://",
    "encrypted_blob://",
    "Ignore previous instructions",
    "Search primary sources",
    "Gather approved metrics",
    "Reproduce the local login flow",
]


class DashboardGatewayRuntimeReceipt(StrictModel):
    receipt_id: str = Field(min_length=1)
    action_key: str = Field(min_length=1)
    gateway_tool: str = Field(min_length=1)
    target_ref: str = Field(min_length=1)
    status: GatewayRuntimeStatus
    gateway_called: bool
    mutation: bool = False
    data_egress: bool = False
    external_effect: bool = False
    result_kind: str = Field(min_length=1)
    result_summary: dict[str, int | str | bool] = Field(default_factory=dict)
    blocked_reasons: list[str] = Field(default_factory=list)
    error_type: str | None = None
    content_redacted: bool = True
    source_refs_redacted: bool = True
    procedure_redacted: bool = True
    raw_payload_returned: bool = False
    generated_at: datetime
    policy_refs: list[str] = Field(default_factory=lambda: [DASHBOARD_GATEWAY_RUNTIME_POLICY_REF])

    @model_validator(mode="after")
    def _validate_runtime_boundary(self) -> "DashboardGatewayRuntimeReceipt":
        if DASHBOARD_GATEWAY_RUNTIME_POLICY_REF not in self.policy_refs:
            raise ValueError("dashboard runtime receipt requires policy ref")
        if self.gateway_called:
            if self.gateway_tool not in _READ_ONLY_GATEWAY_TOOLS:
                raise ValueError("only read-only dashboard tools may reach gateway")
            if self.status not in {"executed_read_only", "failed"}:
                raise ValueError("called gateway receipts must execute read-only or fail closed")
            if (
                self.status == "executed_read_only"
                and (self.mutation or self.data_egress or self.external_effect)
            ):
                raise ValueError("called dashboard tools cannot mutate, export, or act externally")
        else:
            if self.status != "blocked_before_gateway":
                raise ValueError("uncalled dashboard receipts must be blocked before gateway")
            if not self.blocked_reasons:
                raise ValueError("blocked dashboard runtime receipts require reasons")
        if not self.content_redacted or not self.source_refs_redacted or not self.procedure_redacted:
            raise ValueError("dashboard runtime summaries must stay redacted")
        if self.raw_payload_returned:
            raise ValueError("dashboard runtime receipts cannot return raw payloads")
        serialized = json.dumps(self.result_summary, sort_keys=True)
        if any(marker in serialized for marker in _PROHIBITED_RESULT_MARKERS):
            raise ValueError("dashboard runtime summary contains prohibited marker")
        return self


class DashboardGatewayRuntimeBatch(StrictModel):
    batch_id: str = DASHBOARD_GATEWAY_RUNTIME_READONLY_ID
    generated_at: datetime
    receipts: list[DashboardGatewayRuntimeReceipt]
    executed_count: int = Field(ge=0)
    blocked_count: int = Field(ge=0)
    failed_count: int = Field(ge=0)
    mutation_count: int = Field(ge=0)
    data_egress_count: int = Field(ge=0)
    external_effect_count: int = Field(ge=0)
    raw_payload_count: int = Field(ge=0)
    content_redacted: bool = True
    policy_refs: list[str] = Field(default_factory=lambda: [DASHBOARD_GATEWAY_RUNTIME_POLICY_REF])


class DashboardContextPackLiveSummary(StrictModel):
    summary_id: str = DASHBOARD_CONTEXT_PACK_LIVE_SUMMARY_ID
    generated_at: datetime
    goal: str
    relevant_memory_count: int = Field(ge=0)
    retrieval_receipt_count: int = Field(ge=0)
    fusion_diagnostic_count: int = Field(ge=0)
    warning_count: int = Field(ge=0)
    blocked_memory_count: int = Field(ge=0)
    next_step_count: int = Field(ge=0)
    budget_estimated_prompt_tokens: int = Field(ge=0)
    content_redacted: bool = True
    source_refs_redacted: bool = True
    raw_payload_returned: bool = False
    policy_refs: list[str] = Field(default_factory=lambda: [DASHBOARD_CONTEXT_PACK_LIVE_SUMMARY_POLICY_REF])


class DashboardSkillReviewLiveSummary(StrictModel):
    summary_id: str = DASHBOARD_SKILL_REVIEW_LIVE_SUMMARY_ID
    generated_at: datetime
    skill_id: str = Field(min_length=1)
    risk_level: str = Field(min_length=1)
    maturity_level: int = Field(ge=0, le=5)
    execution_mode: str = Field(min_length=1)
    learned_from_count: int = Field(ge=0)
    trigger_count: int = Field(ge=0)
    procedure_step_count: int = Field(ge=0)
    success_signal_count: int = Field(ge=0)
    failure_mode_count: int = Field(ge=0)
    requires_confirmation_count: int = Field(ge=0)
    content_redacted: bool = True
    procedure_redacted: bool = True
    mutation: bool = False
    external_effect: bool = False
    policy_refs: list[str] = Field(default_factory=lambda: [DASHBOARD_SKILL_REVIEW_LIVE_SUMMARY_POLICY_REF])


class DashboardOpsQualityPanel(StrictModel):
    panel_id: str = DASHBOARD_OPS_QUALITY_PANEL_ID
    generated_at: datetime
    latest_run_id: str = Field(min_length=1)
    artifact_name: str = Field(min_length=1)
    total_cases: int = Field(ge=0)
    passed_cases: int = Field(ge=0)
    failed_cases: int = Field(ge=0)
    suite_count: int = Field(ge=0)
    all_passed: bool
    invalid_identifier_count: int = Field(ge=0)
    content_redacted: bool = True
    raw_case_payloads_included: bool = False
    artifact_payload_redacted: bool = True
    policy_refs: list[str] = Field(default_factory=lambda: [DASHBOARD_OPS_QUALITY_PANEL_POLICY_REF])


class DashboardLiveGatewayPanel(StrictModel):
    panel_id: str = "dashboard_live_gateway_panel_v1"
    generated_at: datetime
    runtime: DashboardGatewayRuntimeBatch
    context_pack: DashboardContextPackLiveSummary
    skill_reviews: list[DashboardSkillReviewLiveSummary]
    ops_quality: DashboardOpsQualityPanel
    content_redacted: bool = True
    raw_payload_returned: bool = False
    policy_refs: list[str]


def build_dashboard_gateway_runtime_server(
    *, now: datetime | None = None
) -> CortexMCPServer:
    from cortex_memory_os.dashboard_shell import _sample_memories, _sample_skills

    timestamp = _timestamp(now)
    tempdir = TemporaryDirectory()
    store = SQLiteMemoryGraphStore(Path(tempdir.name) / "cortex-dashboard.sqlite3")
    for memory in _sample_memories(timestamp):
        store.add_memory(memory)
    skills = {skill.skill_id: skill for skill in _sample_skills()}
    return CortexMCPServer(
        store=store,
        palace=MemoryPalaceService(store),
        skills=skills,
        _tempdir=tempdir,
    )


def execute_dashboard_gateway_receipts(
    *,
    gateway_action_receipts: list[DashboardGatewayActionReceipt] | None = None,
    server: CortexMCPServer | None = None,
    now: datetime | None = None,
) -> DashboardGatewayRuntimeBatch:
    if gateway_action_receipts is None:
        from cortex_memory_os.dashboard_shell import build_dashboard_shell

    timestamp = _timestamp(now)
    if gateway_action_receipts is None:
        gateway_action_receipts = build_dashboard_shell(
            now=timestamp
        ).gateway_action_receipts
    server = server or build_dashboard_gateway_runtime_server(now=timestamp)
    receipts = [
        _execute_receipt(receipt, server=server, now=timestamp)
        for receipt in gateway_action_receipts
    ]
    return DashboardGatewayRuntimeBatch(
        generated_at=timestamp,
        receipts=receipts,
        executed_count=sum(1 for receipt in receipts if receipt.status == "executed_read_only"),
        blocked_count=sum(1 for receipt in receipts if receipt.status == "blocked_before_gateway"),
        failed_count=sum(1 for receipt in receipts if receipt.status == "failed"),
        mutation_count=sum(int(receipt.mutation) for receipt in receipts),
        data_egress_count=sum(int(receipt.data_egress) for receipt in receipts),
        external_effect_count=sum(int(receipt.external_effect) for receipt in receipts),
        raw_payload_count=sum(int(receipt.raw_payload_returned) for receipt in receipts),
    )


def build_context_pack_live_summary(
    *,
    server: CortexMCPServer | None = None,
    goal: str = "primary source research synthesis",
    now: datetime | None = None,
) -> DashboardContextPackLiveSummary:
    timestamp = _timestamp(now)
    server = server or build_dashboard_gateway_runtime_server(now=timestamp)
    pack = server.get_context_pack(
        {
            "goal": goal,
            "active_project": "cortex-memory-os",
            "limit": 3,
        }
    )
    return DashboardContextPackLiveSummary(
        generated_at=timestamp,
        goal=goal,
        relevant_memory_count=len(pack.relevant_memories),
        retrieval_receipt_count=len(pack.retrieval_explanation_receipts),
        fusion_diagnostic_count=len(pack.hybrid_fusion_diagnostics),
        warning_count=len(pack.warnings),
        blocked_memory_count=len(pack.blocked_memory_ids),
        next_step_count=len(pack.recommended_next_steps),
        budget_estimated_prompt_tokens=pack.budget.estimated_prompt_tokens,
    )


def build_skill_review_live_summaries(
    *,
    server: CortexMCPServer | None = None,
    now: datetime | None = None,
) -> list[DashboardSkillReviewLiveSummary]:
    timestamp = _timestamp(now)
    server = server or build_dashboard_gateway_runtime_server(now=timestamp)
    summaries: list[DashboardSkillReviewLiveSummary] = []
    for skill_id in sorted(server.skills):
        response = server.call_tool("skill.review_candidate", {"skill_id": skill_id})
        review = response["review"]
        summaries.append(
            DashboardSkillReviewLiveSummary(
                generated_at=timestamp,
                skill_id=review["skill_id"],
                risk_level=review["risk_level"],
                maturity_level=review["maturity_level"],
                execution_mode=review["execution_mode"],
                learned_from_count=review["learned_from_count"],
                trigger_count=review["trigger_count"],
                procedure_step_count=review["procedure_step_count"],
                success_signal_count=review["success_signal_count"],
                failure_mode_count=review["failure_mode_count"],
                requires_confirmation_count=review["requires_confirmation_count"],
            )
        )
    return summaries


def build_ops_quality_panel(
    summary: OpsQualitySummary | None = None,
    *,
    now: datetime | None = None,
) -> DashboardOpsQualityPanel:
    timestamp = _timestamp(now)
    summary = summary or _sample_ops_quality_summary(now=timestamp)
    return DashboardOpsQualityPanel(
        generated_at=timestamp,
        latest_run_id=summary.latest_run_id,
        artifact_name=summary.artifact_name,
        total_cases=summary.total_cases,
        passed_cases=summary.passed_cases,
        failed_cases=summary.failed_cases,
        suite_count=summary.suite_count,
        all_passed=summary.all_passed,
        invalid_identifier_count=summary.invalid_identifier_count,
    )


def build_dashboard_live_gateway_panel(
    *,
    gateway_action_receipts: list[DashboardGatewayActionReceipt] | None = None,
    now: datetime | None = None,
) -> DashboardLiveGatewayPanel:
    timestamp = _timestamp(now)
    server = build_dashboard_gateway_runtime_server(now=timestamp)
    runtime = execute_dashboard_gateway_receipts(
        gateway_action_receipts=gateway_action_receipts,
        server=server,
        now=timestamp,
    )
    context_pack = build_context_pack_live_summary(server=server, now=timestamp)
    skill_reviews = build_skill_review_live_summaries(server=server, now=timestamp)
    return DashboardLiveGatewayPanel(
        generated_at=timestamp,
        runtime=runtime,
        context_pack=context_pack,
        skill_reviews=skill_reviews,
        ops_quality=build_ops_quality_panel(now=timestamp),
        policy_refs=[
            DASHBOARD_GATEWAY_RUNTIME_POLICY_REF,
            DASHBOARD_CONTEXT_PACK_LIVE_SUMMARY_POLICY_REF,
            DASHBOARD_SKILL_REVIEW_LIVE_SUMMARY_POLICY_REF,
            DASHBOARD_OPS_QUALITY_PANEL_POLICY_REF,
        ],
    )


def _execute_receipt(
    receipt: DashboardGatewayActionReceipt,
    *,
    server: CortexMCPServer,
    now: datetime,
) -> DashboardGatewayRuntimeReceipt:
    if not receipt.allowed_gateway_call:
        return DashboardGatewayRuntimeReceipt(
            receipt_id=f"runtime_{receipt.receipt_id}",
            action_key=receipt.action_key,
            gateway_tool=receipt.gateway_tool,
            target_ref=receipt.target_ref,
            status="blocked_before_gateway",
            gateway_called=False,
            mutation=receipt.mutation,
            data_egress=receipt.data_egress,
            external_effect=receipt.external_effect,
            result_kind="blocked_preview",
            result_summary={"blocked_reason_count": len(receipt.blocked_reasons)},
            blocked_reasons=receipt.blocked_reasons,
            generated_at=now,
        )

    try:
        response = server.call_tool(receipt.gateway_tool, _gateway_arguments(receipt))
    except JsonRpcError as error:
        return DashboardGatewayRuntimeReceipt(
            receipt_id=f"runtime_{receipt.receipt_id}",
            action_key=receipt.action_key,
            gateway_tool=receipt.gateway_tool,
            target_ref=receipt.target_ref,
            status="failed",
            gateway_called=True,
            result_kind="gateway_error",
            result_summary={"error_code": error.code},
            error_type=type(error).__name__,
            generated_at=now,
        )

    return DashboardGatewayRuntimeReceipt(
        receipt_id=f"runtime_{receipt.receipt_id}",
        action_key=receipt.action_key,
        gateway_tool=receipt.gateway_tool,
        target_ref=receipt.target_ref,
        status="executed_read_only",
        gateway_called=True,
        result_kind=_result_kind(receipt.gateway_tool),
        result_summary=_summarize_gateway_response(receipt.gateway_tool, response),
        generated_at=now,
    )


def _gateway_arguments(receipt: DashboardGatewayActionReceipt) -> dict[str, str]:
    if receipt.gateway_tool == "memory.explain":
        return {"memory_id": receipt.target_ref}
    if receipt.gateway_tool == "skill.review_candidate":
        return {"skill_id": receipt.target_ref}
    raise JsonRpcError(-32601, f"dashboard tool is not read-only callable: {receipt.gateway_tool}")


def _result_kind(gateway_tool: str) -> str:
    return {
        "memory.explain": "memory_explanation_summary",
        "skill.review_candidate": "skill_candidate_review_summary",
    }.get(gateway_tool, "unknown_summary")


def _summarize_gateway_response(
    gateway_tool: str,
    response: dict[str, Any],
) -> dict[str, int | str | bool]:
    if gateway_tool == "memory.explain":
        return {
            "source_ref_count": len(response.get("source_refs", [])),
            "allowed_influence_count": len(response.get("allowed_influence", [])),
            "forbidden_influence_count": len(response.get("forbidden_influence", [])),
            "available_action_count": len(response.get("available_actions", [])),
            "recall_eligible": bool(response.get("recall_eligible")),
            "status": str(response.get("status", "")),
        }
    if gateway_tool == "skill.review_candidate":
        review = response.get("review", {})
        return {
            "learned_from_count": int(review.get("learned_from_count", 0)),
            "trigger_count": int(review.get("trigger_count", 0)),
            "procedure_step_count": int(review.get("procedure_step_count", 0)),
            "requires_confirmation_count": int(review.get("requires_confirmation_count", 0)),
            "maturity_level": int(review.get("maturity_level", 0)),
            "risk_level": str(review.get("risk_level", "")),
        }
    return {}


def _sample_ops_quality_summary(*, now: datetime) -> OpsQualitySummary:
    return summarize_ops_quality_payload(
        {
            "run_id": "bench_20260501T010628Z",
            "created_at": "2026-05-01T01:06:28.218808Z",
            "case_results": [
                {
                    "case_id": "COMPUTER-DASHBOARD-LIVE-PROOF-001/sample",
                    "suite": "COMPUTER-DASHBOARD-LIVE-PROOF-001",
                    "passed": True,
                },
                {
                    "case_id": "DASHBOARD-GATEWAY-RUNTIME-READONLY-001/sample",
                    "suite": "DASHBOARD-GATEWAY-RUNTIME-READONLY-001",
                    "passed": True,
                },
            ],
        },
        artifact_name="bench_20260501T010628Z.json",
        now=now,
    )


def _timestamp(now: datetime | None) -> datetime:
    timestamp = now or datetime.now(UTC)
    if timestamp.tzinfo is None:
        return timestamp.replace(tzinfo=UTC)
    return timestamp.astimezone(UTC)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    panel = build_dashboard_live_gateway_panel()
    if args.json:
        print(json.dumps(panel.model_dump(mode="json"), indent=2, sort_keys=True))
    else:
        print(
            "dashboard live gateway panel: "
            f"{panel.runtime.executed_count} executed, {panel.runtime.blocked_count} blocked"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
