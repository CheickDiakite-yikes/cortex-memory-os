# Shadow Pointer Controls

Last updated: 2026-04-29

`SHADOW-POINTER-CONTROLS-001` defines the native-ready control contract for the
Shadow Pointer overlay.

The Shadow Pointer is trust infrastructure. It must expose the current
observation state and let the user stop, narrow, inspect, or delete observation
without relying on hidden agent behavior.

## Control Commands

| Command | Required input | Confirmation | Result |
| --- | --- | --- | --- |
| `status` | none | No | Returns the current snapshot without mutation. |
| `pause_observation` | `duration_minutes` | No | Switches to `paused`, disables observation, and blocks memory writes until resume or timeout. |
| `resume_observation` | none | No | Restores observation within the current consent scope. |
| `delete_recent` | `delete_window_minutes` | Yes | Marks the chosen window for deletion/tombstoning and blocks memory writes until deletion completes. |
| `ignore_app` | `app_name` | Yes | Removes the app from visible capture scope and blocks memory writes from that app. |

## Receipt Contract

Every command returns a `ShadowPointerControlReceipt` with:

- resulting snapshot;
- observation-active flag;
- memory-write-allowed flag;
- audit requirement and audit action;
- confirmation state;
- affected apps or delete window when relevant;
- safety notes for the native overlay and Memory Palace.

Status is read-only and does not require an audit. Pause, resume, delete-recent,
and app-ignore require audit receipts because they change consent or observation
scope.

## Native Overlay Expectations

The first native overlay should wire these commands directly:

- a pause control with visible timeout;
- a resume/status control;
- a delete-recent control with an explicit confirmation step;
- an app-ignore control anchored to the currently observed app;
- a visible receipt/status row after every control action.

Native capture adapters must obey the receipt. If `observation_active` is false,
capture stops. If `memory_write_allowed` is false, scene segmentation and memory
compilation must not promote new memory from the affected scope.

## Benchmark Contract

`SHADOW-POINTER-CONTROLS-001` verifies that:

- pause blocks observation and memory writes;
- delete-recent requires confirmation and produces deletion audit metadata;
- app-ignore requires confirmation, removes the app from visible capture, and
  blocks memory writes from that app;
- status is read-only;
- the static prototype exposes the controls and a receipt/status area.
