"""Local evidence vault skeleton with retention and checksum metadata."""

from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field

from cortex_memory_os.contracts import EvidenceRecord, RetentionPolicy

EVIDENCE_VAULT_ENCRYPTION_POLICY_REF = "policy_evidence_vault_encryption_v1"


class VaultRuntimeMode(str, Enum):
    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


class BlobCipher(Protocol):
    name: str
    authenticated_encryption: bool

    def seal(self, plaintext: bytes) -> bytes:
        ...

    def open(self, ciphertext: bytes) -> bytes:
        ...


class NoopDevCipher:
    """Development-only cipher boundary.

    This keeps the vault interface encryption-ready without claiming real encryption.
    Production must replace this with a Keychain-backed cipher.
    """

    name = "noop-dev"
    authenticated_encryption = False

    def seal(self, plaintext: bytes) -> bytes:
        return plaintext

    def open(self, ciphertext: bytes) -> bytes:
        return ciphertext


@dataclass(frozen=True)
class VaultCipherDecision:
    mode: VaultRuntimeMode
    cipher_name: str
    allowed: bool
    reason: str
    policy_ref: str = EVIDENCE_VAULT_ENCRYPTION_POLICY_REF


class EvidenceVaultMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str
    raw_ref: str | None
    blob_path: str | None
    sha256: str | None
    byte_count: int
    retention_policy: RetentionPolicy
    created_at: datetime
    expires_at: datetime | None
    raw_deleted_at: datetime | None = None
    cipher: str = Field(min_length=1)


class EvidenceVault:
    def __init__(
        self,
        root: Path,
        *,
        cipher: BlobCipher | None = None,
        mode: VaultRuntimeMode | str = VaultRuntimeMode.DEVELOPMENT,
    ) -> None:
        self.root = root
        self.blob_dir = root / "blobs"
        self.db_path = root / "evidence.sqlite3"
        self.cipher = cipher or NoopDevCipher()
        self.mode = VaultRuntimeMode(mode)
        self.cipher_decision = assess_vault_cipher(self.cipher, self.mode)
        if not self.cipher_decision.allowed:
            raise ValueError(
                f"vault cipher rejected for {self.mode.value}: {self.cipher_decision.reason}"
            )
        self.root.mkdir(parents=True, exist_ok=True)
        self.blob_dir.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def store(
        self,
        evidence: EvidenceRecord,
        payload: bytes,
        *,
        now: datetime | None = None,
    ) -> EvidenceVaultMetadata:
        created_at = _ensure_utc(now or evidence.timestamp)
        expires_at = expires_at_for(evidence.retention_policy, created_at)

        if evidence.retention_policy == RetentionPolicy.DISCARD:
            metadata = EvidenceVaultMetadata(
                evidence_id=evidence.evidence_id,
                raw_ref=None,
                blob_path=None,
                sha256=None,
                byte_count=0,
                retention_policy=evidence.retention_policy,
                created_at=created_at,
                expires_at=created_at,
                raw_deleted_at=created_at,
                cipher=self.cipher.name,
            )
            self._upsert_metadata(metadata)
            return metadata

        sealed = self.cipher.seal(payload)
        blob_path = self.blob_dir / f"{evidence.evidence_id}.blob"
        blob_path.write_bytes(sealed)

        metadata = EvidenceVaultMetadata(
            evidence_id=evidence.evidence_id,
            raw_ref=f"vault://evidence/{evidence.evidence_id}",
            blob_path=str(blob_path.relative_to(self.root)),
            sha256=hashlib.sha256(payload).hexdigest(),
            byte_count=len(payload),
            retention_policy=evidence.retention_policy,
            created_at=created_at,
            expires_at=expires_at,
            raw_deleted_at=None,
            cipher=self.cipher.name,
        )
        self._upsert_metadata(metadata)
        return metadata

    def read_raw(self, evidence_id: str, *, now: datetime | None = None) -> bytes | None:
        metadata = self.get_metadata(evidence_id)
        if metadata is None or metadata.raw_deleted_at is not None or metadata.blob_path is None:
            return None

        current = _ensure_utc(now or datetime.now(UTC))
        if metadata.expires_at is not None and metadata.expires_at <= current:
            self.expire(current)
            return None

        blob = (self.root / metadata.blob_path).read_bytes()
        plaintext = self.cipher.open(blob)
        if hashlib.sha256(plaintext).hexdigest() != metadata.sha256:
            raise ValueError(f"evidence blob checksum mismatch: {evidence_id}")
        return plaintext

    def expire(self, now: datetime | None = None) -> list[str]:
        current = _ensure_utc(now or datetime.now(UTC))
        expired_ids: list[str] = []

        with self._connect() as con:
            rows = con.execute(
                """
                SELECT evidence_id, blob_path
                FROM evidence_metadata
                WHERE raw_deleted_at IS NULL
                  AND expires_at IS NOT NULL
                  AND expires_at <= ?
                """,
                (current.isoformat(),),
            ).fetchall()

            for evidence_id, blob_path in rows:
                if blob_path:
                    path = self.root / blob_path
                    if path.exists():
                        path.unlink()
                con.execute(
                    """
                    UPDATE evidence_metadata
                    SET raw_deleted_at = ?, raw_ref = NULL, blob_path = NULL
                    WHERE evidence_id = ?
                    """,
                    (current.isoformat(), evidence_id),
                )
                expired_ids.append(evidence_id)

        return expired_ids

    def get_metadata(self, evidence_id: str) -> EvidenceVaultMetadata | None:
        with self._connect() as con:
            row = con.execute(
                """
                SELECT evidence_id, raw_ref, blob_path, sha256, byte_count,
                       retention_policy, created_at, expires_at, raw_deleted_at, cipher
                FROM evidence_metadata
                WHERE evidence_id = ?
                """,
                (evidence_id,),
            ).fetchone()

        if row is None:
            return None

        return EvidenceVaultMetadata(
            evidence_id=row[0],
            raw_ref=row[1],
            blob_path=row[2],
            sha256=row[3],
            byte_count=row[4],
            retention_policy=row[5],
            created_at=row[6],
            expires_at=row[7],
            raw_deleted_at=row[8],
            cipher=row[9],
        )

    def _init_db(self) -> None:
        with self._connect() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS evidence_metadata (
                    evidence_id TEXT PRIMARY KEY,
                    raw_ref TEXT,
                    blob_path TEXT,
                    sha256 TEXT,
                    byte_count INTEGER NOT NULL,
                    retention_policy TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT,
                    raw_deleted_at TEXT,
                    cipher TEXT NOT NULL
                )
                """
            )

    def _upsert_metadata(self, metadata: EvidenceVaultMetadata) -> None:
        with self._connect() as con:
            con.execute(
                """
                INSERT INTO evidence_metadata (
                    evidence_id, raw_ref, blob_path, sha256, byte_count,
                    retention_policy, created_at, expires_at, raw_deleted_at, cipher
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(evidence_id) DO UPDATE SET
                    raw_ref = excluded.raw_ref,
                    blob_path = excluded.blob_path,
                    sha256 = excluded.sha256,
                    byte_count = excluded.byte_count,
                    retention_policy = excluded.retention_policy,
                    created_at = excluded.created_at,
                    expires_at = excluded.expires_at,
                    raw_deleted_at = excluded.raw_deleted_at,
                    cipher = excluded.cipher
                """,
                (
                    metadata.evidence_id,
                    metadata.raw_ref,
                    metadata.blob_path,
                    metadata.sha256,
                    metadata.byte_count,
                    metadata.retention_policy.value,
                    metadata.created_at.isoformat(),
                    metadata.expires_at.isoformat() if metadata.expires_at else None,
                    metadata.raw_deleted_at.isoformat() if metadata.raw_deleted_at else None,
                    metadata.cipher,
                ),
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)


def expires_at_for(policy: RetentionPolicy, created_at: datetime) -> datetime | None:
    if policy == RetentionPolicy.DISCARD:
        return created_at
    if policy == RetentionPolicy.EPHEMERAL_SESSION:
        return created_at
    if policy == RetentionPolicy.DELETE_RAW_AFTER_10M:
        return created_at + timedelta(minutes=10)
    if policy == RetentionPolicy.DELETE_RAW_AFTER_6H:
        return created_at + timedelta(hours=6)
    if policy == RetentionPolicy.KEEP_DERIVED_30D:
        return created_at + timedelta(days=30)
    return None


def assess_vault_cipher(
    cipher: BlobCipher,
    mode: VaultRuntimeMode | str,
) -> VaultCipherDecision:
    runtime_mode = VaultRuntimeMode(mode)
    cipher_name = cipher.name
    authenticated = bool(getattr(cipher, "authenticated_encryption", False))

    if runtime_mode == VaultRuntimeMode.PRODUCTION:
        if cipher_name == NoopDevCipher.name:
            return VaultCipherDecision(
                mode=runtime_mode,
                cipher_name=cipher_name,
                allowed=False,
                reason="noop_dev_cipher_forbidden_in_production",
            )
        if not authenticated:
            return VaultCipherDecision(
                mode=runtime_mode,
                cipher_name=cipher_name,
                allowed=False,
                reason="cipher_must_advertise_authenticated_encryption",
            )
        return VaultCipherDecision(
            mode=runtime_mode,
            cipher_name=cipher_name,
            allowed=True,
            reason="production_cipher_boundary_satisfied",
        )

    if cipher_name == NoopDevCipher.name:
        return VaultCipherDecision(
            mode=runtime_mode,
            cipher_name=cipher_name,
            allowed=True,
            reason="noop_dev_cipher_allowed_only_outside_production",
        )
    if authenticated:
        return VaultCipherDecision(
            mode=runtime_mode,
            cipher_name=cipher_name,
            allowed=True,
            reason="authenticated_cipher_allowed",
        )
    return VaultCipherDecision(
        mode=runtime_mode,
        cipher_name=cipher_name,
        allowed=True,
        reason="non_production_cipher_allowed_for_tests_only",
    )


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
