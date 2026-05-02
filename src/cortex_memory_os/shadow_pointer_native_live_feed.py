"""Display-only native Shadow Pointer live-feed receipts."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import Field, model_validator

from cortex_memory_os.contracts import SourceTrust, StrictModel
from cortex_memory_os.shadow_pointer import (
    SHADOW_POINTER_LIVE_RECEIPT_POLICY_REF,
    SHADOW_POINTER_STATE_MACHINE_POLICY_REF,
    ShadowPointerLiveReceipt,
    ShadowPointerObservationMode,
    ShadowPointerState,
)

NATIVE_SHADOW_POINTER_LIVE_FEED_ID = "NATIVE-SHADOW-POINTER-LIVE-FEED-001"
NATIVE_SHADOW_POINTER_LIVE_FEED_POLICY_REF = (
    "policy_native_shadow_pointer_live_feed_v1"
)


class NativeShadowPointerLiveFeedReceipt(StrictModel):
    feed_id: str = NATIVE_SHADOW_POINTER_LIVE_FEED_ID
    generated_at: datetime
    native_surface: str = "macos_shadow_pointer_overlay"
    receipt_count: int = Field(ge=1)
    latest_state: ShadowPointerState
    latest_observation_mode: ShadowPointerObservationMode
    external_untrusted_count: int = Field(ge=0)
    memory_eligible_count: int = Field(ge=0)
    display_only: bool = True
    capture_started: bool = False
    accessibility_observer_started: bool = False
    memory_write_allowed: bool = False
    raw_ref_retained: bool = False
    raw_payload_included: bool = False
    allowed_effects: list[str] = Field(default_factory=list)
    blocked_effects: list[str] = Field(default_factory=list)
    policy_refs: tuple[str, ...] = Field(
        default=(
            NATIVE_SHADOW_POINTER_LIVE_FEED_POLICY_REF,
            SHADOW_POINTER_LIVE_RECEIPT_POLICY_REF,
            SHADOW_POINTER_STATE_MACHINE_POLICY_REF,
        )
    )

    @model_validator(mode="after")
    def keep_native_feed_display_only(self) -> NativeShadowPointerLiveFeedReceipt:
        if NATIVE_SHADOW_POINTER_LIVE_FEED_POLICY_REF not in self.policy_refs:
            raise ValueError("native live feed requires policy ref")
        if not self.display_only:
            raise ValueError("native live feed must remain display-only")
        if self.capture_started or self.accessibility_observer_started:
            raise ValueError("native live feed cannot start capture or observers")
        if self.memory_write_allowed:
            raise ValueError("native live feed cannot write memory")
        if self.raw_ref_retained or self.raw_payload_included:
            raise ValueError("native live feed cannot retain raw refs or payloads")
        allowed = set(self.allowed_effects)
        if allowed - {"render_native_overlay_frame", "render_redacted_receipt_summary"}:
            raise ValueError("native live feed allowed effects are too broad")
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
            raise ValueError(f"native live feed missing blocked effects: {missing}")
        return self


def build_native_shadow_pointer_live_feed(
    receipts: list[ShadowPointerLiveReceipt],
    *,
    now: datetime | None = None,
) -> NativeShadowPointerLiveFeedReceipt:
    if not receipts:
        raise ValueError("native live feed requires at least one live receipt")
    if any(receipt.raw_payload_included for receipt in receipts):
        raise ValueError("native live feed cannot accept raw-payload receipts")
    latest = receipts[-1]
    return NativeShadowPointerLiveFeedReceipt(
        generated_at=_ensure_utc(now or datetime.now(UTC)),
        receipt_count=len(receipts),
        latest_state=latest.state,
        latest_observation_mode=latest.observation_mode,
        external_untrusted_count=sum(
            int(
                receipt.trust_class
                in {SourceTrust.EXTERNAL_UNTRUSTED, SourceTrust.HOSTILE_UNTIL_SAFE}
            )
            for receipt in receipts
        ),
        memory_eligible_count=sum(int(receipt.memory_eligible) for receipt in receipts),
        raw_ref_retained=any(receipt.raw_ref_retained for receipt in receipts),
        raw_payload_included=any(receipt.raw_payload_included for receipt in receipts),
        allowed_effects=[
            "render_native_overlay_frame",
            "render_redacted_receipt_summary",
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
    )


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
