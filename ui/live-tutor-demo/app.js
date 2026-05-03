const frame = document.querySelector("#studio-frame");
const highlight = document.querySelector("#target-highlight");
const cursor = document.querySelector("#shadow-tutor-cursor");
const bubble = document.querySelector("#instruction-bubble");
const form = document.querySelector("#question-form");
const input = document.querySelector("#question-input");
const token = document.querySelector('meta[name="cortex-live-tutor-token"]')?.content || "";
const activePageChip = document.querySelector("#active-page-chip");
const turnList = document.querySelector("#turn-list");
const fields = {
  target: document.querySelector("#receipt-target"),
  intent: document.querySelector("#receipt-intent"),
  confidence: document.querySelector("#receipt-confidence"),
  effects: document.querySelector("#receipt-effects"),
  blocked: document.querySelector("#receipt-blocked"),
};

let activePage = "edit";

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
  fields.intent.textContent = "thinking";
  const response = await fetch("/tutor/turn", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Cortex-Live-Tutor-Token": token,
    },
    body: JSON.stringify({
      user_utterance: question,
      active_page: activePage,
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
  fields.confidence.textContent = "0.00";
  fields.effects.textContent = "none";
  fields.blocked.textContent = "request rejected before receipt";
  bubble.textContent = "That request was blocked before any tutor cue.";
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

  bubble.style.left = `${Math.min(centerX + 28, frameRect.width - 320)}px`;
  bubble.style.top = `${Math.max(centerY - 24, 18)}px`;
  bubble.textContent = turn.assistant_response;
  bubble.classList.add("visible");

  fields.target.textContent = turn.target_label;
  fields.intent.textContent = formatToken(turn.intent_label);
  fields.confidence.textContent = Number(turn.confidence).toFixed(2);
  fields.effects.textContent = turn.target_coordinates.allowed_effects
    .map(formatToken)
    .slice(1, 4)
    .join(", ");
  fields.blocked.textContent = "click, type, capture, memory, export";

  const item = document.createElement("li");
  item.innerHTML = `<strong>${escapeHtml(turn.target_label)}</strong><span>${escapeHtml(formatToken(turn.intent_label))} · confidence ${Number(turn.confidence).toFixed(2)} · raw refs ${turn.raw_ref_retained ? "retained" : "none"}</span>`;
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

askTutor(input.value);
