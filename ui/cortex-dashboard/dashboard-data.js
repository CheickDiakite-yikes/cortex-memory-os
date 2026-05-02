window.CORTEX_DASHBOARD_DATA = {
  "active_project": "cortex-memory-os",
  "audit_logging": true,
  "cloud_sync": false,
  "consent_onboarding": {
    "durable_private_memory_write_enabled": false,
    "external_effect_enabled": false,
    "observation_mode": "invoked",
    "plan_id": "CONSENT-FIRST-ONBOARDING-001",
    "policy_refs": [
      "policy_consent_first_onboarding_v1"
    ],
    "raw_storage_enabled": false,
    "real_capture_started": false,
    "steps": [
      {
        "allowed_effects": [
          "render_shadow_pointer"
        ],
        "blocked_effects": [
          "screen_capture",
          "memory_write"
        ],
        "label": "Show Cortex off",
        "proof": "Shadow Pointer renders off state before any observation.",
        "requires_user_action": false,
        "step_id": "show_off"
      },
      {
        "allowed_effects": [
          "synthetic_observation",
          "ephemeral_receipt"
        ],
        "blocked_effects": [
          "real_screen_capture",
          "raw_ref_retention"
        ],
        "label": "Invoke disposable observation",
        "proof": "Synthetic page event produces an ephemeral receipt.",
        "requires_user_action": true,
        "step_id": "invoke_synthetic_observation"
      },
      {
        "allowed_effects": [
          "redaction_preview"
        ],
        "blocked_effects": [
          "secret_echo",
          "raw_payload_display"
        ],
        "label": "Prove masking",
        "proof": "Secret-looking fixture is redacted before any write.",
        "requires_user_action": false,
        "step_id": "prove_masking"
      },
      {
        "allowed_effects": [
          "candidate_memory_preview"
        ],
        "blocked_effects": [
          "private_durable_memory_write"
        ],
        "label": "Create synthetic memory candidate",
        "proof": "Candidate is synthetic, scoped, and user-visible.",
        "requires_user_action": true,
        "step_id": "create_candidate_memory"
      },
      {
        "allowed_effects": [
          "candidate_delete",
          "audit_tombstone"
        ],
        "blocked_effects": [
          "silent_retention"
        ],
        "label": "Delete candidate",
        "proof": "User can remove the candidate and see the tombstone receipt.",
        "requires_user_action": true,
        "step_id": "delete_candidate_memory"
      },
      {
        "allowed_effects": [
          "audit_receipt_preview"
        ],
        "blocked_effects": [
          "external_effect"
        ],
        "label": "Show audit receipt",
        "proof": "Final receipt explains what was seen, masked, stored, and deleted.",
        "requires_user_action": false,
        "step_id": "show_audit_receipt"
      }
    ],
    "synthetic_only": true
  },
  "demo_path": {
    "blocked_effects": [
      "real_screen_capture",
      "durable_raw_screen_storage",
      "raw_private_refs",
      "secret_echo",
      "mutation",
      "export",
      "draft_execution",
      "external_effect"
    ],
    "mutation_enabled": false,
    "path_id": "DEMO-READINESS-001",
    "policy_refs": [
      "policy_demo_readiness_v1",
      "policy_cortex_dashboard_shell_v1"
    ],
    "raw_storage_enabled": false,
    "real_capture_started": false,
    "steps": [
      {
        "command": "python3 -m http.server 8792 --bind 127.0.0.1",
        "content_redacted": true,
        "label": "Dashboard",
        "proof": "Shadow Pointer, Memory Palace, Skill Forge, guardrails, receipts.",
        "safety_note": "Synthetic view model only; no live capture starts.",
        "source_refs_redacted": true,
        "state": "ready",
        "step_id": "demo_dashboard",
        "surface": "localhost static UI"
      },
      {
        "command": "uv run cortex-synthetic-capture-ladder --json",
        "content_redacted": true,
        "label": "Capture Ladder",
        "proof": "Temp raw ref expires; audited synthetic memory retrieves.",
        "safety_note": "Secret fixture is masked before raw or memory write.",
        "source_refs_redacted": true,
        "state": "ready",
        "step_id": "demo_ladder",
        "surface": "cortex-synthetic-capture-ladder"
      },
      {
        "command": null,
        "content_redacted": true,
        "label": "Encrypted Index",
        "proof": "Metadata-only search over sealed memory and HMAC terms.",
        "safety_note": "Content, source refs, graph terms, and query text stay redacted.",
        "source_refs_redacted": true,
        "state": "ready",
        "step_id": "demo_index",
        "surface": "memory.search_index"
      },
      {
        "command": null,
        "content_redacted": true,
        "label": "Context Pack",
        "proof": "Policy refs and redacted retrieval diagnostics are visible.",
        "safety_note": "No mutation, export, draft execution, or external effect is enabled.",
        "source_refs_redacted": true,
        "state": "ready",
        "step_id": "demo_context",
        "surface": "memory.get_context_pack"
      }
    ],
    "stress_command": "uv run cortex-demo-stress --iterations 12 --json",
    "stress_iterations": 12,
    "summary": "A localhost-only walkthrough that proves the brain loop using synthetic data.",
    "synthetic_only": true,
    "title": "Safe Demo Path"
  },
  "design_notes": [
    "Two primary work areas stay centered while guardrail insight panels stay compact.",
    "Skill Metrics are shown as outcome summaries, not procedure previews.",
    "Retrieval Receipts are shown as redacted context/debug metadata.",
    "Status strip exposes observation, project, consent, and firewall state.",
    "Evidence, context, firewall, and ops health use calm count-only panels.",
    "Selected details live in a sparse focus inspector instead of every queue card.",
    "Demo path shows the safe localhost narrative without adding another dense work queue.",
    "Action controls are declarative UI plans; this shell does not execute mutations.",
    "Shadow Pointer Live Receipt stays compact and policy-first.",
    "Live Shadow Pointer receipt is compact and sits above deeper review queues."
  ],
  "encrypted_at_rest": true,
  "focus_inspector": {
    "actions": [
      {
        "allowed_gateway_call": true,
        "gateway_tool": "memory.explain",
        "label": "Explain",
        "requires_confirmation": false
      },
      {
        "allowed_gateway_call": false,
        "gateway_tool": "memory.correct",
        "label": "Correct",
        "requires_confirmation": true
      },
      {
        "allowed_gateway_call": false,
        "gateway_tool": "memory.forget",
        "label": "Forget",
        "requires_confirmation": true
      }
    ],
    "content_redacted": true,
    "inspector_id": "focus_inspector_default",
    "metrics": [
      {
        "label": "Confidence",
        "state": "healthy",
        "value": "0.92"
      },
      {
        "label": "Scope",
        "state": "healthy",
        "value": "project"
      },
      {
        "label": "Action mode",
        "state": "neutral",
        "value": "preview"
      }
    ],
    "policy_refs": [
      "policy_dashboard_focus_inspector_v1",
      "policy_cortex_dashboard_shell_v1"
    ],
    "procedure_redacted": true,
    "source_refs_redacted": true,
    "state": "healthy",
    "subject_type": "memory",
    "summary": "Active project-scoped memory. Content and source refs stay governed; review actions are routed through read-only gateway receipts first.",
    "target_ref": "mem_smallest_safe_change",
    "title": "Focus Inspector"
  },
  "gateway_action_receipts": [
    {
      "action_key": "memory.explain:mem_auth_redirect_root_cause",
      "action_source": "memory_palace",
      "allowed_gateway_call": true,
      "audit_action": null,
      "audit_required": false,
      "blocked_reasons": [],
      "content_redacted": true,
      "data_egress": false,
      "external_effect": false,
      "gateway_tool": "memory.explain",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": false,
      "payload_preview": {
        "memory_id_or_visible_card_anchor": "mem_auth_redirect_root_cause"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": true,
      "receipt_id": "dash_gateway_memory_palace_explain_memory_mem_auth_redirect_root_cause",
      "required_inputs": [
        "memory_id_or_visible_card_anchor"
      ],
      "requires_confirmation": false,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "mem_auth_redirect_root_cause"
    },
    {
      "action_key": "memory.correct:mem_auth_redirect_root_cause",
      "action_source": "memory_palace",
      "allowed_gateway_call": false,
      "audit_action": "correct_memory",
      "audit_required": true,
      "blocked_reasons": [
        "tool_not_enabled_for_read_only_dashboard_slice",
        "not_read_only",
        "mutation_blocked"
      ],
      "content_redacted": true,
      "data_egress": false,
      "external_effect": false,
      "gateway_tool": "memory.correct",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": true,
      "payload_preview": {
        "corrected_content": "<redacted_user_supplied_value>",
        "memory_id_or_visible_card_anchor": "mem_auth_redirect_root_cause"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": false,
      "receipt_id": "dash_gateway_memory_palace_correct_memory_mem_auth_redirect_root_cause",
      "required_inputs": [
        "memory_id_or_visible_card_anchor",
        "corrected_content"
      ],
      "requires_confirmation": false,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "mem_auth_redirect_root_cause"
    },
    {
      "action_key": "memory.forget:mem_auth_redirect_root_cause",
      "action_source": "memory_palace",
      "allowed_gateway_call": false,
      "audit_action": "delete_memory",
      "audit_required": true,
      "blocked_reasons": [
        "tool_not_enabled_for_read_only_dashboard_slice",
        "not_read_only",
        "mutation_blocked",
        "confirmation_required"
      ],
      "content_redacted": true,
      "data_egress": false,
      "external_effect": false,
      "gateway_tool": "memory.forget",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": true,
      "payload_preview": {
        "explicit_delete_confirmation": "<required_at_confirmation>",
        "memory_id_or_visible_card_anchor": "mem_auth_redirect_root_cause"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": false,
      "receipt_id": "dash_gateway_memory_palace_delete_memory_mem_auth_redirect_root_cause",
      "required_inputs": [
        "memory_id_or_visible_card_anchor",
        "explicit_delete_confirmation"
      ],
      "requires_confirmation": true,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "mem_auth_redirect_root_cause"
    },
    {
      "action_key": "memory.export:mem_auth_redirect_root_cause",
      "action_source": "memory_palace",
      "allowed_gateway_call": false,
      "audit_action": "export_memories",
      "audit_required": true,
      "blocked_reasons": [
        "tool_not_enabled_for_read_only_dashboard_slice",
        "not_read_only",
        "data_egress_blocked",
        "confirmation_required"
      ],
      "content_redacted": true,
      "data_egress": true,
      "external_effect": false,
      "gateway_tool": "memory.export",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": false,
      "payload_preview": {
        "explicit_export_confirmation": "<required_at_confirmation>",
        "selected_memory_ids_or_scope": "mem_auth_redirect_root_cause"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": false,
      "receipt_id": "dash_gateway_memory_palace_export_memories_mem_auth_redirect_root_cause",
      "required_inputs": [
        "selected_memory_ids_or_scope",
        "explicit_export_confirmation"
      ],
      "requires_confirmation": true,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "mem_auth_redirect_root_cause"
    },
    {
      "action_key": "memory.explain:mem_smallest_safe_change",
      "action_source": "memory_palace",
      "allowed_gateway_call": true,
      "audit_action": null,
      "audit_required": false,
      "blocked_reasons": [],
      "content_redacted": true,
      "data_egress": false,
      "external_effect": false,
      "gateway_tool": "memory.explain",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": false,
      "payload_preview": {
        "memory_id_or_visible_card_anchor": "mem_smallest_safe_change"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": true,
      "receipt_id": "dash_gateway_memory_palace_explain_memory_mem_smallest_safe_change",
      "required_inputs": [
        "memory_id_or_visible_card_anchor"
      ],
      "requires_confirmation": false,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "mem_smallest_safe_change"
    },
    {
      "action_key": "memory.correct:mem_smallest_safe_change",
      "action_source": "memory_palace",
      "allowed_gateway_call": false,
      "audit_action": "correct_memory",
      "audit_required": true,
      "blocked_reasons": [
        "tool_not_enabled_for_read_only_dashboard_slice",
        "not_read_only",
        "mutation_blocked"
      ],
      "content_redacted": true,
      "data_egress": false,
      "external_effect": false,
      "gateway_tool": "memory.correct",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": true,
      "payload_preview": {
        "corrected_content": "<redacted_user_supplied_value>",
        "memory_id_or_visible_card_anchor": "mem_smallest_safe_change"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": false,
      "receipt_id": "dash_gateway_memory_palace_correct_memory_mem_smallest_safe_change",
      "required_inputs": [
        "memory_id_or_visible_card_anchor",
        "corrected_content"
      ],
      "requires_confirmation": false,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "mem_smallest_safe_change"
    },
    {
      "action_key": "memory.forget:mem_smallest_safe_change",
      "action_source": "memory_palace",
      "allowed_gateway_call": false,
      "audit_action": "delete_memory",
      "audit_required": true,
      "blocked_reasons": [
        "tool_not_enabled_for_read_only_dashboard_slice",
        "not_read_only",
        "mutation_blocked",
        "confirmation_required"
      ],
      "content_redacted": true,
      "data_egress": false,
      "external_effect": false,
      "gateway_tool": "memory.forget",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": true,
      "payload_preview": {
        "explicit_delete_confirmation": "<required_at_confirmation>",
        "memory_id_or_visible_card_anchor": "mem_smallest_safe_change"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": false,
      "receipt_id": "dash_gateway_memory_palace_delete_memory_mem_smallest_safe_change",
      "required_inputs": [
        "memory_id_or_visible_card_anchor",
        "explicit_delete_confirmation"
      ],
      "requires_confirmation": true,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "mem_smallest_safe_change"
    },
    {
      "action_key": "memory.export:mem_smallest_safe_change",
      "action_source": "memory_palace",
      "allowed_gateway_call": false,
      "audit_action": "export_memories",
      "audit_required": true,
      "blocked_reasons": [
        "tool_not_enabled_for_read_only_dashboard_slice",
        "not_read_only",
        "data_egress_blocked",
        "confirmation_required"
      ],
      "content_redacted": true,
      "data_egress": true,
      "external_effect": false,
      "gateway_tool": "memory.export",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": false,
      "payload_preview": {
        "explicit_export_confirmation": "<required_at_confirmation>",
        "selected_memory_ids_or_scope": "mem_smallest_safe_change"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": false,
      "receipt_id": "dash_gateway_memory_palace_export_memories_mem_smallest_safe_change",
      "required_inputs": [
        "selected_memory_ids_or_scope",
        "explicit_export_confirmation"
      ],
      "requires_confirmation": true,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "mem_smallest_safe_change"
    },
    {
      "action_key": "memory.explain:mem_linear_label_tracking",
      "action_source": "memory_palace",
      "allowed_gateway_call": true,
      "audit_action": null,
      "audit_required": false,
      "blocked_reasons": [],
      "content_redacted": true,
      "data_egress": false,
      "external_effect": false,
      "gateway_tool": "memory.explain",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": false,
      "payload_preview": {
        "memory_id_or_visible_card_anchor": "mem_linear_label_tracking"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": true,
      "receipt_id": "dash_gateway_memory_palace_explain_memory_mem_linear_label_tracking",
      "required_inputs": [
        "memory_id_or_visible_card_anchor"
      ],
      "requires_confirmation": false,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "mem_linear_label_tracking"
    },
    {
      "action_key": "memory.correct:mem_linear_label_tracking",
      "action_source": "memory_palace",
      "allowed_gateway_call": false,
      "audit_action": "correct_memory",
      "audit_required": true,
      "blocked_reasons": [
        "tool_not_enabled_for_read_only_dashboard_slice",
        "not_read_only",
        "mutation_blocked"
      ],
      "content_redacted": true,
      "data_egress": false,
      "external_effect": false,
      "gateway_tool": "memory.correct",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": true,
      "payload_preview": {
        "corrected_content": "<redacted_user_supplied_value>",
        "memory_id_or_visible_card_anchor": "mem_linear_label_tracking"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": false,
      "receipt_id": "dash_gateway_memory_palace_correct_memory_mem_linear_label_tracking",
      "required_inputs": [
        "memory_id_or_visible_card_anchor",
        "corrected_content"
      ],
      "requires_confirmation": false,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "mem_linear_label_tracking"
    },
    {
      "action_key": "memory.forget:mem_linear_label_tracking",
      "action_source": "memory_palace",
      "allowed_gateway_call": false,
      "audit_action": "delete_memory",
      "audit_required": true,
      "blocked_reasons": [
        "tool_not_enabled_for_read_only_dashboard_slice",
        "not_read_only",
        "mutation_blocked",
        "confirmation_required"
      ],
      "content_redacted": true,
      "data_egress": false,
      "external_effect": false,
      "gateway_tool": "memory.forget",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": true,
      "payload_preview": {
        "explicit_delete_confirmation": "<required_at_confirmation>",
        "memory_id_or_visible_card_anchor": "mem_linear_label_tracking"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": false,
      "receipt_id": "dash_gateway_memory_palace_delete_memory_mem_linear_label_tracking",
      "required_inputs": [
        "memory_id_or_visible_card_anchor",
        "explicit_delete_confirmation"
      ],
      "requires_confirmation": true,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "mem_linear_label_tracking"
    },
    {
      "action_key": "memory.export:mem_linear_label_tracking",
      "action_source": "memory_palace",
      "allowed_gateway_call": false,
      "audit_action": "export_memories",
      "audit_required": true,
      "blocked_reasons": [
        "tool_not_enabled_for_read_only_dashboard_slice",
        "not_read_only",
        "data_egress_blocked",
        "confirmation_required"
      ],
      "content_redacted": true,
      "data_egress": true,
      "external_effect": false,
      "gateway_tool": "memory.export",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": false,
      "payload_preview": {
        "explicit_export_confirmation": "<required_at_confirmation>",
        "selected_memory_ids_or_scope": "mem_linear_label_tracking"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": false,
      "receipt_id": "dash_gateway_memory_palace_export_memories_mem_linear_label_tracking",
      "required_inputs": [
        "selected_memory_ids_or_scope",
        "explicit_export_confirmation"
      ],
      "requires_confirmation": true,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "mem_linear_label_tracking"
    },
    {
      "action_key": "memory.explain:mem_research_depth_candidate",
      "action_source": "memory_palace",
      "allowed_gateway_call": true,
      "audit_action": null,
      "audit_required": false,
      "blocked_reasons": [],
      "content_redacted": true,
      "data_egress": false,
      "external_effect": false,
      "gateway_tool": "memory.explain",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": false,
      "payload_preview": {
        "memory_id_or_visible_card_anchor": "mem_research_depth_candidate"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": true,
      "receipt_id": "dash_gateway_memory_palace_explain_memory_mem_research_depth_candidate",
      "required_inputs": [
        "memory_id_or_visible_card_anchor"
      ],
      "requires_confirmation": false,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "mem_research_depth_candidate"
    },
    {
      "action_key": "memory.correct:mem_research_depth_candidate",
      "action_source": "memory_palace",
      "allowed_gateway_call": false,
      "audit_action": "correct_memory",
      "audit_required": true,
      "blocked_reasons": [
        "tool_not_enabled_for_read_only_dashboard_slice",
        "not_read_only",
        "mutation_blocked"
      ],
      "content_redacted": true,
      "data_egress": false,
      "external_effect": false,
      "gateway_tool": "memory.correct",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": true,
      "payload_preview": {
        "corrected_content": "<redacted_user_supplied_value>",
        "memory_id_or_visible_card_anchor": "mem_research_depth_candidate"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": false,
      "receipt_id": "dash_gateway_memory_palace_correct_memory_mem_research_depth_candidate",
      "required_inputs": [
        "memory_id_or_visible_card_anchor",
        "corrected_content"
      ],
      "requires_confirmation": false,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "mem_research_depth_candidate"
    },
    {
      "action_key": "memory.forget:mem_research_depth_candidate",
      "action_source": "memory_palace",
      "allowed_gateway_call": false,
      "audit_action": "delete_memory",
      "audit_required": true,
      "blocked_reasons": [
        "tool_not_enabled_for_read_only_dashboard_slice",
        "not_read_only",
        "mutation_blocked",
        "confirmation_required"
      ],
      "content_redacted": true,
      "data_egress": false,
      "external_effect": false,
      "gateway_tool": "memory.forget",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": true,
      "payload_preview": {
        "explicit_delete_confirmation": "<required_at_confirmation>",
        "memory_id_or_visible_card_anchor": "mem_research_depth_candidate"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": false,
      "receipt_id": "dash_gateway_memory_palace_delete_memory_mem_research_depth_candidate",
      "required_inputs": [
        "memory_id_or_visible_card_anchor",
        "explicit_delete_confirmation"
      ],
      "requires_confirmation": true,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "mem_research_depth_candidate"
    },
    {
      "action_key": "memory.export:mem_research_depth_candidate",
      "action_source": "memory_palace",
      "allowed_gateway_call": false,
      "audit_action": "export_memories",
      "audit_required": true,
      "blocked_reasons": [
        "tool_not_enabled_for_read_only_dashboard_slice",
        "not_read_only",
        "data_egress_blocked",
        "confirmation_required"
      ],
      "content_redacted": true,
      "data_egress": true,
      "external_effect": false,
      "gateway_tool": "memory.export",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": false,
      "payload_preview": {
        "explicit_export_confirmation": "<required_at_confirmation>",
        "selected_memory_ids_or_scope": "mem_research_depth_candidate"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": false,
      "receipt_id": "dash_gateway_memory_palace_export_memories_mem_research_depth_candidate",
      "required_inputs": [
        "selected_memory_ids_or_scope",
        "explicit_export_confirmation"
      ],
      "requires_confirmation": true,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "mem_research_depth_candidate"
    },
    {
      "action_key": "skill.review_candidate:skill_doc_doc_monthly_update_workflow_candidate_v1",
      "action_source": "skill_forge",
      "allowed_gateway_call": true,
      "audit_action": null,
      "audit_required": false,
      "blocked_reasons": [],
      "content_redacted": true,
      "data_egress": false,
      "external_effect": false,
      "gateway_tool": "skill.review_candidate",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": false,
      "payload_preview": {
        "skill_id": "skill_doc_doc_monthly_update_workflow_candidate_v1"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": true,
      "receipt_id": "dash_gateway_skill_forge_review_candidate_skill_doc_doc_monthly_update_workflow_candidate_v1",
      "required_inputs": [
        "skill_id"
      ],
      "requires_confirmation": false,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "skill_doc_doc_monthly_update_workflow_candidate_v1"
    },
    {
      "action_key": "skill.execute_draft:skill_doc_doc_monthly_update_workflow_candidate_v1",
      "action_source": "skill_forge",
      "allowed_gateway_call": false,
      "audit_action": null,
      "audit_required": false,
      "blocked_reasons": [
        "tool_not_enabled_for_read_only_dashboard_slice",
        "not_read_only"
      ],
      "content_redacted": true,
      "data_egress": false,
      "external_effect": false,
      "gateway_tool": "skill.execute_draft",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": false,
      "payload_preview": {
        "input_summary": "<redacted_user_supplied_value>",
        "skill_id": "skill_doc_doc_monthly_update_workflow_candidate_v1"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": false,
      "receipt_id": "dash_gateway_skill_forge_execute_draft_skill_doc_doc_monthly_update_workflow_candidate_v1",
      "required_inputs": [
        "skill_id",
        "input_summary"
      ],
      "requires_confirmation": false,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "skill_doc_doc_monthly_update_workflow_candidate_v1"
    },
    {
      "action_key": "skill.approve_draft_only:skill_doc_doc_monthly_update_workflow_candidate_v1",
      "action_source": "skill_forge",
      "allowed_gateway_call": false,
      "audit_action": "approve_skill_candidate",
      "audit_required": true,
      "blocked_reasons": [
        "tool_not_enabled_for_read_only_dashboard_slice",
        "not_read_only",
        "mutation_blocked",
        "confirmation_required"
      ],
      "content_redacted": true,
      "data_egress": false,
      "external_effect": false,
      "gateway_tool": "skill.approve_draft_only",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": true,
      "payload_preview": {
        "approval_ref": "<required_at_confirmation>",
        "skill_id": "skill_doc_doc_monthly_update_workflow_candidate_v1"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": false,
      "receipt_id": "dash_gateway_skill_forge_approve_draft_only_skill_doc_doc_monthly_update_workflow_candidate_v1",
      "required_inputs": [
        "skill_id",
        "approval_ref"
      ],
      "requires_confirmation": true,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "skill_doc_doc_monthly_update_workflow_candidate_v1"
    },
    {
      "action_key": "skill.edit_candidate:skill_doc_doc_monthly_update_workflow_candidate_v1",
      "action_source": "skill_forge",
      "allowed_gateway_call": false,
      "audit_action": "edit_skill_candidate",
      "audit_required": true,
      "blocked_reasons": [
        "tool_not_enabled_for_read_only_dashboard_slice",
        "not_read_only",
        "mutation_blocked",
        "confirmation_required"
      ],
      "content_redacted": true,
      "data_egress": false,
      "external_effect": false,
      "gateway_tool": "skill.edit_candidate",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": true,
      "payload_preview": {
        "approval_ref": "<required_at_confirmation>",
        "corrected_steps": "<redacted_user_supplied_value>",
        "skill_id": "skill_doc_doc_monthly_update_workflow_candidate_v1"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": false,
      "receipt_id": "dash_gateway_skill_forge_edit_steps_skill_doc_doc_monthly_update_workflow_candidate_v1",
      "required_inputs": [
        "skill_id",
        "corrected_steps",
        "approval_ref"
      ],
      "requires_confirmation": true,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "skill_doc_doc_monthly_update_workflow_candidate_v1"
    },
    {
      "action_key": "skill.need_more_data:skill_doc_doc_monthly_update_workflow_candidate_v1",
      "action_source": "skill_forge",
      "allowed_gateway_call": false,
      "audit_action": "defer_skill_candidate",
      "audit_required": true,
      "blocked_reasons": [
        "tool_not_enabled_for_read_only_dashboard_slice",
        "not_read_only",
        "mutation_blocked"
      ],
      "content_redacted": true,
      "data_egress": false,
      "external_effect": false,
      "gateway_tool": "skill.need_more_data",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": true,
      "payload_preview": {
        "reason": "<redacted_user_supplied_value>",
        "skill_id": "skill_doc_doc_monthly_update_workflow_candidate_v1"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": false,
      "receipt_id": "dash_gateway_skill_forge_need_more_data_skill_doc_doc_monthly_update_workflow_candidate_v1",
      "required_inputs": [
        "skill_id",
        "reason"
      ],
      "requires_confirmation": false,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "skill_doc_doc_monthly_update_workflow_candidate_v1"
    },
    {
      "action_key": "skill.reject_candidate:skill_doc_doc_monthly_update_workflow_candidate_v1",
      "action_source": "skill_forge",
      "allowed_gateway_call": false,
      "audit_action": "reject_skill_candidate",
      "audit_required": true,
      "blocked_reasons": [
        "tool_not_enabled_for_read_only_dashboard_slice",
        "not_read_only",
        "mutation_blocked",
        "confirmation_required"
      ],
      "content_redacted": true,
      "data_egress": false,
      "external_effect": false,
      "gateway_tool": "skill.reject_candidate",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": true,
      "payload_preview": {
        "approval_ref": "<required_at_confirmation>",
        "skill_id": "skill_doc_doc_monthly_update_workflow_candidate_v1"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": false,
      "receipt_id": "dash_gateway_skill_forge_reject_candidate_skill_doc_doc_monthly_update_workflow_candidate_v1",
      "required_inputs": [
        "skill_id",
        "approval_ref"
      ],
      "requires_confirmation": true,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "skill_doc_doc_monthly_update_workflow_candidate_v1"
    },
    {
      "action_key": "skill.review_candidate:skill_frontend_auth_debugging_flow_v1",
      "action_source": "skill_forge",
      "allowed_gateway_call": true,
      "audit_action": null,
      "audit_required": false,
      "blocked_reasons": [],
      "content_redacted": true,
      "data_egress": false,
      "external_effect": false,
      "gateway_tool": "skill.review_candidate",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": false,
      "payload_preview": {
        "skill_id": "skill_frontend_auth_debugging_flow_v1"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": true,
      "receipt_id": "dash_gateway_skill_forge_review_candidate_skill_frontend_auth_debugging_flow_v1",
      "required_inputs": [
        "skill_id"
      ],
      "requires_confirmation": false,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "skill_frontend_auth_debugging_flow_v1"
    },
    {
      "action_key": "skill.execute_draft:skill_frontend_auth_debugging_flow_v1",
      "action_source": "skill_forge",
      "allowed_gateway_call": false,
      "audit_action": null,
      "audit_required": false,
      "blocked_reasons": [
        "tool_not_enabled_for_read_only_dashboard_slice",
        "not_read_only"
      ],
      "content_redacted": true,
      "data_egress": false,
      "external_effect": false,
      "gateway_tool": "skill.execute_draft",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": false,
      "payload_preview": {
        "input_summary": "<redacted_user_supplied_value>",
        "skill_id": "skill_frontend_auth_debugging_flow_v1"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": false,
      "receipt_id": "dash_gateway_skill_forge_execute_draft_skill_frontend_auth_debugging_flow_v1",
      "required_inputs": [
        "skill_id",
        "input_summary"
      ],
      "requires_confirmation": false,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "skill_frontend_auth_debugging_flow_v1"
    },
    {
      "action_key": "skill.approve_draft_only:skill_frontend_auth_debugging_flow_v1",
      "action_source": "skill_forge",
      "allowed_gateway_call": false,
      "audit_action": "approve_skill_candidate",
      "audit_required": true,
      "blocked_reasons": [
        "tool_not_enabled_for_read_only_dashboard_slice",
        "not_read_only",
        "mutation_blocked",
        "confirmation_required"
      ],
      "content_redacted": true,
      "data_egress": false,
      "external_effect": false,
      "gateway_tool": "skill.approve_draft_only",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": true,
      "payload_preview": {
        "approval_ref": "<required_at_confirmation>",
        "skill_id": "skill_frontend_auth_debugging_flow_v1"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": false,
      "receipt_id": "dash_gateway_skill_forge_approve_draft_only_skill_frontend_auth_debugging_flow_v1",
      "required_inputs": [
        "skill_id",
        "approval_ref"
      ],
      "requires_confirmation": true,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "skill_frontend_auth_debugging_flow_v1"
    },
    {
      "action_key": "skill.edit_candidate:skill_frontend_auth_debugging_flow_v1",
      "action_source": "skill_forge",
      "allowed_gateway_call": false,
      "audit_action": "edit_skill_candidate",
      "audit_required": true,
      "blocked_reasons": [
        "tool_not_enabled_for_read_only_dashboard_slice",
        "not_read_only",
        "mutation_blocked",
        "confirmation_required"
      ],
      "content_redacted": true,
      "data_egress": false,
      "external_effect": false,
      "gateway_tool": "skill.edit_candidate",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": true,
      "payload_preview": {
        "approval_ref": "<required_at_confirmation>",
        "corrected_steps": "<redacted_user_supplied_value>",
        "skill_id": "skill_frontend_auth_debugging_flow_v1"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": false,
      "receipt_id": "dash_gateway_skill_forge_edit_steps_skill_frontend_auth_debugging_flow_v1",
      "required_inputs": [
        "skill_id",
        "corrected_steps",
        "approval_ref"
      ],
      "requires_confirmation": true,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "skill_frontend_auth_debugging_flow_v1"
    },
    {
      "action_key": "skill.need_more_data:skill_frontend_auth_debugging_flow_v1",
      "action_source": "skill_forge",
      "allowed_gateway_call": false,
      "audit_action": "defer_skill_candidate",
      "audit_required": true,
      "blocked_reasons": [
        "tool_not_enabled_for_read_only_dashboard_slice",
        "not_read_only",
        "mutation_blocked"
      ],
      "content_redacted": true,
      "data_egress": false,
      "external_effect": false,
      "gateway_tool": "skill.need_more_data",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": true,
      "payload_preview": {
        "reason": "<redacted_user_supplied_value>",
        "skill_id": "skill_frontend_auth_debugging_flow_v1"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": false,
      "receipt_id": "dash_gateway_skill_forge_need_more_data_skill_frontend_auth_debugging_flow_v1",
      "required_inputs": [
        "skill_id",
        "reason"
      ],
      "requires_confirmation": false,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "skill_frontend_auth_debugging_flow_v1"
    },
    {
      "action_key": "skill.reject_candidate:skill_frontend_auth_debugging_flow_v1",
      "action_source": "skill_forge",
      "allowed_gateway_call": false,
      "audit_action": "reject_skill_candidate",
      "audit_required": true,
      "blocked_reasons": [
        "tool_not_enabled_for_read_only_dashboard_slice",
        "not_read_only",
        "mutation_blocked",
        "confirmation_required"
      ],
      "content_redacted": true,
      "data_egress": false,
      "external_effect": false,
      "gateway_tool": "skill.reject_candidate",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": true,
      "payload_preview": {
        "approval_ref": "<required_at_confirmation>",
        "skill_id": "skill_frontend_auth_debugging_flow_v1"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": false,
      "receipt_id": "dash_gateway_skill_forge_reject_candidate_skill_frontend_auth_debugging_flow_v1",
      "required_inputs": [
        "skill_id",
        "approval_ref"
      ],
      "requires_confirmation": true,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "skill_frontend_auth_debugging_flow_v1"
    },
    {
      "action_key": "skill.review_candidate:skill_research_synthesis_blueprint_v1",
      "action_source": "skill_forge",
      "allowed_gateway_call": true,
      "audit_action": null,
      "audit_required": false,
      "blocked_reasons": [],
      "content_redacted": true,
      "data_egress": false,
      "external_effect": false,
      "gateway_tool": "skill.review_candidate",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": false,
      "payload_preview": {
        "skill_id": "skill_research_synthesis_blueprint_v1"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": true,
      "receipt_id": "dash_gateway_skill_forge_review_candidate_skill_research_synthesis_blueprint_v1",
      "required_inputs": [
        "skill_id"
      ],
      "requires_confirmation": false,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "skill_research_synthesis_blueprint_v1"
    },
    {
      "action_key": "skill.execute_draft:skill_research_synthesis_blueprint_v1",
      "action_source": "skill_forge",
      "allowed_gateway_call": false,
      "audit_action": null,
      "audit_required": false,
      "blocked_reasons": [
        "tool_not_enabled_for_read_only_dashboard_slice",
        "not_read_only"
      ],
      "content_redacted": true,
      "data_egress": false,
      "external_effect": false,
      "gateway_tool": "skill.execute_draft",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": false,
      "payload_preview": {
        "input_summary": "<redacted_user_supplied_value>",
        "skill_id": "skill_research_synthesis_blueprint_v1"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": false,
      "receipt_id": "dash_gateway_skill_forge_execute_draft_skill_research_synthesis_blueprint_v1",
      "required_inputs": [
        "skill_id",
        "input_summary"
      ],
      "requires_confirmation": false,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "skill_research_synthesis_blueprint_v1"
    },
    {
      "action_key": "skill.approve_draft_only:skill_research_synthesis_blueprint_v1",
      "action_source": "skill_forge",
      "allowed_gateway_call": false,
      "audit_action": "approve_skill_candidate",
      "audit_required": true,
      "blocked_reasons": [
        "tool_not_enabled_for_read_only_dashboard_slice",
        "not_read_only",
        "mutation_blocked",
        "confirmation_required"
      ],
      "content_redacted": true,
      "data_egress": false,
      "external_effect": false,
      "gateway_tool": "skill.approve_draft_only",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": true,
      "payload_preview": {
        "approval_ref": "<required_at_confirmation>",
        "skill_id": "skill_research_synthesis_blueprint_v1"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": false,
      "receipt_id": "dash_gateway_skill_forge_approve_draft_only_skill_research_synthesis_blueprint_v1",
      "required_inputs": [
        "skill_id",
        "approval_ref"
      ],
      "requires_confirmation": true,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "skill_research_synthesis_blueprint_v1"
    },
    {
      "action_key": "skill.edit_candidate:skill_research_synthesis_blueprint_v1",
      "action_source": "skill_forge",
      "allowed_gateway_call": false,
      "audit_action": "edit_skill_candidate",
      "audit_required": true,
      "blocked_reasons": [
        "tool_not_enabled_for_read_only_dashboard_slice",
        "not_read_only",
        "mutation_blocked",
        "confirmation_required"
      ],
      "content_redacted": true,
      "data_egress": false,
      "external_effect": false,
      "gateway_tool": "skill.edit_candidate",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": true,
      "payload_preview": {
        "approval_ref": "<required_at_confirmation>",
        "corrected_steps": "<redacted_user_supplied_value>",
        "skill_id": "skill_research_synthesis_blueprint_v1"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": false,
      "receipt_id": "dash_gateway_skill_forge_edit_steps_skill_research_synthesis_blueprint_v1",
      "required_inputs": [
        "skill_id",
        "corrected_steps",
        "approval_ref"
      ],
      "requires_confirmation": true,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "skill_research_synthesis_blueprint_v1"
    },
    {
      "action_key": "skill.need_more_data:skill_research_synthesis_blueprint_v1",
      "action_source": "skill_forge",
      "allowed_gateway_call": false,
      "audit_action": "defer_skill_candidate",
      "audit_required": true,
      "blocked_reasons": [
        "tool_not_enabled_for_read_only_dashboard_slice",
        "not_read_only",
        "mutation_blocked"
      ],
      "content_redacted": true,
      "data_egress": false,
      "external_effect": false,
      "gateway_tool": "skill.need_more_data",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": true,
      "payload_preview": {
        "reason": "<redacted_user_supplied_value>",
        "skill_id": "skill_research_synthesis_blueprint_v1"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": false,
      "receipt_id": "dash_gateway_skill_forge_need_more_data_skill_research_synthesis_blueprint_v1",
      "required_inputs": [
        "skill_id",
        "reason"
      ],
      "requires_confirmation": false,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "skill_research_synthesis_blueprint_v1"
    },
    {
      "action_key": "skill.reject_candidate:skill_research_synthesis_blueprint_v1",
      "action_source": "skill_forge",
      "allowed_gateway_call": false,
      "audit_action": "reject_skill_candidate",
      "audit_required": true,
      "blocked_reasons": [
        "tool_not_enabled_for_read_only_dashboard_slice",
        "not_read_only",
        "mutation_blocked",
        "confirmation_required"
      ],
      "content_redacted": true,
      "data_egress": false,
      "external_effect": false,
      "gateway_tool": "skill.reject_candidate",
      "generated_at": "2026-05-02T03:23:21.247269Z",
      "mutation": true,
      "payload_preview": {
        "approval_ref": "<required_at_confirmation>",
        "skill_id": "skill_research_synthesis_blueprint_v1"
      },
      "policy_refs": [
        "policy_dashboard_gateway_actions_v1"
      ],
      "read_only": false,
      "receipt_id": "dash_gateway_skill_forge_reject_candidate_skill_research_synthesis_blueprint_v1",
      "required_inputs": [
        "skill_id",
        "approval_ref"
      ],
      "requires_confirmation": true,
      "safety_notes": [
        "dashboard actions are receipt previews before gateway execution",
        "only read-only explain and review tools are callable in this slice",
        "mutation, export, draft execution, and external-effect tools remain blocked"
      ],
      "target_ref": "skill_research_synthesis_blueprint_v1"
    }
  ],
  "generated_at": "2026-05-02T03:23:21.247269Z",
  "insight_panels": [
    {
      "content_redacted": true,
      "detail": "Count-only summaries, no source refs",
      "metrics": [
        {
          "label": "Live requests",
          "state": "healthy",
          "value": "3"
        },
        {
          "label": "Warnings",
          "state": "healthy",
          "value": "0"
        },
        {
          "label": "Raw refs",
          "state": "healthy",
          "value": "0"
        }
      ],
      "panel_id": "context_pack_health",
      "policy_refs": [
        "policy_cortex_dashboard_shell_v1"
      ],
      "source_refs_redacted": true,
      "state": "healthy",
      "title": "Context Pack Health",
      "value": "Healthy"
    },
    {
      "content_redacted": true,
      "detail": "Prompt-risk and secret lanes stay pre-write",
      "metrics": [
        {
          "label": "Blocked",
          "state": "warning",
          "value": "23"
        },
        {
          "label": "Redacted",
          "state": "healthy",
          "value": "156"
        },
        {
          "label": "Quarantined",
          "state": "warning",
          "value": "8"
        }
      ],
      "panel_id": "privacy_firewall",
      "policy_refs": [
        "policy_cortex_dashboard_shell_v1"
      ],
      "source_refs_redacted": true,
      "state": "healthy",
      "title": "Privacy Firewall",
      "value": "Strict"
    },
    {
      "content_redacted": true,
      "detail": "Synthetic raw refs auto-delete; metadata remains",
      "metrics": [
        {
          "label": "Raw auto-delete",
          "state": "healthy",
          "value": "6h"
        },
        {
          "label": "Restart expiry",
          "state": "healthy",
          "value": "on"
        },
        {
          "label": "Raw payloads",
          "state": "healthy",
          "value": "0 shown"
        }
      ],
      "panel_id": "evidence_vault",
      "policy_refs": [
        "policy_cortex_dashboard_shell_v1"
      ],
      "source_refs_redacted": true,
      "state": "healthy",
      "title": "Evidence Vault",
      "value": "Raw expires"
    },
    {
      "content_redacted": true,
      "detail": "Durable memory content needs authenticated encryption",
      "metrics": [
        {
          "label": "Sensitive writes",
          "state": "healthy",
          "value": "sealed"
        },
        {
          "label": "No-op cipher",
          "state": "healthy",
          "value": "blocked"
        },
        {
          "label": "Plaintext JSON",
          "state": "healthy",
          "value": "0"
        }
      ],
      "panel_id": "encryption_default",
      "policy_refs": [
        "policy_cortex_dashboard_shell_v1",
        "policy_memory_encryption_default_v1"
      ],
      "source_refs_redacted": true,
      "state": "healthy",
      "title": "Encryption Default",
      "value": "Required"
    },
    {
      "content_redacted": true,
      "detail": "Aggregate-only benchmark status",
      "metrics": [
        {
          "label": "Suites",
          "state": "healthy",
          "value": "tracked"
        },
        {
          "label": "Raw cases",
          "state": "healthy",
          "value": "hidden"
        },
        {
          "label": "Artifacts",
          "state": "healthy",
          "value": "ignored"
        }
      ],
      "panel_id": "ops_quality",
      "policy_refs": [
        "policy_cortex_dashboard_shell_v1"
      ],
      "source_refs_redacted": true,
      "state": "healthy",
      "title": "Ops Quality",
      "value": "Passing"
    }
  ],
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
    "dashboard_id": "memory_palace_dashboard_20260502T032321Z",
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
    "generated_at": "2026-05-02T03:23:21.247269Z",
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
    "policy_skill_forge_candidate_list_v1",
    "policy_skill_metrics_dashboard_surface_v1",
    "policy_retrieval_receipts_dashboard_v1",
    "policy_dashboard_gateway_actions_v1",
    "policy_dashboard_focus_inspector_v1",
    "policy_demo_readiness_v1",
    "policy_memory_encryption_default_v1",
    "policy_shadow_pointer_state_machine_v1",
    "policy_shadow_pointer_live_receipt_v1",
    "policy_consent_first_onboarding_v1"
  ],
  "retrieval_debug": {
    "cards": [
      {
        "card_id": "retrieval_receipt_mem_research_depth_candidate_included",
        "content_included": false,
        "content_redacted": true,
        "decision": "included",
        "hostile_text_included": false,
        "memory_id": "mem_research_depth_candidate",
        "policy_refs": [
          "policy_retrieval_receipts_dashboard_v1",
          "policy_retrieval_explanation_receipts_v1",
          "RETRIEVAL-EXPLANATION-RECEIPTS-001"
        ],
        "rank": 1,
        "reason_tags": [
          "query_overlap",
          "confidence",
          "source_trust",
          "recency"
        ],
        "score": 0.7182,
        "source_ref_count": 2,
        "source_refs_redacted": true
      },
      {
        "card_id": "retrieval_receipt_mem_external_receipt_attack_evidence_only",
        "content_included": false,
        "content_redacted": true,
        "decision": "evidence_only",
        "hostile_text_included": false,
        "memory_id": "mem_external_receipt_attack",
        "policy_refs": [
          "policy_retrieval_receipts_dashboard_v1",
          "policy_retrieval_explanation_receipts_v1",
          "RETRIEVAL-EXPLANATION-RECEIPTS-001"
        ],
        "rank": null,
        "reason_tags": [
          "external_evidence_only"
        ],
        "score": 0.7868,
        "source_ref_count": 1,
        "source_refs_redacted": true
      }
    ],
    "content_redacted": true,
    "dashboard_id": "RETRIEVAL-RECEIPTS-DASHBOARD-SURFACE-001",
    "decision_counts": {
      "evidence_only": 1,
      "included": 1
    },
    "generated_at": "2026-05-02T03:23:21.247269Z",
    "hostile_text_included": false,
    "policy_refs": [
      "policy_retrieval_receipts_dashboard_v1",
      "policy_retrieval_explanation_receipts_v1"
    ],
    "receipt_count": 2,
    "safety_notes": [
      "Dashboard receipts expose decisions and reason tags only.",
      "Memory content, source refs, and hostile text remain redacted.",
      "Receipts explain retrieval; they do not change ranking or scope."
    ],
    "source_refs_redacted": true
  },
  "safe_receipts": [
    {
      "actor": "system",
      "content_redacted": true,
      "label": "Memory created",
      "receipt_id": "receipt_memory_created",
      "state": "healthy",
      "target_ref": "mem_smallest_safe_change",
      "timestamp": "2026-05-02T03:23:21.247269Z"
    },
    {
      "actor": "system",
      "content_redacted": true,
      "label": "Export preview prepared",
      "receipt_id": "receipt_memory_export_preview",
      "state": "neutral",
      "target_ref": "export_preview_project_scope",
      "timestamp": "2026-05-02T03:23:21.247269Z"
    },
    {
      "actor": "system",
      "content_redacted": true,
      "label": "Skill candidate created",
      "receipt_id": "receipt_skill_candidate_created",
      "state": "healthy",
      "target_ref": "skill_frontend_auth_debugging_flow_v1",
      "timestamp": "2026-05-02T03:23:21.247269Z"
    },
    {
      "actor": "user",
      "content_redacted": true,
      "label": "Observation paused",
      "receipt_id": "receipt_observation_paused",
      "state": "warning",
      "target_ref": "session_20260430",
      "timestamp": "2026-05-02T03:23:21.247269Z"
    }
  ],
  "safety_notes": [
    "Static fixture contains synthetic view-model data only.",
    "No raw private memory, screenshots, databases, logs, or API responses are embedded.",
    "Action buttons resolve to gateway receipts before any tool call is allowed.",
    "Skill metric cards do not include procedure text, task content, or autonomy-changing controls.",
    "Retrieval receipt cards do not include memory content, source refs, or hostile text.",
    "Shadow Pointer receipts do not include raw page payloads or raw refs."
  ],
  "shadow_pointer_live_receipt": {
    "action_required": false,
    "allowed_effects": [
      "render_pointer",
      "show_receipt"
    ],
    "blocked_effects": [
      "raw_ref_retention_without_policy",
      "trusted_instruction_promotion",
      "durable_memory_write",
      "raw_ref_retention"
    ],
    "compact_fields": {
      "memory": "not eligible",
      "policy": "ephemeral_only; derived_only",
      "raw_refs": "none",
      "trust": "external_untrusted"
    },
    "evidence_write_mode": "derived_only",
    "firewall_decision": "ephemeral_only",
    "memory_eligible": false,
    "observation_mode": "session",
    "policy_refs": [
      "policy_shadow_pointer_live_receipt_v1",
      "policy_shadow_pointer_state_machine_v1"
    ],
    "primary_line": "External page observation: Debugging auth flow",
    "raw_payload_included": false,
    "raw_ref_retained": false,
    "receipt_id": "shadow_live_observing_session",
    "state": "observing",
    "title": "Observing With Consent",
    "trust_class": "D"
  },
  "shadow_pointer_states": [
    {
      "allowed_effects": [
        "render_off_badge"
      ],
      "blocked_effects": [
        "capture",
        "memory_write"
      ],
      "compact_label": "Off",
      "icon": "power",
      "label": "Observation Off",
      "peripheral_cue": "no halo",
      "pointer_shape": "hidden",
      "policy_refs": [
        "policy_shadow_pointer_state_machine_v1"
      ],
      "state": "off",
      "tone": "neutral"
    },
    {
      "allowed_effects": [
        "render_pointer",
        "show_receipt"
      ],
      "blocked_effects": [
        "raw_ref_retention_without_policy"
      ],
      "compact_label": "Observing",
      "icon": "eye",
      "label": "Observing With Consent",
      "peripheral_cue": "steady halo",
      "pointer_shape": "soft_ring",
      "policy_refs": [
        "policy_shadow_pointer_state_machine_v1"
      ],
      "state": "observing",
      "tone": "healthy"
    },
    {
      "allowed_effects": [
        "render_masking_state",
        "show_blocked_sources"
      ],
      "blocked_effects": [
        "memory_write",
        "raw_ref_retention"
      ],
      "compact_label": "Masking",
      "icon": "shield",
      "label": "Private Masking",
      "peripheral_cue": "amber shield pulse",
      "pointer_shape": "shield_ring",
      "policy_refs": [
        "policy_shadow_pointer_state_machine_v1"
      ],
      "state": "private_masking",
      "tone": "warning"
    },
    {
      "allowed_effects": [
        "render_pointer",
        "show_workstream_label"
      ],
      "blocked_effects": [
        "durable_skill_promotion"
      ],
      "compact_label": "Segmenting",
      "icon": "route",
      "label": "Segmenting Workstream",
      "peripheral_cue": "slow dotted sweep",
      "pointer_shape": "dotted_ring",
      "policy_refs": [
        "policy_shadow_pointer_state_machine_v1"
      ],
      "state": "segmenting",
      "tone": "info"
    },
    {
      "allowed_effects": [
        "render_pointer",
        "show_memory_candidate"
      ],
      "blocked_effects": [
        "unreviewed_private_write"
      ],
      "compact_label": "Remembering",
      "icon": "archive",
      "label": "Memory Candidate",
      "peripheral_cue": "brief save glint",
      "pointer_shape": "small_badge",
      "policy_refs": [
        "policy_shadow_pointer_state_machine_v1"
      ],
      "state": "remembering",
      "tone": "info"
    },
    {
      "allowed_effects": [
        "render_pointer",
        "show_skill_candidate"
      ],
      "blocked_effects": [
        "autonomy_promotion_without_review"
      ],
      "compact_label": "Learning Skill",
      "icon": "spark",
      "label": "Skill Candidate",
      "peripheral_cue": "brief pattern pulse",
      "pointer_shape": "small_badge",
      "policy_refs": [
        "policy_shadow_pointer_state_machine_v1"
      ],
      "state": "learning_skill",
      "tone": "info"
    },
    {
      "allowed_effects": [
        "render_pointer",
        "show_context_receipt"
      ],
      "blocked_effects": [
        "raw_context_dump"
      ],
      "compact_label": "Contexting",
      "icon": "package",
      "label": "Agent Contexting",
      "peripheral_cue": "blue context pulse",
      "pointer_shape": "ring_with_dot",
      "policy_refs": [
        "policy_shadow_pointer_state_machine_v1"
      ],
      "state": "agent_contexting",
      "tone": "info"
    },
    {
      "allowed_effects": [
        "render_pointer",
        "show_action_receipt"
      ],
      "blocked_effects": [
        "privileged_action_without_confirmation"
      ],
      "compact_label": "Acting",
      "icon": "cursor",
      "label": "Agent Action Pending",
      "peripheral_cue": "red approval pulse",
      "pointer_shape": "attention_ring",
      "policy_refs": [
        "policy_shadow_pointer_state_machine_v1"
      ],
      "state": "agent_acting",
      "tone": "danger"
    },
    {
      "allowed_effects": [
        "render_pointer",
        "show_approval_receipt"
      ],
      "blocked_effects": [
        "privileged_action_without_confirmation"
      ],
      "compact_label": "Approval",
      "icon": "hand",
      "label": "Needs Approval",
      "peripheral_cue": "amber approval pulse",
      "pointer_shape": "attention_ring",
      "policy_refs": [
        "policy_shadow_pointer_state_machine_v1"
      ],
      "state": "needs_approval",
      "tone": "warning"
    },
    {
      "allowed_effects": [
        "render_pause_badge"
      ],
      "blocked_effects": [
        "capture",
        "memory_write"
      ],
      "compact_label": "Paused",
      "icon": "pause",
      "label": "Observation Paused",
      "peripheral_cue": "dimmed halo",
      "pointer_shape": "muted_ring",
      "policy_refs": [
        "policy_shadow_pointer_state_machine_v1"
      ],
      "state": "paused",
      "tone": "neutral"
    }
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
        "content_redacted": true,
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
        "procedure_preview": [],
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
        "content_redacted": true,
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
        "procedure_preview": [],
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
        "content_redacted": true,
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
        "procedure_preview": [],
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
    "generated_at": "2026-05-02T03:23:21.247269Z",
    "list_id": "skill_forge_candidate_list_20260502T032321Z",
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
  "skill_metrics": {
    "autonomy_change_allowed": false,
    "cards": [
      {
        "autonomy_change_allowed": false,
        "content_redacted": true,
        "correction_rate": 0.0,
        "execution_mode": "draft_only",
        "maturity_level": 2,
        "name": "Prepare monthly investor update",
        "outcome_counts": {
          "failed": 0,
          "partial": 0,
          "success": 0,
          "unsafe_blocked": 1,
          "user_rejected": 0
        },
        "policy_refs": [
          "policy_skill_success_metrics_v1"
        ],
        "procedure_redacted": true,
        "promotion_blockers": [
          "user_approval_required"
        ],
        "review_actions": [
          "skill.review_metrics",
          "skill.inspect_outcomes",
          "skill.review_promotion_gate"
        ],
        "review_recommendation": "safety_review_before_reuse",
        "risk_level": "high",
        "skill_id": "skill_doc_doc_monthly_update_workflow_candidate_v1",
        "success_rate": 0.0,
        "verification_ref_count": 1
      },
      {
        "autonomy_change_allowed": false,
        "content_redacted": true,
        "correction_rate": 0.5,
        "execution_mode": "draft_only",
        "maturity_level": 2,
        "name": "Frontend Auth Debugging Flow",
        "outcome_counts": {
          "failed": 0,
          "partial": 1,
          "success": 1,
          "unsafe_blocked": 0,
          "user_rejected": 0
        },
        "policy_refs": [
          "policy_skill_success_metrics_v1"
        ],
        "procedure_redacted": true,
        "promotion_blockers": [
          "user_approval_required"
        ],
        "review_actions": [
          "skill.review_metrics",
          "skill.inspect_outcomes",
          "skill.review_promotion_gate"
        ],
        "review_recommendation": "keep_draft_only_collect_more_evidence",
        "risk_level": "medium",
        "skill_id": "skill_frontend_auth_debugging_flow_v1",
        "success_rate": 0.5,
        "verification_ref_count": 2
      },
      {
        "autonomy_change_allowed": false,
        "content_redacted": true,
        "correction_rate": 0.5,
        "execution_mode": "draft_only",
        "maturity_level": 2,
        "name": "Research Synthesis Blueprint",
        "outcome_counts": {
          "failed": 0,
          "partial": 0,
          "success": 2,
          "unsafe_blocked": 0,
          "user_rejected": 0
        },
        "policy_refs": [
          "policy_skill_success_metrics_v1"
        ],
        "procedure_redacted": true,
        "promotion_blockers": [
          "user_approval_required"
        ],
        "review_actions": [
          "skill.review_metrics",
          "skill.inspect_outcomes",
          "skill.review_promotion_gate"
        ],
        "review_recommendation": "eligible_for_human_promotion_review",
        "risk_level": "low",
        "skill_id": "skill_research_synthesis_blueprint_v1",
        "success_rate": 1.0,
        "verification_ref_count": 2
      }
    ],
    "content_redacted": true,
    "dashboard_id": "SKILL-METRICS-DASHBOARD-SURFACE-001",
    "generated_at": "2026-05-02T03:23:21.247269Z",
    "policy_refs": [
      "policy_skill_metrics_dashboard_surface_v1",
      "policy_skill_success_metrics_v1"
    ],
    "procedure_text_included": false,
    "review_required_count": 3,
    "safety_notes": [
      "Metrics cards summarize outcomes without procedure text.",
      "Review recommendations do not change maturity or autonomy.",
      "Task content and verification details remain redacted."
    ],
    "skill_count": 3,
    "task_content_included": false,
    "total_run_count": 5
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
