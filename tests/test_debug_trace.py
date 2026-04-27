from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from cortex_memory_os.debug_trace import DebugTraceRecord, DebugTraceStatus, make_debug_trace
from cortex_memory_os.sensitive_data_policy import (
    REDACTED_SECRET_PLACEHOLDER,
    SECRET_PII_POLICY_REF,
)


def test_debug_trace_factory_redacts_summary_and_details():
    secret = "CORTEX_FAKE_TOKEN_debugSECRET123"
    trace = make_debug_trace(
        layer="gateway",
        event="context_pack_failed",
        status=DebugTraceStatus.ERROR,
        summary=f"Failed while token={secret}",
        details={"stderr": f"Bearer {secret}"},
        now=datetime(2026, 4, 27, 20, 10, tzinfo=UTC),
    )
    serialized = trace.model_dump_json()

    assert secret not in serialized
    assert REDACTED_SECRET_PLACEHOLDER in serialized
    assert trace.redaction_count == 2
    assert SECRET_PII_POLICY_REF in trace.policy_refs


def test_debug_trace_record_rejects_unredacted_secret_like_text():
    with pytest.raises(ValidationError, match="unredacted secret-like"):
        DebugTraceRecord(
            trace_id="dbg_bad",
            timestamp=datetime(2026, 4, 27, 20, 10, tzinfo=UTC),
            layer="vault",
            event="write_failed",
            status=DebugTraceStatus.ERROR,
            summary="CORTEX_FAKE_TOKEN_should_redact_12345",
            details={},
            artifact_refs=[],
            redaction_count=0,
            policy_refs=[SECRET_PII_POLICY_REF],
        )


def test_debug_trace_keeps_repro_refs_without_raw_payloads():
    trace = make_debug_trace(
        layer="benchmarks",
        event="case_failed",
        status=DebugTraceStatus.WARNING,
        summary="Synthetic deletion benchmark failed.",
        details={"case_id": "MEM-FORGET-001/deleted_memory"},
        artifact_refs=["benchmarks/runs/synthetic.json"],
        now=datetime(2026, 4, 27, 20, 11, tzinfo=UTC),
    )

    assert trace.details["case_id"] == "MEM-FORGET-001/deleted_memory"
    assert trace.artifact_refs == ["benchmarks/runs/synthetic.json"]
    assert trace.redaction_count == 0
