import pytest
from pydantic import ValidationError

from cortex_memory_os.contracts import SourceTrust
from cortex_memory_os.shadow_pointer import (
    CONSENT_FIRST_ONBOARDING_ID,
    CONSENT_FIRST_ONBOARDING_POLICY_REF,
    SHADOW_POINTER_LIVE_RECEIPT_POLICY_REF,
    SHADOW_POINTER_STATE_MACHINE_POLICY_REF,
    SPATIAL_PROPOSAL_SCHEMA_POLICY_REF,
    ShadowPointerCoordinateSpace,
    ShadowPointerObservationMode,
    ShadowPointerPointingAction,
    ShadowPointerPointingProposal,
    ShadowPointerState,
    ShadowPointerStatePresentation,
    all_state_presentations,
    build_live_receipt,
    default_consent_first_onboarding_plan,
    default_shadow_pointer_snapshot,
    map_pointing_proposal_to_viewport,
    state_presentation,
)


def test_all_shadow_pointer_states_have_compact_visual_contracts():
    presentations = all_state_presentations()

    assert {presentation.state for presentation in presentations} == set(ShadowPointerState)
    assert all(SHADOW_POINTER_STATE_MACHINE_POLICY_REF in item.policy_refs for item in presentations)
    assert all(item.compact_label for item in presentations)
    assert state_presentation(ShadowPointerState.PRIVATE_MASKING).tone == "warning"
    assert state_presentation(ShadowPointerState.OBSERVING).peripheral_cue == "steady halo"


def test_agent_action_state_blocks_unconfirmed_privileged_actions():
    with pytest.raises(ValidationError, match="unconfirmed actions"):
        ShadowPointerStatePresentation(
            state=ShadowPointerState.AGENT_ACTING,
            label="Agent Action",
            compact_label="Acting",
            icon="cursor",
            tone="danger",
            pointer_shape="attention",
            peripheral_cue="red pulse",
            allowed_effects=["render_pointer"],
            blocked_effects=[],
        )


def test_external_live_receipt_is_compact_and_memory_ineligible():
    snapshot = default_shadow_pointer_snapshot()

    receipt = build_live_receipt(
        snapshot,
        observation_mode=ShadowPointerObservationMode.SESSION,
        source_trust=SourceTrust.EXTERNAL_UNTRUSTED,
        firewall_decision="ephemeral_only",
        evidence_write_mode="derived_only",
        memory_eligible=False,
        raw_ref_retained=False,
        latest_action="Google News click",
    )

    assert receipt.policy_refs == (
        SHADOW_POINTER_LIVE_RECEIPT_POLICY_REF,
        SHADOW_POINTER_STATE_MACHINE_POLICY_REF,
    )
    assert receipt.title == "Observing With Consent"
    assert receipt.compact_fields["trust"] == "external_untrusted"
    assert receipt.compact_fields["memory"] == "not eligible"
    assert receipt.compact_fields["raw_refs"] == "none"
    assert receipt.raw_payload_included is False
    assert "trusted_instruction_promotion" in receipt.blocked_effects
    assert "durable_memory_write" in receipt.blocked_effects


def test_external_live_receipt_cannot_be_memory_eligible_or_retain_raw_refs():
    snapshot = default_shadow_pointer_snapshot()

    with pytest.raises(ValidationError, match="memory eligible"):
        build_live_receipt(
            snapshot,
            observation_mode=ShadowPointerObservationMode.SESSION,
            source_trust=SourceTrust.EXTERNAL_UNTRUSTED,
            firewall_decision="ephemeral_only",
            evidence_write_mode="derived_only",
            memory_eligible=True,
            raw_ref_retained=False,
        )

    with pytest.raises(ValidationError, match="retain raw refs"):
        build_live_receipt(
            snapshot,
            observation_mode=ShadowPointerObservationMode.SESSION,
            source_trust=SourceTrust.EXTERNAL_UNTRUSTED,
            firewall_decision="ephemeral_only",
            evidence_write_mode="derived_only",
            memory_eligible=False,
            raw_ref_retained=True,
        )


def test_paused_live_receipt_cannot_be_memory_eligible():
    snapshot = default_shadow_pointer_snapshot()

    with pytest.raises(ValidationError, match="inactive observation modes"):
        build_live_receipt(
            snapshot,
            observation_mode=ShadowPointerObservationMode.PAUSED,
            source_trust=SourceTrust.LOCAL_OBSERVED,
            firewall_decision="paused",
            evidence_write_mode="none",
            memory_eligible=True,
            raw_ref_retained=False,
        )


def test_spatial_mapping_keeps_pointing_display_only_and_bounded():
    proposal = ShadowPointerPointingProposal(
        proposal_id="point_ux_001",
        coordinate_space=ShadowPointerCoordinateSpace.SCREEN_NORMALIZED,
        x=0.5,
        y=0.25,
        target_label="Technology tab",
        reason="Model proposes highlighting a visible tab.",
        evidence_refs=["ev_browser_001"],
        confidence=0.8,
        requested_action=ShadowPointerPointingAction.CLICK,
    )

    mapping = map_pointing_proposal_to_viewport(
        proposal,
        viewport_width_px=1440,
        viewport_height_px=900,
        device_pixel_ratio=2.0,
    )

    assert mapping.policy_refs == (
        SPATIAL_PROPOSAL_SCHEMA_POLICY_REF,
        "policy_shadow_pointer_pointing_proposal_v1",
    )
    assert mapping.x_css_px == 720
    assert mapping.y_css_px == 225
    assert mapping.x_device_px == 1440
    assert mapping.y_device_px == 450
    assert mapping.display_only is True
    assert mapping.clamped is False


def test_consent_first_onboarding_plan_teaches_deletion_before_real_capture():
    plan = default_consent_first_onboarding_plan()

    assert plan.plan_id == CONSENT_FIRST_ONBOARDING_ID
    assert CONSENT_FIRST_ONBOARDING_POLICY_REF in plan.policy_refs
    assert plan.observation_mode == ShadowPointerObservationMode.INVOKED
    assert plan.synthetic_only is True
    assert plan.real_capture_started is False
    assert plan.raw_storage_enabled is False
    assert plan.durable_private_memory_write_enabled is False
    assert plan.external_effect_enabled is False
    assert [step.step_id for step in plan.steps] == [
        "show_off",
        "invoke_synthetic_observation",
        "prove_masking",
        "create_candidate_memory",
        "delete_candidate_memory",
        "show_audit_receipt",
    ]
    assert "silent_retention" in plan.steps[4].blocked_effects
