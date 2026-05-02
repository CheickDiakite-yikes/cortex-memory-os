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
GET /api/capture/preflight
GET /api/capture/receipts
POST /api/capture/start
POST /api/capture/screen-probe
POST /api/capture/stop
```

`CAPTURE-CONTROL-TOKEN-001` requires the dashboard to load a session token from
`capture-control-config.js`. `CAPTURE-CONTROL-ORIGIN-CSRF-001` rejects bad
`Origin` headers and non-local clients. `CAPTURE-CONTROL-LIFECYCLE-001` keeps
the `start`, `status`, and `stop` path explicit.
`CAPTURE-CONTROL-PREFLIGHT-BRIDGE-001` exposes tokenized
`GET /api/capture/preflight` diagnostics before screen probing.

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
- `skip_reason` when no frame was captured, such as `screen_recording_preflight_false`;
- next user actions when permission is blocking the probe;
- frame dimensions if available;
- `raw_pixels_returned: false`;
- `raw_ref_retained: false`;
- `memory_write_allowed: false`.

`CAPTURE-CONTROL-PERMISSION-BRIDGE-001` powers `Check Permissions` without
prompting. `CAPTURE-PERMISSION-GUIDE-001` and
`CAPTURE-PREFLIGHT-DIAGNOSTICS-001` power the dashboard `Preflight` button,
which explains the current host process, missing permissions, and whether a
metadata probe or real session is safe. `SCREEN-PROBE-RESULT-UX-001` makes a
blocked probe readable instead of cryptic. `SCREEN-PROBE-SKIP-RECEIPT-001`
records skipped probes and proves no frame was captured.

`CAPTURE-CONTROL-REAL-PROBE-SMOKE-001` covers the tokenized bridge path for the
metadata probe. `CAPTURE-SESSION-WATCHDOG-001` makes exited overlay processes
visible as `exited` instead of stale `running`. `CAPTURE-CONTROL-RECEIPT-AUDIT-001`
powers count-only, raw-payload-free receipt summary text, now including
preflight, skipped probe, and watchdog counts. `RAW-REF-SCAVENGER-001` and
`REAL-CAPTURE-NEXT-GATE-001` define the cleanup and ScreenCaptureKit gate before
broader capture.

`REAL-CAPTURE-PERMISSION-ONBOARDING-UI-001` requires the UI to show the
Preflight path before any broader capture claim. `SCREEN-METADATA-STREAM-PLAN-001`
defines the next metadata_count_receipts stream while continuous capture,
raw pixels, raw refs, and memory writes remain blocked.

## Product Behavior

The panel should stay visually quieter than the old crowded dashboard. It belongs in Overview, Agent Gateway, and Policies because it is both a user-facing start path and a governance surface.

Clicking the panel buttons updates the local interaction receipt:

- `Turn On Cortex` starts the localhost bridge path when available, otherwise it explains the CLI fallback.
- `cortex-shadow-clicker` shows the native command and reminds that it follows the system cursor without capture.
- `Check Permissions` shows prompt-free Screen Recording and Accessibility readiness.
- `Preflight` explains missing permissions and whether screen probe or real session is blocked.
- `Screen Probe` runs the metadata-only real capture probe when the bridge is active.
- `Receipts` shows the count-only local receipt summary.
- `Stop Observation` shows the stop receipt state.

This is the bridge from synthetic demos to a real system-wide Shadow Clicker without enabling broad screen memory prematurely.
