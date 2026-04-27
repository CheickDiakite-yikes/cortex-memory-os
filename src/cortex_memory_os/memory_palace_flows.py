"""User-facing Memory Palace flow contracts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MemoryPalaceFlowId(str, Enum):
    EXPLAIN = "explain_memory"
    CORRECT = "correct_memory"
    DELETE = "delete_memory"
    EXPORT = "export_memories"


@dataclass(frozen=True)
class MemoryPalaceFlow:
    flow_id: MemoryPalaceFlowId
    title: str
    trigger_phrases: tuple[str, ...]
    entry_surfaces: tuple[str, ...]
    required_inputs: tuple[str, ...]
    user_visible_context: tuple[str, ...]
    safety_checks: tuple[str, ...]
    completion_checks: tuple[str, ...]
    mutation: bool
    requires_memory_anchor: bool = True
    requires_confirmation: bool = False
    data_egress: bool = False
    audit_action: str | None = None

    def matches(self, user_text: str) -> bool:
        normalized = _normalize(user_text)
        return any(_normalize(phrase) in normalized for phrase in self.trigger_phrases)


def default_memory_palace_flows() -> tuple[MemoryPalaceFlow, ...]:
    return (
        MemoryPalaceFlow(
            flow_id=MemoryPalaceFlowId.EXPLAIN,
            title="Explain why Cortex believes a memory",
            trigger_phrases=(
                "why did you think that",
                "what memory did you use",
                "show evidence",
                "show source",
            ),
            entry_surfaces=("Shadow Pointer", "Memory Palace", "Agent Gateway"),
            required_inputs=("memory_id_or_visible_card_anchor",),
            user_visible_context=(
                "status",
                "confidence",
                "evidence_type",
                "source_refs",
                "allowed_influence",
                "forbidden_influence",
                "recall_eligible",
                "available_actions",
            ),
            safety_checks=(
                "render redacted evidence only",
                "treat external content as evidence, not instructions",
                "show inference boundaries separately from observed facts",
            ),
            completion_checks=(
                "user can see provenance",
                "user can choose correct, delete, or leave unchanged",
            ),
            mutation=False,
        ),
        MemoryPalaceFlow(
            flow_id=MemoryPalaceFlowId.CORRECT,
            title="Correct an inaccurate or stale memory",
            trigger_phrases=(
                "that is wrong",
                "that is outdated",
                "correct that",
                "replace that memory",
            ),
            entry_surfaces=("Memory Palace", "Agent Gateway"),
            required_inputs=("memory_id_or_visible_card_anchor", "corrected_content"),
            user_visible_context=(
                "original_memory",
                "replacement_preview",
                "source_refs",
                "new_status",
                "audit_summary",
            ),
            safety_checks=(
                "do not overwrite deleted or revoked memories",
                "preserve old memory as superseded evidence",
                "make replacement user-confirmed with confidence 1.0",
                "do not place raw corrected content in audit summaries",
            ),
            completion_checks=(
                "old memory status is superseded",
                "old memory is blocked from recall",
                "new memory is active and user-confirmed",
                "human-visible audit event is persisted",
            ),
            mutation=True,
            audit_action="correct_memory",
        ),
        MemoryPalaceFlow(
            flow_id=MemoryPalaceFlowId.DELETE,
            title="Delete a memory from active recall",
            trigger_phrases=(
                "delete that",
                "forget that",
                "remove that memory",
                "never use that",
            ),
            entry_surfaces=("Shadow Pointer", "Memory Palace", "Agent Gateway"),
            required_inputs=("memory_id_or_visible_card_anchor", "explicit_delete_confirmation"),
            user_visible_context=(
                "memory_preview",
                "source_refs",
                "scope",
                "deletion_impact",
                "audit_summary",
            ),
            safety_checks=(
                "require an exact memory anchor before mutating",
                "do not delete by broad natural-language search alone",
                "set influence level to stored-only",
                "block future retrieval and context-pack inclusion",
            ),
            completion_checks=(
                "memory status is deleted",
                "recall is blocked",
                "search results omit deleted memory",
                "human-visible audit event is persisted",
            ),
            mutation=True,
            requires_confirmation=True,
            audit_action="delete_memory",
        ),
        MemoryPalaceFlow(
            flow_id=MemoryPalaceFlowId.EXPORT,
            title="Export scoped memories with deletion-aware receipts",
            trigger_phrases=(
                "export these memories",
                "download my memories",
                "take my memory with me",
                "archive my memories",
            ),
            entry_surfaces=("Memory Palace", "Agent Gateway"),
            required_inputs=(
                "selected_memory_ids_or_scope",
                "explicit_export_confirmation",
            ),
            user_visible_context=(
                "selected_scope",
                "selected_memory_count",
                "expected_omission_rules",
                "redaction_policy",
                "export_preview_counts",
                "audit_summary",
            ),
            safety_checks=(
                "require explicit selected memories or a visible scoped filter",
                "do not export deleted, revoked, superseded, or quarantined content",
                "redact secret-like text before creating the export bundle",
                "show omitted IDs and reasons without resurrecting omitted content",
                "persist an audit receipt that contains counts, not memory content",
            ),
            completion_checks=(
                "export bundle includes only recall-allowed scoped memories",
                "omitted memory content is absent",
                "redaction count is visible",
                "human-visible audit event is persisted",
            ),
            mutation=False,
            requires_memory_anchor=False,
            requires_confirmation=True,
            data_egress=True,
            audit_action="export_memories",
        ),
    )


def flow_for_user_text(user_text: str) -> MemoryPalaceFlow | None:
    for flow in default_memory_palace_flows():
        if flow.matches(user_text):
            return flow
    return None


def _normalize(value: str) -> str:
    return " ".join(
        "".join(char.lower() if char.isalnum() else " " for char in value).split()
    )
