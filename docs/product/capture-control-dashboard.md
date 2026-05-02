# Capture Control Dashboard

`DASHBOARD-CAPTURE-CONTROL-001` adds a calm Capture Control panel to the local dashboard.

It is designed for the user goal:

```text
Turn On Cortex -> visible native Shadow Clicker -> consented capture readiness
```

The panel shows:

- `Turn On Cortex` as the primary control label.
- Native Shadow Clicker status.
- Screen Recording and Accessibility readiness.
- Missing permission names from `REAL-CAPTURE-READINESS-001`.
- The command for the native Shadow Clicker: `cortex-shadow-clicker`.

The dashboard uses `policy_dashboard_capture_control_v1`.

## Honest Button Boundary

Static HTML cannot safely launch a native process by itself, and the UI must not pretend otherwise.

When served by the localhost bridge, the panel calls fixed local endpoints:

```text
GET /api/capture/status
POST /api/capture/start
POST /api/capture/stop
```

The bridge command is:

```bash
uv run cortex-capture-control-server --port 8799
```

Then open:

```text
http://127.0.0.1:8799/index.html
```

The bridge can launch only the fixed native Shadow Clicker command:

```bash
swift run --package-path native/macos-shadow-pointer cortex-shadow-clicker --duration 30
```

When opened as static `file://` HTML, the same panel emits a local receipt that names the native command. In both modes:

- no raw payload is returned;
- no arbitrary command is accepted;
- no shell command is interpreted;
- no screen capture starts;
- no durable memory write is allowed;
- no raw ref is retained;
- no external effect is possible beyond showing and stopping the display-only overlay.

## Product Behavior

The panel should stay visually quieter than the old crowded dashboard. It belongs in Overview, Agent Gateway, and Policies because it is both a user-facing start path and a governance surface.

Clicking the panel buttons updates the local interaction receipt:

- `Turn On Cortex` starts the localhost bridge path when available, otherwise it explains the CLI fallback.
- `cortex-shadow-clicker` shows the native command and reminds that it follows the system cursor without capture.
- `Stop Observation` shows the stop receipt state.

This is the bridge from synthetic demos to a real system-wide Shadow Clicker without enabling broad screen memory prematurely.
