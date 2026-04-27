"""Human-visible audit receipts for Skill Forge maturity changes."""

from __future__ import annotations

from datetime import UTC, datetime

from cortex_memory_os.contracts import AuditEvent, SkillRecord
from cortex_memory_os.skill_policy import SkillPromotionDecision, SkillRollbackDecision
from cortex_memory_os.sqlite_store import SQLiteMemoryGraphStore

SKILL_AUDIT_POLICY_REF = "policy_skill_maturity_audit_v1"


def record_skill_promotion_audit(
    store: SQLiteMemoryGraphStore,
    skill: SkillRecord,
    decision: SkillPromotionDecision,
    *,
    actor: str = "user",
    now: datetime | None = None,
) -> AuditEvent:
    event = _skill_audit_event(
        skill=skill,
        action="promote_skill",
        actor=actor,
        timestamp=now or datetime.now(UTC),
        result=decision.reason,
        redacted_summary=(
            "Skill promotion decision: "
            f"target maturity {decision.target_maturity}, "
            f"allowed {str(decision.allowed).lower()}."
        ),
    )
    store.add_audit_event(event)
    return event


def record_skill_rollback_audit(
    store: SQLiteMemoryGraphStore,
    skill: SkillRecord,
    decision: SkillRollbackDecision,
    *,
    actor: str = "user",
    now: datetime | None = None,
) -> AuditEvent:
    event = _skill_audit_event(
        skill=skill,
        action="rollback_skill",
        actor=actor,
        timestamp=now or datetime.now(UTC),
        result=decision.reason,
        redacted_summary=(
            "Skill rollback decision: "
            f"target maturity {decision.target_maturity}, "
            f"allowed {str(decision.allowed).lower()}."
        ),
    )
    store.add_audit_event(event)
    return event


def record_skill_maturity_audit(
    store: SQLiteMemoryGraphStore,
    *,
    skill_id: str,
    action: str,
    target_maturity: int,
    allowed: bool,
    reason: str,
    actor: str = "agent",
    now: datetime | None = None,
) -> AuditEvent:
    if action not in {"promote_skill", "rollback_skill"}:
        raise ValueError("unsupported skill maturity audit action")
    timestamp = now or datetime.now(UTC)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=UTC)
    event = AuditEvent(
        audit_event_id=(
            f"audit_{action}_{_safe_id_fragment(skill_id)}_"
            f"{timestamp.strftime('%Y%m%dT%H%M%SZ')}"
        ),
        timestamp=timestamp,
        actor=actor,
        action=action,
        target_ref=skill_id,
        policy_refs=[SKILL_AUDIT_POLICY_REF],
        result=reason,
        human_visible=True,
        redacted_summary=(
            "Skill maturity decision: "
            f"target maturity {target_maturity}, "
            f"allowed {str(allowed).lower()}."
        ),
    )
    store.add_audit_event(event)
    return event


def _skill_audit_event(
    *,
    skill: SkillRecord,
    action: str,
    actor: str,
    timestamp: datetime,
    result: str,
    redacted_summary: str,
) -> AuditEvent:
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=UTC)
    return AuditEvent(
        audit_event_id=(
            f"audit_{action}_{_safe_id_fragment(skill.skill_id)}_"
            f"{timestamp.strftime('%Y%m%dT%H%M%SZ')}"
        ),
        timestamp=timestamp,
        actor=actor,
        action=action,
        target_ref=skill.skill_id,
        policy_refs=[SKILL_AUDIT_POLICY_REF],
        result=result,
        human_visible=True,
        redacted_summary=redacted_summary,
    )


def _safe_id_fragment(value: str) -> str:
    return "".join(char if char.isalnum() else "_" for char in value)
