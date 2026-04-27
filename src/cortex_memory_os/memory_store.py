"""Small in-memory store used by tests and synthetic benchmarks."""

from __future__ import annotations

from collections.abc import Iterable

from cortex_memory_os.contracts import MemoryRecord, MemoryStatus
from cortex_memory_os.retrieval import (
    RetrievalScope,
    RankedMemory,
    rank_memories,
    tokenize,
)
from cortex_memory_os.memory_lifecycle import transition_memory


class InMemoryMemoryStore:
    def __init__(self, memories: Iterable[MemoryRecord] | None = None) -> None:
        self._memories: dict[str, MemoryRecord] = {}
        for memory in memories or []:
            self.add(memory)

    def add(self, memory: MemoryRecord) -> None:
        self._memories[memory.memory_id] = memory

    def get(self, memory_id: str) -> MemoryRecord | None:
        return self._memories.get(memory_id)

    def forget(self, memory_id: str) -> MemoryRecord:
        memory = self._memories[memory_id]
        deleted = transition_memory(memory, MemoryStatus.DELETED)
        self._memories[memory_id] = deleted
        return deleted

    def search(
        self,
        query: str,
        *,
        limit: int = 5,
        scope: RetrievalScope | None = None,
    ) -> list[MemoryRecord]:
        return [ranked.memory for ranked in self.rank(query, limit=limit, scope=scope)]

    def rank(
        self,
        query: str,
        *,
        limit: int = 5,
        scope: RetrievalScope | None = None,
    ) -> list[RankedMemory]:
        return rank_memories(self._memories.values(), query, limit=limit, scope=scope)


def _tokenize(text: str) -> set[str]:
    return tokenize(text)
