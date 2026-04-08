(function initTungeeSyncBridge() {
  document.documentElement.dataset.tungeeSessionSyncInstalled = "1";

  function postToPage(payload) {
    window.postMessage(
      {
        source: "tungee-session-sync-extension",
        ...payload,
      },
      window.location.origin,
    );
  }

  function sendRuntimeMessage(message) {
    return new Promise((resolve, reject) => {
      chrome.runtime.sendMessage(message, (response) => {
        const error = chrome.runtime.lastError;
        if (error) {
          reject(new Error(error.message));
          return;
        }
        resolve(response);
      });
    });
  }

  window.addEventListener("message", async (event) => {
    if (event.source !== window) {
      return;
    }
    const data = event.data || {};
    if (data.source !== "bussiness-console") {
      return;
    }
    if (data.type === "TUNGEE_PLUGIN_SEARCH_REQUEST") {
      try {
        const response = await sendRuntimeMessage({
          type: "searchCompaniesInBrowser",
          companyNames: data.companyNames || [],
        });
        postToPage({
          type: "search-result",
          requestId: data.requestId,
          payload: response,
        });
      } catch (error) {
        postToPage({
          type: "search-result",
          requestId: data.requestId,
          payload: { ok: false, message: String(error.message || error) },
        });
      }
      return;
    }
    if (data.type !== "TUNGEE_PLUGIN_SYNC_REQUEST") {
      return;
    }
    try {
      const response = await sendRuntimeMessage({
        type: "syncCurrentTungeeContext",
        localApiBase: data.localApiBase || window.location.origin,
      });
      postToPage({
        type: "sync-result",
        requestId: data.requestId,
        payload: response,
      });
    } catch (error) {
      postToPage({
        type: "sync-result",
        requestId: data.requestId,
        payload: { ok: false, message: String(error.message || error) },
      });
    }
  });

  postToPage({ type: "ready" });
})();
