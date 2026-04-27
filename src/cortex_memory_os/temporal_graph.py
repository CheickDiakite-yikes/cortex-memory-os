"""Temporal graph edge compiler."""

from __future__ import annotations

import re

from cortex_memory_os.contracts import MemoryRecord, TemporalEdge


def compile_temporal_edge(memory: MemoryRecord) -> TemporalEdge:
    subject, predicate, object_value = _edge_triplet(memory)
    return TemporalEdge(
        edge_id=f"edge_{memory.memory_id}",
        subject=subject,
        predicate=predicate,
        object=object_value,
        valid_from=memory.valid_from,
        valid_to=memory.valid_to,
        confidence=memory.confidence,
        source_refs=[memory.memory_id, *memory.source_refs],
        status=memory.status,
        supersedes=memory.contradicts,
    )


def _edge_triplet(memory: MemoryRecord) -> tuple[str, str, str]:
    content = memory.content
    lowered = content.lower()

    if "user prefers" in lowered:
        return "user", "prefers", _slug(content.split("prefers", 1)[-1])
    if "apps involved:" in lowered:
        return "user", "worked_on", _slug(_extract_between(content, "captured work on:", "."))
    if memory.type.value == "self_lesson":
        return "cortex", "learned", _slug(content)
    return "memory", "states", _slug(content)


def _extract_between(text: str, start: str, end: str) -> str:
    lowered = text.lower()
    start_index = lowered.find(start)
    if start_index == -1:
        return text
    value_start = start_index + len(start)
    value_end = text.find(end, value_start)
    if value_end == -1:
        value_end = len(text)
    return text[value_start:value_end]


def _slug(value: str) -> str:
    tokens = re.findall(r"[a-z0-9]+", value.lower())
    return "_".join(tokens[:12]) or "unknown"

