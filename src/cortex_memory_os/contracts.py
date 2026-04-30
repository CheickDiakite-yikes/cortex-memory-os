"""Typed contracts for the Cortex evidence-to-memory loop."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum, IntEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class StrictModel(BaseModel):
    """Base model that keeps contract fixtures honest."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )


class ObservationEventType(str, Enum):
    APP_WINDOW = "app_window"
    SCREEN_FRAME = "screen_frame"
    OCR_TEXT = "ocr_text"
    ACCESSIBILITY_TREE = "accessibility_tree"
    TERMINAL_COMMAND = "terminal_command"
    TERMINAL_OUTPUT = "terminal_output"
    BROWSER_DOM = "browser_dom"
    FILE_EVENT = "file_event"
    AGENT_ACTION = "agent_action"
    OUTCOME = "outcome"


class PerceptionSourceKind(str, Enum):
    SCREEN = "screen"
    APP_WINDOW = "app_window"
    ACCESSIBILITY = "accessibility"
    TERMINAL = "terminal"
    BROWSER = "browser"
    IDE = "ide"
    FILE_SYSTEM = "file_system"
    AGENT = "agent"
    ROBOT_SENSOR = "robot_sensor"


class PerceptionRoute(str, Enum):
    FIREWALL_REQUIRED = "firewall_required"
    EPHEMERAL_ONLY = "ephemeral_only"
    DISCARD = "discard"


class SourceTrust(str, Enum):
    USER_CONFIRMED = "A"
    LOCAL_OBSERVED = "B"
    AGENT_INFERRED = "C"
    EXTERNAL_UNTRUSTED = "D"
    HOSTILE_UNTIL_SAFE = "E"


class ConsentState(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    REVOKED = "revoked"
    UNKNOWN = "unknown"


class FirewallDecision(str, Enum):
    DISCARD = "discard"
    MASK = "mask"
    EPHEMERAL_ONLY = "ephemeral_only"
    MEMORY_ELIGIBLE = "memory_eligible"
    QUARANTINE = "quarantine"


class Sensitivity(str, Enum):
    PUBLIC = "public"
    LOW = "low"
    PRIVATE_WORK = "private_work"
    CONFIDENTIAL = "confidential"
    REGULATED = "regulated"
    SECRET = "secret"


class RetentionPolicy(str, Enum):
    DISCARD = "discard"
    EPHEMERAL_SESSION = "ephemeral_session"
    DELETE_RAW_AFTER_10M = "delete_raw_after_10m"
    DELETE_RAW_AFTER_6H = "delete_raw_after_6h"
    KEEP_DERIVED_30D = "keep_derived_30d"
    PROJECT_RETENTION = "project_retention"
    USER_PINNED = "user_pinned"
    LEGAL_HOLD = "legal_hold"


class MemoryStatus(str, Enum):
    CANDIDATE = "candidate"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    SUPERSEDED = "superseded"
    REVOKED = "revoked"
    DELETED = "deleted"
    QUARANTINED = "quarantined"


class ScopeLevel(str, Enum):
    PERSONAL_GLOBAL = "personal_global"
    WORK_GLOBAL = "work_global"
    PROJECT_SPECIFIC = "project_specific"
    APP_SPECIFIC = "app_specific"
    AGENT_SPECIFIC = "agent_specific"
    SESSION_ONLY = "session_only"
    EPHEMERAL = "ephemeral"
    NEVER_STORE = "never_store"


class InfluenceLevel(IntEnum):
    STORED_ONLY = 0
    DIRECT_QUERY = 1
    PERSONALIZATION = 2
    PLANNING = 3
    TOOL_ACTIONS = 4
    AUTONOMOUS_TRIGGER = 5


class ActionRisk(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EvidenceType(str, Enum):
    USER_CONFIRMED = "user_confirmed"
    OBSERVED = "observed"
    INFERRED = "inferred"
    OBSERVED_AND_INFERRED = "observed_and_inferred"
    EXTERNAL_EVIDENCE = "external_evidence"


class MemoryType(str, Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    PREFERENCE = "preference"
    PROJECT = "project"
    RELATIONSHIP = "relationship"
    AFFECTIVE = "affective"
    SELF_LESSON = "self_lesson"
    POLICY = "policy"


class ExecutionMode(str, Enum):
    DRAFT_ONLY = "draft_only"
    ASSISTIVE = "assistive"
    BOUNDED_AUTONOMY = "bounded_autonomy"
    RECURRING_AUTOMATION = "recurring_automation"


class OutcomeStatus(str, Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    USER_REJECTED = "user_rejected"
    UNSAFE_BLOCKED = "unsafe_blocked"


class ObservationEvent(StrictModel):
    event_id: str = Field(min_length=1)
    event_type: ObservationEventType
    timestamp: datetime
    device: str = Field(min_length=1)
    app: str | None = None
    window_title: str | None = None
    project_id: str | None = None
    payload_ref: str = Field(min_length=1)
    source_trust: SourceTrust
    capture_scope: ScopeLevel
    consent_state: ConsentState
    raw_contains_user_input: bool

    @model_validator(mode="after")
    def require_active_consent_for_observation(self) -> ObservationEvent:
        if self.consent_state != ConsentState.ACTIVE and self.payload_ref.startswith("raw://"):
            raise ValueError("raw observations require active consent")
        return self


class PerceptionEventEnvelope(StrictModel):
    envelope_id: str = Field(min_length=1)
    schema_version: str = "perception_event_envelope.v1"
    source_kind: PerceptionSourceKind
    observation: ObservationEvent
    observed_at: datetime
    sequence: int = Field(ge=0)
    consent_state: ConsentState
    capture_scope: ScopeLevel
    source_trust: SourceTrust
    sensitivity_hint: Sensitivity
    route: PerceptionRoute = PerceptionRoute.FIREWALL_REQUIRED
    raw_ref: str | None = None
    derived_refs: list[str] = Field(default_factory=list)
    third_party_content: bool = False
    prompt_injection_risk: bool = False
    required_policy_refs: list[str] = Field(default_factory=list)
    robot_capability: str | None = None
    simulation_required: bool = False

    @model_validator(mode="after")
    def keep_envelope_aligned_with_observation(self) -> PerceptionEventEnvelope:
        if self.consent_state != self.observation.consent_state:
            raise ValueError("envelope consent_state must match observation consent_state")
        if self.capture_scope != self.observation.capture_scope:
            raise ValueError("envelope capture_scope must match observation capture_scope")
        if self.source_trust != self.observation.source_trust:
            raise ValueError("envelope source_trust must match observation source_trust")
        if self.raw_ref and self.raw_ref.startswith("raw://"):
            if self.consent_state != ConsentState.ACTIVE:
                raise ValueError("raw perception refs require active consent")
            if self.route != PerceptionRoute.FIREWALL_REQUIRED:
                raise ValueError("raw perception refs must route through the firewall")
        if self.prompt_injection_risk and self.route != PerceptionRoute.FIREWALL_REQUIRED:
            raise ValueError("prompt-injection risk must route through the firewall")
        if self.third_party_content and self.route == PerceptionRoute.DISCARD:
            if self.derived_refs:
                raise ValueError("discarded third-party content cannot keep derived refs")
        if self.source_kind == PerceptionSourceKind.ROBOT_SENSOR:
            if not self.robot_capability:
                raise ValueError("robot sensor events require explicit capability")
            if not self.simulation_required:
                raise ValueError("robot sensor events require simulation-first validation")
        elif self.robot_capability:
            raise ValueError("robot capability is only valid for robot sensor events")
        return self


class FirewallRedaction(StrictModel):
    type: str = Field(min_length=1)
    span_ref: str = Field(min_length=1)
    replacement: str = Field(min_length=1)


class FirewallDecisionRecord(StrictModel):
    decision_id: str = Field(min_length=1)
    event_id: str = Field(min_length=1)
    decision: FirewallDecision
    sensitivity: Sensitivity
    detected_risks: list[str] = Field(default_factory=list)
    redactions: list[FirewallRedaction] = Field(default_factory=list)
    retention_policy: RetentionPolicy
    eligible_for_memory: bool
    eligible_for_model_training: bool = False
    policy_refs: list[str] = Field(default_factory=list)
    audit_event_id: str = Field(min_length=1)

    @model_validator(mode="after")
    def enforce_security_decision_consistency(self) -> FirewallDecisionRecord:
        if self.decision in {FirewallDecision.DISCARD, FirewallDecision.QUARANTINE}:
            if self.eligible_for_memory:
                raise ValueError("discarded or quarantined content cannot be memory eligible")
        if self.sensitivity == Sensitivity.SECRET and self.decision != FirewallDecision.DISCARD:
            if not self.redactions:
                raise ValueError("secret content must be redacted or discarded")
        if self.eligible_for_model_training:
            raise ValueError("MVP contract forbids model-training eligibility")
        return self


class Scene(StrictModel):
    scene_id: str = Field(min_length=1)
    start_time: datetime
    end_time: datetime
    scene_type: str = Field(min_length=1)
    inferred_goal: str = Field(min_length=1)
    apps: list[str] = Field(min_length=1)
    entities: list[str] = Field(default_factory=list)
    action_trace_refs: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(min_length=1)
    outcome: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    privacy_level: Sensitivity
    segmentation_reason: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def end_must_not_precede_start(self) -> Scene:
        if self.end_time < self.start_time:
            raise ValueError("scene end_time cannot be before start_time")
        return self


class EvidenceRecord(StrictModel):
    evidence_id: str = Field(min_length=1)
    source: ObservationEventType
    device: str = Field(min_length=1)
    app: str | None = None
    timestamp: datetime
    raw_ref: str | None = None
    derived_text_refs: list[str] = Field(default_factory=list)
    retention_policy: RetentionPolicy
    sensitivity: Sensitivity
    contains_third_party_content: bool
    eligible_for_memory: bool
    eligible_for_model_training: bool = False

    @model_validator(mode="after")
    def enforce_retention_and_training_rules(self) -> EvidenceRecord:
        if self.retention_policy == RetentionPolicy.DISCARD and self.raw_ref:
            raise ValueError("discard retention cannot keep a raw_ref")
        if self.eligible_for_model_training:
            raise ValueError("MVP contract forbids model-training eligibility")
        if self.sensitivity == Sensitivity.SECRET and self.eligible_for_memory:
            raise ValueError("secret evidence cannot be memory eligible")
        return self


class MemoryRecord(StrictModel):
    memory_id: str = Field(min_length=1)
    type: MemoryType
    content: str = Field(min_length=1)
    source_refs: list[str] = Field(min_length=1)
    evidence_type: EvidenceType
    confidence: float = Field(ge=0.0, le=1.0)
    status: MemoryStatus
    created_at: datetime
    valid_from: date
    valid_to: date | None = None
    sensitivity: Sensitivity
    scope: ScopeLevel
    influence_level: InfluenceLevel
    allowed_influence: list[str] = Field(default_factory=list)
    forbidden_influence: list[str] = Field(default_factory=list)
    decay_policy: str | None = None
    contradicts: list[str] = Field(default_factory=list)
    user_visible: bool = True
    requires_user_confirmation: bool = False

    @model_validator(mode="after")
    def enforce_memory_safety(self) -> MemoryRecord:
        if self.valid_to is not None and self.valid_to < self.valid_from:
            raise ValueError("valid_to cannot be before valid_from")
        if self.evidence_type == EvidenceType.INFERRED and self.status == MemoryStatus.ACTIVE:
            if not self.requires_user_confirmation and self.confidence < 0.9:
                raise ValueError("low-confidence inferred memories cannot be active without review")
        if self.influence_level >= InfluenceLevel.TOOL_ACTIONS and self.status == MemoryStatus.ACTIVE:
            if not self.allowed_influence:
                raise ValueError("tool/action-influencing memories need allowed_influence")
        if self.status in {MemoryStatus.DELETED, MemoryStatus.REVOKED} and self.influence_level != 0:
            raise ValueError("deleted or revoked memories must have influence_level 0")
        return self


class TemporalEdge(StrictModel):
    edge_id: str = Field(min_length=1)
    subject: str = Field(min_length=1)
    predicate: str = Field(min_length=1)
    object: str = Field(min_length=1)
    valid_from: date
    valid_to: date | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    source_refs: list[str] = Field(min_length=1)
    status: MemoryStatus
    supersedes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def enforce_temporal_order(self) -> TemporalEdge:
        if self.valid_to is not None and self.valid_to < self.valid_from:
            raise ValueError("valid_to cannot be before valid_from")
        return self


class SkillRecord(StrictModel):
    skill_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    learned_from: list[str] = Field(min_length=1)
    trigger_conditions: list[str] = Field(min_length=1)
    inputs: dict[str, Any] = Field(default_factory=dict)
    procedure: list[str] = Field(min_length=1)
    success_signals: list[str] = Field(default_factory=list)
    failure_modes: list[str] = Field(default_factory=list)
    risk_level: ActionRisk
    maturity_level: int = Field(ge=0, le=5)
    execution_mode: ExecutionMode
    requires_confirmation_before: list[str] = Field(default_factory=list)
    status: MemoryStatus

    @model_validator(mode="after")
    def enforce_skill_maturity_and_risk(self) -> SkillRecord:
        if self.maturity_level >= 4 and self.status != MemoryStatus.ACTIVE:
            raise ValueError("bounded/autonomous skill maturity requires active status")
        if self.risk_level in {ActionRisk.HIGH, ActionRisk.CRITICAL}:
            if self.execution_mode in {
                ExecutionMode.BOUNDED_AUTONOMY,
                ExecutionMode.RECURRING_AUTOMATION,
            }:
                raise ValueError("high and critical risk skills cannot be autonomous by default")
            if not self.requires_confirmation_before:
                raise ValueError("high and critical risk skills require confirmation gates")
        if self.risk_level == ActionRisk.CRITICAL and self.maturity_level > 2:
            raise ValueError("critical skills cannot exceed draft-only maturity in the MVP")
        return self


class RelevantMemory(StrictModel):
    memory_id: str = Field(min_length=1)
    content: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)


class RelevantSelfLesson(StrictModel):
    lesson_id: str = Field(min_length=1)
    content: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    applies_to: list[str] = Field(min_length=1)
    scope: ScopeLevel = ScopeLevel.PERSONAL_GLOBAL


class SelfLessonExclusion(StrictModel):
    lesson_id: str = Field(min_length=1)
    status: MemoryStatus
    scope: ScopeLevel
    reason_tags: list[str] = Field(min_length=1)
    required_context: str | None = None
    content_redacted: bool = True


class SelfLessonReviewSummary(StrictModel):
    review_required_count: int = Field(default=0, ge=0)
    reason_counts: dict[str, int] = Field(default_factory=dict)
    scope_counts: dict[str, int] = Field(default_factory=dict)
    review_queue_tool: str = "self_lesson.review_queue"
    review_flow_tool: str = "self_lesson.review_flow"
    review_flow_requires_lesson_id: bool = True
    review_flow_audit_preview_available: bool = True
    review_flow_audit_preview_requires_lesson_id: bool = True
    review_flow_audit_shape_id: str = "self_lesson_decision_audit_v1"
    content_redacted: bool = True


class RetrievalScoreSummary(StrictModel):
    memory_id: str = Field(min_length=1)
    score: float = Field(ge=0.0)
    reason_tags: list[str] = Field(default_factory=list)


RETRIEVAL_EXPLANATION_POLICY_REF = "policy_retrieval_explanation_receipts_v1"


class RetrievalExplanationReceipt(StrictModel):
    memory_id: str = Field(min_length=1)
    decision: Literal["included", "evidence_only", "excluded"]
    rank: int | None = Field(default=None, ge=1)
    score: float = Field(ge=0.0, le=1.0)
    reason_tags: list[str] = Field(min_length=1)
    source_ref_count: int = Field(ge=0)
    source_refs_redacted: bool = True
    content_redacted: bool = True
    content_included: bool = False
    policy_refs: list[str] = Field(
        default_factory=lambda: [RETRIEVAL_EXPLANATION_POLICY_REF]
    )

    @model_validator(mode="after")
    def keep_receipt_non_leaky(self) -> RetrievalExplanationReceipt:
        if not self.source_refs_redacted:
            raise ValueError("retrieval explanation receipts must redact source refs")
        if not self.content_redacted or self.content_included:
            raise ValueError("retrieval explanation receipts cannot include content")
        if RETRIEVAL_EXPLANATION_POLICY_REF not in self.policy_refs:
            raise ValueError("retrieval explanation receipts require policy ref")
        if self.decision == "included" and self.rank is None:
            raise ValueError("included retrieval receipts require a rank")
        if self.decision != "included" and self.rank is not None:
            raise ValueError("non-included retrieval receipts cannot carry rank")
        return self


HYBRID_FUSION_CONTEXT_DIAGNOSTIC_POLICY_REF = (
    "policy_hybrid_fusion_context_pack_diagnostics_v1"
)


class HybridFusionContextDiagnostic(StrictModel):
    memory_id: str = Field(min_length=1)
    score: float = Field(ge=0.0, le=1.0)
    included: bool
    excluded_reason_tags: list[str] = Field(default_factory=list)
    component_scores: dict[str, float] = Field(default_factory=dict)
    source_ref_count: int = Field(ge=0)
    content_redacted: bool = True
    source_refs_redacted: bool = True
    policy_refs: list[str] = Field(
        default_factory=lambda: [HYBRID_FUSION_CONTEXT_DIAGNOSTIC_POLICY_REF]
    )

    @model_validator(mode="after")
    def keep_diagnostic_metadata_only(self) -> HybridFusionContextDiagnostic:
        allowed_components = {
            "semantic",
            "sparse",
            "graph",
            "recency",
            "trust",
            "privacy_risk",
            "prompt_injection_risk",
            "staleness_penalty",
            "contradiction_penalty",
        }
        if not self.content_redacted:
            raise ValueError("hybrid fusion diagnostics must redact content")
        if not self.source_refs_redacted:
            raise ValueError("hybrid fusion diagnostics must redact source refs")
        if HYBRID_FUSION_CONTEXT_DIAGNOSTIC_POLICY_REF not in self.policy_refs:
            raise ValueError("hybrid fusion diagnostics require policy refs")
        unknown_components = set(self.component_scores).difference(allowed_components)
        if unknown_components:
            raise ValueError("hybrid fusion diagnostics contain unknown components")
        for component, score in self.component_scores.items():
            if score < 0.0 or score > 1.0:
                raise ValueError(f"hybrid fusion component out of range: {component}")
        if self.included and self.excluded_reason_tags:
            raise ValueError("included fusion diagnostics cannot carry exclusion reasons")
        if not self.included and not self.excluded_reason_tags:
            raise ValueError("excluded fusion diagnostics require reason tags")
        return self


CONTEXT_BUDGET_POLICY_REF = "policy_context_pack_budget_v1"


class ContextBudget(StrictModel):
    max_prompt_tokens: int = Field(default=1200, ge=1, le=200_000)
    estimated_prompt_tokens: int = Field(default=0, ge=0)
    max_wall_clock_ms: int = Field(default=300_000, ge=1, le=86_400_000)
    max_tool_calls: int = Field(default=0, ge=0, le=1000)
    max_artifacts: int = Field(default=0, ge=0, le=1000)
    memory_budget: int = Field(default=3, ge=0, le=50)
    self_lesson_budget: int = Field(default=0, ge=0, le=10)
    max_action_risk: ActionRisk = ActionRisk.LOW
    autonomy_ceiling: ExecutionMode = ExecutionMode.ASSISTIVE
    policy_refs: list[str] = Field(default_factory=lambda: [CONTEXT_BUDGET_POLICY_REF])

    @model_validator(mode="after")
    def keep_context_budget_bounded(self) -> ContextBudget:
        if self.estimated_prompt_tokens > self.max_prompt_tokens:
            raise ValueError("estimated context tokens cannot exceed budget")
        if self.max_action_risk in {ActionRisk.HIGH, ActionRisk.CRITICAL}:
            raise ValueError("context-pack budgets cannot authorize high or critical risk")
        if self.autonomy_ceiling in {
            ExecutionMode.BOUNDED_AUTONOMY,
            ExecutionMode.RECURRING_AUTOMATION,
        }:
            raise ValueError("context-pack budgets cannot grant autonomous execution")
        if not self.policy_refs:
            raise ValueError("context-pack budgets require policy refs")
        return self


class AuditMetadata(StrictModel):
    audit_event_id: str = Field(min_length=1)
    action: str = Field(min_length=1)
    target_ref: str = Field(min_length=1)
    result: str = Field(min_length=1)
    policy_refs: list[str] = Field(default_factory=list)
    human_visible: bool = True


class ContextPack(StrictModel):
    context_pack_id: str = Field(min_length=1)
    goal: str = Field(min_length=1)
    active_project: str | None = None
    budget: ContextBudget = Field(default_factory=ContextBudget)
    relevant_files: list[str] = Field(default_factory=list)
    recent_events: list[str] = Field(default_factory=list)
    relevant_memories: list[RelevantMemory] = Field(default_factory=list)
    relevant_self_lessons: list[RelevantSelfLesson] = Field(default_factory=list)
    self_lesson_exclusions: list[SelfLessonExclusion] = Field(default_factory=list)
    self_lesson_review_summary: SelfLessonReviewSummary = Field(
        default_factory=SelfLessonReviewSummary
    )
    retrieval_scores: list[RetrievalScoreSummary] = Field(default_factory=list)
    retrieval_explanation_receipts: list[RetrievalExplanationReceipt] = Field(
        default_factory=list
    )
    hybrid_fusion_diagnostics: list[HybridFusionContextDiagnostic] = Field(
        default_factory=list
    )
    audit_metadata: list[AuditMetadata] = Field(default_factory=list)
    blocked_memory_ids: list[str] = Field(default_factory=list)
    untrusted_evidence_refs: list[str] = Field(default_factory=list)
    context_policy_refs: list[str] = Field(default_factory=list)
    relevant_skills: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    recommended_next_steps: list[str] = Field(default_factory=list)

    @field_validator("warnings")
    @classmethod
    def warnings_must_be_plain(cls, warnings: list[str]) -> list[str]:
        for warning in warnings:
            if "ignore previous" in warning.lower():
                raise ValueError("context warnings cannot echo prompt-injection instructions")
        return warnings

    @model_validator(mode="after")
    def keep_context_pack_inside_budget(self) -> ContextPack:
        if len(self.relevant_memories) > self.budget.memory_budget:
            raise ValueError("context pack exceeds memory budget")
        if len(self.relevant_self_lessons) > self.budget.self_lesson_budget:
            raise ValueError("context pack exceeds self-lesson budget")
        return self


class OutcomeRecord(StrictModel):
    outcome_id: str = Field(min_length=1)
    task_id: str = Field(min_length=1)
    agent_id: str = Field(min_length=1)
    status: OutcomeStatus
    evidence_refs: list[str] = Field(default_factory=list)
    user_feedback: str | None = None
    memory_updates: list[str] = Field(default_factory=list)
    skill_updates: list[str] = Field(default_factory=list)
    postmortem_ref: str | None = None
    created_at: datetime


class SelfLesson(StrictModel):
    lesson_id: str = Field(min_length=1)
    type: MemoryType = MemoryType.SELF_LESSON
    content: str = Field(min_length=1)
    learned_from: list[str] = Field(min_length=1)
    applies_to: list[str] = Field(min_length=1)
    scope: ScopeLevel = ScopeLevel.PERSONAL_GLOBAL
    confidence: float = Field(ge=0.0, le=1.0)
    status: MemoryStatus
    risk_level: ActionRisk
    last_validated: date | None = None
    rollback_if: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def enforce_self_lesson_scope(self) -> SelfLesson:
        if self.risk_level in {ActionRisk.HIGH, ActionRisk.CRITICAL}:
            raise ValueError("self-lessons cannot be high or critical risk")
        if self.scope in {ScopeLevel.EPHEMERAL, ScopeLevel.NEVER_STORE}:
            raise ValueError("self-lessons cannot use ephemeral or never-store scope")
        if self.status == MemoryStatus.ACTIVE and self.confidence < 0.75:
            raise ValueError("active self-lessons require confidence >= 0.75")
        required_tag = {
            ScopeLevel.PROJECT_SPECIFIC: "project:",
            ScopeLevel.AGENT_SPECIFIC: "agent:",
            ScopeLevel.SESSION_ONLY: "session:",
            ScopeLevel.EPHEMERAL: "session:",
        }.get(self.scope)
        if required_tag and not any(ref.startswith(required_tag) for ref in self.learned_from):
            raise ValueError("scoped self-lessons require matching provenance tags")
        return self


class AuditEvent(StrictModel):
    audit_event_id: str = Field(min_length=1)
    timestamp: datetime
    actor: str = Field(min_length=1)
    action: str = Field(min_length=1)
    target_ref: str = Field(min_length=1)
    policy_refs: list[str] = Field(default_factory=list)
    result: str = Field(min_length=1)
    human_visible: bool
    redacted_summary: str = Field(min_length=1)
