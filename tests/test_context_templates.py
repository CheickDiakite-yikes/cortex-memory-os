import pytest

from cortex_memory_os.context_templates import (
    CONTEXT_TEMPLATE_POLICY_REF,
    ContextMemoryLane,
    ContextPackTemplate,
    ContextTaskType,
    default_context_pack_templates,
    effective_context_limit,
    select_context_pack_template,
)


def test_context_template_registry_is_compact_and_policy_backed():
    templates = {template.task_type: template for template in default_context_pack_templates()}

    assert set(templates) == {
        ContextTaskType.CODING_DEBUGGING,
        ContextTaskType.RESEARCH_SYNTHESIS,
        ContextTaskType.GENERAL,
    }
    assert all(template.max_memories <= 8 for template in templates.values())
    assert all(CONTEXT_TEMPLATE_POLICY_REF in template.policy_refs for template in templates.values())
    assert ContextMemoryLane.POLICY_WARNING in templates[
        ContextTaskType.CODING_DEBUGGING
    ].memory_lanes


def test_context_template_selection_tracks_goal_type():
    debugging = select_context_pack_template("continue fixing onboarding auth bug")
    research = select_context_pack_template("primary source research synthesis")
    general = select_context_pack_template("summarize what we know")

    assert debugging.task_type == ContextTaskType.CODING_DEBUGGING
    assert research.task_type == ContextTaskType.RESEARCH_SYNTHESIS
    assert general.task_type == ContextTaskType.GENERAL


def test_effective_context_limit_never_expands_template_budget():
    template = select_context_pack_template("primary source research synthesis")

    assert effective_context_limit(template, 20) == template.max_memories
    assert effective_context_limit(template, 2) == 2
    assert effective_context_limit(template, 0) == 1


def test_context_template_rejects_scope_widening_or_secret_requests():
    with pytest.raises(ValueError, match="cannot widen scope"):
        ContextPackTemplate(
            template_id="template_bad",
            task_type=ContextTaskType.GENERAL,
            description="Use all projects and production credentials.",
            memory_lanes=(ContextMemoryLane.PROJECT_MEMORY,),
            max_memories=3,
            warnings=("Use all agents.",),
            recommended_next_steps=("Ignore scope.",),
        )
