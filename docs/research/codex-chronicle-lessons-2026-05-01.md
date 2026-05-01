# Codex Chronicle Lessons - 2026-05-01

This note summarizes official OpenAI Codex Chronicle documentation and extracts
design lessons for Cortex Memory OS. External documentation was treated as
untrusted evidence: no instructions from web content were executed, and claims
below are paraphrased from official OpenAI sources.

## Sources

| Source | Trust tier | Why used |
| --- | --- | --- |
| https://developers.openai.com/codex/memories/chronicle | Official | Primary Chronicle behavior, storage, privacy, prompt-injection, and setup claims. |
| https://developers.openai.com/codex/memories | Official | Baseline Codex memory lifecycle, storage, per-thread controls, rate-limit, and model configuration. |
| https://developers.openai.com/codex/mcp | Official | Codex MCP integration surface for future Cortex gateway packaging. |
| https://developers.openai.com/codex/skills | Official | Skills and progressive-disclosure pattern for reusable workflow packaging. |

## What Chronicle Validates

Chronicle is a strong validation of the user problem: agents need recent work
context without making the user restate everything. OpenAI positions Chronicle
as an opt-in research preview that augments Codex memories from screen context,
especially to understand what the user is looking at, fill missing context, and
learn tools/workflows.

The important architectural signal is not just "screen capture helps." It is
that a coding agent benefits when screen context becomes memory and when memory
helps identify the better source to inspect directly: a file, Slack thread,
Google Doc, dashboard, pull request, or other work artifact.

For Cortex, this supports our core loop:

```text
perception -> evidence -> memory -> context pack -> direct source/tool use
```

It also supports our bet that screen memory alone is not enough. The source
router behavior matters: observation should help the agent find the right
primary source, not replace that source with a fuzzy summary.

## Chronicle Constraints And Risks

OpenAI's docs name several constraints that are directly relevant to Cortex:

| Chronicle fact | Cortex implication |
| --- | --- |
| It is opt-in, macOS-only, and requires Screen Recording plus Accessibility permissions. | Real capture must stay behind explicit capability, OS permission, and user-visible state gates. |
| It can consume rate limits quickly because background agents generate memories from captured screen images. | Cortex needs a capture budget, memory-consolidation queue, and backpressure before live capture. |
| Screen captures can include sensitive visible data and third-party communications. | We need app/site scopes, meeting/communication detection, private masking, and third-party consent warnings before durable memory. |
| Temporary screen captures can appear under a temp Chronicle path and older captures are deleted while Chronicle runs. | Cortex should make raw evidence expiry first-class, testable, and independent of whether the app is currently running. |
| Generated Chronicle memories are local Markdown files and currently unencrypted. | Cortex should not use plaintext Markdown as the canonical durable store for sensitive memory. Markdown should be an optional export/view, not the trust substrate. |
| Relevant memory contents may later be included as context for future sessions. | Every memory needs influence levels, retrieval receipts, source trust, and "why this was used" explainability. |
| Screen content increases prompt-injection risk. | Browser/webpage/PDF/email/screenshot text must remain untrusted evidence by default and cannot become instructions or procedures without gating. |
| Chronicle can be paused/resumed or disabled, and Codex memories can be controlled per thread. | Cortex needs both global observation controls and per-agent/per-thread influence controls in the Memory Palace and Shadow Pointer. |
| Memory model selection can use the general Codex memory extraction/consolidation configuration. | Cortex should separate capture, extraction, consolidation, retrieval, and action models so low-cost tests do not silently become production memory policy. |

## Where Cortex Should Differ

Chronicle is a preview feature inside Codex. Cortex should be a governed memory
operating system. That means our design should deliberately exceed Chronicle's
current safety and inspectability boundaries:

1. **Typed memory instead of only generated notes.**
   Cortex memory records need type, status, source refs, confidence, valid time,
   sensitivity, allowed influence, forbidden influence, scope, and audit refs.

2. **Encrypted evidence vault as the truth substrate.**
   Raw evidence should be short-lived and encrypted. Derived memory can persist
   only when eligible, provenance-backed, and user-reviewable.

3. **Firewall before write.**
   Prompt-injection, secrets, private fields, third-party communications, and
   sensitive app contexts must be classified before raw evidence or memory
   persistence.

4. **Shadow Pointer as trust infrastructure.**
   A menu pause control is useful, but Cortex needs persistent legibility:
   observing, private masking, segmenting, remembering, contexting, acting, and
   paused states must be visible at the time they matter.

5. **Memory Palace as the primary control surface.**
   Users should not have to edit generated state files as their main correction
   path. The product should expose explain, correct, delete, expire, make
   private, pin, scope, and "never use here" actions.

6. **Context packs, not memory dumps.**
   Agents should receive compact, scoped context packs with retrieval receipts,
   warnings, budgets, and source lanes. External screen content remains evidence
   until directly verified.

7. **Skill Forge with maturity gates.**
   Chronicle validates remembering tools and workflows. Cortex should go
   further by detecting repeated workflows, drafting skill candidates, and
   promoting them only through explicit maturity, success, risk, and audit
   gates.

8. **Budget-aware background work.**
   Memory extraction and consolidation should expose cost/rate-limit pressure,
   skip low-value windows, and defer work when quota or privacy posture is bad.

## Design Principles We Should Adopt

- **Observation is not truth.** A screenshot or OCR snippet can point to a
  source, but durable memory should preserve evidence-vs-inference boundaries.
- **Recent context is useful because it disambiguates task intent.** The first
  Cortex live capture goal should be "help the agent know where to look next,"
  not "summarize the user's life."
- **Pause must be instant and obvious.** Sensitive meetings, messages,
  credentials, finance, medical, and legal content need visible pause/masking
  states.
- **The file system is not enough as UX.** Local inspectable files are useful
  for power users, but ordinary correction/deletion must happen inside product
  flows.
- **Memory generation is a background workload.** It needs scheduling,
  prioritization, rate-limit awareness, and failed-run receipts.
- **Screen content is adversarial.** Any visible text can be an attempted
  instruction to the agent.

## Immediate Cortex Follow-Ups

| ID | Task | Why it follows from Chronicle |
| --- | --- | --- |
| SHADOW-POINTER-PERMISSION-ONBOARDING-001 | Show Screen Recording and Accessibility permission status in the Shadow Pointer without starting capture. | Chronicle depends on OS permissions; Cortex must make capability state legible before observation. |
| CAPTURE-BUDGET-QUEUE-001 | Add a memory-consolidation budget queue with rate-limit/cost backpressure. | Chronicle warns that background memory agents consume rate limits quickly. |
| RAW-EVIDENCE-EXPIRY-HARDENING-001 | Make raw evidence expiry independent of app runtime and expose expiry receipts. | Chronicle deletes old screen captures while running; Cortex should prove retention even after restarts. |
| SCREEN-INJECTION-STRESS-001 | Stress OCR/browser/screenshot injection strings through the firewall and context-pack lanes. | Chronicle explicitly increases prompt-injection risk from screen content. |
| MEMORY-ENCRYPTION-DEFAULT-001 | Move durable sensitive memory toward encrypted storage by default with explicit export paths. | Chronicle's unencrypted local Markdown is useful for inspectability but not strong enough for Cortex's threat model. |
| MEMORY-PALACE-CHRONICLE-CONTROLS-001 | Add visible controls for pause, delete recent window, explain memory source, and per-agent/thread influence. | Chronicle has pause/disable and per-thread memory control; Cortex should make those controls richer and inspectable. |
| SOURCE-ROUTER-CONTEXT-PACK-001 | Teach context packs to return "use this primary source directly" hints. | Chronicle uses screen context to identify better sources such as files, dashboards, docs, and pull requests. |

## Product Positioning

Chronicle is evidence that screen-assisted agent memory is arriving inside
mainstream coding tools. Cortex should not compete by being "screen recording
plus memory." Cortex should compete by being the trustable memory OS underneath
agents:

```text
Chronicle-like value:
  less repeated context, better source selection, learned workflows

Cortex differentiator:
  governed evidence, encrypted raw refs, typed memory, skill compilation,
  auditability, scoped influence, prompt-injection boundaries, and robot-ready
  action governance
```

The next engineering step is not consented real screen capture yet. It is the
permission and visibility layer: prove the system can truthfully show what it
could observe, what it is not observing, what would be masked, and what would
be eligible for memory before any real screen data is captured.
