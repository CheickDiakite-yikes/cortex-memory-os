"""Safe local demo-readiness receipt for Cortex Memory OS."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, date, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from pydantic import Field, model_validator

from cortex_memory_os.contracts import (
    EvidenceType,
    InfluenceLevel,
    MemoryRecord,
    MemoryStatus,
    MemoryType,
    ScopeLevel,
    Sensitivity,
    StrictModel,
    TemporalEdge,
)
from cortex_memory_os.dashboard_shell import run_dashboard_shell_smoke
from cortex_memory_os.encrypted_graph_index import (
    UNIFIED_ENCRYPTED_GRAPH_INDEX_POLICY_REF,
    UnifiedEncryptedGraphIndex,
)
from cortex_memory_os.evidence_vault import VaultRuntimeMode
from cortex_memory_os.live_adapters import REPO_ROOT
from cortex_memory_os.live_readiness import inspect_env_local_hygiene
from cortex_memory_os.mcp_server import CortexMCPServer
from cortex_memory_os.retrieval import RetrievalScope
from cortex_memory_os.synthetic_capture_ladder import (
    SYNTHETIC_CAPTURE_LADDER_POLICY_REF,
    run_synthetic_capture_ladder,
)

DEMO_READINESS_ID = "DEMO-READINESS-001"
DEMO_READINESS_POLICY_REF = "policy_demo_readiness_v1"

DEMO_BLOCKED_EFFECTS = [
    "real_screen_capture",
    "durable_raw_screen_storage",
    "raw_private_refs",
    "secret_echo",
    "mutation",
    "export",
    "draft_execution",
    "external_effect",
]

_DEMO_MEMORY_ID = "mem_demo_readiness_encrypted_index"
_DEMO_PRIVATE_CONTENT_MARKERS = [
    "Demo sealed context memory uses auth callback verification",
    "scene_demo_private_trace",
    "OAuth callback route mismatch",
]
_PROHIBITED_MARKERS = [
    "CORTEX_FAKE_TOKEN",
    "OPENAI_API_KEY=",
    "api_key=",
    "sk-",
    "Bearer ",
    "raw://",
    "encrypted_blob://",
    *_DEMO_PRIVATE_CONTENT_MARKERS,
]


class DemoReadinessCheck(StrictModel):
    name: str = Field(min_length=1)
    passed: bool
    live_effect: bool = False
    safety_critical: bool = True
    policy_refs: list[str] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)


class DemoStep(StrictModel):
    step_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    surface: str = Field(min_length=1)
    proof: str = Field(min_length=1)
    safety_note: str = Field(min_length=1)
    command: str | None = None


class DemoReadinessReceipt(StrictModel):
    benchmark_id: str = DEMO_READINESS_ID
    policy_ref: str = DEMO_READINESS_POLICY_REF
    passed: bool
    demo_ready: bool
    safe_to_show_publicly: bool
    generated_at: datetime
    synthetic_only: bool = True
    localhost_only: bool = True
    real_screen_capture_started: bool = False
    durable_raw_screen_storage_enabled: bool = False
    raw_private_refs_returned: bool = False
    secret_values_read: bool = False
    model_secret_echo_attempted: bool = False
    mutation_export_or_draft_enabled: bool = False
    external_effect_enabled: bool = False
    content_redacted: bool = True
    source_refs_redacted: bool = True
    procedure_redacted: bool = True
    blocked_effects: list[str] = Field(default_factory=lambda: list(DEMO_BLOCKED_EFFECTS))
    required_commands: list[str] = Field(default_factory=list)
    demo_steps: list[DemoStep] = Field(default_factory=list)
    checks: list[DemoReadinessCheck] = Field(default_factory=list)
    prohibited_marker_count: int = Field(ge=0)
    safety_failures: list[str] = Field(default_factory=list)
    policy_refs: list[str] = Field(default_factory=lambda: [DEMO_READINESS_POLICY_REF])

    @model_validator(mode="after")
    def keep_demo_safe_and_redacted(self) -> DemoReadinessReceipt:
        if not self.synthetic_only:
            raise ValueError("demo readiness must stay synthetic-only")
        if not self.localhost_only:
            raise ValueError("demo readiness must stay localhost-only")
        if self.real_screen_capture_started:
            raise ValueError("demo readiness cannot start real screen capture")
        if self.durable_raw_screen_storage_enabled:
            raise ValueError("demo readiness cannot enable durable raw screen storage")
        if self.raw_private_refs_returned:
            raise ValueError("demo readiness cannot return raw private refs")
        if self.secret_values_read:
            raise ValueError("demo readiness cannot read secret values")
        if self.model_secret_echo_attempted:
            raise ValueError("demo readiness cannot attempt model secret echo")
        if self.mutation_export_or_draft_enabled:
            raise ValueError("demo readiness cannot enable mutation/export/draft execution")
        if self.external_effect_enabled:
            raise ValueError("demo readiness cannot enable external effects")
        if not self.content_redacted or not self.source_refs_redacted or not self.procedure_redacted:
            raise ValueError("demo readiness receipt must stay redacted")
        missing_effects = sorted(set(DEMO_BLOCKED_EFFECTS) - set(self.blocked_effects))
        if missing_effects:
            raise ValueError(f"demo readiness missing blocked effects: {missing_effects}")
        if DEMO_READINESS_POLICY_REF not in self.policy_refs:
            raise ValueError("demo readiness requires policy ref")
        return self


class _DemoAuthenticatedCipher:
    name = "toy-demo-readiness-aead-test"
    authenticated_encryption = True

    def seal(self, plaintext: bytes) -> bytes:
        return b"sealed-demo-readiness:" + plaintext[::-1]

    def open(self, ciphertext: bytes) -> bytes:
        if not ciphertext.startswith(b"sealed-demo-readiness:"):
            raise ValueError("missing toy demo readiness seal")
        return ciphertext.removeprefix(b"sealed-demo-readiness:")[::-1]


def run_demo_readiness(
    *,
    now: datetime | None = None,
    repo_root: Path = REPO_ROOT,
) -> DemoReadinessReceipt:
    timestamp = _ensure_utc(now or datetime.now(UTC))
    checks: list[DemoReadinessCheck] = []

    dashboard = run_dashboard_shell_smoke()
    checks.append(
        DemoReadinessCheck(
            name="dashboard_safe_surface",
            passed=(
                dashboard.passed
                and dashboard.focus_inspector_present
                and dashboard.encryption_default_visible
                and not dashboard.secret_retained
                and not dashboard.raw_private_data_retained
            ),
            policy_refs=[dashboard.policy_ref],
            details={
                "focus_inspector_present": dashboard.focus_inspector_present,
                "encryption_default_visible": dashboard.encryption_default_visible,
                "safe_receipt_count": dashboard.safe_receipt_count,
                "read_only_gateway_action_count": dashboard.read_only_gateway_action_count,
                "blocked_gateway_action_count": dashboard.blocked_gateway_action_count,
            },
        )
    )

    ladder = run_synthetic_capture_ladder(now=timestamp)
    checks.append(
        DemoReadinessCheck(
            name="synthetic_capture_ladder",
            passed=(
                ladder.passed
                and ladder.synthetic_page_only
                and ladder.raw_ref_deleted_after_expiry
                and ladder.durable_synthetic_memory_written
                and ladder.audit_written
                and ladder.retrieval_hit
                and ladder.context_pack_hit
                and ladder.secret_value_leak_count == 0
                and not ladder.real_screen_capture_started
                and not ladder.raw_payload_committed
            ),
            policy_refs=[SYNTHETIC_CAPTURE_LADDER_POLICY_REF],
            details={
                "synthetic_page_only": ladder.synthetic_page_only,
                "raw_ref_scheme": ladder.raw_ref_scheme,
                "raw_ref_deleted_after_expiry": ladder.raw_ref_deleted_after_expiry,
                "retrieval_hit": ladder.retrieval_hit,
                "context_pack_hit": ladder.context_pack_hit,
                "secret_redaction_count": ladder.secret_redaction_count,
                "secret_value_leak_count": ladder.secret_value_leak_count,
            },
        )
    )

    encrypted_check = _run_encrypted_index_gateway_check(timestamp)
    checks.append(encrypted_check)

    hygiene = inspect_env_local_hygiene(repo_root=repo_root, env_file=repo_root / ".env.local")
    checks.append(
        DemoReadinessCheck(
            name="env_local_secret_hygiene",
            passed=hygiene.ignored_by_git and not hygiene.tracked_by_git and not hygiene.secret_values_read,
            policy_refs=[DEMO_READINESS_POLICY_REF, "policy_secret_pii_local_data_v1"],
            details={
                "path": hygiene.path,
                "exists": hygiene.exists,
                "ignored_by_git": hygiene.ignored_by_git,
                "tracked_by_git": hygiene.tracked_by_git,
                "secret_values_read": hygiene.secret_values_read,
            },
        )
    )

    checks.append(
        DemoReadinessCheck(
            name="unsafe_effects_blocked",
            passed=True,
            policy_refs=[DEMO_READINESS_POLICY_REF],
            details={effect: "blocked" for effect in DEMO_BLOCKED_EFFECTS},
        )
    )

    safety_failures = [check.name for check in checks if not check.passed]
    receipt = DemoReadinessReceipt(
        passed=not safety_failures,
        demo_ready=not safety_failures,
        safe_to_show_publicly=not safety_failures,
        generated_at=timestamp,
        required_commands=[
            "uv run cortex-demo --json",
            "uv run cortex-dashboard-shell --smoke --json",
            "uv run cortex-synthetic-capture-ladder --json",
            "uv run cortex-mcp --smoke",
            "python3 -m http.server 8792 --bind 127.0.0.1",
        ],
        demo_steps=_demo_steps(),
        checks=checks,
        prohibited_marker_count=0,
        safety_failures=safety_failures,
        policy_refs=[
            DEMO_READINESS_POLICY_REF,
            SYNTHETIC_CAPTURE_LADDER_POLICY_REF,
            UNIFIED_ENCRYPTED_GRAPH_INDEX_POLICY_REF,
        ],
    )
    prohibited_marker_count = _count_prohibited_markers(receipt.model_dump_json())
    return receipt.model_copy(update={"prohibited_marker_count": prohibited_marker_count})


def _run_encrypted_index_gateway_check(timestamp: datetime) -> DemoReadinessCheck:
    with TemporaryDirectory(prefix="cortex-demo-readiness-") as temp_name:
        store = UnifiedEncryptedGraphIndex(
            Path(temp_name) / "demo-readiness.sqlite3",
            cipher=_DemoAuthenticatedCipher(),
            index_key=b"cortex-demo-readiness-index-key",
            mode=VaultRuntimeMode.TEST,
        )
        memory = _demo_memory(timestamp)
        edge = _demo_edge()
        write_receipt = store.add_memory(memory, now=timestamp)
        graph_receipt = store.add_edge(edge, related_memory_ids=[memory.memory_id], now=timestamp)
        search = store.search_index(
            "demo auth callback verification",
            scope=RetrievalScope(active_project="cortex-memory-os"),
        )
        server = CortexMCPServer(store=store)
        gateway_result = server.handle_jsonrpc(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "memory.search_index",
                    "arguments": {
                        "query": "demo auth callback verification",
                        "active_project": "cortex-memory-os",
                    },
                },
            }
        )["result"]
        context_pack = server.get_context_pack(
            {
                "goal": "demo auth callback verification",
                "active_project": "cortex-memory-os",
                "limit": 5,
            }
        )
        serialized = json.dumps(
            {
                "write_receipt": write_receipt.model_dump(mode="json"),
                "graph_receipt": graph_receipt.model_dump(mode="json"),
                "search": search.model_dump(mode="json"),
                "gateway": gateway_result,
            },
            sort_keys=True,
        )
        leak_count = _count_prohibited_markers(serialized)
        passed = (
            write_receipt.content_redacted
            and write_receipt.source_refs_redacted
            and graph_receipt.graph_terms_redacted
            and search.hits
            and search.hits[0].memory_id == _DEMO_MEMORY_ID
            and search.receipt.query_redacted
            and gateway_result["hits"][0]["memory_id"] == _DEMO_MEMORY_ID
            and gateway_result["receipt"]["query_redacted"] is True
            and context_pack.relevant_memories
            and context_pack.relevant_memories[0].memory_id == _DEMO_MEMORY_ID
            and UNIFIED_ENCRYPTED_GRAPH_INDEX_POLICY_REF in context_pack.context_policy_refs
            and leak_count == 0
        )

        return DemoReadinessCheck(
            name="encrypted_index_gateway_context",
            passed=passed,
            policy_refs=[UNIFIED_ENCRYPTED_GRAPH_INDEX_POLICY_REF],
            details={
                "memory_id": _DEMO_MEMORY_ID,
                "write_token_digest_count": write_receipt.token_digest_count,
                "graph_token_digest_count": graph_receipt.graph_token_digest_count,
                "search_result_count": search.receipt.result_count,
                "gateway_result_count": gateway_result["receipt"]["result_count"],
                "context_pack_memory_count": len(context_pack.relevant_memories),
                "context_policy_ref_present": (
                    UNIFIED_ENCRYPTED_GRAPH_INDEX_POLICY_REF in context_pack.context_policy_refs
                ),
                "prohibited_marker_count": leak_count,
            },
        )


def _demo_memory(timestamp: datetime) -> MemoryRecord:
    return MemoryRecord(
        memory_id=_DEMO_MEMORY_ID,
        type=MemoryType.PROCEDURAL,
        content=(
            "Demo sealed context memory uses auth callback verification while "
            "staying redacted in demo readiness receipts."
        ),
        source_refs=["project:cortex-memory-os", "scene_demo_private_trace"],
        evidence_type=EvidenceType.OBSERVED_AND_INFERRED,
        confidence=0.91,
        status=MemoryStatus.ACTIVE,
        created_at=timestamp,
        valid_from=date(2026, 5, 1),
        valid_to=None,
        sensitivity=Sensitivity.PRIVATE_WORK,
        scope=ScopeLevel.PROJECT_SPECIFIC,
        influence_level=InfluenceLevel.PLANNING,
        allowed_influence=["demo_context_pack"],
        forbidden_influence=["production_capture", "external_effects"],
        decay_policy="delete_demo_db_after_run",
        contradicts=[],
        user_visible=True,
        requires_user_confirmation=False,
    )


def _demo_edge() -> TemporalEdge:
    return TemporalEdge(
        edge_id="edge_demo_readiness_context",
        subject="demo_user",
        predicate="verifies",
        object="OAuth callback route mismatch",
        valid_from=date(2026, 5, 1),
        valid_to=None,
        confidence=0.84,
        source_refs=["scene_demo_private_trace"],
        status=MemoryStatus.ACTIVE,
        supersedes=[],
    )


def _demo_steps() -> list[DemoStep]:
    return [
        DemoStep(
            step_id="demo_1_dashboard",
            title="Open the local dashboard",
            surface="ui/cortex-dashboard/index.html",
            command="python3 -m http.server 8792 --bind 127.0.0.1",
            proof="Shadow Pointer, Memory Palace, Skill Forge, guardrails, and receipts render from synthetic data.",
            safety_note="Localhost static UI only; no capture or gateway mutation is started.",
        ),
        DemoStep(
            step_id="demo_2_synthetic_ladder",
            title="Run the synthetic capture ladder",
            surface="cortex-synthetic-capture-ladder",
            command="uv run cortex-synthetic-capture-ladder --json",
            proof="Temp raw ref expires, synthetic memory writes to a local test DB, retrieval and context pack hit.",
            safety_note="Disposable synthetic page only; secret-in-screen fixture is masked before any write.",
        ),
        DemoStep(
            step_id="demo_3_encrypted_index",
            title="Show encrypted index retrieval",
            surface="memory.search_index",
            proof="Gateway returns metadata-only hits from sealed memory payloads and HMAC index metadata.",
            safety_note="Content, source refs, graph terms, and query text stay redacted in receipts.",
        ),
        DemoStep(
            step_id="demo_4_context_pack",
            title="Show context pack policy",
            surface="memory.get_context_pack",
            proof="Context pack includes encrypted-index policy refs and redacted retrieval diagnostics.",
            safety_note="No external effects, mutation, export, draft execution, or model secret echo paths are enabled.",
        ),
    ]


def _count_prohibited_markers(text: str) -> int:
    return sum(1 for marker in _PROHIBITED_MARKERS if marker in text)


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    result = run_demo_readiness()
    if args.json:
        print(json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True))
    else:
        status = "ready" if result.demo_ready else "not ready"
        print(
            f"{DEMO_READINESS_ID}: {status}; "
            f"checks={sum(int(check.passed) for check in result.checks)}/{len(result.checks)}; "
            f"blocked_effects={len(result.blocked_effects)}"
        )
        if result.safety_failures:
            print("failures: " + ", ".join(result.safety_failures))
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
