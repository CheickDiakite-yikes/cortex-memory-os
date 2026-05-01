from datetime import UTC, datetime, timedelta

from cortex_memory_os.capture_budget_queue import (
    CAPTURE_BUDGET_QUEUE_POLICY_REF,
    CaptureBudgetEnvelope,
    CaptureConsolidationJob,
    schedule_capture_consolidation,
)


def test_capture_budget_queue_accepts_priority_jobs_within_budget():
    now = datetime(2026, 5, 1, 12, 0, tzinfo=UTC)
    jobs = [
        CaptureConsolidationJob(
            job_id="job_low",
            source_window_id="window_a",
            priority=10,
            estimated_tokens=300,
            estimated_cost_cents=2,
            requested_at=now,
        ),
        CaptureConsolidationJob(
            job_id="job_high",
            source_window_id="window_b",
            priority=90,
            estimated_tokens=500,
            estimated_cost_cents=3,
            requested_at=now + timedelta(seconds=1),
        ),
        CaptureConsolidationJob(
            job_id="job_overflow",
            source_window_id="window_c",
            priority=80,
            estimated_tokens=600,
            estimated_cost_cents=3,
            requested_at=now + timedelta(seconds=2),
        ),
    ]
    budget = CaptureBudgetEnvelope(
        remaining_tokens=900,
        remaining_cost_cents=5,
        remaining_jobs=2,
    )

    decision = schedule_capture_consolidation(jobs, budget)

    assert decision.accepted_job_ids == ["job_high", "job_low"]
    assert decision.deferred_job_ids == ["job_overflow"]
    assert decision.total_tokens == 800
    assert decision.total_cost_cents == 5
    assert decision.backpressure_active is True
    assert "budget_or_rate_limit_backpressure" in decision.reasons
    assert "start_real_screen_capture" in decision.blocked_effects
    assert CAPTURE_BUDGET_QUEUE_POLICY_REF in decision.policy_refs


def test_capture_budget_queue_privacy_pause_skips_all_work():
    jobs = [
        CaptureConsolidationJob(
            job_id="job_private",
            source_window_id="window_private",
            priority=100,
            estimated_tokens=200,
            estimated_cost_cents=1,
        )
    ]

    decision = schedule_capture_consolidation(
        jobs,
        CaptureBudgetEnvelope(
            remaining_tokens=10_000,
            remaining_cost_cents=50,
            remaining_jobs=10,
            privacy_pause_active=True,
        ),
    )

    assert decision.accepted_job_ids == []
    assert decision.skipped_job_ids == ["job_private"]
    assert decision.reasons == ["privacy_pause_active"]
    assert decision.allowed_effects == ["queue_metadata_only"]
    assert "call_model_for_capture_summary" in decision.blocked_effects


def test_capture_budget_queue_skips_sensitive_jobs_before_consolidation():
    decision = schedule_capture_consolidation(
        [
            CaptureConsolidationJob(
                job_id="job_sensitive",
                source_window_id="window_sensitive",
                priority=100,
                estimated_tokens=50,
                estimated_cost_cents=1,
                contains_sensitive_content=True,
            )
        ],
        CaptureBudgetEnvelope(
            remaining_tokens=100,
            remaining_cost_cents=2,
            remaining_jobs=1,
        ),
    )

    assert decision.accepted_job_ids == []
    assert decision.skipped_job_ids == ["job_sensitive"]
    assert "sensitive_content_requires_firewall" in decision.reasons
