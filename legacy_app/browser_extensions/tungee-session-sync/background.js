const RELEVANT_PATHS = [
  "/api/enterprises/search",
  "/api/enterprise/info/detail",
  "/api/enterprise/info/basic",
  "/api/lead/contact/top-n-contacts",
];
const DEFAULT_LOCAL_API_BASE = "http://127.0.0.1:8000";

const capturesByTab = new Map();
const MAX_CAPTURES_PER_TAB = 30;

function normalizeHeaders(requestHeaders = []) {
  const normalized = {};
  for (const header of requestHeaders) {
    if (!header || !header.name) {
      continue;
    }
    normalized[String(header.name).toLowerCase()] = String(header.value || "");
  }
  return normalized;
}

function isRelevantRequest(url) {
  return RELEVANT_PATHS.some((path) => url.includes(path));
}

function promisifyChrome(fn, ...args) {
  return new Promise((resolve, reject) => {
    fn(...args, (result) => {
      const error = chrome.runtime.lastError;
      if (error) {
        reject(new Error(error.message));
        return;
      }
      resolve(result);
    });
  });
}

function parseEnterpriseId(url) {
  const match = String(url || "").match(/\/enterprise-details\/([^/]+)\//);
  return match ? match[1] : null;
}

function normalizeCompanyName(name) {
  return String(name || "")
    .trim()
    .replace(/\s+/g, "")
    .replace(/有限责任公司|股份有限公司|集团有限公司|有限公司|公司/g, "")
    .replace(/[()（）·-]/g, "");
}

function pickBestEnterprise(keyword, enterprises) {
  const normalizedKeyword = normalizeCompanyName(keyword);
  if (!normalizedKeyword || !Array.isArray(enterprises) || enterprises.length === 0) {
    return null;
  }

  function score(candidate) {
    const name = String(candidate?.name || "").trim();
    const normalizedCandidate = normalizeCompanyName(name);
    const contactNumber = Number(candidate?.contactNumber || 0);
    if (normalizedCandidate === normalizedKeyword) {
      return [0, 0, -contactNumber];
    }
    if (normalizedCandidate.includes(normalizedKeyword)) {
      return [1, Math.abs(normalizedCandidate.length - normalizedKeyword.length), -contactNumber];
    }
    return [9, normalizedCandidate.length || 999, -contactNumber];
  }

  const ranked = [...enterprises].sort((left, right) => {
    const a = score(left);
    const b = score(right);
    for (let index = 0; index < Math.max(a.length, b.length); index += 1) {
      const diff = (a[index] || 0) - (b[index] || 0);
      if (diff !== 0) {
        return diff;
      }
    }
    return 0;
  });
  return ranked[0] || null;
}

function sortCookies(cookies) {
  return [...cookies].sort((a, b) => {
    const pathDiff = String(b.path || "").length - String(a.path || "").length;
    if (pathDiff !== 0) {
      return pathDiff;
    }
    const domainDiff = String(a.domain || "").localeCompare(String(b.domain || ""));
    if (domainDiff !== 0) {
      return domainDiff;
    }
    return String(a.name || "").localeCompare(String(b.name || ""));
  });
}

function buildCookieHeader(cookies) {
  return sortCookies(cookies)
    .map((cookie) => `${cookie.name}=${cookie.value}`)
    .join("; ");
}

function parseCookieHeader(cookieHeader) {
  const text = String(cookieHeader || "").trim();
  if (!text) {
    return {};
  }
  const cookies = {};
  for (const part of text.split(";")) {
    const item = String(part || "").trim();
    if (!item || !item.includes("=")) {
      continue;
    }
    const [name, ...rest] = item.split("=");
    const key = String(name || "").trim();
    const value = rest.join("=").trim();
    if (key) {
      cookies[key] = value;
    }
  }
  return cookies;
}

function mergeCookieSources(cookieHeaders) {
  const merged = {};
  for (const header of cookieHeaders) {
    const parsed = parseCookieHeader(header);
    Object.assign(merged, parsed);
  }
  return Object.entries(merged)
    .map(([name, value]) => `${name}=${value}`)
    .join("; ");
}

function dedupeCookies(cookies) {
  const seen = new Set();
  const deduped = [];
  for (const cookie of cookies) {
    const signature = [
      cookie.storeId || "",
      cookie.domain || "",
      cookie.path || "",
      cookie.name || "",
    ].join("|");
    if (seen.has(signature)) {
      continue;
    }
    seen.add(signature);
    deduped.push(cookie);
  }
  return deduped;
}

async function getCaptureForTab(tabId) {
  const captures = capturesByTab.get(tabId) || [];
  return captures[captures.length - 1] || null;
}

async function clearCaptureForTab(tabId) {
  capturesByTab.delete(tabId);
}

function findBestCaptureForTab(tabId) {
  const captures = capturesByTab.get(tabId) || [];
  const matched = [...captures]
    .reverse()
    .find(
      (capture) =>
        capture?.headers?.["x-tonxis-pid"] &&
        capture?.headers?.["x-tonxis-sid"] &&
        capture?.headers?.["x-tonxis-signature"],
    );
  return matched || captures[captures.length - 1] || null;
}

function findBestSearchCaptureForTab(tabId) {
  const captures = capturesByTab.get(tabId) || [];
  return (
    [...captures]
      .reverse()
      .find(
        (capture) =>
          capture?.url?.includes("/api/enterprises/search") &&
          capture?.headers?.["x-tonxis-pid"] &&
          capture?.headers?.["x-tonxis-sid"] &&
          capture?.headers?.["x-tonxis-signature"],
      ) || null
  );
}

function findBestCookieCaptureForTab(tabId) {
  const captures = capturesByTab.get(tabId) || [];
  return (
    [...captures]
      .reverse()
      .find((capture) => {
        const cookieHeader = String(capture?.headers?.cookie || "").trim();
        return Boolean(cookieHeader);
      }) || null
  );
}

function findBestSearchCookieCaptureForTab(tabId) {
  const captures = capturesByTab.get(tabId) || [];
  return (
    [...captures]
      .reverse()
      .find((capture) => {
        const cookieHeader = String(capture?.headers?.cookie || "").trim();
        return Boolean(cookieHeader) && String(capture?.url || "").includes("/api/enterprises/search");
      }) || null
  );
}

async function getCookiesForUrl(url) {
  return promisifyChrome(chrome.cookies.getAll, { url });
}

async function getCookiesForDomains(domains) {
  const groups = await Promise.all(
    domains.map((domain) => promisifyChrome(chrome.cookies.getAll, { domain })),
  );
  return dedupeCookies(groups.flat());
}

async function executeCaptureRequest(tabId, enterpriseId) {
  const results = await promisifyChrome(chrome.scripting.executeScript, {
    target: { tabId },
    world: "MAIN",
    func: async (targetEnterpriseId) => {
      const requestUrls = [
        `/api/enterprise/info/basic?enterprise_id=${encodeURIComponent(targetEnterpriseId)}`,
        `/api/enterprise/info/detail?enterprise_id=${encodeURIComponent(targetEnterpriseId)}`,
        `/api/enterprise/lead/info?enterprise_id=${encodeURIComponent(targetEnterpriseId)}`,
        `/api/lead/contact/top-n-contacts?enterprise_id=${encodeURIComponent(targetEnterpriseId)}&take_count=5`,
      ];
      const results = [];
      try {
        let keyword = "";
        for (const requestUrl of requestUrls) {
          try {
            const response = await window.fetch(requestUrl, { credentials: "include" });
            const text = await response.text();
            if (!keyword && requestUrl.includes("/api/enterprise/info/basic")) {
              try {
                const payload = JSON.parse(text);
                keyword = String(payload.name || "").trim();
              } catch (_error) {
                keyword = "";
              }
            }
            results.push({
              url: requestUrl,
              ok: response.ok,
              status: response.status,
              body: text.slice(0, 120),
            });
          } catch (error) {
            results.push({
              url: requestUrl,
              ok: false,
              error: String(error),
            });
          }
        }
        if (keyword) {
          const searchParams = new URLSearchParams({
            start: "0",
            end: "10",
            keywords: keyword,
            filter: '{"show_associate":0}',
            filter_lead: "0",
            industry: "financial",
            is_canary: "1",
          });
          const searchUrl = `/api/enterprises/search?${searchParams.toString()}`;
          try {
            const response = await window.fetch(searchUrl, { credentials: "include" });
            const text = await response.text();
            results.push({
              url: searchUrl,
              ok: response.ok,
              status: response.status,
              body: text.slice(0, 120),
            });
          } catch (error) {
            results.push({
              url: searchUrl,
              ok: false,
              error: String(error),
            });
          }
        }
        return { ok: true, requests: results, pageCookie: document.cookie || "" };
      } catch (error) {
        return { ok: false, error: String(error) };
      }
    },
    args: [enterpriseId],
  });
  return results?.[0]?.result || null;
}

async function readPageCookie(tabId) {
  const results = await promisifyChrome(chrome.scripting.executeScript, {
    target: { tabId },
    world: "MAIN",
    func: () => document.cookie || "",
  });
  return results?.[0]?.result || "";
}

async function waitForCapturedHeaders(tabId, timeoutMs = 12000) {
  const startedAt = Date.now();
  while (Date.now() - startedAt < timeoutMs) {
    const capture = findBestCaptureForTab(tabId);
    if (capture?.headers?.["x-tonxis-sid"] && capture?.headers?.["x-tonxis-signature"]) {
      return capture;
    }
    await new Promise((resolve) => setTimeout(resolve, 400));
  }
  return null;
}

async function querySalesTabs() {
  const tabs = await promisifyChrome(chrome.tabs.query, { url: ["https://sales.tungee.com/*"] });
  return tabs.filter((tab) => parseEnterpriseId(tab.url));
}

function pickBestSalesTab(tabs, preferredTabId) {
  if (preferredTabId) {
    const preferred = tabs.find((tab) => tab.id === preferredTabId && parseEnterpriseId(tab.url));
    if (preferred) {
      return preferred;
    }
  }
  return [...tabs].sort((a, b) => Number(b.lastAccessed || 0) - Number(a.lastAccessed || 0))[0] || null;
}

async function syncTungeeContext({ localApiBase, preferredTabId = null }) {
  const apiBase = String(localApiBase || DEFAULT_LOCAL_API_BASE).trim() || DEFAULT_LOCAL_API_BASE;
  const salesTabs = await querySalesTabs();
  const salesTab = pickBestSalesTab(salesTabs, preferredTabId);
  if (!salesTab?.id || !salesTab.url) {
    throw new Error("没有找到已打开的探迹企业详情页，请先在浏览器里打开一个 sales.tungee.com 企业详情页。");
  }

  const enterpriseId = parseEnterpriseId(salesTab.url);
  if (!enterpriseId) {
    throw new Error("当前探迹页面无法识别企业 ID。");
  }

  let capture = findBestCaptureForTab(salesTab.id);
  let pageCookieHeader = "";
  if (!capture?.headers?.["x-tonxis-sid"] || !capture?.headers?.["x-tonxis-signature"]) {
    await clearCaptureForTab(salesTab.id);
    const executeResult = await executeCaptureRequest(salesTab.id, enterpriseId);
    if (executeResult?.error) {
      throw new Error(`页面注入请求失败：${executeResult.error}`);
    }
    pageCookieHeader = executeResult?.pageCookie || "";
    capture = await waitForCapturedHeaders(salesTab.id);
  }
  if (!capture) {
    throw new Error("未捕获到带 x-tonxis-sid / x-tonxis-signature 的请求。请先确保探迹企业详情页已完全加载，或者在详情页里手动点一次联系人/详情相关内容后再重试。");
  }
  if (!pageCookieHeader) {
    pageCookieHeader = await readPageCookie(salesTab.id);
  }
  const searchCapture = findBestSearchCaptureForTab(salesTab.id);
  const cookieCapture = findBestCookieCaptureForTab(salesTab.id);
  const searchCookieCapture = findBestSearchCookieCaptureForTab(salesTab.id);

  const [salesCookies, userCookies] = await Promise.all([
    getCookiesForDomains(["sales.tungee.com", ".sales.tungee.com", "tungee.com", ".tungee.com"]),
    getCookiesForDomains(["user.tungee.com", ".user.tungee.com", "tungee.com", ".tungee.com"]),
  ]);
  const salesCookieHeader = mergeCookieSources([
    cookieCapture?.headers?.cookie || "",
    capture?.headers?.cookie || "",
    searchCapture?.headers?.cookie || "",
    pageCookieHeader,
    buildCookieHeader(salesCookies),
  ]);
  const userCookieHeader = buildCookieHeader(userCookies);
  if (!salesCookieHeader) {
    throw new Error("没有读取到 sales.tungee.com 可用 cookie。");
  }

  const response = await fetch(`${apiBase.replace(/\/$/, "")}/api/tungee/session/import`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      user_agent: capture.headers["user-agent"] || "",
      sales_cookie_header: salesCookieHeader,
      sales_search_cookie_header: searchCookieCapture?.headers?.cookie || "",
      user_cookie_header: userCookieHeader || null,
      sales_request_headers: {
        "x-tonxis-pid": capture.headers["x-tonxis-pid"] || "",
        "x-tonxis-sid": capture.headers["x-tonxis-sid"] || "",
        "x-tonxis-signature": capture.headers["x-tonxis-signature"] || "",
      },
      sales_search_request_headers: {
        "x-tonxis-pid": searchCapture?.headers?.["x-tonxis-pid"] || capture.headers["x-tonxis-pid"] || "",
        "x-tonxis-sid": searchCapture?.headers?.["x-tonxis-sid"] || capture.headers["x-tonxis-sid"] || "",
        "x-tonxis-signature": searchCapture?.headers?.["x-tonxis-signature"] || capture.headers["x-tonxis-signature"] || "",
      },
      source_url: salesTab.url,
    }),
  });

  let payload;
  try {
    payload = await response.json();
  } catch (error) {
    throw new Error(`本地服务返回了非 JSON 响应：${String(error)}`);
  }

  if (!response.ok || payload?.ok === false) {
    throw new Error(payload?.message || `同步失败：HTTP ${response.status}`);
  }

  return {
    ok: true,
    session: payload.session || null,
    profile: payload.profile || null,
    sales_headers_ready: Boolean(payload.sales_headers_ready),
    sales_tab_url: salesTab.url,
    imported_into: apiBase,
  };
}

async function searchCompaniesInBrowser({ companyNames, preferredTabId = null }) {
  const salesTabs = await querySalesTabs();
  const salesTab = pickBestSalesTab(salesTabs, preferredTabId);
  if (!salesTab?.id || !salesTab.url) {
    throw new Error("没有找到已打开的探迹企业详情页，请先在浏览器里打开一个 sales.tungee.com 企业详情页。");
  }

  const results = await promisifyChrome(chrome.scripting.executeScript, {
    target: { tabId: salesTab.id },
    world: "MAIN",
    func: async (keywords) => {
      const output = [];
      for (const keyword of keywords) {
        const searchParams = new URLSearchParams({
          start: "0",
          end: "10",
          keywords: keyword,
          filter: '{"show_associate":0}',
          filter_lead: "0",
          industry: "financial",
          is_canary: "1",
        });
        const response = await window.fetch(`/api/enterprises/search?${searchParams.toString()}`, {
          credentials: "include",
        });
        const text = await response.text();
        let payload = {};
        try {
          payload = JSON.parse(text);
        } catch (_error) {
          payload = { raw: text };
        }
        output.push({
          keyword,
          ok: response.ok,
          status: response.status,
          payload,
        });
      }
      return output;
    },
    args: [companyNames],
  });

  const payloads = results?.[0]?.result || [];
  const resolved_matches = [];
  const prefetched_results = [];
  for (const item of payloads) {
    const matched = pickBestEnterprise(item.keyword, item.payload?.enterprises || []);
    if (!matched || !matched._id) {
      continue;
    }
    resolved_matches.push({
      input_company_name: item.keyword,
      matched_company_name: String(matched.name || item.keyword),
      external_company_id: String(matched._id),
    });
    const matchedPayload = JSON.parse(JSON.stringify(matched));
    const searchPayload = JSON.parse(JSON.stringify(item.payload || {}));
    const prefetchResult = await promisifyChrome(chrome.scripting.executeScript, {
      target: { tabId: salesTab.id },
      world: "MAIN",
      func: async (enterpriseId, keyword, recruitingKeyword, matchedData, searchData) => {
        async function fetchJson(url, init) {
          const response = await window.fetch(url, { credentials: "include", ...(init || {}) });
          const text = await response.text();
          let payload;
          try {
            payload = JSON.parse(text);
          } catch (_error) {
            payload = { raw: text, stat: response.ok ? 1 : 0 };
          }
          return {
            ok: response.ok,
            status: response.status,
            payload,
          };
        }
        function isMaskedContactValue(value) {
          const text = String(value || "").trim();
          if (!text) {
            return true;
          }
          return text.includes("*") || text.includes("****");
        }
        function needsUnlock(topContacts, enterprise) {
          const totalContactCount = Number((topContacts?.contact_basic_info || {}).total_contact_count || 0);
          const searchContactCount = Number(enterprise?.contactNumber || 0);
          const topItems = Array.isArray(topContacts?.top_contacts) ? topContacts.top_contacts : [];
          const candidates = topItems;

          if (candidates.some((item) => item?.has_unlocked === true && !isMaskedContactValue(item?.contact_label))) {
            return false;
          }
          if (candidates.some((item) => !isMaskedContactValue(item?.contact_label))) {
            return false;
          }
          if (candidates.some((item) => item?.has_unlocked === false)) {
            return true;
          }
          if (totalContactCount > 0) {
            return true;
          }
          if (searchContactCount > 0 && candidates.length === 0) {
            return true;
          }
          return false;
        }
        const basicResponse = await fetchJson(`/api/enterprise/info/basic?enterprise_id=${encodeURIComponent(enterpriseId)}`);
        const detailResponse = await fetchJson(`/api/enterprise/info/detail?enterprise_id=${encodeURIComponent(enterpriseId)}`);
        let leadInfoResponse = await fetchJson(`/api/enterprise/lead/info?enterprise_id=${encodeURIComponent(enterpriseId)}`);
        let topContactsResponse = await fetchJson(`/api/lead/contact/top-n-contacts?enterprise_id=${encodeURIComponent(enterpriseId)}&take_count=5`);
        const basic = basicResponse.payload;
        const detail = detailResponse.payload;
        let leadInfo = leadInfoResponse.payload;
        let topContacts = topContactsResponse.payload;
        let unlockPayload = null;
        console.info("[tungee-session-sync] contact prefetch result", {
          enterpriseId,
          keyword,
          topContactsStatus: topContactsResponse.status,
          topContactsCount: Array.isArray(topContacts?.top_contacts) ? topContacts.top_contacts.length : 0,
        });
        if (needsUnlock(topContacts, matchedData)) {
          const unlockResponse = await fetchJson("/api/lead/unlock", {
            method: "PUT",
            body: (() => {
              const form = new FormData();
              form.append("source", "4");
              form.append("enterprise_id", enterpriseId);
              form.append("entity_type", "enterprise");
              return form;
            })(),
          });
          unlockPayload = unlockResponse.payload;
          leadInfoResponse = await fetchJson(`/api/enterprise/lead/info?enterprise_id=${encodeURIComponent(enterpriseId)}`);
          topContactsResponse = await fetchJson(`/api/lead/contact/top-n-contacts?enterprise_id=${encodeURIComponent(enterpriseId)}&take_count=5`);
          leadInfo = leadInfoResponse.payload;
          topContacts = topContactsResponse.payload;
          console.info("[tungee-session-sync] contact prefetch retry after unlock", {
            enterpriseId,
            keyword,
            unlockStatus: unlockResponse.status,
            topContactsStatus: topContactsResponse.status,
            topContactsCount: Array.isArray(topContacts?.top_contacts) ? topContacts.top_contacts.length : 0,
          });
        }
        const recruitingPages = [];
        let recruitingsPayload = [];
        const firstRecruitingPageResponse = await fetchJson(
          `/api/enterprise/info/recruiting/list?enterprise_id=${encodeURIComponent(enterpriseId)}&start=0&end=10&keyword=${encodeURIComponent(recruitingKeyword || "")}`,
        );
        const firstRecruitingPage = firstRecruitingPageResponse.payload;
        recruitingPages.push([0, firstRecruitingPage]);
        const total = Number(firstRecruitingPage.total || 0);
        recruitingsPayload = [...(firstRecruitingPage.data || firstRecruitingPage.recruitings || [])];
        for (let start = 10; start < Math.min(total, 100); start += 10) {
          const pageResponse = await fetchJson(
            `/api/enterprise/info/recruiting/list?enterprise_id=${encodeURIComponent(enterpriseId)}&start=${start}&end=${start + 10}&keyword=${encodeURIComponent(recruitingKeyword || "")}`,
          );
          const pagePayload = pageResponse.payload;
          recruitingPages.push([start, pagePayload]);
          recruitingsPayload = recruitingsPayload.concat(pagePayload.data || pagePayload.recruitings || []);
        }
        return {
          input_company_name: keyword,
          matched: matchedData,
          search_payload: searchData,
          basic,
          detail,
          lead_info: leadInfo,
          top_contacts: topContacts,
          unlock_payload: unlockPayload,
          recruitings_payload: recruitingsPayload,
          recruiting_pages: recruitingPages,
        };
      },
      args: [String(matched._id), item.keyword, "", matchedPayload, searchPayload],
    });
    if (prefetchResult?.[0]?.result) {
      console.info("[tungee-session-sync] prefetch summary", {
        keyword: item.keyword,
        enterpriseId: String(matched._id),
        topContactsCount: Array.isArray(prefetchResult[0].result?.top_contacts?.top_contacts)
          ? prefetchResult[0].result.top_contacts.top_contacts.length
          : 0,
      });
      prefetched_results.push(prefetchResult[0].result);
    }
  }

  return {
    ok: true,
    sales_tab_url: salesTab.url,
    resolved_matches,
    prefetched_results,
    raw_results: payloads,
  };
}

chrome.webRequest.onBeforeSendHeaders.addListener(
  (details) => {
    if (details.tabId < 0 || !isRelevantRequest(details.url)) {
      return;
    }
    const captures = capturesByTab.get(details.tabId) || [];
    captures.push({
      url: details.url,
      capturedAt: Date.now(),
      headers: normalizeHeaders(details.requestHeaders),
    });
    if (captures.length > MAX_CAPTURES_PER_TAB) {
      captures.splice(0, captures.length - MAX_CAPTURES_PER_TAB);
    }
    capturesByTab.set(details.tabId, captures);
  },
  { urls: ["https://sales.tungee.com/api/*"] },
  ["requestHeaders", "extraHeaders"],
);

chrome.tabs.onRemoved.addListener((tabId) => {
  capturesByTab.delete(tabId);
});

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message?.type === "getCaptureForTab") {
    sendResponse({ capture: findBestCaptureForTab(message.tabId) || null });
    return;
  }
  if (message?.type === "clearCaptureForTab") {
    capturesByTab.delete(message.tabId);
    sendResponse({ ok: true });
    return;
  }
  if (message?.type === "syncCurrentTungeeContext") {
    syncTungeeContext({
      localApiBase: message.localApiBase,
      preferredTabId: message.preferredTabId || null,
    })
      .then((payload) => sendResponse(payload))
      .catch((error) => sendResponse({ ok: false, message: String(error.message || error) }));
    return true;
  }
  if (message?.type === "searchCompaniesInBrowser") {
    searchCompaniesInBrowser({
      companyNames: message.companyNames || [],
      preferredTabId: message.preferredTabId || null,
    })
      .then((payload) => sendResponse(payload))
      .catch((error) => sendResponse({ ok: false, message: String(error.message || error) }));
    return true;
  }
  if (message?.type === "recordSalesCapture") {
    const tabId = _sender?.tab?.id;
    if (typeof tabId !== "number" || tabId < 0) {
      sendResponse({ ok: false, message: "invalid tab id" });
      return;
    }
    const capture = message.payload || {};
    const captures = capturesByTab.get(tabId) || [];
    captures.push({
      url: capture.url || "",
      capturedAt: capture.capturedAt || Date.now(),
      headers: normalizeHeaders(
        Object.entries(capture.headers || {}).map(([name, value]) => ({ name, value })),
      ),
    });
    if (captures.length > MAX_CAPTURES_PER_TAB) {
      captures.splice(0, captures.length - MAX_CAPTURES_PER_TAB);
    }
    capturesByTab.set(tabId, captures);
    sendResponse({ ok: true });
    return;
  }
  sendResponse({ ok: false, message: "unknown message" });
});
