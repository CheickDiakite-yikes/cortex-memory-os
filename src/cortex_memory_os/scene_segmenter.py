"""Deterministic scene segmentation for synthetic observation streams."""

from __future__ import annotations

from collections import OrderedDict
from datetime import timedelta

from pydantic import Field

from cortex_memory_os.contracts import ObservationEvent, Scene, Sensitivity, StrictModel


class SegmentableEvent(StrictModel):
    observation: ObservationEvent
    topic_terms: list[str] = Field(min_length=1)
    evidence_ref: str = Field(min_length=1)
    action_trace_ref: str | None = None
    entities: list[str] = Field(default_factory=list)
    goal_hint: str | None = None


def segment_events(
    events: list[SegmentableEvent],
    *,
    max_gap: timedelta = timedelta(minutes=20),
) -> list[Scene]:
    if not events:
        return []

    sorted_events = sorted(events, key=lambda item: item.observation.timestamp)
    groups: list[list[SegmentableEvent]] = [[sorted_events[0]]]

    for event in sorted_events[1:]:
        current = groups[-1]
        previous = current[-1]
        if _starts_new_scene(previous, event, current, max_gap):
            groups.append([event])
        else:
            current.append(event)

    return [_compile_scene(index, group) for index, group in enumerate(groups, start=1)]


def _starts_new_scene(
    previous: SegmentableEvent,
    event: SegmentableEvent,
    current_group: list[SegmentableEvent],
    max_gap: timedelta,
) -> bool:
    if event.observation.timestamp - previous.observation.timestamp > max_gap:
        return True
    if event.observation.project_id != previous.observation.project_id:
        return True

    current_terms = set().union(*[set(item.topic_terms) for item in current_group])
    next_terms = set(event.topic_terms)
    overlap = current_terms & next_terms
    return not overlap and event.observation.app != previous.observation.app


def _compile_scene(index: int, group: list[SegmentableEvent]) -> Scene:
    first = group[0]
    last = group[-1]
    apps = list(OrderedDict.fromkeys(item.observation.app or "unknown" for item in group))
    entities = list(OrderedDict.fromkeys(entity for item in group for entity in item.entities))
    evidence_refs = [item.evidence_ref for item in group]
    action_trace_refs = [
        item.action_trace_ref for item in group if item.action_trace_ref is not None
    ]
    topic_terms = set().union(*[set(item.topic_terms) for item in group])
    goal = _infer_goal(group, topic_terms)

    return Scene(
        scene_id=f"scene_{first.observation.timestamp.strftime('%Y%m%d_%H%M%S')}_{index}",
        start_time=first.observation.timestamp,
        end_time=last.observation.timestamp,
        scene_type=_infer_scene_type(apps, topic_terms),
        inferred_goal=goal,
        apps=apps,
        entities=entities,
        action_trace_refs=action_trace_refs,
        evidence_refs=evidence_refs,
        outcome=None,
        confidence=_confidence_for(group),
        privacy_level=Sensitivity.PRIVATE_WORK,
        segmentation_reason=_segmentation_reasons(group),
    )


def _infer_scene_type(apps: list[str], topic_terms: set[str]) -> str:
    lowered_apps = {app.lower() for app in apps}
    if "research" in topic_terms or "mcp" in topic_terms or "graphiti" in topic_terms:
        return "research_sprint"
    if lowered_apps & {"terminal", "vs code", "cursor"}:
        if {"bug", "test", "auth", "error"} & topic_terms:
            return "coding_debugging"
        return "coding_work"
    return "workstream"


def _infer_goal(group: list[SegmentableEvent], topic_terms: set[str]) -> str:
    for item in group:
        if item.goal_hint:
            return item.goal_hint
    important_terms = ", ".join(sorted(topic_terms)[:6])
    return f"Work on {important_terms}"


def _confidence_for(group: list[SegmentableEvent]) -> float:
    base = 0.62
    if len(group) >= 2:
        base += 0.12
    if any(item.goal_hint for item in group):
        base += 0.08
    if len({item.observation.app for item in group}) > 1:
        base += 0.05
    return min(base, 0.92)


def _segmentation_reasons(group: list[SegmentableEvent]) -> list[str]:
    reasons = ["topic_continuity"]
    if len({item.observation.app for item in group}) > 1:
        reasons.append("app_switch_cluster")
    if any(item.goal_hint for item in group):
        reasons.append("explicit_goal_hint")
    return reasons

