const frame = document.querySelector("#studio-frame");
const highlight = document.querySelector("#target-highlight");
const traceLayer = document.querySelector("#cursor-trace-layer");
const cursor = document.querySelector("#shadow-tutor-cursor");
const talkCard = document.querySelector("#cursor-talk-card");
const pointerStatusLabel = document.querySelector("#pointer-status-label");
const pointerTargetLabel = document.querySelector("#pointer-target-label");
const pointerEntityLabel = document.querySelector("#pointer-entity-label");
const pointerRouteChip = document.querySelector("#pointer-route-chip");
const pointerConfidenceChip = document.querySelector("#pointer-confidence-chip");
const pointerTourStrip = document.querySelector("#pointer-tour-strip");
const pointerSafetyLabel = document.querySelector("#pointer-safety-label");
const pointerCommandSuggestions = document.querySelector("#pointer-command-suggestions");
const pointerThisChip = document.querySelector("#pointer-this-chip");
const pointerThatChip = document.querySelector("#pointer-that-chip");
const pointerTheseChip = document.querySelector("#pointer-these-chip");
const bubble = document.querySelector("#instruction-bubble");
const receiptToast = document.querySelector("#pointer-receipt-toast");
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
const voiceStatusChip = document.querySelector("#voice-status-chip");
const voiceOutputChip = document.querySelector("#voice-output-chip");
const voiceGestureHint = document.querySelector("#voice-gesture-hint");
const turnList = document.querySelector("#turn-list");
const receiptSummary = document.querySelector("#receipt-summary");
const receiptsToggle = document.querySelector("#receipts-toggle");
const receiptStack = document.querySelector("#receipt-stack");
const aiModeButtons = document.querySelectorAll("[data-ai-mode]");
const DEMO_VIEWPORT_WIDTH = 1440;
const DEMO_VIEWPORT_HEIGHT = 960;
const TOUR_STEPS = [
  {
    targetId: "color_page_button",
    title: "Step 1 of 4",
    prompt: "Start color grading by opening Color yourself.",
  },
  {
    targetId: "node_graph",
    title: "Step 2 of 4",
    prompt: "The node graph is where the grade is built.",
  },
  {
    targetId: "lut_menu",
    title: "Step 3 of 4",
    prompt: "Preview looks from the LUT menu before applying anything.",
  },
  {
    targetId: "inspector",
    title: "Step 4 of 4",
    prompt: "Use Inspector settings to make small, reversible adjustments.",
  },
];
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
let voiceGestureType = "single_click_context";
let lastTraceAt = 0;
let holdTimer = null;
let holdStartedAt = 0;
let followerVisible = false;
let helperActive = false;
let currentTargetId = null;
let currentTargetLabel = "this surface";
let previousTargetId = null;
let selectedTargetIds = [];
let pinnedTargetIds = [];
let tourActive = false;
let tourIndex = 0;
let lastPointer = { x: null, y: null };
let pendingFollowerFrame = null;
let pendingFollowerPlacement = null;

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

function shortLabel(value, fallback = "none") {
  const label = String(value || fallback).trim();
  return label.length > 22 ? `${label.slice(0, 19)}...` : label;
}

function safePointerForRequest() {
  const frameRect = frame.getBoundingClientRect();
  return {
    x:
      lastPointer.x === null
        ? null
        : Math.round(clamp(lastPointer.x, 0, frameRect.width)),
    y:
      lastPointer.y === null
        ? null
        : Math.round(clamp(lastPointer.y, 0, frameRect.height)),
    width: Math.round(frameRect.width),
    height: Math.round(frameRect.height),
    coordinateSpace: "client_surface_css",
  };
}

function setVoiceGesture(type) {
  const known = {
    triple_click_voice_dialogue: {
      status: "Voice dialogue",
      output: "Brief voice",
      hint: "Triple click routes to a short spoken answer, gated by the cost guard.",
    },
    press_hold_text_reply: {
      status: "Hold to ask",
      output: "Text reply",
      hint: "Click and hold asks with voice intent but answers as text beside the pointer.",
    },
    press_hold_action_only: {
      status: "Silent action",
      output: "No voice back",
      hint: "Action-only mode moves the guide cue and stays silent.",
    },
    drag_select_targets: {
      status: "Selection",
      output: "Text reply",
      hint: "Selected targets can be explained together before any workflow is saved.",
    },
    single_click_context: {
      status: "Voice safe demo",
      output: "Text first",
      hint: "Triple click for voice. Hold for text. Hold with silent mode for action-only.",
    },
  };
  voiceGestureType = known[type] ? type : "single_click_context";
  voiceStatusChip.textContent = known[voiceGestureType].status;
  voiceOutputChip.textContent = known[voiceGestureType].output;
  voiceGestureHint.textContent = known[voiceGestureType].hint;
}

async function askTutor(question, options = {}) {
  if (!helperActive) {
    setHelperActive(true);
  }
  const gestureForRequest = options.voiceGestureType || voiceGestureType;
  const pointerForRequest = safePointerForRequest();
  fields.intent.textContent = aiMode === "openai_dry_run" ? "thinking safely" : "thinking";
  fields.aiMode.textContent = aiMode === "openai_dry_run" ? "AI draft" : "local";
  pointerSafetyLabel.textContent =
    aiMode === "openai_dry_run"
      ? "AI draft uses controlled facts only."
      : "Display only. You stay in control.";
  setThinkingState(true);
  try {
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
        voice_gesture_type: gestureForRequest,
        pointed_target_id: currentTargetId,
        previous_target_id: previousTargetId,
        selected_target_ids: pinnedTargetIds.length ? pinnedTargetIds : selectedTargetIds,
        pointer_coordinate_space: pointerForRequest.coordinateSpace,
        pointer_x: pointerForRequest.x,
        pointer_y: pointerForRequest.y,
        client_surface_width: pointerForRequest.width,
        client_surface_height: pointerForRequest.height,
      }),
    });
    const payload = await response.json();
    if (!response.ok) {
      renderError(payload);
      return;
    }
    renderTurn(payload);
  } finally {
    setThinkingState(false);
  }
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
  showReceiptToast("Request blocked. No action was taken.");
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

function targetMeta(targetId) {
  const element = targetId ? document.querySelector(`[data-target-id="${targetId}"]`) : null;
  return {
    entityKind: element?.dataset?.entityKind || "controlled demo entity",
    role: element?.dataset?.targetRole || "safe local target",
  };
}

function setCursorPosition(x, y) {
  cursor.style.transform = `translate3d(${Math.round(x - 8)}px, ${Math.round(
    y - 8
  )}px, 0)`;
}

function renderCommandSuggestions(suggestions = ["Explain this", "What next?", "Remember this"]) {
  const labels = suggestions.slice(0, 3);
  pointerCommandSuggestions.innerHTML = "";
  labels.forEach((label) => {
    const button = document.createElement("button");
    button.type = "button";
    button.dataset.pointerCommand = label;
    button.textContent =
      label === "Explain this"
        ? "Explain"
        : label === "What next?"
          ? "Next"
          : label === "Remember this"
            ? "Remember"
            : label.replace(" memory", "");
    const targetRequired = /explain this|remember this/i.test(label);
    button.disabled = targetRequired && !currentTargetId;
    if (button.disabled) {
      button.title = "Point at something first";
    }
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      if (!currentTargetId && /explain this|remember this/i.test(label)) {
        dockState.textContent = "Point first";
        dockSummary.textContent = "Move over a tool, then ask about this.";
        bubble.textContent = "Point at something first so I know what 'this' means.";
        bubble.classList.add("visible");
        return;
      }
      setVoiceGesture("single_click_context");
      input.value = label;
      askTutor(label);
    });
    pointerCommandSuggestions.append(button);
  });
}

function setThinkingState(active) {
  document.body.classList.toggle("pointer-thinking", active);
  pointerStatusLabel.textContent = active
    ? "Cortex thinking"
    : currentTargetId
      ? "Cortex sees"
      : "Cortex nearby";
  pointerRouteChip.textContent = active ? "Thinking safely" : "Show only";
}

function showReceiptToast(text) {
  receiptToast.textContent = text || "Pointer receipt updated.";
  receiptToast.classList.add("visible");
  window.clearTimeout(showReceiptToast.hideTimer);
  showReceiptToast.hideTimer = window.setTimeout(() => {
    receiptToast.classList.remove("visible");
  }, 2800);
}

function updateContextChips(flowState = null) {
  const currentLabel = flowState?.current_target_label || currentTargetLabel;
  const previousLabel = flowState?.previous_target_label || targetLabel(previousTargetId);
  const selectedLabels =
    flowState?.selected_target_labels ||
    (pinnedTargetIds.length ? pinnedTargetIds : selectedTargetIds).map((targetId) =>
      targetLabel(targetId)
    );
  pointerThisChip.textContent = `This: ${shortLabel(currentTargetId ? currentLabel : "surface")}`;
  pointerThatChip.textContent = `That: ${shortLabel(previousTargetId ? previousLabel : "none")}`;
  pointerTheseChip.textContent = `Stack: ${selectedLabels.filter(Boolean).length}`;
}

function setHoverHighlight(targetId) {
  if (!helperActive || !targetId) {
    if (!document.body.classList.contains("pointer-thinking")) {
      highlight.classList.remove("visible", "hovering");
    }
    return;
  }
  const target = document.querySelector(`[data-target-id="${targetId}"]`);
  if (!target) return;
  const rect = target.getBoundingClientRect();
  const frameRect = frame.getBoundingClientRect();
  highlight.style.left = `${rect.left - frameRect.left}px`;
  highlight.style.top = `${rect.top - frameRect.top}px`;
  highlight.style.width = `${rect.width}px`;
  highlight.style.height = `${rect.height}px`;
  highlight.classList.add("visible", "hovering");
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
  pointerRouteChip.textContent =
    aiMode === "openai_dry_run" ? "AI draft · show only" : "Show only";
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
  const meta = targetMeta(currentTargetId);
  pointerEntityLabel.textContent = `${meta.entityKind} · ${meta.role}`;
  pointerConfidenceChip.textContent = currentTargetId ? "Confidence live" : "Confidence --";
  updateContextChips();
  renderCommandSuggestions();
  setHoverHighlight(currentTargetId);
  fields.target.textContent = currentTargetLabel;
  renderPinnedTargets();
}

function placeCueOnTarget(targetId, { pulse = false } = {}) {
  const target = document.querySelector(`[data-target-id="${targetId}"]`);
  if (!target) return null;
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
  highlight.classList.remove("hovering");
  setCursorPosition(centerX, centerY);
  cursor.classList.add("visible");
  if (pulse) {
    cursor.classList.add("pulse");
    window.setTimeout(() => cursor.classList.remove("pulse"), 360);
  }
  placeFloatingElement(talkCard, centerX, centerY, {
    fallbackWidth: 232,
    fallbackHeight: 76,
    gap: 14,
    anchor: "target",
  });
  talkCard.classList.add("visible");
  return { centerX, centerY };
}

function renderTourStep() {
  if (!tourActive) return;
  const step = TOUR_STEPS[tourIndex];
  const point = placeCueOnTarget(step.targetId, { pulse: true });
  updatePointerTarget(step.targetId);
  pointerTourStrip.textContent = `${step.title}: ${targetLabel(step.targetId)}`;
  pointerRouteChip.textContent = "Tour · show only";
  pointerConfidenceChip.textContent = "Confidence guided";
  dockState.textContent = "Guided tour";
  dockSummary.textContent = step.prompt;
  bubble.textContent = step.prompt;
  bubble.classList.add("visible");
  if (point) {
    placeFloatingElement(bubble, point.centerX, point.centerY, {
      fallbackWidth: 318,
      fallbackHeight: 88,
      gap: 22,
      anchor: "target",
    });
  }
  showReceiptToast("Tour cue rendered only. Cortex did not click or save.");
}

function startGuidedTour() {
  if (!helperActive) {
    setHelperActive(true);
  }
  tourActive = true;
  tourIndex = 0;
  document.body.classList.add("tour-active");
  renderTourStep();
}

function advanceGuidedTour() {
  if (!tourActive) {
    startGuidedTour();
    return;
  }
  tourIndex = (tourIndex + 1) % TOUR_STEPS.length;
  renderTourStep();
}

function stopGuidedTour() {
  tourActive = false;
  tourIndex = 0;
  document.body.classList.remove("tour-active");
  pointerTourStrip.textContent = "Tour off";
  pointerRouteChip.textContent = aiMode === "openai_dry_run" ? "AI draft · show only" : "Show only";
  dockState.textContent = "Tour stopped";
  dockSummary.textContent = "Cortex will keep following your pointer.";
}

function targetFromEvent(event) {
  const element = event.target?.closest?.("[data-target-id]");
  return element?.dataset?.targetId || null;
}

function floatingSize(element, fallbackWidth, fallbackHeight) {
  const rect = element.getBoundingClientRect();
  return {
    width: rect.width || fallbackWidth,
    height: rect.height || fallbackHeight,
  };
}

function placeFloatingElement(element, anchorX, anchorY, options = {}) {
  const frameRect = frame.getBoundingClientRect();
  const margin = options.margin ?? 12;
  const gap = options.gap ?? 18;
  const size = floatingSize(
    element,
    options.fallbackWidth ?? 240,
    options.fallbackHeight ?? 72
  );
  const fitsRight = anchorX + gap + size.width <= frameRect.width - margin;
  const x = fitsRight ? anchorX + gap : anchorX - gap - size.width;
  const y = clamp(anchorY - size.height / 2, margin, frameRect.height - size.height - margin);
  element.style.left = `${clamp(x, margin, frameRect.width - size.width - margin)}px`;
  element.style.top = `${y}px`;
  element.dataset.anchorSide = fitsRight ? "right" : "left";
  element.dataset.anchor = options.anchor || "cursor";
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

  pendingFollowerPlacement = { followerX, followerY };
  if (!pendingFollowerFrame) {
    pendingFollowerFrame = window.requestAnimationFrame(() => {
      const placement = pendingFollowerPlacement;
      pendingFollowerFrame = null;
      if (!placement) return;
      setCursorPosition(placement.followerX, placement.followerY);
      cursor.classList.add("visible", "tracking");
      placeFloatingElement(talkCard, placement.followerX + 24, placement.followerY + 20, {
        fallbackWidth: 232,
        fallbackHeight: 76,
        gap: 12,
        anchor: "cursor",
      });
      talkCard.classList.add("visible");
    });
  }

  if (!followerVisible) {
    fields.effects.textContent = "tracking cursor, rendering trace, display-only";
    followerVisible = true;
  }

  if (!trace) return;
  const now = Date.now();
  if (now - lastTraceAt < 72) return;
  lastTraceAt = now;

  const dot = document.createElement("span");
  dot.className = "cursor-trace-dot";
  dot.style.left = `${clamp(x, 8, frameRect.width - 8)}px`;
  dot.style.top = `${clamp(y, 8, frameRect.height - 8)}px`;
  traceLayer.append(dot);
  window.setTimeout(() => dot.remove(), 620);
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

function wakeHelper(event) {
  if (helperActive) return;
  setHelperActive(true);
  highlight.classList.remove("visible");
  currentTargetId = null;
  previousTargetId = null;
  currentTargetLabel = "this surface";
  updatePointerTarget(null);
  renderCommandSuggestions();
  const frameRect = frame.getBoundingClientRect();
  const fallbackX = frameRect.width / 2;
  const fallbackY = Math.min(frameRect.height / 2, 340);
  const localX = event?.clientX ? event.clientX - frameRect.left : fallbackX;
  const localY = event?.clientY ? event.clientY - frameRect.top : fallbackY;
  placeTutorFollower(localX, localY, { trace: false });
  bubble.textContent = "Pointer helper is awake. Move over any tool; I will follow you.";
  bubble.classList.add("visible");
  placeFloatingElement(bubble, localX + 24, localY + 18, {
    fallbackWidth: 300,
    fallbackHeight: 72,
    gap: 18,
    anchor: "cursor",
  });
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
  updateContextChips();
}

function selectCurrentTarget() {
  if (!currentTargetId) {
    dockSummary.textContent = "Point at a target before selecting it.";
    return;
  }
  if (selectedTargetIds.includes(currentTargetId)) {
    selectedTargetIds = selectedTargetIds.filter((targetId) => targetId !== currentTargetId);
    dockSummary.textContent = `${currentTargetLabel} removed from the selection.`;
  } else {
    selectedTargetIds = [...selectedTargetIds, currentTargetId].slice(-4);
    dockSummary.textContent = `${currentTargetLabel} selected. Ask about "these" for a grouped answer.`;
  }
  setVoiceGesture(selectedTargetIds.length > 1 ? "drag_select_targets" : "single_click_context");
  renderPinnedTargets();
  updateContextChips();
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
  const point = placeCueOnTarget(turn.target_id, { pulse: true });
  if (!point) {
    renderError({ error: "target_missing" });
    return;
  }
  const { centerX, centerY } = point;
  followerVisible = false;
  updatePointerTarget(turn.target_id);
  highlight.classList.remove("hovering");
  const entityLens = turn.entity_lens || {};
  const flowState = turn.pointer_flow_state || {};
  pointerEntityLabel.textContent = entityLens.entity_kind
    ? `${formatToken(entityLens.entity_kind)} · ${entityLens.region || "safe target"}`
    : pointerEntityLabel.textContent;
  updateContextChips(flowState);
  renderCommandSuggestions(turn.command_suggestions || flowState.command_suggestions);
  placeFloatingElement(talkCard, centerX, centerY, {
    fallbackWidth: 232,
    fallbackHeight: 76,
    gap: 14,
    anchor: "target",
  });
  talkCard.classList.add("visible");
  pointerSafetyLabel.textContent =
    turn.companion_state?.safety_caption || "Display only. You stay in control.";
  pointerRouteChip.textContent =
    turn.ai_assist_mode === "openai_dry_run" ? "AI draft · show only" : "Show only";
  pointerConfidenceChip.textContent = `Confidence ${Number(turn.confidence).toFixed(2)}`;
  if (tourActive) {
    pointerTourStrip.textContent = "Tour paused by answer";
  }

  bubble.textContent = turn.assistant_response;
  bubble.classList.add("visible");
  placeFloatingElement(bubble, centerX, centerY, {
    fallbackWidth: 318,
    fallbackHeight: 100,
    gap: 22,
    anchor: "target",
  });

  fields.target.textContent = turn.target_label;
  fields.intent.textContent = formatToken(turn.intent_label);
  fields.referent.textContent = turn.pointer_referent || "none";
  fields.confidence.textContent = Number(turn.confidence).toFixed(2);
  fields.aiMode.textContent =
    turn.ai_assist_mode === "openai_dry_run" && turn.ai_model
      ? `${turn.ai_model} store:false`
      : "local";
  setVoiceGesture(turn.voice_gesture_type || "single_click_context");
  voiceOutputChip.textContent = formatToken(turn.voice_output_mode || "text_chip");
  const effectText = turn.target_coordinates.allowed_effects
    .map(formatToken)
    .slice(1, 4)
    .join(", ");
  fields.effects.textContent =
    turn.ai_assist_mode === "openai_dry_run" ? `${effectText}, AI draft` : effectText;
  fields.blocked.textContent = "click, type, capture, memory, export";
  receiptSummary.textContent =
    turn.user_readable_receipt || "Cortex answered safely beside the pointer.";
  showReceiptToast(receiptSummary.textContent);
  dockState.textContent = turn.companion_state?.label || `Pointing at ${turn.target_label}`;
  dockSummary.textContent = turn.micro_steps?.[0] || turn.next_user_action;
  showMemoryProposal(turn.manual_memory_proposal);

  const item = document.createElement("li");
  const proposalText = turn.manual_memory_proposal ? " · memory proposal needs review" : "";
  const aiText =
    turn.ai_assist_mode === "openai_dry_run" && turn.ai_model
      ? ` · AI ${escapeHtml(turn.ai_model)} store:false`
      : "";
  const voiceText = ` · voice ${escapeHtml(formatToken(turn.voice_output_mode || "text_chip"))}`;
  item.innerHTML = `<strong>${escapeHtml(turn.target_label)}</strong><span>${escapeHtml(turn.user_readable_receipt || formatToken(turn.intent_label))} · ${escapeHtml(turn.pointer_referent || "none")} · confidence ${Number(turn.confidence).toFixed(2)} · raw refs ${turn.raw_ref_retained ? "retained" : "none"}${voiceText}${aiText}${proposalText}</span>`;
  turnList.prepend(item);
  voiceGestureType = "single_click_context";
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

frame.addEventListener("click", (event) => {
  if (!helperActive || event.target?.closest?.("button, input, textarea")) return;
  if (event.detail >= 3) {
    event.preventDefault();
    setVoiceGesture("triple_click_voice_dialogue");
    input.value = currentTargetId ? "Voice: explain this" : "Voice: what should I click next?";
    askTutor(input.value, { voiceGestureType: "triple_click_voice_dialogue" });
  }
});

frame.addEventListener("pointerdown", (event) => {
  if (!helperActive || event.target?.closest?.("button, input, textarea")) return;
  document.body.classList.add("pointer-holding");
  holdStartedAt = Date.now();
  window.clearTimeout(holdTimer);
  holdTimer = window.setTimeout(() => {
    const gesture = event.altKey ? "press_hold_action_only" : "press_hold_text_reply";
    setVoiceGesture(gesture);
    input.value =
      gesture === "press_hold_action_only"
        ? "Show me the next action, no voice back."
        : "Tell me what this does, but text only.";
    askTutor(input.value, { voiceGestureType: gesture });
  }, 680);
});

frame.addEventListener("pointerup", () => {
  document.body.classList.remove("pointer-holding");
  if (Date.now() - holdStartedAt < 650) {
    window.clearTimeout(holdTimer);
  }
});

frame.addEventListener("pointercancel", () => {
  document.body.classList.remove("pointer-holding");
  window.clearTimeout(holdTimer);
});

frame.addEventListener("pointerleave", () => {
  dockSummary.textContent = helperActive
    ? "Pointer helper is still awake inside the safe demo surface."
    : "Start helper to see Cortex follow inside this safe demo.";
});

document.querySelectorAll("[data-pointer-command]").forEach((button) => {
  button.addEventListener("click", (event) => {
    event.stopPropagation();
    const command = button.dataset.pointerCommand || "Explain this";
    if (!currentTargetId && /explain this|remember this/i.test(command)) {
      dockState.textContent = "Point first";
      dockSummary.textContent = "Move over a tool, then ask about this.";
      bubble.textContent = "Point at something first so I know what 'this' means.";
      bubble.classList.add("visible");
      return;
    }
    setVoiceGesture("single_click_context");
    input.value = command;
    askTutor(command);
  });
});

document.querySelectorAll("[data-pointer-voice]").forEach((button) => {
  button.addEventListener("click", (event) => {
    event.stopPropagation();
    const gesture = button.dataset.pointerVoice || "single_click_context";
    setVoiceGesture(gesture);
    input.value =
      gesture === "press_hold_action_only"
        ? "Show me the next action, no voice back."
        : gesture === "press_hold_text_reply"
          ? "Tell me what this does, but text only."
          : "Voice: explain this";
    askTutor(input.value, { voiceGestureType: gesture });
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

document.querySelectorAll("[data-pointer-tour]").forEach((button) => {
  button.addEventListener("click", (event) => {
    event.stopPropagation();
    const action = button.dataset.pointerTour || "start";
    if (action === "stop") {
      stopGuidedTour();
      return;
    }
    if (action === "next" && tourActive) {
      advanceGuidedTour();
      return;
    }
    startGuidedTour();
  });
});

document.querySelectorAll("[data-pointer-local]").forEach((button) => {
  button.addEventListener("click", (event) => {
    event.stopPropagation();
    if (button.dataset.pointerLocal === "pin-target") {
      pinCurrentTarget();
    }
    if (button.dataset.pointerLocal === "select-target") {
      selectCurrentTarget();
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
  pointerRouteChip.textContent = "Review only";
  pointerConfidenceChip.textContent = "Save blocked";
  showReceiptToast("Memory is still unsaved. Review before saving.");
});

dismissMemoryProposal.addEventListener("click", () => {
  memoryProposalCard.classList.remove("visible");
  receiptSummary.textContent = "Memory proposal dismissed. Nothing was saved.";
  dockState.textContent = "Proposal dismissed";
  dockSummary.textContent = "Cortex will keep pointing without saving that memory.";
  pointerRouteChip.textContent = "Show only";
  showReceiptToast("Memory proposal dismissed. Nothing was saved.");
});

receiptsToggle.addEventListener("click", () => {
  const collapsed = receiptStack.classList.toggle("collapsed");
  receiptsToggle.textContent = collapsed ? "Show safety receipts" : "Hide safety receipts";
});

setAiMode("local");
setVoiceGesture("single_click_context");
renderCommandSuggestions();
