# Native macOS Shadow Pointer Proof

`SHADOW-POINTER-NATIVE-001` is the first SwiftPM proof for the Cortex Shadow
Pointer overlay. It is intentionally package-first: it proves the native window
boundary, view model, and control receipts without installing a real app or
requesting capture permissions.

`NATIVE-CAPTURE-PERMISSION-SMOKE-001` adds a read-only permission-status
executable, `cortex-permission-smoke`, governed by
`policy_native_capture_permission_smoke_v1`. It calls
`CGPreflightScreenCaptureAccess` and `AXIsProcessTrustedWithOptions` with
`kAXTrustedCheckOptionPrompt` set to false, then reports status without opening
permission prompts.

## What It Proves

- The overlay window boundary is a transparent, non-activating, borderless
  `NSPanel`.
- The panel is configured for floating visibility across Spaces and full-screen
  contexts.
- Mouse events are ignored by default, so model-proposed coordinates cannot
  become clicks.
- Pause, delete-recent, and ignore-app controls produce native receipts that
  block memory writes.
- Pointing proposals remain display-only and require separate confirmation for
  any action outside the overlay.
- Permission status can be read without `promptRequested`, `captureStarted`,
  `accessibilityObserverStarted`, `memoryWriteAllowed`, raw evidence, or
  observer side effects.

## Permission Smoke Safety

The only allowed effect is `read_permission_status`. The smoke blocks
`request_screen_recording_permission`, `request_accessibility_permission`,
`start_screen_capture`, `start_accessibility_observer`, `write_memory`, and
`store_raw_evidence`.

## Commands

```bash
swift build --package-path native/macos-shadow-pointer
swift test --package-path native/macos-shadow-pointer
swift run --package-path native/macos-shadow-pointer cortex-shadow-pointer-smoke
swift run --package-path native/macos-shadow-pointer cortex-permission-smoke
uv run cortex-native-permission-smoke --json
```

This package does not start screen capture, create a persistent agent, or write
private memory.
