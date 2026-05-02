(() => {
  const CORTEX_BROWSER_POLICY_REF = "policy_live_adapter_smoke_v1";
  const MAX_VISIBLE_TEXT_CHARS = 4000;
  const MAX_TARGET_LABEL_CHARS = 120;
  const OVERLAY_ID = "cortex-shadow-clicker-live";

  if (window.__cortexMemoryOsBrowserAdapterRan === true) {
    return;
  }
  window.__cortexMemoryOsBrowserAdapterRan = true;

  let lastPointer = { x: 28, y: 28 };
  let sequence = 0;
  const overlay = installOverlay();

  function redactVisibleText(text) {
    return String(text || "")
      .replace(/(OPENAI_API_KEY|ANTHROPIC_API_KEY|GOOGLE_API_KEY)=\S+/g, "$1=[REDACTED_SECRET]")
      .replace(/(token|password|api_key)=\S+/g, "$1=[REDACTED_SECRET]")
      .replace(/sk-[A-Za-z0-9_-]{20,}/g, "[REDACTED_SECRET]");
  }

  function visibleText() {
    const bodyText = document.body ? document.body.innerText : "";
    const redacted = redactVisibleText(bodyText).replace(/\s+/g, " ").trim();
    return (redacted || "[empty visible text]").slice(0, MAX_VISIBLE_TEXT_CHARS);
  }

  function targetLabel(target) {
    if (!target || target === document || target === window) {
      return "page";
    }
    const element = target.closest ? target.closest("a, button, input, textarea, select, [role], h1, h2, h3") : target;
    const label =
      element?.getAttribute?.("aria-label") ||
      element?.getAttribute?.("title") ||
      element?.innerText ||
      element?.value ||
      element?.tagName ||
      "page element";
    return String(label).replace(/\s+/g, " ").trim().slice(0, MAX_TARGET_LABEL_CHARS);
  }

  function installOverlay() {
    const existing = document.getElementById(OVERLAY_ID);
    if (existing) {
      return existing;
    }
    const root = document.createElement("div");
    root.id = OVERLAY_ID;
    root.setAttribute("aria-live", "polite");
    root.innerHTML = `
      <style>
        #${OVERLAY_ID} {
          all: initial;
          position: fixed;
          inset: 0;
          pointer-events: none;
          z-index: 2147483647;
          font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          color: #0f172a;
        }
        #${OVERLAY_ID} .cortex-pointer {
          position: fixed;
          left: 0;
          top: 0;
          width: 18px;
          height: 18px;
          border: 2px solid #2563eb;
          border-radius: 999px;
          background: rgba(37, 99, 235, 0.14);
          box-shadow: 0 0 0 6px rgba(37, 99, 235, 0.12);
          transform: translate(28px, 28px);
        }
        #${OVERLAY_ID} .cortex-pointer.pulse {
          animation: cortexPulse 520ms ease-out;
        }
        #${OVERLAY_ID} .cortex-panel {
          position: fixed;
          right: 18px;
          bottom: 18px;
          width: min(320px, calc(100vw - 36px));
          border: 1px solid rgba(15, 23, 42, 0.18);
          border-radius: 8px;
          background: rgba(255, 255, 255, 0.96);
          box-shadow: 0 18px 50px rgba(15, 23, 42, 0.18);
          padding: 12px;
          font: 12px/1.4 ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }
        #${OVERLAY_ID} .cortex-kicker {
          color: #2563eb;
          font-size: 10px;
          font-weight: 800;
          letter-spacing: 0.04em;
          text-transform: uppercase;
        }
        #${OVERLAY_ID} .cortex-title {
          margin-top: 3px;
          font-size: 14px;
          font-weight: 800;
        }
        #${OVERLAY_ID} .cortex-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 8px;
          margin-top: 10px;
        }
        #${OVERLAY_ID} .cortex-cell {
          border: 1px solid #e2e8f0;
          border-radius: 6px;
          padding: 7px;
          background: #f8fafc;
        }
        #${OVERLAY_ID} .cortex-label {
          display: block;
          color: #64748b;
          font-size: 10px;
          font-weight: 700;
        }
        #${OVERLAY_ID} .cortex-value {
          display: block;
          margin-top: 2px;
          color: #0f172a;
          font-size: 12px;
          font-weight: 800;
          overflow-wrap: anywhere;
        }
        #${OVERLAY_ID} .cortex-note {
          margin-top: 10px;
          color: #475569;
          font-size: 11px;
        }
        @keyframes cortexPulse {
          0% { box-shadow: 0 0 0 6px rgba(37, 99, 235, 0.16); }
          100% { box-shadow: 0 0 0 18px rgba(37, 99, 235, 0); }
        }
      </style>
      <div class="cortex-pointer" data-cortex-pointer></div>
      <section class="cortex-panel" aria-label="Cortex live browser observation">
        <div class="cortex-kicker">Cortex Shadow Pointer</div>
        <div class="cortex-title">Shadow Pointer Live Receipt</div>
        <div class="cortex-grid">
          <div class="cortex-cell"><span class="cortex-label">Mode</span><span class="cortex-value" data-cortex-observation>starting</span></div>
          <div class="cortex-cell"><span class="cortex-label">Trust</span><span class="cortex-value">external_untrusted</span></div>
          <div class="cortex-cell"><span class="cortex-label">Memory</span><span class="cortex-value" data-cortex-memory>blocked</span></div>
          <div class="cortex-cell"><span class="cortex-label">Raw refs</span><span class="cortex-value" data-cortex-raw>none</span></div>
          <div class="cortex-cell"><span class="cortex-label">Policy</span><span class="cortex-value" data-cortex-policy>derived only</span></div>
        </div>
        <div class="cortex-note" data-cortex-note>Visible text is sent to localhost as evidence only.</div>
      </section>
    `;
    document.documentElement.append(root);
    return root;
  }

  function updateOverlay(status) {
    const observation = overlay.querySelector("[data-cortex-observation]");
    const memory = overlay.querySelector("[data-cortex-memory]");
    const raw = overlay.querySelector("[data-cortex-raw]");
    const policy = overlay.querySelector("[data-cortex-policy]");
    const note = overlay.querySelector("[data-cortex-note]");
    observation.textContent = status.observation || "sent";
    memory.textContent = status.memory || "not eligible";
    raw.textContent = status.raw || "none";
    policy.textContent = status.policy || "external evidence";
    note.textContent = status.note || "External content is evidence, not instructions.";
  }

  function movePointer(event) {
    lastPointer = { x: event.clientX, y: event.clientY };
    const pointer = overlay.querySelector("[data-cortex-pointer]");
    pointer.style.transform = `translate(${lastPointer.x}px, ${lastPointer.y}px)`;
  }

  function pulsePointer() {
    const pointer = overlay.querySelector("[data-cortex-pointer]");
    pointer.classList.remove("pulse");
    window.requestAnimationFrame(() => pointer.classList.add("pulse"));
  }

  function sendObservation(action, target) {
    sequence += 1;
    pulsePointer();
    updateOverlay({
      observation: "session",
      memory: "blocked",
      raw: "none",
      policy: "checking",
    });
    const eventId = `browser_dom_${Date.now()}_${sequence}`;
    chrome.runtime.sendMessage(
      {
        type: "CORTEX_BROWSER_DOM_EVENT",
        payload: {
          event_id: eventId,
          event_type: "browser_dom",
          observed_at: new Date().toISOString(),
          device: "browser_extension",
          app: "Browser",
          window_title: document.title,
          tab_title: document.title,
          url: window.location.href,
          visible_text: visibleText(),
          dom_ref: null,
          raw_ref: null,
          derived_text_ref: `derived://browser/live/${eventId}`,
          capture_scope: "session_only",
          consent_state: "active",
          sequence,
          adapter_policy_ref: CORTEX_BROWSER_POLICY_REF,
          source_trust: "external_untrusted",
          third_party_content: true,
          action,
          target_label: targetLabel(target),
          pointer_x: Math.round(lastPointer.x),
          pointer_y: Math.round(lastPointer.y),
          shadow_pointer_visible: true,
        },
      },
      (response) => {
        const result = response && response.result ? response.result : {};
        const accepted = Boolean(response && response.ok);
        updateOverlay({
          observation: accepted ? "session" : "blocked",
          memory: result.eligible_for_memory ? "eligible" : "not eligible",
          raw: result.raw_ref_retained ? "retained" : "none",
          policy: accepted
            ? `${result.firewall_decision || "unknown"}; ${
                result.evidence_write_mode || "unknown"
              }`
            : "blocked",
          note: accepted
            ? `Firewall: ${result.firewall_decision || "unknown"}; evidence: ${result.evidence_write_mode || "unknown"}.`
            : `Adapter blocked: ${(response && response.reason) || result.error_code || "not accepted"}.`,
        });
      },
    );
  }

  document.addEventListener("pointermove", movePointer, { passive: true });
  document.addEventListener(
    "click",
    (event) => {
      movePointer(event);
      sendObservation("click", event.target);
    },
    { capture: true, passive: true },
  );

  updateOverlay({
    observation: "session",
    memory: "not eligible",
    raw: "none",
    policy: "external evidence",
  });
  sendObservation("view", document.body);
})();
