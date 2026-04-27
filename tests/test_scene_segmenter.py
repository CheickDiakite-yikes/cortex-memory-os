from datetime import datetime, timedelta

from cortex_memory_os.contracts import ObservationEvent
from cortex_memory_os.scene_segmenter import SegmentableEvent, segment_events


def _event(
    event_id: str,
    when: datetime,
    app: str,
    terms: list[str],
    *,
    project_id: str = "cortex-memory-os",
    goal_hint: str | None = None,
) -> SegmentableEvent:
    return SegmentableEvent(
        observation=ObservationEvent(
            event_id=event_id,
            event_type="terminal_output" if app == "Terminal" else "browser_dom",
            timestamp=when,
            device="macbook",
            app=app,
            window_title=project_id,
            project_id=project_id,
            payload_ref=f"volatile://{event_id}",
            source_trust="B",
            capture_scope="project_specific",
            consent_state="active",
            raw_contains_user_input=True,
        ),
        topic_terms=terms,
        evidence_ref=f"ev_{event_id}",
        action_trace_ref=f"trace_{event_id}",
        entities=["MCP"] if "mcp" in terms else [],
        goal_hint=goal_hint,
    )


def test_segments_by_time_gap_and_topic_continuity():
    start = datetime.fromisoformat("2026-04-27T12:00:00-04:00")
    events = [
        _event(
            "001",
            start,
            "Chrome",
            ["research", "mcp", "memory"],
            goal_hint="Research agent memory architecture",
        ),
        _event("002", start + timedelta(minutes=5), "Terminal", ["mcp", "memory", "tests"]),
        _event("003", start + timedelta(minutes=45), "VS Code", ["auth", "bug", "test"]),
        _event("004", start + timedelta(minutes=49), "Terminal", ["auth", "bug", "error"]),
    ]

    scenes = segment_events(events)

    assert len(scenes) == 2
    assert scenes[0].scene_type == "research_sprint"
    assert scenes[0].inferred_goal == "Research agent memory architecture"
    assert scenes[0].apps == ["Chrome", "Terminal"]
    assert scenes[0].evidence_refs == ["ev_001", "ev_002"]
    assert scenes[1].scene_type == "coding_debugging"
    assert scenes[1].apps == ["VS Code", "Terminal"]


def test_segments_by_project_change_even_when_topic_overlaps():
    start = datetime.fromisoformat("2026-04-27T12:00:00-04:00")
    events = [
        _event("001", start, "Terminal", ["auth", "bug"], project_id="project-a"),
        _event("002", start + timedelta(minutes=3), "Terminal", ["auth", "bug"], project_id="project-b"),
    ]

    scenes = segment_events(events)

    assert len(scenes) == 2
    assert scenes[0].evidence_refs == ["ev_001"]
    assert scenes[1].evidence_refs == ["ev_002"]


def test_empty_event_stream_returns_no_scenes():
    assert segment_events([]) == []

