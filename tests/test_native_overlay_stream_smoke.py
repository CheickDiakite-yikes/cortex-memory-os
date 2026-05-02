from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from cortex_memory_os.native_overlay_stream_smoke import (
    NATIVE_OVERLAY_STREAM_SMOKE_ID,
    NATIVE_OVERLAY_STREAM_SMOKE_POLICY_REF,
    NativeOverlayStreamSmokeResult,
    run_native_overlay_stream_smoke,
)


NOW = datetime(2026, 5, 2, 16, 20, tzinfo=UTC)


def test_native_overlay_stream_smoke_feeds_display_only_receipts():
    result = run_native_overlay_stream_smoke(now=NOW)
    payload = result.model_dump_json()

    assert result.proof_id == NATIVE_OVERLAY_STREAM_SMOKE_ID
    assert result.policy_ref == NATIVE_OVERLAY_STREAM_SMOKE_POLICY_REF
    assert result.passed is True
    assert result.manual_overlay_smoke_ready is True
    assert result.frame_count == 3
    assert result.feed.receipt_count == 3
    assert result.feed.display_only is True
    assert result.feed.capture_started is False
    assert result.feed.accessibility_observer_started is False
    assert result.feed.memory_write_allowed is False
    assert all(frame.display_only for frame in result.frames)
    assert all(not frame.memory_eligible for frame in result.frames)
    assert all(not frame.raw_ref_retained for frame in result.frames)
    assert "raw://" not in payload
    assert "encrypted_blob://" not in payload


def test_native_overlay_stream_smoke_rejects_capture_or_raw_refs():
    result = run_native_overlay_stream_smoke(now=NOW)

    with pytest.raises(ValidationError, match="cannot start capture"):
        NativeOverlayStreamSmokeResult.model_validate(
            result.model_dump() | {"capture_started": True}
        )

    with pytest.raises(ValidationError, match="cannot include raw"):
        NativeOverlayStreamSmokeResult.model_validate(
            result.model_dump() | {"raw_ref_retained": True}
        )
