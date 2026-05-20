#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-start}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
LOG_DIR="${TMPDIR:-/tmp}/cortex-native-hud-test"
BACKEND_PID_FILE="$LOG_DIR/live-tutor.pid"
BACKEND_LOG="$LOG_DIR/live-tutor.log"
APP_LOG="$LOG_DIR/native-hud.log"
BACKEND_URL="http://127.0.0.1:8797/"
APP_NAME="cortex-shadow-clicker"

usage() {
  cat >&2 <<USAGE
usage: $0 [start|stop|status|logs|permissions]

start       Start localhost token server and launch the native HUD app.
stop        Stop the native HUD app and the token server started by this script.
status      Show whether the backend and native HUD process are alive.
logs        Tail the local backend/app logs.
permissions Open macOS Privacy settings panes needed for testing.
USAGE
}

api_key_ready() {
  if [[ -n "${OPENAI_API_KEY:-}" ]]; then
    return 0
  fi
  python - <<'PY'
from pathlib import Path
env_path = Path(".env.local")
if not env_path.exists():
    raise SystemExit(1)
for line in env_path.read_text(encoding="utf-8").splitlines():
    stripped = line.strip()
    if stripped.startswith("OPENAI_API_KEY=") and stripped.split("=", 1)[1].strip():
        raise SystemExit(0)
raise SystemExit(1)
PY
}

backend_alive() {
  python - <<'PY'
import sys
import urllib.request

try:
    with urllib.request.urlopen("http://127.0.0.1:8797/", timeout=1) as response:
        raise SystemExit(0 if response.status == 200 else 1)
except Exception:
    raise SystemExit(1)
PY
}

wait_for_backend() {
  python - <<'PY'
import time
import urllib.request

deadline = time.time() + 20
last_error = ""
while time.time() < deadline:
    try:
        with urllib.request.urlopen("http://127.0.0.1:8797/", timeout=1) as response:
            if response.status == 200:
                raise SystemExit(0)
    except Exception as exc:
        last_error = str(exc)
    time.sleep(0.35)
print(f"backend did not become ready: {last_error}", flush=True)
raise SystemExit(1)
PY
}

start_backend() {
  mkdir -p "$LOG_DIR"
  if backend_alive; then
    echo "Backend already responding at $BACKEND_URL"
    return
  fi

  nohup uv run cortex-live-tutor-demo --host 127.0.0.1 --port 8797 \
    >"$BACKEND_LOG" 2>&1 &
  echo "$!" >"$BACKEND_PID_FILE"
  wait_for_backend
  echo "Backend ready at $BACKEND_URL"
}

stop_backend() {
  if [[ -f "$BACKEND_PID_FILE" ]]; then
    local pid
    pid="$(cat "$BACKEND_PID_FILE")"
    if [[ -n "$pid" ]] && kill -0 "$pid" >/dev/null 2>&1; then
      kill "$pid" >/dev/null 2>&1 || true
      sleep 0.5
      kill -9 "$pid" >/dev/null 2>&1 || true
    fi
    rm -f "$BACKEND_PID_FILE"
  fi
}

stop_app() {
  "$ROOT_DIR/script/build_and_run.sh" --stop >/dev/null 2>&1 || true
}

status() {
  if backend_alive; then
    echo "backend: running at $BACKEND_URL"
  else
    echo "backend: stopped"
  fi

  if pgrep -x "$APP_NAME" >/dev/null 2>&1; then
    echo "native HUD: running"
  else
    echo "native HUD: stopped"
  fi

  echo "logs: $LOG_DIR"
}

open_permissions() {
  echo "Opening macOS Privacy panes. Enable Microphone and Accessibility for the app/Codex host if prompted."
  open "x-apple.systempreferences:com.apple.preference.security?Privacy_Microphone" || true
  open "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility" || true
}

start_stack() {
  if ! api_key_ready; then
    cat >&2 <<'MESSAGE'
OPENAI_API_KEY is not available.

Add it to .env.local or export it in your shell. The script only checks that it
exists; it never prints the key.
MESSAGE
    exit 1
  fi

  start_backend

  export CORTEX_SHADOW_CLICKER_DURATION="${CORTEX_SHADOW_CLICKER_DURATION:-900}"
  "$ROOT_DIR/script/build_and_run.sh" >"$APP_LOG" 2>&1

  echo
  echo "Cortex native HUD is ready for your laptop test."
  echo
  echo "What you should see:"
  echo "  1. A blue helper cursor/ring follows your system pointer."
  echo "  2. Hold Control to talk. The blue ring should react to your voice."
  echo "  3. Release Control to send the turn."
  echo
  echo "Safe first phrases:"
  echo "  - \"Move the mouse to the center of the screen.\""
  echo "  - \"Scroll down a little.\""
  echo "  - \"Right click here.\""
  echo
  echo "Stop everything:"
  echo "  ./script/test_native_hud.sh stop"
  echo
  echo "Logs:"
  echo "  tail -f $BACKEND_LOG $APP_LOG"
}

case "$MODE" in
  start)
    start_stack
    ;;
  stop)
    stop_app
    stop_backend
    echo "Stopped Cortex native HUD test stack."
    ;;
  status)
    status
    ;;
  logs)
    mkdir -p "$LOG_DIR"
    touch "$BACKEND_LOG" "$APP_LOG"
    tail -f "$BACKEND_LOG" "$APP_LOG"
    ;;
  permissions)
    open_permissions
    ;;
  *)
    usage
    exit 2
    ;;
esac
