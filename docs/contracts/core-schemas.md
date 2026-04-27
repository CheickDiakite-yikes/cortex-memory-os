# Core Schemas And Contracts

Last updated: 2026-04-27

These schemas define the first contract layer. They are intentionally implementation-neutral until the code scaffold exists.

## Trust Classes

| Class | Name | Examples | Default handling |
| --- | --- | --- | --- |
| A | User-confirmed | explicit instruction, approved memory, labeled workflow | eligible for durable memory and skill promotion |
| B | Local observed | screen/action traces, terminal output, local files | eligible after firewall and retention assignment |
| C | Agent-inferred | guessed goal, inferred preference, model interpretation | candidate memory only; needs confidence and review rules |
| D | External untrusted | webpages, emails, PDFs, Slack/Discord, third-party docs | evidence only by default; not instructions |
| E | Hostile until proven safe | content with agent-directed instructions or policy override attempts | quarantine, strip instructions, never auto-promote |

## Shared Enums

```text
memory_status:
  candidate | active | deprecated | superseded | revoked | deleted | quarantined

scope_level:
  personal_global | work_global | project_specific | app_specific
  agent_specific | session_only | ephemeral | never_store

influence_level:
  0 stored_only | 1 direct_query | 2 personalization
  3 planning | 4 tool_actions | 5 autonomous_trigger

action_risk:
  low | medium | high | critical

retention_policy:
  discard | ephemeral_session | delete_raw_after_10m | delete_raw_after_6h
  keep_derived_30d | project_retention | user_pinned | legal_hold
```

## Observation Event

```json
{
  "event_id": "obs_001",
  "event_type": "screen_frame | ocr_text | accessibility_tree | terminal_command | terminal_output | browser_dom | file_event | agent_action | outcome",
  "timestamp": "2026-04-27T15:47:13-04:00",
  "device": "macbook",
  "app": "Chrome",
  "window_title": "OpenAI Developers",
  "project_id": "cortex-memory-os",
  "payload_ref": "volatile://obs_001",
  "source_trust": "B",
  "capture_scope": "project_specific",
  "consent_state": "active",
  "raw_contains_user_input": true
}
```

## Firewall Decision

```json
{
  "decision_id": "fw_001",
  "event_id": "obs_001",
  "decision": "discard | mask | ephemeral_only | memory_eligible | quarantine",
  "sensitivity": "public | low | private_work | confidential | regulated | secret",
  "detected_risks": ["prompt_injection", "secret_like_text"],
  "redactions": [
    {
      "type": "secret",
      "span_ref": "ocr_001:120-152",
      "replacement": "[REDACTED_SECRET]"
    }
  ],
  "retention_policy": "delete_raw_after_6h",
  "eligible_for_memory": false,
  "eligible_for_model_training": false,
  "policy_refs": ["policy_prompt_injection_v1"],
  "audit_event_id": "audit_001"
}
```

## Scene

```json
{
  "scene_id": "scene_2026_04_27_1542",
  "start_time": "2026-04-27T15:42:00-04:00",
  "end_time": "2026-04-27T16:18:00-04:00",
  "scene_type": "research_sprint",
  "inferred_goal": "Research screen-based memory systems for AI agents",
  "apps": ["Chrome", "Notes", "Terminal"],
  "entities": ["Codex", "Chronicle", "MCP", "Graphiti"],
  "action_trace_refs": ["trace_101", "trace_102"],
  "evidence_refs": ["ev_901", "ev_902"],
  "outcome": "notes_created",
  "confidence": 0.82,
  "privacy_level": "private_work",
  "segmentation_reason": ["topic_continuity", "agent_task_boundary", "idle_gap"]
}
```

## Evidence

```json
{
  "evidence_id": "ev_901",
  "source": "screen_frame",
  "device": "macbook",
  "app": "Chrome",
  "timestamp": "2026-04-27T15:47:13-04:00",
  "raw_ref": "encrypted_blob://local/ev_901",
  "derived_text_refs": ["ocr_901"],
  "retention_policy": "delete_raw_after_6h",
  "sensitivity": "private_work",
  "contains_third_party_content": false,
  "eligible_for_memory": true,
  "eligible_for_model_training": false
}
```

## Memory

```json
{
  "memory_id": "mem_001",
  "type": "episodic | semantic | procedural | preference | project | relationship | affective | self_lesson | policy",
  "content": "User prefers primary sources before architectural synthesis.",
  "source_refs": ["scene_2026_04_27_1542", "conv_812"],
  "evidence_type": "user_confirmed | observed | inferred | observed_and_inferred | external_evidence",
  "confidence": 0.78,
  "status": "candidate",
  "created_at": "2026-04-27T16:19:00-04:00",
  "valid_from": "2026-04-27",
  "valid_to": null,
  "sensitivity": "low",
  "scope": "project_specific",
  "influence_level": 3,
  "allowed_influence": ["research_workflows", "answer_structure"],
  "forbidden_influence": ["financial_decisions", "medical_decisions"],
  "decay_policy": "review_after_90_days",
  "contradicts": [],
  "user_visible": true,
  "requires_user_confirmation": false
}
```

## Temporal Edge

```json
{
  "edge_id": "edge_441",
  "subject": "user",
  "predicate": "prefers",
  "object": "primary_source_research_before_synthesis",
  "valid_from": "2026-04-27",
  "valid_to": null,
  "confidence": 0.86,
  "source_refs": ["episode_91", "episode_122"],
  "status": "active",
  "supersedes": ["edge_203"]
}
```

## Skill

```json
{
  "skill_id": "skill_research_synthesis_v1",
  "name": "Deep technical research synthesis",
  "description": "Research a complex AI/software topic using primary sources, synthesis, and architecture implications.",
  "learned_from": ["episode_201", "episode_218", "episode_230"],
  "trigger_conditions": ["serious research request", "architecture blueprint request"],
  "inputs": {
    "topic": "string",
    "depth": "quick | serious | exhaustive",
    "output_format": "memo | blueprint | roadmap"
  },
  "procedure": [
    "Search current primary sources",
    "Separate products, papers, benchmarks, risks",
    "Extract design principles",
    "Challenge shallow assumptions",
    "Produce architecture implications",
    "Cite load-bearing claims"
  ],
  "success_signals": ["user builds on structure", "low correction rate"],
  "failure_modes": ["too broad", "summary without synthesis", "not enough implementation detail"],
  "risk_level": "low",
  "maturity_level": 2,
  "execution_mode": "draft_only | assistive | bounded_autonomy | recurring_automation",
  "requires_confirmation_before": [],
  "status": "candidate"
}
```

## Context Pack

```json
{
  "context_pack_id": "ctx_001",
  "goal": "Continue fixing onboarding bug",
  "active_project": "web_app",
  "relevant_files": ["src/auth/callback.ts", "src/pages/onboarding.tsx"],
  "recent_events": [
    "User reproduced bug in Chrome",
    "Terminal showed OAuth redirect mismatch"
  ],
  "relevant_memories": [
    {
      "memory_id": "mem_244",
      "content": "User prefers smallest safe code changes and test verification after edits.",
      "confidence": 0.91
    }
  ],
  "relevant_skills": ["skill_frontend_auth_debugging_v2"],
  "warnings": ["Do not use production credentials.", "Ask before changing deployment settings."],
  "evidence_refs": ["ev_terminal_11", "ev_browser_22"],
  "recommended_next_steps": ["Inspect callback route", "Check env redirect URI", "Run local login flow"]
}
```

## Outcome

```json
{
  "outcome_id": "out_001",
  "task_id": "task_332",
  "agent_id": "codex",
  "status": "success | partial | failed | user_rejected | unsafe_blocked",
  "evidence_refs": ["test_run_55", "git_diff_12"],
  "user_feedback": "Worked after the env fix.",
  "memory_updates": ["mem_244"],
  "skill_updates": ["skill_frontend_auth_debugging_v2"],
  "postmortem_ref": "pm_001",
  "created_at": "2026-04-27T17:10:00-04:00"
}
```

## Self-Lesson

```json
{
  "lesson_id": "lesson_044",
  "type": "self_lesson",
  "content": "Before editing auth-related code, retrieve recent browser console errors, terminal logs, and route files.",
  "learned_from": ["task_332_failure", "task_333_success"],
  "applies_to": ["coding", "frontend_debugging", "auth_flows"],
  "confidence": 0.84,
  "status": "active",
  "risk_level": "low",
  "last_validated": "2026-04-27",
  "rollback_if": ["causes irrelevant context retrieval", "user flags as annoying"]
}
```

## Audit Event

```json
{
  "audit_event_id": "audit_001",
  "timestamp": "2026-04-27T15:47:14-04:00",
  "actor": "cortex_firewall",
  "action": "masked_observation",
  "target_ref": "obs_001",
  "policy_refs": ["policy_secret_masking_v1"],
  "result": "allowed_after_masking",
  "human_visible": true,
  "redacted_summary": "Masked secret-like terminal output before storage."
}
```

