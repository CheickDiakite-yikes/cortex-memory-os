import pytest

from cortex_memory_os.contracts import (
    ActionRisk,
    ExecutionMode,
    MemoryStatus,
    ScopeLevel,
    SelfLesson,
)
from cortex_memory_os.context_templates import (
    CONTEXT_TEMPLATE_POLICY_REF,
    ContextMemoryLane,
    ContextPackTemplate,
    ContextTaskType,
    default_context_pack_templates,
    effective_context_limit,
    select_context_self_lessons,
    select_context_pack_template,
)
from cortex_memory_os.fixtures import load_json
from cortex_memory_os.retrieval import RetrievalScope


def test_context_template_registry_is_compact_and_policy_backed():
    templates = {template.task_type: template for template in default_context_pack_templates()}

    assert set(templates) == {
        ContextTaskType.CODING_DEBUGGING,
        ContextTaskType.RESEARCH_SYNTHESIS,
        ContextTaskType.GENERAL,
    }
    assert all(template.max_memories <= 8 for template in templates.values())
    assert all(template.max_prompt_tokens > 0 for template in templates.values())
    assert all(template.max_tool_calls >= 0 for template in templates.values())
    assert all(template.max_artifacts >= 0 for template in templates.values())
    assert all(
        template.autonomy_ceiling == ExecutionMode.ASSISTIVE
        for template in templates.values()
    )
    assert all(
        template.max_action_risk in {ActionRisk.LOW, ActionRisk.MEDIUM}
        for template in templates.values()
    )
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


def test_context_template_routes_active_self_lessons_and_excludes_revoked():
    template = select_context_pack_template("continue fixing onboarding auth bug")
    active = SelfLesson.model_validate(load_json("tests/fixtures/self_lesson_auth.json"))
    revoked = active.model_copy(
        update={
            "lesson_id": "lesson_revoked_auth",
            "status": MemoryStatus.REVOKED,
        }
    )

    selected = select_context_self_lessons(
        [revoked, active],
        "continue fixing onboarding auth bug",
        template,
    )

    assert [lesson.lesson_id for lesson in selected] == ["lesson_044"]


def test_context_template_filters_self_lessons_by_retrieval_scope():
    template = select_context_pack_template("continue fixing onboarding auth bug")
    active = SelfLesson.model_validate(load_json("tests/fixtures/self_lesson_auth.json"))
    alpha = active.model_copy(
        update={
            "lesson_id": "lesson_alpha",
            "scope": ScopeLevel.PROJECT_SPECIFIC,
            "learned_from": ["project:alpha", "task_alpha"],
        }
    )
    beta = active.model_copy(
        update={
            "lesson_id": "lesson_beta",
            "scope": ScopeLevel.PROJECT_SPECIFIC,
            "learned_from": ["project:beta", "task_beta"],
        }
    )

    selected = select_context_self_lessons(
        [beta, alpha],
        "continue fixing onboarding auth bug",
        template,
        scope=RetrievalScope(active_project="alpha"),
    )
    missing_scope = select_context_self_lessons(
        [alpha],
        "continue fixing onboarding auth bug",
        template,
        scope=RetrievalScope(),
    )

    assert [lesson.lesson_id for lesson in selected] == ["lesson_alpha"]
    assert missing_scope == ()


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


def test_context_template_rejects_high_risk_or_autonomy_budget():
    with pytest.raises(ValueError, match="high or critical"):
        ContextPackTemplate(
            template_id="template_high_risk",
            task_type=ContextTaskType.GENERAL,
            description="Unsafe high-risk template.",
            memory_lanes=(ContextMemoryLane.PROJECT_MEMORY,),
            max_memories=3,
            max_action_risk=ActionRisk.HIGH,
            warnings=("Stay scoped.",),
            recommended_next_steps=("Ask before acting.",),
        )

    with pytest.raises(ValueError, match="autonomous execution"):
        ContextPackTemplate(
            template_id="template_autonomous",
            task_type=ContextTaskType.GENERAL,
            description="Unsafe autonomous template.",
            memory_lanes=(ContextMemoryLane.PROJECT_MEMORY,),
            max_memories=3,
            autonomy_ceiling=ExecutionMode.BOUNDED_AUTONOMY,
            warnings=("Stay scoped.",),
            recommended_next_steps=("Ask before acting.",),
        )
