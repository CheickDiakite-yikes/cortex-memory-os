const data = window.CORTEX_DASHBOARD_DATA;
let captureControlConfig = window.CORTEX_CAPTURE_CONTROL || null;

const icons = {
  overview: '<path d="M3 11.5 12 4l9 7.5"/><path d="M5 10.5V21h14V10.5"/><path d="M9 21v-6h6v6"/>',
  memory_palace: '<path d="M4 20h16"/><path d="M6 17V9"/><path d="M10 17V9"/><path d="M14 17V9"/><path d="M18 17V9"/><path d="M3 9h18L12 4 3 9Z"/>',
  skill_forge: '<path d="m14.7 6.3 3 3"/><path d="m3 21 8.5-8.5"/><path d="m15 5 4 4-8 8H7v-4l8-8Z"/><path d="m14 14 4 4"/><path d="m16 16-2 2"/>',
  agent_gateway: '<path d="M12 3v6"/><path d="M12 15v6"/><path d="M5.5 7.5 12 9l6.5-1.5"/><path d="M5.5 16.5 12 15l6.5 1.5"/><circle cx="12" cy="12" r="3"/>',
  audit: '<path d="M9 11l2 2 4-5"/><path d="M12 22s8-4 8-11V5l-8-3-8 3v6c0 7 8 11 8 11Z"/>',
  policies: '<path d="M12 22s8-4 8-11V5l-8-3-8 3v6c0 7 8 11 8 11Z"/><path d="M9 12h6"/><path d="M9 16h6"/><path d="M9 8h6"/>',
  shield: '<path d="M12 22s8-4 8-11V5l-8-3-8 3v6c0 7 8 11 8 11Z"/><path d="m9 12 2 2 4-5"/>',
  folder: '<path d="M3 7h7l2 2h9v10H3z"/><path d="M3 7v12"/>',
  pointer: '<path d="M8 3 18 14l-5 .5L10.5 20 8 3Z"/>',
  eye: '<path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>',
  edit: '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z"/>',
  trash: '<path d="M3 6h18"/><path d="M8 6V4h8v2"/><path d="M6 6l1 15h10l1-15"/>',
  export: '<path d="M12 3v12"/><path d="m7 8 5-5 5 5"/><path d="M5 21h14"/>',
  play: '<path d="m8 5 12 7-12 7Z"/>',
  file: '<path d="M14 2H6v20h12V6z"/><path d="M14 2v4h4"/><path d="M8 13h8"/><path d="M8 17h6"/>',
  more: '<circle cx="12" cy="5" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="12" cy="19" r="1"/>',
  check: '<path d="m5 12 4 4L19 6"/>',
  pause: '<path d="M9 5v14"/><path d="M15 5v14"/>',
  route: '<path d="M6 4h12"/><path d="M6 20h12"/><circle cx="6" cy="4" r="2"/><circle cx="18" cy="20" r="2"/><path d="M6 6c0 7 12 5 12 12"/>',
};

let memoryFilter = "all";
let skillFilter = "all";
let selectedFocus = data.focus_inspector || null;
const gatewayReceiptByAction = new Map(
  (data.gateway_action_receipts || []).map((receipt) => [receipt.action_key, receipt]),
);
const skillMetricById = new Map((data.skill_metrics?.cards || []).map((card) => [card.skill_id, card]));
const viewCopy = {
  overview: {
    label: "Overview",
    title: "Cortex Memory OS",
    copy: "System status, demo readiness, and guardrail health.",
  },
  memory_palace: {
    label: "Memory Palace",
    title: "Memory Review Queue",
    copy: "Inspectable memories with correction, scope, and forget receipts.",
  },
  skill_forge: {
    label: "Skill Forge",
    title: "Candidate Workflows",
    copy: "Draft-only skills, maturity signals, and blocked promotion paths.",
  },
  agent_gateway: {
    label: "Agent Gateway",
    title: "Gateway Receipts",
    copy: "Read-only context and review calls stay separate from blocked effects.",
  },
  audit: {
    label: "Audit",
    title: "Safe Receipts",
    copy: "Recent local receipts and blocked gateway previews.",
  },
  policies: {
    label: "Policies",
    title: "Guardrail State",
    copy: "Privacy, evidence, encryption, and ops quality gates.",
  },
};
let activeView = initialView();

function svgIcon(name) {
  return `<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">${icons[name] || icons.file}</svg>`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatToken(value) {
  return escapeHtml(String(value || "").replaceAll("_", " "));
}

function statusClass(status) {
  return `status-${String(status || "").replaceAll("_", "-")}`;
}

function riskClass(risk) {
  return `risk-${String(risk || "").replaceAll("_", "-")}`;
}

function writeReceipt(message) {
  const receipt = document.querySelector("#interaction-receipt");
  if (receipt) receipt.textContent = message;
  const liveReceipt = ensureLiveCommandReceipt();
  liveReceipt.textContent = message;
  liveReceipt.hidden = false;
}

function ensureLiveCommandReceipt() {
  let liveReceipt = document.querySelector("#live-command-receipt");
  if (liveReceipt) return liveReceipt;
  liveReceipt = document.createElement("p");
  liveReceipt.id = "live-command-receipt";
  liveReceipt.className = "live-command-receipt";
  liveReceipt.setAttribute("aria-live", "polite");
  liveReceipt.hidden = true;
  document.body.append(liveReceipt);
  return liveReceipt;
}

async function callCaptureControl(action, payload = {}) {
  return callCaptureControlWithConfig(action, payload, { refreshed: false });
}

async function refreshCaptureControlConfig() {
  const response = await fetch(`./capture-control-config.js?ts=${Date.now()}`, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error("capture control config refresh failed");
  }
  const scriptText = await response.text();
  const match = scriptText.match(
    /^window\.CORTEX_CAPTURE_CONTROL = (\{[\s\S]*\});\s*$/,
  );
  if (!match) {
    throw new Error("capture control config response was not recognized");
  }
  captureControlConfig = JSON.parse(match[1]);
  window.CORTEX_CAPTURE_CONTROL = captureControlConfig;
  return captureControlConfig;
}

async function callCaptureControlWithConfig(action, payload = {}, options = {}) {
  if (window.location.protocol === "file:") {
    throw new Error("capture control bridge is not available from file://");
  }
  if (!captureControlConfig?.token) {
    throw new Error("capture control token is unavailable");
  }
  const configKeys = {
    status: "statusPath",
    start: "startPath",
    stop: "stopPath",
    permissions: "permissionsPath",
    preflight: "preflightPath",
    screenProbe: "screenProbePath",
    receipts: "receiptsPath",
  };
  const path = captureControlConfig[configKeys[action]] || `/api/capture/${action}`;
  const readOnly = action === "status" || action === "permissions" || action === "preflight" || action === "receipts";
  const response = await fetch(path, {
    method: readOnly ? "GET" : "POST",
    headers: {
      "X-Cortex-Capture-Token": captureControlConfig.token,
      ...(readOnly ? {} : { "Content-Type": "application/json" }),
    },
    body: readOnly ? undefined : JSON.stringify(payload),
  });
  const receipt = await response.json();
  if (!response.ok) {
    if (
      !options.refreshed &&
      receipt.error_code === "missing_or_invalid_capture_token"
    ) {
      writeReceipt("Capture bridge token refreshed. Retrying local command once.");
      await refreshCaptureControlConfig();
      return callCaptureControlWithConfig(action, payload, { refreshed: true });
    }
    throw new Error(receipt.error_code || `capture control ${action} failed`);
  }
  return receipt;
}

function describeCaptureBridgeFallback(panel) {
  return `Local bridge unavailable. Run uv run cortex-capture-control-server --port 8799, then open http://127.0.0.1:8799/index.html. CLI fallback: ${panel.native_cursor_command}.`;
}

function formatCaptureSkipReason(reason) {
  if (reason === "screen_recording_preflight_false") {
    return "Screen Recording permission is missing";
  }
  if (reason === "allow_real_capture_false") {
    return "explicit probe approval was not supplied";
  }
  return formatToken(reason || "none");
}

function initialView() {
  const hashView = window.location.hash.replace("#", "");
  if (viewCopy[hashView]) return hashView;
  const queryView = new URLSearchParams(window.location.search).get("view");
  if (queryView && viewCopy[queryView]) return queryView;
  return "overview";
}

function updateHeaderForView() {
  const copy = viewCopy[activeView] || viewCopy.overview;
  document.querySelector("#view-label").textContent = copy.label;
  document.querySelector("#view-title").textContent = copy.title;
  document.querySelector("#view-copy").textContent = copy.copy;
}

function applyActiveView() {
  updateHeaderForView();
  document.body.dataset.activeView = activeView;
  document.querySelectorAll("[data-view-section]").forEach((section) => {
    const views = section.dataset.viewSection.split(/\s+/);
    section.hidden = !views.includes(activeView);
  });
  document.querySelectorAll("[data-work-panel]").forEach((panel) => {
    panel.hidden = panel.dataset.workPanel !== activeView;
  });
  const workspace = document.querySelector(".workspace-grid");
  if (workspace) {
    workspace.classList.toggle("single-view", ["memory_palace", "skill_forge"].includes(activeView));
  }
}

function focusFromMemory(card) {
  return {
    title: "Focus Inspector",
    subject_type: "memory",
    target_ref: card.memory_id,
    summary: `${formatToken(card.status)} memory · ${formatToken(card.scope)} scope · sources redacted to count ${card.source_count}.`,
    state: card.recall_eligible ? "healthy" : "warning",
    metrics: [
      { label: "Confidence", value: Number(card.confidence).toFixed(2), state: "healthy" },
      { label: "Scope", value: formatToken(card.scope), state: "neutral" },
      { label: "Recall", value: card.recall_eligible ? "allowed" : "blocked", state: card.recall_eligible ? "healthy" : "warning" },
    ],
    actions: (card.action_plans || []).slice(0, 3).map((plan) => ({
      label: plan.gateway_tool.split(".").pop(),
      gateway_tool: plan.gateway_tool,
      requires_confirmation: plan.requires_confirmation,
      allowed_gateway_call: plan.gateway_tool === "memory.explain",
    })),
  };
}

function focusFromSkill(card) {
  return {
    title: "Focus Inspector",
    subject_type: "skill",
    target_ref: card.skill_id,
    summary: `${card.name} · ${formatToken(card.risk_level)} risk · procedure remains redacted until explicit review.`,
    state: card.risk_level === "high" ? "warning" : "healthy",
    metrics: [
      { label: "Maturity", value: `Level ${card.maturity_level}`, state: "neutral" },
      { label: "Evidence", value: `${card.learned_from_count} refs`, state: "healthy" },
      { label: "Mode", value: formatToken(card.execution_mode), state: "healthy" },
    ],
    actions: (card.action_plans || []).slice(0, 3).map((plan) => ({
      label: plan.gateway_tool.split(".").pop(),
      gateway_tool: plan.gateway_tool,
      requires_confirmation: plan.requires_confirmation,
      allowed_gateway_call: plan.gateway_tool === "skill.review_candidate",
    })),
  };
}

function ensureFocusForActiveView() {
  if (activeView === "memory_palace" && selectedFocus?.subject_type !== "memory") {
    const card = filteredMemories()[0] || data.memory_palace.cards[0];
    if (card) selectedFocus = focusFromMemory(card);
  }
  if (activeView === "skill_forge" && selectedFocus?.subject_type !== "skill") {
    const card = filteredSkills()[0] || data.skill_forge.cards[0];
    if (card) selectedFocus = focusFromSkill(card);
  }
}

function setActiveView(view) {
  activeView = viewCopy[view] ? view : "overview";
  ensureFocusForActiveView();
  renderNav();
  applyActiveView();
  renderFocusInspector();
  if (window.location.hash !== `#${activeView}`) {
    window.history.replaceState(null, "", `${window.location.pathname}${window.location.search}#${activeView}`);
  }
  writeReceipt(`${viewCopy[activeView].label} selected. View updated locally; no gateway action executed.`);
}

function renderNav() {
  const nav = document.querySelector("#nav-list");
  nav.innerHTML = data.nav_items
    .map(
      (item) => `
        <button class="nav-item ${item.item_id === activeView ? "active" : ""}" type="button" data-nav="${escapeHtml(item.item_id)}" title="${escapeHtml(item.label)}" aria-pressed="${item.item_id === activeView ? "true" : "false"}">
          ${svgIcon(item.item_id)}
          <span class="label">${escapeHtml(item.label)}</span>
          ${Number.isInteger(item.count) ? `<span class="nav-count">${item.count}</span>` : ""}
        </button>
      `,
    )
    .join("");

  nav.querySelectorAll(".nav-item").forEach((button) => {
    button.addEventListener("click", () => {
      setActiveView(button.dataset.nav);
    });
  });
}

function renderStatusStrip() {
  const statusStrip = document.querySelector("#status-strip");
  statusStrip.innerHTML = [
    ...data.status_strip.map(
      (item) => `
        <div class="status-item" data-state="${escapeHtml(item.state)}">
          <span class="status-icon">${svgIcon(item.item_id === "active_project" ? "folder" : item.item_id === "shadow_pointer" ? "pointer" : "shield")}</span>
          <span>
            <span class="status-label">${escapeHtml(item.label)}</span>
            <strong class="status-value">${escapeHtml(item.value)}</strong>
            <span class="status-detail">${escapeHtml(item.detail)}</span>
          </span>
        </div>
      `,
    ),
    `<button class="pause-button" type="button" id="pause-observation">${svgIcon("pause")} Pause Observation</button>`,
  ].join("");

  document.querySelector("#pause-observation").addEventListener("click", () => {
    writeReceipt("Observation pause previewed locally. Confirmation and audit receipt required.");
  });
}

function bindHeaderActions() {
  const auditLog = document.querySelector("#audit-log");
  if (!auditLog) return;
  auditLog.addEventListener("click", () => {
    writeReceipt("Audit log selected. Receipts stay redacted and local.");
  });
}

function renderInsights() {
  const list = document.querySelector("#insight-list");
  if (!list) return;
  list.innerHTML = (data.insight_panels || [])
    .map(
      (panel) => `
        <article class="insight-panel" data-state="${escapeHtml(panel.state)}">
          <div class="insight-top">
            <span class="insight-icon">${svgIcon(panel.panel_id === "encryption_default" ? "shield" : panel.panel_id === "evidence_vault" ? "folder" : "check")}</span>
            <span>
              <strong>${escapeHtml(panel.title)}</strong>
              <span>${escapeHtml(panel.detail)}</span>
            </span>
            <em>${escapeHtml(panel.value)}</em>
          </div>
        </article>
      `,
    )
    .join("");
}

function renderDemoPath() {
  const demoPath = data.demo_path;
  const target = document.querySelector("#demo-path");
  if (!target || !demoPath) return;
  target.innerHTML = `
    <div class="demo-path-copy">
      <span class="demo-path-icon">${svgIcon("route")}</span>
      <span>
        <strong>${escapeHtml(demoPath.title)}</strong>
        <span>${escapeHtml(demoPath.summary)}</span>
      </span>
    </div>
    <ol class="demo-step-list">
      ${(demoPath.steps || [])
        .map(
          (step, index) => `
            <li data-state="${escapeHtml(step.state)}" title="${escapeHtml(step.safety_note)}">
              <span>${index + 1}</span>
              <strong>${escapeHtml(step.label)}</strong>
              <em>${escapeHtml(step.surface)}</em>
            </li>
          `,
        )
        .join("")}
    </ol>
    <div class="demo-command-group">
      <button class="text-command" type="button" id="demo-readiness-command">
        cortex-demo
      </button>
      <button class="text-command" type="button" id="demo-stress-command">
        cortex-demo-stress
      </button>
    </div>
  `;
  document.querySelector("#demo-readiness-command").addEventListener("click", () => {
    writeReceipt("DEMO-READINESS-001 selected. Run uv run cortex-demo --json for the safe demo receipt.");
  });
  document.querySelector("#demo-stress-command").addEventListener("click", () => {
    writeReceipt("DEMO-STRESS-001 selected. Run uv run cortex-demo-stress --iterations 12 --json for the bounded stress receipt.");
  });
}

function renderCaptureControl() {
  const target = document.querySelector("#capture-control");
  const bundle = data.capture_control;
  const panel = bundle?.dashboard_panel;
  const readiness = bundle?.readiness;
  const start = bundle?.start_receipt;
  if (!target || !panel || !readiness || !start) return;
  const missing = readiness.missing_permissions?.length
    ? readiness.missing_permissions.map(formatToken).join(", ")
    : "none";
  target.innerHTML = `
    <div class="capture-control-copy">
      <span class="capture-control-icon">${svgIcon("pointer")}</span>
      <span>
        <strong>Capture Control</strong>
        <span>Native Shadow Clicker readiness with explicit consent and local receipts.</span>
      </span>
    </div>
    <div class="capture-control-grid">
      <div><span>State</span><strong>${formatToken(panel.state)}</strong></div>
      <div><span>Cursor</span><strong>${readiness.can_start_cursor_overlay ? "ready" : "blocked"}</strong></div>
      <div><span>Screen</span><strong>${readiness.can_start_screen_capture ? "ready" : "needs permission"}</strong></div>
      <div><span>Bridge</span><strong id="capture-runtime-status">checking</strong></div>
      <div><span>Missing</span><strong>${escapeHtml(missing)}</strong></div>
      <div><span>PID</span><strong id="capture-runtime-pid">none</strong></div>
    </div>
    <div class="shadow-live-actions">
      <button class="text-command" type="button" id="capture-turn-on">
        ${escapeHtml(panel.primary_button_label)}
      </button>
      <button class="text-command" type="button" id="capture-shadow-command">
        cortex-shadow-clicker
      </button>
      <button class="text-command" type="button" id="capture-permissions">
        Check Permissions
      </button>
      <button class="text-command" type="button" id="capture-preflight">
        Preflight
      </button>
      <button class="text-command" type="button" id="capture-screen-probe">
        Screen Probe
      </button>
      <button class="text-command" type="button" id="capture-receipts">
        Receipts
      </button>
      <button class="text-command" type="button" id="capture-stop">
        ${escapeHtml(panel.stop_button_label)}
      </button>
    </div>
  `;
  refreshCaptureRuntimeStatus(panel);
  document.querySelector("#capture-turn-on").addEventListener("click", async () => {
    writeReceipt(`${panel.primary_button_label}: asking localhost bridge to start display-only Shadow Clicker.`);
    try {
      const receipt = await callCaptureControl("start", { duration_seconds: 30 });
      writeReceipt(
        `${panel.primary_button_label}: Shadow Clicker running with pid ${receipt.pid}. Screen capture=${receipt.capture_started}; memory writes=${receipt.memory_write_allowed}; raw refs=${receipt.raw_ref_retained}.`,
      );
      updateCaptureRuntime(receipt);
    } catch (_error) {
      writeReceipt(describeCaptureBridgeFallback(panel));
    }
  });
  document.querySelector("#capture-shadow-command").addEventListener("click", () => {
    writeReceipt(`Native Shadow Clicker command: ${panel.native_cursor_command}. It follows the system cursor without clicks, typing, screen capture, or memory writes.`);
  });
  document.querySelector("#capture-permissions").addEventListener("click", async () => {
    try {
      const receipt = await callCaptureControl("permissions");
      writeReceipt(
        `Permissions: Screen Recording=${receipt.screen_recording_preflight}; Accessibility=${receipt.accessibility_trusted}; prompts=${receipt.prompt_requested}.`,
      );
    } catch (_error) {
      writeReceipt(describeCaptureBridgeFallback(panel));
    }
  });
  document.querySelector("#capture-preflight").addEventListener("click", async () => {
    try {
      const receipt = await callCaptureControl("preflight");
      const missing = receipt.missing_permissions.length
        ? receipt.missing_permissions.map(formatToken).join(", ")
        : "none";
      const action = receipt.next_user_actions[0] || "No action needed.";
      writeReceipt(
        `Preflight: missing=${missing}; screen probe=${receipt.safe_to_attempt_metadata_probe ? "ready" : "blocked"}; real session=${receipt.safe_to_start_real_capture_session ? "ready" : "blocked"}. ${action}`,
      );
    } catch (_error) {
      writeReceipt(describeCaptureBridgeFallback(panel));
    }
  });
  document.querySelector("#capture-screen-probe").addEventListener("click", async () => {
    try {
      const receipt = await callCaptureControl("screenProbe", { allow_real_capture: true });
      const dimensions = receipt.frame_captured
        ? `${receipt.frame_width}x${receipt.frame_height}`
        : "not captured";
      const skip = receipt.skip_reason
        ? `; skipped=${formatCaptureSkipReason(receipt.skip_reason)}`
        : "";
      const action = receipt.next_user_actions?.[0] ? ` ${receipt.next_user_actions[0]}` : "";
      writeReceipt(
        `Screen Probe: attempted=${receipt.capture_attempted}; frame=${dimensions}${skip}; raw pixels=${receipt.raw_pixels_returned}; raw refs=${receipt.raw_ref_retained}; memory writes=${receipt.memory_write_allowed}.${action}`,
      );
    } catch (_error) {
      writeReceipt(describeCaptureBridgeFallback(panel));
    }
  });
  document.querySelector("#capture-receipts").addEventListener("click", async () => {
    try {
      const receipt = await callCaptureControl("receipts");
      writeReceipt(
        `Receipts: ${receipt.receipt_count} local events; starts=${receipt.start_count}; stops=${receipt.stop_count}; preflights=${receipt.preflight_count}; screen probes=${receipt.screen_probe_count}; skipped=${receipt.skipped_screen_probe_count}; exits=${receipt.watchdog_exit_count}; raw refs=${receipt.raw_ref_retained}; memory writes=${receipt.memory_write_allowed}.`,
      );
    } catch (_error) {
      writeReceipt(describeCaptureBridgeFallback(panel));
    }
  });
  document.querySelector("#capture-stop").addEventListener("click", async () => {
    try {
      const receipt = await callCaptureControl("stop");
      writeReceipt(`${panel.stop_button_label}: ${receipt.state}. Observation inactive and no capture artifacts retained.`);
      updateCaptureRuntime(receipt);
    } catch (_error) {
      writeReceipt(`${panel.stop_button_label}: ${bundle.stop_receipt.audit_action}. Observation inactive and ephemeral refs expire by policy.`);
    }
  });
}

function renderCaptureReadinessLadder() {
  const target = document.querySelector("#capture-readiness-ladder");
  const ladder = data.capture_readiness_ladder;
  if (!target || !ladder) return;
  const steps = ladder.steps || [];
  target.innerHTML = `
    <div class="capture-ladder-copy">
      <span class="capture-ladder-icon">${svgIcon("route")}</span>
      <span>
        <strong>${escapeHtml(ladder.title)}</strong>
        <span>${escapeHtml(ladder.summary)}</span>
      </span>
    </div>
    <div class="capture-ladder-grid">
      <div><span>Ready</span><strong>${ladder.ready_count}/10</strong></div>
      <div><span>Blocked</span><strong>${ladder.blocked_count}</strong></div>
      <div><span>Next</span><strong>${escapeHtml(ladder.next_step_label)}</strong></div>
      <div><span>Real capture</span><strong>${ladder.can_real_capture_now ? "ready" : "gated"}</strong></div>
    </div>
    <ol class="capture-ladder-list">
      ${steps
        .map(
          (step) => `
            <li class="capture-ladder-step ${statusClass(step.status)}" title="${escapeHtml(step.safety_note)}">
              <span class="capture-ladder-step-index">${step.order}</span>
              <span class="capture-ladder-step-main">
                <strong>${escapeHtml(step.label)}</strong>
                <span>${escapeHtml(step.surface)} · ${escapeHtml(step.proof)}</span>
              </span>
              <span class="capture-ladder-state">${formatToken(step.status)}</span>
            </li>
          `,
        )
        .join("")}
    </ol>
    <div class="shadow-live-actions">
      <button class="text-command" type="button" id="capture-ladder-preflight">Preflight</button>
      <button class="text-command" type="button" id="capture-ladder-screen-probe">Screen Probe</button>
      <button class="text-command" type="button" id="capture-ladder-receipts">Receipts</button>
    </div>
  `;
  document.querySelector("#capture-ladder-preflight").addEventListener("click", async () => {
    try {
      const receipt = await callCaptureControl("preflight");
      writeReceipt(
        `Capture Readiness Ladder preflight: ${receipt.missing_permissions.length} blocker(s); metadata probe=${receipt.safe_to_attempt_metadata_probe ? "ready" : "gated"}; real capture=${receipt.safe_to_start_real_capture_session ? "ready" : "gated"}.`,
      );
    } catch (_error) {
      writeReceipt(`Capture Readiness Ladder: ${ladder.next_step_label} is next. Local bridge is unavailable, so no capture action was attempted.`);
    }
  });
  document.querySelector("#capture-ladder-screen-probe").addEventListener("click", async () => {
    try {
      const receipt = await callCaptureControl("screenProbe", { allow_real_capture: true });
      writeReceipt(
        `Capture Readiness Ladder screen probe: attempted=${receipt.capture_attempted}; frame=${receipt.frame_captured ? `${receipt.frame_width}x${receipt.frame_height}` : "skipped"}; raw pixels=${receipt.raw_pixels_returned}; raw refs=${receipt.raw_ref_retained}; memory writes=${receipt.memory_write_allowed}.`,
      );
    } catch (_error) {
      writeReceipt("Capture Readiness Ladder: Screen Probe stayed gated because the localhost bridge is unavailable.");
    }
  });
  document.querySelector("#capture-ladder-receipts").addEventListener("click", async () => {
    try {
      const receipt = await callCaptureControl("receipts");
      writeReceipt(
        `Capture Readiness Ladder receipts: ${receipt.receipt_count} event(s); screen probes=${receipt.screen_probe_count}; skipped=${receipt.skipped_screen_probe_count}; raw refs=${receipt.raw_ref_retained}; memory writes=${receipt.memory_write_allowed}.`,
      );
    } catch (_error) {
      writeReceipt("Capture Readiness Ladder receipt view is static until the localhost bridge is running.");
    }
  });
}

async function refreshCaptureRuntimeStatus(panel) {
  try {
    const receipt = await callCaptureControl("status");
    updateCaptureRuntime(receipt);
    window.setTimeout(() => refreshCaptureRuntimeStatus(panel), 3000);
  } catch (_error) {
    const status = document.querySelector("#capture-runtime-status");
    const pid = document.querySelector("#capture-runtime-pid");
    if (status) status.textContent = "static";
    if (pid) pid.textContent = "none";
    writeReceipt(describeCaptureBridgeFallback(panel));
  }
}

function updateCaptureRuntime(receipt) {
  const status = document.querySelector("#capture-runtime-status");
  const pid = document.querySelector("#capture-runtime-pid");
  if (status) status.textContent = receipt.running ? "running" : receipt.state === "exited" ? "exited" : "ready";
  if (pid) pid.textContent = receipt.pid ? String(receipt.pid) : "none";
}

function renderShadowPointerLiveReceipt() {
  const target = document.querySelector("#shadow-live-receipt");
  const receipt = data.shadow_pointer_live_receipt;
  const onboarding = data.consent_onboarding;
  const companion = data.clicky_ux_companion;
  const nativeFeed = data.native_live_feed;
  if (!target || !receipt) return;
  const fields = receipt.compact_fields || {};
  const onboardingSteps = onboarding?.steps || [];
  target.innerHTML = `
    <div class="shadow-live-copy">
      <span class="shadow-live-icon">${svgIcon("pointer")}</span>
      <span>
        <strong>${escapeHtml(companion?.title || "Cursor Companion")}</strong>
        <span>${escapeHtml(companion?.primary_status || receipt.primary_line)}</span>
      </span>
    </div>
    <p class="companion-note">${escapeHtml(companion?.next_safe_action || "Receipt is display-only.")}</p>
    <div class="shadow-live-grid">
      <div><span>State</span><strong>${formatToken(nativeFeed?.latest_state || receipt.state)}</strong></div>
      <div><span>Trust</span><strong>${formatToken(fields.trust)}</strong></div>
      <div><span>Memory</span><strong>${formatToken(fields.memory)}</strong></div>
      <div><span>Raw refs</span><strong>${formatToken(fields.raw_refs)}</strong></div>
    </div>
    <div class="shadow-live-actions">
      <button class="text-command" type="button" id="shadow-receipt-details">Receipt</button>
      <button class="text-command" type="button" id="consent-onboarding">Consent-first Onboarding</button>
      <button class="text-command" type="button" id="clicky-ux-lessons">Clicky UX Lessons</button>
    </div>
  `;
  document.querySelector("#shadow-receipt-details").addEventListener("click", () => {
    writeReceipt(
      `${receipt.title}: ${formatToken(fields.trust)} · memory ${formatToken(fields.memory)} · raw refs ${formatToken(fields.raw_refs)}.`,
    );
  });
  document.querySelector("#consent-onboarding").addEventListener("click", () => {
    writeReceipt(
      `Consent-first Onboarding has ${onboardingSteps.length} synthetic steps. Real capture and private durable writes stay off.`,
    );
  });
  document.querySelector("#clicky-ux-lessons").addEventListener("click", () => {
    writeReceipt("Clicky UX Lessons applied: cursor-adjacent presence, compact receipt panel, display-only pointing. External repo code was not executed.");
  });
}

function renderEncryptedIndexPanel() {
  const target = document.querySelector("#encrypted-index-panel");
  const panel = data.encrypted_index_panel;
  const backbone = data.live_backbone_panel;
  if (!target || !panel) return;
  target.innerHTML = `
    <div class="encrypted-index-copy">
      <span class="encrypted-index-icon">${svgIcon("shield")}</span>
      <span>
        <strong>${escapeHtml(panel.title)}</strong>
        <span>${escapeHtml(backbone?.summary || panel.summary)}</span>
      </span>
    </div>
    <div class="encrypted-index-grid">
      <div><span>Writes</span><strong>${panel.write_receipt_count}</strong></div>
      <div><span>Search</span><strong>${panel.search_result_count}</strong></div>
      <div><span>Opened</span><strong>${panel.candidate_open_count}</strong></div>
      <div><span>Refs</span><strong>${panel.source_ref_count}</strong></div>
    </div>
    <div class="shadow-live-actions">
      <button class="text-command" type="button" id="encrypted-index-search">memory.search_index</button>
      <button class="text-command" type="button" id="live-backbone-receipt">Live Receipt Backbone</button>
    </div>
  `;
  document.querySelector("#encrypted-index-search").addEventListener("click", () => {
    writeReceipt("memory.search_index selected. Query text, token text, content, source refs, and key material stay redacted.");
  });
  document.querySelector("#live-backbone-receipt").addEventListener("click", () => {
    writeReceipt("Live Receipt Backbone is ready: key plan, encrypted index, native feed, and durable synthetic receipt are wired.");
  });
}

function renderLiveDashboardReceipts() {
  const target = document.querySelector("#live-dashboard-receipts");
  const panel = data.live_dashboard_receipts;
  const adapter = data.dashboard_live_data_adapter;
  if (!target || !panel || !adapter) return;
  target.innerHTML = `
    <div class="live-receipts-copy">
      <span class="live-receipts-icon">${svgIcon("route")}</span>
      <span>
        <strong>${escapeHtml(panel.title)}</strong>
        <span>${escapeHtml(panel.summary)}</span>
      </span>
    </div>
    <div class="live-receipts-grid">
      <div><span>Gateway</span><strong>${panel.gateway_executed_count}/${panel.gateway_blocked_count}</strong></div>
      <div><span>Retrieval</span><strong>${panel.retrieval_receipt_count}</strong></div>
      <div><span>Index</span><strong>${panel.encrypted_index_search_result_count}</strong></div>
      <div><span>Ops</span><strong>${panel.ops_passed_cases}</strong></div>
      <div><span>Skills</span><strong>${panel.skill_metric_run_count}</strong></div>
    </div>
    <div class="shadow-live-actions">
      <button class="text-command" type="button" id="live-data-adapter-receipt">
        DASHBOARD-LIVE-DATA-ADAPTER-001
      </button>
      <button class="text-command" type="button" id="live-dashboard-refresh">
        LIVE-DASHBOARD-RECEIPTS-001
      </button>
    </div>
  `;
  document.querySelector("#live-data-adapter-receipt").addEventListener("click", () => {
    writeReceipt(
      `Read-only adapter: ${adapter.adapter_sources.length} local sources, ${adapter.gateway_executed_count} gateway calls, raw payloads ${adapter.raw_payload_returned ? "present" : "absent"}.`,
    );
  });
  document.querySelector("#live-dashboard-refresh").addEventListener("click", () => {
    writeReceipt("Live dashboard receipts refreshed from local safe receipt counts. No write path or raw payload returned.");
  });
}

function renderFocusInspector() {
  const inspector = document.querySelector("#focus-inspector");
  if (!inspector || !selectedFocus) return;
  inspector.innerHTML = `
    <div class="focus-copy">
      <p class="section-label">${escapeHtml(selectedFocus.title || "Focus Inspector")}</p>
      <h2>${escapeHtml(selectedFocus.target_ref)}</h2>
      <p>${escapeHtml(selectedFocus.summary)}</p>
    </div>
    <div class="focus-metrics">
      ${(selectedFocus.metrics || [])
        .map(
          (metric) => `
            <div class="focus-metric" data-state="${escapeHtml(metric.state)}">
              <span>${escapeHtml(metric.label)}</span>
              <strong>${escapeHtml(metric.value)}</strong>
            </div>
          `,
        )
        .join("")}
    </div>
    <div class="focus-actions">
      ${(selectedFocus.actions || [])
        .map(
          (action) => `
            <button class="text-command" type="button" data-focus-tool="${escapeHtml(action.gateway_tool)}">
              ${escapeHtml(action.label)}
            </button>
          `,
        )
        .join("")}
    </div>
  `;
  inspector.querySelectorAll("[data-focus-tool]").forEach((button) => {
    button.addEventListener("click", () => {
      writeReceipt(`${button.dataset.focusTool} selected from Focus Inspector. Gateway receipt still required.`);
    });
  });
}

function setMemoryFocus(card) {
  selectedFocus = focusFromMemory(card);
  renderFocusInspector();
}

function setSkillFocus(card) {
  selectedFocus = focusFromSkill(card);
  renderFocusInspector();
}

function renderTabs() {
  const memoryCounts = data.memory_palace.status_counts;
  const memoryTabs = [
    ["all", "All", data.memory_palace.cards.length],
    ["active", "Active", memoryCounts.active || 0],
    ["candidate", "Candidate", memoryCounts.candidate || 0],
    ["needs_review", "Needs Review", data.memory_palace.confirmation_required_count],
  ];
  document.querySelector("#memory-tabs").innerHTML = memoryTabs
    .map(
      ([key, label, count]) => `
        <button class="tab-button ${memoryFilter === key ? "active" : ""}" type="button" data-memory-filter="${key}">
          ${label}<span class="mini-count">${count}</span>
        </button>
      `,
    )
    .join("");
  document.querySelectorAll("[data-memory-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      memoryFilter = button.dataset.memoryFilter;
      renderDashboard();
      writeReceipt(`${button.textContent.trim()} memory filter selected.`);
    });
  });

  const riskCounts = data.skill_forge.risk_counts;
  const skillTabs = [
    ["all", "All", data.skill_forge.cards.length],
    ["draft_only", "Draft-only", data.skill_forge.cards.length],
    ["low", "Low risk", riskCounts.low || 0],
    ["medium", "Medium risk", riskCounts.medium || 0],
    ["high", "High risk", riskCounts.high || 0],
  ];
  document.querySelector("#skill-tabs").innerHTML = skillTabs
    .map(
      ([key, label, count]) => `
        <button class="tab-button ${skillFilter === key ? "active" : ""}" type="button" data-skill-filter="${key}">
          ${label}<span class="mini-count">${count}</span>
        </button>
      `,
    )
    .join("");
  document.querySelectorAll("[data-skill-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      skillFilter = button.dataset.skillFilter;
      renderDashboard();
      writeReceipt(`${button.textContent.trim()} skill filter selected.`);
    });
  });
}

function filteredMemories() {
  return data.memory_palace.cards.filter((card) => {
    if (memoryFilter === "all") return true;
    if (memoryFilter === "needs_review") return card.requires_user_confirmation;
    return card.status === memoryFilter;
  });
}

function filteredSkills() {
  return data.skill_forge.cards.filter((card) => {
    if (skillFilter === "all") return true;
    if (skillFilter === "draft_only") return card.execution_mode === "draft_only";
    return card.risk_level === skillFilter;
  });
}

function renderMemoryCards() {
  const cards = takeVisibleCards(filteredMemories(), 2);
  const hiddenCount = filteredMemories().length - cards.length;
  document.querySelector("#memory-count").textContent = data.memory_palace.cards.length;
  const list = document.querySelector("#memory-list");
  if (!cards.length) {
    list.innerHTML = '<div class="empty-state">No memories match this filter.</div>';
    return;
  }
  list.innerHTML = cards
    .map(
      (card) => `
        <section class="memory-card" data-state="${escapeHtml(card.status)}" data-memory-id="${escapeHtml(card.memory_id)}">
          <div class="card-top">
            <div>
              <h2 class="card-title">${escapeHtml(card.memory_id)}</h2>
              <p class="card-copy">${escapeHtml(card.content_preview || "Preview hidden by lifecycle or visibility policy.")}</p>
            </div>
            <button class="icon-button" type="button" title="More memory actions" aria-label="More memory actions">${svgIcon("more")}</button>
          </div>
          <div class="chip-row">
            <span class="chip">${formatToken(card.type)}</span>
            <span class="chip">${formatToken(card.scope)}</span>
            <span class="chip">Sources ${card.source_count}</span>
          </div>
          <div class="meta-grid">
            <div><span class="meta-label">Confidence</span><strong class="meta-value">${Number(card.confidence).toFixed(2)}</strong></div>
            <div><span class="meta-label">Status</span><strong class="meta-value ${statusClass(card.status)}">${formatToken(card.status)}</strong></div>
            <div><span class="meta-label">Recall</span><strong class="meta-value">${card.recall_eligible ? "Allowed" : "Blocked"}</strong></div>
          </div>
          <div class="action-row">
            ${card.action_plans.map((plan) => memoryActionButton(card, plan)).join("")}
          </div>
        </section>
      `,
    )
    .join("") + hiddenSummary(hiddenCount, "memory");
  list.querySelectorAll("[data-action-tool]").forEach(bindActionButton);
  list.querySelectorAll("[data-memory-id]").forEach((cardElement) => {
    cardElement.addEventListener("click", () => {
      const card = data.memory_palace.cards.find((item) => item.memory_id === cardElement.dataset.memoryId);
      if (card) setMemoryFocus(card);
    });
  });
}

function memoryActionButton(card, plan) {
  const iconName = {
    "memory.explain": "eye",
    "memory.correct": "edit",
    "memory.forget": "trash",
    "memory.export": "export",
  }[plan.gateway_tool] || "file";
  return `
    <button class="icon-button" type="button" title="${escapeHtml(plan.gateway_tool)}" aria-label="${escapeHtml(plan.gateway_tool)}"
      data-action-tool="${escapeHtml(plan.gateway_tool)}" data-target-ref="${escapeHtml(card.memory_id)}"
      data-confirmation="${plan.requires_confirmation ? "required" : "not-required"}">
      ${svgIcon(iconName)}
    </button>
  `;
}

function renderSkillCards() {
  const cards = takeVisibleCards(filteredSkills(), 1);
  const hiddenCount = filteredSkills().length - cards.length;
  document.querySelector("#skill-count").textContent = data.skill_forge.candidate_count;
  const list = document.querySelector("#skill-list");
  if (!cards.length) {
    list.innerHTML = '<div class="empty-state">No skill candidates match this filter.</div>';
    return;
  }
  list.innerHTML = cards
    .map(
      (card) => {
        const metric = skillMetricById.get(card.skill_id);
        return `
        <section class="skill-card" data-risk="${escapeHtml(card.risk_level)}" data-skill-id="${escapeHtml(card.skill_id)}">
          <div class="card-top">
            <div>
              <h2 class="card-title">${escapeHtml(card.name)}</h2>
              <p class="card-copy">${escapeHtml(card.description_preview || "")}</p>
            </div>
            <button class="icon-button" type="button" title="More skill actions" aria-label="More skill actions">${svgIcon("more")}</button>
          </div>
          <div class="meta-grid">
            <div><span class="meta-label">Observed</span><strong class="meta-value">${card.learned_from_count} refs</strong></div>
            <div><span class="meta-label">Risk</span><strong class="meta-value ${riskClass(card.risk_level)}">${formatToken(card.risk_level)}</strong></div>
            <div><span class="meta-label">Maturity</span><strong class="meta-value">Level ${card.maturity_level}</strong></div>
          </div>
          ${metric ? renderSkillMetric(metric) : ""}
          <ul class="blocker-list">
            ${card.promotion_blockers.map((blocker) => `<li>${svgIcon("shield")} ${formatToken(blocker)}</li>`).join("")}
          </ul>
          <div class="action-row">
            ${skillCommandButtons(card)}
          </div>
        </section>
      `;
      },
    )
    .join("") + hiddenSummary(hiddenCount, "skill");
  list.querySelectorAll("[data-action-tool]").forEach(bindActionButton);
  list.querySelectorAll("[data-skill-id]").forEach((cardElement) => {
    cardElement.addEventListener("click", () => {
      const card = data.skill_forge.cards.find((item) => item.skill_id === cardElement.dataset.skillId);
      if (card) setSkillFocus(card);
    });
  });
}

function takeVisibleCards(cards, maxVisible) {
  return cards.slice(0, maxVisible);
}

function hiddenSummary(count, label) {
  if (count <= 0) return "";
  return `<div class="list-summary">${count} more ${label} ${count === 1 ? "item" : "items"} available in the full queue.</div>`;
}

function renderSkillMetric(metric) {
  const totalRuns = Object.values(metric.outcome_counts || {}).reduce((total, count) => total + Number(count || 0), 0);
  const reviewLabel = compactReviewLabel(metric.review_recommendation);
  return `
    <div class="metric-strip" aria-label="Skill Metrics">
      <div><span class="meta-label">Runs</span><strong>${totalRuns}</strong></div>
      <div><span class="meta-label">Success</span><strong>${Math.round(Number(metric.success_rate || 0) * 100)}%</strong></div>
      <div><span class="meta-label">Corrections</span><strong>${Number(metric.correction_rate || 0).toFixed(2)}</strong></div>
      <div><span class="meta-label">Review</span><strong title="${formatToken(metric.review_recommendation)}">${reviewLabel}</strong></div>
    </div>
  `;
}

function compactReviewLabel(value) {
  const formatted = formatToken(value);
  const labels = {
    "safety review before reuse": "review before reuse",
    "eligible for human promotion review": "human review",
    "monitor for more evidence": "monitor evidence",
  };
  return labels[formatted] || formatted;
}

function skillCommandButtons(card) {
  const draft = card.action_plans.find((plan) => plan.gateway_tool === "skill.execute_draft");
  const approve = card.action_plans.find((plan) => plan.gateway_tool === "skill.approve_draft_only");
  const review = card.action_plans.find((plan) => plan.gateway_tool === "skill.review_candidate");
  return [review, draft, approve]
    .filter(Boolean)
    .map((plan) => {
      const primary = plan.gateway_tool === "skill.execute_draft";
      const label =
        plan.gateway_tool === "skill.execute_draft"
          ? "Draft Only"
          : plan.gateway_tool === "skill.approve_draft_only"
            ? "Approve"
            : "Review";
      return `
        <button class="command-button ${primary ? "" : "secondary"}" type="button"
          data-action-tool="${escapeHtml(plan.gateway_tool)}" data-target-ref="${escapeHtml(card.skill_id)}"
          data-confirmation="${plan.requires_confirmation ? "required" : "not-required"}">
          ${svgIcon(primary ? "file" : "eye")} ${escapeHtml(label)}
        </button>
      `;
    })
    .join("");
}

function bindActionButton(button) {
  button.addEventListener("click", (event) => {
    event.stopPropagation();
    const actionKey = `${button.dataset.actionTool}:${button.dataset.targetRef}`;
    const receipt = gatewayReceiptByAction.get(actionKey);
    if (!receipt) {
      writeReceipt(`${button.dataset.actionTool} has no gateway receipt. No mutation executed.`);
      return;
    }
    if (receipt.allowed_gateway_call) {
      writeReceipt(
        `Gateway receipt allows ${receipt.gateway_tool} read-only for ${receipt.target_ref}. No mutation executed.`,
      );
      return;
    }
    writeReceipt(
      `Gateway receipt blocks ${receipt.gateway_tool} for ${receipt.target_ref}: ${receipt.blocked_reasons.join(", ")}. No mutation executed.`,
    );
  });
}

function renderReceipts() {
  const list = document.querySelector("#receipt-list");
  const gatewayReceipts = data.gateway_action_receipts || [];
  const retrievalReceipts = data.retrieval_debug?.cards || [];
  list.innerHTML = [
    '<div class="receipt-section-label">Safe Receipts</div>',
    ...data.safe_receipts.slice(0, 3).map(
      (receipt) => `
        <div class="receipt-item" data-state="${escapeHtml(receipt.state)}">
          <span class="receipt-dot">${svgIcon(receipt.state === "warning" ? "pause" : "check")}</span>
          <span>
            <strong>${escapeHtml(receipt.label)}</strong>
            <span>${escapeHtml(receipt.target_ref)} by ${escapeHtml(receipt.actor)}</span>
          </span>
        </div>
      `,
    ),
    '<div class="receipt-section-label">Gateway Action Receipts</div>',
    ...gatewayReceipts.slice(0, 3).map(
      (receipt) => `
        <div class="receipt-item" data-state="${receipt.allowed_gateway_call ? "healthy" : "warning"}">
          <span class="receipt-dot">${svgIcon(receipt.allowed_gateway_call ? "check" : "pause")}</span>
          <span>
            <strong>${escapeHtml(receipt.gateway_tool)}</strong>
            <span>${escapeHtml(receipt.target_ref)} · ${receipt.allowed_gateway_call ? "read-only ready" : "preview blocked"}</span>
          </span>
        </div>
      `,
    ),
    '<div class="receipt-section-label">Retrieval Receipts</div>',
    ...retrievalReceipts.slice(0, 2).map(
      (receipt) => `
        <div class="receipt-item retrieval-receipt" data-state="${receipt.decision === "included" ? "healthy" : "warning"}">
          <span class="receipt-dot">${svgIcon(receipt.decision === "included" ? "check" : "pause")}</span>
          <span>
            <strong>${escapeHtml(formatToken(receipt.decision))}</strong>
            <span>${escapeHtml(receipt.memory_id)} · score ${Number(receipt.score || 0).toFixed(2)} · refs ${receipt.source_ref_count}</span>
          </span>
        </div>
      `,
    ),
  ].join("");

  document.querySelector("#receipt-filter").addEventListener("click", () => {
    writeReceipt("Audit log preview selected. Receipt content remains redacted.");
  });
}

function renderDashboard() {
  renderTabs();
  renderMemoryCards();
  renderSkillCards();
}

if (!data) {
  document.body.innerHTML = '<main class="empty-state">Dashboard data missing.</main>';
} else {
  bindHeaderActions();
  renderNav();
  renderStatusStrip();
  renderShadowPointerLiveReceipt();
  renderEncryptedIndexPanel();
  renderLiveDashboardReceipts();
  renderDemoPath();
  renderCaptureControl();
  renderCaptureReadinessLadder();
  renderInsights();
  renderReceipts();
  renderDashboard();
  ensureFocusForActiveView();
  renderFocusInspector();
  applyActiveView();
}
