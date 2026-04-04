(function initTungeeSalesCapture() {
  const RELEVANT_PATHS = [
    "/api/enterprise/info/basic",
    "/api/enterprise/info/detail",
    "/api/enterprise/lead/info",
    "/api/lead/contact/top-n-contacts",
    "/api/enterprises/search",
  ];

  function isRelevant(url) {
    return RELEVANT_PATHS.some((path) => String(url || "").includes(path));
  }

  function toHeaderMap(input) {
    const normalized = {};
    if (!input) {
      return normalized;
    }
    if (input instanceof Headers) {
      input.forEach((value, key) => {
        normalized[String(key).toLowerCase()] = String(value || "");
      });
      return normalized;
    }
    if (Array.isArray(input)) {
      for (const item of input) {
        if (!Array.isArray(item) || item.length < 2) {
          continue;
        }
        normalized[String(item[0]).toLowerCase()] = String(item[1] || "");
      }
      return normalized;
    }
    for (const [key, value] of Object.entries(input)) {
      normalized[String(key).toLowerCase()] = String(value || "");
    }
    return normalized;
  }

  function emitCapture(payload) {
    window.postMessage(
      {
        source: "tungee-session-sync-sales-main",
        type: "sales-request-capture",
        payload,
      },
      window.location.origin,
    );
  }

  const originalFetch = window.fetch;
  window.fetch = async function patchedFetch(input, init) {
    const request = input instanceof Request ? input : null;
    const url = request ? request.url : String(input || "");
    const method = String((init && init.method) || (request && request.method) || "GET").toUpperCase();
    const headers = {
      ...toHeaderMap(request ? request.headers : null),
      ...toHeaderMap(init && init.headers),
    };
    if (isRelevant(url)) {
      emitCapture({
        transport: "fetch",
        url,
        method,
        headers,
        capturedAt: Date.now(),
      });
    }
    return originalFetch.apply(this, arguments);
  };

  const originalOpen = XMLHttpRequest.prototype.open;
  const originalSend = XMLHttpRequest.prototype.send;
  const originalSetRequestHeader = XMLHttpRequest.prototype.setRequestHeader;

  XMLHttpRequest.prototype.open = function patchedOpen(method, url) {
    this.__tungeeCapture = {
      method: String(method || "GET").toUpperCase(),
      url: String(url || ""),
      headers: {},
    };
    return originalOpen.apply(this, arguments);
  };

  XMLHttpRequest.prototype.setRequestHeader = function patchedSetRequestHeader(name, value) {
    if (this.__tungeeCapture) {
      this.__tungeeCapture.headers[String(name || "").toLowerCase()] = String(value || "");
    }
    return originalSetRequestHeader.apply(this, arguments);
  };

  XMLHttpRequest.prototype.send = function patchedSend() {
    if (this.__tungeeCapture && isRelevant(this.__tungeeCapture.url)) {
      emitCapture({
        transport: "xhr",
        url: this.__tungeeCapture.url,
        method: this.__tungeeCapture.method,
        headers: this.__tungeeCapture.headers,
        capturedAt: Date.now(),
      });
    }
    return originalSend.apply(this, arguments);
  };
})();
