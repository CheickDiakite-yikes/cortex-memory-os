window.CORTEX_DASHBOARD_DATA = {
  "active_project": "cortex-memory-os",
  "audit_logging": true,
  "cloud_sync": false,
  "design_notes": [
    "Two primary work areas: Memory Palace review queue and Skill Forge candidates.",
    "Status strip exposes observation, project, consent, and firewall state.",
    "Action controls are declarative UI plans; this shell does not execute mutations."
  ],
  "encrypted_at_rest": true,
  "generated_at": "2026-04-30T04:01:17.784922Z",
  "local_mode": true,
  "memory_palace": {
    "audit_summary": {
      "content_redacted": true,
      "counts_by_action": {
        "create_memory": 1,
        "create_skill_candidate": 1
      },
      "human_visible_count": 2,
      "latest_audit_event_id": "audit_skill_candidate_created_auth"
    },
    "cards": [
      {
        "action_plans": [
          {
            "audit_action": null,
            "content_redacted": true,
            "data_egress": false,
            "flow_id": "explain_memory",
            "gateway_tool": "memory.explain",
            "mutation": false,
            "required_inputs": [
              "memory_id_or_visible_card_anchor"
            ],
            "requires_confirmation": false
          },
          {
            "audit_action": "correct_memory",
            "content_redacted": true,
            "data_egress": false,
            "flow_id": "correct_memory",
            "gateway_tool": "memory.correct",
            "mutation": true,
            "required_inputs": [
              "memory_id_or_visible_card_anchor",
              "corrected_content"
            ],
            "requires_confirmation": false
          },
          {
            "audit_action": "delete_memory",
            "content_redacted": true,
            "data_egress": false,
            "flow_id": "delete_memory",
            "gateway_tool": "memory.forget",
            "mutation": true,
            "required_inputs": [
              "memory_id_or_visible_card_anchor",
              "explicit_delete_confirmation"
            ],
            "requires_confirmation": true
          },
          {
            "audit_action": "export_memories",
            "content_redacted": true,
            "data_egress": true,
            "flow_id": "export_memories",
            "gateway_tool": "memory.export",
            "mutation": false,
            "required_inputs": [
              "selected_memory_ids_or_scope",
              "explicit_export_confirmation"
            ],
            "requires_confirmation": true
          }
        ],
        "audit_count": 0,
        "confidence": 0.87,
        "content_preview": "In local development, OAuth redirect URI mismatches usually require checking callback route and env configuration together.",
        "content_redacted": false,
        "evidence_type": "observed",
        "memory_id": "mem_auth_redirect_root_cause",
        "recall_eligible": true,
        "redaction_count": 0,
        "requires_user_confirmation": false,
        "scope": "project_specific",
        "sensitivity": "low",
        "source_count": 2,
        "source_refs": [
          "project:cortex-memory-os",
          "terminal:test_auth_flow"
        ],
        "status": "active",
        "type": "semantic",
        "user_visible": true
      },
      {
        "action_plans": [
          {
            "audit_action": null,
            "content_redacted": true,
            "data_egress": false,
            "flow_id": "explain_memory",
            "gateway_tool": "memory.explain",
            "mutation": false,
            "required_inputs": [
              "memory_id_or_visible_card_anchor"
            ],
            "requires_confirmation": false
          },
          {
            "audit_action": "correct_memory",
            "content_redacted": true,
            "data_egress": false,
            "flow_id": "correct_memory",
            "gateway_tool": "memory.correct",
            "mutation": true,
            "required_inputs": [
              "memory_id_or_visible_card_anchor",
              "corrected_content"
            ],
            "requires_confirmation": false
          },
          {
            "audit_action": "delete_memory",
            "content_redacted": true,
            "data_egress": false,
            "flow_id": "delete_memory",
            "gateway_tool": "memory.forget",
            "mutation": true,
            "required_inputs": [
              "memory_id_or_visible_card_anchor",
              "explicit_delete_confirmation"
            ],
            "requires_confirmation": true
          },
          {
            "audit_action": "export_memories",
            "content_redacted": true,
            "data_egress": true,
            "flow_id": "export_memories",
            "gateway_tool": "memory.export",
            "mutation": false,
            "required_inputs": [
              "selected_memory_ids_or_scope",
              "explicit_export_confirmation"
            ],
            "requires_confirmation": true
          }
        ],
        "audit_count": 1,
        "confidence": 0.92,
        "content_preview": "User consistently asks for minimal diffs and targeted fixes with tests after each change.",
        "content_redacted": false,
        "evidence_type": "observed_and_inferred",
        "memory_id": "mem_smallest_safe_change",
        "recall_eligible": true,
        "redaction_count": 0,
        "requires_user_confirmation": false,
        "scope": "project_specific",
        "sensitivity": "low",
        "source_count": 2,
        "source_refs": [
          "project:cortex-memory-os",
          "scene:onboarding_debug"
        ],
        "status": "active",
        "type": "preference",
        "user_visible": true
      },
      {
        "action_plans": [
          {
            "audit_action": null,
            "content_redacted": true,
            "data_egress": false,
            "flow_id": "explain_memory",
            "gateway_tool": "memory.explain",
            "mutation": false,
            "required_inputs": [
              "memory_id_or_visible_card_anchor"
            ],
            "requires_confirmation": false
          },
          {
            "audit_action": "correct_memory",
            "content_redacted": true,
            "data_egress": false,
            "flow_id": "correct_memory",
            "gateway_tool": "memory.correct",
            "mutation": true,
            "required_inputs": [
              "memory_id_or_visible_card_anchor",
              "corrected_content"
            ],
            "requires_confirmation": false
          },
          {
            "audit_action": "delete_memory",
            "content_redacted": true,
            "data_egress": false,
            "flow_id": "delete_memory",
            "gateway_tool": "memory.forget",
            "mutation": true,
            "required_inputs": [
              "memory_id_or_visible_card_anchor",
              "explicit_delete_confirmation"
            ],
            "requires_confirmation": true
          },
          {
            "audit_action": "export_memories",
            "content_redacted": true,
            "data_egress": true,
            "flow_id": "export_memories",
            "gateway_tool": "memory.export",
            "mutation": false,
            "required_inputs": [
              "selected_memory_ids_or_scope",
              "explicit_export_confirmation"
            ],
            "requires_confirmation": true
          }
        ],
        "audit_count": 0,
        "confidence": 0.65,
        "content_preview": "Uses labels like In Progress, Blocked, Review, and Done for work items.",
        "content_redacted": false,
        "evidence_type": "inferred",
        "memory_id": "mem_linear_label_tracking",
        "recall_eligible": true,
        "redaction_count": 0,
        "requires_user_confirmation": true,
        "scope": "project_specific",
        "sensitivity": "low",
        "source_count": 2,
        "source_refs": [
          "project:cortex-memory-os",
          "scene:ops_board"
        ],
        "status": "candidate",
        "type": "project",
        "user_visible": true
      },
      {
        "action_plans": [
          {
            "audit_action": null,
            "content_redacted": true,
            "data_egress": false,
            "flow_id": "explain_memory",
            "gateway_tool": "memory.explain",
            "mutation": false,
            "required_inputs": [
              "memory_id_or_visible_card_anchor"
            ],
            "requires_confirmation": false
          },
          {
            "audit_action": "correct_memory",
            "content_redacted": true,
            "data_egress": false,
            "flow_id": "correct_memory",
            "gateway_tool": "memory.correct",
            "mutation": true,
            "required_inputs": [
              "memory_id_or_visible_card_anchor",
              "corrected_content"
            ],
            "requires_confirmation": false
          },
          {
            "audit_action": "delete_memory",
            "content_redacted": true,
            "data_egress": false,
            "flow_id": "delete_memory",
            "gateway_tool": "memory.forget",
            "mutation": true,
            "required_inputs": [
              "memory_id_or_visible_card_anchor",
              "explicit_delete_confirmation"
            ],
            "requires_confirmation": true
          },
          {
            "audit_action": "export_memories",
            "content_redacted": true,
            "data_egress": true,
            "flow_id": "export_memories",
            "gateway_tool": "memory.export",
            "mutation": false,
            "required_inputs": [
              "selected_memory_ids_or_scope",
              "explicit_export_confirmation"
            ],
            "requires_confirmation": true
          }
        ],
        "audit_count": 0,
        "confidence": 0.73,
        "content_preview": "When exploring AI systems, user often prefers primary-source research, comparative synthesis, and architecture implications.",
        "content_redacted": false,
        "evidence_type": "observed_and_inferred",
        "memory_id": "mem_research_depth_candidate",
        "recall_eligible": true,
        "redaction_count": 0,
        "requires_user_confirmation": true,
        "scope": "project_specific",
        "sensitivity": "low",
        "source_count": 2,
        "source_refs": [
          "project:cortex-memory-os",
          "scene:frontier_research"
        ],
        "status": "candidate",
        "type": "procedural",
        "user_visible": true
      }
    ],
    "confirmation_required_count": 8,
    "dashboard_id": "memory_palace_dashboard_20260430T040117Z",
    "export_preview": {
      "data_egress": true,
      "exportable_count": 3,
      "gateway_tool": "memory.export",
      "omission_reasons": {},
      "omitted_count": 0,
      "omitted_memory_ids": [],
      "policy_refs": [
        "policy_memory_export_deletion_aware_v1",
        "policy_secret_pii_local_data_v1"
      ],
      "redaction_count": 0,
      "requires_confirmation": true,
      "selected_count": 3,
      "selected_memory_ids": [
        "mem_smallest_safe_change",
        "mem_auth_redirect_root_cause",
        "mem_research_depth_candidate"
      ],
      "selection_mode": "explicit_ids"
    },
    "generated_at": "2026-04-30T04:01:17.784922Z",
    "policy_refs": [
      "policy_memory_palace_dashboard_v1",
      "policy_memory_export_deletion_aware_v1",
      "policy_secret_pii_local_data_v1"
    ],
    "recall_eligible_count": 4,
    "safety_notes": [
      "Dashboard previews redact secret-like text before rendering.",
      "Deleted, revoked, and quarantined memory content stays hidden.",
      "Export previews show counts and omissions; export still requires confirmation.",
      "Action plans point to gateway tools but do not execute mutations."
    ],
    "status_counts": {
      "active": 2,
      "candidate": 2
    }
  },
  "nav_items": [
    {
      "active": true,
      "count": null,
      "item_id": "overview",
      "label": "Overview"
    },
    {
      "active": false,
      "count": 4,
      "item_id": "memory_palace",
      "label": "Memory Palace"
    },
    {
      "active": false,
      "count": 3,
      "item_id": "skill_forge",
      "label": "Skill Forge"
    },
    {
      "active": false,
      "count": null,
      "item_id": "agent_gateway",
      "label": "Agent Gateway"
    },
    {
      "active": false,
      "count": 2,
      "item_id": "audit",
      "label": "Audit"
    },
    {
      "active": false,
      "count": null,
      "item_id": "policies",
      "label": "Policies"
    }
  ],
  "policy_refs": [
    "policy_cortex_dashboard_shell_v1",
    "policy_memory_palace_dashboard_v1",
    "policy_skill_forge_candidate_list_v1"
  ],
  "safe_receipts": [
    {
      "actor": "system",
      "content_redacted": true,
      "label": "Memory created",
      "receipt_id": "receipt_memory_created",
      "state": "healthy",
      "target_ref": "mem_smallest_safe_change",
      "timestamp": "2026-04-30T04:01:17.784922Z"
    },
    {
      "actor": "system",
      "content_redacted": true,
      "label": "Export preview prepared",
      "receipt_id": "receipt_memory_export_preview",
      "state": "neutral",
      "target_ref": "export_preview_project_scope",
      "timestamp": "2026-04-30T04:01:17.784922Z"
    },
    {
      "actor": "system",
      "content_redacted": true,
      "label": "Skill candidate created",
      "receipt_id": "receipt_skill_candidate_created",
      "state": "healthy",
      "target_ref": "skill_frontend_auth_debugging_flow_v1",
      "timestamp": "2026-04-30T04:01:17.784922Z"
    },
    {
      "actor": "user",
      "content_redacted": true,
      "label": "Observation paused",
      "receipt_id": "receipt_observation_paused",
      "state": "warning",
      "target_ref": "session_20260430",
      "timestamp": "2026-04-30T04:01:17.784922Z"
    }
  ],
  "safety_notes": [
    "Static fixture contains synthetic view-model data only.",
    "No raw private memory, screenshots, databases, logs, or API responses are embedded.",
    "All action buttons update local UI receipts instead of calling gateway tools."
  ],
  "shell_id": "MEMORY-PALACE-SKILL-FORGE-UI-001",
  "skill_forge": {
    "candidate_count": 3,
    "cards": [
      {
        "action_plans": [
          {
            "action_id": "review_candidate",
            "audit_action": null,
            "content_redacted": true,
            "external_effect": false,
            "gateway_tool": "skill.review_candidate",
            "mutation": false,
            "required_inputs": [
              "skill_id"
            ],
            "requires_confirmation": false
          },
          {
            "action_id": "execute_draft",
            "audit_action": null,
            "content_redacted": true,
            "external_effect": false,
            "gateway_tool": "skill.execute_draft",
            "mutation": false,
            "required_inputs": [
              "skill_id",
              "input_summary"
            ],
            "requires_confirmation": false
          },
          {
            "action_id": "approve_draft_only",
            "audit_action": "approve_skill_candidate",
            "content_redacted": true,
            "external_effect": false,
            "gateway_tool": "skill.approve_draft_only",
            "mutation": true,
            "required_inputs": [
              "skill_id",
              "approval_ref"
            ],
            "requires_confirmation": true
          },
          {
            "action_id": "edit_steps",
            "audit_action": "edit_skill_candidate",
            "content_redacted": true,
            "external_effect": false,
            "gateway_tool": "skill.edit_candidate",
            "mutation": true,
            "required_inputs": [
              "skill_id",
              "corrected_steps",
              "approval_ref"
            ],
            "requires_confirmation": true
          },
          {
            "action_id": "need_more_data",
            "audit_action": "defer_skill_candidate",
            "content_redacted": true,
            "external_effect": false,
            "gateway_tool": "skill.need_more_data",
            "mutation": true,
            "required_inputs": [
              "skill_id",
              "reason"
            ],
            "requires_confirmation": false
          },
          {
            "action_id": "reject_candidate",
            "audit_action": "reject_skill_candidate",
            "content_redacted": true,
            "external_effect": false,
            "gateway_tool": "skill.reject_candidate",
            "mutation": true,
            "required_inputs": [
              "skill_id",
              "approval_ref"
            ],
            "requires_confirmation": true
          }
        ],
        "content_redacted": false,
        "description_preview": "Draft-only skill candidate derived from a governed document workflow. Source trust: B.",
        "execution_mode": "draft_only",
        "failure_mode_count": 3,
        "learned_from_count": 3,
        "learned_from_refs": [
          "doc_monthly_update_workflow",
          "docs/workflows/monthly-update.md",
          "ev_monthly_update_workflow"
        ],
        "maturity_level": 2,
        "name": "Prepare monthly investor update",
        "procedure_preview": [
          "Gather approved metrics and source refs",
          "Summarize shipped work and blockers"
        ],
        "procedure_step_count": 3,
        "promotion_allowed_now": false,
        "promotion_blockers": [
          "user_approval_required"
        ],
        "promotion_target_maturity": 3,
        "recommended_execution_mode": "draft_only",
        "redaction_count": 0,
        "requires_confirmation_before": [
          "promotion",
          "external_effect",
          "procedure_change",
          "source_deletion"
        ],
        "risk_level": "high",
        "skill_id": "skill_doc_doc_monthly_update_workflow_candidate_v1",
        "status": "candidate",
        "success_signal_count": 3,
        "trigger_count": 1
      },
      {
        "action_plans": [
          {
            "action_id": "review_candidate",
            "audit_action": null,
            "content_redacted": true,
            "external_effect": false,
            "gateway_tool": "skill.review_candidate",
            "mutation": false,
            "required_inputs": [
              "skill_id"
            ],
            "requires_confirmation": false
          },
          {
            "action_id": "execute_draft",
            "audit_action": null,
            "content_redacted": true,
            "external_effect": false,
            "gateway_tool": "skill.execute_draft",
            "mutation": false,
            "required_inputs": [
              "skill_id",
              "input_summary"
            ],
            "requires_confirmation": false
          },
          {
            "action_id": "approve_draft_only",
            "audit_action": "approve_skill_candidate",
            "content_redacted": true,
            "external_effect": false,
            "gateway_tool": "skill.approve_draft_only",
            "mutation": true,
            "required_inputs": [
              "skill_id",
              "approval_ref"
            ],
            "requires_confirmation": true
          },
          {
            "action_id": "edit_steps",
            "audit_action": "edit_skill_candidate",
            "content_redacted": true,
            "external_effect": false,
            "gateway_tool": "skill.edit_candidate",
            "mutation": true,
            "required_inputs": [
              "skill_id",
              "corrected_steps",
              "approval_ref"
            ],
            "requires_confirmation": true
          },
          {
            "action_id": "need_more_data",
            "audit_action": "defer_skill_candidate",
            "content_redacted": true,
            "external_effect": false,
            "gateway_tool": "skill.need_more_data",
            "mutation": true,
            "required_inputs": [
              "skill_id",
              "reason"
            ],
            "requires_confirmation": false
          },
          {
            "action_id": "reject_candidate",
            "audit_action": "reject_skill_candidate",
            "content_redacted": true,
            "external_effect": false,
            "gateway_tool": "skill.reject_candidate",
            "mutation": true,
            "required_inputs": [
              "skill_id",
              "approval_ref"
            ],
            "requires_confirmation": true
          }
        ],
        "content_redacted": false,
        "description_preview": "Reproduce auth issue, inspect logs, fix callback route, and verify outcome.",
        "execution_mode": "draft_only",
        "failure_mode_count": 2,
        "learned_from_count": 3,
        "learned_from_refs": [
          "scene_auth_1",
          "scene_auth_2",
          "scene_auth_3"
        ],
        "maturity_level": 2,
        "name": "Frontend Auth Debugging Flow",
        "procedure_preview": [
          "Reproduce the local login flow",
          "Inspect route, console, and terminal errors"
        ],
        "procedure_step_count": 4,
        "promotion_allowed_now": false,
        "promotion_blockers": [
          "user_approval_required"
        ],
        "promotion_target_maturity": 3,
        "recommended_execution_mode": "draft_only",
        "redaction_count": 0,
        "requires_confirmation_before": [
          "deployment_settings"
        ],
        "risk_level": "medium",
        "skill_id": "skill_frontend_auth_debugging_flow_v1",
        "status": "candidate",
        "success_signal_count": 2,
        "trigger_count": 2
      },
      {
        "action_plans": [
          {
            "action_id": "review_candidate",
            "audit_action": null,
            "content_redacted": true,
            "external_effect": false,
            "gateway_tool": "skill.review_candidate",
            "mutation": false,
            "required_inputs": [
              "skill_id"
            ],
            "requires_confirmation": false
          },
          {
            "action_id": "execute_draft",
            "audit_action": null,
            "content_redacted": true,
            "external_effect": false,
            "gateway_tool": "skill.execute_draft",
            "mutation": false,
            "required_inputs": [
              "skill_id",
              "input_summary"
            ],
            "requires_confirmation": false
          },
          {
            "action_id": "approve_draft_only",
            "audit_action": "approve_skill_candidate",
            "content_redacted": true,
            "external_effect": false,
            "gateway_tool": "skill.approve_draft_only",
            "mutation": true,
            "required_inputs": [
              "skill_id",
              "approval_ref"
            ],
            "requires_confirmation": true
          },
          {
            "action_id": "edit_steps",
            "audit_action": "edit_skill_candidate",
            "content_redacted": true,
            "external_effect": false,
            "gateway_tool": "skill.edit_candidate",
            "mutation": true,
            "required_inputs": [
              "skill_id",
              "corrected_steps",
              "approval_ref"
            ],
            "requires_confirmation": true
          },
          {
            "action_id": "need_more_data",
            "audit_action": "defer_skill_candidate",
            "content_redacted": true,
            "external_effect": false,
            "gateway_tool": "skill.need_more_data",
            "mutation": true,
            "required_inputs": [
              "skill_id",
              "reason"
            ],
            "requires_confirmation": false
          },
          {
            "action_id": "reject_candidate",
            "audit_action": "reject_skill_candidate",
            "content_redacted": true,
            "external_effect": false,
            "gateway_tool": "skill.reject_candidate",
            "mutation": true,
            "required_inputs": [
              "skill_id",
              "approval_ref"
            ],
            "requires_confirmation": true
          }
        ],
        "content_redacted": false,
        "description_preview": "Deep technical research, group findings, extract principles, and produce architecture implications.",
        "execution_mode": "draft_only",
        "failure_mode_count": 2,
        "learned_from_count": 3,
        "learned_from_refs": [
          "scene_research_201",
          "scene_research_218",
          "scene_research_230"
        ],
        "maturity_level": 2,
        "name": "Research Synthesis Blueprint",
        "procedure_preview": [
          "Search primary sources",
          "Separate product claims, papers, benchmarks, and risks"
        ],
        "procedure_step_count": 4,
        "promotion_allowed_now": false,
        "promotion_blockers": [
          "user_approval_required"
        ],
        "promotion_target_maturity": 3,
        "recommended_execution_mode": "draft_only",
        "redaction_count": 0,
        "requires_confirmation_before": [],
        "risk_level": "low",
        "skill_id": "skill_research_synthesis_blueprint_v1",
        "status": "candidate",
        "success_signal_count": 2,
        "trigger_count": 2
      }
    ],
    "external_effect_action_count": 0,
    "generated_at": "2026-04-30T04:01:17.784922Z",
    "list_id": "skill_forge_candidate_list_20260430T040117Z",
    "policy_refs": [
      "policy_skill_forge_candidate_list_v1"
    ],
    "review_required_count": 9,
    "risk_counts": {
      "high": 1,
      "low": 1,
      "medium": 1
    },
    "safety_notes": [
      "Candidate list cards are review surfaces, not execution permission.",
      "Procedure previews are truncated and redacted before rendering.",
      "Promotion blockers show why autonomy cannot expand yet.",
      "Action plans point to gateway tools but do not perform external effects."
    ],
    "status_counts": {
      "candidate": 3
    }
  },
  "status_strip": [
    {
      "detail": "Debugging \"onboarding bug\"",
      "item_id": "shadow_pointer",
      "label": "Shadow Pointer",
      "state": "healthy",
      "value": "Observing"
    },
    {
      "detail": "~/Codex/cortex-memory-os",
      "item_id": "active_project",
      "label": "Active Project",
      "state": "neutral",
      "value": "cortex-memory-os"
    },
    {
      "detail": "Code, tools, and docs only",
      "item_id": "consent_scope",
      "label": "Consent Scope",
      "state": "healthy",
      "value": "Project-specific"
    },
    {
      "detail": "No issue detected",
      "item_id": "safety_firewall",
      "label": "Safety Firewall",
      "state": "healthy",
      "value": "Healthy"
    }
  ],
  "version_label": "Cortex Memory OS v0.6.0"
};
