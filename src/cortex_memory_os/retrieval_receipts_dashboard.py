"""Dashboard-safe retrieval explanation receipt cards."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from datetime import UTC, datetime

from pydantic import Field, model_validator

from cortex_memory_os.contracts import (
    RETRIEVAL_EXPLANATION_POLICY_REF,
    RetrievalExplanationReceipt,
    StrictModel,
)
from cortex_memory_os.retrieval_explanations import RETRIEVAL_EXPLANATION_RECEIPTS_ID

RETRIEVAL_RECEIPTS_DASHBOARD_SURFACE_ID = "RETRIEVAL-RECEIPTS-DASHBOARD-SURFACE-001"
RETRIEVAL_RECEIPTS_DASHBOARD_POLICY_REF = "policy_retrieval_receipts_dashboard_v1"


class RetrievalReceiptCard(StrictModel):
    card_id: str = Field(min_length=1)
    memory_id: str = Field(min_length=1)
    decision: str = Field(min_length=1)
    rank: int | None = Field(default=None, ge=1)
    score: float = Field(ge=0.0, le=1.0)
    reason_tags: list[str] = Field(min_length=1)
    source_ref_count: int = Field(ge=0)
    source_refs_redacted: bool = True
    content_redacted: bool = True
    content_included: bool = False
    hostile_text_included: bool = False
    policy_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def keep_card_non_leaky(self) -> RetrievalReceiptCard:
        if not self.source_refs_redacted:
            raise ValueError("retrieval receipt dashboard cards must redact source refs")
        if not self.content_redacted or self.content_included:
            raise ValueError("retrieval receipt dashboard cards cannot include content")
        if self.hostile_text_included:
            raise ValueError("retrieval receipt dashboard cards cannot include hostile text")
        if RETRIEVAL_RECEIPTS_DASHBOARD_POLICY_REF not in self.policy_refs:
            raise ValueError("retrieval receipt dashboard cards require dashboard policy ref")
        if RETRIEVAL_EXPLANATION_POLICY_REF not in self.policy_refs:
            raise ValueError("retrieval receipt dashboard cards require receipt policy ref")
        return self


class RetrievalReceiptsDashboard(StrictModel):
    dashboard_id: str = RETRIEVAL_RECEIPTS_DASHBOARD_SURFACE_ID
    generated_at: datetime
    cards: list[RetrievalReceiptCard] = Field(default_factory=list)
    receipt_count: int = Field(ge=0)
    decision_counts: dict[str, int] = Field(default_factory=dict)
    content_redacted: bool = True
    source_refs_redacted: bool = True
    hostile_text_included: bool = False
    policy_refs: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def keep_dashboard_non_leaky(self) -> RetrievalReceiptsDashboard:
        if not self.content_redacted or not self.source_refs_redacted:
            raise ValueError("retrieval receipts dashboard must redact content and source refs")
        if self.hostile_text_included:
            raise ValueError("retrieval receipts dashboard cannot include hostile text")
        if RETRIEVAL_RECEIPTS_DASHBOARD_POLICY_REF not in self.policy_refs:
            raise ValueError("retrieval receipts dashboard requires dashboard policy ref")
        if RETRIEVAL_EXPLANATION_POLICY_REF not in self.policy_refs:
            raise ValueError("retrieval receipts dashboard requires receipt policy ref")
        if any(
            not card.content_redacted
            or not card.source_refs_redacted
            or card.content_included
            or card.hostile_text_included
            for card in self.cards
        ):
            raise ValueError("retrieval receipt cards must stay redacted")
        return self


def build_retrieval_receipts_dashboard(
    receipts: Iterable[RetrievalExplanationReceipt],
    *,
    now: datetime | None = None,
) -> RetrievalReceiptsDashboard:
    timestamp = now or datetime.now(UTC)
    cards = [_card_from_receipt(receipt) for receipt in receipts]
    counts = Counter(card.decision for card in cards)

    return RetrievalReceiptsDashboard(
        generated_at=timestamp,
        cards=cards,
        receipt_count=len(cards),
        decision_counts=dict(sorted(counts.items())),
        content_redacted=True,
        source_refs_redacted=True,
        hostile_text_included=False,
        policy_refs=[
            RETRIEVAL_RECEIPTS_DASHBOARD_POLICY_REF,
            RETRIEVAL_EXPLANATION_POLICY_REF,
        ],
        safety_notes=[
            "Dashboard receipts expose decisions and reason tags only.",
            "Memory content, source refs, and hostile text remain redacted.",
            "Receipts explain retrieval; they do not change ranking or scope.",
        ],
    )


def _card_from_receipt(receipt: RetrievalExplanationReceipt) -> RetrievalReceiptCard:
    return RetrievalReceiptCard(
        card_id=f"retrieval_receipt_{receipt.memory_id}_{receipt.decision}",
        memory_id=receipt.memory_id,
        decision=receipt.decision,
        rank=receipt.rank,
        score=receipt.score,
        reason_tags=list(receipt.reason_tags),
        source_ref_count=receipt.source_ref_count,
        source_refs_redacted=receipt.source_refs_redacted,
        content_redacted=receipt.content_redacted,
        content_included=receipt.content_included,
        hostile_text_included=False,
        policy_refs=[
            RETRIEVAL_RECEIPTS_DASHBOARD_POLICY_REF,
            RETRIEVAL_EXPLANATION_POLICY_REF,
            RETRIEVAL_EXPLANATION_RECEIPTS_ID,
        ],
    )
