"""Hardening receipts for the next real-capture gate."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import gettempdir

from pydantic import Field, model_validator

from cortex_memory_os.contracts import StrictModel

RAW_REF_SCAVENGER_ID = "RAW-REF-SCAVENGER-001"
RAW_REF_SCAVENGER_POLICY_REF = "policy_raw_ref_scavenger_v1"
REAL_CAPTURE_NEXT_GATE_ID = "REAL-CAPTURE-NEXT-GATE-001"
REAL_CAPTURE_NEXT_GATE_POLICY_REF = "policy_real_capture_next_gate_v1"


class RawRefScavengerReceipt(StrictModel):
    scavenger_id: str = RAW_REF_SCAVENGER_ID
    policy_ref: str = RAW_REF_SCAVENGER_POLICY_REF
    checked_at: datetime
    temp_root: str
    ttl_seconds: int = Field(ge=1, le=3600)
    scanned_count: int = Field(ge=0)
    deleted_count: int = Field(ge=0)
    retained_count: int = Field(ge=0)
    durable_storage_allowed: bool = False
    memory_write_allowed: bool = False
    raw_payloads_read: bool = False
    passed: bool

    @model_validator(mode="after")
    def enforce_cleanup_boundary(self) -> "RawRefScavengerReceipt":
        if self.scavenger_id != RAW_REF_SCAVENGER_ID:
            raise ValueError("raw ref scavenger id mismatch")
        if self.policy_ref != RAW_REF_SCAVENGER_POLICY_REF:
            raise ValueError("raw ref scavenger policy mismatch")
        if self.durable_storage_allowed or self.memory_write_allowed or self.raw_payloads_read:
            raise ValueError("raw ref scavenger cannot read payloads or enable storage/memory writes")
        if self.scanned_count != self.deleted_count + self.retained_count:
            raise ValueError("raw ref scavenger counts must balance")
        return self


class RealCaptureNextGatePlan(StrictModel):
    gate_id: str = REAL_CAPTURE_NEXT_GATE_ID
    policy_ref: str = REAL_CAPTURE_NEXT_GATE_POLICY_REF
    required_user_action: str = "click Turn On Cortex, then Screen Probe"
    prerequisites: list[str] = Field(default_factory=list)
    allowed_effects: list[str] = Field(default_factory=list)
    blocked_effects: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    durable_memory_writes_allowed: bool = False
    raw_pixel_return_allowed: bool = False
    continuous_capture_allowed: bool = False
    passed: bool

    @model_validator(mode="after")
    def enforce_next_gate_boundary(self) -> "RealCaptureNextGatePlan":
        required_prereqs = {
            "session_token_required",
            "localhost_origin_required",
            "screen_recording_preflight_required",
            "sensitive_app_filter_required",
            "raw_ref_scavenger_required",
        }
        if missing := sorted(required_prereqs.difference(self.prerequisites)):
            raise ValueError(f"next gate missing prerequisites: {missing}")
        required_blocked = {
            "continuous_capture",
            "raw_pixel_return",
            "durable_memory_write",
            "sensitive_app_capture",
            "accessibility_value_capture",
            "arbitrary_command_execution",
        }
        if missing := sorted(required_blocked.difference(self.blocked_effects)):
            raise ValueError(f"next gate missing blocked effects: {missing}")
        if (
            self.durable_memory_writes_allowed
            or self.raw_pixel_return_allowed
            or self.continuous_capture_allowed
        ):
            raise ValueError("next gate cannot enable continuous capture, raw pixels, or memory writes")
        return self


def run_raw_ref_scavenger(
    *,
    temp_root: Path | None = None,
    now: datetime | None = None,
    ttl_seconds: int = 600,
) -> RawRefScavengerReceipt:
    timestamp = now or datetime.now(UTC)
    root = temp_root or Path(gettempdir()) / "cortex" / "raw_refs"
    root.mkdir(parents=True, exist_ok=True)
    cutoff = timestamp - timedelta(seconds=ttl_seconds)
    scanned = deleted = retained = 0
    for path in root.iterdir():
        if not path.is_file():
            continue
        scanned += 1
        modified = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
        if modified < cutoff:
            path.unlink()
            deleted += 1
        else:
            retained += 1
    return RawRefScavengerReceipt(
        checked_at=timestamp,
        temp_root=str(root),
        ttl_seconds=ttl_seconds,
        scanned_count=scanned,
        deleted_count=deleted,
        retained_count=retained,
        durable_storage_allowed=False,
        memory_write_allowed=False,
        raw_payloads_read=False,
        passed=True,
    )


def build_real_capture_next_gate_plan() -> RealCaptureNextGatePlan:
    return RealCaptureNextGatePlan(
        prerequisites=[
            "session_token_required",
            "localhost_origin_required",
            "screen_recording_preflight_required",
            "sensitive_app_filter_required",
            "raw_ref_scavenger_required",
        ],
        allowed_effects=[
            "render_shadow_clicker_overlay",
            "read_permission_status",
            "capture_one_frame_in_memory",
            "return_metadata_receipt",
        ],
        blocked_effects=[
            "continuous_capture",
            "raw_pixel_return",
            "durable_memory_write",
            "sensitive_app_capture",
            "accessibility_value_capture",
            "arbitrary_command_execution",
        ],
        success_criteria=[
            "button starts display-only overlay",
            "permission bridge returns prompt-free status",
            "screen probe returns dimensions only when preflight allows",
            "receipt summary remains raw-payload-free",
        ],
        passed=True,
    )


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--temp-root", type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    receipt = run_raw_ref_scavenger(temp_root=args.temp_root)
    gate = build_real_capture_next_gate_plan()
    if args.json:
        print(
            json.dumps(
                {
                    "scavenger": receipt.model_dump(mode="json"),
                    "next_gate": gate.model_dump(mode="json"),
                },
                indent=2,
            )
        )
    else:
        print(f"{receipt.scavenger_id}: passed={receipt.passed}; deleted={receipt.deleted_count}")
        print(f"{gate.gate_id}: passed={gate.passed}")
    return 0 if receipt.passed and gate.passed else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
