const CORTEX_BROWSER_POLICY_REF = "policy_live_adapter_smoke_v1";
const DEFAULT_CORTEX_ENDPOINT = "http://127.0.0.1:8765/adapter/browser";

function endpointAllowed(endpoint) {
  return (
    endpoint.startsWith("http://127.0.0.1:") ||
    endpoint.startsWith("http://localhost:")
  );
}

function isHttpTab(tab) {
  return Boolean(tab && tab.id && tab.url && /^https?:\/\//.test(tab.url));
}

async function cortexSettings() {
  const settings = await chrome.storage.local.get({
    cortexEnabled: true,
    cortexEndpoint: DEFAULT_CORTEX_ENDPOINT,
  });
  return {
    enabled: settings.cortexEnabled === true,
    endpoint: String(settings.cortexEndpoint || DEFAULT_CORTEX_ENDPOINT),
  };
}

chrome.action.onClicked.addListener(async (tab) => {
  const settings = await cortexSettings();
  if (!settings.enabled || !endpointAllowed(settings.endpoint) || !isHttpTab(tab)) {
    return;
  }

  await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    files: ["content-script.js"],
  });
});

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (!message || message.type !== "CORTEX_BROWSER_DOM_EVENT") {
    return false;
  }

  (async () => {
    const settings = await cortexSettings();
    if (!settings.enabled || !endpointAllowed(settings.endpoint)) {
      sendResponse({ ok: false, reason: "adapter_disabled_or_endpoint_blocked" });
      return;
    }

    const payload = {
      ...message.payload,
      adapter_policy_ref: CORTEX_BROWSER_POLICY_REF,
      source_trust: "external_untrusted",
      third_party_content: true,
      dom_ref: null,
      raw_ref: null,
    };

    const response = await fetch(settings.endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    sendResponse({
      ok: response.ok && result.accepted === true,
      endpoint_status: response.status,
      result,
    });
  })().catch((error) => {
    sendResponse({ ok: false, reason: String(error && error.message ? error.message : error) });
  });

  return true;
});
