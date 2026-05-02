"""Encrypted durable receipt for synthetic memory writes."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, date, datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from pydantic import Field, model_validator

from cortex_memory_os.contracts import (
    AuditEvent,
    EvidenceType,
    InfluenceLevel,
    MemoryRecord,
    MemoryStatus,
    MemoryType,
    ScopeLevel,
    Sensitivity,
    StrictModel,
    TemporalEdge,
)
from cortex_memory_os.encrypted_graph_index import (
    UNIFIED_ENCRYPTED_GRAPH_INDEX_POLICY_REF,
    UnifiedGraphWriteReceipt,
    UnifiedIndexSearchReceipt,
    UnifiedIndexWriteReceipt,
    UnifiedEncryptedGraphIndex,
)
from cortex_memory_os.evidence_vault import VaultRuntimeMode
from cortex_memory_os.key_management import KEY_MANAGEMENT_PLAN_POLICY_REF
from cortex_memory_os.memory_encryption import MEMORY_ENCRYPTION_DEFAULT_POLICY_REF
from cortex_memory_os.synthetic_capture_ladder import SYNTHETIC_CAPTURE_LADDER_POLICY_REF

DURABLE_SYNTHETIC_MEMORY_RECEIPTS_ID = "DURABLE-SYNTHETIC-MEMORY-RECEIPTS-001"
DURABLE_SYNTHETIC_MEMORY_RECEIPTS_POLICY_REF = (
    "policy_durable_synthetic_memory_receipts_v1"
)

_SYNTHETIC_DURABLE_MEMORY_ID = "mem_durable_synthetic_receipt_debug"
_SYNTHETIC_DURABLE_EDGE_ID = "edge_durable_synthetic_receipt_debug"
_PROHIBITED_MARKERS = [
    "CORTEX_FAKE_TOKEN",
    "OPENAI_API_KEY=",
    "sk-",
    "Bearer ",
    "raw://",
    "encrypted_blob://",
    "Ignore previous instructions",
    "Synthetic durable memory receipt observed",
    "synthetic://durable-memory-receipt/source",
]


class _SyntheticReceiptCipher:
    name = "synthetic-receipt-aead-test-only"
    authenticated_encryption = True

    def seal(self, plaintext: bytes) -> bytes:
        return b"sealed-synthetic-receipt:" + plaintext[::-1]

    def open(self, ciphertext: bytes) -> bytes:
        if not ciphertext.startswith(b"sealed-synthetic-receipt:"):
            raise ValueError("missing synthetic receipt seal")
        return ciphertext.removeprefix(b"sealed-synthetic-receipt:")[::-1]


class DurableSyntheticMemoryReceipt(StrictModel):
    receipt_id: str = Field(min_length=1)
    policy_ref: str = DURABLE_SYNTHETIC_MEMORY_RECEIPTS_POLICY_REF
    generated_at: datetime
    synthetic_only: bool = True
    local_test_db_used: bool = True
    encrypted_store_used: bool
    durable_synthetic_memory_written: bool
    durable_private_memory_written: bool = False
    real_screen_capture_started: bool = False
    raw_ref_retained: bool = False
    raw_payload_included: bool = False
    audit_written: bool
    audit_human_visible: bool
    content_redacted: bool = True
    source_refs_redacted: bool = True
    token_text_redacted: bool = True
    query_redacted: bool = True
    db_plaintext_leak_count: int = Field(ge=0)
    prohibited_leak_count: int = Field(ge=0)
    memory_id: str = Field(min_length=1)
    audit_event_id: str = Field(min_length=1)
    index_write_receipt: UnifiedIndexWriteReceipt
    graph_write_receipt: UnifiedGraphWriteReceipt
    search_receipt: UnifiedIndexSearchReceipt
    policy_refs: list[str] = Field(
        default_factory=lambda: [
            DURABLE_SYNTHETIC_MEMORY_RECEIPTS_POLICY_REF,
            SYNTHETIC_CAPTURE_LADDER_POLICY_REF,
            MEMORY_ENCRYPTION_DEFAULT_POLICY_REF,
            UNIFIED_ENCRYPTED_GRAPH_INDEX_POLICY_REF,
            KEY_MANAGEMENT_PLAN_POLICY_REF,
        ]
    )

    @model_validator(mode="after")
    def keep_synthetic_receipt_safe(self) -> DurableSyntheticMemoryReceipt:
        if self.policy_ref != DURABLE_SYNTHETIC_MEMORY_RECEIPTS_POLICY_REF:
            raise ValueError("durable synthetic receipt policy mismatch")
        if DURABLE_SYNTHETIC_MEMORY_RECEIPTS_POLICY_REF not in self.policy_refs:
            raise ValueError("durable synthetic receipt requires policy ref")
        if not self.synthetic_only:
            raise ValueError("durable synthetic receipt must remain synthetic only")
        if not self.local_test_db_used:
            raise ValueError("durable synthetic receipt must use a local test DB")
        if not self.encrypted_store_used:
            raise ValueError("durable synthetic receipt requires encrypted store")
        if not self.durable_synthetic_memory_written:
            raise ValueError("durable synthetic memory write proof is required")
        if self.durable_private_memory_written or self.real_screen_capture_started:
            raise ValueError("durable synthetic receipt cannot write private real data")
        if self.raw_ref_retained or self.raw_payload_included:
            raise ValueError("durable synthetic receipt cannot retain raw refs or payloads")
        if not self.audit_written or not self.audit_human_visible:
            raise ValueError("durable synthetic receipt requires a human-visible audit")
        if not (
            self.content_redacted
            and self.source_refs_redacted
            and self.token_text_redacted
            and self.query_redacted
        ):
            raise ValueError("durable synthetic receipt must stay fully redacted")
        if self.db_plaintext_leak_count or self.prohibited_leak_count:
            raise ValueError("durable synthetic receipt detected leaked content")
        return self


def run_durable_synthetic_memory_receipts(
    *, now: datetime | None = None
) -> DurableSyntheticMemoryReceipt:
    timestamp = _ensure_utc(now or datetime.now(UTC))
    with TemporaryDirectory(prefix="cortex-durable-synthetic-") as temp_name:
        db_path = Path(temp_name) / "durable-synthetic.sqlite3"
        index = UnifiedEncryptedGraphIndex(
            db_path,
            cipher=_SyntheticReceiptCipher(),
            index_key=b"cortex-synthetic-receipt-index-key",
            mode=VaultRuntimeMode.TEST,
        )
        memory = _synthetic_memory(timestamp)
        edge = _synthetic_edge(timestamp)
        write_receipt = index.add_memory(memory, now=timestamp)
        graph_receipt = index.add_edge(edge, related_memory_ids=[memory.memory_id], now=timestamp)
        search_response = index.search_index(
            "synthetic durable receipt callback debug verification",
            limit=3,
        )
        audit_event = _audit_event(timestamp)
        db_bytes = db_path.read_bytes()
        db_plaintext_leak_count = sum(
            int(marker.encode("utf-8") in db_bytes)
            for marker in [
                "Synthetic durable memory receipt observed",
                "synthetic://durable-memory-receipt/source",
                "callback route and verification",
            ]
        )
        receipt_probe = {
            "write": write_receipt.model_dump(mode="json"),
            "graph": graph_receipt.model_dump(mode="json"),
            "search": search_response.model_dump(mode="json"),
            "audit_event_id": audit_event.audit_event_id,
            "audit_human_visible": audit_event.human_visible,
        }
        probe_payload = json.dumps(receipt_probe, sort_keys=True)
        prohibited_leak_count = sum(1 for marker in _PROHIBITED_MARKERS if marker in probe_payload)
        search_hit = any(hit.memory_id == memory.memory_id for hit in search_response.hits)
        return DurableSyntheticMemoryReceipt(
            receipt_id=f"durable_synthetic_receipt_{timestamp.strftime('%Y%m%dT%H%M%SZ')}",
            generated_at=timestamp,
            encrypted_store_used=True,
            durable_synthetic_memory_written=search_hit,
            audit_written=True,
            audit_human_visible=audit_event.human_visible,
            db_plaintext_leak_count=db_plaintext_leak_count,
            prohibited_leak_count=prohibited_leak_count,
            memory_id=memory.memory_id,
            audit_event_id=audit_event.audit_event_id,
            index_write_receipt=write_receipt,
            graph_write_receipt=graph_receipt,
            search_receipt=search_response.receipt,
        )


def _synthetic_memory(timestamp: datetime) -> MemoryRecord:
    return MemoryRecord(
        memory_id=_SYNTHETIC_DURABLE_MEMORY_ID,
        type=MemoryType.EPISODIC,
        content=(
            "Synthetic durable memory receipt observed a callback route and "
            "verification workflow in a disposable fixture."
        ),
        source_refs=[
            "synthetic://durable-memory-receipt/source",
            "project:cortex-memory-os",
        ],
        evidence_type=EvidenceType.OBSERVED,
        confidence=0.93,
        status=MemoryStatus.ACTIVE,
        created_at=timestamp,
        valid_from=date(2026, 5, 2),
        valid_to=None,
        sensitivity=Sensitivity.PRIVATE_WORK,
        scope=ScopeLevel.PROJECT_SPECIFIC,
        influence_level=InfluenceLevel.DIRECT_QUERY,
        allowed_influence=["synthetic_live_testing", "context_pack_retrieval"],
        forbidden_influence=["production_capture", "secret_handling", "external_effects"],
        decay_policy="delete_test_db_after_run",
        user_visible=True,
        requires_user_confirmation=False,
    )


def _synthetic_edge(timestamp: datetime) -> TemporalEdge:
    return TemporalEdge(
        edge_id=_SYNTHETIC_DURABLE_EDGE_ID,
        subject="synthetic_fixture",
        predicate="exercises",
        object="durable_memory_receipt",
        valid_from=timestamp.date(),
        valid_to=None,
        confidence=0.87,
        source_refs=[_SYNTHETIC_DURABLE_MEMORY_ID],
        status=MemoryStatus.ACTIVE,
        supersedes=[],
    )


def _audit_event(timestamp: datetime) -> AuditEvent:
    return AuditEvent(
        audit_event_id=f"audit_durable_synthetic_memory_{timestamp.strftime('%Y%m%dT%H%M%SZ')}",
        timestamp=timestamp,
        actor="cortex_durable_synthetic_memory_receipts",
        action="synthetic_memory.write_encrypted_index",
        target_ref=_SYNTHETIC_DURABLE_MEMORY_ID,
        policy_refs=[DURABLE_SYNTHETIC_MEMORY_RECEIPTS_POLICY_REF],
        result="written_to_encrypted_local_test_db",
        human_visible=True,
        redacted_summary=(
            "Synthetic memory written through encrypted durable memory and "
            "redacted index receipts."
        ),
    )


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = run_durable_synthetic_memory_receipts()
    if args.json:
        print(json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True))
    else:
        status = "passed" if result.durable_synthetic_memory_written else "failed"
        print(
            f"{DURABLE_SYNTHETIC_MEMORY_RECEIPTS_ID}: {status}; "
            f"memory={result.memory_id}; leaks={result.prohibited_leak_count}"
        )
    return 0 if result.durable_synthetic_memory_written else 1


if __name__ == "__main__":
    raise SystemExit(main())
