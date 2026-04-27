"""Privacy-aware structured debug traces."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum

from pydantic import Field, model_validator

from cortex_memory_os.contracts import StrictModel
from cortex_memory_os.firewall import redact_sensitive_text
from cortex_memory_os.sensitive_data_policy import SECRET_PII_POLICY_REF


class DebugTraceStatus(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    RESOLVED = "resolved"


class DebugTraceRecord(StrictModel):
    trace_id: str = Field(min_length=1)
    timestamp: datetime
    layer: str = Field(min_length=1)
    event: str = Field(min_length=1)
    status: DebugTraceStatus
    summary: str = Field(min_length=1)
    details: dict[str, str] = Field(default_factory=dict)
    artifact_refs: list[str] = Field(default_factory=list)
    redaction_count: int = Field(ge=0)
    policy_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def reject_unredacted_secret_like_text(self) -> DebugTraceRecord:
        texts = [self.summary, *self.details.values(), *self.artifact_refs]
        for text in texts:
            _, redactions = redact_sensitive_text(text)
            if redactions:
                raise ValueError("debug trace contains unredacted secret-like text")
        return self


def make_debug_trace(
    *,
    layer: str,
    event: str,
    status: DebugTraceStatus,
    summary: str,
    details: dict[str, str] | None = None,
    artifact_refs: list[str] | None = None,
    now: datetime | None = None,
) -> DebugTraceRecord:
    timestamp = now or datetime.now(UTC)
    redacted_summary, summary_redactions = redact_sensitive_text(summary)
    redacted_details: dict[str, str] = {}
    redaction_count = len(summary_redactions)
    for key, value in (details or {}).items():
        redacted_value, redactions = redact_sensitive_text(value)
        redacted_details[key] = redacted_value
        redaction_count += len(redactions)

    return DebugTraceRecord(
        trace_id=(
            f"dbg_{timestamp.strftime('%Y%m%dT%H%M%SZ')}_"
            f"{_safe_id_fragment(layer)}_{_safe_id_fragment(event)}"
        ),
        timestamp=timestamp,
        layer=layer,
        event=event,
        status=status,
        summary=redacted_summary,
        details=redacted_details,
        artifact_refs=artifact_refs or [],
        redaction_count=redaction_count,
        policy_refs=[SECRET_PII_POLICY_REF],
    )


def _safe_id_fragment(value: str) -> str:
    return "".join(char.lower() if char.isalnum() else "_" for char in value).strip("_")
