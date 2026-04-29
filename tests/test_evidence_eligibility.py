import pytest

from cortex_memory_os.contracts import (
    FirewallDecision,
    PerceptionEventEnvelope,
    RetentionPolicy,
    Sensitivity,
)
from cortex_memory_os.evidence_eligibility import (
    EVIDENCE_ELIGIBILITY_HANDOFF_POLICY_REF,
    EvidenceWriteMode,
    build_evidence_eligibility_plan,
)
from cortex_memory_os.evidence_vault import EvidenceVault
from cortex_memory_os.firewall import assess_perception_envelope
from cortex_memory_os.fixtures import load_json


def _envelope(**updates) -> PerceptionEventEnvelope:
    payload = load_json("tests/fixtures/perception_terminal_envelope.json")
    payload.update(updates)
    return PerceptionEventEnvelope.model_validate(payload)


def test_memory_eligible_firewall_decision_allows_raw_and_derived_vault_write(tmp_path):
    envelope = _envelope()
    assessment = assess_perception_envelope(envelope, "uv run pytest passed")

    plan = build_evidence_eligibility_plan(envelope, assessment.decision)
    evidence = plan.to_evidence_record()
    vault = EvidenceVault(tmp_path)
    metadata = vault.store(evidence, b"synthetic raw terminal event")

    assert assessment.decision.decision == FirewallDecision.MEMORY_ELIGIBLE
    assert plan.write_mode == EvidenceWriteMode.RAW_AND_DERIVED
    assert plan.raw_blob_write_allowed is True
    assert plan.eligible_for_memory is True
    assert plan.raw_ref == "raw://terminal/obs_001"
    assert plan.derived_text_refs == ["ocr_001"]
    assert EVIDENCE_ELIGIBILITY_HANDOFF_POLICY_REF in plan.policy_refs
    assert evidence.raw_ref == "raw://terminal/obs_001"
    assert metadata.raw_ref == "vault://evidence/ev_obs_001"
    assert vault.read_raw("ev_obs_001", now=evidence.timestamp) == b"synthetic raw terminal event"


def test_secret_mask_plan_drops_raw_and_keeps_only_redacted_ref(tmp_path):
    envelope = _envelope()
    assessment = assess_perception_envelope(
        envelope,
        "token=CORTEX_FAKE_TOKEN_handoffSECRET123",
    )

    plan = build_evidence_eligibility_plan(
        envelope,
        assessment.decision,
        redacted_text_ref="derived://redacted/obs_001",
    )
    vault = EvidenceVault(tmp_path)
    metadata = vault.store_metadata_only(plan.to_evidence_record())

    assert assessment.decision.decision == FirewallDecision.MASK
    assert plan.write_mode == EvidenceWriteMode.DERIVED_ONLY
    assert plan.sensitivity == Sensitivity.SECRET
    assert plan.raw_ref is None
    assert plan.raw_blob_write_allowed is False
    assert plan.eligible_for_memory is False
    assert plan.derived_text_refs == ["derived://redacted/obs_001"]
    assert metadata.raw_ref is None
    assert metadata.blob_path is None
    assert list((tmp_path / "blobs").glob("*")) == []
    assert vault.read_raw("ev_obs_001") is None


def test_prompt_injection_quarantine_plan_discards_all_refs(tmp_path):
    envelope = _envelope(raw_ref=None, prompt_injection_risk=True)
    assessment = assess_perception_envelope(envelope, "ordinary copied page text")

    plan = build_evidence_eligibility_plan(envelope, assessment.decision)
    metadata = EvidenceVault(tmp_path).store_metadata_only(plan.to_evidence_record())

    assert assessment.decision.decision == FirewallDecision.QUARANTINE
    assert plan.write_mode == EvidenceWriteMode.DISCARD
    assert plan.retention_policy == RetentionPolicy.DISCARD
    assert plan.raw_ref is None
    assert plan.derived_text_refs == []
    assert plan.eligible_for_memory is False
    assert metadata.raw_ref is None
    assert metadata.raw_deleted_at is not None


def test_third_party_content_plan_is_never_raw_or_memory_eligible():
    envelope = _envelope(third_party_content=True)
    assessment = assess_perception_envelope(envelope, "benign newsletter text")

    plan = build_evidence_eligibility_plan(envelope, assessment.decision)

    assert assessment.decision.decision == FirewallDecision.EPHEMERAL_ONLY
    assert plan.write_mode == EvidenceWriteMode.DERIVED_ONLY
    assert plan.raw_ref is None
    assert plan.raw_blob_write_allowed is False
    assert plan.contains_third_party_content is True
    assert plan.eligible_for_memory is False
    assert plan.derived_text_refs == ["ocr_001"]


def test_evidence_plan_rejects_mismatched_firewall_decision_event():
    envelope = _envelope()
    assessment = assess_perception_envelope(envelope, "uv run pytest passed")
    mismatched = assessment.decision.model_copy(update={"event_id": "obs_other"})

    with pytest.raises(ValueError, match="event_id must match"):
        build_evidence_eligibility_plan(envelope, mismatched)
