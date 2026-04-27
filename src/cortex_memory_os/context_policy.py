"""Context-pack policy for trusted memory versus untrusted evidence."""

from __future__ import annotations

from dataclasses import dataclass

from cortex_memory_os.contracts import EvidenceType, MemoryRecord, Sensitivity

CONTEXT_PACK_POLICY_REF = "policy_context_pack_hostile_source_v1"

UNTRUSTED_EVIDENCE_TYPES = {
    EvidenceType.EXTERNAL_EVIDENCE,
}


@dataclass(frozen=True)
class ContextMemoryDecision:
    memory_id: str
    include_as_memory: bool
    cite_as_untrusted_evidence: bool
    reason_tags: tuple[str, ...]


def evaluate_context_memory(memory: MemoryRecord) -> ContextMemoryDecision:
    reasons: list[str] = []
    include_as_memory = True
    cite_as_untrusted_evidence = False

    if memory.evidence_type in UNTRUSTED_EVIDENCE_TYPES:
        include_as_memory = False
        cite_as_untrusted_evidence = memory.sensitivity != Sensitivity.SECRET
        reasons.append("external_evidence_only")

    if memory.sensitivity == Sensitivity.SECRET:
        include_as_memory = False
        cite_as_untrusted_evidence = False
        reasons.append("secret_blocked")

    return ContextMemoryDecision(
        memory_id=memory.memory_id,
        include_as_memory=include_as_memory,
        cite_as_untrusted_evidence=cite_as_untrusted_evidence,
        reason_tags=tuple(reasons),
    )


def is_untrusted_context_memory(memory: MemoryRecord) -> bool:
    return not evaluate_context_memory(memory).include_as_memory
