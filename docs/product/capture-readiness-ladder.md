# Capture Readiness Ladder

Benchmark: `CAPTURE-READINESS-LADDER-001`

Policy: `policy_capture_readiness_ladder_v1`

The Capture Readiness Ladder is the dashboard version of the next ten
real-capture gates. It is deliberately display-only: it explains what is ready,
what is blocked, and what the next safe action is without starting continuous
capture, storing raw pixels, writing durable private memory, or enabling any
external effect.

## Ten Gates

1. Bridge token: the local bridge serves an ephemeral dashboard token.
2. Localhost origin: remote clients and bad origins are rejected.
3. Shadow Clicker: the display-only native cursor overlay can run first.
4. Permission preflight: Screen Recording and Accessibility blockers are named.
5. Sensitive app filter: private apps remain excluded before capture
   eligibility.
6. Screen Probe: one metadata-only frame is allowed only after preflight.
7. Probe receipt UX: skipped probes produce visible receipts instead of silent
   failure.
8. Raw ref scavenger: temp refs are cleaned by age without reading payloads.
9. Metadata stream plan: future ScreenCaptureKit streaming stays count-only.
10. Receipt audit: starts, stops, probes, skips, and watchdog exits stay
    count-only.

## Safety Contract

The ladder blocks `continuous_capture`, `raw_pixel_return`,
`raw_ref_retention`, `durable_memory_write`, `external_effect`, and
`arbitrary_command_execution`.

The dashboard can route the user to Preflight, Screen Probe, and Receipts, but
those buttons still go through the tokenized localhost bridge and its existing
origin and CSRF checks. Static dashboard data never includes raw payloads, raw
refs, private memory content, secrets, or external instructions.

This is the bridge between the current Shadow Clicker demo and later consented
real screen capture: the user should be able to see exactly which gate failed
before we ask for more capability.
