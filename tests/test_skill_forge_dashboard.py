from datetime import UTC, datetime

from cortex_memory_os.contracts import (
    ActionRisk,
    ExecutionMode,
    MemoryStatus,
    Scene,
    Sensitivity,
    SourceTrust,
)
from cortex_memory_os.fixtures import load_json
from cortex_memory_os.skill_forge import (
    DocumentSkillDerivationRequest,
    derive_skill_candidate_from_document,
    detect_skill_candidates,
)
from cortex_memory_os.skill_forge_dashboard import (
    SKILL_FORGE_CANDIDATE_LIST_POLICY_REF,
    build_skill_forge_candidate_list,
)


def _scene(scene_id: str, scene_type: str = "research_sprint") -> Scene:
    payload = load_json("tests/fixtures/scene_research.json")
    payload["scene_id"] = scene_id
    payload["scene_type"] = scene_type
    return Scene.model_validate(payload)


def _document_skill():
    request = DocumentSkillDerivationRequest(
        document_id="doc_monthly_update",
        title="Monthly update workflow",
        source_ref="docs/workflows/monthly-update.md",
        source_trust=SourceTrust.LOCAL_OBSERVED,
        sensitivity=Sensitivity.PRIVATE_WORK,
        workflow_name="Prepare monthly update draft",
        trigger_conditions=["user asks for monthly update"],
        procedure_steps=[
            "Gather approved metrics",
            "Draft update with source refs",
            "Flag missing approvals before external sharing",
        ],
        evidence_refs=["ev_doc_monthly_update"],
        risk_level=ActionRisk.MEDIUM,
    )
    return derive_skill_candidate_from_document(request).skill


def test_candidate_list_cards_are_reviewable_without_external_effects():
    repeated = detect_skill_candidates(
        [
            _scene("scene_1", "coding_debugging"),
            _scene("scene_2", "coding_debugging"),
            _scene("scene_3", "coding_debugging"),
        ]
    )[0]
    document = _document_skill()

    dashboard = build_skill_forge_candidate_list(
        [repeated, document],
        now=datetime(2026, 4, 29, 4, 30, tzinfo=UTC),
    )

    assert dashboard.candidate_count == 2
    assert dashboard.external_effect_action_count == 0
    assert dashboard.review_required_count == 6
    assert SKILL_FORGE_CANDIDATE_LIST_POLICY_REF in dashboard.policy_refs
    assert dashboard.risk_counts == {"medium": 2}
    assert all(card.status == MemoryStatus.CANDIDATE for card in dashboard.cards)
    assert all(card.execution_mode == ExecutionMode.DRAFT_ONLY for card in dashboard.cards)
    assert all(card.promotion_blockers == ["user_approval_required"] for card in dashboard.cards)
    assert {plan.gateway_tool for plan in dashboard.cards[0].action_plans} >= {
        "skill.review_candidate",
        "skill.execute_draft",
        "skill.approve_draft_only",
        "skill.reject_candidate",
    }


def test_candidate_list_redacts_secret_like_previews_and_counts_sources():
    fake_secret = "abcdefghijklmnop1234"
    skill = _document_skill().model_copy(
        update={
            "description": f"Use api_key={fake_secret} only in local dry runs.",
            "procedure": [
                f"Never expose api_key={fake_secret} in rendered UI",
                "Ask user to approve draft only",
            ],
        }
    )

    dashboard = build_skill_forge_candidate_list([skill])
    card = dashboard.cards[0]

    assert card.learned_from_count == 3
    assert card.procedure_step_count == 2
    assert card.redaction_count == 2
    assert card.content_redacted is True
    assert fake_secret not in card.description_preview
    assert all(fake_secret not in step for step in card.procedure_preview)


def test_candidate_list_omits_non_candidate_skills_but_counts_statuses():
    active = _document_skill().model_copy(update={"status": MemoryStatus.ACTIVE})
    candidate = _document_skill()

    dashboard = build_skill_forge_candidate_list([active, candidate])

    assert dashboard.candidate_count == 1
    assert [card.skill_id for card in dashboard.cards] == [candidate.skill_id]
    assert dashboard.status_counts == {"active": 1, "candidate": 1}
