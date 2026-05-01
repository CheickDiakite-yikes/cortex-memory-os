"""Unified encrypted memory payload store with redacted graph/index metadata."""

from __future__ import annotations

import hashlib
import hmac
import json
import sqlite3
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from pydantic import Field, model_validator

from cortex_memory_os.contracts import (
    InfluenceLevel,
    MemoryRecord,
    MemoryStatus,
    ScopeLevel,
    Sensitivity,
    StrictModel,
    TemporalEdge,
)
from cortex_memory_os.evidence_vault import BlobCipher, VaultRuntimeMode
from cortex_memory_os.memory_encryption import (
    EncryptedMemoryStore,
    MEMORY_ENCRYPTION_DEFAULT_POLICY_REF,
    MemoryStorageReceipt,
)
from cortex_memory_os.retrieval import (
    RankedMemory,
    RetrievalScope,
    rank_memories,
    tokenize,
)

UNIFIED_ENCRYPTED_GRAPH_INDEX_ID = "UNIFIED-ENCRYPTED-GRAPH-INDEX-001"
UNIFIED_ENCRYPTED_GRAPH_INDEX_POLICY_REF = "policy_unified_encrypted_graph_index_v1"


class UnifiedIndexWriteReceipt(StrictModel):
    memory_id: str = Field(min_length=1)
    stored_at: datetime
    token_digest_count: int = Field(ge=0)
    source_ref_count: int = Field(ge=0)
    storage_receipt: MemoryStorageReceipt
    content_redacted: bool = True
    source_refs_redacted: bool = True
    token_text_redacted: bool = True
    allowed_effects: list[str] = Field(default_factory=list)
    blocked_effects: list[str] = Field(default_factory=list)
    policy_refs: list[str] = Field(
        default_factory=lambda: [
            UNIFIED_ENCRYPTED_GRAPH_INDEX_POLICY_REF,
            MEMORY_ENCRYPTION_DEFAULT_POLICY_REF,
        ]
    )

    @model_validator(mode="after")
    def keep_receipt_redacted(self) -> UnifiedIndexWriteReceipt:
        if not self.content_redacted:
            raise ValueError("unified index receipts cannot include memory content")
        if not self.source_refs_redacted:
            raise ValueError("unified index receipts cannot include source refs")
        if not self.token_text_redacted:
            raise ValueError("unified index receipts cannot include token text")
        if UNIFIED_ENCRYPTED_GRAPH_INDEX_POLICY_REF not in self.policy_refs:
            raise ValueError("unified index receipts require policy refs")
        if MEMORY_ENCRYPTION_DEFAULT_POLICY_REF not in self.policy_refs:
            raise ValueError("unified index receipts require memory encryption policy refs")
        return self


class UnifiedGraphWriteReceipt(StrictModel):
    edge_id: str = Field(min_length=1)
    stored_at: datetime
    related_memory_count: int = Field(ge=1)
    graph_token_digest_count: int = Field(ge=0)
    payload_sha256: str = Field(min_length=64, max_length=64)
    sealed_byte_count: int = Field(ge=1)
    content_redacted: bool = True
    source_refs_redacted: bool = True
    graph_terms_redacted: bool = True
    policy_refs: list[str] = Field(
        default_factory=lambda: [UNIFIED_ENCRYPTED_GRAPH_INDEX_POLICY_REF]
    )

    @model_validator(mode="after")
    def keep_graph_receipt_redacted(self) -> UnifiedGraphWriteReceipt:
        if not self.content_redacted:
            raise ValueError("graph receipts cannot include graph payload content")
        if not self.source_refs_redacted:
            raise ValueError("graph receipts cannot include source refs")
        if not self.graph_terms_redacted:
            raise ValueError("graph receipts cannot include graph terms")
        if UNIFIED_ENCRYPTED_GRAPH_INDEX_POLICY_REF not in self.policy_refs:
            raise ValueError("graph receipts require policy refs")
        return self


class UnifiedIndexHit(StrictModel):
    memory_id: str = Field(min_length=1)
    score: float = Field(ge=0.0, le=1.0)
    matched_token_digest_count: int = Field(ge=0)
    graph_boosted: bool
    source_ref_count: int = Field(ge=0)
    status: MemoryStatus
    scope: ScopeLevel
    sensitivity: Sensitivity
    influence_level: InfluenceLevel
    content_redacted: bool = True
    source_refs_redacted: bool = True
    query_redacted: bool = True
    token_text_redacted: bool = True
    policy_refs: list[str] = Field(
        default_factory=lambda: [UNIFIED_ENCRYPTED_GRAPH_INDEX_POLICY_REF]
    )

    @model_validator(mode="after")
    def keep_hit_metadata_only(self) -> UnifiedIndexHit:
        if not self.content_redacted:
            raise ValueError("unified index hits cannot include content")
        if not self.source_refs_redacted:
            raise ValueError("unified index hits cannot include source refs")
        if not self.query_redacted:
            raise ValueError("unified index hits cannot include query text")
        if not self.token_text_redacted:
            raise ValueError("unified index hits cannot include token text")
        if UNIFIED_ENCRYPTED_GRAPH_INDEX_POLICY_REF not in self.policy_refs:
            raise ValueError("unified index hits require policy refs")
        return self


class UnifiedIndexSearchReceipt(StrictModel):
    query_digest_count: int = Field(ge=0)
    considered_index_rows: int = Field(ge=0)
    candidate_open_count: int = Field(ge=0)
    result_count: int = Field(ge=0)
    content_redacted: bool = True
    source_refs_redacted: bool = True
    query_redacted: bool = True
    token_text_redacted: bool = True
    policy_refs: list[str] = Field(
        default_factory=lambda: [UNIFIED_ENCRYPTED_GRAPH_INDEX_POLICY_REF]
    )

    @model_validator(mode="after")
    def keep_search_receipt_metadata_only(self) -> UnifiedIndexSearchReceipt:
        if not self.content_redacted:
            raise ValueError("unified index search receipts cannot include content")
        if not self.source_refs_redacted:
            raise ValueError("unified index search receipts cannot include source refs")
        if not self.query_redacted:
            raise ValueError("unified index search receipts cannot include query text")
        if not self.token_text_redacted:
            raise ValueError("unified index search receipts cannot include token text")
        if UNIFIED_ENCRYPTED_GRAPH_INDEX_POLICY_REF not in self.policy_refs:
            raise ValueError("unified index search receipts require policy refs")
        return self


class UnifiedIndexSearchResponse(StrictModel):
    hits: list[UnifiedIndexHit] = Field(default_factory=list)
    receipt: UnifiedIndexSearchReceipt
    content_redacted: bool = True
    source_refs_redacted: bool = True
    query_redacted: bool = True
    policy_refs: list[str] = Field(
        default_factory=lambda: [UNIFIED_ENCRYPTED_GRAPH_INDEX_POLICY_REF]
    )

    @model_validator(mode="after")
    def keep_response_metadata_only(self) -> UnifiedIndexSearchResponse:
        if not self.content_redacted:
            raise ValueError("unified index search responses cannot include content")
        if not self.source_refs_redacted:
            raise ValueError("unified index search responses cannot include source refs")
        if not self.query_redacted:
            raise ValueError("unified index search responses cannot include query text")
        if UNIFIED_ENCRYPTED_GRAPH_INDEX_POLICY_REF not in self.policy_refs:
            raise ValueError("unified index search responses require policy refs")
        return self


@dataclass(frozen=True)
class _CandidateHit:
    memory_id: str
    index_score: float
    matched_token_digest_count: int
    graph_boosted: bool


class UnifiedEncryptedGraphIndex:
    """Redacted local index over authenticated encrypted memory payloads."""

    def __init__(
        self,
        db_path: str | Path,
        *,
        cipher: BlobCipher,
        index_key: bytes | str,
        mode: VaultRuntimeMode | str = VaultRuntimeMode.DEVELOPMENT,
    ) -> None:
        self.db_path = Path(db_path)
        self.index_key = _normalize_index_key(index_key)
        if not bool(getattr(cipher, "authenticated_encryption", False)):
            raise ValueError("authenticated_encryption_required_for_unified_index")
        self.memory_store = EncryptedMemoryStore(
            self.db_path,
            cipher=cipher,
            mode=mode,
        )
        self.cipher = cipher
        self.mode = VaultRuntimeMode(mode)
        self._init_index_db()

    def add_memory(
        self,
        memory: MemoryRecord,
        *,
        now: datetime | None = None,
    ) -> UnifiedIndexWriteReceipt:
        storage_receipt = self.memory_store.add_memory(memory, now=now)
        token_digests = sorted(self._memory_token_digests(memory))
        stored_at = _ensure_utc(now or datetime.now(UTC))
        with self._connect() as con:
            con.execute(
                """
                INSERT INTO redacted_memory_index (
                    memory_id, status, sensitivity, scope, influence_level,
                    token_digests_json, source_ref_count, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(memory_id) DO UPDATE SET
                    status = excluded.status,
                    sensitivity = excluded.sensitivity,
                    scope = excluded.scope,
                    influence_level = excluded.influence_level,
                    token_digests_json = excluded.token_digests_json,
                    source_ref_count = excluded.source_ref_count,
                    updated_at = excluded.updated_at
                """,
                (
                    memory.memory_id,
                    memory.status.value,
                    memory.sensitivity.value,
                    memory.scope.value,
                    int(memory.influence_level),
                    json.dumps(token_digests, sort_keys=True),
                    len(memory.source_refs),
                    stored_at.isoformat(),
                ),
            )
        return UnifiedIndexWriteReceipt(
            memory_id=memory.memory_id,
            stored_at=stored_at,
            token_digest_count=len(token_digests),
            source_ref_count=len(memory.source_refs),
            storage_receipt=storage_receipt,
            allowed_effects=[
                "write_sealed_memory_payload",
                "write_redacted_hmac_index_terms",
            ],
            blocked_effects=[
                "store_plaintext_memory_content",
                "store_plaintext_source_refs",
                "store_plaintext_graph_terms",
            ],
        )

    def add_memories(self, memories: Iterable[MemoryRecord]) -> list[UnifiedIndexWriteReceipt]:
        return [self.add_memory(memory) for memory in memories]

    def add_edge(
        self,
        edge: TemporalEdge,
        *,
        related_memory_ids: Iterable[str],
        now: datetime | None = None,
    ) -> UnifiedGraphWriteReceipt:
        related = sorted(set(related_memory_ids))
        if not related:
            raise ValueError("encrypted graph index edges require related memory ids")
        plaintext = edge.model_dump_json().encode("utf-8")
        sealed = self.cipher.seal(plaintext)
        payload_sha256 = hashlib.sha256(plaintext).hexdigest()
        token_digests = sorted(self._graph_token_digests(edge))
        stored_at = _ensure_utc(now or datetime.now(UTC))
        with self._connect() as con:
            con.execute(
                """
                INSERT INTO encrypted_graph_edges (
                    edge_id, status, related_memory_ids_json, token_digests_json,
                    payload_sha256, payload_ciphertext, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(edge_id) DO UPDATE SET
                    status = excluded.status,
                    related_memory_ids_json = excluded.related_memory_ids_json,
                    token_digests_json = excluded.token_digests_json,
                    payload_sha256 = excluded.payload_sha256,
                    payload_ciphertext = excluded.payload_ciphertext,
                    updated_at = excluded.updated_at
                """,
                (
                    edge.edge_id,
                    edge.status.value,
                    json.dumps(related, sort_keys=True),
                    json.dumps(token_digests, sort_keys=True),
                    payload_sha256,
                    sealed,
                    stored_at.isoformat(),
                ),
            )
        return UnifiedGraphWriteReceipt(
            edge_id=edge.edge_id,
            stored_at=stored_at,
            related_memory_count=len(related),
            graph_token_digest_count=len(token_digests),
            payload_sha256=payload_sha256,
            sealed_byte_count=len(sealed),
        )

    def get_memory(self, memory_id: str) -> MemoryRecord | None:
        return self.memory_store.get_memory(memory_id)

    def list_memories(self, *, status: MemoryStatus | None = None) -> list[MemoryRecord]:
        return self.memory_store.list_memories(status=status)

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
        candidate_ids = [
            candidate.memory_id
            for candidate in self._candidate_hits(query, limit=max(limit * 4, limit))
        ]
        candidates = [
            memory
            for memory_id in candidate_ids
            if (memory := self.get_memory(memory_id)) is not None
        ]
        return rank_memories(candidates, query, limit=limit, scope=scope)

    def search_index(
        self,
        query: str,
        *,
        limit: int = 5,
        scope: RetrievalScope | None = None,
    ) -> UnifiedIndexSearchResponse:
        query_digests = self._query_token_digests(query)
        candidates = self._candidate_hits(query, limit=max(limit * 4, limit))
        hits: list[UnifiedIndexHit] = []
        candidate_open_count = 0

        if candidates:
            by_id = {candidate.memory_id: candidate for candidate in candidates}
            memories = [
                memory
                for candidate in candidates
                if (memory := self.get_memory(candidate.memory_id)) is not None
            ]
            candidate_open_count = len(memories)
            ranked = rank_memories(memories, query, limit=limit, scope=scope)
            for ranked_memory in ranked:
                candidate = by_id[ranked_memory.memory.memory_id]
                hits.append(
                    UnifiedIndexHit(
                        memory_id=ranked_memory.memory.memory_id,
                        score=round(max(ranked_memory.score.total, candidate.index_score), 4),
                        matched_token_digest_count=candidate.matched_token_digest_count,
                        graph_boosted=candidate.graph_boosted,
                        source_ref_count=len(ranked_memory.memory.source_refs),
                        status=ranked_memory.memory.status,
                        scope=ranked_memory.memory.scope,
                        sensitivity=ranked_memory.memory.sensitivity,
                        influence_level=ranked_memory.memory.influence_level,
                    )
                )

        return UnifiedIndexSearchResponse(
            hits=hits,
            receipt=UnifiedIndexSearchReceipt(
                query_digest_count=len(query_digests),
                considered_index_rows=self._memory_index_row_count(),
                candidate_open_count=candidate_open_count,
                result_count=len(hits),
            ),
        )

    def context_policy_refs(self) -> list[str]:
        return [UNIFIED_ENCRYPTED_GRAPH_INDEX_POLICY_REF]

    def _candidate_hits(self, query: str, *, limit: int) -> list[_CandidateHit]:
        if limit < 1:
            raise ValueError("limit must be at least 1")
        query_digests = self._query_token_digests(query)
        if not query_digests:
            return []
        query_set = set(query_digests)
        graph_boosted_ids = self._graph_boosted_memory_ids(query_set)
        candidates: list[_CandidateHit] = []
        with self._connect() as con:
            rows = con.execute(
                """
                SELECT memory_id, token_digests_json
                FROM redacted_memory_index
                WHERE status NOT IN (?, ?, ?)
                  AND influence_level != ?
                ORDER BY memory_id ASC
                """,
                (
                    MemoryStatus.DELETED.value,
                    MemoryStatus.REVOKED.value,
                    MemoryStatus.QUARANTINED.value,
                    int(InfluenceLevel.STORED_ONLY),
                ),
            ).fetchall()
        for row in rows:
            token_digests = set(json.loads(row["token_digests_json"]))
            overlap_count = len(query_set.intersection(token_digests))
            graph_boosted = row["memory_id"] in graph_boosted_ids
            if not overlap_count and not graph_boosted:
                continue
            index_score = min(
                1.0,
                (overlap_count / len(query_set)) * 0.86
                + (0.14 if graph_boosted else 0.0),
            )
            candidates.append(
                _CandidateHit(
                    memory_id=row["memory_id"],
                    index_score=round(index_score, 4),
                    matched_token_digest_count=overlap_count,
                    graph_boosted=graph_boosted,
                )
            )
        candidates.sort(key=lambda item: (-item.index_score, item.memory_id))
        return candidates[:limit]

    def _graph_boosted_memory_ids(self, query_digests: set[str]) -> set[str]:
        boosted: set[str] = set()
        with self._connect() as con:
            rows = con.execute(
                """
                SELECT related_memory_ids_json, token_digests_json
                FROM encrypted_graph_edges
                WHERE status NOT IN (?, ?, ?)
                """,
                (
                    MemoryStatus.DELETED.value,
                    MemoryStatus.REVOKED.value,
                    MemoryStatus.QUARANTINED.value,
                ),
            ).fetchall()
        for row in rows:
            edge_digests = set(json.loads(row["token_digests_json"]))
            if query_digests.intersection(edge_digests):
                boosted.update(json.loads(row["related_memory_ids_json"]))
        return boosted

    def _memory_token_digests(self, memory: MemoryRecord) -> set[str]:
        text = " ".join(
            [
                memory.content,
                memory.type.value,
                memory.scope.value,
                memory.status.value,
                *memory.allowed_influence,
                *memory.forbidden_influence,
            ]
        )
        return self._term_digests(text)

    def _graph_token_digests(self, edge: TemporalEdge) -> set[str]:
        return self._term_digests(
            " ".join([edge.subject, edge.predicate, edge.object, edge.status.value])
        )

    def _query_token_digests(self, query: str) -> list[str]:
        return sorted(self._term_digests(query))

    def _term_digests(self, text: str) -> set[str]:
        return {
            hmac.new(
                self.index_key,
                token.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
            for token in tokenize(text)
        }

    def _memory_index_row_count(self) -> int:
        with self._connect() as con:
            row = con.execute("SELECT COUNT(*) AS count FROM redacted_memory_index").fetchone()
        return int(row["count"])

    def _init_index_db(self) -> None:
        with self._connect() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS redacted_memory_index (
                    memory_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    sensitivity TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    influence_level INTEGER NOT NULL,
                    token_digests_json TEXT NOT NULL,
                    source_ref_count INTEGER NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS encrypted_graph_edges (
                    edge_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    related_memory_ids_json TEXT NOT NULL,
                    token_digests_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL,
                    payload_ciphertext BLOB NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con


def _normalize_index_key(index_key: bytes | str) -> bytes:
    key = index_key.encode("utf-8") if isinstance(index_key, str) else index_key
    if len(key) < 16:
        raise ValueError("unified index key must be at least 16 bytes")
    return key


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
