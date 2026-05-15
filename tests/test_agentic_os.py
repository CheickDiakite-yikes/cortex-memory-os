import pytest

from cortex_memory_os.agentic_os import (
    AGENTIC_OS_PLANNER_ID,
    AGENTIC_OS_POLICY_REF,
    AI_POINTER_PRINCIPLES,
    AgenticOSPlan,
    build_agentic_os_dashboard_panel,
    build_agentic_os_plan,
    main,
    run_agentic_os_smoke,
)
from cortex_memory_os.contracts import ActionRisk, ExecutionMode


def test_agentic_os_plan_preserves_pointer_first_os_boundaries():
    plan = build_agentic_os_plan()
    payload = plan.model_dump_json()

    assert plan.plan_id == AGENTIC_OS_PLANNER_ID
    assert plan.policy_ref == AGENTIC_OS_POLICY_REF
    assert set(plan.principles) == set(AI_POINTER_PRINCIPLES)
    assert len(plan.routes) >= 5
    assert len(plan.steps) >= 6
    assert plan.display_only_pointer is True
    assert plan.real_screen_capture_started is False
    assert plan.voice_capture_started is False
    assert plan.memory_write_allowed is False
    assert plan.raw_ref_retained is False
    assert plan.external_effect_enabled is False
    assert plan.content_redacted is True
    assert plan.source_refs_redacted is True
    assert "execute_click" in plan.blocked_effects
    assert "write_memory_without_review" in plan.blocked_effects
    assert "store_raw_evidence" in plan.blocked_effects
    assert "raw://" not in payload
    assert "encrypted_blob://" not in payload
    assert "OPENAI_API_KEY" not in payload
    assert "sk-" not in payload


def test_agentic_os_routes_require_confirmation_before_effectful_work():
    plan = build_agentic_os_plan()

    medium_routes = [route for route in plan.routes if route.risk_level == ActionRisk.MEDIUM]
    assert medium_routes
    assert all(route.requires_confirmation for route in medium_routes)
    assert all(
        route.execution_mode in {ExecutionMode.DRAFT_ONLY, ExecutionMode.ASSISTIVE}
        for route in plan.routes
    )
    assert all(not route.external_effect for route in plan.routes)
    assert any(route.gateway_tool == "memory.get_context_pack" for route in plan.routes)
    assert any(route.gateway_tool == "runtime_trace.record" for route in plan.routes)
    assert any(route.gateway_tool == "skill.execute_draft" for route in plan.routes)


def test_agentic_os_plan_rejects_unsafe_or_unredacted_variants():
    plan = build_agentic_os_plan()

    with pytest.raises(ValueError, match="display-only"):
        AgenticOSPlan.model_validate(
            plan.model_dump() | {"display_only_pointer": False}
        )

    with pytest.raises(ValueError, match="capture"):
        AgenticOSPlan.model_validate(
            plan.model_dump() | {"real_screen_capture_started": True}
        )

    with pytest.raises(ValueError, match="redacted"):
        AgenticOSPlan.model_validate(plan.model_dump() | {"content_redacted": False})

    bad_route_payload = plan.routes[0].model_dump() | {
        "gateway_tool": "browser.click",
        "risk_level": ActionRisk.MEDIUM,
        "requires_confirmation": False,
    }
    with pytest.raises(ValueError, match="medium-risk"):
        type(plan.routes[0]).model_validate(bad_route_payload)


def test_agentic_os_smoke_and_cli(capsys):
    result = run_agentic_os_smoke()

    assert result.passed
    assert result.route_count >= 5
    assert result.step_count >= 6
    assert result.confirmation_gate_count >= 2
    assert result.blocked_effect_count >= 8

    assert main(["--smoke", "--json"]) == 0
    output = capsys.readouterr().out
    assert AGENTIC_OS_PLANNER_ID in output
    assert AGENTIC_OS_POLICY_REF in output
    assert "write_memory_without_review" in output


def test_agentic_os_dashboard_panel_is_simple_and_safe():
    panel = build_agentic_os_dashboard_panel()

    assert panel.panel_id == AGENTIC_OS_PLANNER_ID
    assert panel.route_count >= 5
    assert panel.step_count >= 6
    assert panel.confirmation_gate_count >= 2
    assert "Goal -> pointer context" in panel.summary
    assert "memory.get_context_pack" in panel.ready_routes
    assert "runtime_trace.record" in panel.ready_routes
    assert "Ask before doing anything with effects" in panel.review_steps
    assert panel.display_only_pointer is True
    assert panel.memory_write_allowed is False
    assert panel.external_effect_enabled is False
    assert panel.raw_ref_retained is False
    assert panel.content_redacted is True
    assert panel.source_refs_redacted is True
    assert "execute_click" in panel.blocked_effects
    assert panel.smoke_command == "uv run cortex-agentic-os --smoke --json"


def test_agentic_os_plan_rejects_high_risk_routes():
    plan = build_agentic_os_plan()

    with pytest.raises(ValueError, match="high and critical"):
        type(plan.routes[0]).model_validate(
            plan.routes[0].model_dump() | {"risk_level": ActionRisk.HIGH}
        )

    with pytest.raises(ValueError, match="draft/assistive"):
        type(plan.routes[0]).model_validate(
            plan.routes[0].model_dump()
            | {"execution_mode": ExecutionMode.BOUNDED_AUTONOMY}
        )
