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

The implementation is intentionally split into ten governed slices:

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

## Default Safety State

Real capture now has a stronger path, but defaults stay conservative:

- `REAL-CAPTURE-INTENT-001` requires explicit confirmation.
- `REAL-CAPTURE-READINESS-001` can report that cursor overlay is ready even when Screen Recording or Accessibility is missing; the explicit receipt field is `missing_permissions`.
- `REAL-CAPTURE-SENSITIVE-APP-FILTER-001` blocks private/sensitive apps before capture.
- `REAL-CAPTURE-EPHEMERAL-RAW-REF-001` keeps raw refs temporary.
- `REAL-CAPTURE-OBSERVATION-SAMPLER-001` begins with count-only receipts and prompt-injection screening.

The next step after this is a session-token challenge around the localhost controller and then, only later, ScreenCaptureKit under the same receipt/audit boundary.
