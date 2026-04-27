"""Synthetic privacy and prompt-injection firewall primitives."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime

from cortex_memory_os.contracts import (
    FirewallDecision,
    FirewallDecisionRecord,
    FirewallRedaction,
    ObservationEvent,
    RetentionPolicy,
    Sensitivity,
    SourceTrust,
)
from cortex_memory_os.sensitive_data_policy import (
    FIREWALL_POLICY_REF,
    REDACTED_SECRET_PLACEHOLDER,
    SECRET_PII_POLICY_REF,
)

PROMPT_INJECTION_PATTERNS = [
    re.compile(r"\bignore (all )?(previous|prior) instructions\b", re.IGNORECASE),
    re.compile(r"\breveal (the )?(system prompt|developer message|secrets?)\b", re.IGNORECASE),
    re.compile(r"\bexport all (secrets?|credentials?|tokens?)\b", re.IGNORECASE),
    re.compile(r"\bdisable (safety|guardrails|policy|logging)\b", re.IGNORECASE),
    re.compile(r"\brun (this )?(curl|bash|sh|powershell)\b", re.IGNORECASE),
]

SECRET_PATTERNS = [
    ("api_key", re.compile(r"\b(?:api[_-]?key|token|secret)\s*=\s*[A-Za-z0-9_\-]{12,}\b", re.IGNORECASE)),
    ("bearer_token", re.compile(r"\bBearer\s+[A-Za-z0-9_\-.]{16,}\b", re.IGNORECASE)),
    ("fake_cortex_token", re.compile(r"\bCORTEX_FAKE_TOKEN_[A-Za-z0-9_\-]{8,}\b")),
]


@dataclass(frozen=True)
class FirewallAssessment:
    decision: FirewallDecisionRecord
    redacted_text: str


def detect_prompt_injection(text: str) -> list[str]:
    risks: list[str] = []
    for pattern in PROMPT_INJECTION_PATTERNS:
        if pattern.search(text):
            risks.append("prompt_injection")
            break
    return risks


def redact_sensitive_text(text: str) -> tuple[str, list[FirewallRedaction]]:
    redactions: list[FirewallRedaction] = []
    redacted = text
    offset = 0

    for secret_type, pattern in SECRET_PATTERNS:
        matches = list(pattern.finditer(redacted))
        for match in matches:
            start, end = match.span()
            span_ref = f"text:{start + offset}-{end + offset}"
            replacement = REDACTED_SECRET_PLACEHOLDER
            redactions.append(
                FirewallRedaction(type=secret_type, span_ref=span_ref, replacement=replacement)
            )
            redacted = redacted[:start] + replacement + redacted[end:]
            offset += (end - start) - len(replacement)

    return redacted, redactions


def assess_observation_text(
    event: ObservationEvent,
    text: str,
    *,
    now: datetime | None = None,
) -> FirewallAssessment:
    """Classify synthetic observation text before durable memory eligibility."""

    timestamp = now or event.timestamp
    injection_risks = detect_prompt_injection(text)
    redacted_text, redactions = redact_sensitive_text(text)
    risks = [*injection_risks]

    if redactions:
        risks.append("secret_like_text")

    is_external_or_hostile = event.source_trust in {
        SourceTrust.EXTERNAL_UNTRUSTED,
        SourceTrust.HOSTILE_UNTIL_SAFE,
    }
    has_injection = "prompt_injection" in risks

    if has_injection or event.source_trust == SourceTrust.HOSTILE_UNTIL_SAFE:
        decision = FirewallDecision.QUARANTINE
        retention = RetentionPolicy.DISCARD
        eligible = False
    elif redactions:
        decision = FirewallDecision.MASK
        retention = RetentionPolicy.DELETE_RAW_AFTER_10M
        eligible = False
    elif is_external_or_hostile:
        decision = FirewallDecision.EPHEMERAL_ONLY
        retention = RetentionPolicy.EPHEMERAL_SESSION
        eligible = False
    else:
        decision = FirewallDecision.MEMORY_ELIGIBLE
        retention = RetentionPolicy.DELETE_RAW_AFTER_6H
        eligible = True

    sensitivity = Sensitivity.SECRET if redactions else Sensitivity.PRIVATE_WORK

    record = FirewallDecisionRecord(
        decision_id=f"fw_{event.event_id}",
        event_id=event.event_id,
        decision=decision,
        sensitivity=sensitivity,
        detected_risks=risks,
        redactions=redactions,
        retention_policy=retention,
        eligible_for_memory=eligible,
        eligible_for_model_training=False,
        policy_refs=[FIREWALL_POLICY_REF, SECRET_PII_POLICY_REF],
        audit_event_id=f"audit_{event.event_id}_{int(timestamp.timestamp())}",
    )
    return FirewallAssessment(decision=record, redacted_text=redacted_text)
