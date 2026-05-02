const data = window.CORTEX_DASHBOARD_DATA;

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
  document.querySelector("#interaction-receipt").textContent = message;
}

function renderNav() {
  const nav = document.querySelector("#nav-list");
  nav.innerHTML = data.nav_items
    .map(
      (item) => `
        <button class="nav-item ${item.active ? "active" : ""}" type="button" data-nav="${escapeHtml(item.item_id)}" title="${escapeHtml(item.label)}">
          ${svgIcon(item.item_id)}
          <span class="label">${escapeHtml(item.label)}</span>
          ${Number.isInteger(item.count) ? `<span class="nav-count">${item.count}</span>` : ""}
        </button>
      `,
    )
    .join("");

  nav.querySelectorAll(".nav-item").forEach((button) => {
    button.addEventListener("click", () => {
      nav.querySelectorAll(".nav-item").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      writeReceipt(`${button.textContent.trim()} selected. No gateway action executed.`);
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
  selectedFocus = {
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
  renderFocusInspector();
}

function setSkillFocus(card) {
  selectedFocus = {
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
  renderDemoPath();
  renderInsights();
  renderFocusInspector();
  renderReceipts();
  renderDashboard();
}
