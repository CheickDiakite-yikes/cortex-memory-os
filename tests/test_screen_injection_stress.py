from cortex_memory_os.screen_injection_stress import (
    SCREEN_INJECTION_STRESS_POLICY_REF,
    run_screen_injection_stress,
)


def test_screen_injection_stress_quarantines_hostile_visual_context():
    result = run_screen_injection_stress()

    assert result.policy_ref == SCREEN_INJECTION_STRESS_POLICY_REF
    assert result.event_count == 4
    assert result.quarantine_count == 4
    assert result.eligible_for_memory_count == 0
    assert result.redaction_count == 4
    assert result.relevant_context_memory_count == 0
    assert result.blocked_context_memory_count == 1
    assert result.untrusted_evidence_ref_count >= 1
    assert result.source_route_hint_count >= 1
    assert result.hostile_instruction_promoted is False
    assert result.fake_secret_leaked is False
    assert result.raw_refs_in_context is False
    assert result.passed is True
