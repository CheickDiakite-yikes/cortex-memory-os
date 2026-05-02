const clicker = document.querySelector("#shadow-clicker");
const eventList = document.querySelector("#event-list");
const pointerReadout = document.querySelector("#pointer-readout");
const demoToken = document.querySelector('meta[name="cortex-demo-token"]')?.content || "";

const fields = {
  observation: document.querySelector("#observation-state"),
  firewall: document.querySelector("#firewall-state"),
  evidence: document.querySelector("#evidence-state"),
  memory: document.querySelector("#memory-state"),
  latestTarget: document.querySelector("#latest-target"),
  shadow: document.querySelector("#shadow-state"),
  retrieval: document.querySelector("#retrieval-state"),
  context: document.querySelector("#context-state"),
  rawRef: document.querySelector("#raw-ref-state"),
};

let lastPointer = { x: 36, y: 36 };
let sequence = 0;

function moveClicker(event) {
  lastPointer = { x: event.clientX, y: event.clientY };
  clicker.style.transform = `translate(${lastPointer.x}px, ${lastPointer.y}px)`;
  pointerReadout.textContent = `Pointer ${Math.round(lastPointer.x)}, ${Math.round(lastPointer.y)}`;
}

function pulseClicker() {
  clicker.classList.remove("pulse");
  window.requestAnimationFrame(() => {
    clicker.classList.add("pulse");
  });
}

function visibleSafeText(targetLabel, action) {
  const note = document.querySelector("#safe-note").value.trim().slice(0, 160);
  return `${targetLabel}. ${action}. ${note || "safe local demo note"}`;
}

async function submitObservation(action, targetLabel) {
  sequence += 1;
  pulseClicker();
  fields.observation.textContent = "sending";
  const payload = {
    action,
    target_label: targetLabel,
    pointer_x: Math.round(lastPointer.x),
    pointer_y: Math.round(lastPointer.y),
    page_url: window.location.href,
    visible_text: visibleSafeText(targetLabel, action),
    sequence,
  };

  const response = await fetch("/observe", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Cortex-Demo-Token": demoToken,
    },
    body: JSON.stringify(payload),
  });
  const receipt = await response.json();
  if (!response.ok) {
    renderRejectedReceipt(receipt, targetLabel);
    return;
  }
  renderReceipt(receipt);
}

function renderRejectedReceipt(receipt, targetLabel) {
  fields.observation.textContent = "rejected";
  fields.firewall.textContent = receipt.error || "invalid";
  fields.evidence.textContent = "not written";
  fields.memory.textContent = "blocked";
  fields.latestTarget.textContent = targetLabel;
  fields.shadow.textContent = "blocked";
  fields.retrieval.textContent = "not run";
  fields.context.textContent = "not run";
  fields.rawRef.textContent = "none";
  fields.memory.className = "warn";
  fields.rawRef.className = "good";
}

function renderReceipt(receipt) {
  fields.observation.textContent = receipt.observation_active ? "active" : "blocked";
  fields.firewall.textContent = receipt.firewall_decision;
  fields.evidence.textContent = receipt.evidence_write_mode;
  fields.memory.textContent = receipt.demo_candidate_memory_written ? "candidate written" : "not written";
  fields.latestTarget.textContent = receipt.target_label;
  fields.shadow.textContent = receipt.shadow_pointer_state;
  fields.retrieval.textContent = receipt.retrieval_hit ? "hit" : "no hit";
  fields.context.textContent = receipt.context_pack_hit ? "hit" : "no hit";
  fields.rawRef.textContent = receipt.raw_ref_retained ? "retained" : "none";
  fields.memory.className = receipt.demo_candidate_memory_written ? "good" : "warn";
  fields.rawRef.className = receipt.raw_ref_retained ? "warn" : "good";

  const item = document.createElement("li");
  item.innerHTML = `<strong>${escapeHtml(receipt.event_id)}</strong> ${escapeHtml(receipt.action)} on ${escapeHtml(receipt.target_label)}: shadow ${escapeHtml(receipt.shadow_pointer_state)}, memory ${receipt.demo_candidate_memory_written ? "candidate written" : "blocked"}.`;
  eventList.prepend(item);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

document.addEventListener("pointermove", moveClicker);

document.querySelectorAll("[data-observe]").forEach((button) => {
  button.addEventListener("click", (event) => {
    moveClicker(event);
    submitObservation("click", button.dataset.observe);
  });
});

document.querySelector("[data-observe-input]").addEventListener("change", (event) => {
  const rect = event.target.getBoundingClientRect();
  lastPointer = {
    x: Math.round(rect.left + rect.width - 12),
    y: Math.round(rect.top + rect.height - 12),
  };
  clicker.style.transform = `translate(${lastPointer.x}px, ${lastPointer.y}px)`;
  submitObservation("input", event.target.dataset.observeInput);
});

submitObservation("view", "Initial safe site view");
