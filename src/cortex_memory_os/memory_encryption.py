"""Encrypted-by-default storage boundary for durable memory records."""

from __future__ import annotations

import hashlib
import sqlite3
from collections.abc import Iterable
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
)
from cortex_memory_os.evidence_vault import (
    BlobCipher,
    NoopDevCipher,
    VaultRuntimeMode,
    assess_vault_cipher,
)
from cortex_memory_os.retrieval import RankedMemory, RetrievalScope, rank_memories

MEMORY_ENCRYPTION_DEFAULT_ID = "MEMORY-ENCRYPTION-DEFAULT-001"
MEMORY_ENCRYPTION_DEFAULT_POLICY_REF = "policy_memory_encryption_default_v1"

_NON_DURABLE_SCOPES = {
    ScopeLevel.SESSION_ONLY,
    ScopeLevel.EPHEMERAL,
    ScopeLevel.NEVER_STORE,
}
_CONTENT_BLOCKED_STATUSES = {
    MemoryStatus.DELETED,
    MemoryStatus.REVOKED,
    MemoryStatus.QUARANTINED,
}
_SENSITIVE_DURABLE_LEVELS = {
    Sensitivity.PRIVATE_WORK,
    Sensitivity.CONFIDENTIAL,
    Sensitivity.REGULATED,
    Sensitivity.SECRET,
}


class MemoryEncryptionDecision(StrictModel):
    memory_id: str = Field(min_length=1)
    durable_write: bool
    sensitivity: Sensitivity
    scope: ScopeLevel
    status: MemoryStatus
    influence_level: InfluenceLevel
    sensitive_durable: bool
    requires_authenticated_encryption: bool
    cipher_name: str = Field(min_length=1)
    cipher_authenticated: bool
    cipher_allowed_for_runtime: bool
    allowed: bool
    reason: str = Field(min_length=1)
    allowed_effects: list[str] = Field(default_factory=list)
    blocked_effects: list[str] = Field(default_factory=list)
    content_redacted: bool = True
    source_refs_redacted: bool = True
    policy_refs: list[str] = Field(
        default_factory=lambda: [MEMORY_ENCRYPTION_DEFAULT_POLICY_REF]
    )

    @model_validator(mode="after")
    def keep_decision_safe_and_consistent(self) -> MemoryEncryptionDecision:
        if not self.content_redacted:
            raise ValueError("memory encryption decisions cannot include memory content")
        if not self.source_refs_redacted:
            raise ValueError("memory encryption decisions cannot include source refs")
        if MEMORY_ENCRYPTION_DEFAULT_POLICY_REF not in self.policy_refs:
            raise ValueError("memory encryption decisions require policy ref")
        if self.allowed and not self.durable_write:
            raise ValueError("encrypted durable store cannot allow non-durable writes")
        if self.allowed and not self.cipher_allowed_for_runtime:
            raise ValueError("allowed memory write requires runtime-allowed cipher")
        if self.allowed and self.requires_authenticated_encryption:
            if not self.cipher_authenticated:
                raise ValueError("durable memory writes require authenticated encryption")
        if self.allowed and "write_plaintext_memory_payload" in self.allowed_effects:
            raise ValueError("durable memory writes cannot allow plaintext payload storage")
        return self


class MemoryStorageReceipt(StrictModel):
    memory_id: str = Field(min_length=1)
    stored_at: datetime
    cipher_name: str = Field(min_length=1)
    payload_sha256: str = Field(min_length=64, max_length=64)
    sealed_byte_count: int = Field(ge=1)
    decision: MemoryEncryptionDecision
    content_redacted: bool = True
    source_refs_redacted: bool = True
    policy_refs: list[str] = Field(
        default_factory=lambda: [MEMORY_ENCRYPTION_DEFAULT_POLICY_REF]
    )

    @model_validator(mode="after")
    def keep_receipt_non_leaky(self) -> MemoryStorageReceipt:
        if not self.content_redacted:
            raise ValueError("memory storage receipts cannot include memory content")
        if not self.source_refs_redacted:
            raise ValueError("memory storage receipts cannot include source refs")
        if MEMORY_ENCRYPTION_DEFAULT_POLICY_REF not in self.policy_refs:
            raise ValueError("memory storage receipts require policy ref")
        if not self.decision.allowed:
            raise ValueError("successful memory storage receipt requires allowed decision")
        return self


class MemoryEncryptionRequiredError(RuntimeError):
    """Raised when a durable memory write does not meet encryption policy."""

    def __init__(self, decision: MemoryEncryptionDecision) -> None:
        self.decision = decision
        super().__init__(
            "memory durable write rejected: "
            f"memory_id={decision.memory_id} reason={decision.reason} "
            f"cipher={decision.cipher_name}"
        )


class EncryptedMemoryStore:
    """SQLite-backed memory store that seals memory payload JSON by default."""

    def __init__(
        self,
        db_path: str | Path,
        *,
        cipher: BlobCipher | None = None,
        mode: VaultRuntimeMode | str = VaultRuntimeMode.DEVELOPMENT,
    ) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.cipher = cipher or NoopDevCipher()
        self.mode = VaultRuntimeMode(mode)
        self.cipher_decision = assess_vault_cipher(self.cipher, self.mode)
        if not self.cipher_decision.allowed:
            raise ValueError(
                f"memory cipher rejected for {self.mode.value}: "
                f"{self.cipher_decision.reason}"
            )
        self._init_db()

    def add_memory(
        self,
        memory: MemoryRecord,
        *,
        now: datetime | None = None,
    ) -> MemoryStorageReceipt:
        decision = assess_memory_encryption_default(memory, self.cipher, self.mode)
        if not decision.allowed:
            raise MemoryEncryptionRequiredError(decision)

        plaintext = memory.model_dump_json().encode("utf-8")
        sealed = self.cipher.seal(plaintext)
        payload_sha256 = hashlib.sha256(plaintext).hexdigest()
        stored_at = _ensure_utc(now or datetime.now(UTC))
        with self._connect() as con:
            con.execute(
                """
                INSERT INTO encrypted_memories (
                    memory_id, status, sensitivity, scope, influence_level,
                    valid_from, valid_to, cipher, payload_sha256,
                    payload_ciphertext, stored_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(memory_id) DO UPDATE SET
                    status = excluded.status,
                    sensitivity = excluded.sensitivity,
                    scope = excluded.scope,
                    influence_level = excluded.influence_level,
                    valid_from = excluded.valid_from,
                    valid_to = excluded.valid_to,
                    cipher = excluded.cipher,
                    payload_sha256 = excluded.payload_sha256,
                    payload_ciphertext = excluded.payload_ciphertext,
                    updated_at = excluded.updated_at
                """,
                (
                    memory.memory_id,
                    memory.status.value,
                    memory.sensitivity.value,
                    memory.scope.value,
                    int(memory.influence_level),
                    memory.valid_from.isoformat(),
                    memory.valid_to.isoformat() if memory.valid_to else None,
                    self.cipher.name,
                    payload_sha256,
                    sealed,
                    stored_at.isoformat(),
                    stored_at.isoformat(),
                ),
            )

        return MemoryStorageReceipt(
            memory_id=memory.memory_id,
            stored_at=stored_at,
            cipher_name=self.cipher.name,
            payload_sha256=payload_sha256,
            sealed_byte_count=len(sealed),
            decision=decision,
            content_redacted=True,
            source_refs_redacted=True,
            policy_refs=[MEMORY_ENCRYPTION_DEFAULT_POLICY_REF],
        )

    def add_memories(self, memories: Iterable[MemoryRecord]) -> list[MemoryStorageReceipt]:
        return [self.add_memory(memory) for memory in memories]

    def get_memory(self, memory_id: str) -> MemoryRecord | None:
        with self._connect() as con:
            row = con.execute(
                """
                SELECT payload_sha256, payload_ciphertext
                FROM encrypted_memories
                WHERE memory_id = ?
                """,
                (memory_id,),
            ).fetchone()
        if row is None:
            return None
        plaintext = self.cipher.open(row["payload_ciphertext"])
        if hashlib.sha256(plaintext).hexdigest() != row["payload_sha256"]:
            raise ValueError(f"memory payload checksum mismatch: {memory_id}")
        return MemoryRecord.model_validate_json(plaintext)

    def list_memories(self, *, status: MemoryStatus | None = None) -> list[MemoryRecord]:
        with self._connect() as con:
            if status is None:
                rows = con.execute(
                    """
                    SELECT memory_id
                    FROM encrypted_memories
                    ORDER BY status ASC, memory_id ASC
                    """
                ).fetchall()
            else:
                rows = con.execute(
                    """
                    SELECT memory_id
                    FROM encrypted_memories
                    WHERE status = ?
                    ORDER BY memory_id ASC
                    """,
                    (status.value,),
                ).fetchall()
        return [
            memory
            for row in rows
            if (memory := self.get_memory(row["memory_id"])) is not None
        ]

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
        return rank_memories(self.list_memories(), query, limit=limit, scope=scope)

    def _init_db(self) -> None:
        with self._connect() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS encrypted_memories (
                    memory_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    sensitivity TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    influence_level INTEGER NOT NULL,
                    valid_from TEXT NOT NULL,
                    valid_to TEXT,
                    cipher TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL,
                    payload_ciphertext BLOB NOT NULL,
                    stored_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con


def assess_memory_encryption_default(
    memory: MemoryRecord,
    cipher: BlobCipher | None = None,
    mode: VaultRuntimeMode | str = VaultRuntimeMode.DEVELOPMENT,
) -> MemoryEncryptionDecision:
    runtime_mode = VaultRuntimeMode(mode)
    selected_cipher = cipher or NoopDevCipher()
    cipher_decision = assess_vault_cipher(selected_cipher, runtime_mode)
    durable_write = _is_durable_content_write(memory)
    sensitive_durable = (
        durable_write
        and (
            memory.sensitivity in _SENSITIVE_DURABLE_LEVELS
            or memory.influence_level >= InfluenceLevel.PLANNING
        )
    )
    requires_authenticated_encryption = durable_write
    cipher_authenticated = bool(
        getattr(selected_cipher, "authenticated_encryption", False)
    )

    if memory.scope in _NON_DURABLE_SCOPES:
        return _decision(
            memory,
            selected_cipher,
            durable_write=durable_write,
            sensitive_durable=sensitive_durable,
            requires_authenticated_encryption=requires_authenticated_encryption,
            cipher_allowed_for_runtime=cipher_decision.allowed,
            cipher_authenticated=cipher_authenticated,
            allowed=False,
            reason="non_durable_scope_cannot_write_to_encrypted_store",
            allowed_effects=["keep_ephemeral_in_memory_only"],
            blocked_effects=[
                "write_durable_memory_record",
                "write_plaintext_memory_payload",
            ],
        )

    if memory.status in _CONTENT_BLOCKED_STATUSES:
        return _decision(
            memory,
            selected_cipher,
            durable_write=durable_write,
            sensitive_durable=sensitive_durable,
            requires_authenticated_encryption=requires_authenticated_encryption,
            cipher_allowed_for_runtime=cipher_decision.allowed,
            cipher_authenticated=cipher_authenticated,
            allowed=False,
            reason="memory_status_cannot_write_content_to_durable_store",
            allowed_effects=["store_redacted_tombstone_metadata_elsewhere"],
            blocked_effects=[
                "write_durable_memory_record",
                "write_plaintext_memory_payload",
            ],
        )

    if not cipher_decision.allowed:
        return _decision(
            memory,
            selected_cipher,
            durable_write=durable_write,
            sensitive_durable=sensitive_durable,
            requires_authenticated_encryption=requires_authenticated_encryption,
            cipher_allowed_for_runtime=False,
            cipher_authenticated=cipher_authenticated,
            allowed=False,
            reason=cipher_decision.reason,
            allowed_effects=[],
            blocked_effects=[
                "write_durable_memory_record",
                "write_plaintext_memory_payload",
            ],
        )

    if requires_authenticated_encryption and not cipher_authenticated:
        return _decision(
            memory,
            selected_cipher,
            durable_write=durable_write,
            sensitive_durable=sensitive_durable,
            requires_authenticated_encryption=requires_authenticated_encryption,
            cipher_allowed_for_runtime=True,
            cipher_authenticated=False,
            allowed=False,
            reason="authenticated_encryption_required_for_durable_memory",
            allowed_effects=["store_redacted_metadata_only"],
            blocked_effects=[
                "write_durable_memory_record",
                "write_plaintext_memory_payload",
                "export_unencrypted_memory",
            ],
        )

    return _decision(
        memory,
        selected_cipher,
        durable_write=durable_write,
        sensitive_durable=sensitive_durable,
        requires_authenticated_encryption=requires_authenticated_encryption,
        cipher_allowed_for_runtime=True,
        cipher_authenticated=True,
        allowed=True,
        reason="durable_memory_authenticated_encryption_satisfied",
        allowed_effects=[
            "write_sealed_memory_payload",
            "store_redacted_index_metadata",
            "open_payload_after_authorized_read",
        ],
        blocked_effects=[
            "write_plaintext_memory_payload",
            "store_raw_source_refs_outside_ciphertext",
            "export_unencrypted_memory",
        ],
    )


def _is_durable_content_write(memory: MemoryRecord) -> bool:
    return memory.scope not in _NON_DURABLE_SCOPES and memory.status not in _CONTENT_BLOCKED_STATUSES


def _decision(
    memory: MemoryRecord,
    cipher: BlobCipher,
    *,
    durable_write: bool,
    sensitive_durable: bool,
    requires_authenticated_encryption: bool,
    cipher_allowed_for_runtime: bool,
    cipher_authenticated: bool,
    allowed: bool,
    reason: str,
    allowed_effects: list[str],
    blocked_effects: list[str],
) -> MemoryEncryptionDecision:
    return MemoryEncryptionDecision(
        memory_id=memory.memory_id,
        durable_write=durable_write,
        sensitivity=memory.sensitivity,
        scope=memory.scope,
        status=memory.status,
        influence_level=memory.influence_level,
        sensitive_durable=sensitive_durable,
        requires_authenticated_encryption=requires_authenticated_encryption,
        cipher_name=cipher.name,
        cipher_authenticated=cipher_authenticated,
        cipher_allowed_for_runtime=cipher_allowed_for_runtime,
        allowed=allowed,
        reason=reason,
        allowed_effects=allowed_effects,
        blocked_effects=blocked_effects,
        content_redacted=True,
        source_refs_redacted=True,
        policy_refs=[MEMORY_ENCRYPTION_DEFAULT_POLICY_REF],
    )


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
