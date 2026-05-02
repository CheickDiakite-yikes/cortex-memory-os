from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta

from cortex_memory_os.real_capture_hardening import (
    RAW_REF_SCAVENGER_ID,
    REAL_CAPTURE_NEXT_GATE_ID,
    build_real_capture_next_gate_plan,
    run_raw_ref_scavenger,
)


def test_raw_ref_scavenger_deletes_expired_files_without_reading_payloads(tmp_path) -> None:
    now = datetime(2026, 5, 2, 19, 0, tzinfo=UTC)
    expired = tmp_path / "expired.raw"
    fresh = tmp_path / "fresh.raw"
    expired.write_text("do-not-read-expired")
    fresh.write_text("do-not-read-fresh")
    old_timestamp = (now - timedelta(seconds=900)).timestamp()
    fresh_timestamp = (now - timedelta(seconds=30)).timestamp()
    os.utime(expired, (old_timestamp, old_timestamp))
    os.utime(fresh, (fresh_timestamp, fresh_timestamp))

    receipt = run_raw_ref_scavenger(temp_root=tmp_path, now=now, ttl_seconds=600)

    assert receipt.scavenger_id == RAW_REF_SCAVENGER_ID
    assert receipt.passed
    assert receipt.scanned_count == 2
    assert receipt.deleted_count == 1
    assert receipt.retained_count == 1
    assert not expired.exists()
    assert fresh.exists()
    assert not receipt.raw_payloads_read
    assert not receipt.durable_storage_allowed
    assert not receipt.memory_write_allowed


def test_real_capture_next_gate_blocks_continuous_capture_and_memory_writes() -> None:
    plan = build_real_capture_next_gate_plan()

    assert plan.gate_id == REAL_CAPTURE_NEXT_GATE_ID
    assert plan.passed
    assert "session_token_required" in plan.prerequisites
    assert "screen_recording_preflight_required" in plan.prerequisites
    assert "capture_one_frame_in_memory" in plan.allowed_effects
    assert "continuous_capture" in plan.blocked_effects
    assert "raw_pixel_return" in plan.blocked_effects
    assert "durable_memory_write" in plan.blocked_effects
    assert not plan.continuous_capture_allowed
    assert not plan.raw_pixel_return_allowed
    assert not plan.durable_memory_writes_allowed
