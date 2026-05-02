# Consented Real Capture Control

This slice moves Cortex toward real local capture without collapsing the safety ladder.

The goal is the user flow:

```text
Click Turn On Cortex
-> see explicit confirmation and permission readiness
-> start the native Shadow Clicker
-> observe a visible cursor-following overlay anywhere on macOS
-> only then consider screen/accessibility capture
```

The first implementation was intentionally split into ten governed slices:

| ID | Policy | Purpose | Boundary |
| --- | --- | --- | --- |
| `REAL-CAPTURE-INTENT-001` | `policy_real_capture_intent_v1` | Requires a real button action and exact confirmation text: `Turn on Cortex observation`. | No durable memory writes or external effects can be requested by intent. |
| `REAL-CAPTURE-READINESS-001` | `policy_real_capture_readiness_v1` | Combines Screen Recording, Accessibility, and native cursor overlay readiness. | Cursor overlay readiness is separate from screen-capture readiness. |
| `REAL-CAPTURE-SENSITIVE-APP-FILTER-001` | `policy_real_capture_sensitive_app_filter_v1` | Blocks sensitive app capture before any observation. | Sensitive app window titles and raw content stay unavailable. |
| `REAL-CAPTURE-SESSION-PLAN-001` | `policy_real_capture_session_plan_v1` | Produces a time-bounded session plan and native command. | Raw screen storage, memory writes, and external effects stay disabled. |
| `REAL-CAPTURE-START-RECEIPT-001` | `policy_real_capture_start_receipt_v1` | Audits the consented start path. | Starts observation only after confirmation; raw storage and memory writes stay off. |
| `REAL-CAPTURE-STOP-RECEIPT-001` | `policy_real_capture_stop_receipt_v1` | Audits the stop path. | Overlay, capture, observers, and memory influence shut down together. |
| `REAL-CAPTURE-EPHEMERAL-RAW-REF-001` | `policy_real_capture_ephemeral_raw_ref_v1` | Defines ephemeral raw refs under the system temp directory. | No durable storage and no direct memory writes from raw refs. |
| `REAL-CAPTURE-OBSERVATION-SAMPLER-001` | `policy_real_capture_observation_sampler_v1` | Starts sampling as count-only receipts. | No raw pixels, private accessibility values, or window titles by default. |
| `NATIVE-CURSOR-FOLLOW-001` | `policy_native_cursor_follow_v1` | Adds `cortex-shadow-clicker`, a native Shadow Clicker overlay that can follow the global cursor. | Uses `read_global_cursor_position`; display-only; no screen capture, Accessibility observer, click, type, export, raw ref, or memory write. |
| `DASHBOARD-CAPTURE-CONTROL-001` | `policy_dashboard_capture_control_v1` | Exposes Capture Control and Turn On Cortex state in the dashboard. | Static dashboard HTML does not claim to launch native processes directly; when served by the localhost bridge it can call fixed start/status/stop endpoints for the display-only overlay. |

The next ten slices harden the bridge and add the first metadata-only real screen probe:

| ID | Policy | Purpose | Boundary |
| --- | --- | --- | --- |
| `CAPTURE-CONTROL-TOKEN-001` | `policy_capture_control_local_bridge_v1` | Serves an ephemeral session token to the dashboard. | API calls without the token are rejected. |
| `CAPTURE-CONTROL-ORIGIN-CSRF-001` | `policy_capture_control_local_bridge_v1` | Enforces localhost-only client and `Origin` checks. | Remote clients and hostile origins are rejected. |
| `CAPTURE-CONTROL-LIFECYCLE-001` | `policy_capture_control_local_bridge_v1` | Tracks `start`, `status`, and `stop` receipts. | No arbitrary command or shell text is accepted. |
| `CAPTURE-CONTROL-PERMISSION-BRIDGE-001` | `policy_capture_control_local_bridge_v1` | Exposes prompt-free permission status through `/api/capture/permissions`. | It does not request permissions or start capture. |
| `NATIVE-SCREEN-CAPTURE-PROBE-001` | `policy_native_screen_capture_probe_v1` | Adds `cortex-screen-capture-probe` for one metadata-only in-memory frame. | Requires `--allow-real-capture`; returns dimensions only, never raw pixels. |
| `CAPTURE-CONTROL-SCREEN-PROBE-BRIDGE-001` | `policy_capture_control_local_bridge_v1` | Exposes tokenized `/api/capture/screen-probe`. | `screen-probe` is metadata-only and raw-payload-free. |
| `DASHBOARD-SCREEN-PROBE-001` | `policy_capture_control_local_bridge_v1` | Adds the dashboard `Screen Probe` button and `capture-control-config.js` token bridge. | The button shows metadata receipts only. |
| `CAPTURE-CONTROL-RECEIPT-AUDIT-001` | `policy_capture_control_local_bridge_v1` | Exposes a count-only receipt summary. | The receipt summary is raw-payload-free. |
| `RAW-REF-SCAVENGER-001` | `policy_raw_ref_scavenger_v1` | Deletes expired temp raw refs without reading payloads. | No durable storage or memory writes are enabled. |
| `REAL-CAPTURE-NEXT-GATE-001` | `policy_real_capture_next_gate_v1` | Defines the next ScreenCaptureKit gate. | Continuous capture, raw pixel return, and durable memory writes stay blocked. |

The current follow-on hardening slice adds another ten contracts before broad capture:

| ID | Policy | Purpose | Boundary |
| --- | --- | --- | --- |
| `CAPTURE-PERMISSION-GUIDE-001` | `policy_capture_permission_guide_v1` | Gives explicit Screen Recording and Accessibility setup steps for the hosting app. | The guide does not prompt, capture, write memory, or retain raw refs. |
| `CAPTURE-PREFLIGHT-DIAGNOSTICS-001` | `policy_capture_preflight_diagnostics_v1` | Reports host process, missing permissions, and safe next actions. | Prompt-free and read-only; it can block screen probing when Screen Recording preflight is false. |
| `CAPTURE-CONTROL-PREFLIGHT-BRIDGE-001` | `policy_capture_control_local_bridge_v1` | Exposes tokenized `GET /api/capture/preflight` diagnostics. | The endpoint is tokenized and cannot start capture or return raw payloads. |
| `SCREEN-PROBE-RESULT-UX-001` | `policy_screen_probe_result_ux_v1` | Turns screen-probe receipts into clear user-facing messages. | No pixels, raw refs, evidence refs, or memory writes are surfaced. |
| `SCREEN-PROBE-SKIP-RECEIPT-001` | `policy_screen_probe_skip_receipt_v1` | Records skipped probes such as `screen_recording_preflight_false`. | A skip receipt proves no frame was captured. |
| `SCREEN-PROBE-LIVE-CONTRACT-001` | `policy_screen_probe_live_contract_v1` | Defines the live no prompt behavior when Screen Recording is missing. | The probe must skip safely instead of requesting permission or capturing. |
| `CAPTURE-CONTROL-REAL-PROBE-SMOKE-001` | `policy_capture_control_real_probe_smoke_v1` | Exercises the tokenized bridge path for the metadata probe. | The tokenized bridge returns metadata only and blocks raw refs/memory writes. |
| `CAPTURE-SESSION-WATCHDOG-001` | `policy_capture_control_local_bridge_v1` | Converts exited Shadow Clicker processes into explicit watchdog receipts. | Stale overlay state cannot be reported as running. |
| `REAL-CAPTURE-PERMISSION-ONBOARDING-UI-001` | `policy_real_capture_permission_onboarding_ui_v1` | Adds a dashboard `Preflight` path that explains permission blockers before capture. | UI cannot imply real capture is ready while preflight is blocked. |
| `SCREEN-METADATA-STREAM-PLAN-001` | `policy_screen_metadata_stream_plan_v1` | Defines the future ScreenCaptureKit metadata_count_receipts stream. | Continuous capture, raw pixel return, raw ref retention, and memory_write stay blocked. |
| `CAPTURE-CONTROL-RECEIPT-AUDIT-001` | `policy_capture_control_local_bridge_v1` | Extends receipt summaries with preflight, skipped probe, and watchdog counts. | The summary remains count-only and raw-payload-free. |

## Native Shadow Clicker

`cortex-shadow-clicker` is a SwiftPM executable in `native/macos-shadow-pointer`.

Smoke:

```bash
swift run --package-path native/macos-shadow-pointer cortex-shadow-clicker --smoke --json
```

Manual display-only run:

```bash
swift run --package-path native/macos-shadow-pointer cortex-shadow-clicker --duration 30
```

The overlay uses a transparent non-activating panel and ignores mouse events. It polls the global cursor location and moves the overlay window; it does not read screen pixels or the accessibility tree.

Dashboard bridge:

```bash
uv run cortex-capture-control-server --port 8799
```

Open `http://127.0.0.1:8799/index.html`, then click `Turn On Cortex`. The bridge accepts only localhost requests and only launches the fixed `cortex-shadow-clicker` command; it does not run arbitrary shell text, start screen capture, write memory, or retain raw refs.

Use `Preflight` before `Screen Probe`. `CAPTURE-PREFLIGHT-DIAGNOSTICS-001`
reports the host process and whether `screen_recording_preflight` and
Accessibility are ready. If Screen Recording is false, `SCREEN-PROBE-SKIP-RECEIPT-001`
records `screen_recording_preflight_false` and no frame is captured.

## Native Screen Probe

`cortex-screen-capture-probe` is the first real-capture-adjacent executable.

Preflight-only smoke:

```bash
swift run --package-path native/macos-shadow-pointer cortex-screen-capture-probe --json
```

Explicit metadata-only probe:

```bash
swift run --package-path native/macos-shadow-pointer cortex-screen-capture-probe --allow-real-capture --json
```

The probe uses `CGPreflightScreenCaptureAccess` first. If Screen Recording is not preflight-ready, it returns a skipped receipt. If it is ready and `--allow-real-capture` is present, it may capture one frame in memory and return dimensions only. It never returns raw pixels, writes memory, stores raw refs, starts continuous capture, or reads Accessibility values.

## Default Safety State

Real capture now has a stronger path, but defaults stay conservative:

- `REAL-CAPTURE-INTENT-001` requires explicit confirmation.
- `REAL-CAPTURE-READINESS-001` can report that cursor overlay is ready even when Screen Recording or Accessibility is missing; the explicit receipt field is `missing_permissions`.
- `REAL-CAPTURE-SENSITIVE-APP-FILTER-001` blocks private/sensitive apps before capture.
- `REAL-CAPTURE-EPHEMERAL-RAW-REF-001` keeps raw refs temporary.
- `REAL-CAPTURE-OBSERVATION-SAMPLER-001` begins with count-only receipts and prompt-injection screening.

The next step after this is ScreenCaptureKit under the same tokenized receipt/audit boundary, still starting with metadata-only checks before any raw evidence or durable memory path.
