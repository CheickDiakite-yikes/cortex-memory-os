window.CORTEX_DASHBOARD_DATA = {
  "active_project": "cortex-memory-os",
  "audit_logging": true,
  "capture_control": {
    "dashboard_panel": {
      "local_only": true,
      "mutation_enabled": false,
      "native_cursor_command": "swift run --package-path native/macos-shadow-pointer cortex-shadow-clicker --duration 30",
      "panel_id": "DASHBOARD-CAPTURE-CONTROL-001",
      "policy_ref": "policy_dashboard_capture_control_v1",
      "primary_button_label": "Turn On Cortex",
      "raw_payload_returned": false,
      "requires_confirmation": true,
      "shows_shadow_clicker_status": true,
      "starts_from_static_dashboard": false,
      "state": "ready",
      "stop_button_label": "Stop Observation"
    },
    "ephemeral_raw_ref_policy": {
      "auto_delete_at": "2026-05-03T00:31:24.156979Z",
      "durable_storage_allowed": false,
      "memory_write_allowed_from_raw": false,
      "policy_id": "REAL-CAPTURE-EPHEMERAL-RAW-REF-001",
      "policy_ref": "policy_real_capture_ephemeral_raw_ref_v1",
      "raw_ref_prefix": "tmp://cortex/raw/",
      "storage_root": "/var/folders/vv/nxhl855j0mxb1r8c6qdtfhnw0000gn/T/cortex/raw_refs",
      "ttl_seconds": 600
    },
    "generated_at": "2026-05-03T00:21:24.156979Z",
    "intent": {
      "accessibility_requested": true,
      "capture_scope": "session_only",
      "confirmation_text": "Turn on Cortex observation",
      "cursor_overlay_requested": true,
      "durable_memory_writes_requested": false,
      "external_effects_requested": false,
      "intent_id": "REAL-CAPTURE-INTENT-001",
      "policy_ref": "policy_real_capture_intent_v1",
      "screen_capture_requested": true,
      "storage_mode": "ephemeral_only",
      "user_clicked_start": true
    },
    "native_cursor_follow": {
      "accessibility_observer_started": false,
      "benchmark_id": "NATIVE-CURSOR-FOLLOW-001",
      "capture_started": false,
      "checked_at": "2026-05-03T00:21:24.156979Z",
      "config": {
        "allowed_effects": [
          "read_global_cursor_position",
          "render_shadow_clicker_overlay",
          "move_overlay_window"
        ],
        "blocked_effects": [
          "start_screen_capture",
          "start_accessibility_observer",
          "execute_click",
          "type_text",
          "read_window_contents",
          "write_memory",
          "store_raw_evidence",
          "export_payload"
        ],
        "display_only": true,
        "ignores_mouse_events": true,
        "offset_x": 14.0,
        "offset_y": -14.0,
        "overlay_diameter": 34.0,
        "policy_ref": "policy_native_cursor_follow_v1",
        "sample_hz": 30
      },
      "cursor_samples": [
        {
          "timestamp": "2026-05-03T00:21:24.156979Z",
          "x": 120.0,
          "y": 240.0
        },
        {
          "timestamp": "2026-05-03T00:21:24.156979Z",
          "x": 180.0,
          "y": 260.0
        }
      ],
      "display_only": true,
      "external_effects": [],
      "memory_write_allowed": false,
      "overlay_spec": null,
      "passed": true,
      "policy_ref": "policy_native_cursor_follow_v1",
      "raw_ref_retained": false
    },
    "passed": true,
    "readiness": {
      "accessibility_ready": false,
      "can_start_cursor_overlay": true,
      "can_start_screen_capture": false,
      "checked_at": "2026-05-03T00:21:24.156979Z",
      "durable_memory_write_allowed": false,
      "missing_permissions": [
        "screen_recording",
        "accessibility"
      ],
      "native_cursor_follow_ready": true,
      "passed": true,
      "policy_ref": "policy_real_capture_readiness_v1",
      "raw_storage_mode": "ephemeral_only",
      "readiness_id": "REAL-CAPTURE-READINESS-001",
      "screen_recording_ready": false
    },
    "sampler_plan": {
      "include_accessibility_values": false,
      "include_raw_pixels": false,
      "include_window_titles": false,
      "max_events_per_minute": 60,
      "output_shape": "count_only_receipts",
      "policy_ref": "policy_real_capture_observation_sampler_v1",
      "prompt_injection_screening_required": true,
      "sample_interval_ms": 1000,
      "sampler_id": "REAL-CAPTURE-OBSERVATION-SAMPLER-001"
    },
    "sensitive_filter": {
      "decisions": [
        {
          "allowed_for_capture": true,
          "app_name": "VS Code",
          "bundle_id": "com.microsoft.VSCode",
          "reason": "allowed_by_default_safe_fixture",
          "window_title_allowed": true
        },
        {
          "allowed_for_capture": false,
          "app_name": "Messages",
          "bundle_id": "com.apple.MobileSMS",
          "reason": "sensitive_app_blocked",
          "window_title_allowed": false
        },
        {
          "allowed_for_capture": false,
          "app_name": "1Password",
          "bundle_id": "com.1password.1password",
          "reason": "sensitive_app_blocked",
          "window_title_allowed": false
        }
      ],
      "default_deny_unknown_private_apps": true,
      "filter_id": "REAL-CAPTURE-SENSITIVE-APP-FILTER-001",
      "passed": true,
      "policy_ref": "policy_real_capture_sensitive_app_filter_v1",
      "raw_content_allowed": false
    },
    "session_plan": {
      "cursor_overlay_command": "swift run --package-path native/macos-shadow-pointer cortex-shadow-clicker --duration 30",
      "external_effects_enabled": false,
      "intent": {
        "accessibility_requested": true,
        "capture_scope": "session_only",
        "confirmation_text": "Turn on Cortex observation",
        "cursor_overlay_requested": true,
        "durable_memory_writes_requested": false,
        "external_effects_requested": false,
        "intent_id": "REAL-CAPTURE-INTENT-001",
        "policy_ref": "policy_real_capture_intent_v1",
        "screen_capture_requested": true,
        "storage_mode": "ephemeral_only",
        "user_clicked_start": true
      },
      "max_duration_minutes": 30,
      "memory_writes_enabled": false,
      "plan_id": "REAL-CAPTURE-SESSION-PLAN-001",
      "policy_ref": "policy_real_capture_session_plan_v1",
      "raw_screen_storage_enabled": false,
      "raw_storage_mode": "ephemeral_only",
      "readiness": {
        "accessibility_ready": false,
        "can_start_cursor_overlay": true,
        "can_start_screen_capture": false,
        "checked_at": "2026-05-03T00:21:24.156979Z",
        "durable_memory_write_allowed": false,
        "missing_permissions": [
          "screen_recording",
          "accessibility"
        ],
        "native_cursor_follow_ready": true,
        "passed": true,
        "policy_ref": "policy_real_capture_readiness_v1",
        "raw_storage_mode": "ephemeral_only",
        "readiness_id": "REAL-CAPTURE-READINESS-001",
        "screen_recording_ready": false
      },
      "sensitive_filter": {
        "decisions": [
          {
            "allowed_for_capture": true,
            "app_name": "VS Code",
            "bundle_id": "com.microsoft.VSCode",
            "reason": "allowed_by_default_safe_fixture",
            "window_title_allowed": true
          },
          {
            "allowed_for_capture": false,
            "app_name": "Messages",
            "bundle_id": "com.apple.MobileSMS",
            "reason": "sensitive_app_blocked",
            "window_title_allowed": false
          },
          {
            "allowed_for_capture": false,
            "app_name": "1Password",
            "bundle_id": "com.1password.1password",
            "reason": "sensitive_app_blocked",
            "window_title_allowed": false
          }
        ],
        "default_deny_unknown_private_apps": true,
        "filter_id": "REAL-CAPTURE-SENSITIVE-APP-FILTER-001",
        "passed": true,
        "policy_ref": "policy_real_capture_sensitive_app_filter_v1",
        "raw_content_allowed": false
      },
      "session_id": "capture_session_local_001",
      "state": "ready"
    },
    "start_receipt": {
      "accessibility_observer_running": false,
      "audit_action": "start_consented_capture_session",
      "confirmation_observed": true,
      "cursor_overlay_running": true,
      "memory_write_allowed": false,
      "observation_active": true,
      "policy_ref": "policy_real_capture_start_receipt_v1",
      "raw_screen_storage_enabled": false,
      "receipt_id": "REAL-CAPTURE-START-RECEIPT-001",
      "safety_notes": [
        "Shadow Clicker overlay follows the cursor system-wide.",
        "Screen capture is permission-gated and raw storage remains disabled.",
        "Durable memory writes remain disabled until separate review."
      ],
      "screen_capture_running": false,
      "session_id": "capture_session_local_001",
      "state": "running"
    },
    "stop_receipt": {
      "accessibility_observer_running": false,
      "audit_action": "stop_consented_capture_session",
      "confirmation_observed": true,
      "cursor_overlay_running": false,
      "memory_write_allowed": false,
      "observation_active": false,
      "policy_ref": "policy_real_capture_stop_receipt_v1",
      "raw_screen_storage_enabled": false,
      "receipt_id": "REAL-CAPTURE-STOP-RECEIPT-001",
      "safety_notes": [
        "Observation stopped.",
        "Ephemeral refs expire or are deleted by policy."
      ],
      "screen_capture_running": false,
      "session_id": "capture_session_local_001",
      "state": "stopped"
    }
  },
  "capture_readiness_ladder": {
    "blocked_count": 2,
    "blocked_effects": [
      "continuous_capture",
      "raw_pixel_return",
      "durable_memory_write",
      "raw_ref_retention",
      "external_effect",
      "arbitrary_command_execution"
    ],
    "can_demo_now": true,
    "can_probe_now": false,
    "can_real_capture_now": false,
    "display_only": true,
    "external_effect_enabled": false,
    "generated_at": "2026-05-03T00:21:24.156979Z",
    "ladder_id": "CAPTURE-READINESS-LADDER-001",
    "memory_write_allowed": false,
    "next_step_label": "Permission preflight",
    "planned_count": 1,
    "policy_ref": "policy_capture_readiness_ladder_v1",
    "policy_refs": [
      "policy_capture_readiness_ladder_v1",
      "policy_dashboard_capture_control_v1",
      "policy_capture_preflight_diagnostics_v1",
      "policy_native_screen_capture_probe_v1",
      "policy_raw_ref_scavenger_v1",
      "policy_real_capture_next_gate_v1",
      "policy_screen_metadata_stream_plan_v1",
      "policy_capture_control_local_bridge_v1"
    ],
    "raw_payloads_included": false,
    "raw_ref_retained": false,
    "ready_count": 6,
    "steps": [
      {
        "command": null,
        "external_effect_enabled": false,
        "label": "Bridge token",
        "memory_write_allowed": false,
        "next_action": "Keep the dashboard loaded from the local bridge.",
        "order": 1,
        "proof": "Dynamic config serves an ephemeral token.",
        "raw_payloads_included": false,
        "raw_ref_retained": false,
        "safety_note": "Token is local only and never grants external network authority.",
        "status": "ready",
        "step_id": "capture_token",
        "surface": "Local bridge"
      },
      {
        "command": null,
        "external_effect_enabled": false,
        "label": "Localhost origin",
        "memory_write_allowed": false,
        "next_action": "Use 127.0.0.1 or localhost for live testing.",
        "order": 2,
        "proof": "Bridge rejects remote clients and bad origins.",
        "raw_payloads_included": false,
        "raw_ref_retained": false,
        "safety_note": "No arbitrary command path is exposed.",
        "status": "ready",
        "step_id": "localhost_origin",
        "surface": "Local bridge"
      },
      {
        "command": "swift run --package-path native/macos-shadow-pointer cortex-shadow-clicker --duration 30",
        "external_effect_enabled": false,
        "label": "Shadow Clicker",
        "memory_write_allowed": false,
        "next_action": "Click Turn On Cortex to start the native clicker.",
        "order": 3,
        "proof": "Display-only cursor follower can run without Screen Recording.",
        "raw_payloads_included": false,
        "raw_ref_retained": false,
        "safety_note": "It follows the cursor without clicks, typing, capture, or memory writes.",
        "status": "ready",
        "step_id": "shadow_clicker",
        "surface": "Native overlay"
      },
      {
        "command": null,
        "external_effect_enabled": false,
        "label": "Permission preflight",
        "memory_write_allowed": false,
        "next_action": "Enable Screen Recording for the hosting app, then restart it.",
        "order": 4,
        "proof": "Missing permissions: screen_recording, accessibility.",
        "raw_payloads_included": false,
        "raw_ref_retained": false,
        "safety_note": "Preflight is prompt-free and starts no observers.",
        "status": "blocked",
        "step_id": "permission_preflight",
        "surface": "Dashboard"
      },
      {
        "command": null,
        "external_effect_enabled": false,
        "label": "Sensitive app filter",
        "memory_write_allowed": false,
        "next_action": "Keep password, message, mail, and keychain surfaces excluded.",
        "order": 5,
        "proof": "Known private apps are blocked before capture eligibility.",
        "raw_payloads_included": false,
        "raw_ref_retained": false,
        "safety_note": "Window titles from blocked apps are not allowed.",
        "status": "ready",
        "step_id": "sensitive_app_filter",
        "surface": "Privacy firewall"
      },
      {
        "command": null,
        "external_effect_enabled": false,
        "label": "Screen Probe",
        "memory_write_allowed": false,
        "next_action": "Enable Screen Recording for the hosting app.",
        "order": 6,
        "proof": "Skipped before frame capture: screen_recording_preflight_false.",
        "raw_payloads_included": false,
        "raw_ref_retained": false,
        "safety_note": "Probe returns metadata only; raw pixels and raw refs stay off.",
        "status": "blocked",
        "step_id": "screen_probe",
        "surface": "Native probe"
      },
      {
        "command": null,
        "external_effect_enabled": false,
        "label": "Probe receipt UX",
        "memory_write_allowed": false,
        "next_action": "Use the visible receipt to decide the next safe step.",
        "order": 7,
        "proof": "Probe UX is blocked; skip reason is screen_recording_preflight_false.",
        "raw_payloads_included": false,
        "raw_ref_retained": false,
        "safety_note": "Skipped probes are explicit receipts, not silent failures.",
        "status": "ready",
        "step_id": "probe_skip_or_ux",
        "surface": "Dashboard receipt"
      },
      {
        "command": null,
        "external_effect_enabled": false,
        "label": "Raw ref scavenger",
        "memory_write_allowed": false,
        "next_action": "Run scavenger before and after real capture experiments.",
        "order": 8,
        "proof": "Scanned 0; deleted 0.",
        "raw_payloads_included": false,
        "raw_ref_retained": false,
        "safety_note": "Scavenger deletes by metadata age and does not read payloads.",
        "status": "ready",
        "step_id": "raw_ref_scavenger",
        "surface": "Temp storage"
      },
      {
        "command": null,
        "external_effect_enabled": false,
        "label": "Metadata stream plan",
        "memory_write_allowed": false,
        "next_action": "Keep future streaming count-only until separate review.",
        "order": 9,
        "proof": "Output shape is metadata_count_receipts.",
        "raw_payloads_included": false,
        "raw_ref_retained": false,
        "safety_note": "Continuous capture, raw pixels, raw refs, and memory writes are blocked.",
        "status": "planned",
        "step_id": "metadata_stream_plan",
        "surface": "Future ScreenCaptureKit"
      },
      {
        "command": null,
        "external_effect_enabled": false,
        "label": "Receipt audit",
        "memory_write_allowed": false,
        "next_action": "Use Receipts after every live action.",
        "order": 10,
        "proof": "0 local events; exits=0.",
        "raw_payloads_included": false,
        "raw_ref_retained": false,
        "safety_note": "Audit summaries are count-only and raw-payload-free.",
        "status": "watching",
        "step_id": "receipt_audit",
        "surface": "Dashboard receipts"
      }
    ],
    "summary": "Ten local gates from button click to metadata-only capture, with raw payloads, durable memory writes, and external effects off.",
    "title": "Real Capture Readiness Ladder",
    "watching_count": 1
  },
  "clicky_ux_companion": {
    "allowed_effects": [
      "render_cursor_companion",
      "open_compact_receipt_panel"
    ],
    "blocked_effects": [
      "start_screen_capture",
      "start_microphone_capture",
      "execute_click",
      "type_text",
      "write_memory",
      "export_payload",
      "send_to_remote_proxy"
    ],
    "compact_chip_labels": [
      "State",
      "Trust",
      "Memory",
      "Raw refs"
    ],
    "content_redacted": true,
    "display_mode": "cursor_adjacent_receipt",
    "display_only": true,
    "learned_from_patterns": [
      "cursor-adjacent presence",
      "compact control panel",
      "visible spatial pointing",
      "onboarding by demonstration"
    ],
    "memory_write_allowed": false,
    "native_feed_id": "NATIVE-SHADOW-POINTER-LIVE-FEED-001",
    "next_safe_action": "Open receipt details or pause observation; no memory write happens here.",
    "panel_id": "CLICKY-UX-COMPANION-001",
    "policy_refs": [
      "policy_clicky_ux_companion_v1",
      "policy_clicky_ux_lessons_v1",
      "policy_native_shadow_pointer_live_feed_v1"
    ],
    "primary_status": "observing; 1 redacted receipt ready",
    "raw_payload_included": false,
    "raw_ref_retained": false,
    "real_screen_capture_started": false,
    "receipt_count": 1,
    "source_refs_redacted": true,
    "summary": "A small cursor-adjacent status surface shows what Cortex is doing without turning the dashboard into the live interaction.",
    "title": "Cursor Companion",
    "voice_capture_enabled": false
  },
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
  "dashboard_live_data_adapter": {
    "adapter_sources": [
      "dashboard_gateway_runtime",
      "context_pack_gateway",
      "skill_review_gateway",
      "ops_quality_reader",
      "encrypted_index_receipts",
      "native_shadow_pointer_feed",
      "durable_synthetic_receipts",
      "skill_metrics_reader",
      "retrieval_receipts_reader"
    ],
    "content_redacted": true,
    "context_pack_memory_count": 1,
    "context_pack_warning_count": 2,
    "durable_synthetic_write_count": 1,
    "encrypted_index_candidate_open_count": 1,
    "encrypted_index_search_result_count": 1,
    "gateway_blocked_count": 27,
    "gateway_executed_count": 7,
    "generated_at": "2026-05-03T00:21:24.156979Z",
    "local_only": true,
    "mutation_enabled": false,
    "native_receipt_count": 1,
    "ops_passed_cases": 2,
    "ops_total_cases": 2,
    "policy_refs": [
      "policy_dashboard_live_data_adapter_v1",
      "policy_dashboard_gateway_runtime_readonly_v1",
      "policy_dashboard_context_pack_summary_v1",
      "policy_dashboard_skill_review_summary_v1",
      "policy_dashboard_ops_quality_panel_v1",
      "policy_encrypted_index_dashboard_live_v1",
      "policy_skill_metrics_dashboard_surface_v1",
      "policy_retrieval_receipts_dashboard_v1"
    ],
    "raw_payload_returned": false,
    "raw_ref_retained": false,
    "read_only": true,
    "retrieval_receipt_count": 2,
    "skill_metric_run_count": 5,
    "skill_review_count": 3,
    "snapshot_id": "DASHBOARD-LIVE-DATA-ADAPTER-001",
    "source_refs_redacted": true,
    "write_path_enabled": false
  },
  "dashboard_live_gateway": {
    "content_redacted": true,
    "context_pack": {
      "blocked_memory_count": 0,
      "budget_estimated_prompt_tokens": 84,
      "content_redacted": true,
      "fusion_diagnostic_count": 1,
      "generated_at": "2026-05-03T00:21:24.156979Z",
      "goal": "primary source research synthesis",
      "next_step_count": 3,
      "policy_refs": [
        "policy_dashboard_context_pack_summary_v1"
      ],
      "raw_payload_returned": false,
      "relevant_memory_count": 1,
      "retrieval_receipt_count": 1,
      "source_refs_redacted": true,
      "summary_id": "DASHBOARD-CONTEXT-PACK-LIVE-SUMMARY-001",
      "warning_count": 2
    },
    "generated_at": "2026-05-03T00:21:24.156979Z",
    "ops_quality": {
      "all_passed": true,
      "artifact_name": "bench_20260501T010628Z.json",
      "artifact_payload_redacted": true,
      "content_redacted": true,
      "failed_cases": 0,
      "generated_at": "2026-05-03T00:21:24.156979Z",
      "invalid_identifier_count": 0,
      "latest_run_id": "bench_20260501T010628Z",
      "panel_id": "DASHBOARD-OPS-QUALITY-PANEL-001",
      "passed_cases": 2,
      "policy_refs": [
        "policy_dashboard_ops_quality_panel_v1"
      ],
      "raw_case_payloads_included": false,
      "suite_count": 2,
      "total_cases": 2
    },
    "panel_id": "dashboard_live_gateway_panel_v1",
    "policy_refs": [
      "policy_dashboard_gateway_runtime_readonly_v1",
      "policy_dashboard_context_pack_summary_v1",
      "policy_dashboard_skill_review_summary_v1",
      "policy_dashboard_ops_quality_panel_v1"
    ],
    "raw_payload_returned": false,
    "runtime": {
      "batch_id": "DASHBOARD-GATEWAY-RUNTIME-READONLY-001",
      "blocked_count": 27,
      "content_redacted": true,
      "data_egress_count": 4,
      "executed_count": 7,
      "external_effect_count": 0,
      "failed_count": 0,
      "generated_at": "2026-05-03T00:21:24.156979Z",
      "mutation_count": 20,
      "policy_refs": [
        "policy_dashboard_gateway_runtime_readonly_v1"
      ],
      "raw_payload_count": 0,
      "receipts": [
        {
          "action_key": "memory.explain:mem_auth_redirect_root_cause",
          "blocked_reasons": [],
          "content_redacted": true,
          "data_egress": false,
          "error_type": null,
          "external_effect": false,
          "gateway_called": true,
          "gateway_tool": "memory.explain",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": false,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_memory_palace_explain_memory_mem_auth_redirect_root_cause",
          "result_kind": "memory_explanation_summary",
          "result_summary": {
            "allowed_influence_count": 1,
            "available_action_count": 3,
            "forbidden_influence_count": 2,
            "recall_eligible": true,
            "source_ref_count": 2,
            "status": "active"
          },
          "source_refs_redacted": true,
          "status": "executed_read_only",
          "target_ref": "mem_auth_redirect_root_cause"
        },
        {
          "action_key": "memory.correct:mem_auth_redirect_root_cause",
          "blocked_reasons": [
            "tool_not_enabled_for_read_only_dashboard_slice",
            "not_read_only",
            "mutation_blocked"
          ],
          "content_redacted": true,
          "data_egress": false,
          "error_type": null,
          "external_effect": false,
          "gateway_called": false,
          "gateway_tool": "memory.correct",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": true,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_memory_palace_correct_memory_mem_auth_redirect_root_cause",
          "result_kind": "blocked_preview",
          "result_summary": {
            "blocked_reason_count": 3
          },
          "source_refs_redacted": true,
          "status": "blocked_before_gateway",
          "target_ref": "mem_auth_redirect_root_cause"
        },
        {
          "action_key": "memory.forget:mem_auth_redirect_root_cause",
          "blocked_reasons": [
            "tool_not_enabled_for_read_only_dashboard_slice",
            "not_read_only",
            "mutation_blocked",
            "confirmation_required"
          ],
          "content_redacted": true,
          "data_egress": false,
          "error_type": null,
          "external_effect": false,
          "gateway_called": false,
          "gateway_tool": "memory.forget",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": true,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_memory_palace_delete_memory_mem_auth_redirect_root_cause",
          "result_kind": "blocked_preview",
          "result_summary": {
            "blocked_reason_count": 4
          },
          "source_refs_redacted": true,
          "status": "blocked_before_gateway",
          "target_ref": "mem_auth_redirect_root_cause"
        },
        {
          "action_key": "memory.export:mem_auth_redirect_root_cause",
          "blocked_reasons": [
            "tool_not_enabled_for_read_only_dashboard_slice",
            "not_read_only",
            "data_egress_blocked",
            "confirmation_required"
          ],
          "content_redacted": true,
          "data_egress": true,
          "error_type": null,
          "external_effect": false,
          "gateway_called": false,
          "gateway_tool": "memory.export",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": false,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_memory_palace_export_memories_mem_auth_redirect_root_cause",
          "result_kind": "blocked_preview",
          "result_summary": {
            "blocked_reason_count": 4
          },
          "source_refs_redacted": true,
          "status": "blocked_before_gateway",
          "target_ref": "mem_auth_redirect_root_cause"
        },
        {
          "action_key": "memory.explain:mem_smallest_safe_change",
          "blocked_reasons": [],
          "content_redacted": true,
          "data_egress": false,
          "error_type": null,
          "external_effect": false,
          "gateway_called": true,
          "gateway_tool": "memory.explain",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": false,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_memory_palace_explain_memory_mem_smallest_safe_change",
          "result_kind": "memory_explanation_summary",
          "result_summary": {
            "allowed_influence_count": 2,
            "available_action_count": 3,
            "forbidden_influence_count": 2,
            "recall_eligible": true,
            "source_ref_count": 2,
            "status": "active"
          },
          "source_refs_redacted": true,
          "status": "executed_read_only",
          "target_ref": "mem_smallest_safe_change"
        },
        {
          "action_key": "memory.correct:mem_smallest_safe_change",
          "blocked_reasons": [
            "tool_not_enabled_for_read_only_dashboard_slice",
            "not_read_only",
            "mutation_blocked"
          ],
          "content_redacted": true,
          "data_egress": false,
          "error_type": null,
          "external_effect": false,
          "gateway_called": false,
          "gateway_tool": "memory.correct",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": true,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_memory_palace_correct_memory_mem_smallest_safe_change",
          "result_kind": "blocked_preview",
          "result_summary": {
            "blocked_reason_count": 3
          },
          "source_refs_redacted": true,
          "status": "blocked_before_gateway",
          "target_ref": "mem_smallest_safe_change"
        },
        {
          "action_key": "memory.forget:mem_smallest_safe_change",
          "blocked_reasons": [
            "tool_not_enabled_for_read_only_dashboard_slice",
            "not_read_only",
            "mutation_blocked",
            "confirmation_required"
          ],
          "content_redacted": true,
          "data_egress": false,
          "error_type": null,
          "external_effect": false,
          "gateway_called": false,
          "gateway_tool": "memory.forget",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": true,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_memory_palace_delete_memory_mem_smallest_safe_change",
          "result_kind": "blocked_preview",
          "result_summary": {
            "blocked_reason_count": 4
          },
          "source_refs_redacted": true,
          "status": "blocked_before_gateway",
          "target_ref": "mem_smallest_safe_change"
        },
        {
          "action_key": "memory.export:mem_smallest_safe_change",
          "blocked_reasons": [
            "tool_not_enabled_for_read_only_dashboard_slice",
            "not_read_only",
            "data_egress_blocked",
            "confirmation_required"
          ],
          "content_redacted": true,
          "data_egress": true,
          "error_type": null,
          "external_effect": false,
          "gateway_called": false,
          "gateway_tool": "memory.export",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": false,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_memory_palace_export_memories_mem_smallest_safe_change",
          "result_kind": "blocked_preview",
          "result_summary": {
            "blocked_reason_count": 4
          },
          "source_refs_redacted": true,
          "status": "blocked_before_gateway",
          "target_ref": "mem_smallest_safe_change"
        },
        {
          "action_key": "memory.explain:mem_linear_label_tracking",
          "blocked_reasons": [],
          "content_redacted": true,
          "data_egress": false,
          "error_type": null,
          "external_effect": false,
          "gateway_called": true,
          "gateway_tool": "memory.explain",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": false,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_memory_palace_explain_memory_mem_linear_label_tracking",
          "result_kind": "memory_explanation_summary",
          "result_summary": {
            "allowed_influence_count": 1,
            "available_action_count": 3,
            "forbidden_influence_count": 2,
            "recall_eligible": true,
            "source_ref_count": 2,
            "status": "candidate"
          },
          "source_refs_redacted": true,
          "status": "executed_read_only",
          "target_ref": "mem_linear_label_tracking"
        },
        {
          "action_key": "memory.correct:mem_linear_label_tracking",
          "blocked_reasons": [
            "tool_not_enabled_for_read_only_dashboard_slice",
            "not_read_only",
            "mutation_blocked"
          ],
          "content_redacted": true,
          "data_egress": false,
          "error_type": null,
          "external_effect": false,
          "gateway_called": false,
          "gateway_tool": "memory.correct",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": true,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_memory_palace_correct_memory_mem_linear_label_tracking",
          "result_kind": "blocked_preview",
          "result_summary": {
            "blocked_reason_count": 3
          },
          "source_refs_redacted": true,
          "status": "blocked_before_gateway",
          "target_ref": "mem_linear_label_tracking"
        },
        {
          "action_key": "memory.forget:mem_linear_label_tracking",
          "blocked_reasons": [
            "tool_not_enabled_for_read_only_dashboard_slice",
            "not_read_only",
            "mutation_blocked",
            "confirmation_required"
          ],
          "content_redacted": true,
          "data_egress": false,
          "error_type": null,
          "external_effect": false,
          "gateway_called": false,
          "gateway_tool": "memory.forget",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": true,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_memory_palace_delete_memory_mem_linear_label_tracking",
          "result_kind": "blocked_preview",
          "result_summary": {
            "blocked_reason_count": 4
          },
          "source_refs_redacted": true,
          "status": "blocked_before_gateway",
          "target_ref": "mem_linear_label_tracking"
        },
        {
          "action_key": "memory.export:mem_linear_label_tracking",
          "blocked_reasons": [
            "tool_not_enabled_for_read_only_dashboard_slice",
            "not_read_only",
            "data_egress_blocked",
            "confirmation_required"
          ],
          "content_redacted": true,
          "data_egress": true,
          "error_type": null,
          "external_effect": false,
          "gateway_called": false,
          "gateway_tool": "memory.export",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": false,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_memory_palace_export_memories_mem_linear_label_tracking",
          "result_kind": "blocked_preview",
          "result_summary": {
            "blocked_reason_count": 4
          },
          "source_refs_redacted": true,
          "status": "blocked_before_gateway",
          "target_ref": "mem_linear_label_tracking"
        },
        {
          "action_key": "memory.explain:mem_research_depth_candidate",
          "blocked_reasons": [],
          "content_redacted": true,
          "data_egress": false,
          "error_type": null,
          "external_effect": false,
          "gateway_called": true,
          "gateway_tool": "memory.explain",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": false,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_memory_palace_explain_memory_mem_research_depth_candidate",
          "result_kind": "memory_explanation_summary",
          "result_summary": {
            "allowed_influence_count": 1,
            "available_action_count": 3,
            "forbidden_influence_count": 2,
            "recall_eligible": true,
            "source_ref_count": 2,
            "status": "candidate"
          },
          "source_refs_redacted": true,
          "status": "executed_read_only",
          "target_ref": "mem_research_depth_candidate"
        },
        {
          "action_key": "memory.correct:mem_research_depth_candidate",
          "blocked_reasons": [
            "tool_not_enabled_for_read_only_dashboard_slice",
            "not_read_only",
            "mutation_blocked"
          ],
          "content_redacted": true,
          "data_egress": false,
          "error_type": null,
          "external_effect": false,
          "gateway_called": false,
          "gateway_tool": "memory.correct",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": true,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_memory_palace_correct_memory_mem_research_depth_candidate",
          "result_kind": "blocked_preview",
          "result_summary": {
            "blocked_reason_count": 3
          },
          "source_refs_redacted": true,
          "status": "blocked_before_gateway",
          "target_ref": "mem_research_depth_candidate"
        },
        {
          "action_key": "memory.forget:mem_research_depth_candidate",
          "blocked_reasons": [
            "tool_not_enabled_for_read_only_dashboard_slice",
            "not_read_only",
            "mutation_blocked",
            "confirmation_required"
          ],
          "content_redacted": true,
          "data_egress": false,
          "error_type": null,
          "external_effect": false,
          "gateway_called": false,
          "gateway_tool": "memory.forget",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": true,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_memory_palace_delete_memory_mem_research_depth_candidate",
          "result_kind": "blocked_preview",
          "result_summary": {
            "blocked_reason_count": 4
          },
          "source_refs_redacted": true,
          "status": "blocked_before_gateway",
          "target_ref": "mem_research_depth_candidate"
        },
        {
          "action_key": "memory.export:mem_research_depth_candidate",
          "blocked_reasons": [
            "tool_not_enabled_for_read_only_dashboard_slice",
            "not_read_only",
            "data_egress_blocked",
            "confirmation_required"
          ],
          "content_redacted": true,
          "data_egress": true,
          "error_type": null,
          "external_effect": false,
          "gateway_called": false,
          "gateway_tool": "memory.export",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": false,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_memory_palace_export_memories_mem_research_depth_candidate",
          "result_kind": "blocked_preview",
          "result_summary": {
            "blocked_reason_count": 4
          },
          "source_refs_redacted": true,
          "status": "blocked_before_gateway",
          "target_ref": "mem_research_depth_candidate"
        },
        {
          "action_key": "skill.review_candidate:skill_doc_doc_monthly_update_workflow_candidate_v1",
          "blocked_reasons": [],
          "content_redacted": true,
          "data_egress": false,
          "error_type": null,
          "external_effect": false,
          "gateway_called": true,
          "gateway_tool": "skill.review_candidate",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": false,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_skill_forge_review_candidate_skill_doc_doc_monthly_update_workflow_candidate_v1",
          "result_kind": "skill_candidate_review_summary",
          "result_summary": {
            "learned_from_count": 3,
            "maturity_level": 2,
            "procedure_step_count": 3,
            "requires_confirmation_count": 4,
            "risk_level": "high",
            "trigger_count": 1
          },
          "source_refs_redacted": true,
          "status": "executed_read_only",
          "target_ref": "skill_doc_doc_monthly_update_workflow_candidate_v1"
        },
        {
          "action_key": "skill.execute_draft:skill_doc_doc_monthly_update_workflow_candidate_v1",
          "blocked_reasons": [
            "tool_not_enabled_for_read_only_dashboard_slice",
            "not_read_only"
          ],
          "content_redacted": true,
          "data_egress": false,
          "error_type": null,
          "external_effect": false,
          "gateway_called": false,
          "gateway_tool": "skill.execute_draft",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": false,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_skill_forge_execute_draft_skill_doc_doc_monthly_update_workflow_candidate_v1",
          "result_kind": "blocked_preview",
          "result_summary": {
            "blocked_reason_count": 2
          },
          "source_refs_redacted": true,
          "status": "blocked_before_gateway",
          "target_ref": "skill_doc_doc_monthly_update_workflow_candidate_v1"
        },
        {
          "action_key": "skill.approve_draft_only:skill_doc_doc_monthly_update_workflow_candidate_v1",
          "blocked_reasons": [
            "tool_not_enabled_for_read_only_dashboard_slice",
            "not_read_only",
            "mutation_blocked",
            "confirmation_required"
          ],
          "content_redacted": true,
          "data_egress": false,
          "error_type": null,
          "external_effect": false,
          "gateway_called": false,
          "gateway_tool": "skill.approve_draft_only",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": true,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_skill_forge_approve_draft_only_skill_doc_doc_monthly_update_workflow_candidate_v1",
          "result_kind": "blocked_preview",
          "result_summary": {
            "blocked_reason_count": 4
          },
          "source_refs_redacted": true,
          "status": "blocked_before_gateway",
          "target_ref": "skill_doc_doc_monthly_update_workflow_candidate_v1"
        },
        {
          "action_key": "skill.edit_candidate:skill_doc_doc_monthly_update_workflow_candidate_v1",
          "blocked_reasons": [
            "tool_not_enabled_for_read_only_dashboard_slice",
            "not_read_only",
            "mutation_blocked",
            "confirmation_required"
          ],
          "content_redacted": true,
          "data_egress": false,
          "error_type": null,
          "external_effect": false,
          "gateway_called": false,
          "gateway_tool": "skill.edit_candidate",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": true,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_skill_forge_edit_steps_skill_doc_doc_monthly_update_workflow_candidate_v1",
          "result_kind": "blocked_preview",
          "result_summary": {
            "blocked_reason_count": 4
          },
          "source_refs_redacted": true,
          "status": "blocked_before_gateway",
          "target_ref": "skill_doc_doc_monthly_update_workflow_candidate_v1"
        },
        {
          "action_key": "skill.need_more_data:skill_doc_doc_monthly_update_workflow_candidate_v1",
          "blocked_reasons": [
            "tool_not_enabled_for_read_only_dashboard_slice",
            "not_read_only",
            "mutation_blocked"
          ],
          "content_redacted": true,
          "data_egress": false,
          "error_type": null,
          "external_effect": false,
          "gateway_called": false,
          "gateway_tool": "skill.need_more_data",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": true,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_skill_forge_need_more_data_skill_doc_doc_monthly_update_workflow_candidate_v1",
          "result_kind": "blocked_preview",
          "result_summary": {
            "blocked_reason_count": 3
          },
          "source_refs_redacted": true,
          "status": "blocked_before_gateway",
          "target_ref": "skill_doc_doc_monthly_update_workflow_candidate_v1"
        },
        {
          "action_key": "skill.reject_candidate:skill_doc_doc_monthly_update_workflow_candidate_v1",
          "blocked_reasons": [
            "tool_not_enabled_for_read_only_dashboard_slice",
            "not_read_only",
            "mutation_blocked",
            "confirmation_required"
          ],
          "content_redacted": true,
          "data_egress": false,
          "error_type": null,
          "external_effect": false,
          "gateway_called": false,
          "gateway_tool": "skill.reject_candidate",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": true,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_skill_forge_reject_candidate_skill_doc_doc_monthly_update_workflow_candidate_v1",
          "result_kind": "blocked_preview",
          "result_summary": {
            "blocked_reason_count": 4
          },
          "source_refs_redacted": true,
          "status": "blocked_before_gateway",
          "target_ref": "skill_doc_doc_monthly_update_workflow_candidate_v1"
        },
        {
          "action_key": "skill.review_candidate:skill_frontend_auth_debugging_flow_v1",
          "blocked_reasons": [],
          "content_redacted": true,
          "data_egress": false,
          "error_type": null,
          "external_effect": false,
          "gateway_called": true,
          "gateway_tool": "skill.review_candidate",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": false,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_skill_forge_review_candidate_skill_frontend_auth_debugging_flow_v1",
          "result_kind": "skill_candidate_review_summary",
          "result_summary": {
            "learned_from_count": 3,
            "maturity_level": 2,
            "procedure_step_count": 4,
            "requires_confirmation_count": 1,
            "risk_level": "medium",
            "trigger_count": 2
          },
          "source_refs_redacted": true,
          "status": "executed_read_only",
          "target_ref": "skill_frontend_auth_debugging_flow_v1"
        },
        {
          "action_key": "skill.execute_draft:skill_frontend_auth_debugging_flow_v1",
          "blocked_reasons": [
            "tool_not_enabled_for_read_only_dashboard_slice",
            "not_read_only"
          ],
          "content_redacted": true,
          "data_egress": false,
          "error_type": null,
          "external_effect": false,
          "gateway_called": false,
          "gateway_tool": "skill.execute_draft",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": false,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_skill_forge_execute_draft_skill_frontend_auth_debugging_flow_v1",
          "result_kind": "blocked_preview",
          "result_summary": {
            "blocked_reason_count": 2
          },
          "source_refs_redacted": true,
          "status": "blocked_before_gateway",
          "target_ref": "skill_frontend_auth_debugging_flow_v1"
        },
        {
          "action_key": "skill.approve_draft_only:skill_frontend_auth_debugging_flow_v1",
          "blocked_reasons": [
            "tool_not_enabled_for_read_only_dashboard_slice",
            "not_read_only",
            "mutation_blocked",
            "confirmation_required"
          ],
          "content_redacted": true,
          "data_egress": false,
          "error_type": null,
          "external_effect": false,
          "gateway_called": false,
          "gateway_tool": "skill.approve_draft_only",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": true,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_skill_forge_approve_draft_only_skill_frontend_auth_debugging_flow_v1",
          "result_kind": "blocked_preview",
          "result_summary": {
            "blocked_reason_count": 4
          },
          "source_refs_redacted": true,
          "status": "blocked_before_gateway",
          "target_ref": "skill_frontend_auth_debugging_flow_v1"
        },
        {
          "action_key": "skill.edit_candidate:skill_frontend_auth_debugging_flow_v1",
          "blocked_reasons": [
            "tool_not_enabled_for_read_only_dashboard_slice",
            "not_read_only",
            "mutation_blocked",
            "confirmation_required"
          ],
          "content_redacted": true,
          "data_egress": false,
          "error_type": null,
          "external_effect": false,
          "gateway_called": false,
          "gateway_tool": "skill.edit_candidate",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": true,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_skill_forge_edit_steps_skill_frontend_auth_debugging_flow_v1",
          "result_kind": "blocked_preview",
          "result_summary": {
            "blocked_reason_count": 4
          },
          "source_refs_redacted": true,
          "status": "blocked_before_gateway",
          "target_ref": "skill_frontend_auth_debugging_flow_v1"
        },
        {
          "action_key": "skill.need_more_data:skill_frontend_auth_debugging_flow_v1",
          "blocked_reasons": [
            "tool_not_enabled_for_read_only_dashboard_slice",
            "not_read_only",
            "mutation_blocked"
          ],
          "content_redacted": true,
          "data_egress": false,
          "error_type": null,
          "external_effect": false,
          "gateway_called": false,
          "gateway_tool": "skill.need_more_data",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": true,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_skill_forge_need_more_data_skill_frontend_auth_debugging_flow_v1",
          "result_kind": "blocked_preview",
          "result_summary": {
            "blocked_reason_count": 3
          },
          "source_refs_redacted": true,
          "status": "blocked_before_gateway",
          "target_ref": "skill_frontend_auth_debugging_flow_v1"
        },
        {
          "action_key": "skill.reject_candidate:skill_frontend_auth_debugging_flow_v1",
          "blocked_reasons": [
            "tool_not_enabled_for_read_only_dashboard_slice",
            "not_read_only",
            "mutation_blocked",
            "confirmation_required"
          ],
          "content_redacted": true,
          "data_egress": false,
          "error_type": null,
          "external_effect": false,
          "gateway_called": false,
          "gateway_tool": "skill.reject_candidate",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": true,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_skill_forge_reject_candidate_skill_frontend_auth_debugging_flow_v1",
          "result_kind": "blocked_preview",
          "result_summary": {
            "blocked_reason_count": 4
          },
          "source_refs_redacted": true,
          "status": "blocked_before_gateway",
          "target_ref": "skill_frontend_auth_debugging_flow_v1"
        },
        {
          "action_key": "skill.review_candidate:skill_research_synthesis_blueprint_v1",
          "blocked_reasons": [],
          "content_redacted": true,
          "data_egress": false,
          "error_type": null,
          "external_effect": false,
          "gateway_called": true,
          "gateway_tool": "skill.review_candidate",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": false,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_skill_forge_review_candidate_skill_research_synthesis_blueprint_v1",
          "result_kind": "skill_candidate_review_summary",
          "result_summary": {
            "learned_from_count": 3,
            "maturity_level": 2,
            "procedure_step_count": 4,
            "requires_confirmation_count": 0,
            "risk_level": "low",
            "trigger_count": 2
          },
          "source_refs_redacted": true,
          "status": "executed_read_only",
          "target_ref": "skill_research_synthesis_blueprint_v1"
        },
        {
          "action_key": "skill.execute_draft:skill_research_synthesis_blueprint_v1",
          "blocked_reasons": [
            "tool_not_enabled_for_read_only_dashboard_slice",
            "not_read_only"
          ],
          "content_redacted": true,
          "data_egress": false,
          "error_type": null,
          "external_effect": false,
          "gateway_called": false,
          "gateway_tool": "skill.execute_draft",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": false,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_skill_forge_execute_draft_skill_research_synthesis_blueprint_v1",
          "result_kind": "blocked_preview",
          "result_summary": {
            "blocked_reason_count": 2
          },
          "source_refs_redacted": true,
          "status": "blocked_before_gateway",
          "target_ref": "skill_research_synthesis_blueprint_v1"
        },
        {
          "action_key": "skill.approve_draft_only:skill_research_synthesis_blueprint_v1",
          "blocked_reasons": [
            "tool_not_enabled_for_read_only_dashboard_slice",
            "not_read_only",
            "mutation_blocked",
            "confirmation_required"
          ],
          "content_redacted": true,
          "data_egress": false,
          "error_type": null,
          "external_effect": false,
          "gateway_called": false,
          "gateway_tool": "skill.approve_draft_only",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": true,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_skill_forge_approve_draft_only_skill_research_synthesis_blueprint_v1",
          "result_kind": "blocked_preview",
          "result_summary": {
            "blocked_reason_count": 4
          },
          "source_refs_redacted": true,
          "status": "blocked_before_gateway",
          "target_ref": "skill_research_synthesis_blueprint_v1"
        },
        {
          "action_key": "skill.edit_candidate:skill_research_synthesis_blueprint_v1",
          "blocked_reasons": [
            "tool_not_enabled_for_read_only_dashboard_slice",
            "not_read_only",
            "mutation_blocked",
            "confirmation_required"
          ],
          "content_redacted": true,
          "data_egress": false,
          "error_type": null,
          "external_effect": false,
          "gateway_called": false,
          "gateway_tool": "skill.edit_candidate",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": true,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_skill_forge_edit_steps_skill_research_synthesis_blueprint_v1",
          "result_kind": "blocked_preview",
          "result_summary": {
            "blocked_reason_count": 4
          },
          "source_refs_redacted": true,
          "status": "blocked_before_gateway",
          "target_ref": "skill_research_synthesis_blueprint_v1"
        },
        {
          "action_key": "skill.need_more_data:skill_research_synthesis_blueprint_v1",
          "blocked_reasons": [
            "tool_not_enabled_for_read_only_dashboard_slice",
            "not_read_only",
            "mutation_blocked"
          ],
          "content_redacted": true,
          "data_egress": false,
          "error_type": null,
          "external_effect": false,
          "gateway_called": false,
          "gateway_tool": "skill.need_more_data",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": true,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_skill_forge_need_more_data_skill_research_synthesis_blueprint_v1",
          "result_kind": "blocked_preview",
          "result_summary": {
            "blocked_reason_count": 3
          },
          "source_refs_redacted": true,
          "status": "blocked_before_gateway",
          "target_ref": "skill_research_synthesis_blueprint_v1"
        },
        {
          "action_key": "skill.reject_candidate:skill_research_synthesis_blueprint_v1",
          "blocked_reasons": [
            "tool_not_enabled_for_read_only_dashboard_slice",
            "not_read_only",
            "mutation_blocked",
            "confirmation_required"
          ],
          "content_redacted": true,
          "data_egress": false,
          "error_type": null,
          "external_effect": false,
          "gateway_called": false,
          "gateway_tool": "skill.reject_candidate",
          "generated_at": "2026-05-03T00:21:24.156979Z",
          "mutation": true,
          "policy_refs": [
            "policy_dashboard_gateway_runtime_readonly_v1"
          ],
          "procedure_redacted": true,
          "raw_payload_returned": false,
          "receipt_id": "runtime_dash_gateway_skill_forge_reject_candidate_skill_research_synthesis_blueprint_v1",
          "result_kind": "blocked_preview",
          "result_summary": {
            "blocked_reason_count": 4
          },
          "source_refs_redacted": true,
          "status": "blocked_before_gateway",
          "target_ref": "skill_research_synthesis_blueprint_v1"
        }
      ]
    },
    "skill_reviews": [
      {
        "content_redacted": true,
        "execution_mode": "draft_only",
        "external_effect": false,
        "failure_mode_count": 3,
        "generated_at": "2026-05-03T00:21:24.156979Z",
        "learned_from_count": 3,
        "maturity_level": 2,
        "mutation": false,
        "policy_refs": [
          "policy_dashboard_skill_review_summary_v1"
        ],
        "procedure_redacted": true,
        "procedure_step_count": 3,
        "requires_confirmation_count": 4,
        "risk_level": "high",
        "skill_id": "skill_doc_doc_monthly_update_workflow_candidate_v1",
        "success_signal_count": 3,
        "summary_id": "DASHBOARD-SKILL-REVIEW-LIVE-SUMMARY-001",
        "trigger_count": 1
      },
      {
        "content_redacted": true,
        "execution_mode": "draft_only",
        "external_effect": false,
        "failure_mode_count": 2,
        "generated_at": "2026-05-03T00:21:24.156979Z",
        "learned_from_count": 3,
        "maturity_level": 2,
        "mutation": false,
        "policy_refs": [
          "policy_dashboard_skill_review_summary_v1"
        ],
        "procedure_redacted": true,
        "procedure_step_count": 4,
        "requires_confirmation_count": 1,
        "risk_level": "medium",
        "skill_id": "skill_frontend_auth_debugging_flow_v1",
        "success_signal_count": 2,
        "summary_id": "DASHBOARD-SKILL-REVIEW-LIVE-SUMMARY-001",
        "trigger_count": 2
      },
      {
        "content_redacted": true,
        "execution_mode": "draft_only",
        "external_effect": false,
        "failure_mode_count": 2,
        "generated_at": "2026-05-03T00:21:24.156979Z",
        "learned_from_count": 3,
        "maturity_level": 2,
        "mutation": false,
        "policy_refs": [
          "policy_dashboard_skill_review_summary_v1"
        ],
        "procedure_redacted": true,
        "procedure_step_count": 4,
        "requires_confirmation_count": 0,
        "risk_level": "low",
        "skill_id": "skill_research_synthesis_blueprint_v1",
        "success_signal_count": 2,
        "summary_id": "DASHBOARD-SKILL-REVIEW-LIVE-SUMMARY-001",
        "trigger_count": 2
      }
    ]
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
    "Live Shadow Pointer receipt is compact and sits above deeper review queues.",
    "Clicky-inspired UX keeps live presence cursor-adjacent and makes the dashboard a review space.",
    "Encrypted index receipts show counts and policy state instead of raw memory or query text.",
    "Live dashboard panels refresh from local read-only adapter receipts, not embedded raw payloads.",
    "Capture control shows an honest button path for the native Shadow Clicker without claiming static HTML can launch it.",
    "Capture readiness ladder turns the next ten real-capture gates into one readable checklist."
  ],
  "durable_synthetic_memory_receipt": {
    "audit_event_id": "audit_durable_synthetic_memory_20260503T002124Z",
    "audit_human_visible": true,
    "audit_written": true,
    "content_redacted": true,
    "db_plaintext_leak_count": 0,
    "durable_private_memory_written": false,
    "durable_synthetic_memory_written": true,
    "encrypted_store_used": true,
    "generated_at": "2026-05-03T00:21:24.156979Z",
    "graph_write_receipt": {
      "content_redacted": true,
      "edge_id": "edge_durable_synthetic_receipt_debug",
      "graph_terms_redacted": true,
      "graph_token_digest_count": 4,
      "payload_sha256": "440ef0720d02d98ce31666d29d26daefc785d992cecc6a2ea0701d93f484e512",
      "policy_refs": [
        "policy_unified_encrypted_graph_index_v1"
      ],
      "related_memory_count": 1,
      "sealed_byte_count": 311,
      "source_refs_redacted": true,
      "stored_at": "2026-05-03T00:21:24.156979Z"
    },
    "index_write_receipt": {
      "allowed_effects": [
        "write_sealed_memory_payload",
        "write_redacted_hmac_index_terms"
      ],
      "blocked_effects": [
        "store_plaintext_memory_content",
        "store_plaintext_source_refs",
        "store_plaintext_graph_terms"
      ],
      "content_redacted": true,
      "memory_id": "mem_durable_synthetic_receipt_debug",
      "policy_refs": [
        "policy_unified_encrypted_graph_index_v1",
        "policy_memory_encryption_default_v1"
      ],
      "source_ref_count": 2,
      "source_refs_redacted": true,
      "storage_receipt": {
        "cipher_name": "synthetic-receipt-aead-test-only",
        "content_redacted": true,
        "decision": {
          "allowed": true,
          "allowed_effects": [
            "write_sealed_memory_payload",
            "store_redacted_index_metadata",
            "open_payload_after_authorized_read"
          ],
          "blocked_effects": [
            "write_plaintext_memory_payload",
            "store_raw_source_refs_outside_ciphertext",
            "export_unencrypted_memory"
          ],
          "cipher_allowed_for_runtime": true,
          "cipher_authenticated": true,
          "cipher_name": "synthetic-receipt-aead-test-only",
          "content_redacted": true,
          "durable_write": true,
          "influence_level": 1,
          "memory_id": "mem_durable_synthetic_receipt_debug",
          "policy_refs": [
            "policy_memory_encryption_default_v1"
          ],
          "reason": "durable_memory_authenticated_encryption_satisfied",
          "requires_authenticated_encryption": true,
          "scope": "project_specific",
          "sensitive_durable": true,
          "sensitivity": "private_work",
          "source_refs_redacted": true,
          "status": "active"
        },
        "memory_id": "mem_durable_synthetic_receipt_debug",
        "payload_sha256": "96ac4bfe50c1624495fe080e52a1ca9dd9a773973a356baadc9a90f187d8b047",
        "policy_refs": [
          "policy_memory_encryption_default_v1"
        ],
        "sealed_byte_count": 795,
        "source_refs_redacted": true,
        "stored_at": "2026-05-03T00:21:24.156979Z"
      },
      "stored_at": "2026-05-03T00:21:24.156979Z",
      "token_digest_count": 22,
      "token_text_redacted": true
    },
    "local_test_db_used": true,
    "memory_id": "mem_durable_synthetic_receipt_debug",
    "policy_ref": "policy_durable_synthetic_memory_receipts_v1",
    "policy_refs": [
      "policy_durable_synthetic_memory_receipts_v1",
      "policy_synthetic_capture_ladder_v1",
      "policy_memory_encryption_default_v1",
      "policy_unified_encrypted_graph_index_v1",
      "policy_key_management_plan_v1"
    ],
    "prohibited_leak_count": 0,
    "query_redacted": true,
    "raw_payload_included": false,
    "raw_ref_retained": false,
    "real_screen_capture_started": false,
    "receipt_id": "durable_synthetic_receipt_20260503T002124Z",
    "search_receipt": {
      "candidate_open_count": 1,
      "considered_index_rows": 1,
      "content_redacted": true,
      "policy_refs": [
        "policy_unified_encrypted_graph_index_v1"
      ],
      "query_digest_count": 6,
      "query_redacted": true,
      "result_count": 1,
      "source_refs_redacted": true,
      "token_text_redacted": true
    },
    "source_refs_redacted": true,
    "synthetic_only": true,
    "token_text_redacted": true
  },
  "encrypted_at_rest": true,
  "encrypted_index_panel": {
    "candidate_open_count": 1,
    "content_redacted": true,
    "gateway_tools": [
      "memory.search_index",
      "memory.get_context_pack"
    ],
    "graph_receipt_count": 1,
    "graph_token_digest_count": 4,
    "key_material_visible": false,
    "key_plan_id": "KEY-MANAGEMENT-PLAN-001",
    "panel_id": "ENCRYPTED-INDEX-DASHBOARD-LIVE-001",
    "policy_refs": [
      "policy_encrypted_index_dashboard_live_v1",
      "policy_unified_encrypted_graph_index_v1",
      "policy_memory_encryption_default_v1",
      "policy_key_management_plan_v1"
    ],
    "query_redacted": true,
    "raw_private_data_retained": false,
    "search_result_count": 1,
    "source_ref_count": 2,
    "source_refs_redacted": true,
    "summary": "Metadata-only encrypted index search is available; query text, token text, source refs, memory content, and key material stay hidden.",
    "title": "Encrypted Index Receipts",
    "token_digest_count": 22,
    "token_text_redacted": true,
    "write_receipt_count": 1
  },
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "generated_at": "2026-05-03T00:21:24.156979Z",
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
  "generated_at": "2026-05-03T00:21:24.156979Z",
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
  "key_management_plan": {
    "audit_events": [
      "key.created",
      "key.activated",
      "key.rotated",
      "key.revoked",
      "key.deleted",
      "payload.resealed"
    ],
    "default_rotation_days": 90,
    "deletion_controls": [
      "delete key ref after retention and user-confirmed forget flow",
      "retain redacted tombstone audit without decryptable payload"
    ],
    "key_boundaries": [
      {
        "allowed_effects": [
          "store_wrapped_key_metadata",
          "seal_payloads_with_active_key_version",
          "audit_key_version_use"
        ],
        "blocked_effects": [
          "store_raw_key_material",
          "commit_key_material",
          "reuse_key_across_material_classes",
          "export_unwrapped_key"
        ],
        "key_class": "memory_payload",
        "key_id_ref": "keyref_memory_payload_active",
        "key_material_included": false,
        "production_required": true,
        "purpose": "Seal durable MemoryRecord payload JSON.",
        "rotation_days": 90,
        "storage_backend": "macos_keychain_secure_enclave_when_available",
        "wrapped_by": "macos_keychain_application_password_item"
      },
      {
        "allowed_effects": [
          "store_wrapped_key_metadata",
          "seal_payloads_with_active_key_version",
          "audit_key_version_use"
        ],
        "blocked_effects": [
          "store_raw_key_material",
          "commit_key_material",
          "reuse_key_across_material_classes",
          "export_unwrapped_key"
        ],
        "key_class": "graph_edge_payload",
        "key_id_ref": "keyref_graph_edge_payload_active",
        "key_material_included": false,
        "production_required": true,
        "purpose": "Seal temporal graph edge payload JSON.",
        "rotation_days": 90,
        "storage_backend": "macos_keychain_secure_enclave_when_available",
        "wrapped_by": "macos_keychain_application_password_item"
      },
      {
        "allowed_effects": [
          "store_wrapped_key_metadata",
          "seal_payloads_with_active_key_version",
          "audit_key_version_use"
        ],
        "blocked_effects": [
          "store_raw_key_material",
          "commit_key_material",
          "reuse_key_across_material_classes",
          "export_unwrapped_key"
        ],
        "key_class": "hmac_index",
        "key_id_ref": "keyref_hmac_index_terms_active",
        "key_material_included": false,
        "production_required": true,
        "purpose": "Derive redacted token digests for memory and graph lookup.",
        "rotation_days": 90,
        "storage_backend": "macos_keychain_secure_enclave_when_available",
        "wrapped_by": "macos_keychain_application_password_item"
      },
      {
        "allowed_effects": [
          "store_wrapped_key_metadata",
          "seal_payloads_with_active_key_version",
          "audit_key_version_use"
        ],
        "blocked_effects": [
          "store_raw_key_material",
          "commit_key_material",
          "reuse_key_across_material_classes",
          "export_unwrapped_key"
        ],
        "key_class": "evidence_blob",
        "key_id_ref": "keyref_evidence_blob_active",
        "key_material_included": false,
        "production_required": true,
        "purpose": "Seal short-retention raw evidence blobs before expiry.",
        "rotation_days": 90,
        "storage_backend": "macos_keychain_secure_enclave_when_available",
        "wrapped_by": "macos_keychain_application_password_item"
      }
    ],
    "lifecycle_steps": [
      {
        "allowed_effects": [
          "create_key_ref",
          "write_key_audit"
        ],
        "blocked_effects": [
          "return_unwrapped_key_material",
          "write_key_to_env_file"
        ],
        "label": "Generate wrapped key version",
        "proof": "New key material is generated inside the native key boundary and only a key ref is returned.",
        "required_for": [
          "memory_payload",
          "graph_edge_payload",
          "hmac_index",
          "evidence_blob"
        ],
        "step_id": "generate_wrapped_key"
      },
      {
        "allowed_effects": [
          "mark_active_key_ref",
          "seal_new_payloads"
        ],
        "blocked_effects": [
          "rewrite_without_audit"
        ],
        "label": "Activate key version",
        "proof": "New writes use the active key ref while old versions remain readable until rotation closes.",
        "required_for": [
          "memory_payload",
          "graph_edge_payload",
          "hmac_index",
          "evidence_blob"
        ],
        "step_id": "activate_key_version"
      },
      {
        "allowed_effects": [
          "reseal_payloads",
          "write_rotation_audit"
        ],
        "blocked_effects": [
          "reuse_old_index_key",
          "drop_unmigrated_payloads"
        ],
        "label": "Rotate key version",
        "proof": "Rotation creates a new key ref, reseals eligible payloads, and records old/new refs.",
        "required_for": [
          "memory_payload",
          "graph_edge_payload",
          "hmac_index",
          "evidence_blob"
        ],
        "step_id": "rotate_key_version"
      },
      {
        "allowed_effects": [
          "block_new_writes",
          "write_revocation_audit"
        ],
        "blocked_effects": [
          "silent_reactivation"
        ],
        "label": "Revoke key version",
        "proof": "Revoked keys stop new writes and require explicit recovery or delete flow.",
        "required_for": [
          "memory_payload",
          "graph_edge_payload",
          "hmac_index",
          "evidence_blob"
        ],
        "step_id": "revoke_key_version"
      },
      {
        "allowed_effects": [
          "destroy_wrapped_key",
          "write_delete_audit"
        ],
        "blocked_effects": [
          "retain_unwrapped_key_backup",
          "skip_user_visible_receipt"
        ],
        "label": "Delete key version",
        "proof": "Deleting a key version makes associated unrecovered payloads cryptographically unreadable.",
        "required_for": [
          "memory_payload",
          "graph_edge_payload",
          "hmac_index",
          "evidence_blob"
        ],
        "step_id": "delete_key_version"
      }
    ],
    "local_dev_uses_test_keys": true,
    "plan_id": "KEY-MANAGEMENT-PLAN-001",
    "policy_refs": [
      "policy_key_management_plan_v1",
      "policy_memory_encryption_default_v1",
      "policy_unified_encrypted_graph_index_v1",
      "policy_evidence_vault_encryption_v1"
    ],
    "production_allows_noop_cipher": false,
    "raw_key_material_included": false,
    "recovery_controls": [
      "recovery requires user-visible local backup policy",
      "payload recovery never exports unwrapped key material"
    ],
    "runtime_boundary": "local_engine_with_native_keychain"
  },
  "live_backbone_panel": {
    "blocked_effects": [
      "real_screen_capture",
      "durable_private_memory_write",
      "raw_ref_retention",
      "external_effect"
    ],
    "content_redacted": true,
    "durable_receipt_id": "durable_synthetic_receipt_20260503T002124Z",
    "encrypted_index_panel_id": "ENCRYPTED-INDEX-DASHBOARD-LIVE-001",
    "key_material_visible": false,
    "key_plan_id": "KEY-MANAGEMENT-PLAN-001",
    "native_feed_id": "NATIVE-SHADOW-POINTER-LIVE-FEED-001",
    "panel_id": "DASHBOARD-LIVE-BACKBONE-001",
    "policy_refs": [
      "policy_dashboard_live_backbone_v1",
      "policy_key_management_plan_v1",
      "policy_encrypted_index_dashboard_live_v1",
      "policy_native_shadow_pointer_live_feed_v1",
      "policy_durable_synthetic_memory_receipts_v1"
    ],
    "raw_private_data_retained": false,
    "ready_components": [
      "key_management_plan",
      "encrypted_index_panel",
      "native_live_feed",
      "durable_synthetic_receipt"
    ],
    "source_refs_redacted": true,
    "summary": "Key lifecycle, encrypted index receipts, native overlay feed, and synthetic durable writes are wired as redacted receipts.",
    "title": "Live Receipt Backbone"
  },
  "live_dashboard_receipts": {
    "content_redacted": true,
    "encrypted_index_search_result_count": 1,
    "gateway_blocked_count": 27,
    "gateway_executed_count": 7,
    "generated_at": "2026-05-03T00:21:24.156979Z",
    "mutation_enabled": false,
    "ops_passed_cases": 2,
    "panel_id": "LIVE-DASHBOARD-RECEIPTS-001",
    "policy_refs": [
      "policy_live_dashboard_receipts_v1",
      "policy_dashboard_live_data_adapter_v1"
    ],
    "raw_payload_returned": false,
    "refresh_mode": "read_only_receipts",
    "refresh_sources": [
      "gateway_runtime",
      "retrieval_receipts",
      "encrypted_index",
      "ops_quality",
      "skill_metrics"
    ],
    "retrieval_receipt_count": 2,
    "skill_metric_run_count": 5,
    "source_refs_redacted": true,
    "summary": "Retrieval, encrypted index, ops quality, skill metrics, and gateway receipts refresh from local read-only adapters.",
    "title": "Live Safe Receipts"
  },
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
    "dashboard_id": "memory_palace_dashboard_20260503T002124Z",
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
    "generated_at": "2026-05-03T00:21:24.156979Z",
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
  "native_live_feed": {
    "accessibility_observer_started": false,
    "allowed_effects": [
      "render_native_overlay_frame",
      "render_redacted_receipt_summary"
    ],
    "blocked_effects": [
      "start_screen_capture",
      "start_accessibility_observer",
      "write_memory",
      "retain_raw_ref",
      "execute_click",
      "type_text",
      "export_payload"
    ],
    "capture_started": false,
    "display_only": true,
    "external_untrusted_count": 1,
    "feed_id": "NATIVE-SHADOW-POINTER-LIVE-FEED-001",
    "generated_at": "2026-05-03T00:21:24.156979Z",
    "latest_observation_mode": "session",
    "latest_state": "observing",
    "memory_eligible_count": 0,
    "memory_write_allowed": false,
    "native_surface": "macos_shadow_pointer_overlay",
    "policy_refs": [
      "policy_native_shadow_pointer_live_feed_v1",
      "policy_shadow_pointer_live_receipt_v1",
      "policy_shadow_pointer_state_machine_v1"
    ],
    "raw_payload_included": false,
    "raw_ref_retained": false,
    "receipt_count": 1
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
    "policy_consent_first_onboarding_v1",
    "policy_key_management_plan_v1",
    "policy_encrypted_index_dashboard_live_v1",
    "policy_native_shadow_pointer_live_feed_v1",
    "policy_durable_synthetic_memory_receipts_v1",
    "policy_dashboard_live_backbone_v1",
    "policy_clicky_ux_lessons_v1",
    "policy_clicky_ux_companion_v1",
    "policy_dashboard_live_data_adapter_v1",
    "policy_live_dashboard_receipts_v1",
    "policy_dashboard_capture_control_v1",
    "policy_real_capture_intent_v1",
    "policy_real_capture_readiness_v1",
    "policy_real_capture_sensitive_app_filter_v1",
    "policy_real_capture_session_plan_v1",
    "policy_real_capture_start_receipt_v1",
    "policy_real_capture_stop_receipt_v1",
    "policy_real_capture_ephemeral_raw_ref_v1",
    "policy_real_capture_observation_sampler_v1",
    "policy_capture_readiness_ladder_v1"
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
    "generated_at": "2026-05-03T00:21:24.156979Z",
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
      "timestamp": "2026-05-03T00:21:24.156979Z"
    },
    {
      "actor": "system",
      "content_redacted": true,
      "label": "Export preview prepared",
      "receipt_id": "receipt_memory_export_preview",
      "state": "neutral",
      "target_ref": "export_preview_project_scope",
      "timestamp": "2026-05-03T00:21:24.156979Z"
    },
    {
      "actor": "system",
      "content_redacted": true,
      "label": "Skill candidate created",
      "receipt_id": "receipt_skill_candidate_created",
      "state": "healthy",
      "target_ref": "skill_frontend_auth_debugging_flow_v1",
      "timestamp": "2026-05-03T00:21:24.156979Z"
    },
    {
      "actor": "user",
      "content_redacted": true,
      "label": "Observation paused",
      "receipt_id": "receipt_observation_paused",
      "state": "warning",
      "target_ref": "session_20260430",
      "timestamp": "2026-05-03T00:21:24.156979Z"
    }
  ],
  "safety_notes": [
    "Dashboard data is generated from local safe read-only adapters and synthetic view-model seeds.",
    "No raw private memory, screenshots, databases, logs, or API responses are embedded.",
    "Action buttons resolve to gateway receipts before any tool call is allowed.",
    "Skill metric cards do not include procedure text, task content, or autonomy-changing controls.",
    "Retrieval receipt cards do not include memory content, source refs, or hostile text.",
    "Shadow Pointer receipts do not include raw page payloads or raw refs.",
    "Clicky UX lessons were treated as untrusted external evidence and no repo code was executed.",
    "Encrypted index dashboard panels never expose key material, token text, queries, or source refs.",
    "Live adapters expose aggregate counts only and keep write paths disabled.",
    "Real capture control starts with cursor overlay readiness and keeps raw storage and memory writes disabled.",
    "Capture readiness ladder is display-only; it blocks continuous capture, raw pixels, durable memory writes, and external effects."
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
    "generated_at": "2026-05-03T00:21:24.156979Z",
    "list_id": "skill_forge_candidate_list_20260503T002124Z",
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
    "generated_at": "2026-05-03T00:21:24.156979Z",
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
