"""Outcome postmortems compiled from safe runtime trace metadata."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import Field, model_validator

from cortex_memory_os.contracts import ActionRisk, OutcomeRecord, OutcomeStatus, StrictModel
from cortex_memory_os.runtime_trace import (
    AgentRuntimeTrace,
    RuntimeTraceSummary,
    summarize_runtime_trace,
    trace_evidence_refs,
)

OUTCOME_POSTMORTEM_TRACE_ID = "OUTCOME-POSTMORTEM-TRACE-001"
OUTCOME_POSTMORTEM_TRACE_POLICY_REF = "policy_outcome_postmortem_trace_v1"


class OutcomePostmortem(StrictModel):
    postmortem_id: str = Field(min_length=1)
    task_id: str = Field(min_length=1)
    agent_id: str = Field(min_length=1)
    outcome_id: str = Field(min_length=1)
    outcome_status: OutcomeStatus
    trace_id: str = Field(min_length=1)
    created_at: datetime
    event_count: int = Field(ge=0)
    tool_call_count: int = Field(ge=0)
    shell_action_count: int = Field(ge=0)
    browser_action_count: int = Field(ge=0)
    artifact_count: int = Field(ge=0)
    approval_count: int = Field(ge=0)
    retry_count: int = Field(ge=0)
    external_effect_count: int = Field(ge=0)
    highest_risk: ActionRisk
    evidence_ref_count: int = Field(ge=0)
    outcome_evidence_ref_count: int = Field(ge=0)
    safe_findings: list[str] = Field(default_factory=list)
    follow_up_task_ids: list[str] = Field(default_factory=list)
    review_required: bool
    summary_text_redacted: bool = True
    event_summaries_included: bool = False
    content_redacted: bool = True
    allowed_effects: list[str] = Field(
        default_factory=lambda: ["compile_redacted_outcome_postmortem"]
    )
    blocked_effects: list[str] = Field(
        default_factory=lambda: [
            "copy_runtime_event_summary_text",
            "promote_trace_text_to_instruction",
            "change_skill_maturity",
            "create_active_self_lesson",
        ]
    )
    policy_refs: list[str] = Field(
        default_factory=lambda: [OUTCOME_POSTMORTEM_TRACE_POLICY_REF]
    )

    @model_validator(mode="after")
    def enforce_redacted_postmortem(self) -> OutcomePostmortem:
        if not self.content_redacted:
            raise ValueError("outcome postmortems must be content redacted")
        if not self.summary_text_redacted:
            raise ValueError("outcome postmortems must redact summary text")
        if self.event_summaries_included:
            raise ValueError("outcome postmortems cannot include event summaries")
        if OUTCOME_POSTMORTEM_TRACE_POLICY_REF not in self.policy_refs:
            raise ValueError("outcome postmortems require policy refs")
        return self


def compile_outcome_postmortem_from_trace(
    trace: AgentRuntimeTrace,
    outcome: OutcomeRecord,
    *,
    created_at: datetime | None = None,
) -> OutcomePostmortem:
    """Compile a redacted postmortem using counts and refs, not trace prose."""

    if trace.task_id != outcome.task_id:
        raise ValueError("runtime trace and outcome task_id must match")
    if trace.agent_id != outcome.agent_id:
        raise ValueError("runtime trace and outcome agent_id must match")

    summary = summarize_runtime_trace(trace)
    combined_evidence_refs = sorted(
        set(trace_evidence_refs(trace)).union(outcome.evidence_refs)
    )
    safe_findings = _safe_findings(summary)
    follow_up_task_ids = _follow_up_task_ids(summary)

    return OutcomePostmortem(
        postmortem_id=f"postmortem_{outcome.outcome_id}",
        task_id=outcome.task_id,
        agent_id=outcome.agent_id,
        outcome_id=outcome.outcome_id,
        outcome_status=outcome.status,
        trace_id=trace.trace_id,
        created_at=created_at or datetime.now(UTC),
        event_count=summary.event_count,
        tool_call_count=summary.tool_call_count,
        shell_action_count=summary.shell_action_count,
        browser_action_count=summary.browser_action_count,
        artifact_count=summary.artifact_count,
        approval_count=summary.approval_count,
        retry_count=summary.retry_count,
        external_effect_count=summary.external_effect_count,
        highest_risk=summary.highest_risk,
        evidence_ref_count=len(combined_evidence_refs),
        outcome_evidence_ref_count=len(outcome.evidence_refs),
        safe_findings=safe_findings,
        follow_up_task_ids=follow_up_task_ids,
        review_required=bool(follow_up_task_ids),
        policy_refs=[OUTCOME_POSTMORTEM_TRACE_POLICY_REF],
    )


def _safe_findings(summary: RuntimeTraceSummary) -> list[str]:
    findings = [f"outcome_{summary.outcome_status.value}"]
    if summary.retry_count:
        findings.append("retry_observed")
    if summary.approval_count:
        findings.append("approval_present")
    if summary.artifact_count:
        findings.append("artifact_evidence_present")
    if summary.external_effect_count:
        findings.append("external_effect_observed")
    if summary.highest_risk in {ActionRisk.HIGH, ActionRisk.CRITICAL}:
        findings.append("high_risk_observed")
    if summary.content_redacted:
        findings.append("trace_content_redacted")
    return findings


def _follow_up_task_ids(summary: RuntimeTraceSummary) -> list[str]:
    follow_ups: list[str] = []
    if summary.outcome_status != OutcomeStatus.SUCCESS:
        follow_ups.append(f"{OUTCOME_POSTMORTEM_TRACE_ID}/review_non_success")
    if summary.retry_count:
        follow_ups.append(f"{OUTCOME_POSTMORTEM_TRACE_ID}/review_retries")
    if summary.highest_risk in {ActionRisk.HIGH, ActionRisk.CRITICAL}:
        follow_ups.append(f"{OUTCOME_POSTMORTEM_TRACE_ID}/review_high_risk")
    return follow_ups
