"""Agent runtime trace contracts for auditable agent execution."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from enum import Enum

from pydantic import Field, model_validator

from cortex_memory_os.contracts import (
    ActionRisk,
    OutcomeStatus,
    Sensitivity,
    SourceTrust,
    StrictModel,
)

RUNTIME_TRACE_POLICY_REF = "policy_agent_runtime_trace_v1"


class RuntimeEventKind(str, Enum):
    AGENT_STARTED = "agent_started"
    TOOL_CALL = "tool_call"
    SHELL_ACTION = "shell_action"
    BROWSER_ACTION = "browser_action"
    ARTIFACT_CREATED = "artifact_created"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_GRANTED = "approval_granted"
    APPROVAL_REJECTED = "approval_rejected"
    RETRY = "retry"
    OUTCOME_CHECK = "outcome_check"
    AGENT_FINISHED = "agent_finished"


class RuntimeEventStatus(str, Enum):
    PLANNED = "planned"
    STARTED = "started"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    BLOCKED = "blocked"
    APPROVED = "approved"
    REJECTED = "rejected"


class RuntimeEffect(str, Enum):
    NONE = "none"
    LOCAL_READ = "local_read"
    LOCAL_WRITE = "local_write"
    NETWORK_CALL = "network_call"
    EXTERNAL_ACTION = "external_action"
    DATA_EGRESS = "data_egress"
    DESTRUCTIVE_ACTION = "destructive_action"


class RuntimeArtifactKind(str, Enum):
    PATCH = "patch"
    FILE = "file"
    LOG = "log"
    SCREENSHOT = "screenshot"
    BENCHMARK = "benchmark"
    EXPORT = "export"


class AgentRuntimeEvent(StrictModel):
    event_id: str = Field(min_length=1)
    sequence: int = Field(ge=0)
    timestamp: datetime
    kind: RuntimeEventKind
    status: RuntimeEventStatus
    actor: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    source_trust: SourceTrust
    risk_level: ActionRisk = ActionRisk.LOW
    effects: list[RuntimeEffect] = Field(default_factory=lambda: [RuntimeEffect.NONE])
    tool_name: str | None = None
    target_ref: str | None = None
    approval_ref: str | None = None
    retry_of: str | None = None
    attempt: int = Field(default=1, ge=1)
    artifact_refs: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    policy_refs: list[str] = Field(default_factory=lambda: [RUNTIME_TRACE_POLICY_REF])
    content_redacted: bool = True
    redaction_count: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def enforce_event_contract(self) -> AgentRuntimeEvent:
        if "ignore previous" in self.summary.lower():
            raise ValueError("runtime trace summaries cannot echo prompt-injection instructions")
        if not self.policy_refs:
            raise ValueError("runtime events require policy refs")
        if self.kind == RuntimeEventKind.TOOL_CALL and not self.tool_name:
            raise ValueError("tool_call events require tool_name")
        if self.kind == RuntimeEventKind.SHELL_ACTION:
            _require_target_prefix(self.target_ref, "shell:")
        if self.kind == RuntimeEventKind.BROWSER_ACTION:
            _require_target_prefix(self.target_ref, "browser:")
        if self.kind == RuntimeEventKind.ARTIFACT_CREATED and not self.artifact_refs:
            raise ValueError("artifact_created events require artifact_refs")
        if self.kind == RuntimeEventKind.RETRY:
            if not self.retry_of:
                raise ValueError("retry events require retry_of")
            if self.attempt < 2:
                raise ValueError("retry events require attempt >= 2")
        if self.source_trust in {
            SourceTrust.EXTERNAL_UNTRUSTED,
            SourceTrust.HOSTILE_UNTIL_SAFE,
        } and not self.content_redacted:
            raise ValueError("external or hostile trace content must be redacted")
        if (
            self.kind
            not in {
                RuntimeEventKind.APPROVAL_REQUESTED,
                RuntimeEventKind.APPROVAL_GRANTED,
                RuntimeEventKind.APPROVAL_REJECTED,
            }
            and self.status != RuntimeEventStatus.BLOCKED
            and _requires_approval(self.risk_level, self.effects)
            and not self.approval_ref
        ):
            raise ValueError("medium/high-risk or external-effect events require approval_ref")
        return self


class RuntimeArtifact(StrictModel):
    artifact_id: str = Field(min_length=1)
    kind: RuntimeArtifactKind
    uri_ref: str = Field(min_length=1)
    created_by_event_id: str = Field(min_length=1)
    sensitivity: Sensitivity = Sensitivity.LOW
    retained: bool = True
    checksum_sha256: str | None = None
    policy_refs: list[str] = Field(default_factory=lambda: [RUNTIME_TRACE_POLICY_REF])

    @model_validator(mode="after")
    def enforce_artifact_contract(self) -> RuntimeArtifact:
        if self.sensitivity == Sensitivity.SECRET and self.retained:
            raise ValueError("secret runtime artifacts cannot be retained")
        if not self.policy_refs:
            raise ValueError("runtime artifacts require policy refs")
        return self


class RuntimeTraceSummary(StrictModel):
    event_count: int = Field(ge=0)
    tool_call_count: int = Field(ge=0)
    shell_action_count: int = Field(ge=0)
    browser_action_count: int = Field(ge=0)
    artifact_count: int = Field(ge=0)
    approval_count: int = Field(ge=0)
    retry_count: int = Field(ge=0)
    external_effect_count: int = Field(ge=0)
    highest_risk: ActionRisk
    outcome_status: OutcomeStatus
    content_redacted: bool = True


class AgentRuntimeTrace(StrictModel):
    trace_id: str = Field(min_length=1)
    task_id: str = Field(min_length=1)
    agent_id: str = Field(min_length=1)
    goal: str = Field(min_length=1)
    started_at: datetime
    ended_at: datetime | None = None
    events: list[AgentRuntimeEvent] = Field(min_length=1)
    artifacts: list[RuntimeArtifact] = Field(default_factory=list)
    outcome_status: OutcomeStatus
    outcome_ref: str | None = None
    policy_refs: list[str] = Field(default_factory=lambda: [RUNTIME_TRACE_POLICY_REF])

    @model_validator(mode="after")
    def enforce_trace_contract(self) -> AgentRuntimeTrace:
        if self.ended_at is not None and self.ended_at < self.started_at:
            raise ValueError("trace ended_at cannot precede started_at")
        if not self.policy_refs:
            raise ValueError("runtime traces require policy refs")

        event_ids: set[str] = set()
        event_sequences: dict[str, int] = {}
        approval_sequences: dict[str, int] = {}
        previous_sequence = -1
        previous_timestamp: datetime | None = None
        for event in self.events:
            if event.event_id in event_ids:
                raise ValueError("runtime trace event IDs must be unique")
            event_ids.add(event.event_id)
            event_sequences[event.event_id] = event.sequence
            if event.sequence <= previous_sequence:
                raise ValueError("runtime trace events must be strictly ordered by sequence")
            previous_sequence = event.sequence
            if previous_timestamp is not None and event.timestamp < previous_timestamp:
                raise ValueError("runtime trace event timestamps must be monotonic")
            previous_timestamp = event.timestamp
            if event.timestamp < self.started_at:
                raise ValueError("runtime trace events cannot precede started_at")
            if self.ended_at is not None and event.timestamp > self.ended_at:
                raise ValueError("runtime trace events cannot follow ended_at")
            if event.kind == RuntimeEventKind.APPROVAL_GRANTED:
                approval_sequences[event.event_id] = event.sequence

        for event in self.events:
            if event.retry_of and event.retry_of not in event_ids:
                raise ValueError("retry events must reference a prior event")
            if event.retry_of and event_sequences[event.retry_of] >= event.sequence:
                raise ValueError("retry events must reference a prior event")
            if event.approval_ref and event.approval_ref not in approval_sequences:
                raise ValueError("approval_ref must reference an approval_granted event")
            if event.approval_ref and approval_sequences[event.approval_ref] >= event.sequence:
                raise ValueError("approval_ref must reference a prior approval_granted event")

        for artifact in self.artifacts:
            if artifact.created_by_event_id not in event_ids:
                raise ValueError("runtime artifacts must reference an existing event")
            creator = next(
                event for event in self.events if event.event_id == artifact.created_by_event_id
            )
            if artifact.artifact_id not in creator.artifact_refs:
                raise ValueError("artifact creator event must list artifact_id")

        if self.outcome_status == OutcomeStatus.SUCCESS:
            if not any(
                event.kind == RuntimeEventKind.OUTCOME_CHECK
                and event.status == RuntimeEventStatus.SUCCEEDED
                for event in self.events
            ):
                raise ValueError("successful traces require a succeeded outcome_check event")
        return self


def summarize_runtime_trace(trace: AgentRuntimeTrace) -> RuntimeTraceSummary:
    counts = Counter(event.kind for event in trace.events)
    external_effect_count = sum(
        1
        for event in trace.events
        if any(
            effect
            in {
                RuntimeEffect.NETWORK_CALL,
                RuntimeEffect.EXTERNAL_ACTION,
                RuntimeEffect.DATA_EGRESS,
                RuntimeEffect.DESTRUCTIVE_ACTION,
            }
            for effect in event.effects
        )
    )
    highest_risk = max(
        (event.risk_level for event in trace.events),
        key=_risk_rank,
        default=ActionRisk.LOW,
    )
    return RuntimeTraceSummary(
        event_count=len(trace.events),
        tool_call_count=counts[RuntimeEventKind.TOOL_CALL],
        shell_action_count=counts[RuntimeEventKind.SHELL_ACTION],
        browser_action_count=counts[RuntimeEventKind.BROWSER_ACTION],
        artifact_count=len(trace.artifacts),
        approval_count=counts[RuntimeEventKind.APPROVAL_GRANTED],
        retry_count=counts[RuntimeEventKind.RETRY],
        external_effect_count=external_effect_count,
        highest_risk=highest_risk,
        outcome_status=trace.outcome_status,
        content_redacted=all(event.content_redacted for event in trace.events),
    )


def trace_evidence_refs(trace: AgentRuntimeTrace) -> list[str]:
    refs: list[str] = []
    for event in trace.events:
        refs.extend(event.evidence_refs)
        refs.extend(f"runtime_event:{ref}" for ref in event.artifact_refs)
    refs.extend(f"runtime_artifact:{artifact.artifact_id}" for artifact in trace.artifacts)
    if trace.outcome_ref:
        refs.append(trace.outcome_ref)
    return sorted(set(refs))


def _requires_approval(risk_level: ActionRisk, effects: list[RuntimeEffect]) -> bool:
    if risk_level in {ActionRisk.MEDIUM, ActionRisk.HIGH, ActionRisk.CRITICAL}:
        return True
    return any(
        effect
        in {
            RuntimeEffect.EXTERNAL_ACTION,
            RuntimeEffect.DATA_EGRESS,
            RuntimeEffect.DESTRUCTIVE_ACTION,
        }
        for effect in effects
    )


def _require_target_prefix(target_ref: str | None, prefix: str) -> None:
    if target_ref is None or not target_ref.startswith(prefix):
        raise ValueError(f"{prefix.rstrip(':')} events require target_ref prefix {prefix}")


def _risk_rank(risk: ActionRisk) -> int:
    return {
        ActionRisk.LOW: 0,
        ActionRisk.MEDIUM: 1,
        ActionRisk.HIGH: 2,
        ActionRisk.CRITICAL: 3,
    }[risk]
