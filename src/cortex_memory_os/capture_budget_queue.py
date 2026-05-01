"""Capture consolidation budget queue with cost and rate-limit backpressure."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import Field, model_validator

from cortex_memory_os.contracts import StrictModel


CAPTURE_BUDGET_QUEUE_ID = "CAPTURE-BUDGET-QUEUE-001"
CAPTURE_BUDGET_QUEUE_POLICY_REF = "policy_capture_budget_queue_v1"


class CaptureConsolidationJob(StrictModel):
    job_id: str = Field(min_length=1)
    source_window_id: str = Field(min_length=1)
    priority: int = Field(default=50, ge=0, le=100)
    estimated_tokens: int = Field(ge=1)
    estimated_cost_cents: int = Field(ge=0)
    contains_sensitive_content: bool = False
    requested_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CaptureBudgetEnvelope(StrictModel):
    remaining_tokens: int = Field(ge=0)
    remaining_cost_cents: int = Field(ge=0)
    remaining_jobs: int = Field(ge=0)
    rate_limit_reset_at: datetime | None = None
    privacy_pause_active: bool = False
    policy_refs: list[str] = Field(
        default_factory=lambda: [CAPTURE_BUDGET_QUEUE_POLICY_REF]
    )

    @model_validator(mode="after")
    def require_budget_policy_ref(self) -> CaptureBudgetEnvelope:
        if CAPTURE_BUDGET_QUEUE_POLICY_REF not in self.policy_refs:
            raise ValueError("capture budget envelope requires policy ref")
        return self


class CaptureBudgetDecision(StrictModel):
    benchmark_id: str = Field(default=CAPTURE_BUDGET_QUEUE_ID)
    accepted_job_ids: list[str] = Field(default_factory=list)
    deferred_job_ids: list[str] = Field(default_factory=list)
    skipped_job_ids: list[str] = Field(default_factory=list)
    total_tokens: int = Field(ge=0)
    total_cost_cents: int = Field(ge=0)
    backpressure_active: bool
    reasons: list[str] = Field(min_length=1)
    allowed_effects: list[str] = Field(default_factory=list)
    blocked_effects: list[str] = Field(default_factory=list)
    policy_refs: list[str] = Field(
        default_factory=lambda: [CAPTURE_BUDGET_QUEUE_POLICY_REF]
    )

    @model_validator(mode="after")
    def enforce_queue_decision_boundary(self) -> CaptureBudgetDecision:
        if self.benchmark_id != CAPTURE_BUDGET_QUEUE_ID:
            raise ValueError("capture budget queue benchmark_id mismatch")
        if CAPTURE_BUDGET_QUEUE_POLICY_REF not in self.policy_refs:
            raise ValueError("capture budget decision requires policy ref")
        all_ids = self.accepted_job_ids + self.deferred_job_ids + self.skipped_job_ids
        if len(all_ids) != len(set(all_ids)):
            raise ValueError("capture budget decision cannot duplicate job ids")
        if self.total_tokens == 0 and self.accepted_job_ids:
            raise ValueError("accepted jobs require token budget usage")
        if "start_real_screen_capture" in self.allowed_effects:
            raise ValueError("budget queue cannot start real screen capture")
        if "write_durable_memory" in self.allowed_effects:
            raise ValueError("budget queue cannot write durable memory")
        return self


def schedule_capture_consolidation(
    jobs: list[CaptureConsolidationJob],
    budget: CaptureBudgetEnvelope,
) -> CaptureBudgetDecision:
    """Accept only jobs that fit the explicit consolidation budget."""

    if budget.privacy_pause_active:
        return CaptureBudgetDecision(
            accepted_job_ids=[],
            deferred_job_ids=[],
            skipped_job_ids=[job.job_id for job in jobs],
            total_tokens=0,
            total_cost_cents=0,
            backpressure_active=True,
            reasons=["privacy_pause_active"],
            allowed_effects=["queue_metadata_only"],
            blocked_effects=[
                "start_background_consolidation",
                "call_model_for_capture_summary",
                "start_real_screen_capture",
                "write_durable_memory",
            ],
        )

    accepted: list[str] = []
    deferred: list[str] = []
    skipped: list[str] = []
    total_tokens = 0
    total_cost_cents = 0
    remaining_tokens = budget.remaining_tokens
    remaining_cost_cents = budget.remaining_cost_cents
    remaining_jobs = budget.remaining_jobs
    reasons: set[str] = set()

    for job in sorted(jobs, key=lambda item: (-item.priority, item.requested_at, item.job_id)):
        if job.contains_sensitive_content:
            skipped.append(job.job_id)
            reasons.add("sensitive_content_requires_firewall")
            continue
        fits = (
            remaining_jobs > 0
            and job.estimated_tokens <= remaining_tokens
            and job.estimated_cost_cents <= remaining_cost_cents
        )
        if fits:
            accepted.append(job.job_id)
            remaining_jobs -= 1
            remaining_tokens -= job.estimated_tokens
            remaining_cost_cents -= job.estimated_cost_cents
            total_tokens += job.estimated_tokens
            total_cost_cents += job.estimated_cost_cents
            continue
        deferred.append(job.job_id)
        reasons.add("budget_or_rate_limit_backpressure")

    backpressure_active = bool(deferred or skipped)
    if accepted:
        reasons.add("accepted_within_budget")
    if not jobs:
        reasons.add("queue_empty")

    return CaptureBudgetDecision(
        accepted_job_ids=accepted,
        deferred_job_ids=deferred,
        skipped_job_ids=skipped,
        total_tokens=total_tokens,
        total_cost_cents=total_cost_cents,
        backpressure_active=backpressure_active,
        reasons=sorted(reasons),
        allowed_effects=["schedule_synthetic_consolidation_jobs"]
        if accepted
        else ["queue_metadata_only"],
        blocked_effects=[
            "start_real_screen_capture",
            "write_durable_memory",
        ],
        policy_refs=[CAPTURE_BUDGET_QUEUE_POLICY_REF],
    )
