from cortex_memory_os.contracts import MemoryRecord, MemoryStatus, Scene
from cortex_memory_os.fixtures import load_json
from cortex_memory_os.memory_compiler import compile_scene_memory
from cortex_memory_os.temporal_graph import compile_temporal_edge


def test_preference_memory_compiles_to_preference_edge():
    memory = MemoryRecord.model_validate(load_json("tests/fixtures/memory_preference.json"))

    edge = compile_temporal_edge(memory)

    assert edge.subject == "user"
    assert edge.predicate == "prefers"
    assert edge.object.startswith("primary_source_research")
    assert edge.valid_from == memory.valid_from
    assert edge.confidence == memory.confidence
    assert edge.source_refs[0] == memory.memory_id


def test_scene_memory_compiles_to_worked_on_edge():
    scene = Scene.model_validate(load_json("tests/fixtures/scene_research.json"))
    memory = compile_scene_memory(scene)

    edge = compile_temporal_edge(memory)

    assert edge.subject == "user"
    assert edge.predicate == "worked_on"
    assert "research_screen_based_memory" in edge.object
    assert edge.status == MemoryStatus.CANDIDATE
    assert scene.scene_id in edge.source_refs

