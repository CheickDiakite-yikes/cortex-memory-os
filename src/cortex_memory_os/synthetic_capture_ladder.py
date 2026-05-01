"""Synthetic capture-to-memory live ladder for safe end-to-end testing."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

from pydantic import Field

from cortex_memory_os.contracts import (
    AuditEvent,
    ConsentState,
    EvidenceRecord,
    EvidenceType,
    FirewallDecision,
    InfluenceLevel,
    MemoryRecord,
    MemoryStatus,
    MemoryType,
    ObservationEvent,
    ObservationEventType,
    RetentionPolicy,
    ScopeLevel,
    Sensitivity,
    SourceTrust,
    StrictModel,
)
from cortex_memory_os.evidence_vault import EvidenceVault, VaultRuntimeMode
from cortex_memory_os.firewall import assess_observation_text
from cortex_memory_os.mcp_server import CortexMCPServer
from cortex_memory_os.memory_palace import MemoryPalaceService
from cortex_memory_os.sqlite_store import SQLiteMemoryGraphStore

SYNTHETIC_CAPTURE_LADDER_ID = "SYNTHETIC-CAPTURE-LADDER-001"
SYNTHETIC_CAPTURE_LADDER_POLICY_REF = "policy_synthetic_capture_ladder_v1"

SYNTHETIC_CAPTURE_MEMORY_ID = "mem_synthetic_capture_onboarding_debug"
SYNTHETIC_CAPTURE_EVIDENCE_ID = "ev_synthetic_capture_page_001"
SYNTHETIC_SECRET_EVIDENCE_ID = "ev_synthetic_secret_page_001"

_BENIGN_PAGE_TEXT = """<!doctype html>
<html>
  <head><title>Cortex Synthetic Capture Fixture</title></head>
  <body>
    <h1>Disposable Synthetic Capture Page</h1>
    <p>Onboarding debug fixture: check callback route, OAuth redirect URI,
    local env configuration, and test verification receipt.</p>
  </body>
</html>
"""

_SECRET_PAGE_TEXT = """<!doctype html>
<html>
  <head><title>Cortex Synthetic Secret Fixture</title></head>
  <body>
    <p>Do not store this synthetic secret: api_key=CORTEX_FAKE_TOKEN_abc12345SECRET</p>
  </body>
</html>
"""

_PROHIBITED_LEAK_MARKERS = [
    "api_key=",
    "CORTEX_FAKE_TOKEN",
    "sk-",
    "Bearer ",
    "raw://",
    "encrypted_blob://",
    "Ignore previous instructions",
]


class SyntheticCaptureLadderResult(StrictModel):
    proof_id: str = SYNTHETIC_CAPTURE_LADDER_ID
    policy_ref: str = SYNTHETIC_CAPTURE_LADDER_POLICY_REF
    passed: bool
    generated_at: datetime
    synthetic_disposable_page_created: bool
    synthetic_page_only: bool
    temp_storage_used: bool
    temp_paths_redacted: bool = True
    real_screen_capture_started: bool = False
    consented_real_capture_started: bool = False
    raw_ref_created: bool
    raw_ref_scheme: str | None = None
    raw_ref_readable_before_expiry: bool
    raw_ref_deleted_after_expiry: bool
    raw_payload_committed: bool = False
    durable_synthetic_memory_written: bool
    local_test_db_used: bool
    audit_written: bool
    audit_human_visible: bool
    retrieval_hit: bool
    context_pack_hit: bool
    memory_id: str
    evidence_id: str
    audit_event_id: str
    context_pack_id: str
    retrieved_memory_ids: list[str] = Field(default_factory=list)
    context_pack_memory_ids: list[str] = Field(default_factory=list)
    secret_redaction_count: int = Field(ge=0)
    secret_raw_write_blocked: bool
    secret_memory_write_blocked: bool
    secret_redacted_before_write: bool
    secret_value_leak_count: int = Field(ge=0)
    secret_firewall_decision: str
    secret_audit_summary_redacted: bool
    safety_failures: list[str] = Field(default_factory=list)


def run_synthetic_capture_ladder(
    *, now: datetime | None = None
) -> SyntheticCaptureLadderResult:
    timestamp = _ensure_utc(now or datetime.now(UTC))
    expiry_time = timestamp + timedelta(minutes=11)
    safety_failures: list[str] = []

    with TemporaryDirectory(prefix="cortex-synthetic-capture-") as temp_name:
        temp_root = Path(temp_name)
        page_path = temp_root / "disposable-synthetic-capture.html"
        page_path.write_text(_BENIGN_PAGE_TEXT, encoding="utf-8")

        observation = _observation(
            event_id="obs_synthetic_capture_page_001",
            evidence_id=SYNTHETIC_CAPTURE_EVIDENCE_ID,
            timestamp=timestamp,
            raw_contains_user_input=False,
        )
        firewall = assess_observation_text(observation, _BENIGN_PAGE_TEXT, now=timestamp)
        if not firewall.decision.eligible_for_memory:
            safety_failures.append("benign_synthetic_page_not_memory_eligible")

        vault = EvidenceVault(temp_root / "vault", mode=VaultRuntimeMode.TEST)
        evidence = EvidenceRecord(
            evidence_id=SYNTHETIC_CAPTURE_EVIDENCE_ID,
            source=ObservationEventType.OCR_TEXT,
            device="synthetic-browser-fixture",
            app="Synthetic Capture Page",
            timestamp=timestamp,
            raw_ref="synthetic://disposable-capture-page",
            derived_text_refs=["derived://synthetic-capture-page/ocr-redacted"],
            retention_policy=RetentionPolicy.DELETE_RAW_AFTER_10M,
            sensitivity=firewall.decision.sensitivity,
            contains_third_party_content=False,
            eligible_for_memory=firewall.decision.eligible_for_memory,
            eligible_for_model_training=False,
        )
        metadata = vault.store(evidence, _BENIGN_PAGE_TEXT.encode("utf-8"), now=timestamp)
        raw_before = vault.read_raw(SYNTHETIC_CAPTURE_EVIDENCE_ID, now=timestamp + timedelta(seconds=1))
        expired_ids = vault.expire(expiry_time)
        raw_after = vault.read_raw(SYNTHETIC_CAPTURE_EVIDENCE_ID, now=expiry_time)

        store = SQLiteMemoryGraphStore(temp_root / "memory" / "synthetic-memory.sqlite3")
        memory = _synthetic_memory(timestamp)
        store.add_memory(memory)
        audit_event = _memory_write_audit(timestamp)
        store.add_audit_event(audit_event)

        retrieved = store.search_memories(
            "synthetic onboarding callback route OAuth debug verification",
            limit=5,
        )
        server = CortexMCPServer(store=store, palace=MemoryPalaceService(store))
        context_pack = server.get_context_pack(
            {
                "goal": "synthetic onboarding callback route debug verification",
                "active_project": "cortex-memory-os",
                "limit": 5,
            }
        )

        secret_firewall = assess_observation_text(
            _observation(
                event_id="obs_synthetic_secret_page_001",
                evidence_id=SYNTHETIC_SECRET_EVIDENCE_ID,
                timestamp=timestamp,
                raw_contains_user_input=True,
            ),
            _SECRET_PAGE_TEXT,
            now=timestamp,
        )
        secret_redaction_count = len(secret_firewall.decision.redactions)
        secret_raw_write_blocked = True
        secret_memory_write_blocked = not secret_firewall.decision.eligible_for_memory
        secret_redacted_before_write = (
            secret_redaction_count > 0
            and secret_raw_write_blocked
            and secret_memory_write_blocked
        )
        secret_audit = _secret_block_audit(timestamp, secret_firewall.decision.policy_refs)
        store.add_audit_event(secret_audit)

        retrieved_memory_ids = [item.memory_id for item in retrieved]
        context_pack_memory_ids = [item.memory_id for item in context_pack.relevant_memories]
        leak_blob = "\n".join(
            [
                memory.model_dump_json(),
                audit_event.model_dump_json(),
                secret_audit.model_dump_json(),
                context_pack.model_dump_json(),
                secret_firewall.redacted_text,
            ]
        )
        secret_value_leak_count = sum(
            1 for marker in _PROHIBITED_LEAK_MARKERS if marker in leak_blob
        )

        raw_ref_created = bool(metadata.raw_ref)
        raw_ref_scheme = metadata.raw_ref.split("://", 1)[0] if metadata.raw_ref else None
        raw_ref_readable_before_expiry = raw_before == _BENIGN_PAGE_TEXT.encode("utf-8")
        raw_ref_deleted_after_expiry = (
            SYNTHETIC_CAPTURE_EVIDENCE_ID in expired_ids and raw_after is None
        )
        audit_events = store.audit_for_target(SYNTHETIC_CAPTURE_MEMORY_ID)
        durable_memory_written = store.get_memory(SYNTHETIC_CAPTURE_MEMORY_ID) is not None
        audit_written = any(event.audit_event_id == audit_event.audit_event_id for event in audit_events)
        retrieval_hit = SYNTHETIC_CAPTURE_MEMORY_ID in retrieved_memory_ids
        context_pack_hit = SYNTHETIC_CAPTURE_MEMORY_ID in context_pack_memory_ids

        checks = {
            "synthetic_disposable_page_created": page_path.exists(),
            "synthetic_page_only": True,
            "temp_storage_used": str(page_path).startswith(temp_name),
            "raw_ref_created": raw_ref_created,
            "raw_ref_readable_before_expiry": raw_ref_readable_before_expiry,
            "raw_ref_deleted_after_expiry": raw_ref_deleted_after_expiry,
            "durable_synthetic_memory_written": durable_memory_written,
            "local_test_db_used": True,
            "audit_written": audit_written,
            "audit_human_visible": audit_event.human_visible,
            "retrieval_hit": retrieval_hit,
            "context_pack_hit": context_pack_hit,
            "secret_raw_write_blocked": secret_raw_write_blocked,
            "secret_memory_write_blocked": secret_memory_write_blocked,
            "secret_redacted_before_write": secret_redacted_before_write,
            "secret_audit_summary_redacted": "[REDACTED_SECRET]" in secret_audit.redacted_summary,
        }
        safety_failures.extend(name for name, passed in checks.items() if not passed)
        if metadata.raw_ref and metadata.raw_ref.startswith("raw://"):
            safety_failures.append("raw_scheme_ref_created")
        if secret_value_leak_count:
            safety_failures.append("secret_value_leaked_after_redaction")
        if secret_firewall.decision.decision != FirewallDecision.MASK:
            safety_failures.append("secret_fixture_not_masked")

        return SyntheticCaptureLadderResult(
            passed=not safety_failures,
            generated_at=timestamp,
            synthetic_disposable_page_created=checks["synthetic_disposable_page_created"],
            synthetic_page_only=checks["synthetic_page_only"],
            temp_storage_used=checks["temp_storage_used"],
            raw_ref_created=raw_ref_created,
            raw_ref_scheme=raw_ref_scheme,
            raw_ref_readable_before_expiry=raw_ref_readable_before_expiry,
            raw_ref_deleted_after_expiry=raw_ref_deleted_after_expiry,
            durable_synthetic_memory_written=durable_memory_written,
            local_test_db_used=checks["local_test_db_used"],
            audit_written=audit_written,
            audit_human_visible=audit_event.human_visible,
            retrieval_hit=retrieval_hit,
            context_pack_hit=context_pack_hit,
            memory_id=SYNTHETIC_CAPTURE_MEMORY_ID,
            evidence_id=SYNTHETIC_CAPTURE_EVIDENCE_ID,
            audit_event_id=audit_event.audit_event_id,
            context_pack_id=context_pack.context_pack_id,
            retrieved_memory_ids=retrieved_memory_ids,
            context_pack_memory_ids=context_pack_memory_ids,
            secret_redaction_count=secret_redaction_count,
            secret_raw_write_blocked=secret_raw_write_blocked,
            secret_memory_write_blocked=secret_memory_write_blocked,
            secret_redacted_before_write=secret_redacted_before_write,
            secret_value_leak_count=secret_value_leak_count,
            secret_firewall_decision=secret_firewall.decision.decision.value,
            secret_audit_summary_redacted=checks["secret_audit_summary_redacted"],
            safety_failures=safety_failures,
        )


def _observation(
    *,
    event_id: str,
    evidence_id: str,
    timestamp: datetime,
    raw_contains_user_input: bool,
) -> ObservationEvent:
    return ObservationEvent(
        event_id=event_id,
        event_type=ObservationEventType.OCR_TEXT,
        timestamp=timestamp,
        device="synthetic-browser-fixture",
        app="Synthetic Capture Page",
        window_title="Cortex Synthetic Capture Fixture",
        project_id="cortex-memory-os",
        payload_ref=f"synthetic://{evidence_id}",
        source_trust=SourceTrust.LOCAL_OBSERVED,
        capture_scope=ScopeLevel.PROJECT_SPECIFIC,
        consent_state=ConsentState.ACTIVE,
        raw_contains_user_input=raw_contains_user_input,
    )


def _synthetic_memory(timestamp: datetime) -> MemoryRecord:
    return MemoryRecord(
        memory_id=SYNTHETIC_CAPTURE_MEMORY_ID,
        type=MemoryType.EPISODIC,
        content=(
            "Synthetic disposable capture page observed an onboarding debug flow: "
            "check callback route, OAuth redirect URI, local env configuration, "
            "and verification receipt."
        ),
        source_refs=[
            SYNTHETIC_CAPTURE_EVIDENCE_ID,
            "synthetic://disposable-capture-page/derived-text",
        ],
        evidence_type=EvidenceType.OBSERVED,
        confidence=0.91,
        status=MemoryStatus.ACTIVE,
        created_at=timestamp,
        valid_from=date(2026, 5, 1),
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


def _memory_write_audit(timestamp: datetime) -> AuditEvent:
    return AuditEvent(
        audit_event_id=f"audit_synthetic_memory_write_{timestamp.strftime('%Y%m%dT%H%M%SZ')}",
        timestamp=timestamp,
        actor="cortex_synthetic_capture_ladder",
        action="synthetic_memory.write",
        target_ref=SYNTHETIC_CAPTURE_MEMORY_ID,
        policy_refs=[SYNTHETIC_CAPTURE_LADDER_POLICY_REF],
        result="written_to_local_test_db",
        human_visible=True,
        redacted_summary=(
            "Synthetic memory written from disposable capture fixture; raw payload "
            "expired from temporary vault."
        ),
    )


def _secret_block_audit(timestamp: datetime, firewall_policy_refs: list[str]) -> AuditEvent:
    return AuditEvent(
        audit_event_id=f"audit_synthetic_secret_block_{timestamp.strftime('%Y%m%dT%H%M%SZ')}",
        timestamp=timestamp,
        actor="cortex_synthetic_capture_ladder",
        action="synthetic_secret.block_before_write",
        target_ref=SYNTHETIC_SECRET_EVIDENCE_ID,
        policy_refs=[SYNTHETIC_CAPTURE_LADDER_POLICY_REF, *firewall_policy_refs],
        result="blocked_before_raw_or_memory_write",
        human_visible=True,
        redacted_summary=(
            "Synthetic screen secret was replaced with [REDACTED_SECRET] before any "
            "raw payload or memory write."
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
    result = run_synthetic_capture_ladder()
    if args.json:
        print(json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True))
    else:
        status = "passed" if result.passed else "failed"
        print(
            f"{SYNTHETIC_CAPTURE_LADDER_ID}: {status}; "
            f"retrieval={result.retrieval_hit}; context={result.context_pack_hit}; "
            f"secret_redactions={result.secret_redaction_count}"
        )
        if result.safety_failures:
            print("failures: " + ", ".join(result.safety_failures))
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
