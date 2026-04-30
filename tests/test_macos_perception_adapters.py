import pytest
from pydantic import ValidationError

from cortex_memory_os.contracts import (
    ConsentState,
    FirewallDecision,
    ObservationEventType,
    PerceptionRoute,
    PerceptionSourceKind,
    ScopeLevel,
    SourceTrust,
)
from cortex_memory_os.evidence_eligibility import EvidenceWriteMode
from cortex_memory_os.perception_adapters import (
    MACOS_PERCEPTION_ADAPTER_POLICY_REF,
    MacOSAccessibilityAdapterEvent,
    MacOSAppWindowAdapterEvent,
    MacOSPermissionState,
    build_macos_accessibility_envelope,
    build_macos_app_window_envelope,
    handoff_macos_accessibility_event,
    handoff_macos_app_window_event,
)


def _window_event(**updates):
    payload = {
        "event_id": "macos_window_001",
        "observed_at": "2026-04-30T09:00:00-04:00",
        "device": "macbook",
        "app": "Xcode",
        "bundle_id": "com.apple.dt.Xcode",
        "window_title": "Cortex Memory OS",
        "project_id": "cortex-memory-os",
        "capture_scope": ScopeLevel.APP_SPECIFIC,
        "consent_state": ConsentState.ACTIVE,
        "screen_recording_permission": MacOSPermissionState.GRANTED,
        "accessibility_permission": MacOSPermissionState.GRANTED,
        "app_allowed": True,
        "sensitive_app": False,
        "derived_text_ref": "derived://macos/app-window/macos_window_001",
        "sequence": 11,
    }
    payload.update(updates)
    return MacOSAppWindowAdapterEvent.model_validate(payload)


def _accessibility_event(**updates):
    payload = {
        "event_id": "macos_ax_001",
        "observed_at": "2026-04-30T09:01:00-04:00",
        "device": "macbook",
        "app": "VS Code",
        "bundle_id": "com.microsoft.VSCode",
        "window_title": "perception_adapters.py",
        "focused_role": "AXTextArea",
        "focused_label": "Editor",
        "value_preview": "handoff_macos_app_window_event",
        "project_id": "cortex-memory-os",
        "capture_scope": ScopeLevel.APP_SPECIFIC,
        "consent_state": ConsentState.ACTIVE,
        "accessibility_permission": MacOSPermissionState.GRANTED,
        "app_allowed": True,
        "private_field_detected": False,
        "derived_text_ref": "derived://macos/accessibility/macos_ax_001",
        "sequence": 12,
    }
    payload.update(updates)
    return MacOSAccessibilityAdapterEvent.model_validate(payload)


def test_macos_app_window_adapter_derives_without_raw_capture():
    event = _window_event()

    envelope = build_macos_app_window_envelope(event)
    result = handoff_macos_app_window_event(event)

    assert envelope.source_kind == PerceptionSourceKind.APP_WINDOW
    assert envelope.observation.event_type == ObservationEventType.APP_WINDOW
    assert envelope.source_trust == SourceTrust.LOCAL_OBSERVED
    assert envelope.route == PerceptionRoute.FIREWALL_REQUIRED
    assert envelope.raw_ref is None
    assert MACOS_PERCEPTION_ADAPTER_POLICY_REF in envelope.required_policy_refs
    assert result.firewall.decision == FirewallDecision.MEMORY_ELIGIBLE
    assert result.evidence_plan.write_mode == EvidenceWriteMode.DERIVED_ONLY
    assert result.evidence_plan.raw_blob_write_allowed is False
    assert result.evidence_plan.eligible_for_memory is True


def test_macos_accessibility_adapter_derives_allowed_elements_only():
    event = _accessibility_event()

    envelope = build_macos_accessibility_envelope(event)
    result = handoff_macos_accessibility_event(event)

    assert envelope.source_kind == PerceptionSourceKind.ACCESSIBILITY
    assert envelope.observation.event_type == ObservationEventType.ACCESSIBILITY_TREE
    assert envelope.route == PerceptionRoute.FIREWALL_REQUIRED
    assert envelope.raw_ref is None
    assert result.firewall.decision == FirewallDecision.MEMORY_ELIGIBLE
    assert result.evidence_plan.write_mode == EvidenceWriteMode.DERIVED_ONLY
    assert result.evidence_plan.derived_text_refs == [
        "derived://macos/accessibility/macos_ax_001"
    ]
    assert result.evidence_plan.raw_ref is None


def test_macos_accessibility_secret_preview_is_redacted_and_not_memory_eligible():
    event = _accessibility_event(
        event_id="macos_ax_secret",
        value_preview="token=CORTEX_FAKE_TOKEN_macosSECRET123",
        derived_text_ref="derived://macos/accessibility/macos_ax_secret",
    )

    result = handoff_macos_accessibility_event(event)

    assert result.firewall.decision == FirewallDecision.MASK
    assert result.evidence_plan.write_mode == EvidenceWriteMode.DERIVED_ONLY
    assert result.evidence_plan.eligible_for_memory is False
    assert result.evidence_plan.raw_ref is None
    assert "CORTEX_FAKE_TOKEN_macosSECRET123" not in result.redacted_text
    assert result.evidence_plan.derived_text_refs == [
        "derived://macos/accessibility/redacted/macos_ax_secret"
    ]


def test_macos_private_or_unpermitted_sources_discard_before_handoff():
    private_ax = _accessibility_event(
        event_id="macos_ax_private",
        private_field_detected=True,
        value_preview=None,
        derived_text_ref="derived://macos/accessibility/macos_ax_private",
    )
    denied_window = _window_event(
        event_id="macos_window_denied",
        screen_recording_permission=MacOSPermissionState.DENIED,
        derived_text_ref="derived://macos/app-window/macos_window_denied",
    )
    blocked_app = _window_event(
        event_id="macos_window_blocked",
        app_allowed=False,
        derived_text_ref="derived://macos/app-window/macos_window_blocked",
    )

    private_result = handoff_macos_accessibility_event(private_ax)
    denied_result = handoff_macos_app_window_event(denied_window)
    blocked_result = handoff_macos_app_window_event(blocked_app)

    for result in [private_result, denied_result, blocked_result]:
        assert result.envelope.route == PerceptionRoute.DISCARD
        assert result.firewall.decision == FirewallDecision.DISCARD
        assert result.evidence_plan.write_mode == EvidenceWriteMode.DISCARD
        assert result.evidence_plan.raw_ref is None
        assert result.evidence_plan.derived_text_refs == []
        assert result.evidence_plan.eligible_for_memory is False


def test_macos_adapter_shapes_reject_raw_or_private_payloads():
    with pytest.raises(ValidationError, match="cannot carry raw capture refs"):
        _window_event(raw_ref="raw://macos/window/not_allowed")

    with pytest.raises(ValidationError, match="sensitive macOS apps cannot carry"):
        _window_event(sensitive_app=True, window_title="Bank Account")

    with pytest.raises(ValidationError, match="cannot carry raw tree refs"):
        _accessibility_event(raw_tree_ref="raw://macos/ax/tree")

    with pytest.raises(ValidationError, match="private accessibility fields"):
        _accessibility_event(private_field_detected=True)
