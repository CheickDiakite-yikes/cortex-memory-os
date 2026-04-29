"""Robot-ready spatial safety contracts for future embodied actions."""

from __future__ import annotations

from enum import Enum

from pydantic import Field, field_validator, model_validator

from cortex_memory_os.contracts import ActionRisk, StrictModel

ROBOT_SPATIAL_SAFETY_POLICY_REF = "policy_robot_spatial_safety_v1"
ROBOT_MAX_FORCE_NEWTONS = 30.0
ROBOT_MAX_SPEED_MPS = 0.35


class RobotHazardKind(str, Enum):
    HUMAN_PROXIMITY = "human_proximity"
    FRAGILE_OBJECT = "fragile_object"
    LIQUID = "liquid"
    HEAT = "heat"
    SHARP_EDGE = "sharp_edge"
    PINCH_POINT = "pinch_point"
    RESTRICTED_ZONE = "restricted_zone"
    UNKNOWN_OBJECT = "unknown_object"


class RobotSimulationStatus(str, Enum):
    NOT_RUN = "not_run"
    FAILED = "failed"
    PASSED = "passed"


class RobotSpatialSafetyEnvelope(StrictModel):
    action_id: str = Field(min_length=1)
    capability: str = Field(min_length=1)
    action_summary: str = Field(min_length=1)
    source_refs: list[str] = Field(min_length=1)
    workspace_bounds_ref: str = Field(min_length=1)
    target_object_ref: str | None = None
    affordances: list[str] = Field(default_factory=list)
    material_constraints: list[str] = Field(default_factory=list)
    hazards: list[RobotHazardKind] = Field(default_factory=list)
    bystander_present: bool = False
    risk_level: ActionRisk = ActionRisk.MEDIUM
    physical_effect: bool = True
    simulation_status: RobotSimulationStatus = RobotSimulationStatus.NOT_RUN
    simulation_evidence_refs: list[str] = Field(default_factory=list)
    approval_ref: str | None = None
    emergency_stop_ref: str | None = None
    max_force_newtons: float | None = Field(default=None, gt=0)
    max_speed_mps: float | None = Field(default=None, gt=0)
    policy_refs: list[str] = Field(
        default_factory=lambda: [ROBOT_SPATIAL_SAFETY_POLICY_REF],
        min_length=1,
    )

    @field_validator(
        "capability",
        "workspace_bounds_ref",
        "target_object_ref",
        "approval_ref",
        "emergency_stop_ref",
    )
    @classmethod
    def reject_wildcard_scalar_refs(cls, value: str | None) -> str | None:
        if value is not None and _is_wildcard_ref(value):
            raise ValueError("robot spatial safety refs cannot be wildcard scopes")
        return value

    @field_validator("source_refs", "simulation_evidence_refs", "policy_refs")
    @classmethod
    def reject_wildcard_list_refs(cls, values: list[str]) -> list[str]:
        if any(_is_wildcard_ref(value) for value in values):
            raise ValueError("robot spatial safety refs cannot be wildcard scopes")
        return values

    @model_validator(mode="after")
    def enforce_spatial_safety_metadata(self) -> RobotSpatialSafetyEnvelope:
        if ROBOT_SPATIAL_SAFETY_POLICY_REF not in self.policy_refs:
            raise ValueError("robot spatial safety policy ref is required")
        if not self.capability.startswith("robot."):
            raise ValueError("robot actions require explicit robot capability refs")
        if self.simulation_status in {
            RobotSimulationStatus.FAILED,
            RobotSimulationStatus.PASSED,
        } and not self.simulation_evidence_refs:
            raise ValueError("simulation status requires simulation evidence refs")
        if self.physical_effect:
            if not self.emergency_stop_ref:
                raise ValueError("physical robot effects require emergency-stop ref")
            if self.max_force_newtons is None:
                raise ValueError("physical robot effects require max force metadata")
            if self.max_speed_mps is None:
                raise ValueError("physical robot effects require max speed metadata")
        return self


class RobotSpatialSafetyDecision(StrictModel):
    allowed: bool
    required_behavior: str
    reason_codes: list[str]
    policy_refs: list[str]
    audit_tags: list[str]


def evaluate_robot_spatial_safety(
    envelope: RobotSpatialSafetyEnvelope,
) -> RobotSpatialSafetyDecision:
    reason_codes: list[str] = []

    if envelope.physical_effect and envelope.simulation_status != RobotSimulationStatus.PASSED:
        reason_codes.append("simulation_not_passed")
    if envelope.physical_effect and not envelope.approval_ref:
        reason_codes.append("approval_required_before_physical_effect")
    if envelope.bystander_present:
        reason_codes.append("bystander_present_step_review_required")
    if envelope.hazards:
        reason_codes.append("spatial_hazards_require_step_review")
    if envelope.risk_level == ActionRisk.HIGH:
        reason_codes.append("high_risk_step_review_required")
    if envelope.risk_level == ActionRisk.CRITICAL:
        reason_codes.append("critical_action_blocked_by_default")
    if (
        envelope.max_force_newtons is not None
        and envelope.max_force_newtons > ROBOT_MAX_FORCE_NEWTONS
    ):
        reason_codes.append("force_limit_exceeded")
    if envelope.max_speed_mps is not None and envelope.max_speed_mps > ROBOT_MAX_SPEED_MPS:
        reason_codes.append("speed_limit_exceeded")

    return RobotSpatialSafetyDecision(
        allowed=not reason_codes,
        required_behavior=_required_behavior(envelope, reason_codes),
        reason_codes=reason_codes,
        policy_refs=[ROBOT_SPATIAL_SAFETY_POLICY_REF],
        audit_tags=[
            f"capability:{envelope.capability}",
            f"workspace:{envelope.workspace_bounds_ref}",
            f"simulation:{envelope.simulation_status.value}",
            f"hazards:{len(envelope.hazards)}",
        ],
    )


def _required_behavior(
    envelope: RobotSpatialSafetyEnvelope,
    reason_codes: list[str],
) -> str:
    if "critical_action_blocked_by_default" in reason_codes:
        return "blocked_by_default"
    step_review_reasons = {
        "bystander_present_step_review_required",
        "spatial_hazards_require_step_review",
        "high_risk_step_review_required",
    }
    if any(reason in step_review_reasons for reason in reason_codes):
        return "step_by_step_review"
    if reason_codes:
        return "fix_metadata_before_action"
    if envelope.physical_effect:
        return "approval_before_physical_effect"
    return "audit_only"


def _is_wildcard_ref(value: str) -> bool:
    return value.strip().lower() in {"*", "all", "global", "any"}
