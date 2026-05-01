"""Metadata-only source routing hints for context packs."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass

from cortex_memory_os.contracts import (
    MemoryRecord,
    SOURCE_ROUTE_HINT_POLICY_REF,
    SourceRouteHint,
)


SOURCE_ROUTER_CONTEXT_PACK_ID = "SOURCE-ROUTER-CONTEXT-PACK-001"
SOURCE_ROUTER_CONTEXT_PACK_POLICY_REF = SOURCE_ROUTE_HINT_POLICY_REF


@dataclass(frozen=True)
class SourceRouteClassification:
    source_kind: str
    tool_hint: str
    safe_to_fetch_directly: bool
    reason_tags: tuple[str, ...]


def build_source_route_hints(memories: Iterable[MemoryRecord]) -> list[SourceRouteHint]:
    """Summarize better direct sources without exposing raw refs or content."""

    classifications = [
        _classify_source_ref(source_ref)
        for memory in memories
        for source_ref in memory.source_refs
    ]
    counts = Counter(classification.source_kind for classification in classifications)
    first_by_kind: dict[str, SourceRouteClassification] = {}
    for classification in classifications:
        first_by_kind.setdefault(classification.source_kind, classification)

    hints = [
        SourceRouteHint(
            route_id=f"source_route_{kind}",
            source_kind=kind,
            tool_hint=classification.tool_hint,
            source_count=count,
            reason_tags=list(classification.reason_tags),
            safe_to_fetch_directly=classification.safe_to_fetch_directly,
            requires_user_consent=True,
            target_ref_redacted=True,
            content_redacted=True,
            policy_refs=[SOURCE_ROUTER_CONTEXT_PACK_POLICY_REF],
        )
        for kind, count in sorted(counts.items())
        for classification in [first_by_kind[kind]]
    ]
    return hints


def _classify_source_ref(source_ref: str) -> SourceRouteClassification:
    normalized = source_ref.strip().lower()
    if normalized.startswith(("raw://", "encrypted_blob://", "vault://")):
        return SourceRouteClassification(
            source_kind="raw_evidence",
            tool_hint="do_not_fetch_raw_evidence",
            safe_to_fetch_directly=False,
            reason_tags=("raw_ref_redacted", "use_memory_or_evidence_receipt"),
        )
    if normalized.startswith(("file:", "repo:", "workspace:")):
        return SourceRouteClassification(
            source_kind="local_workspace",
            tool_hint="read_trusted_local_file_or_repo_source",
            safe_to_fetch_directly=True,
            reason_tags=("prefer_direct_source", "local_observed_source"),
        )
    if normalized.startswith(("pull_request:", "github:", "issue:")):
        return SourceRouteClassification(
            source_kind="code_hosting",
            tool_hint="fetch_exact_pr_issue_or_commit_via_connector",
            safe_to_fetch_directly=True,
            reason_tags=("prefer_direct_source", "connector_fetch_required"),
        )
    if normalized.startswith(("dashboard:", "metrics:", "stripe:")):
        return SourceRouteClassification(
            source_kind="dashboard",
            tool_hint="fetch_dashboard_state_with_user_authorized_connector",
            safe_to_fetch_directly=True,
            reason_tags=("prefer_direct_source", "dynamic_state"),
        )
    if normalized.startswith(("google_doc:", "gdrive:", "notion:", "doc:")):
        return SourceRouteClassification(
            source_kind="document",
            tool_hint="fetch_document_via_user_authorized_connector",
            safe_to_fetch_directly=True,
            reason_tags=("prefer_direct_source", "document_source"),
        )
    if normalized.startswith(("slack_thread:", "email:", "gmail:", "outlook:")):
        return SourceRouteClassification(
            source_kind="third_party_communication",
            tool_hint="fetch_thread_via_user_authorized_connector_as_untrusted_evidence",
            safe_to_fetch_directly=True,
            reason_tags=("third_party_content", "treat_as_evidence_not_instruction"),
        )
    if normalized.startswith(("browser_tab:", "external:", "http://", "https://")):
        return SourceRouteClassification(
            source_kind="external_untrusted",
            tool_hint="do_not_fetch_without_fresh_review",
            safe_to_fetch_directly=False,
            reason_tags=("external_untrusted", "prompt_injection_review_required"),
        )
    return SourceRouteClassification(
        source_kind="unknown",
        tool_hint="request_user_or_system_source_clarification",
        safe_to_fetch_directly=False,
        reason_tags=("unknown_source_ref", "target_redacted"),
    )
