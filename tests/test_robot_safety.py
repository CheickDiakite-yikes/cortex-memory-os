import pytest
from pydantic import ValidationError

from cortex_memory_os.contracts import ActionRisk
from cortex_memory_os.robot_safety import (
    ROBOT_SPATIAL_SAFETY_POLICY_REF,
    RobotHazardKind,
    RobotSimulationStatus,
    RobotSpatialSafetyEnvelope,
    evaluate_robot_spatial_safety,
)


def _envelope(**overrides):
    payload = {
        "action_id": "robot_action_pick_cup_001",
        "capability": "robot.arm.grasp.v1",
        "action_summary": "Pick up the empty cup from the marked test table.",
        "source_refs": ["scene_robot_lab_synthetic"],
        "workspace_bounds_ref": "workspace://lab/table-a/bounds-v1",
        "target_object_ref": "object://cup-empty-blue",
        "affordances": ["top_grasp", "stable_table_surface"],
        "material_constraints": ["ceramic", "do_not_squeeze"],
        "hazards": [],
        "bystander_present": False,
        "risk_level": ActionRisk.MEDIUM,
        "physical_effect": True,
        "simulation_status": RobotSimulationStatus.PASSED,
        "simulation_evidence_refs": ["sim://pick-cup/pass-001"],
        "approval_ref": "approval://user/session-001",
        "emergency_stop_ref": "estop://local/session-001",
        "max_force_newtons": 10.0,
        "max_speed_mps": 0.2,
        "policy_refs": [ROBOT_SPATIAL_SAFETY_POLICY_REF],
    }
    payload.update(overrides)
    return RobotSpatialSafetyEnvelope.model_validate(payload)


def test_valid_spatial_robot_action_requires_approval_and_audit_metadata():
    envelope = _envelope()
    decision = evaluate_robot_spatial_safety(envelope)

    assert decision.allowed
    assert decision.required_behavior == "approval_before_physical_effect"
    assert decision.reason_codes == []
    assert "capability:robot.arm.grasp.v1" in decision.audit_tags
    assert ROBOT_SPATIAL_SAFETY_POLICY_REF in decision.policy_refs


def test_physical_robot_effect_requires_emergency_stop_force_and_speed_metadata():
    with pytest.raises(ValidationError, match="emergency-stop"):
        _envelope(emergency_stop_ref=None)

    with pytest.raises(ValidationError, match="max force"):
        _envelope(max_force_newtons=None)

    with pytest.raises(ValidationError, match="max speed"):
        _envelope(max_speed_mps=None)


def test_physical_robot_action_is_denied_until_simulation_passes_and_user_approves():
    decision = evaluate_robot_spatial_safety(
        _envelope(
            simulation_status=RobotSimulationStatus.NOT_RUN,
            simulation_evidence_refs=[],
            approval_ref=None,
        )
    )

    assert not decision.allowed
    assert decision.required_behavior == "fix_metadata_before_action"
    assert decision.reason_codes == [
        "simulation_not_passed",
        "approval_required_before_physical_effect",
    ]


def test_spatial_hazards_and_bystanders_force_step_review():
    decision = evaluate_robot_spatial_safety(
        _envelope(
            hazards=[RobotHazardKind.HUMAN_PROXIMITY, RobotHazardKind.LIQUID],
            bystander_present=True,
        )
    )

    assert not decision.allowed
    assert decision.required_behavior == "step_by_step_review"
    assert "spatial_hazards_require_step_review" in decision.reason_codes
    assert "bystander_present_step_review_required" in decision.reason_codes


def test_high_or_critical_robot_risk_never_slips_into_autonomous_execution():
    high = evaluate_robot_spatial_safety(_envelope(risk_level=ActionRisk.HIGH))
    critical = evaluate_robot_spatial_safety(_envelope(risk_level=ActionRisk.CRITICAL))

    assert not high.allowed
    assert high.required_behavior == "step_by_step_review"
    assert "high_risk_step_review_required" in high.reason_codes
    assert not critical.allowed
    assert critical.required_behavior == "blocked_by_default"
    assert "critical_action_blocked_by_default" in critical.reason_codes


def test_robot_safety_rejects_wildcard_or_non_robot_capability_refs():
    with pytest.raises(ValidationError, match="explicit robot capability"):
        _envelope(capability="arm.grasp.v1")

    with pytest.raises(ValidationError, match="wildcard"):
        _envelope(source_refs=["all"])

    with pytest.raises(ValidationError, match="wildcard"):
        _envelope(workspace_bounds_ref="global")
