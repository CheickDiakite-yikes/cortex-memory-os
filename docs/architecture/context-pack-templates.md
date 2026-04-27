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

## Benchmark

`CONTEXT-TEMPLATE-001` verifies:

- the default registry includes coding/debugging, research/synthesis, and
  general templates;
- templates are compact and policy-backed;
- goal selection picks the expected template;
- requested limits cannot exceed the template memory budget;
- template text cannot widen scope or request secrets;
- gateway context packs include template policy refs and suggested skills.
