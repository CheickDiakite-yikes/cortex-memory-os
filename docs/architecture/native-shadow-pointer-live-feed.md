# Native Shadow Pointer Live Feed

Benchmark: `NATIVE-SHADOW-POINTER-LIVE-FEED-001`

Policy: `policy_native_shadow_pointer_live_feed_v1`

This contract feeds redacted `ShadowPointerLiveReceipt` objects into the native
macOS Shadow Pointer overlay without starting capture or creating input
authority.

## Allowed Effects

- `render_native_overlay_frame`
- `render_redacted_receipt_summary`

## Blocked Effects

- `start_screen_capture`
- `start_accessibility_observer`
- `write_memory`
- `retain_raw_ref`
- `execute_click`
- `type_text`
- `export_payload`

## Product Rule

The native overlay is a display-only trust surface. It can show the latest
state, observation mode, external-untrusted count, memory-eligible count, and
raw-ref status. It cannot become a capture daemon, a click executor, or a memory
writer.
