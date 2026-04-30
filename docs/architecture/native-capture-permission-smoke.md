# Native Capture Permission Smoke

Last updated: 2026-04-30

`NATIVE-CAPTURE-PERMISSION-SMOKE-001` is the first native permission-status
smoke for Cortex capture. It is intentionally read-only: it reports whether the
current process already has macOS Screen Recording and Accessibility trust, but
it does not request permissions, start capture, start Accessibility observers,
write memory, or store evidence.

## Boundary

The SwiftPM executable lives at `native/macos-shadow-pointer` and is exposed as
`cortex-permission-smoke`.

The smoke uses:

- `CGPreflightScreenCaptureAccess` for Screen Recording status;
- `AXIsProcessTrustedWithOptions` with `kAXTrustedCheckOptionPrompt` set to
  `false` for Accessibility status;
- `policy_native_capture_permission_smoke_v1` as the governing policy ref;
- `NATIVE-CAPTURE-PERMISSION-SMOKE-001` as the benchmark suite ID.

The only allowed effect is:

```text
read_permission_status
```

The blocked effects are:

```text
request_screen_recording_permission
request_accessibility_permission
start_screen_capture
start_accessibility_observer
write_memory
store_raw_evidence
```

## Receipt Contract

The native smoke JSON includes:

- `prompt_requested: false`;
- `capture_started: false`;
- `accessibility_observer_started: false`;
- `memory_write_allowed: false`;
- `evidence_refs: []`;
- `allowed_effects: ["read_permission_status"]`;
- blocked effect names for permission prompts, capture, observers, memory
  writes, and evidence storage.

`screen_recording_preflight` and `accessibility_trusted` are status values, not
pass/fail values. A machine can pass this smoke even when both are false,
because the slice proves safe inspection, not permission acquisition.

## Verification

```bash
swift build --package-path native/macos-shadow-pointer
swift test --package-path native/macos-shadow-pointer
swift run --package-path native/macos-shadow-pointer cortex-permission-smoke
uv run cortex-native-permission-smoke --json
uv run cortex-native-permission-smoke --fixture --json
```

This smoke must remain separate from real capture adapters. Future onboarding
can use this receipt to tell the Shadow Pointer what permissions are missing,
but any prompt or capture start belongs behind explicit user action.
