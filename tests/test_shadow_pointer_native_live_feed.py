from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from cortex_memory_os.contracts import SourceTrust
from cortex_memory_os.shadow_pointer import (
    ShadowPointerObservationMode,
    build_live_receipt,
    default_shadow_pointer_snapshot,
)
from cortex_memory_os.shadow_pointer_native_live_feed import (
    NATIVE_SHADOW_POINTER_LIVE_FEED_ID,
    NATIVE_SHADOW_POINTER_LIVE_FEED_POLICY_REF,
    NativeShadowPointerLiveFeedReceipt,
    build_native_shadow_pointer_live_feed,
)


def test_native_shadow_pointer_live_feed_is_display_only():
    receipt = build_live_receipt(
        default_shadow_pointer_snapshot(),
        observation_mode=ShadowPointerObservationMode.SESSION,
        source_trust=SourceTrust.EXTERNAL_UNTRUSTED,
        firewall_decision="ephemeral_only",
        evidence_write_mode="derived_only",
        memory_eligible=False,
        raw_ref_retained=False,
        latest_action="Real page observation",
    )

    feed = build_native_shadow_pointer_live_feed(
        [receipt],
        now=datetime(2026, 5, 2, 12, 0, tzinfo=UTC),
    )

    assert feed.feed_id == NATIVE_SHADOW_POINTER_LIVE_FEED_ID
    assert NATIVE_SHADOW_POINTER_LIVE_FEED_POLICY_REF in feed.policy_refs
    assert feed.display_only
    assert feed.receipt_count == 1
    assert feed.external_untrusted_count == 1
    assert feed.memory_eligible_count == 0
    assert not feed.capture_started
    assert not feed.accessibility_observer_started
    assert not feed.memory_write_allowed
    assert not feed.raw_ref_retained
    assert not feed.raw_payload_included
    assert "start_screen_capture" in feed.blocked_effects
    assert "write_memory" in feed.blocked_effects


def test_native_shadow_pointer_live_feed_rejects_effect_expansion():
    with pytest.raises(ValidationError, match="allowed effects"):
        NativeShadowPointerLiveFeedReceipt(
            generated_at=datetime(2026, 5, 2, 12, 0, tzinfo=UTC),
            receipt_count=1,
            latest_state="observing",
            latest_observation_mode="session",
            external_untrusted_count=0,
            memory_eligible_count=0,
            allowed_effects=["render_native_overlay_frame", "execute_click"],
            blocked_effects=[
                "start_screen_capture",
                "start_accessibility_observer",
                "write_memory",
                "retain_raw_ref",
                "execute_click",
                "type_text",
                "export_payload",
            ],
        )
