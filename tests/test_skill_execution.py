from datetime import UTC, datetime

from cortex_memory_os.contracts import ExecutionMode, SkillRecord
from cortex_memory_os.fixtures import load_json
from cortex_memory_os.skill_execution import (
    DRAFT_SKILL_EXECUTION_POLICY_REF,
    DraftSkillExecutionStatus,
    prepare_draft_skill_execution,
)


def _skill(**updates) -> SkillRecord:
    payload = load_json("tests/fixtures/skill_draft.json")
    payload.update(updates)
    return SkillRecord.model_validate(payload)


def test_draft_skill_execution_returns_reviewable_outputs_without_effects():
    skill = _skill()

    result = prepare_draft_skill_execution(
        skill,
        inputs={"topic": "memory export UI"},
        now=datetime(2026, 4, 27, 22, 0, tzinfo=UTC),
    )

    assert result.status == DraftSkillExecutionStatus.DRAFT_READY
    assert result.execution_mode == ExecutionMode.DRAFT_ONLY
    assert result.policy_refs == (DRAFT_SKILL_EXECUTION_POLICY_REF,)
    assert result.external_effects_requested == ()
    assert result.external_effects_performed == ()
    assert result.required_review_actions == ("review", "edit", "approve_or_discard")
    assert [output.kind for output in result.proposed_outputs] == [
        "draft_plan",
        "review_checklist",
    ]
    assert all(output.review_required for output in result.proposed_outputs)
    assert "External effects performed: none." in result.proposed_outputs[0].content


def test_draft_skill_execution_blocks_requested_external_effects():
    skill = _skill()

    result = prepare_draft_skill_execution(
        skill,
        requested_external_effects=("send_email",),
        now=datetime(2026, 4, 27, 22, 1, tzinfo=UTC),
    )

    assert result.status == DraftSkillExecutionStatus.BLOCKED
    assert result.blocked_reason == "draft_mode_blocks_external_effects"
    assert result.proposed_outputs == ()
    assert result.external_effects_requested == ("send_email",)
    assert result.external_effects_performed == ()


def test_draft_skill_execution_rejects_non_draft_skill():
    skill = _skill().model_copy(
        update={
            "maturity_level": 3,
            "execution_mode": ExecutionMode.ASSISTIVE,
            "status": "active",
        }
    )

    result = prepare_draft_skill_execution(
        skill,
        now=datetime(2026, 4, 27, 22, 2, tzinfo=UTC),
    )

    assert result.status == DraftSkillExecutionStatus.BLOCKED
    assert result.blocked_reason == "skill_not_draft_only"
    assert result.external_effects_performed == ()
