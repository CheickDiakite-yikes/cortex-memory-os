# Perception Event Envelope

Last updated: 2026-04-29

`PERCEPTION-EVENT-ENVELOPE-001` defines the first stable Perception Bus input
contract. It does not implement native capture yet. It defines the shape every
future adapter must produce before Privacy + Safety Firewall processing,
Evidence Vault storage, scene segmentation, memory compilation, or skill
learning.

## Purpose

The envelope wraps a raw `ObservationEvent` with the control metadata Cortex
needs before anything becomes durable:

- source kind: screen, app window, accessibility, terminal, browser, IDE, file
  system, agent, or robot sensor;
- consent state and capture scope;
- source trust class;
- sensitivity hint;
- routing decision: firewall required, ephemeral only, or discard;
- raw and derived refs;
- third-party-content and prompt-injection-risk markers;
- required policy refs;
- robot capability and simulation-first gate when the source is embodied.

## Hard Boundaries

- Raw perception refs require active consent.
- Raw perception refs must route through the Privacy + Safety Firewall.
- Prompt-injection risk must route through the Privacy + Safety Firewall.
- Discarded third-party content cannot keep derived refs.
- Robot sensor events require an explicit capability and simulation-first
  validation.
- Robot capability metadata is forbidden on non-robot sources.

## MVP Source Kinds

| Source kind | Example event type | First adapter |
| --- | --- | --- |
| `screen` | `screen_frame` | macOS ScreenCaptureKit sampling |
| `app_window` | `screen_frame` | active app/window watcher |
| `accessibility` | `accessibility_tree` | macOS accessibility observer |
| `terminal` | `terminal_command`, `terminal_output` | shell integration |
| `browser` | `browser_dom`, `ocr_text` | browser extension |
| `ide` | `file_event`, `agent_action` | editor extension or local watcher |
| `file_system` | `file_event` | project-local file watcher |
| `agent` | `agent_action`, `outcome` | Codex/Claude gateway events |
| `robot_sensor` | future embodied sensor event | simulation-gated robot adapter |

## Benchmark Contract

`PERCEPTION-EVENT-ENVELOPE-001` verifies that:

- a terminal command can be wrapped in a consented, firewall-routed perception
  envelope;
- raw refs fail without active consent;
- prompt-injection risk cannot bypass the firewall route;
- robot sensor events require explicit capability and simulation-first
  validation;
- this document and the benchmark plan name the contract.

The next layer is `PERCEPTION-FIREWALL-HANDOFF-001`, which converts valid
envelopes into `FirewallDecisionRecord` objects before evidence or memory
eligibility.
