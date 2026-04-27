# ADR 0003: Runtime Shell And Local Service Shape

Status: Accepted

Date: 2026-04-27

## Context

The laptop MVP needs to observe coding and research workflows with explicit user consent, show a Shadow Pointer overlay, capture screen/accessibility/terminal/browser signals, store governed evidence locally, and expose context packs to Codex/Claude through MCP.

The first runtime decision must optimize for:

- macOS Screen Recording and Accessibility permissions.
- reliable transparent/floating overlay behavior.
- strong local security boundaries.
- fast iteration on memory contracts, benchmarks, and agent gateway behavior.
- future compatibility with phone and robot embodiments.

Primary docs checked on 2026-04-27:

- Apple ScreenCaptureKit docs describe high-performance screen/audio capture, shareable content selection, frame metadata, and the system content-sharing picker.
- Apple AXUIElement docs describe the macOS Accessibility API used by assistive applications to communicate with accessible applications and handle disabled/failed API states.
- Apple NSWindow docs expose native window levels for floating/status/overlay-like behavior.
- Tauri docs emphasize small, fast, secure cross-platform apps, but transparent windows on macOS require the `macos-private-api` feature and are not App Store acceptable.
- Electron docs provide mature window controls such as always-on-top, visible-on-all-workspaces, focusability, mouse-event pass-through, and transparency, while Electron's own security guide stresses strict renderer isolation and web-content controls.

## Decision

Use a two-process local system for the MVP:

```text
Native macOS shell: SwiftUI + AppKit
  - permissions
  - Shadow Pointer overlay
  - ScreenCaptureKit observer
  - Accessibility observer
  - app/window state
  - local status/control surface

Python local engine
  - contracts and schemas
  - privacy/firewall decisions
  - scene segmentation
  - evidence vault metadata
  - memory compiler
  - benchmark harness
  - MCP server
  - local dashboard API
```

The native shell talks to the Python engine over a local-only interface. Prefer a Unix domain socket for packaged production and allow `127.0.0.1` HTTP during development.

The Memory Palace and Skill Forge can be local web views served by the Python engine, but sensitive native permissions and overlay behavior stay in the SwiftUI/AppKit shell.

## Why Not Tauri First

Tauri remains a possible distribution shell later, especially for a cross-platform dashboard. It is not the first choice for the macOS observer because:

- The Shadow Pointer wants transparent/floating overlay behavior.
- Tauri's macOS transparent-window path depends on private API configuration.
- The observer needs direct native capture and accessibility integration anyway.
- Adding Rust/webview boundaries before the memory contracts exist slows down the first verified slices.

## Why Not Electron First

Electron is viable for fast UI prototyping and has strong overlay controls, including always-on-top, visible-on-all-workspaces, focusability, mouse-event pass-through, and transparency.

It is not the first choice because:

- The app will handle extremely sensitive local context.
- Electron increases the renderer/security-hardening surface.
- Native capture/permission behavior is central, not incidental.
- The UI can still be web-based inside a native shell when needed.

## Consequences

- The first implementation can begin in Python without waiting on macOS packaging.
- Native macOS work has a clear boundary and can be mocked by synthetic observation fixtures.
- The contract layer remains independent of SwiftUI, Electron, Tauri, or future robot runtimes.
- The dashboard can still be web-based without making the whole app an Electron app.
- The MCP server lives in the local engine, which keeps agent integration close to memory policy and audit.

## Alternatives Considered

| Option | Pros | Cons | Decision |
| --- | --- | --- | --- |
| SwiftUI/AppKit shell + Python engine | best macOS permissions/overlay fit, strongest native boundary, Python speed for memory/bench/MCP | two-process packaging complexity | accepted |
| Tauri shell + Python sidecar | small cross-platform shell, security-focused framework | macOS transparency private API issue, Rust/webview overhead early | defer |
| Electron app + Python sidecar | fastest web UI, mature overlay controls | larger attack surface, more hardening burden | defer |
| Python-only app | fastest backend iteration | poor macOS permissions and overlay story | reject |
| Swift-only monolith | strongest native integration | slower iteration for memory benchmarks and MCP ecosystem | reject |

## Verification Plan

- Implement contracts and benchmark harness in Python first.
- Keep observation input mockable through synthetic fixtures.
- Before building native capture, create a minimal SwiftUI/AppKit proof for Shadow Pointer states and pause/delete controls.
- Before enabling real screen capture, prove firewall fixtures for prompt injection and fake secrets.
- Any future move to Tauri/Electron requires a replacement ADR and a security review.

