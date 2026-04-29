from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from cortex_memory_os.contracts import ActionRisk, OutcomeStatus, SourceTrust
from cortex_memory_os.fixtures import load_json
from cortex_memory_os.runtime_trace import (
    AgentRuntimeEvent,
    AgentRuntimeTrace,
    RuntimeEffect,
    RuntimeEventKind,
    RuntimeEventStatus,
    summarize_runtime_trace,
    trace_evidence_refs,
)


def _trace() -> AgentRuntimeTrace:
    return AgentRuntimeTrace.model_validate(
        load_json("tests/fixtures/agent_runtime_trace.json")
    )


def test_runtime_trace_fixture_summarizes_agent_execution():
    trace = _trace()
    summary = summarize_runtime_trace(trace)
    evidence_refs = trace_evidence_refs(trace)

    assert trace.trace_id == "trace_cortex_debug_001"
    assert summary.event_count == 11
    assert summary.tool_call_count == 1
    assert summary.shell_action_count == 2
    assert summary.browser_action_count == 2
    assert summary.artifact_count == 1
    assert summary.approval_count == 1
    assert summary.retry_count == 1
    assert summary.highest_risk == ActionRisk.HIGH
    assert summary.outcome_status == OutcomeStatus.SUCCESS
    assert summary.content_redacted is True
    assert "runtime_artifact:artifact_patch_001" in evidence_refs
    assert "outcome:onboarding-debug-local-tests" in evidence_refs


def test_medium_risk_or_external_effect_events_require_approval_ref():
    with pytest.raises(ValidationError, match="approval_ref"):
        AgentRuntimeEvent(
            event_id="evt_unapproved_write",
            sequence=1,
            timestamp=datetime(2026, 4, 29, 10, 0, tzinfo=UTC),
            kind=RuntimeEventKind.SHELL_ACTION,
            status=RuntimeEventStatus.SUCCEEDED,
            actor="codex",
            summary="Applied local write without approval.",
            source_trust=SourceTrust.LOCAL_OBSERVED,
            risk_level=ActionRisk.MEDIUM,
            effects=[RuntimeEffect.LOCAL_WRITE],
            target_ref="shell:apply-patch",
        )

    with pytest.raises(ValidationError, match="approval_ref"):
        AgentRuntimeEvent(
            event_id="evt_unapproved_egress",
            sequence=2,
            timestamp=datetime(2026, 4, 29, 10, 1, tzinfo=UTC),
            kind=RuntimeEventKind.TOOL_CALL,
            status=RuntimeEventStatus.SUCCEEDED,
            actor="codex",
            summary="Tried to send external message.",
            source_trust=SourceTrust.LOCAL_OBSERVED,
            risk_level=ActionRisk.LOW,
            effects=[RuntimeEffect.DATA_EGRESS],
            tool_name="email.send",
        )


def test_runtime_trace_rejects_unredacted_hostile_browser_content():
    with pytest.raises(ValidationError, match="external or hostile"):
        AgentRuntimeEvent(
            event_id="evt_hostile",
            sequence=1,
            timestamp=datetime(2026, 4, 29, 10, 0, tzinfo=UTC),
            kind=RuntimeEventKind.BROWSER_ACTION,
            status=RuntimeEventStatus.BLOCKED,
            actor="codex",
            summary="Hostile page tried to become instructions.",
            source_trust=SourceTrust.HOSTILE_UNTIL_SAFE,
            risk_level=ActionRisk.HIGH,
            effects=[RuntimeEffect.NONE],
            target_ref="browser:external-page",
            content_redacted=False,
        )


def test_runtime_trace_rejects_bad_order_missing_retry_and_missing_artifact_refs():
    payload = load_json("tests/fixtures/agent_runtime_trace.json")
    payload["events"][3]["retry_of"] = "evt_missing"
    with pytest.raises(ValidationError, match="retry events must reference"):
        AgentRuntimeTrace.model_validate(payload)

    payload = load_json("tests/fixtures/agent_runtime_trace.json")
    payload["events"][3]["retry_of"] = "evt_patch"
    with pytest.raises(ValidationError, match="prior event"):
        AgentRuntimeTrace.model_validate(payload)

    payload = load_json("tests/fixtures/agent_runtime_trace.json")
    payload["events"][1]["risk_level"] = "medium"
    payload["events"][1]["approval_ref"] = "evt_approval"
    with pytest.raises(ValidationError, match="prior approval"):
        AgentRuntimeTrace.model_validate(payload)

    payload = load_json("tests/fixtures/agent_runtime_trace.json")
    payload["events"][4]["artifact_refs"] = []
    with pytest.raises(ValidationError, match="artifact_created events require"):
        AgentRuntimeTrace.model_validate(payload)

    payload = load_json("tests/fixtures/agent_runtime_trace.json")
    payload["events"][2], payload["events"][3] = payload["events"][3], payload["events"][2]
    with pytest.raises(ValidationError, match="strictly ordered"):
        AgentRuntimeTrace.model_validate(payload)


def test_successful_runtime_trace_requires_outcome_check():
    payload = load_json("tests/fixtures/agent_runtime_trace.json")
    payload["events"] = [
        event for event in payload["events"] if event["kind"] != "outcome_check"
    ]

    with pytest.raises(ValidationError, match="successful traces require"):
        AgentRuntimeTrace.model_validate(payload)
