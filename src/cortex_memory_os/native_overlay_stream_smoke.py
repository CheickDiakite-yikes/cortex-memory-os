"""Manual-safe native overlay stream smoke against local live receipts."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime

from pydantic import Field, model_validator

from cortex_memory_os.contracts import SourceTrust, StrictModel
from cortex_memory_os.shadow_pointer import (
    ShadowPointerObservationMode,
    build_live_receipt,
    default_shadow_pointer_snapshot,
)
from cortex_memory_os.shadow_pointer_native_live_feed import (
    NATIVE_SHADOW_POINTER_LIVE_FEED_POLICY_REF,
    NativeShadowPointerLiveFeedReceipt,
    build_native_shadow_pointer_live_feed,
)

NATIVE_OVERLAY_STREAM_SMOKE_ID = "NATIVE-OVERLAY-STREAM-SMOKE-001"
NATIVE_OVERLAY_STREAM_SMOKE_POLICY_REF = "policy_native_overlay_stream_smoke_v1"


class NativeOverlayStreamFrame(StrictModel):
    frame_id: str = Field(min_length=1)
    sequence: int = Field(ge=1)
    state: str = Field(min_length=1)
    trust_class: str = Field(min_length=1)
    memory_eligible: bool
    raw_ref_retained: bool
    display_only: bool = True

    @model_validator(mode="after")
    def keep_frame_display_only(self) -> "NativeOverlayStreamFrame":
        if not self.display_only:
            raise ValueError("native overlay stream frames must be display-only")
        if self.raw_ref_retained:
            raise ValueError("native overlay stream frames cannot retain raw refs")
        return self


class NativeOverlayStreamSmokeResult(StrictModel):
    proof_id: str = NATIVE_OVERLAY_STREAM_SMOKE_ID
    policy_ref: str = NATIVE_OVERLAY_STREAM_SMOKE_POLICY_REF
    generated_at: datetime
    feed: NativeShadowPointerLiveFeedReceipt
    frame_count: int = Field(ge=1)
    frames: list[NativeOverlayStreamFrame]
    manual_overlay_smoke_ready: bool
    capture_started: bool = False
    accessibility_observer_started: bool = False
    memory_write_allowed: bool = False
    raw_payload_included: bool = False
    raw_ref_retained: bool = False
    allowed_effects: list[str] = Field(default_factory=list)
    blocked_effects: list[str] = Field(default_factory=list)
    policy_refs: list[str] = Field(
        default_factory=lambda: [
            NATIVE_OVERLAY_STREAM_SMOKE_POLICY_REF,
            NATIVE_SHADOW_POINTER_LIVE_FEED_POLICY_REF,
        ]
    )
    passed: bool

    @model_validator(mode="after")
    def keep_smoke_non_capturing(self) -> "NativeOverlayStreamSmokeResult":
        if NATIVE_OVERLAY_STREAM_SMOKE_POLICY_REF not in self.policy_refs:
            raise ValueError("native overlay stream smoke requires policy ref")
        if self.capture_started or self.accessibility_observer_started:
            raise ValueError("native overlay stream smoke cannot start capture or observers")
        if self.memory_write_allowed:
            raise ValueError("native overlay stream smoke cannot allow memory writes")
        if self.raw_payload_included or self.raw_ref_retained:
            raise ValueError("native overlay stream smoke cannot include raw payloads or refs")
        required_allowed = {
            "render_native_overlay_frame",
            "render_redacted_receipt_summary",
            "advance_local_receipt_stream",
        }
        if missing := sorted(required_allowed.difference(self.allowed_effects)):
            raise ValueError(f"native overlay stream smoke missing allowed effects: {missing}")
        required_blocked = {
            "start_screen_capture",
            "start_accessibility_observer",
            "write_memory",
            "retain_raw_ref",
            "execute_click",
            "type_text",
            "export_payload",
        }
        if missing := sorted(required_blocked.difference(self.blocked_effects)):
            raise ValueError(f"native overlay stream smoke missing blocked effects: {missing}")
        if self.frame_count != len(self.frames):
            raise ValueError("native overlay stream smoke frame_count mismatch")
        return self


def run_native_overlay_stream_smoke(
    *, now: datetime | None = None
) -> NativeOverlayStreamSmokeResult:
    timestamp = _timestamp(now)
    receipts = [
        build_live_receipt(
            default_shadow_pointer_snapshot(),
            observation_mode=ShadowPointerObservationMode.SESSION,
            source_trust=SourceTrust.EXTERNAL_UNTRUSTED,
            firewall_decision="ephemeral_only",
            evidence_write_mode="derived_only",
            memory_eligible=False,
            raw_ref_retained=False,
            latest_action=action,
        )
        for action in [
            "Local receipt stream boot",
            "Pointer moved over safe page",
            "Observation accepted as external evidence only",
        ]
    ]
    feed = build_native_shadow_pointer_live_feed(receipts, now=timestamp)
    frames = [
        NativeOverlayStreamFrame(
            frame_id=f"native_overlay_frame_{index}",
            sequence=index,
            state=receipt.state.value,
            trust_class=receipt.trust_class.value,
            memory_eligible=receipt.memory_eligible,
            raw_ref_retained=receipt.raw_ref_retained,
        )
        for index, receipt in enumerate(receipts, start=1)
    ]
    passed = (
        feed.display_only
        and not feed.capture_started
        and not feed.accessibility_observer_started
        and not feed.memory_write_allowed
        and feed.receipt_count == len(frames)
        and all(frame.display_only for frame in frames)
        and all(not frame.raw_ref_retained for frame in frames)
    )
    return NativeOverlayStreamSmokeResult(
        generated_at=timestamp,
        feed=feed,
        frame_count=len(frames),
        frames=frames,
        manual_overlay_smoke_ready=True,
        allowed_effects=[
            "render_native_overlay_frame",
            "render_redacted_receipt_summary",
            "advance_local_receipt_stream",
        ],
        blocked_effects=[
            "start_screen_capture",
            "start_accessibility_observer",
            "write_memory",
            "retain_raw_ref",
            "execute_click",
            "type_text",
            "export_payload",
        ],
        passed=passed,
    )


def _timestamp(now: datetime | None) -> datetime:
    timestamp = now or datetime.now(UTC)
    if timestamp.tzinfo is None:
        return timestamp.replace(tzinfo=UTC)
    return timestamp.astimezone(UTC)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = run_native_overlay_stream_smoke()
    if args.json:
        print(json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True))
    else:
        print(
            f"{NATIVE_OVERLAY_STREAM_SMOKE_ID}: "
            f"{'passed' if result.passed else 'failed'}; frames={result.frame_count}"
        )
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
