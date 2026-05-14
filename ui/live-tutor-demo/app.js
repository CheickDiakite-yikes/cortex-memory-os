const frame = document.querySelector("#studio-frame");
const highlight = document.querySelector("#target-highlight");
const traceLayer = document.querySelector("#cursor-trace-layer");
const cursor = document.querySelector("#shadow-tutor-cursor");
const talkCard = document.querySelector("#cursor-talk-card");
const pointerStatusLabel = document.querySelector("#pointer-status-label");
const pointerTargetLabel = document.querySelector("#pointer-target-label");
const pointerSafetyLabel = document.querySelector("#pointer-safety-label");
const bubble = document.querySelector("#instruction-bubble");
const wakeCard = document.querySelector("#wake-card");
const wakeHelperButton = document.querySelector("#wake-helper");
const dockState = document.querySelector("#dock-state");
const dockSummary = document.querySelector("#dock-summary");
const pinnedTargets = document.querySelector("#pinned-targets");
const memoryProposalCard = document.querySelector("#memory-proposal-card");
const memoryProposalTarget = document.querySelector("#memory-proposal-target");
const memoryProposalPreview = document.querySelector("#memory-proposal-preview");
const reviewMemoryProposal = document.querySelector("#review-memory-proposal");
const dismissMemoryProposal = document.querySelector("#dismiss-memory-proposal");
const form = document.querySelector("#question-form");
const input = document.querySelector("#question-input");
const token = document.querySelector('meta[name="cortex-live-tutor-token"]')?.content || "";
const activePageChip = document.querySelector("#active-page-chip");
const aiModeChip = document.querySelector("#ai-mode-chip");
const aiModeNote = document.querySelector("#ai-mode-note");
const turnList = document.querySelector("#turn-list");
const receiptSummary = document.querySelector("#receipt-summary");
const receiptsToggle = document.querySelector("#receipts-toggle");
const receiptStack = document.querySelector("#receipt-stack");
const aiModeButtons = document.querySelectorAll("[data-ai-mode]");
const fields = {
  target: document.querySelector("#receipt-target"),
  intent: document.querySelector("#receipt-intent"),
  referent: document.querySelector("#receipt-referent"),
  confidence: document.querySelector("#receipt-confidence"),
  aiMode: document.querySelector("#receipt-ai-mode"),
  effects: document.querySelector("#receipt-effects"),
  blocked: document.querySelector("#receipt-blocked"),
};

let activePage = "edit";
let aiMode = "local";
let lastTraceAt = 0;
let followerVisible = false;
let helperActive = false;
let currentTargetId = null;
let currentTargetLabel = "this surface";
let previousTargetId = null;
let selectedTargetIds = [];
let pinnedTargetIds = [];
let lastPointer = { x: null, y: null };

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
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
  return String(value || "").replaceAll("_", " ");
}

async function askTutor(question) {
  if (!helperActive) {
    setHelperActive(true);
  }
  fields.intent.textContent = aiMode === "openai_dry_run" ? "thinking safely" : "thinking";
  fields.aiMode.textContent = aiMode === "openai_dry_run" ? "AI draft" : "local";
  pointerSafetyLabel.textContent =
    aiMode === "openai_dry_run"
      ? "AI draft uses controlled facts only."
      : "Display only. You stay in control.";
  const response = await fetch("/tutor/turn", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Cortex-Live-Tutor-Token": token,
    },
    body: JSON.stringify({
      user_utterance: question,
      active_page: activePage,
      ai_mode: aiMode,
      pointed_target_id: currentTargetId,
      previous_target_id: previousTargetId,
      selected_target_ids: pinnedTargetIds.length ? pinnedTargetIds : selectedTargetIds,
      pointer_x: lastPointer.x,
      pointer_y: lastPointer.y,
    }),
  });
  const payload = await response.json();
  if (!response.ok) {
    renderError(payload);
    return;
  }
  renderTurn(payload);
}

function renderError(payload) {
  fields.target.textContent = "blocked";
  fields.intent.textContent = payload.error || "rejected";
  fields.referent.textContent = "none";
  fields.confidence.textContent = "0.00";
  fields.aiMode.textContent = "blocked";
  fields.effects.textContent = "none";
  fields.blocked.textContent = "request rejected before receipt";
  receiptSummary.textContent = "Request blocked before Cortex produced a pointer receipt.";
  dockState.textContent = "Blocked";
  dockSummary.textContent = "No action was taken.";
  bubble.textContent = "That request was blocked before any tutor cue.";
}

function targetLabel(targetId) {
  if (!targetId) return "this surface";
  const element = document.querySelector(`[data-target-id="${targetId}"]`);
  if (!element) return targetId.replaceAll("_", " ");
  return (
    element.getAttribute("aria-label") ||
    element.querySelector("h2")?.textContent ||
    element.textContent ||
    targetId.replaceAll("_", " ")
  ).trim();
}

function setAiMode(mode) {
  aiMode = mode === "openai_dry_run" ? "openai_dry_run" : "local";
  document.body.classList.toggle("ai-draft-mode", aiMode === "openai_dry_run");
  aiModeButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.aiMode === aiMode);
  });
  aiModeChip.textContent = aiMode === "openai_dry_run" ? "AI draft safe" : "Local answers";
  aiModeNote.textContent =
    aiMode === "openai_dry_run"
      ? "Uses controlled target facts only with store:false receipts."
      : "No network from the UI. Live OpenAI smoke stays in CLI.";
  pointerSafetyLabel.textContent =
    aiMode === "openai_dry_run"
      ? "AI draft: store:false, controlled facts only."
      : "Display only. You stay in control.";
  fields.aiMode.textContent = aiMode === "openai_dry_run" ? "AI draft" : "local";
}

function updatePointerTarget(targetId) {
  if (targetId && targetId !== currentTargetId) {
    previousTargetId = currentTargetId;
    currentTargetId = targetId;
    currentTargetLabel = targetLabel(targetId);
    selectedTargetIds = [previousTargetId, currentTargetId].filter(Boolean).slice(-4);
  }
  pointerStatusLabel.textContent = currentTargetId ? "Cortex sees" : "Cortex nearby";
  pointerTargetLabel.textContent = currentTargetLabel;
  fields.target.textContent = currentTargetLabel;
  renderPinnedTargets();
}

function targetFromEvent(event) {
  const element = event.target?.closest?.("[data-target-id]");
  return element?.dataset?.targetId || null;
}

function placeTutorFollower(x, y, { trace = true } = {}) {
  if (!helperActive) return;
  const frameRect = frame.getBoundingClientRect();
  lastPointer = {
    x: Math.round(clamp(x, 0, frameRect.width)),
    y: Math.round(clamp(y, 0, frameRect.height)),
  };
  const followerX = clamp(x + 18, 10, frameRect.width - 84);
  const followerY = clamp(y + 18, 10, frameRect.height - 58);

  cursor.style.left = `${followerX}px`;
  cursor.style.top = `${followerY}px`;
  cursor.classList.add("visible", "tracking");

  talkCard.style.left = `${clamp(followerX + 42, 8, frameRect.width - 220)}px`;
  talkCard.style.top = `${clamp(followerY + 22, 8, frameRect.height - 62)}px`;
  talkCard.classList.add("visible");

  if (!followerVisible) {
    fields.effects.textContent = "tracking cursor, rendering trace, display-only";
    followerVisible = true;
  }

  if (!trace) return;
  const now = Date.now();
  if (now - lastTraceAt < 46) return;
  lastTraceAt = now;

  const dot = document.createElement("span");
  dot.className = "cursor-trace-dot";
  dot.style.left = `${clamp(x, 8, frameRect.width - 8)}px`;
  dot.style.top = `${clamp(y, 8, frameRect.height - 8)}px`;
  traceLayer.append(dot);
  window.setTimeout(() => dot.remove(), 820);
}

function handlePointerMove(event) {
  if (!helperActive) return;
  const frameRect = frame.getBoundingClientRect();
  updatePointerTarget(targetFromEvent(event));
  placeTutorFollower(event.clientX - frameRect.left, event.clientY - frameRect.top);
}

function setHelperActive(active) {
  helperActive = active;
  document.body.classList.toggle("helper-active", active);
  wakeCard.classList.toggle("hidden", active);
  talkCard.classList.toggle("visible", active);
  dockState.textContent = active ? "Pointer awake" : "Pointer off";
  dockSummary.textContent = active
    ? "Move over the studio. Cortex will stay beside your pointer."
    : "Start helper to see Cortex follow inside this safe demo.";
}

function wakeHelper() {
  if (helperActive) return;
  setHelperActive(true);
  bubble.textContent = "Pointer helper is awake. Move over a tool or ask a question.";
  bubble.classList.add("visible");
  askTutor(input.value.trim() || "How do I start color grading?");
}

function renderPinnedTargets() {
  const ids = pinnedTargetIds.length ? pinnedTargetIds : selectedTargetIds;
  pinnedTargets.innerHTML = "";
  ids.slice(-4).forEach((targetId) => {
    const chip = document.createElement("span");
    chip.textContent = targetLabel(targetId);
    chip.className = pinnedTargetIds.includes(targetId) ? "pinned" : "";
    pinnedTargets.append(chip);
  });
}

function pinCurrentTarget() {
  if (!currentTargetId) {
    dockSummary.textContent = "Point at a target before pinning it.";
    return;
  }
  if (pinnedTargetIds.includes(currentTargetId)) {
    pinnedTargetIds = pinnedTargetIds.filter((targetId) => targetId !== currentTargetId);
    dockSummary.textContent = `${currentTargetLabel} removed from the target stack.`;
  } else {
    pinnedTargetIds = [...pinnedTargetIds, currentTargetId].slice(-4);
    dockSummary.textContent = `${currentTargetLabel} pinned. Ask about "these" to use the stack.`;
  }
  renderPinnedTargets();
}

function showMemoryProposal(proposal) {
  if (!proposal) {
    memoryProposalCard.classList.remove("visible");
    return;
  }
  memoryProposalTarget.textContent = proposal.target_label;
  memoryProposalPreview.textContent = proposal.content_preview;
  memoryProposalCard.classList.add("visible");
}

function renderTurn(turn) {
  const target = document.querySelector(`[data-target-id="${turn.target_id}"]`);
  if (!target) {
    renderError({ error: "target_missing" });
    return;
  }
  const rect = target.getBoundingClientRect();
  const frameRect = frame.getBoundingClientRect();
  const left = rect.left - frameRect.left;
  const top = rect.top - frameRect.top;
  const centerX = left + rect.width / 2;
  const centerY = top + rect.height / 2;

  highlight.style.left = `${left}px`;
  highlight.style.top = `${top}px`;
  highlight.style.width = `${rect.width}px`;
  highlight.style.height = `${rect.height}px`;
  highlight.classList.add("visible");

  cursor.style.left = `${centerX}px`;
  cursor.style.top = `${centerY}px`;
  cursor.classList.add("visible", "pulse");
  window.setTimeout(() => cursor.classList.remove("pulse"), 360);
  followerVisible = false;
  updatePointerTarget(turn.target_id);
  const bubbleX = clamp(centerX + 28, 8, frameRect.width - 330);
  const bubbleY = clamp(centerY - 132, 18, frameRect.height - 180);
  talkCard.style.left = `${clamp(centerX + 42, 8, frameRect.width - 232)}px`;
  talkCard.style.top = `${clamp(bubbleY + 96, 8, frameRect.height - 88)}px`;
  talkCard.classList.add("visible");
  pointerSafetyLabel.textContent =
    turn.companion_state?.safety_caption || "Display only. You stay in control.";

  bubble.style.left = `${bubbleX}px`;
  bubble.style.top = `${bubbleY}px`;
  bubble.textContent = turn.assistant_response;
  bubble.classList.add("visible");

  fields.target.textContent = turn.target_label;
  fields.intent.textContent = formatToken(turn.intent_label);
  fields.referent.textContent = turn.pointer_referent || "none";
  fields.confidence.textContent = Number(turn.confidence).toFixed(2);
  fields.aiMode.textContent =
    turn.ai_assist_mode === "openai_dry_run" && turn.ai_model
      ? `${turn.ai_model} store:false`
      : "local";
  const effectText = turn.target_coordinates.allowed_effects
    .map(formatToken)
    .slice(1, 4)
    .join(", ");
  fields.effects.textContent =
    turn.ai_assist_mode === "openai_dry_run" ? `${effectText}, AI draft` : effectText;
  fields.blocked.textContent = "click, type, capture, memory, export";
  receiptSummary.textContent =
    turn.user_readable_receipt || "Cortex answered safely beside the pointer.";
  dockState.textContent = turn.companion_state?.label || `Pointing at ${turn.target_label}`;
  dockSummary.textContent = turn.micro_steps?.[0] || turn.next_user_action;
  showMemoryProposal(turn.manual_memory_proposal);

  const item = document.createElement("li");
  const proposalText = turn.manual_memory_proposal ? " · memory proposal needs review" : "";
  const aiText =
    turn.ai_assist_mode === "openai_dry_run" && turn.ai_model
      ? ` · AI ${escapeHtml(turn.ai_model)} store:false`
      : "";
  item.innerHTML = `<strong>${escapeHtml(turn.target_label)}</strong><span>${escapeHtml(turn.user_readable_receipt || formatToken(turn.intent_label))} · ${escapeHtml(turn.pointer_referent || "none")} · confidence ${Number(turn.confidence).toFixed(2)} · raw refs ${turn.raw_ref_retained ? "retained" : "none"}${aiText}${proposalText}</span>`;
  turnList.prepend(item);
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  askTutor(input.value.trim() || "What should I click next?");
});

document.querySelectorAll(".quick-prompts button").forEach((button) => {
  button.addEventListener("click", () => {
    input.value = button.textContent;
    askTutor(button.textContent);
  });
});

document.querySelector("#color-page-button").addEventListener("click", () => {
  activePage = "color";
  activePageChip.textContent = "Color page";
  bubble.textContent = "User switched the demo state to Color. Cortex did not click for you.";
  bubble.classList.add("visible");
});

frame.addEventListener("pointerenter", (event) => {
  if (!helperActive) return;
  const frameRect = frame.getBoundingClientRect();
  updatePointerTarget(targetFromEvent(event));
  placeTutorFollower(event.clientX - frameRect.left, event.clientY - frameRect.top, {
    trace: false,
  });
});

frame.addEventListener("pointermove", handlePointerMove);

frame.addEventListener("pointerleave", () => {
  dockSummary.textContent = helperActive
    ? "Pointer helper is still awake inside the safe demo surface."
    : "Start helper to see Cortex follow inside this safe demo.";
});

document.querySelectorAll("[data-pointer-command]").forEach((button) => {
  button.addEventListener("click", (event) => {
    event.stopPropagation();
    const command = button.dataset.pointerCommand || "Explain this";
    input.value = command;
    askTutor(command);
  });
});

document.querySelectorAll("[data-pointer-ai]").forEach((button) => {
  button.addEventListener("click", (event) => {
    event.stopPropagation();
    setAiMode(button.dataset.pointerAi || "openai_dry_run");
    input.value = currentTargetId ? "Explain this" : "What should I click next?";
    askTutor(input.value);
  });
});

document.querySelectorAll("[data-pointer-local]").forEach((button) => {
  button.addEventListener("click", (event) => {
    event.stopPropagation();
    if (button.dataset.pointerLocal === "pin-target") {
      pinCurrentTarget();
    }
  });
});

aiModeButtons.forEach((button) => {
  button.addEventListener("click", () => {
    setAiMode(button.dataset.aiMode || "local");
  });
});

talkCard.addEventListener("click", (event) => {
  if (event.target?.matches?.("button")) return;
  input.value = currentTargetId ? "Explain this" : "What should I click next?";
  input.focus();
  input.select();
  bubble.textContent = currentTargetId
    ? `I understand ${currentTargetLabel}. Use the tiny actions beside the pointer.`
    : "I am tracking beside your cursor. Point at something and ask.";
  bubble.classList.add("visible");
});

wakeHelperButton.addEventListener("click", wakeHelper);

reviewMemoryProposal.addEventListener("click", () => {
  receiptSummary.textContent =
    "Memory proposal opened for review. It still has not been saved.";
  dockState.textContent = "Review memory";
  dockSummary.textContent = "Save only from the Memory Book after checking the card.";
});

dismissMemoryProposal.addEventListener("click", () => {
  memoryProposalCard.classList.remove("visible");
  receiptSummary.textContent = "Memory proposal dismissed. Nothing was saved.";
  dockState.textContent = "Proposal dismissed";
  dockSummary.textContent = "Cortex will keep pointing without saving that memory.";
});

receiptsToggle.addEventListener("click", () => {
  const collapsed = receiptStack.classList.toggle("collapsed");
  receiptsToggle.textContent = collapsed ? "Show safety receipts" : "Hide safety receipts";
});

setAiMode("local");
