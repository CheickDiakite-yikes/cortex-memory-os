# Native Shadow Pointer Overlay

Last updated: 2026-04-29

`SHADOW-POINTER-NATIVE-001` is the first native macOS proof for the Shadow
Pointer. It converts the existing Python state, control, and pointing contracts
into a SwiftPM package that can be built and tested without installing an app or
requesting screen-capture permissions.

## Native Boundary

The proof lives in `native/macos-shadow-pointer`, is rooted at
`native/macos-shadow-pointer/Package.swift`, and defines
`policy_shadow_pointer_native_overlay_v1`.

The native overlay boundary is:

- a transparent `NSPanel`;
- `.nonactivatingPanel` and `.borderless`;
- `.floating` window level;
- `.canJoinAllSpaces`, `.fullScreenAuxiliary`, and `.stationary` collection
  behavior;
- `ignoresMouseEvents = true` by default;
- `canBecomeKey = false` and `canBecomeMain = false`.

This gives Cortex a visible cursor-adjacent trust surface without creating a
hidden action channel. The first native panel may display a halo, state label,
receipt row, and highlight, but it must not synthesize clicks, type text, open
URLs, or call tools.

## Control Bridge

The Swift control bridge mirrors the existing `ShadowPointerControlReceipt`
semantics:

- `pause_observation` disables observation and blocks memory writes;
- `delete_recent` requires explicit confirmation and blocks memory writes until
  deletion/tombstoning completes;
- `ignore_app` requires explicit confirmation, removes the app from visible
  scope, and blocks memory writes from that app;
- `status` is read-only.

The bridge is intentionally separate from capture adapters. A receipt can tell
future capture and memory layers what must stop or be blocked, but the overlay
does not directly observe, remember, or delete evidence by itself.

## Verification

```bash
swift build --package-path native/macos-shadow-pointer
swift test --package-path native/macos-shadow-pointer
swift run --package-path native/macos-shadow-pointer cortex-shadow-pointer-smoke
```

`SHADOW-POINTER-NATIVE-001` benchmarks the package source and docs, while the
Swift tests exercise the native control bridge and overlay window specification.

`NATIVE-CAPTURE-PERMISSION-SMOKE-001` reuses the same SwiftPM package for a
separate read-only permission-status executable:

```bash
swift run --package-path native/macos-shadow-pointer cortex-permission-smoke
uv run cortex-native-permission-smoke --json
```

That smoke checks `CGPreflightScreenCaptureAccess` and
`AXIsProcessTrustedWithOptions` with `kAXTrustedCheckOptionPrompt` set to false.
It reports permission status without prompting, starting capture, starting
Accessibility observers, writing memory, or emitting evidence refs.
