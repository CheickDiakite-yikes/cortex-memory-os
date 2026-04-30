"""Safe explanation receipts for context retrieval decisions."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Literal

from cortex_memory_os.contracts import (
    RETRIEVAL_EXPLANATION_POLICY_REF,
    RetrievalExplanationReceipt,
)
from cortex_memory_os.retrieval import RankedMemory

RETRIEVAL_EXPLANATION_RECEIPTS_ID = "RETRIEVAL-EXPLANATION-RECEIPTS-001"

RetrievalDecision = Literal["included", "evidence_only", "excluded"]


def included_retrieval_receipt(
    ranked: RankedMemory,
    *,
    rank: int,
) -> RetrievalExplanationReceipt:
    """Explain why a memory entered a context pack without copying content."""

    return RetrievalExplanationReceipt(
        memory_id=ranked.memory.memory_id,
        decision="included",
        rank=rank,
        score=round(ranked.score.total, 4),
        reason_tags=_included_reason_tags(ranked),
        source_ref_count=len(ranked.memory.source_refs),
        source_refs_redacted=True,
        content_redacted=True,
        content_included=False,
        policy_refs=[RETRIEVAL_EXPLANATION_POLICY_REF],
    )


def excluded_retrieval_receipt(
    ranked: RankedMemory,
    *,
    decision: RetrievalDecision = "excluded",
    reason_tags: Iterable[str] = (),
) -> RetrievalExplanationReceipt:
    """Explain an exclusion or evidence-only treatment without exposing text."""

    if decision == "included":
        raise ValueError("use included_retrieval_receipt for included decisions")
    tags = [*ranked.score.reasons, *reason_tags]
    if not tags:
        tags = ["context_policy_excluded"]
    return RetrievalExplanationReceipt(
        memory_id=ranked.memory.memory_id,
        decision=decision,
        rank=None,
        score=round(ranked.score.total, 4),
        reason_tags=_dedupe_preserve_order(tags),
        source_ref_count=len(ranked.memory.source_refs),
        source_refs_redacted=True,
        content_redacted=True,
        content_included=False,
        policy_refs=[RETRIEVAL_EXPLANATION_POLICY_REF],
    )


def build_context_retrieval_receipts(
    included_ranked: Iterable[RankedMemory],
    excluded_ranked: Iterable[tuple[RankedMemory, RetrievalDecision, Iterable[str]]],
) -> list[RetrievalExplanationReceipt]:
    receipts: list[RetrievalExplanationReceipt] = []
    for index, ranked in enumerate(included_ranked, start=1):
        receipts.append(included_retrieval_receipt(ranked, rank=index))
    for ranked, decision, reason_tags in excluded_ranked:
        receipts.append(
            excluded_retrieval_receipt(
                ranked,
                decision=decision,
                reason_tags=reason_tags,
            )
        )
    return receipts


def _included_reason_tags(ranked: RankedMemory) -> list[str]:
    tags: list[str] = []
    score = ranked.score
    if score.query_relevance > 0:
        tags.append("query_overlap")
    if score.confidence_component >= 0.7:
        tags.append("confidence")
    if score.source_trust_component >= 0.7:
        tags.append("source_trust")
    if score.recency_component >= 0.5:
        tags.append("recency")
    if not tags:
        tags.append("retrieval_score")
    return tags


def _dedupe_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
