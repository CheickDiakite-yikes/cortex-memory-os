from datetime import UTC, datetime

from cortex_memory_os.dashboard_live_gateway import (
    DASHBOARD_CONTEXT_PACK_LIVE_SUMMARY_ID,
    DASHBOARD_GATEWAY_RUNTIME_BLOCKLIST_ID,
    DASHBOARD_GATEWAY_RUNTIME_READONLY_ID,
    DASHBOARD_OPS_QUALITY_PANEL_ID,
    DASHBOARD_SKILL_REVIEW_LIVE_SUMMARY_ID,
    build_context_pack_live_summary,
    build_dashboard_gateway_runtime_server,
    build_dashboard_live_gateway_panel,
    build_ops_quality_panel,
    build_skill_review_live_summaries,
    execute_dashboard_gateway_receipts,
)
from cortex_memory_os.ops_quality import summarize_ops_quality_payload


NOW = datetime(2026, 5, 1, 9, 30, tzinfo=UTC)


def test_dashboard_gateway_runtime_executes_only_read_only_receipts():
    batch = execute_dashboard_gateway_receipts(now=NOW)
    executed = [receipt for receipt in batch.receipts if receipt.gateway_called]

    assert batch.batch_id == DASHBOARD_GATEWAY_RUNTIME_READONLY_ID
    assert batch.executed_count > 0
    assert {receipt.gateway_tool for receipt in executed} == {
        "memory.explain",
        "skill.review_candidate",
    }
    assert all(receipt.status == "executed_read_only" for receipt in executed)
    assert all(receipt.content_redacted for receipt in executed)
    assert all(receipt.source_refs_redacted for receipt in executed)
    assert all(receipt.procedure_redacted for receipt in executed)
    assert batch.failed_count == 0
    assert batch.raw_payload_count == 0


def test_dashboard_gateway_runtime_blocks_mutation_export_and_draft_before_gateway():
    batch = execute_dashboard_gateway_receipts(now=NOW)
    blocked = [receipt for receipt in batch.receipts if not receipt.gateway_called]
    blocked_tools = {receipt.gateway_tool for receipt in blocked}

    assert DASHBOARD_GATEWAY_RUNTIME_BLOCKLIST_ID
    assert batch.blocked_count > 0
    assert "memory.forget" in blocked_tools
    assert "memory.export" in blocked_tools
    assert "skill.execute_draft" in blocked_tools
    assert all(receipt.status == "blocked_before_gateway" for receipt in blocked)
    assert all(receipt.blocked_reasons for receipt in blocked)
    assert all(not receipt.raw_payload_returned for receipt in blocked)
    assert batch.mutation_count > 0
    assert batch.data_egress_count > 0
    assert batch.external_effect_count == 0


def test_dashboard_context_pack_live_summary_is_count_only_and_redacted():
    summary = build_context_pack_live_summary(now=NOW)
    serialized = summary.model_dump_json()

    assert summary.summary_id == DASHBOARD_CONTEXT_PACK_LIVE_SUMMARY_ID
    assert summary.relevant_memory_count > 0
    assert summary.retrieval_receipt_count > 0
    assert summary.fusion_diagnostic_count > 0
    assert summary.warning_count > 0
    assert summary.content_redacted is True
    assert summary.source_refs_redacted is True
    assert summary.raw_payload_returned is False
    assert "User consistently asks" not in serialized
    assert "project:cortex-memory-os" not in serialized


def test_dashboard_skill_review_live_summary_is_procedure_redacted():
    summaries = build_skill_review_live_summaries(now=NOW)
    serialized = "\n".join(summary.model_dump_json() for summary in summaries)

    assert summaries
    assert {summary.summary_id for summary in summaries} == {
        DASHBOARD_SKILL_REVIEW_LIVE_SUMMARY_ID
    }
    assert any(summary.skill_id == "skill_frontend_auth_debugging_flow_v1" for summary in summaries)
    assert all(summary.procedure_step_count > 0 for summary in summaries)
    assert all(summary.content_redacted for summary in summaries)
    assert all(summary.procedure_redacted for summary in summaries)
    assert all(not summary.mutation for summary in summaries)
    assert all(not summary.external_effect for summary in summaries)
    assert "Reproduce the local login flow" not in serialized
    assert "Gather approved metrics" not in serialized


def test_dashboard_ops_quality_panel_is_aggregate_only():
    ops_summary = summarize_ops_quality_payload(
        {
            "run_id": "bench_20260501T010628Z",
            "created_at": "2026-05-01T01:06:28.218808Z",
            "case_results": [
                {
                    "case_id": "DASHBOARD-GATEWAY-RUNTIME-READONLY-001/sample",
                    "suite": "DASHBOARD-GATEWAY-RUNTIME-READONLY-001",
                    "passed": True,
                    "summary": "raw details should not copy",
                }
            ],
        },
        artifact_name="bench_20260501T010628Z.json",
        now=NOW,
    )

    panel = build_ops_quality_panel(ops_summary, now=NOW)
    serialized = panel.model_dump_json()

    assert panel.panel_id == DASHBOARD_OPS_QUALITY_PANEL_ID
    assert panel.total_cases == 1
    assert panel.passed_cases == 1
    assert panel.failed_cases == 0
    assert panel.raw_case_payloads_included is False
    assert panel.artifact_payload_redacted is True
    assert "raw details should not copy" not in serialized


def test_dashboard_live_gateway_panel_composes_all_summaries():
    panel = build_dashboard_live_gateway_panel(now=NOW)

    assert panel.runtime.executed_count > 0
    assert panel.runtime.blocked_count > 0
    assert panel.context_pack.relevant_memory_count > 0
    assert panel.skill_reviews
    assert panel.ops_quality.all_passed
    assert panel.content_redacted is True
    assert panel.raw_payload_returned is False


def test_dashboard_runtime_server_exposes_dashboard_fixture_ids():
    server = build_dashboard_gateway_runtime_server(now=NOW)

    memory_response = server.call_tool(
        "memory.explain",
        {"memory_id": "mem_smallest_safe_change"},
    )
    skill_response = server.call_tool(
        "skill.review_candidate",
        {"skill_id": "skill_research_synthesis_blueprint_v1"},
    )

    assert memory_response["memory_id"] == "mem_smallest_safe_change"
    assert skill_response["review"]["skill_id"] == "skill_research_synthesis_blueprint_v1"
    assert skill_response["procedure_redacted"] is True
