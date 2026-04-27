# Build Roadmap

Last updated: 2026-04-27

## Milestones

### v0.1: Memory Observer

Goal: observe a narrow coding/research workflow locally with clear consent and evidence controls.

- Shadow Pointer overlay
- app/window tracking
- sampled screenshots
- OCR
- accessibility tree capture
- terminal command capture
- local encrypted evidence vault
- manual pause/delete controls
- initial prompt-injection and secret-redaction fixtures

Exit evidence:

- synthetic observation captured and redacted
- evidence record stored with retention
- raw evidence expiry job demonstrated
- Shadow Pointer states visible
- task board and benchmark log updated

### v0.2: Scene Memory

Goal: turn event streams into inspectable memory candidates.

- scene segmentation
- episodic memory generation
- semantic memory extraction
- temporal edge records
- Memory Palace dashboard
- correction/delete/edit flows

Exit evidence:

- synthetic coding/research scene compiles into typed memory
- user correction supersedes or revokes prior memory
- deleted memory does not return in retrieval

### v0.3: Codex/Claude Context

Goal: expose governed memory to agents through context packs.

- MCP server
- `memory.search`
- `memory.get_context_pack`
- Codex plugin
- Claude-compatible memory bridge
- coding/research context templates

Exit evidence:

- local Codex-compatible MCP call returns task-scoped context pack
- prompt-injection fixture is quarantined or warned
- context pack includes source refs and warnings

### v0.4: Skill Forge

Goal: detect repeated workflows and propose draft-only skills.

- repeated workflow detection
- candidate skill UI
- skill object schema
- draft-only skill execution
- skill audit trail

Exit evidence:

- repeated synthetic workflow creates candidate skill
- user can approve, edit, reject, or request more evidence
- skill cannot execute external effects without policy approval

### v0.5: Self-Improvement

Goal: learn from outcomes without silently changing permissions or values.

- task postmortems
- retrieval quality scoring
- skill success/failure tracking
- self-lesson generation
- rollback for bad lessons

Exit evidence:

- failed task generates scoped self-lesson candidate
- accepted lesson changes retrieval or checklist behavior only
- rejected lesson is suppressed in future context packs

### v1.0: Private Agent Brain

Goal: robust local-first memory and skill substrate for agent work.

- scoped agent access
- project-level graph memory
- approved skill execution
- Shadow Pointer
- Memory Palace
- Skill Forge
- full audit and governance

## First Implementation Slices

| Order | Slice | Output | Proof |
| --- | --- | --- | --- |
| 1 | Runtime decision ADR | Tauri/Electron/SwiftUI plus local service decision | ADR with tradeoffs |
| 2 | Contracts as code | typed schemas for observation, evidence, memory, scene, skill, context pack | unit tests and fixture validation |
| 3 | Synthetic benchmark harness | fixtures for recall, deletion, injection, PII redaction | runnable command and JSON result |
| 4 | Evidence vault skeleton | encrypted or encryption-ready local blob store plus SQLite metadata | store/read/expire fixture |
| 5 | Privacy firewall skeleton | source trust classes, redaction decisions, quarantine decisions | synthetic injection and secret fixtures |
| 6 | Scene segmenter prototype | event stream to scene object | deterministic fixture output |
| 7 | Memory compiler prototype | scene to typed memory candidate | candidate includes evidence, confidence, validity |
| 8 | MCP server skeleton | `memory.search` and `memory.get_context_pack` stubs | local MCP client smoke test |
| 9 | Shadow Pointer prototype | visible states and pause/delete controls | local UI screenshot/manual verification |
| 10 | Memory Palace prototype | inspect/correct/delete memory | deletion benchmark passes |

## Build Trap To Avoid

Do not build:

```text
screen capture -> LLM summary -> vector DB -> search endpoint
```

Build:

```text
consented events
  -> firewall
  -> evidence
  -> scene
  -> typed memory
  -> temporal graph/index
  -> context pack
  -> audited agent gateway
  -> outcome postmortem
```

Then add Skill Forge.

