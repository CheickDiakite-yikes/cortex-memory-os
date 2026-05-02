"""Cross-receipt leak stress for operational dashboard payloads."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime

from pydantic import Field

from cortex_memory_os.contracts import StrictModel
from cortex_memory_os.dashboard_encrypted_index import (
    DASHBOARD_LIVE_BACKBONE_POLICY_REF,
    DashboardOperationalBackbone,
    build_dashboard_operational_backbone,
)
from cortex_memory_os.durable_synthetic_memory_receipts import (
    DURABLE_SYNTHETIC_MEMORY_RECEIPTS_POLICY_REF,
)
from cortex_memory_os.key_management import KEY_MANAGEMENT_PLAN_POLICY_REF
from cortex_memory_os.shadow_pointer_native_live_feed import (
    NATIVE_SHADOW_POINTER_LIVE_FEED_POLICY_REF,
)

RECEIPT_LEAK_STRESS_ID = "RECEIPT-LEAK-STRESS-001"
RECEIPT_LEAK_STRESS_POLICY_REF = "policy_receipt_leak_stress_v1"

_PROHIBITED_MARKERS = [
    "CORTEX_FAKE_TOKEN",
    "OPENAI_API_KEY=",
    "sk-",
    "Bearer ",
    "raw://",
    "encrypted_blob://",
    "Ignore previous instructions",
    "reveal secrets",
    "Synthetic durable memory receipt observed",
    "synthetic://durable-memory-receipt/source",
]


class ReceiptLeakStressResult(StrictModel):
    proof_id: str = RECEIPT_LEAK_STRESS_ID
    policy_ref: str = RECEIPT_LEAK_STRESS_POLICY_REF
    generated_at: datetime
    passed: bool
    checked_payload_count: int = Field(ge=1)
    prohibited_marker_count: int = Field(ge=0)
    content_redacted: bool
    source_refs_redacted: bool
    key_material_visible: bool
    raw_private_data_retained: bool
    policy_refs: list[str] = Field(
        default_factory=lambda: [
            RECEIPT_LEAK_STRESS_POLICY_REF,
            KEY_MANAGEMENT_PLAN_POLICY_REF,
            DURABLE_SYNTHETIC_MEMORY_RECEIPTS_POLICY_REF,
            NATIVE_SHADOW_POINTER_LIVE_FEED_POLICY_REF,
            DASHBOARD_LIVE_BACKBONE_POLICY_REF,
        ]
    )


def run_receipt_leak_stress(
    *, now: datetime | None = None
) -> ReceiptLeakStressResult:
    timestamp = _ensure_utc(now or datetime.now(UTC))
    backbone = build_dashboard_operational_backbone(now=timestamp)
    payloads = _payloads(backbone)
    joined = "\n".join(payloads)
    prohibited_marker_count = sum(1 for marker in _PROHIBITED_MARKERS if marker in joined)
    content_redacted = (
        backbone.encrypted_index_panel.content_redacted
        and backbone.durable_synthetic_memory_receipt.content_redacted
        and backbone.live_backbone_panel.content_redacted
    )
    source_refs_redacted = (
        backbone.encrypted_index_panel.source_refs_redacted
        and backbone.durable_synthetic_memory_receipt.source_refs_redacted
        and backbone.live_backbone_panel.source_refs_redacted
    )
    key_material_visible = (
        backbone.encrypted_index_panel.key_material_visible
        or backbone.live_backbone_panel.key_material_visible
        or backbone.key_management_plan.raw_key_material_included
    )
    raw_private_data_retained = (
        backbone.encrypted_index_panel.raw_private_data_retained
        or backbone.live_backbone_panel.raw_private_data_retained
        or backbone.durable_synthetic_memory_receipt.raw_ref_retained
        or backbone.native_live_feed.raw_ref_retained
    )
    passed = (
        prohibited_marker_count == 0
        and content_redacted
        and source_refs_redacted
        and not key_material_visible
        and not raw_private_data_retained
    )
    return ReceiptLeakStressResult(
        generated_at=timestamp,
        passed=passed,
        checked_payload_count=len(payloads),
        prohibited_marker_count=prohibited_marker_count,
        content_redacted=content_redacted,
        source_refs_redacted=source_refs_redacted,
        key_material_visible=key_material_visible,
        raw_private_data_retained=raw_private_data_retained,
    )


def _payloads(backbone: DashboardOperationalBackbone) -> list[str]:
    return [
        backbone.key_management_plan.model_dump_json(),
        backbone.encrypted_index_panel.model_dump_json(),
        backbone.native_live_feed.model_dump_json(),
        backbone.durable_synthetic_memory_receipt.model_dump_json(),
        backbone.live_backbone_panel.model_dump_json(),
    ]


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = run_receipt_leak_stress()
    if args.json:
        print(json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True))
    else:
        status = "passed" if result.passed else "failed"
        print(
            f"{RECEIPT_LEAK_STRESS_ID}: {status}; "
            f"payloads={result.checked_payload_count}; leaks={result.prohibited_marker_count}"
        )
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
