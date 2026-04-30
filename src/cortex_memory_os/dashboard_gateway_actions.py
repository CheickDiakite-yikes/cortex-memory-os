"""Read-only gateway receipts for dashboard action previews."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import Field, model_validator

from cortex_memory_os.contracts import StrictModel
from cortex_memory_os.memory_palace_dashboard import (
    MemoryPalaceActionPlan,
    MemoryPalaceDashboard,
)
from cortex_memory_os.skill_forge_dashboard import (
    SkillForgeActionPlan,
    SkillForgeCandidateList,
)


DASHBOARD_GATEWAY_ACTIONS_ID = "DASHBOARD-GATEWAY-ACTIONS-001"
DASHBOARD_GATEWAY_ACTIONS_POLICY_REF = "policy_dashboard_gateway_actions_v1"

DashboardActionSource = Literal["memory_palace", "skill_forge"]

_READ_ONLY_TOOLS = {
    "memory.explain",
    "skill.review_candidate",
}


class DashboardGatewayActionReceipt(StrictModel):
    receipt_id: str = Field(min_length=1)
    action_key: str = Field(min_length=1)
    action_source: DashboardActionSource
    gateway_tool: str = Field(min_length=1)
    target_ref: str = Field(min_length=1)
    required_inputs: list[str] = Field(default_factory=list)
    payload_preview: dict[str, str] = Field(default_factory=dict)
    allowed_gateway_call: bool
    read_only: bool
    mutation: bool
    data_egress: bool
    external_effect: bool = False
    requires_confirmation: bool
    blocked_reasons: list[str] = Field(default_factory=list)
    audit_required: bool
    audit_action: str | None = None
    content_redacted: bool = True
    generated_at: datetime
    policy_refs: tuple[str, ...] = Field(min_length=1)
    safety_notes: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def enforce_dashboard_gateway_boundary(self) -> DashboardGatewayActionReceipt:
        if DASHBOARD_GATEWAY_ACTIONS_POLICY_REF not in self.policy_refs:
            raise ValueError("dashboard gateway receipts require policy reference")
        if self.allowed_gateway_call:
            if not self.read_only:
                raise ValueError("dashboard gateway calls must be read-only")
            if self.mutation or self.data_egress or self.external_effect:
                raise ValueError("allowed dashboard calls cannot mutate, export, or act externally")
            if self.requires_confirmation:
                raise ValueError("confirmation-gated dashboard actions stay preview-only")
            if self.blocked_reasons:
                raise ValueError("allowed dashboard calls cannot include blocked reasons")
        else:
            if not self.blocked_reasons:
                raise ValueError("blocked dashboard action receipts need reasons")
        if not self.content_redacted:
            raise ValueError("dashboard gateway receipts must keep content redacted")
        if any("raw://" in value or "encrypted_blob://" in value for value in self.payload_preview.values()):
            raise ValueError("dashboard gateway payload previews cannot include raw private refs")
        return self


def build_dashboard_gateway_action_receipts(
    memory_palace: MemoryPalaceDashboard,
    skill_forge: SkillForgeCandidateList,
    *,
    now: datetime | None = None,
) -> list[DashboardGatewayActionReceipt]:
    timestamp = _timestamp(now)
    receipts: list[DashboardGatewayActionReceipt] = []
    for card in memory_palace.cards:
        for plan in card.action_plans:
            receipts.append(
                prepare_memory_dashboard_action(
                    target_ref=card.memory_id,
                    plan=plan,
                    now=timestamp,
                )
            )
    for card in skill_forge.cards:
        for plan in card.action_plans:
            receipts.append(
                prepare_skill_dashboard_action(
                    target_ref=card.skill_id,
                    plan=plan,
                    now=timestamp,
                )
            )
    return receipts


def prepare_memory_dashboard_action(
    *,
    target_ref: str,
    plan: MemoryPalaceActionPlan,
    now: datetime | None = None,
) -> DashboardGatewayActionReceipt:
    return _build_receipt(
        action_source="memory_palace",
        action_id=plan.flow_id.value,
        gateway_tool=plan.gateway_tool,
        target_ref=target_ref,
        required_inputs=plan.required_inputs,
        mutation=plan.mutation,
        data_egress=plan.data_egress,
        external_effect=False,
        requires_confirmation=plan.requires_confirmation,
        audit_action=plan.audit_action,
        now=now,
    )


def prepare_skill_dashboard_action(
    *,
    target_ref: str,
    plan: SkillForgeActionPlan,
    now: datetime | None = None,
) -> DashboardGatewayActionReceipt:
    return _build_receipt(
        action_source="skill_forge",
        action_id=plan.action_id,
        gateway_tool=plan.gateway_tool,
        target_ref=target_ref,
        required_inputs=plan.required_inputs,
        mutation=plan.mutation,
        data_egress=False,
        external_effect=plan.external_effect,
        requires_confirmation=plan.requires_confirmation,
        audit_action=plan.audit_action,
        now=now,
    )


def _build_receipt(
    *,
    action_source: DashboardActionSource,
    action_id: str,
    gateway_tool: str,
    target_ref: str,
    required_inputs: list[str],
    mutation: bool,
    data_egress: bool,
    external_effect: bool,
    requires_confirmation: bool,
    audit_action: str | None,
    now: datetime | None,
) -> DashboardGatewayActionReceipt:
    read_only = gateway_tool in _READ_ONLY_TOOLS and not (
        mutation or data_egress or external_effect
    )
    blocked_reasons = _blocked_reasons(
        gateway_tool=gateway_tool,
        read_only=read_only,
        mutation=mutation,
        data_egress=data_egress,
        external_effect=external_effect,
        requires_confirmation=requires_confirmation,
    )
    allowed_gateway_call = read_only and not blocked_reasons
    action_key = f"{gateway_tool}:{target_ref}"
    return DashboardGatewayActionReceipt(
        receipt_id=f"dash_gateway_{action_source}_{action_id}_{_safe_id(target_ref)}",
        action_key=action_key,
        action_source=action_source,
        gateway_tool=gateway_tool,
        target_ref=target_ref,
        required_inputs=list(required_inputs),
        payload_preview=_payload_preview(target_ref, required_inputs),
        allowed_gateway_call=allowed_gateway_call,
        read_only=read_only,
        mutation=mutation,
        data_egress=data_egress,
        external_effect=external_effect,
        requires_confirmation=requires_confirmation,
        blocked_reasons=blocked_reasons,
        audit_required=mutation or data_egress or external_effect or bool(audit_action),
        audit_action=audit_action,
        generated_at=_timestamp(now),
        policy_refs=(DASHBOARD_GATEWAY_ACTIONS_POLICY_REF,),
        safety_notes=[
            "dashboard actions are receipt previews before gateway execution",
            "only read-only explain and review tools are callable in this slice",
            "mutation, export, draft execution, and external-effect tools remain blocked",
        ],
    )


def _blocked_reasons(
    *,
    gateway_tool: str,
    read_only: bool,
    mutation: bool,
    data_egress: bool,
    external_effect: bool,
    requires_confirmation: bool,
) -> list[str]:
    reasons: list[str] = []
    if gateway_tool not in _READ_ONLY_TOOLS:
        reasons.append("tool_not_enabled_for_read_only_dashboard_slice")
    if not read_only:
        reasons.append("not_read_only")
    if mutation:
        reasons.append("mutation_blocked")
    if data_egress:
        reasons.append("data_egress_blocked")
    if external_effect:
        reasons.append("external_effect_blocked")
    if requires_confirmation:
        reasons.append("confirmation_required")
    return _dedupe(reasons)


def _payload_preview(target_ref: str, required_inputs: list[str]) -> dict[str, str]:
    payload: dict[str, str] = {}
    for input_name in required_inputs:
        if "memory_id" in input_name or "visible_card_anchor" in input_name:
            payload[input_name] = target_ref
        elif input_name == "skill_id":
            payload[input_name] = target_ref
        elif input_name.endswith("_ref") or "confirmation" in input_name:
            payload[input_name] = "<required_at_confirmation>"
        else:
            payload[input_name] = "<redacted_user_supplied_value>"
    return payload


def _safe_id(value: str) -> str:
    return "".join(character if character.isalnum() else "_" for character in value)


def _timestamp(now: datetime | None) -> datetime:
    timestamp = now or datetime.now(UTC)
    if timestamp.tzinfo is None:
        return timestamp.replace(tzinfo=UTC)
    return timestamp.astimezone(UTC)


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            deduped.append(value)
    return deduped
