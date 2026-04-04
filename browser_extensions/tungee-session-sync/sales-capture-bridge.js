(function initTungeeSalesCaptureBridge() {
  window.addEventListener("message", (event) => {
    if (event.source !== window) {
      return;
    }
    const data = event.data || {};
    if (data.source !== "tungee-session-sync-sales-main" || data.type !== "sales-request-capture") {
      return;
    }
    chrome.runtime.sendMessage({
      type: "recordSalesCapture",
      payload: data.payload || {},
    });
  });
})();
