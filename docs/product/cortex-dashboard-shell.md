# Cortex Dashboard Shell

Last updated: 2026-04-30

Benchmark: `MEMORY-PALACE-SKILL-FORGE-UI-001`

Policy reference: `policy_cortex_dashboard_shell_v1`

This slice turns the generated dashboard concept into a local, static,
inspectable dashboard shell over safe view models. The goal is a usable product
surface for Memory Palace and Skill Forge without introducing live capture,
private memory fixtures, or gateway side effects.

## Design Source

The generated dashboard concept established the first visual direction:

- left navigation for Overview, Memory Palace, Skill Forge, Agent Gateway,
  Audit, and Policies;
- top status strip for Shadow Pointer, active project, consent scope, and
  Safety Firewall;
- two primary work areas for Memory Palace Review Queue and Skill Forge
  Candidate Workflows;
- bottom rail for Recent Safe Receipts;
- restrained local-ops palette with green, blue, amber, and red status
  accents;
- dense but readable operational UI, not a landing page.

## Data Boundary

The shell uses `src/cortex_memory_os/dashboard_shell.py` to compose existing
safe view models:

- `MemoryPalaceDashboard`
- `SkillForgeCandidateList`

The generated `ui/cortex-dashboard/dashboard-data.js` contains synthetic,
redacted, deterministic view-model data. It must contain no raw private memory,
screenshots, databases, API responses, logs, vector stores, or secret-like
tokens.

## UI Contract

The static app in `ui/cortex-dashboard/` must render:

- the status strip;
- Memory Palace review cards with status, confidence, source count, recall
  state, and exact gateway action plans;
- Skill Forge candidate cards with observed refs, risk, maturity, promotion
  blockers, and draft-only actions;
- local filter controls for both lists;
- icon-first action controls that update local UI state;
- Recent Safe Receipts with redacted targets.

All actions are declarative previews. They update local UI state and receipts
only. They do not call MCP, mutate memory, execute skills, export data, or
perform external effects.

## Safety Gates

`MEMORY-PALACE-SKILL-FORGE-UI-001` passes only when:

- UI files are present and reference `window.CORTEX_DASHBOARD_DATA`;
- Memory Palace and Skill Forge cards render from safe view models;
- action plans are visible but inert;
- generated fixture data has no secret markers or raw refs;
- dashboard docs, task board, benchmark plan, and benchmark registry name the
  slice;
- local browser proof confirms the first viewport renders without overlapping
  primary UI.
