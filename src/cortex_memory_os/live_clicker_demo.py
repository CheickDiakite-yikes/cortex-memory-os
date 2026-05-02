"""Visible localhost Shadow Clicker demo with governed observation receipts."""

from __future__ import annotations

import argparse
import json
import mimetypes
import tempfile
import threading
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Literal, Any
from urllib.parse import urlparse

from pydantic import Field, ValidationError, field_validator

from cortex_memory_os.contracts import (
    AuditEvent,
    ConsentState,
    EvidenceType,
    InfluenceLevel,
    MemoryRecord,
    MemoryStatus,
    MemoryType,
    ObservationEvent,
    ObservationEventType,
    PerceptionEventEnvelope,
    PerceptionRoute,
    PerceptionSourceKind,
    ScopeLevel,
    Sensitivity,
    SourceTrust,
    StrictModel,
)
from cortex_memory_os.evidence_eligibility import build_evidence_eligibility_plan
from cortex_memory_os.firewall import assess_perception_envelope
from cortex_memory_os.mcp_server import CortexMCPServer
from cortex_memory_os.memory_palace import MemoryPalaceService
from cortex_memory_os.perception_adapters import AdapterHandoffResult, AdapterSource
from cortex_memory_os.shadow_pointer_capture import (
    SHADOW_POINTER_CAPTURE_WIRING_POLICY_REF,
    build_shadow_pointer_capture_receipt,
)
from cortex_memory_os.sqlite_store import SQLiteMemoryGraphStore

LIVE_CLICKER_DEMO_ID = "LIVE-CLICKER-DEMO-001"
LIVE_CLICKER_DEMO_POLICY_REF = "policy_live_clicker_demo_v1"

REPO_ROOT = Path(__file__).resolve().parents[2]
UI_ROOT = REPO_ROOT / "ui" / "live-clicker-demo"
DEFAULT_LIVE_CLICKER_HOST = "127.0.0.1"
DEFAULT_LIVE_CLICKER_PORT = 8795

_PROHIBITED_MARKERS = [
    "OPENAI_API_KEY=",
    "CORTEX_FAKE_TOKEN",
    "sk-",
    "raw://",
    "encrypted_blob://",
    "Ignore previous instructions",
    "BEGIN " + "PRIVATE KEY",
]


class LiveClickerObservationInput(StrictModel):
    action: Literal["view", "click", "input"]
    target_label: str = Field(min_length=1, max_length=120)
    pointer_x: float = Field(ge=0, le=10000)
    pointer_y: float = Field(ge=0, le=10000)
    page_url: str = Field(min_length=1)
    visible_text: str = Field(min_length=1, max_length=500)
    sequence: int = Field(default=0, ge=0)

    @field_validator("target_label", "visible_text")
    @classmethod
    def reject_obvious_raw_markers(cls, value: str) -> str:
        if any(marker in value for marker in ("raw://", "encrypted_blob://")):
            raise ValueError("live clicker inputs cannot carry raw refs")
        return value


class LiveClickerObservationReceipt(StrictModel):
    receipt_id: str = Field(min_length=1)
    event_id: str = Field(min_length=1)
    action: str = Field(min_length=1)
    target_label: str = Field(min_length=1)
    pointer_x: float = Field(ge=0)
    pointer_y: float = Field(ge=0)
    local_origin: bool
    firewall_decision: str = Field(min_length=1)
    evidence_write_mode: str = Field(min_length=1)
    shadow_pointer_state: str = Field(min_length=1)
    observation_active: bool
    memory_write_allowed: bool
    demo_candidate_memory_written: bool
    memory_id: str | None = None
    memory_status: str | None = None
    audit_event_id: str | None = None
    retrieval_hit: bool = False
    context_pack_hit: bool = False
    raw_ref_retained: bool = False
    external_effect_executed: bool = False
    policy_refs: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)


class LiveClickerDemoResult(StrictModel):
    proof_id: str = LIVE_CLICKER_DEMO_ID
    policy_ref: str = LIVE_CLICKER_DEMO_POLICY_REF
    passed: bool
    generated_at: datetime
    local_origin_only: bool
    shadow_clicker_followed: bool
    observation_count: int = Field(ge=0)
    memory_write_count: int = Field(ge=0)
    retrieval_hit_count: int = Field(ge=0)
    context_pack_hit_count: int = Field(ge=0)
    raw_ref_retained_count: int = Field(ge=0)
    external_effect_count: int = Field(ge=0)
    real_screen_capture_started: bool = False
    durable_private_memory_written: bool = False
    demo_temp_store_used: bool = True
    prohibited_marker_count: int = Field(ge=0)
    latest_shadow_pointer_state: str | None = None
    observed_memory_ids: list[str] = Field(default_factory=list)
    safety_failures: list[str] = Field(default_factory=list)


class LiveClickerDemoSession:
    """Small live session store used by the localhost demo server."""

    def __init__(self, *, db_path: Path, now: datetime | None = None) -> None:
        self.store = SQLiteMemoryGraphStore(db_path)
        self._receipts: list[LiveClickerObservationReceipt] = []
        self._lock = threading.Lock()
        self._fixed_now = _ensure_utc(now) if now else None

    def observe(self, payload: Mapping[str, Any]) -> LiveClickerObservationReceipt:
        observation = LiveClickerObservationInput.model_validate(payload)
        with self._lock:
            sequence = len(self._receipts) + 1
            timestamp = self._timestamp(sequence)
            event_id = f"live_clicker_obs_{sequence:03d}"
            local_origin = _is_local_url(observation.page_url)
            text = _observation_text(observation)
            derived_ref = f"derived://live-clicker-demo/{event_id}"
            envelope = _build_envelope(
                event_id=event_id,
                timestamp=timestamp,
                sequence=sequence,
                page_url=observation.page_url,
                derived_ref=derived_ref,
                local_origin=local_origin,
            )
            firewall = assess_perception_envelope(envelope, text, now=timestamp)
            evidence_plan = build_evidence_eligibility_plan(
                envelope,
                firewall.decision,
                redacted_text_ref=derived_ref,
            )
            handoff = AdapterHandoffResult(
                adapter_source=AdapterSource.BROWSER,
                envelope=envelope,
                firewall=firewall.decision,
                evidence_plan=evidence_plan,
                redacted_text=firewall.redacted_text,
            )
            shadow_receipt = build_shadow_pointer_capture_receipt(handoff)
            memory_id: str | None = None
            memory_status: str | None = None
            audit_event_id: str | None = None
            retrieval_hit = False
            context_pack_hit = False
            demo_candidate_memory_written = False

            if local_origin and evidence_plan.eligible_for_memory:
                memory = _memory_from_observation(
                    event_id=event_id,
                    observation=observation,
                    evidence_id=evidence_plan.evidence_id,
                    timestamp=timestamp,
                )
                self.store.add_memory(memory)
                audit = _memory_audit(memory.memory_id, event_id, timestamp)
                self.store.add_audit_event(audit)
                memory_id = memory.memory_id
                memory_status = memory.status.value
                audit_event_id = audit.audit_event_id
                demo_candidate_memory_written = True
                retrieval_hit = memory_id in {
                    item.memory_id
                    for item in self.store.search_memories(
                        _retrieval_query_for_observation(observation),
                        limit=5,
                    )
                }
                context_pack = CortexMCPServer(
                    store=self.store,
                    palace=MemoryPalaceService(self.store),
                ).get_context_pack(
                    {
                        "goal": _retrieval_query_for_observation(observation),
                        "active_project": "cortex-memory-os",
                        "session_id": "live-clicker-demo",
                        "limit": 5,
                    }
                )
                context_pack_hit = memory_id in {
                    item.memory_id for item in context_pack.relevant_memories
                }

            receipt = LiveClickerObservationReceipt(
                receipt_id=f"receipt_{event_id}",
                event_id=event_id,
                action=observation.action,
                target_label=observation.target_label,
                pointer_x=observation.pointer_x,
                pointer_y=observation.pointer_y,
                local_origin=local_origin,
                firewall_decision=firewall.decision.decision.value,
                evidence_write_mode=evidence_plan.write_mode.value,
                shadow_pointer_state=shadow_receipt.resulting_snapshot.state.value,
                observation_active=shadow_receipt.observation_active,
                memory_write_allowed=shadow_receipt.memory_write_allowed,
                demo_candidate_memory_written=demo_candidate_memory_written,
                memory_id=memory_id,
                memory_status=memory_status,
                audit_event_id=audit_event_id,
                retrieval_hit=retrieval_hit,
                context_pack_hit=context_pack_hit,
                raw_ref_retained=evidence_plan.raw_ref is not None,
                external_effect_executed=False,
                policy_refs=_ordered_policy_refs(
                    [
                        LIVE_CLICKER_DEMO_POLICY_REF,
                        SHADOW_POINTER_CAPTURE_WIRING_POLICY_REF,
                    ],
                    shadow_receipt.policy_refs,
                    evidence_plan.policy_refs,
                ),
                safety_notes=[
                    "localhost demo page only",
                    "pointer telemetry is page-local and user-visible",
                    "candidate memories use the demo temp store, not private production memory",
                    "raw screen capture and external effects stay off",
                ],
            )
            self._receipts.append(receipt)
            return receipt

    def result(self) -> LiveClickerDemoResult:
        with self._lock:
            receipts = list(self._receipts)
        safety_failures: list[str] = []
        local_origin_only = all(receipt.local_origin for receipt in receipts) if receipts else False
        shadow_clicker_followed = all(
            receipt.pointer_x >= 0 and receipt.pointer_y >= 0 for receipt in receipts
        ) and bool(receipts)
        raw_ref_retained_count = sum(1 for receipt in receipts if receipt.raw_ref_retained)
        external_effect_count = sum(1 for receipt in receipts if receipt.external_effect_executed)
        memory_write_count = sum(
            1 for receipt in receipts if receipt.demo_candidate_memory_written
        )
        retrieval_hit_count = sum(1 for receipt in receipts if receipt.retrieval_hit)
        context_pack_hit_count = sum(1 for receipt in receipts if receipt.context_pack_hit)
        marker_blob = "\n".join(receipt.model_dump_json() for receipt in receipts)
        prohibited_marker_count = sum(1 for marker in _PROHIBITED_MARKERS if marker in marker_blob)

        checks = {
            "observation_count": len(receipts) >= 3,
            "local_origin_only": local_origin_only,
            "shadow_clicker_followed": shadow_clicker_followed,
            "memory_write_count": memory_write_count >= 1,
            "retrieval_hit_count": retrieval_hit_count >= 1,
            "context_pack_hit_count": context_pack_hit_count >= 1,
            "raw_ref_retained_count": raw_ref_retained_count == 0,
            "external_effect_count": external_effect_count == 0,
            "prohibited_marker_count": prohibited_marker_count == 0,
        }
        safety_failures.extend(name for name, passed in checks.items() if not passed)
        latest_shadow_state = receipts[-1].shadow_pointer_state if receipts else None
        return LiveClickerDemoResult(
            passed=not safety_failures,
            generated_at=datetime.now(UTC),
            local_origin_only=local_origin_only,
            shadow_clicker_followed=shadow_clicker_followed,
            observation_count=len(receipts),
            memory_write_count=memory_write_count,
            retrieval_hit_count=retrieval_hit_count,
            context_pack_hit_count=context_pack_hit_count,
            raw_ref_retained_count=raw_ref_retained_count,
            external_effect_count=external_effect_count,
            prohibited_marker_count=prohibited_marker_count,
            latest_shadow_pointer_state=latest_shadow_state,
            observed_memory_ids=[
                receipt.memory_id
                for receipt in receipts
                if receipt.memory_id is not None
            ],
            safety_failures=safety_failures,
        )

    def _timestamp(self, sequence: int) -> datetime:
        if self._fixed_now is not None:
            return self._fixed_now.replace(microsecond=0)
        base = datetime.now(UTC).replace(microsecond=0)
        return base.replace(second=min(base.second + sequence, 59))


class LiveClickerDemoHandler(BaseHTTPRequestHandler):
    server_version = "CortexLiveClickerDemo/0.1"

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/":
            path = "/index.html"
        if path == "/results":
            self._write_json(self._session().result().model_dump(mode="json"))
            return
        static_path = (UI_ROOT / path.removeprefix("/")).resolve()
        if not static_path.is_file() or UI_ROOT.resolve() not in static_path.parents:
            self.send_error(HTTPStatus.NOT_FOUND, "not found")
            return
        content_type = mimetypes.guess_type(static_path.name)[0] or "application/octet-stream"
        data = static_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self) -> None:  # noqa: N802
        if urlparse(self.path).path != "/observe":
            self.send_error(HTTPStatus.NOT_FOUND, "not found")
            return
        content_length = int(self.headers.get("Content-Length", "0") or "0")
        if content_length > 64 * 1024:
            self._write_json({"error": "payload_too_large"}, status=HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
            return
        try:
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("payload must be object")
            receipt = self._session().observe(payload)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError, ValidationError) as error:
            self._write_json(
                {
                    "error": "invalid_observation",
                    "message": str(error),
                    "policy_ref": LIVE_CLICKER_DEMO_POLICY_REF,
                },
                status=HTTPStatus.UNPROCESSABLE_ENTITY,
            )
            return
        self._write_json(receipt.model_dump(mode="json"))

    def log_message(self, _format: str, *_args: Any) -> None:
        return

    def _session(self) -> LiveClickerDemoSession:
        if not isinstance(self.server, LiveClickerDemoHTTPServer):
            raise RuntimeError("live clicker demo server missing session")
        return self.server.session

    def _write_json(
        self,
        payload: Mapping[str, Any],
        *,
        status: HTTPStatus = HTTPStatus.OK,
    ) -> None:
        data = json.dumps(payload, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class LiveClickerDemoHTTPServer(ThreadingHTTPServer):
    def __init__(
        self,
        server_address: tuple[str, int],
        session: LiveClickerDemoSession,
    ) -> None:
        super().__init__(server_address, LiveClickerDemoHandler)
        self.session = session


@dataclass
class RunningLiveClickerDemo:
    server: LiveClickerDemoHTTPServer
    thread: threading.Thread
    temp_dir: tempfile.TemporaryDirectory[str]

    @property
    def base_url(self) -> str:
        host, port = self.server.server_address
        return f"http://{host}:{port}"

    def stop(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temp_dir.cleanup()

    def result(self) -> LiveClickerDemoResult:
        return self.server.session.result()


def start_live_clicker_demo(
    *,
    host: str = DEFAULT_LIVE_CLICKER_HOST,
    port: int = DEFAULT_LIVE_CLICKER_PORT,
) -> RunningLiveClickerDemo:
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("live clicker demo must bind localhost")
    temp_dir = tempfile.TemporaryDirectory(prefix="cortex-live-clicker-demo-")
    session = LiveClickerDemoSession(
        db_path=Path(temp_dir.name) / "live-clicker-demo.sqlite3",
    )
    server = LiveClickerDemoHTTPServer((host, port), session)
    thread = threading.Thread(target=server.serve_forever, name="cortex-live-clicker-demo")
    thread.daemon = True
    thread.start()
    return RunningLiveClickerDemo(server=server, thread=thread, temp_dir=temp_dir)


def run_live_clicker_demo_smoke() -> LiveClickerDemoResult:
    timestamp = datetime(2026, 5, 2, 10, 0, tzinfo=UTC)
    with tempfile.TemporaryDirectory(prefix="cortex-live-clicker-demo-smoke-") as temp_name:
        session = LiveClickerDemoSession(
            db_path=Path(temp_name) / "live-clicker-demo.sqlite3",
            now=timestamp,
        )
        for sequence, (action, target, text, x, y) in enumerate(
            [
                (
                    "click",
                    "Open research note",
                    "safe site action for live clicker observation",
                    238,
                    264,
                ),
                (
                    "input",
                    "Capture task note",
                    "typed note: compare primary sources before synthesis",
                    318,
                    378,
                ),
                (
                    "click",
                    "Record conclusion",
                    "safe site conclusion recorded for candidate memory",
                    512,
                    506,
                ),
            ],
            start=1,
        ):
            session.observe(
                {
                    "action": action,
                    "target_label": target,
                    "pointer_x": x,
                    "pointer_y": y,
                    "page_url": "http://127.0.0.1:8795/",
                    "visible_text": text,
                    "sequence": sequence,
                }
            )
        return session.result()


def _build_envelope(
    *,
    event_id: str,
    timestamp: datetime,
    sequence: int,
    page_url: str,
    derived_ref: str,
    local_origin: bool,
) -> PerceptionEventEnvelope:
    observation = ObservationEvent(
        event_id=event_id,
        event_type=ObservationEventType.BROWSER_DOM,
        timestamp=timestamp,
        device="computer-use-browser",
        app="Chrome",
        window_title="Cortex Safe Clicker Demo" if local_origin else None,
        project_id="cortex-memory-os",
        payload_ref=f"volatile://live-clicker-demo/{event_id}",
        source_trust=SourceTrust.LOCAL_OBSERVED if local_origin else SourceTrust.EXTERNAL_UNTRUSTED,
        capture_scope=ScopeLevel.SESSION_ONLY,
        consent_state=ConsentState.ACTIVE,
        raw_contains_user_input=False,
    )
    return PerceptionEventEnvelope(
        envelope_id=f"perception_live_clicker_{event_id}",
        source_kind=PerceptionSourceKind.BROWSER,
        observation=observation,
        observed_at=timestamp,
        sequence=sequence,
        consent_state=ConsentState.ACTIVE,
        capture_scope=ScopeLevel.SESSION_ONLY,
        source_trust=observation.source_trust,
        sensitivity_hint=Sensitivity.LOW if local_origin else Sensitivity.PRIVATE_WORK,
        route=PerceptionRoute.FIREWALL_REQUIRED,
        raw_ref=None,
        derived_refs=[derived_ref],
        third_party_content=not local_origin,
        prompt_injection_risk=False,
        required_policy_refs=[LIVE_CLICKER_DEMO_POLICY_REF],
    )


def _memory_from_observation(
    *,
    event_id: str,
    observation: LiveClickerObservationInput,
    evidence_id: str,
    timestamp: datetime,
) -> MemoryRecord:
    return MemoryRecord(
        memory_id=f"mem_{event_id}",
        type=MemoryType.EPISODIC,
        content=(
            "Live clicker safe site observation: Computer Use performed "
            f"{observation.action} on {observation.target_label}. "
            "This is a demo candidate memory from localhost telemetry."
        ),
        source_refs=[evidence_id, f"event:{event_id}", "session:live-clicker-demo"],
        evidence_type=EvidenceType.OBSERVED,
        confidence=0.84,
        status=MemoryStatus.CANDIDATE,
        created_at=timestamp,
        valid_from=timestamp.date(),
        sensitivity=Sensitivity.LOW,
        scope=ScopeLevel.SESSION_ONLY,
        influence_level=InfluenceLevel.DIRECT_QUERY,
        allowed_influence=["demo_retrieval", "context_pack_debug"],
        forbidden_influence=["external_effects", "production_private_memory"],
        decay_policy="delete_demo_store_after_process_exit",
        user_visible=True,
        requires_user_confirmation=True,
    )


def _memory_audit(memory_id: str, event_id: str, timestamp: datetime) -> AuditEvent:
    return AuditEvent(
        audit_event_id=f"audit_live_clicker_{event_id}",
        timestamp=timestamp,
        actor="cortex-live-clicker-demo",
        action="write_demo_candidate_memory",
        target_ref=f"memory:{memory_id}",
        policy_refs=[LIVE_CLICKER_DEMO_POLICY_REF],
        result="candidate_memory_written_to_demo_temp_store",
        human_visible=True,
        redacted_summary=(
            "Wrote a localhost demo candidate memory from visible pointer telemetry; "
            "raw screen capture, raw refs, and external effects were not used."
        ),
    )


def _observation_text(observation: LiveClickerObservationInput) -> str:
    return (
        f"Local Cortex safe site action. Target: {observation.target_label}. "
        f"Action: {observation.action}. Visible safe text: {observation.visible_text}."
    )


def _retrieval_query_for_observation(observation: LiveClickerObservationInput) -> str:
    return (
        "live clicker safe site observation memory context "
        f"{observation.action} {observation.target_label}"
    )


def _is_local_url(url: str) -> bool:
    parsed = urlparse(url if "://" in url else f"http://{url}")
    return parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "localhost", "::1"}


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _ordered_policy_refs(*groups: list[str] | tuple[str, ...]) -> list[str]:
    refs: list[str] = []
    for group in groups:
        for ref in group:
            if ref not in refs:
                refs.append(ref)
    return refs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=DEFAULT_LIVE_CLICKER_HOST)
    parser.add_argument("--port", default=DEFAULT_LIVE_CLICKER_PORT, type=int)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.smoke:
        result = run_live_clicker_demo_smoke()
        payload = result.model_dump(mode="json")
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(
                "live clicker demo "
                f"{'passed' if result.passed else 'failed'}: "
                f"{result.observation_count} observations, "
                f"{result.memory_write_count} demo memories"
            )
        return 0 if result.passed else 1

    demo = start_live_clicker_demo(host=args.host, port=args.port)
    try:
        print(
            json.dumps(
                {
                    "url": demo.base_url,
                    "proof_id": LIVE_CLICKER_DEMO_ID,
                    "policy_ref": LIVE_CLICKER_DEMO_POLICY_REF,
                    "localhost_only": True,
                },
                sort_keys=True,
            )
        )
        demo.thread.join()
    except KeyboardInterrupt:
        demo.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
