from cortex_memory_os.native_permission_smoke import build_fixture_permission_smoke_result
from cortex_memory_os.shadow_pointer import (
    SHADOW_POINTER_PERMISSION_ONBOARDING_POLICY_REF,
    ShadowPointerState,
    build_permission_onboarding_receipt,
)


def test_permission_onboarding_renders_status_without_capture_or_writes():
    permission_result = build_fixture_permission_smoke_result(
        screen_recording_preflight=True,
        accessibility_trusted=False,
    )

    receipt = build_permission_onboarding_receipt(permission_result)

    assert receipt.policy_ref == SHADOW_POINTER_PERMISSION_ONBOARDING_POLICY_REF
    assert receipt.resulting_snapshot.state == ShadowPointerState.NEEDS_APPROVAL
    assert "Screen Recording: ready" in receipt.resulting_snapshot.seeing
    assert "Accessibility: not ready" in receipt.resulting_snapshot.seeing
    assert "screen capture not started" in receipt.resulting_snapshot.ignoring
    assert receipt.prompt_requested is False
    assert receipt.capture_started is False
    assert receipt.accessibility_observer_started is False
    assert receipt.memory_write_allowed is False
    assert receipt.evidence_refs == []
    assert set(receipt.allowed_effects) == {
        "read_permission_status",
        "render_shadow_pointer_permission_state",
    }
    assert "start_screen_capture" in receipt.blocked_effects
    assert "store_raw_evidence" in receipt.blocked_effects


def test_permission_onboarding_still_requires_consent_when_permissions_are_ready():
    permission_result = build_fixture_permission_smoke_result(
        screen_recording_preflight=True,
        accessibility_trusted=True,
    )

    receipt = build_permission_onboarding_receipt(permission_result)

    assert receipt.resulting_snapshot.state == ShadowPointerState.NEEDS_APPROVAL
    assert receipt.resulting_snapshot.approval_reason == (
        "Start observation requires explicit consent."
    )
    assert receipt.capture_started is False
    assert receipt.memory_write_allowed is False
