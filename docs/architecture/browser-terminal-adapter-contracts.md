# Browser And Terminal Adapter Contracts

Last updated: 2026-04-29

`BROWSER-TERMINAL-ADAPTERS-001` defines the first concrete adapter boundary for
the Perception Bus. These adapters still use synthetic local events, but they
represent the shape future browser extensions and shell integrations must
produce before any data can reach memory, skills, or agent context packs.

## Why This Layer Exists

The Perception Bus should not hand raw app data directly to memory. Browser and
terminal collectors must first produce narrow, consent-aware adapter events that
compile into `PerceptionEventEnvelope` objects.

The adapter contract guarantees that:

- consent state is explicit before raw refs exist;
- terminal events are local observed source-trust Class B;
- browser DOM events are external untrusted source-trust Class D;
- web content is third-party by default and cannot become memory eligible
  merely because it looks useful;
- prompt-injection risk is detected before the firewall handoff;
- every adapter envelope carries `policy_perception_adapter_contract_v1`.

## Terminal Adapter

The terminal adapter emits `TerminalAdapterEvent` records for
`terminal_command` and `terminal_output` observations.

Allowed behavior:

- active consent can keep raw terminal refs for firewall review;
- paused or revoked consent discards the event and drops raw/derived refs;
- benign local commands may become raw-and-derived evidence after firewall
  approval;
- secret-like terminal output is masked, raw refs are dropped, and only a
  redacted derived ref can remain.

Blocked behavior:

- non-terminal event types;
- raw refs when consent is paused, revoked, or unknown;
- direct memory writes before firewall and evidence eligibility planning.

## Browser Adapter

The browser adapter emits `BrowserAdapterEvent` records for browser DOM text.
It requires an `http` or `https` URL and treats visible page text as external
untrusted content.

Allowed behavior:

- browser DOM text can be cited as derived evidence;
- benign external pages route through the firewall and become ephemeral-only;
- prompt-injection pages are quarantined and lose raw and derived refs;
- raw DOM refs can exist only while consent is active, and the evidence
  eligibility handoff must drop them for third-party content.

Blocked behavior:

- `file://` or local paths through the browser adapter;
- treating webpage text as trusted memory or instructions;
- preserving raw browser refs after third-party or injection decisions.

## Handoff Chain

```text
TerminalAdapterEvent / BrowserAdapterEvent
  -> PerceptionEventEnvelope
  -> FirewallDecisionRecord
  -> EvidenceEligibilityPlan
```

The adapter module exposes `handoff_terminal_event` and
`handoff_browser_event` to prove that the whole chain preserves source trust,
policy refs, consent, prompt-injection flags, redaction, and raw-write rules.

## Benchmark Contract

`BROWSER-TERMINAL-ADAPTERS-001` verifies that:

- terminal commands produce local observed, firewall-routed envelopes;
- terminal secret output drops raw refs and keeps only redacted derived refs;
- benign browser DOM is external, third-party, ephemeral-only, and not memory
  eligible;
- browser prompt injection is quarantined before evidence storage;
- paused consent discards adapter refs;
- adapter contracts reject malformed terminal and browser shapes.
