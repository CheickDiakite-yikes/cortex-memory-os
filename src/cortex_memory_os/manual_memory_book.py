"""Manual Memory Book service for the first real Cortex memory loop."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import sqlite3
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Sequence

from pydantic import Field, field_validator, model_validator

from cortex_memory_os.contracts import (
    AuditEvent,
    EvidenceType,
    InfluenceLevel,
    MemoryRecord,
    MemoryStatus,
    MemoryType,
    ScopeLevel,
    Sensitivity,
    StrictModel,
)
from cortex_memory_os.encrypted_graph_index import (
    UNIFIED_ENCRYPTED_GRAPH_INDEX_POLICY_REF,
    UnifiedEncryptedGraphIndex,
)
from cortex_memory_os.evidence_vault import BlobCipher, VaultRuntimeMode
from cortex_memory_os.firewall import detect_prompt_injection, redact_sensitive_text
from cortex_memory_os.memory_encryption import MEMORY_ENCRYPTION_DEFAULT_POLICY_REF
from cortex_memory_os.retrieval import RetrievalScope
from cortex_memory_os.sensitive_data_policy import SECRET_PII_POLICY_REF

MANUAL_MEMORY_BOOK_ID = "MANUAL-MEMORY-BOOK-001"
MANUAL_MEMORY_BOOK_POLICY_REF = "policy_manual_memory_book_v1"
MANUAL_MEMORY_BOOK_MAX_CHARS = 600
DEFAULT_MEMORY_BOOK_DB_PATH = (
    Path.home() / ".cortex-memory-os" / "memory-book.sqlite3"
)
_DEV_KEY = b"cortex-manual-memory-book-dev-key-v1-not-production"
_SEAL_PREFIX = b"cortex-manual-memory-book-v1:"
_SECRET_MARKERS = (
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GOOGLE_API_KEY",
    "GEMINI_API_KEY",
    "DEEPSEEK_API_KEY",
    "KIMI_API_KEY",
    "BEGIN PRIVATE KEY",
    "BEGIN RSA PRIVATE KEY",
    "password=",
    "passwd=",
    "sk-",
    "Bearer ",
)
_FORBIDDEN_INFLUENCE = [
    "tool_actions",
    "autonomous_workflows",
    "external_export",
    "financial_decisions",
    "medical_decisions",
    "legal_decisions",
]


class ManualMemoryRejectedError(ValueError):
    """Raised when manual memory text is unsafe to store."""


class DevAuthenticatedMemoryCipher:
    """Development-only authenticated cipher boundary for local demos.

    This is not a production cipher. It exists so the local Memory Book proves
    the encrypted-store interface and avoids plaintext SQLite payloads while
    the production Keychain/KMS-backed cipher is still a separate slice.
    """

    name = "manual-memory-dev-authenticated-xor-v1"
    authenticated_encryption = True

    def __init__(self, key: bytes = _DEV_KEY) -> None:
        self._key = key

    def seal(self, plaintext: bytes) -> bytes:
        nonce = os.urandom(16)
        ciphertext = _xor_with_stream(plaintext, self._key, nonce)
        tag = hmac.new(self._key, nonce + ciphertext, hashlib.sha256).digest()
        return _SEAL_PREFIX + nonce + tag + ciphertext

    def open(self, ciphertext: bytes) -> bytes:
        if not ciphertext.startswith(_SEAL_PREFIX):
            raise ValueError("missing manual memory seal")
        sealed = ciphertext.removeprefix(_SEAL_PREFIX)
        if len(sealed) < 48:
            raise ValueError("manual memory seal is too short")
        nonce = sealed[:16]
        tag = sealed[16:48]
        body = sealed[48:]
        expected = hmac.new(self._key, nonce + body, hashlib.sha256).digest()
        if not hmac.compare_digest(tag, expected):
            raise ValueError("manual memory seal failed authentication")
        return _xor_with_stream(body, self._key, nonce)


class ManualMemoryInput(StrictModel):
    text: str = Field(min_length=1, max_length=MANUAL_MEMORY_BOOK_MAX_CHARS)
    title: str | None = Field(default=None, max_length=80)
    scope: ScopeLevel = ScopeLevel.PROJECT_SPECIFIC

    @field_validator("text", "title")
    @classmethod
    def strip_visible_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return " ".join(value.strip().split())


class MemoryBookCard(StrictModel):
    memory_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    what_cortex_remembers: str = Field(min_length=1)
    why_it_exists: str = Field(min_length=1)
    where_it_can_be_used: str = Field(min_length=1)
    safety_status: str = Field(min_length=1)
    status: MemoryStatus
    scope: ScopeLevel
    influence_level: InfluenceLevel
    confidence: float = Field(ge=0.0, le=1.0)
    can_find: bool = True
    can_fix: bool = True
    can_forget: bool = True
    content_redacted_in_receipts: bool = True
    source_refs_redacted_in_receipts: bool = True


class ManualMemoryReceipt(StrictModel):
    receipt_id: str = Field(min_length=1)
    action: str = Field(min_length=1)
    memory_id: str = Field(min_length=1)
    result: str = Field(min_length=1)
    generated_at: datetime
    encrypted_store_used: bool = True
    authenticated_cipher_used: bool = True
    content_redacted: bool = True
    source_refs_redacted: bool = True
    raw_ref_retained: bool = False
    raw_payload_included: bool = False
    external_effect_enabled: bool = False
    blocked_effects: list[str] = Field(
        default_factory=lambda: [
            "screen_capture",
            "raw_ref_write",
            "secret_echo",
            "tool_action",
            "autonomous_workflow",
            "external_export",
        ]
    )
    policy_refs: list[str] = Field(
        default_factory=lambda: [
            MANUAL_MEMORY_BOOK_POLICY_REF,
            MEMORY_ENCRYPTION_DEFAULT_POLICY_REF,
            UNIFIED_ENCRYPTED_GRAPH_INDEX_POLICY_REF,
            SECRET_PII_POLICY_REF,
        ]
    )

    @model_validator(mode="after")
    def keep_receipt_safe(self) -> "ManualMemoryReceipt":
        if MANUAL_MEMORY_BOOK_POLICY_REF not in self.policy_refs:
            raise ValueError("manual memory receipt requires policy ref")
        if not self.encrypted_store_used or not self.authenticated_cipher_used:
            raise ValueError("manual memory writes require authenticated encrypted store")
        if not self.content_redacted or not self.source_refs_redacted:
            raise ValueError("manual memory receipts must redact content and source refs")
        if self.raw_ref_retained or self.raw_payload_included or self.external_effect_enabled:
            raise ValueError("manual memory receipts cannot retain raw refs or act externally")
        return self


class ManualMemorySaveResponse(StrictModel):
    card: MemoryBookCard
    receipt: ManualMemoryReceipt


class ManualMemoryListResponse(StrictModel):
    cards: list[MemoryBookCard]
    receipt: ManualMemoryReceipt


class ManualMemorySearchResponse(StrictModel):
    cards: list[MemoryBookCard]
    used_memory_ids: list[str]
    receipt: ManualMemoryReceipt
    query_redacted_in_receipt: bool = True


class ManualMemoryCorrectionResponse(StrictModel):
    old_memory_id: str = Field(min_length=1)
    card: MemoryBookCard
    receipt: ManualMemoryReceipt


class ManualMemoryForgetResponse(StrictModel):
    forgotten_memory_id: str = Field(min_length=1)
    receipt: ManualMemoryReceipt


class ManualMemoryAuditResponse(StrictModel):
    events: list[AuditEvent]
    receipt: ManualMemoryReceipt


class ManualMemoryBookService:
    """Local manual-memory brain loop backed by sealed payloads."""

    def __init__(
        self,
        db_path: str | Path | None = None,
        *,
        cipher: BlobCipher | None = None,
        index_key: bytes | str | None = None,
        active_project: str = "cortex-memory-os",
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self.db_path = Path(db_path or default_memory_book_db_path()).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.active_project = active_project
        self.now = now or (lambda: datetime.now(UTC))
        active_cipher = cipher or DevAuthenticatedMemoryCipher()
        active_index_key = index_key or hashlib.sha256(_DEV_KEY + b":index").digest()
        self.index = UnifiedEncryptedGraphIndex(
            self.db_path,
            cipher=active_cipher,
            index_key=active_index_key,
            mode=VaultRuntimeMode.DEVELOPMENT,
        )
        self._init_audit_db()

    def save(self, request: ManualMemoryInput) -> ManualMemorySaveResponse:
        timestamp = _ensure_utc(self.now())
        safe_text = _validate_safe_manual_text(request.text)
        memory = self._build_memory(
            text=safe_text,
            title=request.title,
            scope=request.scope,
            timestamp=timestamp,
        )
        self.index.add_memory(memory, now=timestamp)
        audit = self._audit_event(
            action="manual_memory.save",
            target_ref=memory.memory_id,
            timestamp=timestamp,
            result="saved",
            summary="User saved a manual memory to the encrypted local Memory Book.",
        )
        self._add_audit(audit)
        return ManualMemorySaveResponse(
            card=self._card(memory),
            receipt=self._receipt("save", memory.memory_id, "saved", timestamp),
        )

    def list_cards(self, *, limit: int = 20) -> ManualMemoryListResponse:
        timestamp = _ensure_utc(self.now())
        cards = [
            self._card(memory)
            for memory in self.index.memory_store.list_memories(status=MemoryStatus.ACTIVE)
            if _visible_manual_memory(memory)
        ][:limit]
        return ManualMemoryListResponse(
            cards=cards,
            receipt=self._receipt("list", "manual_memory_book", "listed", timestamp),
        )

    def search(self, query: str, *, limit: int = 5) -> ManualMemorySearchResponse:
        timestamp = _ensure_utc(self.now())
        safe_query = _validate_safe_manual_text(query)
        memories = self.index.search_memories(
            safe_query,
            limit=limit,
            scope=RetrievalScope(active_project=self.active_project),
        )
        cards = [self._card(memory) for memory in memories if _visible_manual_memory(memory)]
        return ManualMemorySearchResponse(
            cards=cards,
            used_memory_ids=[card.memory_id for card in cards],
            receipt=self._receipt("search", "manual_memory_book", "searched", timestamp),
        )

    def correct(
        self,
        memory_id: str,
        corrected: ManualMemoryInput,
    ) -> ManualMemoryCorrectionResponse:
        timestamp = _ensure_utc(self.now())
        original = self._require_active_memory(memory_id)
        safe_text = _validate_safe_manual_text(corrected.text)
        corrected_memory = self._build_memory(
            text=safe_text,
            title=corrected.title,
            scope=corrected.scope,
            timestamp=timestamp,
            source_refs=[f"manual:corrected:{original.memory_id}"],
        )
        tombstone = _tombstone_memory(
            original,
            content="This memory was corrected by the user and replaced.",
            timestamp=timestamp,
            replacement_id=corrected_memory.memory_id,
        )
        self.index.add_memory(tombstone, now=timestamp)
        self.index.add_memory(corrected_memory, now=timestamp)
        audit = self._audit_event(
            action="manual_memory.correct",
            target_ref=original.memory_id,
            timestamp=timestamp,
            result="corrected",
            summary="User corrected a manual memory; the old payload was replaced.",
        )
        self._add_audit(audit)
        return ManualMemoryCorrectionResponse(
            old_memory_id=original.memory_id,
            card=self._card(corrected_memory),
            receipt=self._receipt(
                "correct",
                corrected_memory.memory_id,
                "corrected",
                timestamp,
            ),
        )

    def forget(self, memory_id: str, *, confirm_forget: bool) -> ManualMemoryForgetResponse:
        timestamp = _ensure_utc(self.now())
        if not confirm_forget:
            raise ManualMemoryRejectedError("forget requires explicit confirmation")
        original = self._require_active_memory(memory_id)
        tombstone = _tombstone_memory(
            original,
            content="This memory was forgotten by the user.",
            timestamp=timestamp,
        )
        self.index.add_memory(tombstone, now=timestamp)
        audit = self._audit_event(
            action="manual_memory.forget",
            target_ref=original.memory_id,
            timestamp=timestamp,
            result="forgotten",
            summary="User forgot a manual memory; active recall was removed.",
        )
        self._add_audit(audit)
        return ManualMemoryForgetResponse(
            forgotten_memory_id=original.memory_id,
            receipt=self._receipt("forget", original.memory_id, "forgotten", timestamp),
        )

    def audit_events(self, *, limit: int = 20) -> ManualMemoryAuditResponse:
        timestamp = _ensure_utc(self.now())
        with self._connect() as con:
            rows = con.execute(
                """
                SELECT payload_json
                FROM manual_memory_audit
                ORDER BY timestamp DESC, audit_event_id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return ManualMemoryAuditResponse(
            events=[AuditEvent.model_validate_json(row["payload_json"]) for row in rows],
            receipt=self._receipt("audit", "manual_memory_book", "listed_audit", timestamp),
        )

    def _build_memory(
        self,
        *,
        text: str,
        title: str | None,
        scope: ScopeLevel,
        timestamp: datetime,
        source_refs: list[str] | None = None,
    ) -> MemoryRecord:
        digest = hashlib.sha256(f"{timestamp.isoformat()}:{text}".encode()).hexdigest()
        return MemoryRecord(
            memory_id=f"mem_manual_{timestamp.strftime('%Y%m%dT%H%M%SZ')}_{digest[:10]}",
            type=MemoryType.PROJECT,
            content=text,
            source_refs=source_refs or ["manual:user_confirmed"],
            evidence_type=EvidenceType.USER_CONFIRMED,
            confidence=1.0,
            status=MemoryStatus.ACTIVE,
            created_at=timestamp,
            valid_from=timestamp.date(),
            valid_to=None,
            sensitivity=Sensitivity.PRIVATE_WORK,
            scope=scope,
            influence_level=InfluenceLevel.DIRECT_QUERY,
            allowed_influence=["direct_memory_search"],
            forbidden_influence=list(_FORBIDDEN_INFLUENCE),
            decay_policy="user_managed",
            contradicts=[],
            user_visible=True,
            requires_user_confirmation=False,
        )

    def _card(self, memory: MemoryRecord) -> MemoryBookCard:
        return MemoryBookCard(
            memory_id=memory.memory_id,
            title=_memory_title(memory),
            what_cortex_remembers=memory.content,
            why_it_exists="You saved this yourself.",
            where_it_can_be_used="Only when you ask Cortex to remember or find it.",
            safety_status="Encrypted locally. No screen capture, raw refs, or actions.",
            status=memory.status,
            scope=memory.scope,
            influence_level=memory.influence_level,
            confidence=memory.confidence,
        )

    def _require_active_memory(self, memory_id: str) -> MemoryRecord:
        memory = self.index.get_memory(memory_id)
        if memory is None or not _visible_manual_memory(memory):
            raise KeyError(memory_id)
        return memory

    def _audit_event(
        self,
        *,
        action: str,
        target_ref: str,
        timestamp: datetime,
        result: str,
        summary: str,
    ) -> AuditEvent:
        return AuditEvent(
            audit_event_id=(
                f"audit_{action.replace('.', '_')}_{_safe_id_fragment(target_ref)}_"
                f"{timestamp.strftime('%Y%m%dT%H%M%SZ')}"
            ),
            timestamp=timestamp,
            actor="user",
            action=action,
            target_ref=target_ref,
            policy_refs=[MANUAL_MEMORY_BOOK_POLICY_REF],
            result=result,
            human_visible=True,
            redacted_summary=summary,
        )

    def _receipt(
        self,
        action: str,
        memory_id: str,
        result: str,
        timestamp: datetime,
    ) -> ManualMemoryReceipt:
        return ManualMemoryReceipt(
            receipt_id=f"receipt_manual_memory_{action}_{timestamp.strftime('%Y%m%dT%H%M%SZ')}",
            action=action,
            memory_id=memory_id,
            result=result,
            generated_at=timestamp,
        )

    def _add_audit(self, event: AuditEvent) -> None:
        with self._connect() as con:
            con.execute(
                """
                INSERT INTO manual_memory_audit (
                    audit_event_id, timestamp, action, target_ref, payload_json
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(audit_event_id) DO UPDATE SET
                    timestamp = excluded.timestamp,
                    action = excluded.action,
                    target_ref = excluded.target_ref,
                    payload_json = excluded.payload_json
                """,
                (
                    event.audit_event_id,
                    event.timestamp.isoformat(),
                    event.action,
                    event.target_ref,
                    event.model_dump_json(),
                ),
            )

    def _init_audit_db(self) -> None:
        with self._connect() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS manual_memory_audit (
                    audit_event_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    action TEXT NOT NULL,
                    target_ref TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        return con


def default_memory_book_db_path() -> Path:
    configured = os.environ.get("CORTEX_MEMORY_BOOK_DB")
    if configured:
        return Path(configured).expanduser()
    return DEFAULT_MEMORY_BOOK_DB_PATH


def _validate_safe_manual_text(text: str) -> str:
    compact = " ".join(text.strip().split())
    if not compact:
        raise ManualMemoryRejectedError("memory text cannot be empty")
    if len(compact) > MANUAL_MEMORY_BOOK_MAX_CHARS:
        raise ManualMemoryRejectedError("memory text is too long")
    if detect_prompt_injection(compact):
        raise ManualMemoryRejectedError("prompt-injection-like text cannot be saved")
    redacted, redactions = redact_sensitive_text(compact)
    if redactions or redacted != compact:
        raise ManualMemoryRejectedError("secret-like text cannot be saved")
    lowered = compact.lower()
    if any(marker.lower() in lowered for marker in _SECRET_MARKERS):
        raise ManualMemoryRejectedError("secret-like text cannot be saved")
    return compact


def _visible_manual_memory(memory: MemoryRecord) -> bool:
    return (
        memory.status == MemoryStatus.ACTIVE
        and memory.influence_level == InfluenceLevel.DIRECT_QUERY
        and memory.evidence_type == EvidenceType.USER_CONFIRMED
        and memory.user_visible
    )


def _tombstone_memory(
    memory: MemoryRecord,
    *,
    content: str,
    timestamp: datetime,
    replacement_id: str | None = None,
) -> MemoryRecord:
    return memory.model_copy(
        update={
            "content": content,
            "source_refs": [
                "manual:memory_lifecycle_tombstone",
                *(["manual:replacement:" + replacement_id] if replacement_id else []),
            ],
            "evidence_type": EvidenceType.USER_CONFIRMED,
            "confidence": 1.0,
            "status": MemoryStatus.SUPERSEDED,
            "created_at": timestamp,
            "valid_to": timestamp.date(),
            "influence_level": InfluenceLevel.STORED_ONLY,
            "allowed_influence": [],
            "forbidden_influence": list(_FORBIDDEN_INFLUENCE),
            "contradicts": [replacement_id] if replacement_id else [],
            "requires_user_confirmation": False,
        }
    )


def _memory_title(memory: MemoryRecord) -> str:
    words = memory.content.split()
    title = " ".join(words[:7])
    return title if len(title) <= 72 else title[:69].rstrip() + "..."


def _safe_id_fragment(value: str) -> str:
    return "".join(character if character.isalnum() else "_" for character in value)[:80]


def _xor_with_stream(payload: bytes, key: bytes, nonce: bytes) -> bytes:
    output = bytearray()
    counter = 0
    while len(output) < len(payload):
        block = hashlib.sha256(key + nonce + counter.to_bytes(8, "big")).digest()
        output.extend(block)
        counter += 1
    return bytes(byte ^ stream for byte, stream in zip(payload, output, strict=False))


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--db", type=Path, default=None)
    return parser.parse_args(argv)


def run_manual_memory_book_smoke(db_path: Path | None = None) -> dict[str, object]:
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        service = ManualMemoryBookService(db_path or Path(temp_dir) / "memory.sqlite3")
        saved = service.save(
            ManualMemoryInput(text="Cortex should keep the dashboard simple.")
        )
        searched = service.search("dashboard simple")
        corrected = service.correct(
            saved.card.memory_id,
            ManualMemoryInput(text="Cortex should keep the Memory Book simple."),
        )
        forgotten = service.forget(corrected.card.memory_id, confirm_forget=True)
        after_forget = service.search("Memory Book simple")
        audit = service.audit_events()
        return {
            "passed": (
                saved.card.memory_id in searched.used_memory_ids
                and corrected.card.memory_id != saved.card.memory_id
                and forgotten.forgotten_memory_id == corrected.card.memory_id
                and after_forget.used_memory_ids == []
                and len(audit.events) == 3
            ),
            "saved_memory_id": saved.card.memory_id,
            "corrected_memory_id": corrected.card.memory_id,
            "after_forget_count": len(after_forget.cards),
            "audit_count": len(audit.events),
            "encrypted_store_used": saved.receipt.encrypted_store_used,
            "content_redacted": saved.receipt.content_redacted,
            "raw_ref_retained": saved.receipt.raw_ref_retained,
        }


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.smoke:
        result = run_manual_memory_book_smoke(args.db)
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(f"{MANUAL_MEMORY_BOOK_ID}: passed={result['passed']}")
        return 0 if result["passed"] else 1
    print(default_memory_book_db_path())
    return 0
