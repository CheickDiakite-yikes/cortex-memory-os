import json
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from cortex_memory_os.contracts import OutcomeRecord, OutcomeStatus
from cortex_memory_os.fixtures import load_json
from cortex_memory_os.outcome_postmortem import (
    OUTCOME_POSTMORTEM_TRACE_POLICY_REF,
    OutcomePostmortem,
    compile_outcome_postmortem_from_trace,
)
from cortex_memory_os.runtime_trace import AgentRuntimeTrace


def _trace() -> AgentRuntimeTrace:
    return AgentRuntimeTrace.model_validate(
        load_json("tests/fixtures/agent_runtime_trace.json")
    )


def _outcome(trace: AgentRuntimeTrace) -> OutcomeRecord:
    return OutcomeRecord(
        outcome_id="outcome_onboarding_debug_001",
        task_id=trace.task_id,
        agent_id=trace.agent_id,
        status=OutcomeStatus.SUCCESS,
        evidence_refs=["outcome:onboarding-debug-local-tests"],
        created_at=datetime(2026, 4, 30, 6, 0, tzinfo=UTC),
    )


def test_outcome_postmortem_uses_safe_trace_metadata_only():
    trace = _trace()
    postmortem = compile_outcome_postmortem_from_trace(
        trace,
        _outcome(trace),
        created_at=datetime(2026, 4, 30, 6, 1, tzinfo=UTC),
    )
    payload = json.dumps(postmortem.model_dump(mode="json"), sort_keys=True)

    assert postmortem.event_count == 11
    assert postmortem.tool_call_count == 1
    assert postmortem.shell_action_count == 2
    assert postmortem.browser_action_count == 2
    assert postmortem.artifact_count == 1
    assert postmortem.approval_count == 1
    assert postmortem.retry_count == 1
    assert postmortem.highest_risk.value == "high"
    assert postmortem.summary_text_redacted
    assert not postmortem.event_summaries_included
    assert postmortem.content_redacted
    assert postmortem.review_required
    assert "retry_observed" in postmortem.safe_findings
    assert "high_risk_observed" in postmortem.safe_findings
    assert OUTCOME_POSTMORTEM_TRACE_POLICY_REF in postmortem.policy_refs
    assert "review_retries" in " ".join(postmortem.follow_up_task_ids)

    for event in trace.events:
        assert event.summary not in payload
    assert "Blocked untrusted external browser content" not in payload
    assert "Agent started scoped debugging task" not in payload


def test_outcome_postmortem_rejects_trace_outcome_mismatch():
    trace = _trace()
    mismatched = _outcome(trace).model_copy(update={"task_id": "task_other"})

    with pytest.raises(ValueError, match="task_id"):
        compile_outcome_postmortem_from_trace(trace, mismatched)


def test_outcome_postmortem_contract_requires_redaction():
    trace = _trace()
    postmortem = compile_outcome_postmortem_from_trace(trace, _outcome(trace))

    with pytest.raises(ValidationError, match="event summaries"):
        OutcomePostmortem.model_validate(
            postmortem.model_dump() | {"event_summaries_included": True}
        )

    with pytest.raises(ValidationError, match="summary text"):
        OutcomePostmortem.model_validate(
            postmortem.model_dump() | {"summary_text_redacted": False}
        )
