# Native macOS Shadow Pointer Proof

`SHADOW-POINTER-NATIVE-001` is the first SwiftPM proof for the Cortex Shadow
Pointer overlay. It is intentionally package-first: it proves the native window
boundary, view model, and control receipts without installing a real app or
requesting capture permissions.

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

## Commands

```bash
swift build --package-path native/macos-shadow-pointer
swift test --package-path native/macos-shadow-pointer
swift run --package-path native/macos-shadow-pointer cortex-shadow-pointer-smoke
```

This package does not start screen capture, create a persistent agent, or write
private memory.
