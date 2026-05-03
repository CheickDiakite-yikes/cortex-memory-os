from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from cortex_memory_os.capture_readiness_ladder import (
    CAPTURE_READINESS_LADDER_ID,
    CAPTURE_READINESS_LADDER_POLICY_REF,
    CaptureReadinessLadderPanel,
    build_fixture_capture_readiness_ladder,
)


def test_capture_readiness_ladder_blocks_probe_until_permissions_are_ready() -> None:
    panel = build_fixture_capture_readiness_ladder(
        permissions_ready=False,
        now=datetime(2026, 5, 2, 21, 0, tzinfo=UTC),
    )

    assert panel.ladder_id == CAPTURE_READINESS_LADDER_ID
    assert panel.policy_ref == CAPTURE_READINESS_LADDER_POLICY_REF
    assert len(panel.steps) == 10
    assert [step.order for step in panel.steps] == list(range(1, 11))
    assert panel.ready_count >= 6
    assert panel.blocked_count == 2
    assert panel.planned_count == 1
    assert panel.watching_count == 1
    assert panel.next_step_label == "Permission preflight"
    assert panel.can_demo_now is True
    assert panel.can_probe_now is False
    assert panel.can_real_capture_now is False
    assert panel.display_only is True
    assert panel.raw_payloads_included is False
    assert panel.raw_ref_retained is False
    assert panel.memory_write_allowed is False
    assert panel.external_effect_enabled is False
    assert "raw_pixel_return" in panel.blocked_effects
    assert "durable_memory_write" in panel.blocked_effects
    assert all(not step.raw_payloads_included for step in panel.steps)
    assert all(not step.memory_write_allowed for step in panel.steps)
    assert all(not step.external_effect_enabled for step in panel.steps)


def test_capture_readiness_ladder_allows_metadata_probe_after_permissions() -> None:
    panel = build_fixture_capture_readiness_ladder(
        permissions_ready=True,
        now=datetime(2026, 5, 2, 21, 5, tzinfo=UTC),
    )

    screen_probe = next(step for step in panel.steps if step.step_id == "screen_probe")

    assert panel.blocked_count == 0
    assert panel.can_demo_now is True
    assert panel.can_probe_now is True
    assert panel.can_real_capture_now is True
    assert screen_probe.status == "ready"
    assert "metadata frame" in screen_probe.proof
    assert panel.next_step_label == "Receipt audit"


def test_capture_readiness_ladder_rejects_raw_payload_or_missing_steps() -> None:
    panel = build_fixture_capture_readiness_ladder(
        permissions_ready=False,
        now=datetime(2026, 5, 2, 21, 10, tzinfo=UTC),
    )
    payload = panel.model_dump()
    payload["raw_payloads_included"] = True

    with pytest.raises(ValidationError, match="side effects"):
        CaptureReadinessLadderPanel.model_validate(payload)

    payload = panel.model_dump()
    payload["steps"] = payload["steps"][:-1]

    with pytest.raises(ValidationError):
        CaptureReadinessLadderPanel.model_validate(payload)
