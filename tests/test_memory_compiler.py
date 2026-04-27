from datetime import UTC, datetime

from cortex_memory_os.contracts import (
    EvidenceType,
    InfluenceLevel,
    MemoryStatus,
    MemoryType,
    Scene,
)
from cortex_memory_os.fixtures import load_json
from cortex_memory_os.memory_compiler import compile_scene_bundle, compile_scene_memory


def _scene() -> Scene:
    return Scene.model_validate(load_json("tests/fixtures/scene_research.json"))


def test_compile_scene_memory_preserves_evidence_and_inference_boundary():
    scene = _scene()
    memory = compile_scene_memory(scene, now=datetime(2026, 4, 27, 18, 0, tzinfo=UTC))

    assert memory.type == MemoryType.EPISODIC
    assert memory.status == MemoryStatus.CANDIDATE
    assert memory.evidence_type == EvidenceType.OBSERVED_AND_INFERRED
    assert memory.source_refs[0] == scene.scene_id
    assert set(scene.evidence_refs).issubset(memory.source_refs)
    assert memory.influence_level == InfluenceLevel.DIRECT_QUERY
    assert "external_actions" in memory.forbidden_influence


def test_compile_scene_memory_is_user_visible_candidate():
    memory = compile_scene_memory(_scene())

    assert memory.user_visible
    assert memory.requires_user_confirmation is False
    assert memory.confidence < _scene().confidence
    assert "Research screen-based memory systems" in memory.content


def test_compile_scene_bundle_contains_scene_id_and_memory():
    scene = _scene()
    bundle = compile_scene_bundle(scene)

    assert bundle.scene_id == scene.scene_id
    assert len(bundle.memories) == 1
    assert bundle.memories[0].memory_id == f"mem_{scene.scene_id}"

