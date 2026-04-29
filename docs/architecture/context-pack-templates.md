# Context Pack Templates

Last updated: 2026-04-27

Code contract: `src/cortex_memory_os/context_templates.py`

Context packs should be compact and task-shaped. Cortex should not dump every
available memory into an agent just because it can.

## Template Goals

Templates define:

- task type;
- memory lanes;
- maximum memory count;
- maximum self-lesson count;
- token, time, tool-call, and artifact budgets;
- maximum action risk and autonomy ceiling;
- suggested skills;
- warnings;
- recommended next steps;
- policy refs.

Templates do not widen project, app, agent, or session scope. Retrieval scope
is still enforced separately by the retrieval policy.

## MVP Templates

| Template | Task Type | Memory Budget | Token Budget | Tool / Artifact Budget | Risk / Autonomy |
| --- | --- | --- | --- | --- | --- |
| `template_coding_debugging_v1` | coding/debugging | 5 | 1800 | 8 tools / 3 artifacts | medium / assistive |
| `template_research_synthesis_v1` | research/synthesis | 4 | 1600 | 5 tools / 2 artifacts | low / assistive |
| `template_general_v1` | general | 3 | 1000 | 3 tools / 1 artifact | low / assistive |

## Safety Rules

Templates must not:

- request all projects;
- ignore project/session/agent scope;
- request all agents or sessions;
- ask for production credentials;
- echo hostile prompt-injection text.

Templates should keep warnings stable and plain so they can be rendered directly
to agent context without becoming another prompt-injection channel.

## Budget Envelope

`CONTEXT-BUDGET-001` makes every gateway context pack carry a `budget` object.
This object is metadata for the receiving agent and UI; it is not permission to
act outside existing policy.

The budget records:

- maximum prompt tokens and estimated prompt tokens;
- wall-clock time budget;
- tool-call budget;
- artifact budget;
- memory and self-lesson lane budgets;
- maximum action risk;
- autonomy ceiling;
- budget policy refs.

Requested budgets can only narrow the selected template. If an agent asks for a
higher token, time, tool, artifact, risk, or autonomy budget than the template
allows, Cortex returns the template ceiling. Context-pack budgets cannot
authorize high-risk or critical actions, and they cannot grant bounded autonomy
or recurring automation.

## Self-Lesson Lane

Coding/debugging and research/synthesis templates include a self-lesson lane.
Only active self-lessons can enter that lane. Revoked, deleted, superseded, or
quarantined lessons stay out of context packs.

Self-lessons are selected by task relevance against the current goal and the
lesson's `applies_to` tags. The lane is separately budgeted so self-improvement
guidance cannot crowd out project evidence. Scoped self-lessons must also match
the request's project, agent, or session scope before they can enter the lane.

## Audit Metadata Lane

Context packs may include audit metadata for relevant active self-lessons.
This lane carries IDs, actions, result codes, target refs, policy refs, and
visibility flags only. It does not include audit summaries, lesson content,
source task text, or instructions.

Agents can use audit metadata as safety evidence, for example to notice that a
self-lesson was explicitly promoted. They must not treat audit metadata as task
instructions or user preferences.

## Benchmark

`CONTEXT-TEMPLATE-001` verifies:

- the default registry includes coding/debugging, research/synthesis, and
  general templates;
- templates are compact and policy-backed;
- goal selection picks the expected template;
- requested limits cannot exceed the template memory budget;
- template text cannot widen scope or request secrets;
- gateway context packs include template policy refs and suggested skills.

`CONTEXT-BUDGET-001` verifies:

- gateway context packs expose token, time, tool-call, artifact, memory,
  self-lesson, risk, and autonomy budget metadata;
- requested budgets cannot exceed selected-template ceilings;
- estimated prompt tokens cannot exceed the prompt budget;
- high-risk, critical-risk, and autonomous budgets are rejected by the contract.

`CONTEXT-PACK-SELF-LESSON-001` verifies:

- active self-lessons can enter matching context packs;
- revoked self-lessons are excluded;
- lesson source refs are attached as evidence refs;
- self-lesson routing follows the selected template lane and budget.

`CONTEXT-PACK-AUDIT-LANE-001` verifies:

- context packs expose audit metadata for relevant active self-lessons;
- audit metadata omits redacted summaries, lesson content, and source task IDs;
- audit metadata does not enter warnings or recommended next steps as guidance.

`SELF-LESSON-RECALL-SCOPE-001` verifies:

- project-scoped self-lessons require a matching active project;
- agent-scoped self-lessons require a matching agent ID;
- session-scoped self-lessons require a matching session ID;
- missing scope context excludes scoped self-lessons from context packs.
