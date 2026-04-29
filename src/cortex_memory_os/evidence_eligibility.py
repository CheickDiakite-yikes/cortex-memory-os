"""Firewall-to-evidence eligibility handoff contracts."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import Field, model_validator

from cortex_memory_os.contracts import (
    EvidenceRecord,
    FirewallDecision,
    FirewallDecisionRecord,
    ObservationEventType,
    PerceptionEventEnvelope,
    RetentionPolicy,
    Sensitivity,
    StrictModel,
)

EVIDENCE_ELIGIBILITY_HANDOFF_POLICY_REF = "policy_evidence_eligibility_handoff_v1"


class EvidenceWriteMode(str, Enum):
    DISCARD = "discard"
    METADATA_ONLY = "metadata_only"
    DERIVED_ONLY = "derived_only"
    RAW_AND_DERIVED = "raw_and_derived"


class EvidenceEligibilityPlan(StrictModel):
    plan_id: str = Field(min_length=1)
    evidence_id: str = Field(min_length=1)
    event_id: str = Field(min_length=1)
    decision_id: str = Field(min_length=1)
    source: ObservationEventType
    device: str = Field(min_length=1)
    app: str | None = None
    timestamp: datetime
    write_mode: EvidenceWriteMode
    raw_ref: str | None = None
    derived_text_refs: list[str] = Field(default_factory=list)
    retention_policy: RetentionPolicy
    sensitivity: Sensitivity
    contains_third_party_content: bool
    eligible_for_memory: bool
    eligible_for_model_training: bool = False
    raw_blob_write_allowed: bool
    metadata_write_allowed: bool = True
    policy_refs: list[str] = Field(default_factory=list)
    audit_event_id: str = Field(min_length=1)
    reasons: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def enforce_write_mode_consistency(self) -> EvidenceEligibilityPlan:
        if self.eligible_for_model_training:
            raise ValueError("evidence handoff forbids model-training eligibility")
        if self.raw_blob_write_allowed and self.write_mode != EvidenceWriteMode.RAW_AND_DERIVED:
            raise ValueError("raw blob writes require raw_and_derived mode")
        if self.raw_blob_write_allowed and not self.raw_ref:
            raise ValueError("raw blob writes require a raw_ref")
        if self.write_mode == EvidenceWriteMode.RAW_AND_DERIVED and not self.raw_ref:
            raise ValueError("raw_and_derived mode requires a raw_ref")
        if self.write_mode in {EvidenceWriteMode.DISCARD, EvidenceWriteMode.METADATA_ONLY}:
            if self.raw_ref or self.derived_text_refs:
                raise ValueError("discard and metadata-only modes cannot keep refs")
        if self.write_mode == EvidenceWriteMode.DERIVED_ONLY and self.raw_ref:
            raise ValueError("derived-only mode cannot keep a raw_ref")
        if self.eligible_for_memory and self.write_mode in {
            EvidenceWriteMode.DISCARD,
            EvidenceWriteMode.METADATA_ONLY,
        }:
            raise ValueError("memory-eligible evidence needs durable raw or derived refs")
        if self.sensitivity == Sensitivity.SECRET:
            if self.eligible_for_memory or self.raw_blob_write_allowed or self.raw_ref:
                raise ValueError("secret evidence cannot be memory eligible or raw writable")
        if self.contains_third_party_content:
            if self.eligible_for_memory or self.raw_blob_write_allowed or self.raw_ref:
                raise ValueError("third-party evidence cannot be memory eligible or raw writable")
        return self

    def to_evidence_record(self) -> EvidenceRecord:
        return EvidenceRecord(
            evidence_id=self.evidence_id,
            source=self.source,
            device=self.device,
            app=self.app,
            timestamp=self.timestamp,
            raw_ref=self.raw_ref,
            derived_text_refs=self.derived_text_refs,
            retention_policy=self.retention_policy,
            sensitivity=self.sensitivity,
            contains_third_party_content=self.contains_third_party_content,
            eligible_for_memory=self.eligible_for_memory,
            eligible_for_model_training=self.eligible_for_model_training,
        )


def build_evidence_eligibility_plan(
    envelope: PerceptionEventEnvelope,
    decision: FirewallDecisionRecord,
    *,
    redacted_text_ref: str | None = None,
) -> EvidenceEligibilityPlan:
    """Convert a firewall decision into an Evidence Vault write plan."""

    if decision.event_id != envelope.observation.event_id:
        raise ValueError("firewall decision event_id must match perception envelope")

    reasons: list[str] = []
    raw_ref = envelope.raw_ref
    derived_text_refs = list(envelope.derived_refs)
    retention_policy = decision.retention_policy
    eligible_for_memory = decision.eligible_for_memory
    raw_blob_write_allowed = False
    write_mode = EvidenceWriteMode.METADATA_ONLY

    if decision.decision in {FirewallDecision.DISCARD, FirewallDecision.QUARANTINE}:
        reasons.append(f"firewall_{decision.decision.value}")
        raw_ref = None
        derived_text_refs = []
        retention_policy = RetentionPolicy.DISCARD
        eligible_for_memory = False
        write_mode = EvidenceWriteMode.DISCARD
    elif decision.decision == FirewallDecision.MASK:
        reasons.append("raw_dropped_after_secret_redaction")
        raw_ref = None
        derived_text_refs = [redacted_text_ref] if redacted_text_ref else []
        eligible_for_memory = False
        write_mode = (
            EvidenceWriteMode.DERIVED_ONLY
            if derived_text_refs
            else EvidenceWriteMode.METADATA_ONLY
        )
    elif decision.decision == FirewallDecision.EPHEMERAL_ONLY:
        reasons.append("ephemeral_or_external_content")
        raw_ref = None
        eligible_for_memory = False
        write_mode = (
            EvidenceWriteMode.DERIVED_ONLY
            if derived_text_refs
            else EvidenceWriteMode.METADATA_ONLY
        )
    elif decision.decision == FirewallDecision.MEMORY_ELIGIBLE:
        reasons.append("firewall_memory_eligible")
        if raw_ref:
            raw_blob_write_allowed = True
            write_mode = EvidenceWriteMode.RAW_AND_DERIVED
        elif derived_text_refs:
            write_mode = EvidenceWriteMode.DERIVED_ONLY
        else:
            eligible_for_memory = False
            reasons.append("no_evidence_refs_available")

    if decision.sensitivity == Sensitivity.SECRET:
        raw_ref = None
        raw_blob_write_allowed = False
        eligible_for_memory = False
        if "secret_sensitivity" not in reasons:
            reasons.append("secret_sensitivity")

    if envelope.third_party_content:
        raw_ref = None
        raw_blob_write_allowed = False
        eligible_for_memory = False
        if "third_party_content" not in reasons:
            reasons.append("third_party_content")
        if write_mode == EvidenceWriteMode.RAW_AND_DERIVED:
            write_mode = (
                EvidenceWriteMode.DERIVED_ONLY
                if derived_text_refs
                else EvidenceWriteMode.METADATA_ONLY
            )

    if not raw_ref and write_mode == EvidenceWriteMode.RAW_AND_DERIVED:
        write_mode = (
            EvidenceWriteMode.DERIVED_ONLY
            if derived_text_refs
            else EvidenceWriteMode.METADATA_ONLY
        )

    policy_refs = _ordered_policy_refs(
        [EVIDENCE_ELIGIBILITY_HANDOFF_POLICY_REF],
        decision.policy_refs,
        envelope.required_policy_refs,
    )

    return EvidenceEligibilityPlan(
        plan_id=f"evidence_plan_{envelope.observation.event_id}",
        evidence_id=f"ev_{envelope.observation.event_id}",
        event_id=envelope.observation.event_id,
        decision_id=decision.decision_id,
        source=envelope.observation.event_type,
        device=envelope.observation.device,
        app=envelope.observation.app,
        timestamp=envelope.observation.timestamp,
        write_mode=write_mode,
        raw_ref=raw_ref,
        derived_text_refs=derived_text_refs,
        retention_policy=retention_policy,
        sensitivity=decision.sensitivity,
        contains_third_party_content=envelope.third_party_content,
        eligible_for_memory=eligible_for_memory,
        eligible_for_model_training=False,
        raw_blob_write_allowed=raw_blob_write_allowed,
        metadata_write_allowed=True,
        policy_refs=policy_refs,
        audit_event_id=decision.audit_event_id,
        reasons=reasons,
    )


def _ordered_policy_refs(*groups: list[str]) -> list[str]:
    refs: list[str] = []
    for group in groups:
        for ref in group:
            if ref not in refs:
                refs.append(ref)
    return refs
