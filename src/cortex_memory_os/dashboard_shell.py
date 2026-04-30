"""Static local dashboard shell for safe Cortex view models."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, date, datetime
from pathlib import Path

from pydantic import Field

from cortex_memory_os.contracts import (
    ActionRisk,
    AuditEvent,
    EvidenceType,
    ExecutionMode,
    InfluenceLevel,
    MemoryRecord,
    MemoryStatus,
    MemoryType,
    OutcomeStatus,
    ScopeLevel,
    Sensitivity,
    SkillRecord,
    SourceTrust,
    StrictModel,
)
from cortex_memory_os.memory_palace_dashboard import (
    MEMORY_PALACE_DASHBOARD_POLICY_REF,
    MemoryPalaceDashboard,
    build_memory_palace_dashboard,
)
from cortex_memory_os.dashboard_gateway_actions import (
    DASHBOARD_GATEWAY_ACTIONS_POLICY_REF,
    DashboardGatewayActionReceipt,
    build_dashboard_gateway_action_receipts,
)
from cortex_memory_os.retrieval import RetrievalScope
from cortex_memory_os.skill_forge import (
    DocumentSkillDerivationRequest,
    derive_skill_candidate_from_document,
)
from cortex_memory_os.skill_forge_dashboard import (
    SKILL_FORGE_CANDIDATE_LIST_POLICY_REF,
    SkillForgeCandidateList,
    build_skill_forge_candidate_list,
)
from cortex_memory_os.skill_metrics import SkillOutcomeEvent
from cortex_memory_os.skill_metrics_dashboard import (
    SKILL_METRICS_DASHBOARD_POLICY_REF,
    SkillMetricsDashboard,
    build_skill_metrics_dashboard,
)

DASHBOARD_SHELL_ID = "MEMORY-PALACE-SKILL-FORGE-UI-001"
DASHBOARD_SHELL_POLICY_REF = "policy_cortex_dashboard_shell_v1"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DASHBOARD_DATA_PATH = REPO_ROOT / "ui" / "cortex-dashboard" / "dashboard-data.js"


class DashboardStatusItem(StrictModel):
    item_id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    value: str = Field(min_length=1)
    detail: str = Field(min_length=1)
    state: str = Field(min_length=1)


class DashboardNavItem(StrictModel):
    item_id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    count: int | None = Field(default=None, ge=0)
    active: bool = False


class DashboardSafeReceipt(StrictModel):
    receipt_id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    target_ref: str = Field(min_length=1)
    actor: str = Field(min_length=1)
    state: str = Field(min_length=1)
    timestamp: datetime
    content_redacted: bool = True


class CortexDashboardShell(StrictModel):
    shell_id: str = DASHBOARD_SHELL_ID
    generated_at: datetime
    version_label: str = "Cortex Memory OS v0.6.0"
    active_project: str = "cortex-memory-os"
    local_mode: bool = True
    cloud_sync: bool = False
    encrypted_at_rest: bool = True
    audit_logging: bool = True
    status_strip: list[DashboardStatusItem] = Field(default_factory=list)
    nav_items: list[DashboardNavItem] = Field(default_factory=list)
    memory_palace: MemoryPalaceDashboard
    skill_forge: SkillForgeCandidateList
    skill_metrics: SkillMetricsDashboard
    safe_receipts: list[DashboardSafeReceipt] = Field(default_factory=list)
    gateway_action_receipts: list[DashboardGatewayActionReceipt] = Field(default_factory=list)
    policy_refs: list[str] = Field(default_factory=list)
    design_notes: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)


class DashboardShellSmokeResult(StrictModel):
    policy_ref: str = DASHBOARD_SHELL_POLICY_REF
    passed: bool
    shell_id: str = DASHBOARD_SHELL_ID
    ui_files_present: bool
    memory_card_count: int = Field(ge=0)
    skill_card_count: int = Field(ge=0)
    skill_metric_card_count: int = Field(ge=0)
    skill_metric_run_count: int = Field(ge=0)
    safe_receipt_count: int = Field(ge=0)
    gateway_action_receipt_count: int = Field(ge=0)
    read_only_gateway_action_count: int = Field(ge=0)
    blocked_gateway_action_count: int = Field(ge=0)
    secret_retained: bool
    raw_private_data_retained: bool
    action_plans_present: bool
    gateway_actions_present: bool
    skill_metrics_present: bool
    procedure_text_retained: bool
    missing_ui_terms: list[str] = Field(default_factory=list)
    missing_doc_terms: list[str] = Field(default_factory=list)


def build_dashboard_shell(*, now: datetime | None = None) -> CortexDashboardShell:
    timestamp = _timestamp(now)
    memories = _sample_memories(timestamp)
    memory_dashboard = build_memory_palace_dashboard(
        memories,
        audit_events=_sample_audit_events(timestamp),
        selected_memory_ids=[
            "mem_smallest_safe_change",
            "mem_auth_redirect_root_cause",
            "mem_research_depth_candidate",
        ],
        scope=RetrievalScope(active_project="cortex-memory-os"),
        now=timestamp,
    )
    skills = _sample_skills()
    skill_list = _redact_dashboard_skill_procedures(
        build_skill_forge_candidate_list(skills, now=timestamp)
    )
    skill_metrics = build_skill_metrics_dashboard(
        skills,
        _sample_skill_outcome_events(skills, timestamp),
        now=timestamp,
    )

    return CortexDashboardShell(
        generated_at=timestamp,
        status_strip=[
            DashboardStatusItem(
                item_id="shadow_pointer",
                label="Shadow Pointer",
                value="Observing",
                detail='Debugging "onboarding bug"',
                state="healthy",
            ),
            DashboardStatusItem(
                item_id="active_project",
                label="Active Project",
                value="cortex-memory-os",
                detail="~/Codex/cortex-memory-os",
                state="neutral",
            ),
            DashboardStatusItem(
                item_id="consent_scope",
                label="Consent Scope",
                value="Project-specific",
                detail="Code, tools, and docs only",
                state="healthy",
            ),
            DashboardStatusItem(
                item_id="safety_firewall",
                label="Safety Firewall",
                value="Healthy",
                detail="No issue detected",
                state="healthy",
            ),
        ],
        nav_items=[
            DashboardNavItem(item_id="overview", label="Overview", active=True),
            DashboardNavItem(
                item_id="memory_palace",
                label="Memory Palace",
                count=len(memory_dashboard.cards),
            ),
            DashboardNavItem(
                item_id="skill_forge",
                label="Skill Forge",
                count=skill_list.candidate_count,
            ),
            DashboardNavItem(item_id="agent_gateway", label="Agent Gateway"),
            DashboardNavItem(
                item_id="audit",
                label="Audit",
                count=len(_sample_audit_events(timestamp)),
            ),
            DashboardNavItem(item_id="policies", label="Policies"),
        ],
        memory_palace=memory_dashboard,
        skill_forge=skill_list,
        skill_metrics=skill_metrics,
        safe_receipts=_sample_safe_receipts(timestamp),
        gateway_action_receipts=build_dashboard_gateway_action_receipts(
            memory_dashboard,
            skill_list,
            now=timestamp,
        ),
        policy_refs=[
            DASHBOARD_SHELL_POLICY_REF,
            MEMORY_PALACE_DASHBOARD_POLICY_REF,
            SKILL_FORGE_CANDIDATE_LIST_POLICY_REF,
            SKILL_METRICS_DASHBOARD_POLICY_REF,
            DASHBOARD_GATEWAY_ACTIONS_POLICY_REF,
        ],
        design_notes=[
            "Two primary work areas: Memory Palace review queue and Skill Forge candidates.",
            "Skill Metrics are shown as outcome summaries, not procedure previews.",
            "Status strip exposes observation, project, consent, and firewall state.",
            "Action controls are declarative UI plans; this shell does not execute mutations.",
        ],
        safety_notes=[
            "Static fixture contains synthetic view-model data only.",
            "No raw private memory, screenshots, databases, logs, or API responses are embedded.",
            "Action buttons resolve to gateway receipts before any tool call is allowed.",
            "Skill metric cards do not include procedure text, task content, or autonomy-changing controls.",
        ],
    )


def render_dashboard_data_js(shell: CortexDashboardShell | None = None) -> str:
    payload = (shell or build_dashboard_shell()).model_dump(mode="json")
    return (
        "window.CORTEX_DASHBOARD_DATA = "
        + json.dumps(payload, indent=2, sort_keys=True)
        + ";\n"
    )


def write_dashboard_data_js(
    path: Path = DEFAULT_DASHBOARD_DATA_PATH,
    *,
    shell: CortexDashboardShell | None = None,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_dashboard_data_js(shell), encoding="utf-8")
    return path


def run_dashboard_shell_smoke() -> DashboardShellSmokeResult:
    shell = build_dashboard_shell(now=datetime(2026, 4, 30, 11, 0, tzinfo=UTC))
    data_js = render_dashboard_data_js(shell)
    serialized = shell.model_dump_json()
    ui_paths = [
        REPO_ROOT / "ui" / "cortex-dashboard" / "index.html",
        REPO_ROOT / "ui" / "cortex-dashboard" / "styles.css",
        REPO_ROOT / "ui" / "cortex-dashboard" / "app.js",
        REPO_ROOT / "ui" / "cortex-dashboard" / "dashboard-data.js",
    ]
    ui_files_present = all(path.exists() for path in ui_paths)
    ui_text = "\n".join(path.read_text(encoding="utf-8") for path in ui_paths if path.exists())
    required_ui_terms = [
        DASHBOARD_SHELL_ID,
        "Memory Palace Review Queue",
        "Skill Forge Candidate Workflows",
        "Shadow Pointer",
        "Safety Firewall",
        "Recent Safe Receipts",
        "Gateway Action Receipts",
        "Skill Metrics",
        "window.CORTEX_DASHBOARD_DATA",
    ]
    missing_ui_terms = _missing_terms(ui_text + "\n" + data_js, required_ui_terms)
    doc_text = (
        REPO_ROOT / "docs" / "product" / "cortex-dashboard-shell.md"
    ).read_text(encoding="utf-8") if (
        REPO_ROOT / "docs" / "product" / "cortex-dashboard-shell.md"
    ).exists() else ""
    required_doc_terms = [
        DASHBOARD_SHELL_ID,
        DASHBOARD_SHELL_POLICY_REF,
        "generated dashboard concept",
        "safe view models",
        "no raw private memory",
        "local UI state",
    ]
    missing_doc_terms = _missing_terms(doc_text, required_doc_terms)
    action_plans_present = any(
        card.action_plans for card in shell.memory_palace.cards
    ) and any(card.action_plans for card in shell.skill_forge.cards)
    gateway_actions_present = (
        bool(shell.gateway_action_receipts)
        and any(receipt.allowed_gateway_call for receipt in shell.gateway_action_receipts)
        and any(not receipt.allowed_gateway_call for receipt in shell.gateway_action_receipts)
    )
    secret_retained = any(
        marker in serialized + data_js
        for marker in ["CORTEX_FAKE_TOKEN", "OPENAI_API_KEY=", "sk-"]
    )
    raw_private_data_retained = "raw://" in serialized or "encrypted_blob://" in serialized
    procedure_text_retained = any(
        text in serialized + data_js
        for text in [
            "Search primary sources",
            "Gather approved metrics",
            "Reproduce the local login flow",
            "Inspect route, console, and terminal errors",
        ]
    )
    skill_metrics_present = (
        bool(shell.skill_metrics.cards)
        and shell.skill_metrics.total_run_count > 0
        and not shell.skill_metrics.procedure_text_included
        and not shell.skill_metrics.autonomy_change_allowed
    )

    passed = (
        ui_files_present
        and shell.memory_palace.cards
        and shell.skill_forge.cards
        and skill_metrics_present
        and shell.safe_receipts
        and gateway_actions_present
        and not secret_retained
        and not raw_private_data_retained
        and not procedure_text_retained
        and action_plans_present
        and not missing_ui_terms
        and not missing_doc_terms
    )
    return DashboardShellSmokeResult(
        passed=passed,
        ui_files_present=ui_files_present,
        memory_card_count=len(shell.memory_palace.cards),
        skill_card_count=len(shell.skill_forge.cards),
        skill_metric_card_count=len(shell.skill_metrics.cards),
        skill_metric_run_count=shell.skill_metrics.total_run_count,
        safe_receipt_count=len(shell.safe_receipts),
        gateway_action_receipt_count=len(shell.gateway_action_receipts),
        read_only_gateway_action_count=sum(
            int(receipt.allowed_gateway_call) for receipt in shell.gateway_action_receipts
        ),
        blocked_gateway_action_count=sum(
            int(not receipt.allowed_gateway_call) for receipt in shell.gateway_action_receipts
        ),
        secret_retained=secret_retained,
        raw_private_data_retained=raw_private_data_retained,
        action_plans_present=action_plans_present,
        gateway_actions_present=gateway_actions_present,
        skill_metrics_present=skill_metrics_present,
        procedure_text_retained=procedure_text_retained,
        missing_ui_terms=missing_ui_terms,
        missing_doc_terms=missing_doc_terms,
    )


def _sample_memories(now: datetime) -> list[MemoryRecord]:
    base_fields = {
        "created_at": now,
        "valid_from": date(2026, 4, 30),
        "valid_to": None,
        "sensitivity": Sensitivity.LOW,
        "scope": ScopeLevel.PROJECT_SPECIFIC,
        "influence_level": InfluenceLevel.PLANNING,
        "forbidden_influence": ["financial_decisions", "medical_decisions"],
        "decay_policy": "review_after_90_days",
        "contradicts": [],
        "user_visible": True,
        "requires_user_confirmation": False,
    }
    return [
        MemoryRecord(
            **base_fields,
            memory_id="mem_smallest_safe_change",
            type=MemoryType.PREFERENCE,
            content=(
                "User consistently asks for minimal diffs and targeted fixes with tests "
                "after each change."
            ),
            source_refs=["project:cortex-memory-os", "scene:onboarding_debug"],
            evidence_type=EvidenceType.OBSERVED_AND_INFERRED,
            confidence=0.92,
            status=MemoryStatus.ACTIVE,
            allowed_influence=["coding_style", "verification_depth"],
        ),
        MemoryRecord(
            **base_fields,
            memory_id="mem_auth_redirect_root_cause",
            type=MemoryType.SEMANTIC,
            content=(
                "In local development, OAuth redirect URI mismatches usually require "
                "checking callback route and env configuration together."
            ),
            source_refs=["project:cortex-memory-os", "terminal:test_auth_flow"],
            evidence_type=EvidenceType.OBSERVED,
            confidence=0.87,
            status=MemoryStatus.ACTIVE,
            allowed_influence=["debugging_plan"],
        ),
        MemoryRecord(
            **{**base_fields, "requires_user_confirmation": True},
            memory_id="mem_research_depth_candidate",
            type=MemoryType.PROCEDURAL,
            content=(
                "When exploring AI systems, user often prefers primary-source research, "
                "comparative synthesis, and architecture implications."
            ),
            source_refs=["project:cortex-memory-os", "scene:frontier_research"],
            evidence_type=EvidenceType.OBSERVED_AND_INFERRED,
            confidence=0.73,
            status=MemoryStatus.CANDIDATE,
            allowed_influence=["research_workflows"],
        ),
        MemoryRecord(
            **{**base_fields, "requires_user_confirmation": True},
            memory_id="mem_linear_label_tracking",
            type=MemoryType.PROJECT,
            content="Uses labels like In Progress, Blocked, Review, and Done for work items.",
            source_refs=["project:cortex-memory-os", "scene:ops_board"],
            evidence_type=EvidenceType.INFERRED,
            confidence=0.65,
            status=MemoryStatus.CANDIDATE,
            allowed_influence=["task_board_structure"],
        ),
    ]


def _sample_skills() -> list[SkillRecord]:
    monthly = derive_skill_candidate_from_document(
        DocumentSkillDerivationRequest(
            document_id="doc_monthly_update_workflow",
            title="Monthly update workflow",
            source_ref="docs/workflows/monthly-update.md",
            source_trust=SourceTrust.LOCAL_OBSERVED,
            workflow_name="Prepare monthly investor update",
            trigger_conditions=["user asks for monthly update"],
            procedure_steps=[
                "Gather approved metrics and source refs",
                "Summarize shipped work and blockers",
                "Draft concise update and ask before sending",
            ],
            evidence_refs=["ev_monthly_update_workflow"],
            risk_level=ActionRisk.HIGH,
        )
    ).skill
    research = SkillRecord(
        skill_id="skill_research_synthesis_blueprint_v1",
        name="Research Synthesis Blueprint",
        description=(
            "Deep technical research, group findings, extract principles, and produce "
            "architecture implications."
        ),
        learned_from=["scene_research_201", "scene_research_218", "scene_research_230"],
        trigger_conditions=["serious research request", "architecture blueprint request"],
        inputs={"topic": "string", "depth": "quick | serious | exhaustive"},
        procedure=[
            "Search primary sources",
            "Separate product claims, papers, benchmarks, and risks",
            "Extract design principles",
            "Cite load-bearing claims",
        ],
        success_signals=["user builds on structure", "low correction rate"],
        failure_modes=["too much summary", "not enough implementation detail"],
        risk_level=ActionRisk.LOW,
        maturity_level=2,
        execution_mode=ExecutionMode.DRAFT_ONLY,
        status=MemoryStatus.CANDIDATE,
    )
    auth = SkillRecord(
        skill_id="skill_frontend_auth_debugging_flow_v1",
        name="Frontend Auth Debugging Flow",
        description="Reproduce auth issue, inspect logs, fix callback route, and verify outcome.",
        learned_from=["scene_auth_1", "scene_auth_2", "scene_auth_3"],
        trigger_conditions=["onboarding login bug", "OAuth callback failure"],
        inputs={"bug_summary": "string", "project": "string"},
        procedure=[
            "Reproduce the local login flow",
            "Inspect route, console, and terminal errors",
            "Patch the smallest safe callback or env mismatch",
            "Run focused tests and smoke the flow",
        ],
        success_signals=["tests pass", "local reproduction closes"],
        failure_modes=["changed deployment settings without approval", "ignored env mismatch"],
        risk_level=ActionRisk.MEDIUM,
        maturity_level=2,
        execution_mode=ExecutionMode.DRAFT_ONLY,
        requires_confirmation_before=["deployment_settings"],
        status=MemoryStatus.CANDIDATE,
    )
    return [auth, monthly, research]


def _redact_dashboard_skill_procedures(
    skill_list: SkillForgeCandidateList,
) -> SkillForgeCandidateList:
    redacted_cards = [
        card.model_copy(update={"procedure_preview": [], "content_redacted": True})
        for card in skill_list.cards
    ]
    return skill_list.model_copy(update={"cards": redacted_cards})


def _sample_audit_events(now: datetime) -> list[AuditEvent]:
    return [
        AuditEvent(
            audit_event_id="audit_memory_created_mem_smallest_safe_change",
            timestamp=now,
            actor="system",
            action="create_memory",
            target_ref="mem_smallest_safe_change",
            policy_refs=[MEMORY_PALACE_DASHBOARD_POLICY_REF],
            result="created",
            human_visible=True,
            redacted_summary="Memory created from synthetic dashboard fixture.",
        ),
        AuditEvent(
            audit_event_id="audit_skill_candidate_created_auth",
            timestamp=now,
            actor="system",
            action="create_skill_candidate",
            target_ref="skill_frontend_auth_debugging_flow_v1",
            policy_refs=[SKILL_FORGE_CANDIDATE_LIST_POLICY_REF],
            result="candidate",
            human_visible=True,
            redacted_summary="Skill candidate created from synthetic dashboard fixture.",
        ),
    ]


def _sample_skill_outcome_events(
    skills: list[SkillRecord],
    now: datetime,
) -> list[SkillOutcomeEvent]:
    by_id = {skill.skill_id: skill for skill in skills}
    return [
        _skill_outcome_event(
            by_id["skill_frontend_auth_debugging_flow_v1"],
            "evt_auth_success_001",
            "task_auth_debug_001",
            OutcomeStatus.SUCCESS,
            now,
            correction_count=0,
            verification_refs=["test://auth-flow/focused"],
        ),
        _skill_outcome_event(
            by_id["skill_frontend_auth_debugging_flow_v1"],
            "evt_auth_partial_001",
            "task_auth_debug_002",
            OutcomeStatus.PARTIAL,
            now,
            correction_count=1,
            verification_refs=["test://auth-flow/regression"],
        ),
        _skill_outcome_event(
            by_id["skill_research_synthesis_blueprint_v1"],
            "evt_research_success_001",
            "task_research_001",
            OutcomeStatus.SUCCESS,
            now,
            correction_count=0,
            verification_refs=["doc://research-synthesis/review"],
        ),
        _skill_outcome_event(
            by_id["skill_research_synthesis_blueprint_v1"],
            "evt_research_success_002",
            "task_research_002",
            OutcomeStatus.SUCCESS,
            now,
            correction_count=1,
            verification_refs=["doc://architecture-implications/review"],
        ),
        _skill_outcome_event(
            by_id["skill_doc_doc_monthly_update_workflow_candidate_v1"],
            "evt_monthly_blocked_001",
            "task_monthly_update_001",
            OutcomeStatus.UNSAFE_BLOCKED,
            now,
            correction_count=0,
            verification_refs=["audit://blocked-send-review"],
        ),
    ]


def _skill_outcome_event(
    skill: SkillRecord,
    event_id: str,
    task_id: str,
    outcome: OutcomeStatus,
    observed_at: datetime,
    *,
    correction_count: int,
    verification_refs: list[str],
) -> SkillOutcomeEvent:
    return SkillOutcomeEvent(
        event_id=event_id,
        skill_id=skill.skill_id,
        task_id=task_id,
        outcome=outcome,
        observed_at=observed_at,
        maturity_level=skill.maturity_level,
        execution_mode=skill.execution_mode,
        risk_level=skill.risk_level,
        user_correction_count=correction_count,
        verification_refs=verification_refs,
    )


def _sample_safe_receipts(now: datetime) -> list[DashboardSafeReceipt]:
    return [
        DashboardSafeReceipt(
            receipt_id="receipt_memory_created",
            label="Memory created",
            target_ref="mem_smallest_safe_change",
            actor="system",
            state="healthy",
            timestamp=now,
        ),
        DashboardSafeReceipt(
            receipt_id="receipt_memory_export_preview",
            label="Export preview prepared",
            target_ref="export_preview_project_scope",
            actor="system",
            state="neutral",
            timestamp=now,
        ),
        DashboardSafeReceipt(
            receipt_id="receipt_skill_candidate_created",
            label="Skill candidate created",
            target_ref="skill_frontend_auth_debugging_flow_v1",
            actor="system",
            state="healthy",
            timestamp=now,
        ),
        DashboardSafeReceipt(
            receipt_id="receipt_observation_paused",
            label="Observation paused",
            target_ref="session_20260430",
            actor="user",
            state="warning",
            timestamp=now,
        ),
    ]


def _timestamp(now: datetime | None) -> datetime:
    timestamp = now or datetime.now(UTC)
    if timestamp.tzinfo is None:
        return timestamp.replace(tzinfo=UTC)
    return timestamp


def _missing_terms(text: str, terms: list[str]) -> list[str]:
    return [term for term in terms if term not in text]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build or validate the Cortex dashboard shell.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--write-ui-data", nargs="?", const=str(DEFAULT_DASHBOARD_DATA_PATH))
    args = parser.parse_args(argv)

    if args.write_ui_data:
        path = write_dashboard_data_js(Path(args.write_ui_data))
        if not args.json:
            print(f"wrote {path}")

    payload: StrictModel
    if args.smoke:
        payload = run_dashboard_shell_smoke()
    else:
        payload = build_dashboard_shell()

    if args.json:
        print(json.dumps(payload.model_dump(mode="json"), indent=2, sort_keys=True))
    return 0 if not args.smoke or run_dashboard_shell_smoke().passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
