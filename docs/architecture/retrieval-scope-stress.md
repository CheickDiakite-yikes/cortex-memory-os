# Retrieval Scope Stress

Last updated: 2026-04-30

`RETRIEVAL-SCOPE-STRESS-001` hardens the retrieval boundary across project,
agent, session, global, lifecycle, and sensitivity constraints.

## Contract

The stress suite verifies:

- project-specific memories do not cross mismatched `active_project`;
- agent-specific memories do not cross mismatched `agent_id`;
- session-only memories do not cross mismatched `session_id`;
- global memories can be excluded with `include_global=false`;
- deleted, revoked, superseded, quarantined, stored-only, secret, and
  never-store memories are not retrieved;
- gateway `memory.search` applies the same scope envelope as context packs.

## Gateway Surface

`memory.search` now accepts `active_project`, `agent_id`, `session_id`, and
`include_global` so direct search cannot bypass the scope controls already used
by `memory.get_context_pack`.

The benchmark remains synthetic and avoids private memory content. It validates
reason tags and returned memory IDs rather than raw source payloads.
