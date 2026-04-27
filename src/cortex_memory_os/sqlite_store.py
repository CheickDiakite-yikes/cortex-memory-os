"""SQLite persistence for governed memories and temporal graph edges."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path

from cortex_memory_os.contracts import (
    AuditEvent,
    InfluenceLevel,
    MemoryRecord,
    MemoryStatus,
    SelfLesson,
    TemporalEdge,
)
from cortex_memory_os.memory_lifecycle import transition_memory
from cortex_memory_os.retrieval import (
    RankedMemory,
    RetrievalScope,
    rank_memories as rank_memory_records,
    tokenize,
)


class SQLiteMemoryGraphStore:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def add_memory(self, memory: MemoryRecord) -> None:
        now = datetime.now(UTC).isoformat()
        with self._connect() as con:
            con.execute(
                """
                INSERT INTO memories (
                    memory_id, status, influence_level, confidence, valid_from,
                    valid_to, content, payload_json, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(memory_id) DO UPDATE SET
                    status = excluded.status,
                    influence_level = excluded.influence_level,
                    confidence = excluded.confidence,
                    valid_from = excluded.valid_from,
                    valid_to = excluded.valid_to,
                    content = excluded.content,
                    payload_json = excluded.payload_json,
                    updated_at = excluded.updated_at
                """,
                (
                    memory.memory_id,
                    memory.status.value,
                    int(memory.influence_level),
                    memory.confidence,
                    memory.valid_from.isoformat(),
                    memory.valid_to.isoformat() if memory.valid_to else None,
                    memory.content,
                    memory.model_dump_json(),
                    now,
                ),
            )

    def add_memories(self, memories: Iterable[MemoryRecord]) -> None:
        for memory in memories:
            self.add_memory(memory)

    def get_memory(self, memory_id: str) -> MemoryRecord | None:
        with self._connect() as con:
            row = con.execute(
                "SELECT payload_json FROM memories WHERE memory_id = ?",
                (memory_id,),
            ).fetchone()
        if row is None:
            return None
        return MemoryRecord.model_validate_json(row["payload_json"])

    def forget_memory(self, memory_id: str) -> MemoryRecord:
        memory = self.get_memory(memory_id)
        if memory is None:
            raise KeyError(memory_id)

        deleted = transition_memory(memory, MemoryStatus.DELETED)
        self.add_memory(deleted)
        return deleted

    def search_memories(
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
        query_terms = tokenize(query)
        if not query_terms:
            return []

        with self._connect() as con:
            rows = con.execute(
                """
                SELECT payload_json
                FROM memories
                WHERE status NOT IN (?, ?, ?)
                  AND influence_level != ?
                """,
                (
                    MemoryStatus.DELETED.value,
                    MemoryStatus.REVOKED.value,
                    MemoryStatus.QUARANTINED.value,
                    int(InfluenceLevel.STORED_ONLY),
                ),
            ).fetchall()

        memories = [MemoryRecord.model_validate_json(row["payload_json"]) for row in rows]
        return rank_memory_records(memories, query, limit=limit, scope=scope)

    def add_edge(self, edge: TemporalEdge) -> None:
        now = datetime.now(UTC).isoformat()
        with self._connect() as con:
            con.execute(
                """
                INSERT INTO temporal_edges (
                    edge_id, subject, predicate, object, status, confidence,
                    valid_from, valid_to, payload_json, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(edge_id) DO UPDATE SET
                    subject = excluded.subject,
                    predicate = excluded.predicate,
                    object = excluded.object,
                    status = excluded.status,
                    confidence = excluded.confidence,
                    valid_from = excluded.valid_from,
                    valid_to = excluded.valid_to,
                    payload_json = excluded.payload_json,
                    updated_at = excluded.updated_at
                """,
                (
                    edge.edge_id,
                    edge.subject,
                    edge.predicate,
                    edge.object,
                    edge.status.value,
                    edge.confidence,
                    edge.valid_from.isoformat(),
                    edge.valid_to.isoformat() if edge.valid_to else None,
                    edge.model_dump_json(),
                    now,
                ),
            )

    def add_self_lesson(self, lesson: SelfLesson) -> None:
        now = datetime.now(UTC).isoformat()
        with self._connect() as con:
            con.execute(
                """
                INSERT INTO self_lessons (
                    lesson_id, status, risk_level, confidence, content,
                    payload_json, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(lesson_id) DO UPDATE SET
                    status = excluded.status,
                    risk_level = excluded.risk_level,
                    confidence = excluded.confidence,
                    content = excluded.content,
                    payload_json = excluded.payload_json,
                    updated_at = excluded.updated_at
                """,
                (
                    lesson.lesson_id,
                    lesson.status.value,
                    lesson.risk_level.value,
                    lesson.confidence,
                    lesson.content,
                    lesson.model_dump_json(),
                    now,
                ),
            )

    def get_self_lesson(self, lesson_id: str) -> SelfLesson | None:
        with self._connect() as con:
            row = con.execute(
                "SELECT payload_json FROM self_lessons WHERE lesson_id = ?",
                (lesson_id,),
            ).fetchone()
        if row is None:
            return None
        return SelfLesson.model_validate_json(row["payload_json"])

    def list_self_lessons(self, *, status: MemoryStatus | None = None) -> list[SelfLesson]:
        with self._connect() as con:
            if status is None:
                rows = con.execute(
                    """
                    SELECT payload_json
                    FROM self_lessons
                    ORDER BY status ASC, confidence DESC, lesson_id ASC
                    """
                ).fetchall()
            else:
                rows = con.execute(
                    """
                    SELECT payload_json
                    FROM self_lessons
                    WHERE status = ?
                    ORDER BY confidence DESC, lesson_id ASC
                    """,
                    (status.value,),
                ).fetchall()
        return [SelfLesson.model_validate_json(row["payload_json"]) for row in rows]

    def active_self_lessons(self) -> list[SelfLesson]:
        return self.list_self_lessons(status=MemoryStatus.ACTIVE)

    def get_edge(self, edge_id: str) -> TemporalEdge | None:
        with self._connect() as con:
            row = con.execute(
                "SELECT payload_json FROM temporal_edges WHERE edge_id = ?",
                (edge_id,),
            ).fetchone()
        if row is None:
            return None
        return TemporalEdge.model_validate_json(row["payload_json"])

    def edges_for_subject(self, subject: str) -> list[TemporalEdge]:
        with self._connect() as con:
            rows = con.execute(
                """
                SELECT payload_json
                FROM temporal_edges
                WHERE subject = ?
                ORDER BY valid_from DESC, edge_id ASC
                """,
                (subject,),
            ).fetchall()
        return [TemporalEdge.model_validate_json(row["payload_json"]) for row in rows]

    def add_audit_event(self, event: AuditEvent) -> None:
        with self._connect() as con:
            con.execute(
                """
                INSERT INTO audit_events (
                    audit_event_id, timestamp, actor, action, target_ref,
                    human_visible, payload_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(audit_event_id) DO UPDATE SET
                    timestamp = excluded.timestamp,
                    actor = excluded.actor,
                    action = excluded.action,
                    target_ref = excluded.target_ref,
                    human_visible = excluded.human_visible,
                    payload_json = excluded.payload_json
                """,
                (
                    event.audit_event_id,
                    event.timestamp.isoformat(),
                    event.actor,
                    event.action,
                    event.target_ref,
                    int(event.human_visible),
                    event.model_dump_json(),
                ),
            )

    def get_audit_event(self, audit_event_id: str) -> AuditEvent | None:
        with self._connect() as con:
            row = con.execute(
                "SELECT payload_json FROM audit_events WHERE audit_event_id = ?",
                (audit_event_id,),
            ).fetchone()
        if row is None:
            return None
        return AuditEvent.model_validate_json(row["payload_json"])

    def audit_for_target(self, target_ref: str) -> list[AuditEvent]:
        with self._connect() as con:
            rows = con.execute(
                """
                SELECT payload_json
                FROM audit_events
                WHERE target_ref = ?
                ORDER BY timestamp ASC, audit_event_id ASC
                """,
                (target_ref,),
            ).fetchall()
        return [AuditEvent.model_validate_json(row["payload_json"]) for row in rows]

    def _init_db(self) -> None:
        with self._connect() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    memory_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    influence_level INTEGER NOT NULL,
                    confidence REAL NOT NULL,
                    valid_from TEXT NOT NULL,
                    valid_to TEXT,
                    content TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            con.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_memories_status_influence
                ON memories(status, influence_level)
                """
            )
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS temporal_edges (
                    edge_id TEXT PRIMARY KEY,
                    subject TEXT NOT NULL,
                    predicate TEXT NOT NULL,
                    object TEXT NOT NULL,
                    status TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    valid_from TEXT NOT NULL,
                    valid_to TEXT,
                    payload_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            con.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_temporal_edges_subject
                ON temporal_edges(subject, predicate, valid_from)
                """
            )
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS self_lessons (
                    lesson_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    risk_level TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    content TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            con.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_self_lessons_status
                ON self_lessons(status, confidence)
                """
            )
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_events (
                    audit_event_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    action TEXT NOT NULL,
                    target_ref TEXT NOT NULL,
                    human_visible INTEGER NOT NULL,
                    payload_json TEXT NOT NULL
                )
                """
            )
            con.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_audit_events_target
                ON audit_events(target_ref, timestamp)
                """
            )

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con
