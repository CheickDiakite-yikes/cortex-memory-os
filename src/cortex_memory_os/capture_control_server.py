"""Localhost-only bridge for launching the native Shadow Clicker from the dashboard."""

from __future__ import annotations

import argparse
import json
import subprocess
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
UI_ROOT = REPO_ROOT / "ui" / "cortex-dashboard"


class ManagedProcess(Protocol):
    pid: int

    def poll(self) -> int | None: ...

    def terminate(self) -> None: ...


PopenFactory = Callable[..., ManagedProcess]


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
    localhost_only: bool = True
    fixed_command_only: bool = True
    capture_started: bool = False
    accessibility_observer_started: bool = False
    memory_write_allowed: bool = False
    raw_ref_retained: bool = False
    raw_screen_storage_enabled: bool = False
    error_code: str | None = None


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

    def status(self) -> CaptureControlBridgeReceipt:
        running = self._is_running()
        return CaptureControlBridgeReceipt(
            action="status",
            state="running" if running else "stopped",
            running=running,
            pid=self._process.pid if running and self._process else None,
            command=self._command if running else [],
            duration_seconds=self._duration_seconds if running else None,
            started_at=self._started_at if running else None,
            stopped_at=None if running else self._stopped_at,
        )

    def start(self, *, duration_seconds: float = 30) -> CaptureControlBridgeReceipt:
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
        return CaptureControlBridgeReceipt(
            action="start",
            state="running",
            running=True,
            pid=process.pid,
            command=command,
            duration_seconds=bounded_duration,
            started_at=self._started_at,
        )

    def stop(self) -> CaptureControlBridgeReceipt:
        if self._is_running() and self._process is not None:
            self._process.terminate()
        self._stopped_at = self.now()
        self._process = None
        self._duration_seconds = None
        self._command = []
        return CaptureControlBridgeReceipt(
            action="stop",
            state="stopped",
            running=False,
            stopped_at=self._stopped_at,
        )

    def _is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None


@dataclass(frozen=True)
class CaptureControlEndpoint:
    server: ThreadingHTTPServer
    thread: threading.Thread
    host: str
    port: int

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
    remote_probe_status: int | None = None,
) -> type[BaseHTTPRequestHandler]:
    class CaptureControlHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            if not self._client_allowed():
                return
            if self.path == CAPTURE_CONTROL_STATUS_PATH:
                self._write_json(200, manager.status().model_dump(mode="json"))
                return
            self._serve_ui_file()

        def do_POST(self) -> None:
            if not self._client_allowed():
                return
            if self.path == CAPTURE_CONTROL_START_PATH:
                payload = self._read_json()
                duration = float(payload.get("duration_seconds", 30)) if isinstance(payload, dict) else 30
                self._write_json(200, manager.start(duration_seconds=duration).model_dump(mode="json"))
                return
            if self.path == CAPTURE_CONTROL_STOP_PATH:
                self._write_json(200, manager.stop().model_dump(mode="json"))
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

        def _serve_ui_file(self) -> None:
            route = self.path.split("?", 1)[0]
            if route in {"", "/"}:
                route = "/index.html"
            allowed = {
                "/index.html": "text/html; charset=utf-8",
                "/app.js": "text/javascript; charset=utf-8",
                "/styles.css": "text/css; charset=utf-8",
                "/dashboard-data.js": "text/javascript; charset=utf-8",
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
            self.send_header("Content-Type", content_type)
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
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return CaptureControlHandler


def start_capture_control_server(
    *,
    host: str = DEFAULT_CAPTURE_CONTROL_HOST,
    port: int = DEFAULT_CAPTURE_CONTROL_PORT,
    manager: CaptureControlProcessManager | None = None,
    ui_root: Path = UI_ROOT,
) -> CaptureControlEndpoint:
    if not client_host_allowed(host):
        raise ValueError("capture control server must bind localhost")
    active_manager = manager or CaptureControlProcessManager()
    server = ThreadingHTTPServer(
        (host, port),
        build_capture_control_handler(active_manager, ui_root=ui_root),
    )
    thread = threading.Thread(target=server.serve_forever, name="cortex-capture-control-server")
    thread.daemon = True
    thread.start()
    return CaptureControlEndpoint(server=server, thread=thread, host=host, port=server.server_port)


def run_capture_control_server_smoke() -> CaptureControlServerSmokeResult:
    manager = CaptureControlProcessManager(popen_factory=FakePopen)
    endpoint = start_capture_control_server(port=0, manager=manager)
    remote_handler = build_capture_control_handler(manager, remote_probe_status=403)
    try:
        status_code, _status = _request_json(endpoint.base_url + CAPTURE_CONTROL_STATUS_PATH)
        dashboard_code, dashboard_body = _request_text(endpoint.base_url + "/index.html")
        start_code, start_payload = _request_json(
            endpoint.base_url + CAPTURE_CONTROL_START_PATH,
            method="POST",
            payload={"duration_seconds": 2},
        )
        stop_code, stop_payload = _request_json(
            endpoint.base_url + CAPTURE_CONTROL_STOP_PATH,
            method="POST",
            payload={},
        )
        remote_server = ThreadingHTTPServer(("127.0.0.1", 0), remote_handler)
        remote_thread = threading.Thread(target=remote_server.handle_request)
        remote_thread.daemon = True
        remote_thread.start()
        remote_code, _remote_payload = _request_json(
            f"http://127.0.0.1:{remote_server.server_port}{CAPTURE_CONTROL_STATUS_PATH}"
        )
        remote_thread.join(timeout=2)
        remote_server.server_close()
    finally:
        endpoint.shutdown()

    start_receipt = CaptureControlBridgeReceipt.model_validate(start_payload)
    stop_receipt = CaptureControlBridgeReceipt.model_validate(stop_payload)
    passed = (
        status_code == 200
        and dashboard_code == 200
        and "capture-control" in dashboard_body
        and start_code == 200
        and stop_code == 200
        and remote_code == 403
        and start_receipt.running
        and "cortex-shadow-clicker" in start_receipt.command
        and not start_receipt.capture_started
        and not start_receipt.memory_write_allowed
        and not start_receipt.raw_ref_retained
        and stop_receipt.action == "stop"
        and stop_receipt.state == "stopped"
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


def _request_json(
    url: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
) -> tuple[int, dict[str, Any]]:
    data = json.dumps(payload or {}).encode("utf-8") if method == "POST" else None
    request = Request(url, data=data, method=method, headers={"Content-Type": "application/json"})
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
