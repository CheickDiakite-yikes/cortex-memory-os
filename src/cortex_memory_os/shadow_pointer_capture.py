"""Shadow Pointer receipts for governed capture adapter outcomes."""

from __future__ import annotations

from pydantic import Field, model_validator

from cortex_memory_os.contracts import (
    ConsentState,
    FirewallDecision,
    PerceptionRoute,
    StrictModel,
)
from cortex_memory_os.evidence_eligibility import EvidenceWriteMode
from cortex_memory_os.perception_adapters import AdapterHandoffResult, AdapterSource
from cortex_memory_os.shadow_pointer import ShadowPointerSnapshot, ShadowPointerState


SHADOW_POINTER_CAPTURE_WIRING_POLICY_REF = "policy_shadow_pointer_capture_wiring_v1"


class ShadowPointerCaptureReceipt(StrictModel):
    receipt_id: str = Field(min_length=1)
    event_id: str = Field(min_length=1)
    adapter_source: AdapterSource
    resulting_snapshot: ShadowPointerSnapshot
    observation_active: bool
    memory_write_allowed: bool
    requires_user_confirmation: bool
    audit_required: bool
    audit_action: str | None = None
    perception_route: PerceptionRoute
    firewall_decision: FirewallDecision
    evidence_write_mode: EvidenceWriteMode
    evidence_refs: list[str] = Field(default_factory=list)
    policy_refs: tuple[str, ...] = Field(min_length=1)
    safety_notes: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def enforce_capture_receipt_safety(self) -> ShadowPointerCaptureReceipt:
        if SHADOW_POINTER_CAPTURE_WIRING_POLICY_REF not in self.policy_refs:
            raise ValueError("capture receipts require the Shadow Pointer capture policy")
        if any(ref.startswith("raw://") for ref in self.evidence_refs):
            raise ValueError("Shadow Pointer capture receipts cannot expose raw refs")
        if self.memory_write_allowed:
            if self.firewall_decision != FirewallDecision.MEMORY_ELIGIBLE:
                raise ValueError("memory writes require memory-eligible firewall decision")
            if self.evidence_write_mode in {
                EvidenceWriteMode.DISCARD,
                EvidenceWriteMode.METADATA_ONLY,
            }:
                raise ValueError("memory writes require durable derived or raw-derived evidence")
            if self.resulting_snapshot.state in {
                ShadowPointerState.OFF,
                ShadowPointerState.PAUSED,
                ShadowPointerState.PRIVATE_MASKING,
                ShadowPointerState.NEEDS_APPROVAL,
            }:
                raise ValueError("blocked Shadow Pointer states cannot allow memory writes")
        if (
            self.resulting_snapshot.state == ShadowPointerState.NEEDS_APPROVAL
            and not self.requires_user_confirmation
        ):
            raise ValueError("needs-approval capture receipts require user confirmation")
        if self.audit_required and not self.audit_action:
            raise ValueError("audit-required capture receipts require audit_action")
        return self


def build_shadow_pointer_capture_receipt(
    result: AdapterHandoffResult,
) -> ShadowPointerCaptureReceipt:
    """Map adapter/firewall/evidence outcomes to a user-visible overlay receipt."""

    state, observation_active, memory_write_allowed, confirmation_required = _state_flags(
        result
    )
    snapshot = _snapshot_for_result(result, state)
    audit_required = state in {
        ShadowPointerState.OFF,
        ShadowPointerState.PAUSED,
        ShadowPointerState.PRIVATE_MASKING,
        ShadowPointerState.NEEDS_APPROVAL,
    }
    return ShadowPointerCaptureReceipt(
        receipt_id=(
            f"shadow_capture_{result.envelope.observation.event_id}_"
            f"{result.firewall.decision.value}"
        ),
        event_id=result.envelope.observation.event_id,
        adapter_source=result.adapter_source,
        resulting_snapshot=snapshot,
        observation_active=observation_active,
        memory_write_allowed=memory_write_allowed,
        requires_user_confirmation=confirmation_required,
        audit_required=audit_required,
        audit_action=_audit_action(state) if audit_required else None,
        perception_route=result.envelope.route,
        firewall_decision=result.firewall.decision,
        evidence_write_mode=result.evidence_plan.write_mode,
        evidence_refs=_overlay_evidence_refs(result),
        policy_refs=_policy_refs(result),
        safety_notes=_safety_notes(result, state),
    )


def _state_flags(
    result: AdapterHandoffResult,
) -> tuple[ShadowPointerState, bool, bool, bool]:
    if result.envelope.consent_state == ConsentState.PAUSED:
        return ShadowPointerState.PAUSED, False, False, False
    if result.envelope.consent_state in {ConsentState.REVOKED, ConsentState.UNKNOWN}:
        return ShadowPointerState.OFF, False, False, False
    if result.envelope.route == PerceptionRoute.DISCARD:
        return ShadowPointerState.PRIVATE_MASKING, False, False, False
    if result.firewall.decision == FirewallDecision.QUARANTINE:
        return ShadowPointerState.NEEDS_APPROVAL, True, False, True
    if result.firewall.decision == FirewallDecision.MASK:
        return ShadowPointerState.PRIVATE_MASKING, True, False, False
    if result.firewall.decision == FirewallDecision.EPHEMERAL_ONLY:
        return ShadowPointerState.OBSERVING, True, False, False
    if (
        result.firewall.decision == FirewallDecision.MEMORY_ELIGIBLE
        and result.evidence_plan.eligible_for_memory
    ):
        return ShadowPointerState.OBSERVING, True, True, False
    return ShadowPointerState.SEGMENTING, True, False, False


def _snapshot_for_result(
    result: AdapterHandoffResult,
    state: ShadowPointerState,
) -> ShadowPointerSnapshot:
    source_label = _source_label(result)
    if state == ShadowPointerState.OFF:
        return ShadowPointerSnapshot(
            state=state,
            workstream_label="Observation off",
        )
    if state == ShadowPointerState.PAUSED:
        return ShadowPointerSnapshot(
            state=state,
            workstream_label="Observation paused",
            ignoring=["all capture adapter output"],
        )
    if state == ShadowPointerState.PRIVATE_MASKING:
        return ShadowPointerSnapshot(
            state=state,
            workstream_label=f"Masking {source_label}",
            seeing=[source_label] if result.envelope.route != PerceptionRoute.DISCARD else [],
            ignoring=_ignoring_reasons(result),
        )
    if state == ShadowPointerState.NEEDS_APPROVAL:
        return ShadowPointerSnapshot(
            state=state,
            workstream_label=f"Review {source_label}",
            seeing=[source_label, "quarantined content"],
            ignoring=_ignoring_reasons(result),
            approval_reason="Prompt-risk content was quarantined before memory use.",
        )
    return ShadowPointerSnapshot(
        state=state,
        workstream_label=f"Observing {source_label}",
        seeing=[source_label],
        ignoring=_ignoring_reasons(result),
        possible_memory=(
            f"Derived {result.adapter_source.value} observation eligible for memory compiler"
            if result.evidence_plan.eligible_for_memory
            else None
        ),
    )


def _source_label(result: AdapterHandoffResult) -> str:
    app = result.evidence_plan.app or result.envelope.observation.app
    if app:
        return app
    return result.adapter_source.value.replace("_", " ")


def _ignoring_reasons(result: AdapterHandoffResult) -> list[str]:
    reasons: list[str] = []
    if result.envelope.route == PerceptionRoute.DISCARD:
        reasons.append("discarded capture output")
    if result.envelope.third_party_content:
        reasons.append("third-party content memory writes")
    if result.firewall.detected_risks:
        reasons.extend(result.firewall.detected_risks)
    if result.firewall.redactions:
        reasons.append("secret-like text redacted")
    if result.evidence_plan.raw_ref is None:
        reasons.append("raw refs hidden from overlay")
    if result.evidence_plan.reasons:
        reasons.extend(result.evidence_plan.reasons)
    if not reasons:
        reasons.append("no private content currently masked")
    return _dedupe(reasons)


def _overlay_evidence_refs(result: AdapterHandoffResult) -> list[str]:
    refs = [result.evidence_plan.evidence_id, *result.evidence_plan.derived_text_refs]
    return [ref for ref in _dedupe(refs) if not ref.startswith("raw://")]


def _policy_refs(result: AdapterHandoffResult) -> tuple[str, ...]:
    return tuple(
        _dedupe(
            [
                SHADOW_POINTER_CAPTURE_WIRING_POLICY_REF,
                *result.envelope.required_policy_refs,
                *result.firewall.policy_refs,
                *result.evidence_plan.policy_refs,
            ]
        )
    )


def _audit_action(state: ShadowPointerState) -> str:
    return f"shadow_pointer_capture_{state.value}"


def _safety_notes(
    result: AdapterHandoffResult,
    state: ShadowPointerState,
) -> list[str]:
    notes = [
        "receipt summarizes adapter outcomes only; it does not start capture",
        "raw refs are not exposed to the overlay receipt",
    ]
    if state == ShadowPointerState.NEEDS_APPROVAL:
        notes.append("quarantined content needs explicit review before reuse")
    if state in {ShadowPointerState.PRIVATE_MASKING, ShadowPointerState.PAUSED}:
        notes.append("memory writes are blocked for this capture outcome")
    if result.evidence_plan.eligible_for_model_training is False:
        notes.append("model training eligibility remains disabled")
    return notes


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            deduped.append(value)
    return deduped
