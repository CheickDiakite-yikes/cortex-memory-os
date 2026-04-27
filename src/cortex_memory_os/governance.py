"""Governance decisions for synthetic action and skill benchmarks."""

from __future__ import annotations

from dataclasses import dataclass

from cortex_memory_os.contracts import ActionRisk


@dataclass(frozen=True)
class ActionGateDecision:
    allowed: bool
    required_behavior: str
    reason: str


def gate_action(risk: ActionRisk, *, skill_approved: bool) -> ActionGateDecision:
    if risk == ActionRisk.LOW:
        if skill_approved:
            return ActionGateDecision(
                allowed=True,
                required_behavior="audit_only",
                reason="low risk approved skill",
            )
        return ActionGateDecision(
            allowed=True,
            required_behavior="confirmation_before_first_run",
            reason="low risk skill is not approved yet",
        )

    if risk == ActionRisk.MEDIUM:
        return ActionGateDecision(
            allowed=True,
            required_behavior="confirmation_before_external_effect",
            reason="medium risk action may alter project artifacts or drafts",
        )

    if risk == ActionRisk.HIGH:
        return ActionGateDecision(
            allowed=False,
            required_behavior="step_by_step_review",
            reason="high risk action requires user review before each external effect",
        )

    return ActionGateDecision(
        allowed=False,
        required_behavior="blocked_by_default",
        reason="critical actions are not autonomous in the MVP",
    )

