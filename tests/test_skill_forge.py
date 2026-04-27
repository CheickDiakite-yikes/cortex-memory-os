from cortex_memory_os.contracts import ExecutionMode, MemoryStatus, Scene
from cortex_memory_os.fixtures import load_json
from cortex_memory_os.skill_forge import detect_skill_candidates


def _scene(scene_id: str, scene_type: str = "research_sprint") -> Scene:
    payload = load_json("tests/fixtures/scene_research.json")
    payload["scene_id"] = scene_id
    payload["scene_type"] = scene_type
    return Scene.model_validate(payload)


def test_repeated_scenes_create_draft_only_skill_candidate():
    scenes = [_scene("scene_1"), _scene("scene_2"), _scene("scene_3")]

    candidates = detect_skill_candidates(scenes)

    assert len(candidates) == 1
    skill = candidates[0]
    assert skill.skill_id == "skill_research_sprint_candidate_v1"
    assert skill.status == MemoryStatus.CANDIDATE
    assert skill.execution_mode == ExecutionMode.DRAFT_ONLY
    assert skill.maturity_level == 2
    assert skill.learned_from == ["scene_1", "scene_2", "scene_3"]
    assert "Prefer official or primary sources" in skill.procedure


def test_two_scenes_are_not_enough_for_skill_candidate():
    assert detect_skill_candidates([_scene("scene_1"), _scene("scene_2")]) == []


def test_coding_debugging_candidate_is_medium_risk_but_draft_only():
    scenes = [
        _scene("scene_1", "coding_debugging"),
        _scene("scene_2", "coding_debugging"),
        _scene("scene_3", "coding_debugging"),
    ]

    skill = detect_skill_candidates(scenes)[0]

    assert skill.risk_level == "medium"
    assert skill.execution_mode == ExecutionMode.DRAFT_ONLY
    assert "Run targeted verification" in skill.procedure

