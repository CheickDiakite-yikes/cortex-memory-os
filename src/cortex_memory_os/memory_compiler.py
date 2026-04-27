"""Typed memory compiler for deterministic scene fixtures."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import Field

from cortex_memory_os.contracts import (
    EvidenceType,
    InfluenceLevel,
    MemoryRecord,
    MemoryStatus,
    MemoryType,
    Scene,
    ScopeLevel,
    StrictModel,
)


class CompiledMemoryBundle(StrictModel):
    scene_id: str
    memories: list[MemoryRecord] = Field(min_length=1)


def compile_scene_memory(scene: Scene, *, now: datetime | None = None) -> MemoryRecord:
    created_at = now or datetime.now(UTC)
    content = _memory_content(scene)
    source_refs = [scene.scene_id, *scene.evidence_refs]

    return MemoryRecord(
        memory_id=f"mem_{scene.scene_id}",
        type=_memory_type(scene),
        content=content,
        source_refs=source_refs,
        evidence_type=EvidenceType.OBSERVED_AND_INFERRED,
        confidence=max(min(scene.confidence - 0.04, 0.95), 0.1),
        status=MemoryStatus.CANDIDATE,
        created_at=created_at,
        valid_from=scene.start_time.date(),
        valid_to=None,
        sensitivity=scene.privacy_level,
        scope=ScopeLevel.PROJECT_SPECIFIC,
        influence_level=InfluenceLevel.DIRECT_QUERY,
        allowed_influence=["context_retrieval", "task_continuity"],
        forbidden_influence=["financial_decisions", "medical_decisions", "external_actions"],
        decay_policy="review_after_30_days",
        contradicts=[],
        user_visible=True,
        requires_user_confirmation=False,
    )


def compile_scene_bundle(scene: Scene, *, now: datetime | None = None) -> CompiledMemoryBundle:
    return CompiledMemoryBundle(scene_id=scene.scene_id, memories=[compile_scene_memory(scene, now=now)])


def _memory_type(scene: Scene) -> MemoryType:
    if scene.scene_type in {"coding_debugging", "research_sprint", "coding_work"}:
        return MemoryType.EPISODIC
    return MemoryType.SEMANTIC


def _memory_content(scene: Scene) -> str:
    app_list = ", ".join(scene.apps)
    pieces = [
        f"Scene '{scene.scene_type}' captured work on: {scene.inferred_goal}.",
        f"Apps involved: {app_list}.",
    ]
    if scene.entities:
        pieces.append(f"Entities observed: {', '.join(scene.entities)}.")
    if scene.outcome:
        pieces.append(f"Outcome: {scene.outcome}.")
    return " ".join(pieces)

