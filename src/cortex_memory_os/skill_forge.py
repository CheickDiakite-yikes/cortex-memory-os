"""Skill Forge pattern detector."""

from __future__ import annotations

from collections import defaultdict

from cortex_memory_os.contracts import (
    ActionRisk,
    ExecutionMode,
    MemoryStatus,
    Scene,
    SkillRecord,
)


MIN_SCENES_FOR_SKILL = 3


def detect_skill_candidates(scenes: list[Scene]) -> list[SkillRecord]:
    grouped: dict[str, list[Scene]] = defaultdict(list)
    for scene in scenes:
        grouped[scene.scene_type].append(scene)

    candidates: list[SkillRecord] = []
    for scene_type, group in sorted(grouped.items()):
        if len(group) < MIN_SCENES_FOR_SKILL:
            continue
        candidates.append(_candidate_from_group(scene_type, group))
    return candidates


def _candidate_from_group(scene_type: str, scenes: list[Scene]) -> SkillRecord:
    learned_from = [scene.scene_id for scene in scenes]
    apps = sorted({app for scene in scenes for app in scene.apps})
    entities = sorted({entity for scene in scenes for entity in scene.entities})

    return SkillRecord(
        skill_id=f"skill_{scene_type}_candidate_v1",
        name=_skill_name(scene_type),
        description=_description(scene_type, apps),
        learned_from=learned_from,
        trigger_conditions=_trigger_conditions(scene_type, entities),
        inputs={
            "goal": "string",
            "active_project": "string",
            "depth": "quick | normal | deep",
        },
        procedure=_procedure(scene_type),
        success_signals=[
            "user accepts draft",
            "low correction rate",
            "task outcome marked success",
        ],
        failure_modes=[
            "too much irrelevant context",
            "missing source refs",
            "action attempted beyond approved scope",
        ],
        risk_level=_risk_level(scene_type),
        maturity_level=2,
        execution_mode=ExecutionMode.DRAFT_ONLY,
        requires_confirmation_before=[],
        status=MemoryStatus.CANDIDATE,
    )


def _skill_name(scene_type: str) -> str:
    return {
        "research_sprint": "Research synthesis workflow",
        "coding_debugging": "Coding debugging workflow",
        "coding_work": "Coding work continuity workflow",
    }.get(scene_type, f"{scene_type.replace('_', ' ').title()} workflow")


def _description(scene_type: str, apps: list[str]) -> str:
    app_text = ", ".join(apps) if apps else "observed apps"
    return f"Draft-only workflow candidate learned from repeated {scene_type} scenes across {app_text}."


def _trigger_conditions(scene_type: str, entities: list[str]) -> list[str]:
    conditions = [f"current scene resembles {scene_type}", "user asks to continue similar work"]
    if entities:
        conditions.append(f"topic mentions {', '.join(entities[:4])}")
    return conditions


def _procedure(scene_type: str) -> list[str]:
    if scene_type == "research_sprint":
        return [
            "Recover active research goal and source refs",
            "Prefer official or primary sources",
            "Separate evidence from inference",
            "Synthesize architecture implications",
            "Return draft with citations and open risks",
        ]
    if scene_type == "coding_debugging":
        return [
            "Recover last reproduction path",
            "Inspect recent terminal and browser evidence refs",
            "Identify smallest safe patch",
            "Run targeted verification",
            "Record outcome and follow-up memory candidate",
        ]
    return [
        "Recover active workstream",
        "Retrieve relevant memories and evidence refs",
        "Draft next steps",
        "Ask before external effects",
    ]


def _risk_level(scene_type: str) -> ActionRisk:
    if scene_type in {"coding_debugging", "coding_work"}:
        return ActionRisk.MEDIUM
    return ActionRisk.LOW

