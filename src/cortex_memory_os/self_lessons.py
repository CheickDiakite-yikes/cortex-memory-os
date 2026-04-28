"""Self-improvement lesson proposal and rollback contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from cortex_memory_os.contracts import ActionRisk, MemoryStatus, MemoryType, SelfLesson

SELF_LESSON_POLICY_REF = "policy_self_lesson_methods_only_v1"


class SelfLessonChangeType(str, Enum):
    RETRIEVAL_RULE = "retrieval_rule"
    CONTEXT_TEMPLATE = "context_template"
    FAILURE_CHECKLIST = "failure_checklist"
    TOOL_CHOICE_POLICY = "tool_choice_policy"
    SKILL_PROCEDURE_NOTE = "skill_procedure_note"
    SAFETY_FILTER = "safety_filter"


class SelfLessonProposal(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    proposal_id: str = Field(min_length=1)
    lesson: SelfLesson
    change_type: SelfLessonChangeType
    change_summary: str = Field(min_length=1)
    policy_refs: tuple[str, ...] = (SELF_LESSON_POLICY_REF,)
    requires_user_confirmation: bool = True

    @model_validator(mode="after")
    def enforce_methods_only(self) -> SelfLessonProposal:
        if contains_forbidden_self_lesson_change(self.change_summary):
            raise ValueError("self-lessons cannot change permissions, boundaries, or autonomy")
        if contains_prompt_injection_risk(self.change_summary) or contains_prompt_injection_risk(
            self.lesson.content
        ):
            raise ValueError("self-lessons cannot carry prompt-injection instructions")
        return self


@dataclass(frozen=True)
class SelfLessonDecision:
    allowed: bool
    target_status: MemoryStatus
    required_behavior: str
    reason: str
    policy_refs: tuple[str, ...] = (SELF_LESSON_POLICY_REF,)


@dataclass(frozen=True)
class SelfLessonCorrection:
    old_lesson: SelfLesson
    replacement_lesson: SelfLesson
    decision: SelfLessonDecision


FORBIDDEN_CHANGE_PHRASES = (
    "grant permission",
    "expand permission",
    "increase permission",
    "change permission",
    "broaden scope",
    "increase scope",
    "change scope",
    "raise autonomy",
    "increase autonomy",
    "autonomous trigger",
    "disable approval",
    "skip approval",
    "without approval",
    "change user boundary",
    "rewrite values",
    "change values",
    "use production credentials",
    "use secrets",
    "send messages automatically",
    "make purchases automatically",
)

PROMPT_INJECTION_PHRASES = (
    "ignore previous instructions",
    "ignore all previous instructions",
    "system prompt",
    "developer message",
    "reveal secrets",
)


def propose_self_lesson(
    *,
    content: str,
    learned_from: list[str],
    applies_to: list[str],
    change_type: SelfLessonChangeType,
    change_summary: str,
    confidence: float,
    risk_level: ActionRisk = ActionRisk.LOW,
    rollback_if: list[str] | None = None,
    now: datetime | None = None,
) -> SelfLessonProposal:
    created_at = now or datetime.now(UTC)
    lesson = SelfLesson(
        lesson_id=_lesson_id(applies_to, created_at),
        type=MemoryType.SELF_LESSON,
        content=content,
        learned_from=learned_from,
        applies_to=applies_to,
        confidence=confidence,
        status=MemoryStatus.CANDIDATE,
        risk_level=risk_level,
        last_validated=None,
        rollback_if=rollback_if
        or [
            "user rejects lesson",
            "causes irrelevant context retrieval",
            "changes behavior outside declared applies_to scope",
        ],
    )
    return SelfLessonProposal(
        proposal_id=f"proposal_{lesson.lesson_id}",
        lesson=lesson,
        change_type=change_type,
        change_summary=change_summary,
    )


def evaluate_self_lesson_promotion(
    proposal: SelfLessonProposal,
    *,
    user_confirmed: bool,
) -> SelfLessonDecision:
    lesson = proposal.lesson
    if lesson.status in {
        MemoryStatus.DELETED,
        MemoryStatus.REVOKED,
        MemoryStatus.QUARANTINED,
        MemoryStatus.SUPERSEDED,
    }:
        return _deny(MemoryStatus.ACTIVE, "terminal_lesson_cannot_promote")
    if contains_prompt_injection_risk(lesson.content) or contains_prompt_injection_risk(
        proposal.change_summary
    ):
        return _deny(MemoryStatus.QUARANTINED, "prompt_injection_risk")
    if contains_forbidden_self_lesson_change(proposal.change_summary):
        return _deny(MemoryStatus.CANDIDATE, "forbidden_change_target")
    if lesson.confidence < 0.75:
        return _deny(MemoryStatus.CANDIDATE, "confidence_too_low")
    if not user_confirmed:
        return _deny(MemoryStatus.CANDIDATE, "user_confirmation_required")
    return SelfLessonDecision(
        allowed=True,
        target_status=MemoryStatus.ACTIVE,
        required_behavior="method_update_only",
        reason="promotion_allowed",
    )


def promote_self_lesson(
    proposal: SelfLessonProposal,
    *,
    user_confirmed: bool,
    today: date | None = None,
) -> SelfLesson:
    decision = evaluate_self_lesson_promotion(
        proposal,
        user_confirmed=user_confirmed,
    )
    if not decision.allowed:
        raise ValueError(decision.reason)
    return proposal.lesson.model_copy(
        update={
            "status": MemoryStatus.ACTIVE,
            "last_validated": today or date.today(),
        }
    )


def evaluate_stored_self_lesson_promotion(
    lesson: SelfLesson,
    *,
    user_confirmed: bool,
) -> SelfLessonDecision:
    if lesson.status in {
        MemoryStatus.DELETED,
        MemoryStatus.REVOKED,
        MemoryStatus.QUARANTINED,
        MemoryStatus.SUPERSEDED,
    }:
        return _deny(MemoryStatus.ACTIVE, "terminal_lesson_cannot_promote")
    if contains_prompt_injection_risk(lesson.content):
        return _deny(MemoryStatus.QUARANTINED, "prompt_injection_risk")
    if lesson.confidence < 0.75:
        return _deny(MemoryStatus.CANDIDATE, "confidence_too_low")
    if not user_confirmed:
        return _deny(MemoryStatus.CANDIDATE, "user_confirmation_required")
    return SelfLessonDecision(
        allowed=True,
        target_status=MemoryStatus.ACTIVE,
        required_behavior="method_update_only",
        reason="promotion_allowed",
    )


def promote_stored_self_lesson(
    lesson: SelfLesson,
    *,
    user_confirmed: bool,
    today: date | None = None,
) -> SelfLesson:
    decision = evaluate_stored_self_lesson_promotion(
        lesson,
        user_confirmed=user_confirmed,
    )
    if not decision.allowed:
        raise ValueError(decision.reason)
    return lesson.model_copy(
        update={
            "status": MemoryStatus.ACTIVE,
            "last_validated": today or date.today(),
        }
    )


def evaluate_self_lesson_correction(
    lesson: SelfLesson,
    *,
    corrected_content: str,
    change_summary: str,
    confidence: float,
    risk_level: ActionRisk | None = None,
) -> SelfLessonDecision:
    if lesson.status in {MemoryStatus.DELETED, MemoryStatus.QUARANTINED}:
        return _deny(MemoryStatus.CANDIDATE, "terminal_lesson_cannot_correct")
    if contains_prompt_injection_risk(corrected_content) or contains_prompt_injection_risk(
        change_summary
    ):
        return _deny(MemoryStatus.QUARANTINED, "prompt_injection_risk")
    if contains_forbidden_self_lesson_change(
        corrected_content
    ) or contains_forbidden_self_lesson_change(change_summary):
        return _deny(MemoryStatus.CANDIDATE, "forbidden_change_target")
    if (risk_level or lesson.risk_level) in {ActionRisk.HIGH, ActionRisk.CRITICAL}:
        return _deny(MemoryStatus.CANDIDATE, "risk_level_too_high")
    if confidence < 0.75:
        return _deny(MemoryStatus.CANDIDATE, "confidence_too_low")
    return SelfLessonDecision(
        allowed=True,
        target_status=MemoryStatus.CANDIDATE,
        required_behavior="candidate_replacement_requires_confirmation",
        reason="correction_allowed",
    )


def correct_self_lesson(
    lesson: SelfLesson,
    *,
    corrected_content: str,
    applies_to: list[str],
    change_summary: str,
    confidence: float,
    risk_level: ActionRisk | None = None,
    now: datetime | None = None,
) -> SelfLessonCorrection:
    decision = evaluate_self_lesson_correction(
        lesson,
        corrected_content=corrected_content,
        change_summary=change_summary,
        confidence=confidence,
        risk_level=risk_level,
    )
    if not decision.allowed:
        raise ValueError(decision.reason)

    corrected_at = now or datetime.now(UTC)
    replacement = SelfLesson(
        lesson_id=_lesson_id(applies_to, corrected_at),
        type=MemoryType.SELF_LESSON,
        content=corrected_content,
        learned_from=[*lesson.learned_from, f"corrected_from:{lesson.lesson_id}"],
        applies_to=applies_to,
        confidence=confidence,
        status=MemoryStatus.CANDIDATE,
        risk_level=risk_level or lesson.risk_level,
        last_validated=None,
        rollback_if=[
            "user rejects lesson",
            "causes irrelevant context retrieval",
            "changes behavior outside declared applies_to scope",
            f"replaces:{lesson.lesson_id}",
        ],
    )
    superseded = lesson.model_copy(
        update={
            "status": MemoryStatus.SUPERSEDED,
            "rollback_if": [*lesson.rollback_if, f"corrected_to:{replacement.lesson_id}"],
        }
    )
    return SelfLessonCorrection(
        old_lesson=superseded,
        replacement_lesson=replacement,
        decision=decision,
    )


def evaluate_self_lesson_rollback(
    lesson: SelfLesson,
    *,
    failure_count: int,
    user_requested: bool = False,
) -> SelfLessonDecision:
    if lesson.status != MemoryStatus.ACTIVE:
        return _deny(MemoryStatus.REVOKED, "only_active_lessons_can_rollback")
    if failure_count < 1 and not user_requested:
        return _deny(MemoryStatus.ACTIVE, "failure_or_user_request_required")
    return SelfLessonDecision(
        allowed=True,
        target_status=MemoryStatus.REVOKED,
        required_behavior="stop_using_lesson",
        reason="rollback_allowed",
    )


def rollback_self_lesson(
    lesson: SelfLesson,
    *,
    failure_count: int,
    user_requested: bool = False,
    reason_ref: str | None = None,
) -> SelfLesson:
    decision = evaluate_self_lesson_rollback(
        lesson,
        failure_count=failure_count,
        user_requested=user_requested,
    )
    if not decision.allowed:
        raise ValueError(decision.reason)
    rollback_if = list(lesson.rollback_if)
    if reason_ref:
        rollback_ref = f"rolled_back:{reason_ref}"
        if rollback_ref not in rollback_if:
            rollback_if.append(rollback_ref)
    return lesson.model_copy(
        update={
            "status": MemoryStatus.REVOKED,
            "rollback_if": rollback_if,
        }
    )


def contains_forbidden_self_lesson_change(value: str) -> bool:
    normalized = _normalize(value)
    return any(phrase in normalized for phrase in FORBIDDEN_CHANGE_PHRASES)


def contains_prompt_injection_risk(value: str) -> bool:
    normalized = _normalize(value)
    return any(phrase in normalized for phrase in PROMPT_INJECTION_PHRASES)


def _deny(target_status: MemoryStatus, reason: str) -> SelfLessonDecision:
    return SelfLessonDecision(
        allowed=False,
        target_status=target_status,
        required_behavior="keep_current_lesson_state",
        reason=reason,
    )


def _lesson_id(applies_to: list[str], created_at: datetime) -> str:
    scope = _slug(applies_to[0]) if applies_to else "general"
    timestamp = created_at.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"lesson_{scope}_{timestamp}"


def _slug(value: str) -> str:
    return "_".join(
        "".join(char.lower() if char.isalnum() else " " for char in value).split()
    )[:48] or "general"


def _normalize(value: str) -> str:
    return " ".join(
        "".join(char.lower() if char.isalnum() else " " for char in value).split()
    )
