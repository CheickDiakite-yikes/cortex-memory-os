"""Localhost-only bridge for launching the native Shadow Clicker from the dashboard."""

from __future__ import annotations

import argparse
import json
import os
import secrets
import subprocess
import sys
import threading
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Protocol
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from pydantic import Field

from cortex_memory_os.contracts import StrictModel
from cortex_memory_os.live_adapters import REPO_ROOT
from cortex_memory_os.native_cursor_follow import (
    NATIVE_CURSOR_FOLLOW_ID,
    NATIVE_CURSOR_FOLLOW_POLICY_REF,
    native_cursor_follow_command,
)
from cortex_memory_os.native_permission_smoke import (
    NativePermissionSmokeResult,
    build_fixture_permission_smoke_result,
    run_native_permission_smoke,
)
from cortex_memory_os.native_screen_capture_probe import (
    NativeScreenCaptureProbeResult,
    build_fixture_native_screen_capture_probe_result,
    run_native_screen_capture_probe,
)
from cortex_memory_os.capture_preflight_diagnostics import (
    CAPTURE_PREFLIGHT_DIAGNOSTICS_ID,
    CapturePreflightDiagnostics,
    build_capture_preflight_diagnostics,
)
from cortex_memory_os.real_capture_control import (
    DASHBOARD_CAPTURE_CONTROL_ID,
)

CAPTURE_CONTROL_SERVER_POLICY_REF = "policy_capture_control_local_bridge_v1"
DEFAULT_CAPTURE_CONTROL_HOST = "127.0.0.1"
DEFAULT_CAPTURE_CONTROL_PORT = 8799
MAX_CAPTURE_CONTROL_DURATION_SECONDS = 300
CAPTURE_CONTROL_STATUS_PATH = "/api/capture/status"
CAPTURE_CONTROL_START_PATH = "/api/capture/start"
CAPTURE_CONTROL_STOP_PATH = "/api/capture/stop"
CAPTURE_CONTROL_PERMISSIONS_PATH = "/api/capture/permissions"
CAPTURE_CONTROL_PREFLIGHT_PATH = "/api/capture/preflight"
CAPTURE_CONTROL_SCREEN_PROBE_PATH = "/api/capture/screen-probe"
CAPTURE_CONTROL_RECEIPTS_PATH = "/api/capture/receipts"
CAPTURE_CONTROL_CONFIG_PATH = "/capture-control-config.js"
CAPTURE_CONTROL_PREFLIGHT_BRIDGE_ID = "CAPTURE-CONTROL-PREFLIGHT-BRIDGE-001"
CAPTURE_SESSION_WATCHDOG_ID = "CAPTURE-SESSION-WATCHDOG-001"
UI_ROOT = REPO_ROOT / "ui" / "cortex-dashboard"


class ManagedProcess(Protocol):
    pid: int

    def poll(self) -> int | None: ...

    def terminate(self) -> None: ...


PopenFactory = Callable[..., ManagedProcess]
PermissionRunner = Callable[[], NativePermissionSmokeResult]
ScreenProbeRunner = Callable[[bool], NativeScreenCaptureProbeResult]


class CaptureControlBridgeReceipt(StrictModel):
    policy_ref: str = CAPTURE_CONTROL_SERVER_POLICY_REF
    dashboard_panel_id: str = DASHBOARD_CAPTURE_CONTROL_ID
    native_benchmark_id: str = NATIVE_CURSOR_FOLLOW_ID
    native_policy_ref: str = NATIVE_CURSOR_FOLLOW_POLICY_REF
    action: str
    state: str
    running: bool
    pid: int | None = None
    command: list[str] = Field(default_factory=list)
    duration_seconds: float | None = None
    started_at: datetime | None = None
    stopped_at: datetime | None = None
    exit_code: int | None = None
    localhost_only: bool = True
    fixed_command_only: bool = True
    capture_started: bool = False
    accessibility_observer_started: bool = False
    memory_write_allowed: bool = False
    raw_ref_retained: bool = False
    raw_screen_storage_enabled: bool = False
    screen_recording_preflight: bool | None = None
    accessibility_trusted: bool | None = None
    skip_reason: str | None = None
    next_user_actions: list[str] = Field(default_factory=list)
    error_code: str | None = None


class CaptureControlReceiptSummary(StrictModel):
    policy_ref: str = CAPTURE_CONTROL_SERVER_POLICY_REF
    receipt_count: int = Field(ge=0)
    running_count: int = Field(ge=0)
    start_count: int = Field(ge=0)
    stop_count: int = Field(ge=0)
    permission_check_count: int = Field(ge=0)
    preflight_count: int = Field(ge=0)
    screen_probe_count: int = Field(ge=0)
    skipped_screen_probe_count: int = Field(ge=0)
    watchdog_exit_count: int = Field(ge=0)
    blocked_count: int = Field(ge=0)
    raw_payloads_included: bool = False
    raw_pixels_returned: bool = False
    raw_ref_retained: bool = False
    memory_write_allowed: bool = False


class CaptureControlServerSmokeResult(StrictModel):
    policy_ref: str = CAPTURE_CONTROL_SERVER_POLICY_REF
    passed: bool
    bind_host: str
    bind_port: int
    status_code: int
    start_status_code: int
    stop_status_code: int
    served_dashboard: bool
    start_receipt: CaptureControlBridgeReceipt
    stop_receipt: CaptureControlBridgeReceipt
    receipts_status_code: int
    receipt_summary: CaptureControlReceiptSummary
    permission_status_code: int
    permission_receipt: NativePermissionSmokeResult
    preflight_status_code: int
    preflight_receipt: CapturePreflightDiagnostics
    screen_probe_status_code: int
    screen_probe_receipt: NativeScreenCaptureProbeResult
    config_status_code: int
    token_required: bool
    missing_token_rejected_status_code: int
    bad_origin_rejected_status_code: int
    remote_rejected_status_code: int


class CaptureControlProcessManager:
    def __init__(
        self,
        *,
        package_path: Path | None = None,
        popen_factory: PopenFactory | None = None,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self.package_path = package_path
        self.popen_factory = popen_factory or subprocess.Popen
        self.now = now or (lambda: datetime.now(UTC))
        self._process: ManagedProcess | None = None
        self._command: list[str] = []
        self._duration_seconds: float | None = None
        self._started_at: datetime | None = None
        self._stopped_at: datetime | None = None
        self._receipts: list[CaptureControlBridgeReceipt] = []

    def status(self) -> CaptureControlBridgeReceipt:
        exited = self._consume_exited_process()
        if exited is not None:
            return exited
        running = self._is_running()
        receipt = CaptureControlBridgeReceipt(
            action="status",
            state="running" if running else "stopped",
            running=running,
            pid=self._process.pid if running and self._process else None,
            command=self._command if running else [],
            duration_seconds=self._duration_seconds if running else None,
            started_at=self._started_at if running else None,
            stopped_at=None if running else self._stopped_at,
        )
        self._record(receipt)
        return receipt

    def start(self, *, duration_seconds: float = 30) -> CaptureControlBridgeReceipt:
        self._consume_exited_process()
        if self._is_running():
            receipt = self.status()
            receipt.action = "start"
            return receipt

        bounded_duration = max(1.0, min(float(duration_seconds), MAX_CAPTURE_CONTROL_DURATION_SECONDS))
        command = native_cursor_follow_command(
            smoke=False,
            json_output=True,
            duration_seconds=bounded_duration,
            **({"package_path": self.package_path} if self.package_path else {}),
        )
        process = self.popen_factory(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self._process = process
        self._command = command
        self._duration_seconds = bounded_duration
        self._started_at = self.now()
        self._stopped_at = None
        receipt = CaptureControlBridgeReceipt(
            action="start",
            state="running",
            running=True,
            pid=process.pid,
            command=command,
            duration_seconds=bounded_duration,
            started_at=self._started_at,
        )
        self._record(receipt)
        return receipt

    def stop(self) -> CaptureControlBridgeReceipt:
        if self._is_running() and self._process is not None:
            self._process.terminate()
        self._stopped_at = self.now()
        self._process = None
        self._duration_seconds = None
        self._command = []
        receipt = CaptureControlBridgeReceipt(
            action="stop",
            state="stopped",
            running=False,
            stopped_at=self._stopped_at,
        )
        self._record(receipt)
        return receipt

    def record_bridge_receipt(self, receipt: CaptureControlBridgeReceipt) -> None:
        self._record(receipt)

    def receipt_summary(self) -> CaptureControlReceiptSummary:
        receipts = list(self._receipts)
        return CaptureControlReceiptSummary(
            receipt_count=len(receipts),
            running_count=sum(int(receipt.running) for receipt in receipts),
            start_count=sum(int(receipt.action == "start") for receipt in receipts),
            stop_count=sum(int(receipt.action == "stop") for receipt in receipts),
            permission_check_count=sum(int(receipt.action == "permissions") for receipt in receipts),
            preflight_count=sum(int(receipt.action == "preflight") for receipt in receipts),
            screen_probe_count=sum(int(receipt.action == "screen_probe") for receipt in receipts),
            skipped_screen_probe_count=sum(
                int(receipt.action == "screen_probe" and receipt.skip_reason is not None)
                for receipt in receipts
            ),
            watchdog_exit_count=sum(int(receipt.action == "watchdog") for receipt in receipts),
            blocked_count=sum(int(receipt.state == "blocked") for receipt in receipts),
            raw_payloads_included=False,
            raw_pixels_returned=False,
            raw_ref_retained=any(receipt.raw_ref_retained for receipt in receipts),
            memory_write_allowed=any(receipt.memory_write_allowed for receipt in receipts),
        )

    def _is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def _consume_exited_process(self) -> CaptureControlBridgeReceipt | None:
        if self._process is None:
            return None
        exit_code = self._process.poll()
        if exit_code is None:
            return None
        pid = self._process.pid
        command = list(self._command)
        stopped_at = self.now()
        self._process = None
        self._command = []
        self._duration_seconds = None
        self._stopped_at = stopped_at
        receipt = CaptureControlBridgeReceipt(
            action="watchdog",
            state="exited",
            running=False,
            pid=pid,
            command=command,
            exit_code=exit_code,
            stopped_at=stopped_at,
            next_user_actions=[
                "Restart Shadow Clicker from the dashboard if observation should continue."
            ],
        )
        self._record(receipt)
        return receipt

    def _record(self, receipt: CaptureControlBridgeReceipt) -> None:
        self._receipts.append(receipt)
        if len(self._receipts) > 50:
            self._receipts = self._receipts[-50:]


@dataclass(frozen=True)
class CaptureControlEndpoint:
    server: ThreadingHTTPServer
    thread: threading.Thread
    host: str
    port: int
    session_token: str

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def shutdown(self) -> None:
        self.server.shutdown()
        self.thread.join(timeout=2)
        self.server.server_close()


def client_host_allowed(host: str) -> bool:
    return host in {"127.0.0.1", "::1", "localhost"}


def build_capture_control_handler(
    manager: CaptureControlProcessManager,
    *,
    ui_root: Path = UI_ROOT,
    session_token: str,
    permission_runner: PermissionRunner = run_native_permission_smoke,
    screen_probe_runner: ScreenProbeRunner = run_native_screen_capture_probe,
    remote_probe_status: int | None = None,
) -> type[BaseHTTPRequestHandler]:
    class CaptureControlHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            if not self._client_allowed():
                return
            if self.path == CAPTURE_CONTROL_CONFIG_PATH:
                self._write_javascript(
                    200,
                    {
                        "token": session_token,
                        "statusPath": CAPTURE_CONTROL_STATUS_PATH,
                        "startPath": CAPTURE_CONTROL_START_PATH,
                        "stopPath": CAPTURE_CONTROL_STOP_PATH,
                        "permissionsPath": CAPTURE_CONTROL_PERMISSIONS_PATH,
                        "preflightPath": CAPTURE_CONTROL_PREFLIGHT_PATH,
                        "screenProbePath": CAPTURE_CONTROL_SCREEN_PROBE_PATH,
                        "receiptsPath": CAPTURE_CONTROL_RECEIPTS_PATH,
                    },
                )
                return
            if self.path == CAPTURE_CONTROL_STATUS_PATH:
                if not self._authorized():
                    return
                self._write_json(200, manager.status().model_dump(mode="json"))
                return
            if self.path == CAPTURE_CONTROL_PERMISSIONS_PATH:
                if not self._authorized():
                    return
                receipt = permission_runner()
                manager.record_bridge_receipt(
                    _bridge_receipt_from_permission_result(receipt)
                )
                self._write_json(200, receipt.model_dump(mode="json"))
                return
            if self.path == CAPTURE_CONTROL_PREFLIGHT_PATH:
                if not self._authorized():
                    return
                permission = permission_runner()
                receipt = build_capture_preflight_diagnostics(
                    permission,
                    host_pid=os.getpid(),
                    executable_path=sys.executable,
                )
                manager.record_bridge_receipt(_bridge_receipt_from_preflight(receipt))
                self._write_json(200, receipt.model_dump(mode="json"))
                return
            if self.path == CAPTURE_CONTROL_RECEIPTS_PATH:
                if not self._authorized():
                    return
                self._write_json(200, manager.receipt_summary().model_dump(mode="json"))
                return
            self._serve_ui_file()

        def do_POST(self) -> None:
            if not self._client_allowed():
                return
            if not self._authorized():
                return
            if self.path == CAPTURE_CONTROL_START_PATH:
                payload = self._read_json()
                duration = float(payload.get("duration_seconds", 30)) if isinstance(payload, dict) else 30
                self._write_json(200, manager.start(duration_seconds=duration).model_dump(mode="json"))
                return
            if self.path == CAPTURE_CONTROL_STOP_PATH:
                self._write_json(200, manager.stop().model_dump(mode="json"))
                return
            if self.path == CAPTURE_CONTROL_SCREEN_PROBE_PATH:
                payload = self._read_json()
                allow_real_capture = bool(payload.get("allow_real_capture", False))
                receipt = screen_probe_runner(allow_real_capture)
                manager.record_bridge_receipt(_bridge_receipt_from_screen_probe(receipt))
                self._write_json(200, receipt.model_dump(mode="json"))
                return
            self._write_json(404, _error_receipt("unknown_path").model_dump(mode="json"))

        def log_message(self, _format: str, *_args: object) -> None:
            return

        def _client_allowed(self) -> bool:
            if remote_probe_status is not None:
                self._write_json(remote_probe_status, _error_receipt("client_host_not_allowed").model_dump(mode="json"))
                return False
            if client_host_allowed(self.client_address[0]):
                return True
            self._write_json(403, _error_receipt("client_host_not_allowed").model_dump(mode="json"))
            return False

        def _authorized(self) -> bool:
            if not self._origin_allowed():
                self._write_json(403, _error_receipt("origin_not_allowed").model_dump(mode="json"))
                return False
            supplied = self.headers.get("X-Cortex-Capture-Token", "")
            if not secrets.compare_digest(supplied, session_token):
                self._write_json(403, _error_receipt("missing_or_invalid_capture_token").model_dump(mode="json"))
                return False
            return True

        def _origin_allowed(self) -> bool:
            origin = self.headers.get("Origin")
            if not origin:
                return True
            allowed = {
                f"http://{self.headers.get('Host')}",
                f"http://127.0.0.1:{self.server.server_port}",
                f"http://localhost:{self.server.server_port}",
            }
            return origin in allowed

        def _serve_ui_file(self) -> None:
            route = self.path.split("?", 1)[0]
            if route in {"", "/"}:
                route = "/index.html"
            allowed = {
                "/index.html": "text/html; charset=utf-8",
                "/app.js": "text/javascript; charset=utf-8",
                "/styles.css": "text/css; charset=utf-8",
                "/dashboard-data.js": "text/javascript; charset=utf-8",
                "/capture-control-config.js": "text/javascript; charset=utf-8",
            }
            content_type = allowed.get(route)
            if content_type is None:
                self._write_json(404, _error_receipt("ui_file_not_found").model_dump(mode="json"))
                return
            path = (ui_root / route.lstrip("/")).resolve()
            if ui_root.resolve() not in path.parents and path != ui_root.resolve():
                self._write_json(403, _error_receipt("ui_path_rejected").model_dump(mode="json"))
                return
            if not path.exists():
                self._write_json(404, _error_receipt("ui_file_not_found").model_dump(mode="json"))
                return
            payload = path.read_bytes()
            self.send_response(200)
            self._write_security_headers(content_type=content_type)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def _read_json(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0") or "0")
            if length <= 0:
                return {}
            return json.loads(self.rfile.read(length).decode("utf-8"))

        def _write_json(self, status_code: int, payload: dict[str, Any]) -> None:
            body = json.dumps(payload, sort_keys=True).encode("utf-8")
            self.send_response(status_code)
            self._write_security_headers(content_type="application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _write_javascript(self, status_code: int, payload: dict[str, Any]) -> None:
            body = (
                "window.CORTEX_CAPTURE_CONTROL = "
                + json.dumps(payload, sort_keys=True)
                + ";\n"
            ).encode("utf-8")
            self.send_response(status_code)
            self._write_security_headers(content_type="text/javascript; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _write_security_headers(self, *, content_type: str) -> None:
            self.send_header("Content-Type", content_type)
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Cross-Origin-Resource-Policy", "same-origin")

    return CaptureControlHandler


def start_capture_control_server(
    *,
    host: str = DEFAULT_CAPTURE_CONTROL_HOST,
    port: int = DEFAULT_CAPTURE_CONTROL_PORT,
    manager: CaptureControlProcessManager | None = None,
    ui_root: Path = UI_ROOT,
    session_token: str | None = None,
    permission_runner: PermissionRunner = run_native_permission_smoke,
    screen_probe_runner: ScreenProbeRunner = run_native_screen_capture_probe,
) -> CaptureControlEndpoint:
    if not client_host_allowed(host):
        raise ValueError("capture control server must bind localhost")
    active_manager = manager or CaptureControlProcessManager()
    token = session_token or secrets.token_urlsafe(24)
    server = ThreadingHTTPServer(
        (host, port),
        build_capture_control_handler(
            active_manager,
            ui_root=ui_root,
            session_token=token,
            permission_runner=permission_runner,
            screen_probe_runner=screen_probe_runner,
        ),
    )
    thread = threading.Thread(target=server.serve_forever, name="cortex-capture-control-server")
    thread.daemon = True
    thread.start()
    return CaptureControlEndpoint(
        server=server,
        thread=thread,
        host=host,
        port=server.server_port,
        session_token=token,
    )


def run_capture_control_server_smoke() -> CaptureControlServerSmokeResult:
    manager = CaptureControlProcessManager(popen_factory=FakePopen)
    permission_fixture = _fixture_permission_receipt()
    screen_probe_fixture = _fixture_screen_probe_receipt()
    endpoint = start_capture_control_server(
        port=0,
        manager=manager,
        session_token="test-token",
        permission_runner=lambda: permission_fixture,
        screen_probe_runner=lambda allow_real_capture: screen_probe_fixture.model_copy(
            update={"allow_real_capture": allow_real_capture}
        ),
    )
    remote_handler = build_capture_control_handler(
        manager,
        session_token="test-token",
        permission_runner=lambda: permission_fixture,
        screen_probe_runner=lambda allow_real_capture: screen_probe_fixture.model_copy(
            update={"allow_real_capture": allow_real_capture}
        ),
        remote_probe_status=403,
    )
    headers = {"X-Cortex-Capture-Token": endpoint.session_token}
    try:
        config_code, config_body = _request_text(endpoint.base_url + CAPTURE_CONTROL_CONFIG_PATH)
        missing_token_code, _missing_token_payload = _request_json(
            endpoint.base_url + CAPTURE_CONTROL_STATUS_PATH
        )
        bad_origin_code, _bad_origin_payload = _request_json(
            endpoint.base_url + CAPTURE_CONTROL_STATUS_PATH,
            headers={
                "X-Cortex-Capture-Token": endpoint.session_token,
                "Origin": "https://example.invalid",
            },
        )
        status_code, _status = _request_json(
            endpoint.base_url + CAPTURE_CONTROL_STATUS_PATH,
            headers=headers,
        )
        dashboard_code, dashboard_body = _request_text(endpoint.base_url + "/index.html")
        permission_code, permission_payload = _request_json(
            endpoint.base_url + CAPTURE_CONTROL_PERMISSIONS_PATH,
            headers=headers,
        )
        preflight_code, preflight_payload = _request_json(
            endpoint.base_url + CAPTURE_CONTROL_PREFLIGHT_PATH,
            headers=headers,
        )
        start_code, start_payload = _request_json(
            endpoint.base_url + CAPTURE_CONTROL_START_PATH,
            method="POST",
            payload={"duration_seconds": 2},
            headers=headers,
        )
        screen_probe_code, screen_probe_payload = _request_json(
            endpoint.base_url + CAPTURE_CONTROL_SCREEN_PROBE_PATH,
            method="POST",
            payload={"allow_real_capture": True},
            headers=headers,
        )
        stop_code, stop_payload = _request_json(
            endpoint.base_url + CAPTURE_CONTROL_STOP_PATH,
            method="POST",
            payload={},
            headers=headers,
        )
        receipts_code, receipts_payload = _request_json(
            endpoint.base_url + CAPTURE_CONTROL_RECEIPTS_PATH,
            headers=headers,
        )
        remote_server = ThreadingHTTPServer(("127.0.0.1", 0), remote_handler)
        remote_thread = threading.Thread(target=remote_server.handle_request)
        remote_thread.daemon = True
        remote_thread.start()
        remote_code, _remote_payload = _request_json(
            f"http://127.0.0.1:{remote_server.server_port}{CAPTURE_CONTROL_STATUS_PATH}",
            headers=headers,
        )
        remote_thread.join(timeout=2)
        remote_server.server_close()
    finally:
        endpoint.shutdown()

    start_receipt = CaptureControlBridgeReceipt.model_validate(start_payload)
    stop_receipt = CaptureControlBridgeReceipt.model_validate(stop_payload)
    permission_receipt = NativePermissionSmokeResult.model_validate(permission_payload)
    preflight_receipt = CapturePreflightDiagnostics.model_validate(preflight_payload)
    screen_probe_receipt = NativeScreenCaptureProbeResult.model_validate(screen_probe_payload)
    receipt_summary = CaptureControlReceiptSummary.model_validate(receipts_payload)
    passed = (
        config_code == 200
        and "test-token" in config_body
        and missing_token_code == 403
        and bad_origin_code == 403
        and status_code == 200
        and dashboard_code == 200
        and "capture-control" in dashboard_body
        and permission_code == 200
        and start_code == 200
        and screen_probe_code == 200
        and stop_code == 200
        and receipts_code == 200
        and remote_code == 403
        and start_receipt.running
        and "cortex-shadow-clicker" in start_receipt.command
        and permission_receipt.passed
        and preflight_receipt.passed
        and preflight_receipt.diagnostic_id == CAPTURE_PREFLIGHT_DIAGNOSTICS_ID
        and screen_probe_receipt.passed
        and not start_receipt.capture_started
        and not start_receipt.memory_write_allowed
        and not start_receipt.raw_ref_retained
        and stop_receipt.action == "stop"
        and stop_receipt.state == "stopped"
        and receipt_summary.receipt_count >= 5
        and receipt_summary.preflight_count == 1
        and not receipt_summary.raw_pixels_returned
        and not receipt_summary.raw_ref_retained
        and not receipt_summary.memory_write_allowed
    )
    return CaptureControlServerSmokeResult(
        passed=passed,
        bind_host=endpoint.host,
        bind_port=endpoint.port,
        status_code=status_code,
        start_status_code=start_code,
        stop_status_code=stop_code,
        served_dashboard=dashboard_code == 200 and "capture-control" in dashboard_body,
        start_receipt=start_receipt,
        stop_receipt=stop_receipt,
        receipts_status_code=receipts_code,
        receipt_summary=receipt_summary,
        permission_status_code=permission_code,
        permission_receipt=permission_receipt,
        preflight_status_code=preflight_code,
        preflight_receipt=preflight_receipt,
        screen_probe_status_code=screen_probe_code,
        screen_probe_receipt=screen_probe_receipt,
        config_status_code=config_code,
        token_required=True,
        missing_token_rejected_status_code=missing_token_code,
        bad_origin_rejected_status_code=bad_origin_code,
        remote_rejected_status_code=remote_code,
    )


class FakePopen:
    pid = 4242

    def __init__(self, *_args: object, **_kwargs: object) -> None:
        self._terminated = False

    def poll(self) -> int | None:
        return 0 if self._terminated else None

    def terminate(self) -> None:
        self._terminated = True


def _error_receipt(error_code: str) -> CaptureControlBridgeReceipt:
    return CaptureControlBridgeReceipt(
        action="error",
        state="blocked",
        running=False,
        error_code=error_code,
    )


def _bridge_receipt_from_permission_result(
    receipt: NativePermissionSmokeResult,
) -> CaptureControlBridgeReceipt:
    return CaptureControlBridgeReceipt(
        action="permissions",
        state="ready" if receipt.passed else "blocked",
        running=False,
        capture_started=receipt.capture_started,
        accessibility_observer_started=receipt.accessibility_observer_started,
        memory_write_allowed=receipt.memory_write_allowed,
        raw_ref_retained=False,
        screen_recording_preflight=receipt.screen_recording_preflight,
        accessibility_trusted=receipt.accessibility_trusted,
    )


def _bridge_receipt_from_preflight(
    receipt: CapturePreflightDiagnostics,
) -> CaptureControlBridgeReceipt:
    return CaptureControlBridgeReceipt(
        action="preflight",
        state="ready" if receipt.safe_to_start_real_capture_session else "blocked",
        running=False,
        capture_started=receipt.capture_started,
        accessibility_observer_started=receipt.accessibility_observer_started,
        memory_write_allowed=receipt.memory_write_allowed,
        raw_ref_retained=receipt.raw_ref_retained,
        raw_screen_storage_enabled=False,
        screen_recording_preflight=receipt.screen_recording_preflight,
        accessibility_trusted=receipt.accessibility_trusted,
        next_user_actions=receipt.next_user_actions,
    )


def _bridge_receipt_from_screen_probe(
    receipt: NativeScreenCaptureProbeResult,
) -> CaptureControlBridgeReceipt:
    return CaptureControlBridgeReceipt(
        action="screen_probe",
        state="probed" if receipt.passed else "blocked",
        running=False,
        capture_started=receipt.capture_attempted,
        accessibility_observer_started=False,
        memory_write_allowed=receipt.memory_write_allowed,
        raw_ref_retained=receipt.raw_ref_retained,
        raw_screen_storage_enabled=False,
        screen_recording_preflight=receipt.screen_recording_preflight,
        skip_reason=receipt.skip_reason,
        next_user_actions=receipt.next_user_actions,
    )


def _fixture_permission_receipt() -> NativePermissionSmokeResult:
    return build_fixture_permission_smoke_result(
        screen_recording_preflight=True,
        accessibility_trusted=True,
        checked_at=datetime(2026, 5, 2, 19, 0, tzinfo=UTC),
    )


def _fixture_screen_probe_receipt() -> NativeScreenCaptureProbeResult:
    return build_fixture_native_screen_capture_probe_result(
        allow_real_capture=True,
        screen_recording_preflight=True,
        checked_at=datetime(2026, 5, 2, 19, 0, tzinfo=UTC),
    )


def _request_json(
    url: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[int, dict[str, Any]]:
    data = json.dumps(payload or {}).encode("utf-8") if method == "POST" else None
    request_headers = {"Content-Type": "application/json"}
    request_headers.update(headers or {})
    request = Request(url, data=data, method=method, headers=request_headers)
    try:
        with urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        return error.code, json.loads(error.read().decode("utf-8"))


def _request_text(url: str) -> tuple[int, str]:
    try:
        with urlopen(url, timeout=5) as response:
            return response.status, response.read().decode("utf-8")
    except HTTPError as error:
        return error.code, error.read().decode("utf-8")


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=DEFAULT_CAPTURE_CONTROL_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_CAPTURE_CONTROL_PORT)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.smoke:
        result = run_capture_control_server_smoke()
        if args.json:
            print(result.model_dump_json(indent=2))
        else:
            print(
                f"{CAPTURE_CONTROL_SERVER_POLICY_REF}: "
                f"passed={result.passed}; port={result.bind_port}"
            )
        return 0 if result.passed else 1

    endpoint = start_capture_control_server(host=args.host, port=args.port)
    print(f"Cortex capture control dashboard: {endpoint.base_url}/index.html")
    try:
        endpoint.thread.join()
    except KeyboardInterrupt:
        endpoint.shutdown()
    return 0
