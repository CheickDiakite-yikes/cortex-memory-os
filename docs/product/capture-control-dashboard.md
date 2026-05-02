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
GET /capture-control-config.js
GET /api/capture/status
GET /api/capture/permissions
GET /api/capture/receipts
POST /api/capture/start
POST /api/capture/screen-probe
POST /api/capture/stop
```

`CAPTURE-CONTROL-TOKEN-001` requires the dashboard to load a session token from
`capture-control-config.js`. `CAPTURE-CONTROL-ORIGIN-CSRF-001` rejects bad
`Origin` headers and non-local clients. `CAPTURE-CONTROL-LIFECYCLE-001` keeps
the `start`, `status`, and `stop` path explicit.

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

## Screen Probe

`DASHBOARD-SCREEN-PROBE-001` adds a `Screen Probe` button. Through
`CAPTURE-CONTROL-SCREEN-PROBE-BRIDGE-001`, it calls the tokenized
`screen-probe` endpoint and can run `cortex-screen-capture-probe` in
metadata-only mode.

The probe receipt reports:

- whether capture was attempted;
- whether one frame was captured;
- frame dimensions if available;
- `raw_pixels_returned: false`;
- `raw_ref_retained: false`;
- `memory_write_allowed: false`.

`CAPTURE-CONTROL-PERMISSION-BRIDGE-001` powers `Check Permissions` without
prompting. `CAPTURE-CONTROL-RECEIPT-AUDIT-001` powers count-only,
raw-payload-free receipt summary text. `RAW-REF-SCAVENGER-001` and
`REAL-CAPTURE-NEXT-GATE-001` define the cleanup and ScreenCaptureKit gate before
broader capture.

## Product Behavior

The panel should stay visually quieter than the old crowded dashboard. It belongs in Overview, Agent Gateway, and Policies because it is both a user-facing start path and a governance surface.

Clicking the panel buttons updates the local interaction receipt:

- `Turn On Cortex` starts the localhost bridge path when available, otherwise it explains the CLI fallback.
- `cortex-shadow-clicker` shows the native command and reminds that it follows the system cursor without capture.
- `Check Permissions` shows prompt-free Screen Recording and Accessibility readiness.
- `Screen Probe` runs the metadata-only real capture probe when the bridge is active.
- `Receipts` shows the count-only local receipt summary.
- `Stop Observation` shows the stop receipt state.

This is the bridge from synthetic demos to a real system-wide Shadow Clicker without enabling broad screen memory prematurely.
