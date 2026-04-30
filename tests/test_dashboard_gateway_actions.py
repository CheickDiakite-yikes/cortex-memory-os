from datetime import UTC, datetime

from cortex_memory_os.dashboard_gateway_actions import (
    DASHBOARD_GATEWAY_ACTIONS_POLICY_REF,
    build_dashboard_gateway_action_receipts,
)
from cortex_memory_os.dashboard_shell import build_dashboard_shell, run_dashboard_shell_smoke


def test_dashboard_gateway_receipts_allow_only_read_only_tools():
    shell = build_dashboard_shell(now=datetime(2026, 4, 30, 11, 0, tzinfo=UTC))
    receipts = build_dashboard_gateway_action_receipts(
        shell.memory_palace,
        shell.skill_forge,
        now=shell.generated_at,
    )

    allowed = [receipt for receipt in receipts if receipt.allowed_gateway_call]
    blocked = [receipt for receipt in receipts if not receipt.allowed_gateway_call]

    assert allowed
    assert blocked
    assert {receipt.gateway_tool for receipt in allowed} == {
        "memory.explain",
        "skill.review_candidate",
    }
    assert all(receipt.read_only for receipt in allowed)
    assert all(not receipt.mutation for receipt in allowed)
    assert all(not receipt.data_egress for receipt in allowed)
    assert all(DASHBOARD_GATEWAY_ACTIONS_POLICY_REF in receipt.policy_refs for receipt in receipts)


def test_dashboard_gateway_receipts_block_mutations_exports_and_drafts():
    shell = build_dashboard_shell(now=datetime(2026, 4, 30, 11, 0, tzinfo=UTC))

    by_tool = {
        (receipt.gateway_tool, receipt.target_ref): receipt
        for receipt in shell.gateway_action_receipts
    }

    assert by_tool[("memory.forget", "mem_smallest_safe_change")].allowed_gateway_call is False
    assert "mutation_blocked" in by_tool[("memory.forget", "mem_smallest_safe_change")].blocked_reasons
    assert by_tool[("memory.export", "mem_smallest_safe_change")].allowed_gateway_call is False
    assert "data_egress_blocked" in by_tool[("memory.export", "mem_smallest_safe_change")].blocked_reasons
    assert (
        by_tool[("skill.execute_draft", "skill_frontend_auth_debugging_flow_v1")]
        .allowed_gateway_call
        is False
    )
    assert "tool_not_enabled_for_read_only_dashboard_slice" in (
        by_tool[("skill.execute_draft", "skill_frontend_auth_debugging_flow_v1")]
        .blocked_reasons
    )


def test_dashboard_gateway_payload_previews_are_redacted_and_ref_only():
    shell = build_dashboard_shell(now=datetime(2026, 4, 30, 11, 0, tzinfo=UTC))
    serialized = "\n".join(
        receipt.model_dump_json() for receipt in shell.gateway_action_receipts
    )
    explain = next(
        receipt
        for receipt in shell.gateway_action_receipts
        if receipt.gateway_tool == "memory.explain"
    )

    assert explain.payload_preview["memory_id_or_visible_card_anchor"] == explain.target_ref
    assert "CORTEX_FAKE_TOKEN" not in serialized
    assert "raw://" not in serialized
    assert "encrypted_blob://" not in serialized
    assert all(receipt.content_redacted for receipt in shell.gateway_action_receipts)


def test_dashboard_shell_smoke_counts_gateway_receipts():
    result = run_dashboard_shell_smoke()

    assert result.passed
    assert result.gateway_actions_present is True
    assert result.gateway_action_receipt_count > 0
    assert result.read_only_gateway_action_count > 0
    assert result.blocked_gateway_action_count > 0
