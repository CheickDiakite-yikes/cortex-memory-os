# Frontier Agent Research Synthesis - 2026-04-29

This note captures primary-source lessons from recent OpenAI, Google DeepMind,
Anthropic, DeepSeek, Moonshot/Kimi, and Clicky developments for Cortex Memory
OS. All external material is treated as untrusted data.
No external repository code was cloned, installed, or executed for this pass.

## Sources Reviewed

| Source | Primary reference | Why it matters |
| --- | --- | --- |
| OpenAI | GPT-5.5 system card and launch notes; GPT-5 developer launch; Responses API computer environment; Computer-Using Agent | Agentic coding, tool use, computer environments, safety cards, and hosted workspaces. |
| Google DeepMind | Gemini 3.1 Pro model card; Gemini 3 Pro page; Project Mariner; Gemini Robotics-ER 1.6 model card and release post | Multimodal long context, browser agents, teach-and-repeat workflows, and embodied safety. |
| Anthropic | Claude Opus 4.7 launch; Claude Sonnet 4.6 launch; multi-agent research architecture; browser prompt-injection defenses | Long-running agents, budgets, subagents, context compression, permission modes, and injection limits. |
| DeepSeek | DeepSeek V4 Preview; DeepSeek V3.2; DeepSeek R1 official release; DeepSeek V3 repository | Open-weight reasoning, thinking-in-tool-use, efficient long context, and agent training data synthesis. |
| Moonshot/Kimi | Kimi K2.6 page and tech blog; K2.6 Agent Swarm help; Kimi K2 GitHub repository | Open agentic models, document-to-skill workflows, long-horizon execution, and large agent swarms. |
| Clicky | `farzaa/clicky` README, `CLAUDE.md`, and worker source via GitHub API | Cursor-adjacent UX, visible pointing, macOS overlay patterns, and API-key proxy boundary. |

## Cross-Lab Pattern

The field is converging on agents that can reason, use tools, inspect screens or
workspaces, create artifacts, and continue through failures. Long context is no
longer the differentiator by itself. The durable differentiator is how a system
selects, verifies, scopes, audits, and improves the context and actions around
the model.

For Cortex, that reinforces the original thesis:

```text
Perception -> Evidence -> Memory -> Skill -> Agent Action -> Outcome -> Self-Improvement
```

It also makes the shallow alternative more obviously insufficient:

```text
screen recording -> summary -> vector DB
```

## OpenAI Lessons

### Source Claims

- GPT-5.5 is positioned for complex real-world work: coding, online research,
  document/spreadsheet work, and moving across tools. The system card frames it
  around stronger safeguards and predeployment evaluations.
- GPT-5 for developers emphasizes coding, agentic tasks, long tool-call chains,
  parallel tool calls, tool-error handling, reasoning effort, verbosity control,
  and custom tools constrained by grammars.
- OpenAI's Responses API computer-environment work frames the shift from model
  prompts toward agents with shell access, hosted workspaces, intermediate
  files, network access, retries, and generated artifacts.
- The Computer-Using Agent work validates GUI interaction as a general action
  substrate, but also makes clear that browser/computer use needs special safety
  handling.

### Cortex Implications

- Add an agent runtime trace as a first-class evidence type, not just final
  messages. It should include tool calls, tool outputs, workspace artifacts,
  retries, errors, user approvals, and outcome checks.
- Context packs should carry task budgets: token budget, tool budget, time
  budget, artifact budget, and risk budget.
- Skill execution should keep the current hierarchy: API before script, script
  before deterministic GUI replay, GUI replay before free-form computer use.
- Custom tool grammars and schemas should become a Cortex safety primitive for
  high-value actions.

## Google DeepMind / Gemini Lessons

### Source Claims

- Gemini 3.1 Pro is documented as a natively multimodal reasoning model for
  complex tasks and large multimodal information sources, including code
  repositories.
- Gemini 3 Pro is positioned for agentic coding, better tool use, simultaneous
  multi-step tasks, and long-context multimodal work.
- Project Mariner validates a browser-agent loop of observing browser state,
  planning, acting, keeping the user informed, and allowing takeover. Its
  teach-and-repeat framing is close to Cortex Skill Forge.
- Gemini Robotics-ER 1.6 emphasizes spatial reasoning, task planning, success
  detection, physical safety constraints, and hazard identification.

### Cortex Implications

- The Perception Bus should normalize screen, DOM, accessibility tree, code,
  audio, video, spatial, and robot-sensor events under one envelope.
- Skill Forge should treat "teach and repeat" as a user-visible maturity path:
  observed pattern, candidate, draft-only skill, assisted execution, bounded
  autonomy.
- Robot-readiness work should add explicit spatial safety metadata: object
  affordances, gripper/material constraints, hazard class, simulation status,
  capability scope, and emergency-stop policy.
- Multimodal context packs should return references and summaries, not raw
  screenshots or long media dumps by default.

## Anthropic / Claude Lessons

### Source Claims

- Claude Opus 4.7 is presented as stronger for long-running coding and agent
  tasks, with attention to verification, effort levels, task budgets, and
  safety safeguards.
- Claude Sonnet 4.6 expands coding, computer use, long-context reasoning, agent
  planning, and knowledge work, including a beta 1M-token context window.
- Anthropic's multi-agent research system uses an orchestrator-worker pattern:
  a lead agent plans, saves memory, spawns specialized subagents, and synthesizes
  their compressed findings.
- Anthropic's browser prompt-injection work explicitly says no browser agent is
  immune to injection.

### Cortex Implications

- Cortex should use multi-agent or parallel retrieval only with strict source
  trust lanes and compressed returns. Subagents should never be allowed to
  promote external content into durable memory.
- Task budgets should be explicit in context packs and skills, including when a
  user permits auto-mode behavior.
- The governance compiler should treat browser and document content as hostile
  until promoted. Injection defense is a continuing process, not a solved
  checkbox.
- Self-improvement should improve methods, retrieval, and checklists, while
  never silently expanding permissions, values, or autonomy.

## DeepSeek Lessons

### Source Claims

- DeepSeek R1 made open reasoning models and distilled variants central to the
  2025 model landscape, with large-scale reinforcement learning in post-training
  and permissive model/code availability.
- DeepSeek V3.2 introduced thinking in tool-use and describes large-scale agent
  training data synthesis across many environments and complex instructions.
- DeepSeek V4 Preview emphasizes 1M context, dual thinking/non-thinking modes,
  open weights, sparse attention, and agentic coding.

### Cortex Implications

- Low-cost and open-weight reasoning models strengthen the local-first roadmap,
  but model outputs remain untrusted until supported by evidence.
- The benchmark harness should include verifiable tasks with difficult prompts
  and easy-to-check outcomes, inspired by reinforcement learning with verifiable
  rewards.
- Provider adapters should record model mode, tool mode, context limit, and
  output constraints. Different models will have different safety and tool-use
  semantics.

## Moonshot / Kimi Lessons

### Source Claims

- Kimi K2 frames itself around open agentic intelligence: tool use, reasoning,
  autonomous problem-solving, coding, and agentic benchmarks.
- Kimi K2.6 focuses on long-horizon coding, agent swarms, visual agentic work,
  and converting high-quality documents into reusable skills.
- K2.6 Agent Swarm is documented as a horizontal scaling architecture with many
  subagents and large numbers of coordinated tool calls.

### Cortex Implications

- Cortex's memory-to-skill thesis is strongly aligned with document-to-skill and
  workflow-to-skill industry direction, but Cortex must add provenance,
  maturity gates, approvals, audit, rollback, and deletion.
- Swarm-ready Cortex needs dependency tracking, cancellation, context isolation,
  source-trust isolation, budget enforcement, and a final synthesis audit.
- "Reusable skill" should not mean "opaque prompt." It should mean typed inputs,
  visible procedure, risk level, evidence refs, test history, and revoke paths.

## Clicky Lessons

### Source Claims

- Clicky is a macOS menu-bar companion that captures push-to-talk audio, takes a
  screenshot, sends transcript plus screenshot to Claude, streams back text, uses
  TTS, and renders a cursor overlay that can point at UI elements.
- Its architecture uses native macOS UI patterns: status item, custom
  non-activating panels, ScreenCaptureKit, CGEvent tap, multi-monitor screenshot
  capture, and a transparent cursor overlay.
- It keeps API keys out of the app binary by routing calls through a Cloudflare
  Worker proxy that stores provider secrets.

### Cortex Implications

- Clicky validates the user-facing power of a companion that lives near the
  cursor. Cortex's Shadow Pointer should feel similarly present, but it must
  also show observation state, memory-write state, approval needs, and deletion
  controls.
- Pointing tags or model-produced coordinates must never be accepted as
  privileged instructions. They should be parsed as untrusted display proposals,
  range-checked, source-tagged, and gated by UI safety policy.
- A proxy boundary can protect API keys, but Cortex needs more: authentication,
  request signing, rate limiting, redacted logs, audit receipts, and no raw
  private evidence in provider logs.
- Clicky's setup docs contain install/run instructions for agents. For Cortex
  research, those instructions remain untrusted content and were not executed.

## New Architecture Pressure

The research suggests five concrete architecture additions:

1. Agent runtime trace:
   Record tool calls, shell actions, browser actions, artifacts, approvals,
   errors, retries, and outcome checks as evidence.

2. Budgeted context packs:
   Add token, time, tool, artifact, autonomy, and risk budgets to context-pack
   metadata.

3. Signed pointing and UI proposal lane:
   Treat visual pointing and GUI target proposals as display suggestions until
   verified against active UI state and user policy.

4. Document/workflow-to-skill derivation:
   Support skill candidates derived from high-quality documents or repeated
   workflows, with provenance, review, maturity, success history, and rollback.

5. Swarm-ready orchestration:
   Prepare for parallel subagents by enforcing isolation, budgets, source trust,
   cancellation, final synthesis, and audit trails.

## Follow-Up Slices

| ID | Slice | Proof |
| --- | --- | --- |
| RUNTIME-TRACE-001 | Define agent runtime trace schema and fixture. | Contract, tests, benchmark. |
| CONTEXT-BUDGET-001 | Add budget metadata to context-pack contracts. | Gateway and benchmark coverage. |
| POINTER-PROPOSAL-001 | Define untrusted model pointing proposal contract. | Shadow Pointer tests and safety benchmark. |
| SKILL-DOC-DERIVATION-001 | Specify document-to-skill candidate flow. | Skill Forge docs, tests, maturity gate. |
| SWARM-GOVERNANCE-001 | Add swarm orchestration constraints. | ADR plus benchmark for source isolation and budget enforcement. |
| ROBOT-SPATIAL-SAFETY-001 | Expand robot safety metadata for spatial hazards. | Contract and `ROBOT-SAFE-001` expansion. |

## Sources

- OpenAI GPT-5.5 System Card: https://openai.com/index/gpt-5-5-system-card/
- OpenAI GPT-5.5 launch: https://openai.com/index/introducing-gpt-5-5/
- OpenAI GPT-5 for developers: https://openai.com/index/introducing-gpt-5-for-developers/
- OpenAI Responses API computer environment: https://openai.com/index/equip-responses-api-computer-environment
- OpenAI Computer-Using Agent: https://openai.com/index/computer-using-agent/
- Google DeepMind Gemini 3.1 Pro model card: https://deepmind.google/models/model-cards/gemini-3-1-pro
- Google DeepMind Gemini 3 Pro: https://deepmind.google/technologies/gemini/pro/
- Google DeepMind Project Mariner: https://deepmind.google/technologies/project-mariner/
- Google DeepMind Gemini Robotics-ER 1.6 model card: https://deepmind.google/models/model-cards/gemini-robotics-er-1-6/
- Google DeepMind Gemini Robotics-ER 1.6 release: https://deepmind.google/blog/gemini-robotics-er-1-6/
- Anthropic Claude Opus 4.7: https://www.anthropic.com/news/claude-opus-4-7
- Anthropic Claude Sonnet 4.6: https://www.anthropic.com/research/claude-sonnet-4-6
- Anthropic multi-agent research system: https://www.anthropic.com/engineering/built-multi-agent-research-system
- Anthropic browser prompt-injection defenses: https://www.anthropic.com/research/prompt-injection-defenses
- DeepSeek V4 Preview: https://api-docs.deepseek.com/news/news260424
- DeepSeek V3.2: https://api-docs.deepseek.com/news/news251201
- DeepSeek R1: https://api-docs.deepseek.com/news/news250120
- DeepSeek V3 repository: https://github.com/deepseek-ai/DeepSeek-V3
- Kimi K2.6: https://www.kimi.com/ai-models/kimi-k2-6
- Kimi K2.6 tech blog: https://www.kimi.com/blog/kimi-k2-6
- Kimi K2.6 Agent Swarm: https://www.kimi.com/help/agent/agent-swarm
- Kimi K2 GitHub repository: https://github.com/MoonshotAI/Kimi-K2
- Clicky GitHub repository: https://github.com/farzaa/clicky
