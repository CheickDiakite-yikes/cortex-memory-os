#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-start}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
LOG_DIR="${TMPDIR:-/tmp}/cortex-native-hud-test"
BACKEND_PID_FILE="$LOG_DIR/live-tutor.pid"
BACKEND_LOG="$LOG_DIR/live-tutor.log"
APP_LOG="$HOME/Library/Logs/CortexShadowClicker/native-hud.log"
BACKEND_URL="http://127.0.0.1:8797/"
APP_NAME="cortex-shadow-clicker"
PYTHON_BIN="${CORTEX_NATIVE_HUD_PYTHON:-$ROOT_DIR/.venv/bin/python3}"
LAUNCH_LABEL="com.cortexmemoryos.live-tutor"
LAUNCH_AGENT_PLIST="$HOME/Library/LaunchAgents/$LAUNCH_LABEL.plist"

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

  if [[ ! -x "$PYTHON_BIN" ]]; then
    PYTHON_BIN="$(uv run python -c 'import sys; print(sys.executable)')"
  fi

  mkdir -p "$(dirname "$LAUNCH_AGENT_PLIST")"
  cat >"$LAUNCH_AGENT_PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$LAUNCH_LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>$PYTHON_BIN</string>
    <string>-m</string>
    <string>cortex_memory_os.live_tutor_overlay</string>
    <string>--host</string>
    <string>127.0.0.1</string>
    <string>--port</string>
    <string>8797</string>
  </array>
  <key>WorkingDirectory</key>
  <string>$ROOT_DIR</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PYTHONPATH</key>
    <string>$ROOT_DIR/src</string>
  </dict>
  <key>StandardOutPath</key>
  <string>$BACKEND_LOG</string>
  <key>StandardErrorPath</key>
  <string>$BACKEND_LOG</string>
  <key>RunAtLoad</key>
  <true/>
</dict>
</plist>
PLIST
  launchctl bootout "gui/$UID" "$LAUNCH_AGENT_PLIST" >/dev/null 2>&1 || true
  launchctl bootstrap "gui/$UID" "$LAUNCH_AGENT_PLIST"
  launchctl kickstart -k "gui/$UID/$LAUNCH_LABEL" >/dev/null 2>&1 || true
  echo "launchd" >"$BACKEND_PID_FILE"
  wait_for_backend
  echo "Backend ready at $BACKEND_URL"
}

stop_backend() {
  launchctl bootout "gui/$UID" "$LAUNCH_AGENT_PLIST" >/dev/null 2>&1 || true
  if [[ -f "$BACKEND_PID_FILE" ]]; then
    local pid
    pid="$(cat "$BACKEND_PID_FILE")"
    if [[ "$pid" =~ ^[0-9]+$ ]] && kill -0 "$pid" >/dev/null 2>&1; then
      kill "$pid" >/dev/null 2>&1 || true
      sleep 0.5
      kill -9 "$pid" >/dev/null 2>&1 || true
    fi
    rm -f "$BACKEND_PID_FILE"
  fi
  while IFS= read -r pid; do
    [[ -z "$pid" ]] && continue
    kill "$pid" >/dev/null 2>&1 || true
    sleep 0.2
    kill -9 "$pid" >/dev/null 2>&1 || true
  done < <(lsof -tiTCP:8797 -sTCP:LISTEN 2>/dev/null || true)
}

stop_app() {
  "$ROOT_DIR/script/build_and_run.sh" --stop >/dev/null 2>&1 || true
}

confirm_stopped() {
  local failed=0
  if backend_alive; then
    echo "backend: still running at $BACKEND_URL" >&2
    failed=1
  fi
  if pgrep -x "$APP_NAME" >/dev/null 2>&1; then
    echo "native HUD: still running" >&2
    failed=1
  fi
  return "$failed"
}

status() {
  if backend_alive; then
    echo "backend: running at $BACKEND_URL"
  else
    echo "backend: stopped"
  fi

  if pgrep -x "$APP_NAME" >/dev/null 2>&1; then
    echo "native HUD: running"
    if pgrep -lf "$APP_NAME" | grep -q -- "--allow-native-input-effects"; then
      echo "native input effects: enabled"
    else
      echo "native input effects: disabled"
    fi
  else
    echo "native HUD: stopped"
  fi

  echo "backend log: $BACKEND_LOG"
  echo "app log: $APP_LOG"
  local latest_connection=""
  latest_connection="$(grep -E 'connection_|realtime_connect' "$APP_LOG" 2>/dev/null | tail -1 || true)"
  if [[ -n "$latest_connection" ]]; then
    echo "latest connection: $latest_connection"
  fi
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

  stop_backend
  start_backend

  export CORTEX_SHADOW_CLICKER_DURATION="${CORTEX_SHADOW_CLICKER_DURATION:-900}"
  mkdir -p "$(dirname "$APP_LOG")"
  : >"$APP_LOG"
  "$ROOT_DIR/script/build_and_run.sh" >"$APP_LOG" 2>&1

  echo
  echo "Cortex native HUD is ready for your laptop test."
  echo
  echo "What you should see:"
  echo "  1. A blue helper cursor/ring follows your system pointer."
  echo "  2. Hold Control to talk. The blue ring should react to your voice."
  echo "  3. Release Control to send the turn."
  echo "  4. Hold Option to ask Cortex to pay attention to the thing under your pointer."
  echo "  5. Hold Shift + Option to pin the current pointer spot before asking."
  echo "  6. The app stays on for 15 minutes by default, or until you stop it."
  echo "  7. Press Control + Option + Command + Q to turn off the desktop app."
  echo "  8. For longer manual tests, explicitly set CORTEX_SHADOW_CLICKER_DURATION seconds."
  echo
  echo "Safe first phrases:"
  echo "  - \"What can you do here?\""
  echo "  - \"Show me where you would move.\""
  echo "  - \"Explain what you see near my pointer.\""
  echo
  echo "Native click/move/drag effects are off by default."
  echo "To explicitly allow them for a local test:"
  echo "  CORTEX_ENABLE_NATIVE_INPUT_EFFECTS=1 ./script/test_native_hud.sh start"
  echo
  echo "Stop everything:"
  echo "  ./script/test_native_hud.sh stop"
  echo "  or press Control + Option + Command + Q"
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
    if confirm_stopped; then
      osascript -e 'display notification "Cortex native HUD stopped" with title "Cortex"' >/dev/null 2>&1 || true
      echo "Stopped and confirmed Cortex native HUD test stack."
    else
      echo "Stop requested, but something is still alive. Run ./script/test_native_hud.sh status." >&2
      exit 1
    fi
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
