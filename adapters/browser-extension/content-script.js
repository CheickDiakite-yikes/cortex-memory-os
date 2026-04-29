(() => {
  const CORTEX_BROWSER_POLICY_REF = "policy_live_adapter_smoke_v1";
  const MAX_VISIBLE_TEXT_CHARS = 4000;

  if (window.__cortexMemoryOsBrowserAdapterRan === true) {
    return;
  }
  window.__cortexMemoryOsBrowserAdapterRan = true;

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

  const eventId = `browser_dom_${Date.now()}`;
  chrome.runtime.sendMessage({
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
      derived_text_ref: `derived://browser/live/${eventId}`,
      capture_scope: "session_only",
      consent_state: "active",
      sequence: Date.now(),
      adapter_policy_ref: CORTEX_BROWSER_POLICY_REF,
      source_trust: "external_untrusted",
      third_party_content: true,
    },
  });
})();
