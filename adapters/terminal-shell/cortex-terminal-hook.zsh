# Cortex Memory OS terminal adapter hook.
#
# Source manually only after review:
#   export CORTEX_TERMINAL_OBSERVER=1
#   source adapters/terminal-shell/cortex-terminal-hook.zsh
#
# The hook is disabled by default, posts only to localhost endpoints, redacts
# secret-like command text before emission, and never writes raw terminal logs.

: "${CORTEX_TERMINAL_ENDPOINT:=http://127.0.0.1:8765/adapter/terminal}"
typeset -g CORTEX_TERMINAL_LAST_COMMAND=""

cortex_terminal_endpoint_allowed() {
  case "${CORTEX_TERMINAL_ENDPOINT}" in
    http://127.0.0.1:*|http://localhost:*) return 0 ;;
    *) return 1 ;;
  esac
}

cortex_terminal_redact() {
  sed -E \
    -e 's/(OPENAI_API_KEY|ANTHROPIC_API_KEY|GOOGLE_API_KEY)=([^[:space:]]+)/\1=[REDACTED_SECRET]/g' \
    -e 's/(token|password|api_key)=([^[:space:]]+)/\1=[REDACTED_SECRET]/g' \
    -e 's/sk-[A-Za-z0-9_-]{20,}/[REDACTED_SECRET]/g'
}

cortex_terminal_emit_event() {
  local command_text="$1"
  local exit_code="$2"

  [[ "${CORTEX_TERMINAL_OBSERVER:-0}" == "1" ]] || return 0
  cortex_terminal_endpoint_allowed || return 0
  command_text="$(print -r -- "${command_text}" | cortex_terminal_redact)"

  local event_id="terminal_command_${EPOCHSECONDS}_${RANDOM}"
  local observed_at
  observed_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

  CORTEX_TERMINAL_EVENT_ID="${event_id}" \
  CORTEX_TERMINAL_OBSERVED_AT="${observed_at}" \
  CORTEX_TERMINAL_COMMAND_TEXT="${command_text}" \
  CORTEX_TERMINAL_EXIT_CODE="${exit_code}" \
  CORTEX_TERMINAL_CWD="${PWD}" \
  CORTEX_TERMINAL_SHELL="${SHELL:-zsh}" \
  python3 - <<'PY' | curl -fsS --max-time 1 \
    -H 'Content-Type: application/json' \
    --data-binary @- \
    "${CORTEX_TERMINAL_ENDPOINT}" >/dev/null 2>&1 || true
import json
import os
import socket

event_id = os.environ["CORTEX_TERMINAL_EVENT_ID"]
exit_code_text = os.environ.get("CORTEX_TERMINAL_EXIT_CODE")
payload = {
    "event_id": event_id,
    "event_type": "terminal_command",
    "observed_at": os.environ["CORTEX_TERMINAL_OBSERVED_AT"],
    "device": socket.gethostname(),
    "app": os.environ.get("TERM_PROGRAM", "Terminal"),
    "window_title": os.environ.get("CORTEX_PROJECT_ID") or os.path.basename(os.getcwd()),
    "project_id": os.environ.get("CORTEX_PROJECT_ID"),
    "command_text": os.environ["CORTEX_TERMINAL_COMMAND_TEXT"],
    "cwd": os.environ.get("CORTEX_TERMINAL_CWD"),
    "shell": os.environ.get("CORTEX_TERMINAL_SHELL", "zsh"),
    "exit_code": int(exit_code_text) if exit_code_text else None,
    "capture_scope": "project_specific",
    "consent_state": "active",
    "raw_ref": None,
    "derived_text_ref": f"derived://terminal/live/{event_id}",
}
print(json.dumps(payload, separators=(",", ":")))
PY
}

cortex_terminal_preexec() {
  CORTEX_TERMINAL_LAST_COMMAND="$1"
}

cortex_terminal_precmd() {
  local last_exit_code="$?"
  if [[ -n "${CORTEX_TERMINAL_LAST_COMMAND}" ]]; then
    cortex_terminal_emit_event "${CORTEX_TERMINAL_LAST_COMMAND}" "${last_exit_code}"
    CORTEX_TERMINAL_LAST_COMMAND=""
  fi
}

if [[ "${CORTEX_TERMINAL_OBSERVER:-0}" == "1" ]]; then
  autoload -Uz add-zsh-hook
  add-zsh-hook preexec cortex_terminal_preexec
  add-zsh-hook precmd cortex_terminal_precmd
fi
