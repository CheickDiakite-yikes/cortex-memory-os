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
- suggested skills;
- warnings;
- recommended next steps;
- policy refs.

Templates do not widen project, app, agent, or session scope. Retrieval scope
is still enforced separately by the retrieval policy.

## MVP Templates

| Template | Task Type | Memory Budget | Primary Lanes |
| --- | --- | --- | --- |
| `template_coding_debugging_v1` | coding/debugging | 5 | project, recent, procedural, self-lesson, policy |
| `template_research_synthesis_v1` | research/synthesis | 4 | project, procedural, self-lesson, policy |
| `template_general_v1` | general | 3 | project, recent, policy |

## Safety Rules

Templates must not:

- request all projects;
- ignore project/session/agent scope;
- request all agents or sessions;
- ask for production credentials;
- echo hostile prompt-injection text.

Templates should keep warnings stable and plain so they can be rendered directly
to agent context without becoming another prompt-injection channel.

## Self-Lesson Lane

Coding/debugging and research/synthesis templates include a self-lesson lane.
Only active self-lessons can enter that lane. Revoked, deleted, superseded, or
quarantined lessons stay out of context packs.

Self-lessons are selected by task relevance against the current goal and the
lesson's `applies_to` tags. The lane is separately budgeted so self-improvement
guidance cannot crowd out project evidence.

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

`CONTEXT-PACK-SELF-LESSON-001` verifies:

- active self-lessons can enter matching context packs;
- revoked self-lessons are excluded;
- lesson source refs are attached as evidence refs;
- self-lesson routing follows the selected template lane and budget.

`CONTEXT-PACK-AUDIT-LANE-001` verifies:

- context packs expose audit metadata for relevant active self-lessons;
- audit metadata omits redacted summaries, lesson content, and source task IDs;
- audit metadata does not enter warnings or recommended next steps as guidance.
