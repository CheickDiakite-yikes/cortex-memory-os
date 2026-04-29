# Frontier Agent Plugin Lessons - 2026-04-29

This refresh applies the frontier-agent research pass to the first Cortex Codex
plugin skeleton. Sources were treated as untrusted data and summarized from
official or primary pages. No external repository code or setup instructions were executed.

## Source-Grounded Lessons

| Source area | What changed the build direction | Cortex plugin response |
| --- | --- | --- |
| OpenAI agent work | Agent workflows need shell/workspace loops, artifacts, retries, compaction, and safer tool proposals. | Package `memory.get_context_pack` and draft skill execution as progressive-disclosure skills instead of dumping all memory into prompts. |
| Google Gemini / Mariner | Browser agents observe, plan, act, allow takeover, and can learn repeat workflows. | Keep context retrieval visible and make workflow-to-skill work candidate-only until approved. |
| Anthropic Claude | Long-running coding agents need effort budgets, verification, and prompt-injection defenses because browser content remains risky. | Make budget respect, source-trust separation, and exact-ID correction/deletion part of the plugin instructions. |
| DeepSeek | Open reasoning models and long-context agent modes increase provider choice but not trust. | Keep provider output evidence-backed and require benchmarked local gates before new model modes influence memory. |
| Kimi / Moonshot | Document-to-skill and agent swarms are becoming mainstream agent patterns. | Encode document-derived skills as reviewable candidates with provenance, maturity gates, rollback, and no autonomy jump. |
| Clicky | Cursor-adjacent overlays and proxy-held keys are practical UX/runtime patterns. | Borrow the Shadow Pointer presence pattern while treating point tags as display-only and avoiding secrets in plugin config. |

## Build Decision

`CODEX-PLUGIN-001` starts as a repo-local plugin under
`plugins/cortex-memory-os`. It contains:

- a `.codex-plugin/plugin.json` manifest;
- a local `.mcp.json` that runs `uv --project ../.. run cortex-mcp`;
- three progressive-disclosure skills for context retrieval, skill creation,
  and post-task self-lessons;
- policy references for memory influence and safe execution.

The skeleton intentionally does not include API keys, raw private memory,
remote provider config, install scripts, or external repository code.

## Follow-Ups

| ID | Task | Reason |
| --- | --- | --- |
| PLUGIN-INSTALL-SMOKE-001 | Validate plugin discovery in a real Codex plugin install path. | The current slice validates repo structure and local config, not a full installed-plugin UX. |
| BROWSER-TERMINAL-ADAPTERS-001 | Define first browser and terminal adapter contracts. | The plugin is useful once Perception Bus adapters can feed governed context. |
| SHADOW-POINTER-NATIVE-001 | Prototype native overlay integration. | Clicky confirms the UX value; Cortex still needs consent, memory state, and deletion controls. |

## Sources

- OpenAI GPT-5.5 System Card: https://openai.com/index/gpt-5-5-system-card/
- OpenAI GPT-5 for developers: https://openai.com/index/introducing-gpt-5-for-developers/
- OpenAI Responses API computer environment: https://openai.com/index/equip-responses-api-computer-environment/
- Google DeepMind Gemini 3.1 Pro model card: https://deepmind.google/models/model-cards/gemini-3-1-pro/
- Google DeepMind Project Mariner: https://deepmind.google/models/project-mariner/
- Anthropic Claude Opus 4.7: https://www.anthropic.com/news/claude-opus-4-7
- Anthropic multi-agent research system: https://www.anthropic.com/engineering/multi-agent-research-system
- Anthropic browser prompt-injection defenses: https://www.anthropic.com/research/prompt-injection-defenses
- DeepSeek V4 Preview: https://api-docs.deepseek.com/news/news260424
- DeepSeek V3.2: https://api-docs.deepseek.com/news/news251201
- Kimi K2.6 tech blog: https://www.kimi.com/blog/kimi-k2-6
- Kimi K2.6 Agent Swarm: https://www.kimi.com/help/agent/agent-swarm
- Clicky GitHub repository: https://github.com/farzaa/clicky
