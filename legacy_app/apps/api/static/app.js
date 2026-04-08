async function apiFetch(url, options = {}) {
  const response = await fetch(url, {
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.message || `请求失败: ${response.status}`);
  }
  return payload;
}

function renderEmpty(container, text) {
  container?.removeAttribute("aria-busy");
  container.innerHTML = `<p class="empty-state">${text}</p>`;
}

const recentJobState = {
  jobs: [],
  search: "",
  status: "all",
  page: 1,
  pageSize: 5,
  total: 0,
  searchTimer: null,
};

const historyJobState = {
  jobs: [],
  page: 1,
  pageSize: 5,
  total: 0,
};

const adminJobState = {
  jobs: [],
  page: 1,
  pageSize: 6,
  total: 0,
};

const TERMINAL_QUERY_JOB_STATUSES = new Set(["completed", "partial_success", "failed", "session_expired"]);
const TERMINAL_QUERY_ITEM_STATUSES = new Set(["completed", "failed", "not_found", "session_expired"]);

const consoleJobAutoRefreshState = {
  token: 0,
  hideTimer: null,
};

const researchListAutoRefreshState = {
  timer: null,
  running: false,
  intervalMs: 3000,
};

const researchUiState = {};

let latestTungeeStatusPayload = null;
const detailPayloadCache = new Map();
const detailPayloadRequestCache = new Map();
const DETAIL_PAYLOAD_CACHE_LIMIT = 40;

function buildApiUrl(path, params = {}) {
  const url = new URL(path, window.location.origin);
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === "") {
      return;
    }
    url.searchParams.set(key, String(value));
  });
  return `${url.pathname}${url.search}`;
}

function renderLoadingState(container, text = "正在加载数据…", { cardCount = 2 } = {}) {
  if (!container) {
    return;
  }
  container.setAttribute("aria-busy", "true");
  container.innerHTML = `
    <div class="loading-block" role="status" aria-live="polite">
      <div class="loading-block__spinner" aria-hidden="true"></div>
      <p class="loading-block__text">${escapeHtml(text)}</p>
    </div>
    <div class="loading-stack">
      ${Array.from({ length: cardCount })
        .map(
          () => `
            <article class="loading-card">
              <div class="skeleton skeleton--title"></div>
              <div class="skeleton skeleton--line"></div>
              <div class="skeleton skeleton--line skeleton--line-short"></div>
            </article>
          `,
        )
        .join("")}
    </div>
  `;
}

function renderStatusLoading(container, text = "正在校验会话状态…") {
  if (!container) {
    return;
  }
  container.setAttribute("aria-busy", "true");
  container.innerHTML = `
    <div class="toolbar-status-card toolbar-status-card--loading" role="status" aria-live="polite">
      <div class="loading-block__spinner loading-block__spinner--inline" aria-hidden="true"></div>
      <span class="toolbar-status-meta">${escapeHtml(text)}</span>
    </div>
  `;
}

function clearBusyState(container) {
  container?.removeAttribute("aria-busy");
}

function setButtonLoading(button, loading, text = "处理中…") {
  if (!button) {
    return;
  }
  if (loading) {
    if (!button.dataset.originalText) {
      button.dataset.originalText = button.textContent || "";
    }
    button.disabled = true;
    button.classList.add("is-loading");
    button.innerHTML = `<span class="btn-spinner" aria-hidden="true"></span><span>${escapeHtml(text)}</span>`;
    return;
  }
  button.disabled = false;
  button.classList.remove("is-loading");
  if (button.dataset.originalText) {
    button.textContent = button.dataset.originalText;
  }
}

function setResearchUiState(queryItemId, state) {
  if (!queryItemId) {
    return;
  }
  if (!state) {
    delete researchUiState[queryItemId];
  } else {
    researchUiState[queryItemId] = {
      ...researchUiState[queryItemId],
      ...state,
    };
  }
  syncResearchButtons(queryItemId);
}

function isResearchInFlight(research) {
  return research?.status === "queued" || research?.status === "running";
}

function formatResearchProgressText(research) {
  const percent = typeof research?.progress_percent === "number" ? research.progress_percent : null;
  if (percent === null) {
    return "详研中…";
  }
  return `详研中 ${percent}%`;
}

function syncResearchButtons(queryItemId = null) {
  const selector = queryItemId
    ? `[data-action="run-research"][data-item-id="${queryItemId}"]`
    : '[data-action="run-research"]';
  document.querySelectorAll(selector).forEach((button) => {
    const itemId = button.dataset.itemId;
    const defaultText = button.dataset.defaultText || button.dataset.originalText || button.textContent || "AI详研";
    button.dataset.originalText = defaultText;
    const state = researchUiState[itemId];
    const backendLoading = ["queued", "running"].includes(button.dataset.researchStatus || "");
    if (state?.loading || backendLoading) {
      setButtonLoading(button, true, state?.text || button.dataset.runningText || "详研中…");
      return;
    }
    setButtonLoading(button, false);
    button.textContent = defaultText;
  });
}

async function withButtonLoading(button, text, task) {
  setButtonLoading(button, true, text);
  try {
    return await task();
  } finally {
    setButtonLoading(button, false);
  }
}

function setQueryFormEnabled(enabled, reason = "") {
  const form = document.getElementById("query-job-form");
  const submitButton = form?.querySelector('button[type="submit"]');
  const textarea = form?.querySelector('textarea[name="company_names"]');
  const message = document.getElementById("query-job-message");

  if (submitButton) {
    submitButton.disabled = !enabled;
  }
  if (textarea) {
    textarea.disabled = !enabled;
  }
  if (!enabled && message && reason) {
    message.textContent = reason;
  }
}

function setFullscreenLoading(visible, text = "", title = "") {
  const overlay = document.getElementById("fullscreen-loading");
  if (!overlay) {
    return;
  }
  const titleNode = overlay.querySelector(".fullscreen-loading__title");
  const textNode = overlay.querySelector(".fullscreen-loading__text");
  if (title && titleNode) {
    titleNode.textContent = title;
  }
  if (text && textNode) {
    textNode.textContent = text;
  }
  overlay.hidden = !visible;
  document.body.style.overflow = visible ? "hidden" : "";
}

function setConsoleJobAutoRefreshIndicator(visible, text = "", state = "loading") {
  const indicator = document.getElementById("console-job-auto-refresh-indicator");
  const textNode = document.getElementById("console-job-auto-refresh-indicator-text");
  if (!indicator || !textNode) {
    return;
  }
  if (consoleJobAutoRefreshState.hideTimer) {
    window.clearTimeout(consoleJobAutoRefreshState.hideTimer);
    consoleJobAutoRefreshState.hideTimer = null;
  }
  if (!visible) {
    indicator.hidden = true;
    delete indicator.dataset.state;
    textNode.textContent = "";
    return;
  }
  indicator.hidden = false;
  indicator.dataset.state = state;
  textNode.textContent = text;
}

function flashConsoleJobAutoRefreshIndicator(text, state = "success", durationMs = 2400) {
  setConsoleJobAutoRefreshIndicator(true, text, state);
  consoleJobAutoRefreshState.hideTimer = window.setTimeout(() => {
    setConsoleJobAutoRefreshIndicator(false);
  }, durationMs);
}

function wait(ms) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

function stopResearchListAutoRefresh() {
  if (researchListAutoRefreshState.timer) {
    window.clearTimeout(researchListAutoRefreshState.timer);
    researchListAutoRefreshState.timer = null;
  }
}

function hasInFlightResearchItems(jobs = []) {
  return jobs.some((job) => (job.items || []).some((item) => isResearchInFlight(item.research || null)));
}

function getResearchListReloadHandler() {
  if (window.BUSSINESS_PAGE === "console") {
    return (options = {}) => reloadConsoleQueryJobs(options);
  }
  if (window.BUSSINESS_PAGE === "history") {
    return (options = {}) => loadHistoryJobs(options);
  }
  if (window.BUSSINESS_PAGE === "admin") {
    return (options = {}) => loadAdminJobs(options);
  }
  return null;
}

function scheduleResearchListAutoRefresh(active) {
  stopResearchListAutoRefresh();
  if (!active) {
    return;
  }
  researchListAutoRefreshState.timer = window.setTimeout(() => {
    void runResearchListAutoRefresh();
  }, researchListAutoRefreshState.intervalMs);
}

async function runResearchListAutoRefresh() {
  if (researchListAutoRefreshState.running) {
    return;
  }
  const reload = getResearchListReloadHandler();
  if (!reload) {
    return;
  }
  if (document.visibilityState === "hidden") {
    scheduleResearchListAutoRefresh(true);
    return;
  }
  researchListAutoRefreshState.running = true;
  try {
    await reload({ silent: true, skipSessionCheck: true });
  } catch (_error) {
    scheduleResearchListAutoRefresh(true);
  } finally {
    researchListAutoRefreshState.running = false;
  }
}

async function pollResearchProgress(queryItemId, { intervalMs = 2500, timeoutMs = 300000, onProgress = null } = {}) {
  const startedAt = Date.now();
  while (Date.now() - startedAt < timeoutMs) {
    const payload = await apiFetch(`/api/research/item/${queryItemId}`);
    const research = payload.research;
    if (!research) {
      await wait(intervalMs);
      continue;
    }

    const stageText = research.current_stage || research.status || "running";
    const percent = typeof research.progress_percent === "number" ? research.progress_percent : 0;
    onProgress?.(research, stageText, percent);

    if (research.status === "completed") {
      return research;
    }
    if (research.status === "failed") {
      throw new Error(research.error_message || "AI详研执行失败");
    }

    await wait(intervalMs);
  }
  throw new Error("AI详研超时，请稍后重试");
}

function formatDateTime(value) {
  if (!value) {
    return "-";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return String(value);
  }
  const parts = new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  }).formatToParts(date);
  const get = (type) => parts.find((part) => part.type === type)?.value || "";
  return `${get("year")}-${get("month")}-${get("day")} ${get("hour")}:${get("minute")}:${get("second")}`;
}

function getTungeeProfileMobile(profile = {}) {
  return String(
    profile?._login_mobile || profile?.phone || profile?.mobile || profile?.login_phone || "",
  ).trim();
}

function getTungeeProfileName(profile = {}) {
  return String(
    profile?.name || profile?.nickname || profile?.nick_name || profile?.user_name || "",
  ).trim();
}

function formatTungeeAccountLabel({ name = "", mobile = "", fallback = "-" } = {}) {
  const normalizedName = String(name || "").trim();
  const normalizedMobile = String(mobile || "").trim();
  if (normalizedName && normalizedMobile) {
    return `${normalizedName}（${normalizedMobile}）`;
  }
  if (normalizedName || normalizedMobile) {
    return normalizedName || normalizedMobile;
  }
  return fallback;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function formatFieldValue(value) {
  if (Array.isArray(value)) {
    return value.length ? value.join("、") : "-";
  }
  return value || "-";
}

function normalizeUrl(url) {
  const raw = String(url || "").trim();
  if (!raw) {
    return "";
  }
  if (/^https?:\/\//i.test(raw)) {
    return raw;
  }
  if (/^\/\//.test(raw)) {
    return `https:${raw}`;
  }
  if (/^(www\.|[a-z0-9-]+\.[a-z]{2,})/i.test(raw)) {
    return `https://${raw}`;
  }
  return raw;
}

function renderExternalLink(url, label) {
  const normalized = normalizeUrl(url);
  if (!normalized) {
    return escapeHtml(label || "-");
  }
  return `<a class="detail-link" href="${escapeHtml(normalized)}" target="_blank" rel="noreferrer">${escapeHtml(label || normalized)}</a>`;
}

function renderVendorMatchList(matches) {
  if (!Array.isArray(matches) || !matches.length) {
    return "";
  }

  return `
    <div class="detail-vendor-match-list">
      ${matches
        .map((match) => {
          const vendorName = String(match?.vendor_name || "").trim();
          const vendorCategory = String(match?.vendor_category || "").trim();
          const clientName = String(match?.client_name || "").trim();
          const confidence = String(match?.confidence || "").trim();
          const collectedDate = String(match?.collected_date || "").trim();
          const evidenceText = String(match?.evidence_text || "").trim();
          const sourceUrl = normalizeUrl(match?.source_url);
          const summaryParts = [
            vendorCategory ? `系统类别：${vendorCategory}` : "",
            clientName ? `客户主体：${clientName}` : "",
            confidence ? `置信度：${confidence}` : "",
            collectedDate ? `采集时间：${collectedDate}` : "",
          ].filter(Boolean);

          return `
            <article class="detail-vendor-match">
              <div class="detail-vendor-match__head">
                <strong class="detail-vendor-match__title">${escapeHtml(vendorName || "本地命中记录")}</strong>
                ${sourceUrl ? `<span class="detail-vendor-match__link">${renderExternalLink(sourceUrl, "公众号原文")}</span>` : ""}
              </div>
              ${
                summaryParts.length
                  ? `<p class="detail-vendor-match__meta">${escapeHtml(summaryParts.join(" · "))}</p>`
                  : ""
              }
              ${
                evidenceText
                  ? `<p class="detail-vendor-match__evidence">${escapeHtml(evidenceText)}</p>`
                  : ""
              }
            </article>
          `;
        })
        .join("")}
    </div>
  `;
}

function statusClass(status) {
  return `status-pill status-pill--${status || "pending"}`;
}

function statusLabel(status) {
  const labels = {
    completed: "已完成",
    partial_success: "部分成功",
    running: "处理中",
    fetching_detail: "抓取详情",
    searching: "查询中",
    failed: "失败",
    session_expired: "会话过期",
    not_found: "未命中",
    hot: "高优先级",
    pending: "等待中",
  };
  return labels[status] || status || "-";
}

function researchStageLabel(stage) {
  const labels = {
    queued: "等待生成",
    resolving_name: "名称校准",
    researching_fields: "字段补全",
    researching_events: "事件补全",
    researching_competitors: "竞品分析",
    building_advice: "生成建议",
    completed: "已完成",
    failed: "失败",
  };
  return labels[stage] || stage || "处理中";
}

function getResearchStatusMeta(item, research = item?.research || null) {
  if (!research) {
    if (item?.status === "completed") {
      return {
        label: "待生成",
        helper: "查询完成后会自动触发",
      };
    }
    return {
      label: "-",
      helper: "",
    };
  }
  if (research.status === "completed") {
    return {
      label: "已完成",
      helper: research.updated_at ? `最近更新：${formatDateTime(research.updated_at)}` : "",
    };
  }
  if (research.status === "failed") {
    return {
      label: "失败",
      helper: research.error_message || "AI详研生成失败",
    };
  }
  const percent = typeof research.progress_percent === "number" ? `${research.progress_percent}%` : "";
  return {
    label: percent ? `生成中 ${percent}` : "生成中",
    helper: researchStageLabel(research.current_stage || research.status),
  };
}

function getResearchActionMeta(research) {
  const defaultText = research ? "重跑AI" : "AI详研";
  if (!isResearchInFlight(research)) {
    return {
      defaultText,
      text: defaultText,
      disabled: false,
      status: research?.status || "",
      runningText: "",
    };
  }
  const runningText = formatResearchProgressText(research);
  return {
    defaultText,
    text: runningText,
    disabled: true,
    status: research.status,
    runningText,
  };
}

function renderStatusPill(status, { translated = false } = {}) {
  return `<span class="${statusClass(status)}">${escapeHtml(translated ? statusLabel(status) : status || "-")}</span>`;
}

function renderStatusSummary(summary = {}) {
  return Object.entries(summary)
    .sort(([, leftCount], [, rightCount]) => rightCount - leftCount)
    .map(
      ([status, count]) =>
        `<span class="summary-pill summary-pill--${escapeHtml(status)}">${escapeHtml(statusLabel(status))} ${escapeHtml(count)}</span>`,
    )
    .join("");
}

function setPillState(element, text, tone = "neutral") {
  if (!element) {
    return;
  }
  element.className = `pill pill--${tone}`;
  element.textContent = text;
}

function setFormMessage(element, text, tone = "error") {
  if (!element) {
    return;
  }
  element.textContent = text || "";
  if (text) {
    element.dataset.tone = tone;
    return;
  }
  delete element.dataset.tone;
}

function setAdminSettingsModalVisible(visible) {
  const modal = document.getElementById("admin-settings-modal");
  if (!modal) {
    return;
  }
  modal.hidden = !visible;
  document.body.style.overflow = visible ? "hidden" : "";
}

function setAdminQueryCount(total) {
  const node = document.getElementById("admin-query-total");
  if (node) {
    node.textContent = String(total);
  }
}

function applyPaginationState(state, pagination = {}) {
  state.page = Number(pagination.page || state.page || 1);
  state.pageSize = Number(pagination.page_size || state.pageSize || 1);
  state.total = Number(pagination.total || 0);
}

function buildDetailPayloadCacheKey(itemPublicId, { admin = false } = {}) {
  return `${admin ? "admin" : "user"}:${itemPublicId || ""}`;
}

function hasFullDetailPayload(payload) {
  const item = payload?.item;
  if (!item) {
    return false;
  }
  return Boolean(
    item.result?.company_snapshot ||
      item.result?.contact_snapshot ||
      item.result?.recruitment_snapshot ||
      item.research?.first_contact_script ||
      (Array.isArray(item.research?.field_results) && item.research.field_results.length) ||
      (Array.isArray(item.research?.event_results) && item.research.event_results.length) ||
      item.started_at ||
      item.finished_at ||
      item.error_message,
  );
}

function setDetailPayloadCache(cacheKey, payload) {
  if (!cacheKey || !hasFullDetailPayload(payload)) {
    return;
  }
  if (detailPayloadCache.has(cacheKey)) {
    detailPayloadCache.delete(cacheKey);
  }
  detailPayloadCache.set(cacheKey, payload);
  if (detailPayloadCache.size <= DETAIL_PAYLOAD_CACHE_LIMIT) {
    return;
  }
  const oldestKey = detailPayloadCache.keys().next().value;
  if (oldestKey) {
    detailPayloadCache.delete(oldestKey);
  }
}

function clearDetailPayloadCache({ admin = null, jobPublicId = null, itemPublicId = null } = {}) {
  if (admin === null && !jobPublicId && !itemPublicId) {
    detailPayloadCache.clear();
    detailPayloadRequestCache.clear();
    return;
  }

  for (const [cacheKey, payload] of detailPayloadCache.entries()) {
    const cacheAdmin = cacheKey.startsWith("admin:");
    if (admin !== null && cacheAdmin !== admin) {
      continue;
    }
    if (jobPublicId && payload?.job?.public_id !== jobPublicId) {
      continue;
    }
    if (itemPublicId && payload?.item?.public_id !== itemPublicId) {
      continue;
    }
    detailPayloadCache.delete(cacheKey);
  }

  for (const cacheKey of detailPayloadRequestCache.keys()) {
    const cacheAdmin = cacheKey.startsWith("admin:");
    if (admin !== null && cacheAdmin !== admin) {
      continue;
    }
    if (itemPublicId && !cacheKey.endsWith(`:${itemPublicId}`)) {
      continue;
    }
    detailPayloadRequestCache.delete(cacheKey);
  }
}

function getDetailPayloadFromLoadedJobs(jobPublicId, itemPublicId, { admin = false } = {}) {
  const jobCollections = admin ? [adminJobState.jobs] : [recentJobState.jobs, historyJobState.jobs];
  for (const jobs of jobCollections) {
    const job = (jobs || []).find((entry) => entry.public_id === jobPublicId);
    const item = (job?.items || []).find((entry) => entry.public_id === itemPublicId);
    const payload = job && item ? { job, item } : null;
    if (hasFullDetailPayload(payload)) {
      return payload;
    }
  }
  return null;
}

async function fetchJobDetailForItem(jobPublicId, itemPublicId, { admin = false } = {}) {
  const cacheKey = buildDetailPayloadCacheKey(itemPublicId, { admin });
  const cachedPayload = detailPayloadCache.get(cacheKey);
  if (cachedPayload) {
    return cachedPayload;
  }

  const loadedPayload = getDetailPayloadFromLoadedJobs(jobPublicId, itemPublicId, { admin });
  if (loadedPayload) {
    setDetailPayloadCache(cacheKey, loadedPayload);
    return loadedPayload;
  }

  const pendingRequest = detailPayloadRequestCache.get(cacheKey);
  if (pendingRequest) {
    return pendingRequest;
  }

  const request = apiFetch(
    admin ? `/api/admin/query-jobs/items/${itemPublicId}/detail` : `/api/query-jobs/items/${itemPublicId}/detail`,
  )
    .then((payload) => {
      const detailPayload = {
        job: payload.job || null,
        item: payload.item || null,
      };
      if (!detailPayload.item) {
        throw new Error("查询项详情不存在");
      }
      setDetailPayloadCache(cacheKey, detailPayload);
      return detailPayload;
    })
    .finally(() => {
      detailPayloadRequestCache.delete(cacheKey);
    });

  detailPayloadRequestCache.set(cacheKey, request);
  return request;
}

function canDeleteRecord(item) {
  return ["completed", "failed", "not_found", "session_expired"].includes(item?.status);
}

function openJobExport(jobId, format) {
  window.open(`/api/query-jobs/${jobId}/export?format=${format}`, "_blank");
}

function isTerminalQueryJobStatus(status) {
  return TERMINAL_QUERY_JOB_STATUSES.has(status);
}

function summarizeProcessedItems(job) {
  return Object.entries(job?.summary || {}).reduce((total, [status, count]) => {
    if (!TERMINAL_QUERY_ITEM_STATUSES.has(status)) {
      return total;
    }
    return total + Number(count || 0);
  }, 0);
}

function sortJobsByCreatedAt(jobs) {
  return [...jobs].sort((left, right) => {
    const leftTimestamp = Date.parse(left?.created_at || "") || 0;
    const rightTimestamp = Date.parse(right?.created_at || "") || 0;
    if (rightTimestamp !== leftTimestamp) {
      return rightTimestamp - leftTimestamp;
    }
    return String(right?.public_id || "").localeCompare(String(left?.public_id || ""));
  });
}

function upsertRecentJob(job) {
  if (!job?.public_id) {
    return;
  }
  const canAffectCurrentTotal = !recentJobState.search.trim() && recentJobState.status === "all";
  if (canAffectCurrentTotal && !recentJobState.jobs.some((existingJob) => existingJob.public_id === job.public_id)) {
    recentJobState.total += 1;
  }
  recentJobState.jobs = sortJobsByCreatedAt([
    job,
    ...recentJobState.jobs.filter((existingJob) => existingJob.public_id !== job.public_id),
  ]);
  renderRecentJobs();
}

function buildQueryJobAutoRefreshMessage(job, { terminal = false } = {}) {
  const statusText = statusLabel(job?.status || "pending");
  const submittedCount = Number(job?.submitted_count || 0);
  const processedCount = Math.min(summarizeProcessedItems(job), submittedCount);
  const progressText = submittedCount > 0 ? `（已处理 ${processedCount}/${submittedCount}）` : "";
  if (terminal) {
    return `后台自动刷新完成，当前批次状态：${statusText}${progressText}`;
  }
  return `已提交，正在后台自动刷新状态… 当前状态：${statusText}${progressText}`;
}

async function pollQueryJobDetail(
  jobPublicId,
  { intervalMs = 2500, timeoutMs = 300000, onProgress = null, token = consoleJobAutoRefreshState.token } = {},
) {
  const startedAt = Date.now();

  while (Date.now() - startedAt < timeoutMs) {
    const payload = await apiFetch(`/api/query-jobs/${jobPublicId}`);
    if (token !== consoleJobAutoRefreshState.token) {
      return null;
    }

    const job = payload.job;
    if (job) {
      onProgress?.(job);
      if (isTerminalQueryJobStatus(job.status)) {
        return job;
      }
    }

    await wait(intervalMs);
    if (token !== consoleJobAutoRefreshState.token) {
      return null;
    }
  }

  if (token !== consoleJobAutoRefreshState.token) {
    return null;
  }
  throw new Error("后台自动刷新超时，请稍后手动刷新查看");
}

function startConsoleJobAutoRefresh(job, messageElement) {
  if (!job?.public_id) {
    return;
  }
  const token = ++consoleJobAutoRefreshState.token;

  recentJobState.page = 1;
  upsertRecentJob(job);
  setFormMessage(messageElement, buildQueryJobAutoRefreshMessage(job), "neutral");
  setConsoleJobAutoRefreshIndicator(true, "正在后台自动刷新批次状态…", "loading");

  void pollQueryJobDetail(job.public_id, {
    token,
    timeoutMs: 300000,
    onProgress: (nextJob) => {
      if (token !== consoleJobAutoRefreshState.token) {
        return;
      }
      upsertRecentJob(nextJob);
      setFormMessage(messageElement, buildQueryJobAutoRefreshMessage(nextJob), "neutral");
      setConsoleJobAutoRefreshIndicator(true, `正在后台自动刷新，当前状态：${statusLabel(nextJob.status || "pending")}`, "loading");
    },
  })
    .then((finalJob) => {
      if (!finalJob || token !== consoleJobAutoRefreshState.token) {
        return;
      }
      const tone = ["failed", "session_expired"].includes(finalJob.status) ? "error" : "success";
      setFormMessage(messageElement, buildQueryJobAutoRefreshMessage(finalJob, { terminal: true }), tone);
      if (tone !== "error") {
        window.setTimeout(() => {
          void reloadConsoleQueryJobs().catch(() => {});
        }, 1200);
      }
      flashConsoleJobAutoRefreshIndicator(
        tone === "error" ? `后台自动刷新结束：${statusLabel(finalJob.status)}` : "后台自动刷新完成",
        tone === "error" ? "error" : "success",
      );
    })
    .catch((error) => {
      if (token !== consoleJobAutoRefreshState.token) {
        return;
      }
      const timeoutMessage = "已提交，正在后台自动刷新状态… 当前批次仍在处理中，可稍后手动刷新查看。";
      if (String(error?.message || "").includes("超时")) {
        setFormMessage(messageElement, timeoutMessage, "neutral");
        flashConsoleJobAutoRefreshIndicator("后台自动刷新超时，可稍后手动刷新查看", "error", 3200);
        return;
      }
      setFormMessage(messageElement, `后台自动刷新失败：${error.message || "请稍后手动刷新查看。"}`);
      flashConsoleJobAutoRefreshIndicator("后台自动刷新失败", "error", 3200);
    });
}

function renderExportFields(result) {
  if (!result || !result.export_fields) {
    return "";
  }

  const fields = result.export_fields;
  const fieldOrder = [
    "公司名称",
    "行业",
    "客户行业",
    "客户省份",
    "规模",
    "城市",
    "成立年份",
    "注册资本",
    "法人",
    "官网",
    "统一信用代码",
    "客户产品/服务",
    "商业模式",
    "客户客群",
    "是否上市",
    "是否IPO",
    "客户收入规模",
    "客户利润",
    "客户营收增长情况",
    "已上线系统",
    "数字化项目动态",
    "数据现状",
    "BI切入机会",
    "相似客户",
    "业务标签",
    "联系人1姓名",
    "联系人1职位",
    "联系人1手机号",
    "联系人2姓名",
    "联系人2职位",
    "联系人2手机号",
    "招聘代表岗位",
    "在招职位数",
    "客户招聘信息",
    "IT团队规模",
    "企业近一年重大事件",
  ];

  return `
    <div class="kv-grid">
      ${fieldOrder
        .map((key) => {
          const value = fields[key];
          const normalized = formatFieldValue(value);
          return `
            <div class="kv-item">
              <span class="kv-label">${escapeHtml(key)}</span>
              <span class="kv-value">${escapeHtml(normalized)}</span>
            </div>
          `;
        })
        .join("")}
    </div>
  `;
}

function renderCollapsibleSection(title, contentHtml, { collapsed = false } = {}) {
  return `
    <section class="detail-section" data-collapsed="${collapsed ? "true" : "false"}">
      <div class="detail-section__header">
        <h4 class="detail-section__title">${escapeHtml(title)}</h4>
        <button class="ghost-btn detail-toggle-btn" type="button" data-action="toggle-detail-section">${collapsed ? "展开" : "收起"}</button>
      </div>
      <div class="detail-section__content"${collapsed ? ' hidden="hidden"' : ""}>
        ${contentHtml}
      </div>
    </section>
  `;
}

function collectRelatedLinks({ item, research, profileSources, events, contactList, recruitings }) {
  const links = [];
  const seen = new Set();
  const pushLink = (label, url, type) => {
    if (!url) return;
    const normalized = normalizeUrl(url);
    if (!normalized || seen.has(`${type}:${normalized}`)) return;
    seen.add(`${type}:${normalized}`);
    links.push({ label, url: normalized, type });
  };

  if (item.external_company_id) {
    pushLink("探迹详情-基本信息", buildTungeeCompanyDetailUrl(item.external_company_id), "探迹");
    pushLink("探迹详情-经营信息", buildTungeeCompanyBusinessInfoUrl(item.external_company_id), "探迹");
  }

  const homepage = item.result?.company_snapshot?.basic?.homepage || item.result?.export_fields?.["官网"];
  pushLink("企业官网", homepage, "官网");

  (contactList || []).forEach((contact, index) => {
    pushLink(`联系方式来源${index + 1}`, contact.source_url, "联系方式");
  });

  (recruitings || []).forEach((job, index) => {
    pushLink(job.title || `招聘原文${index + 1}`, job.source_url, "招聘");
  });

  (profileSources || []).forEach((source) => {
    pushLink(source.source_title || source.field_name || "画像来源", source.source_url, "画像");
  });

  (events || []).forEach((event) => {
    pushLink(event.title || "事件来源", event.source_url, "事件");
  });

  if (research) {
    (research.field_results || []).forEach((field) => {
      pushLink(field.source || field.field_name || "AI详研来源", field.url, "AI详研");
    });
    (research.event_results || []).forEach((event) => {
      pushLink(event.source || event.title || "AI详研事件来源", event.url, "AI详研");
    });
    (research.competitors || []).forEach((competitor) => {
      pushLink(competitor.source || competitor.name || "竞品来源", competitor.url, "竞品");
    });
  }

  return links;
}

function buildRecruitingSearchText(job) {
  const experience = job?.seniority_min
    ? `${job.seniority_min}${job?.seniority_max ? `-${job.seniority_max}` : "+"}年`
    : "";
  return normalizeSearchText(
    [
      job?.title,
      job?.city,
      job?.district,
      job?.education,
      experience,
      job?.salary_min,
      job?.salary_max,
      job?.salary_currency,
      job?.published_at,
      job?.source,
      job?.desc,
    ]
      .filter(Boolean)
      .join(" "),
  );
}

function bindRecruitingSearch(root = document) {
  root.querySelectorAll('[data-role="recruitment-filter"]').forEach((section) => {
    if (section.dataset.bound === "true") {
      return;
    }
    section.dataset.bound = "true";
    const input = section.querySelector('[data-action="filter-recruitings"]');
    const counter = section.querySelector('[data-role="recruiting-filter-count"]');
    const empty = section.querySelector('[data-role="recruiting-filter-empty"]');
    const rows = Array.from(section.querySelectorAll('[data-role="recruiting-row"]'));
    const total = rows.length;

    const applyFilter = () => {
      const keyword = normalizeSearchText(input?.value || "");
      let visibleCount = 0;
      rows.forEach((row) => {
        const haystack = row.dataset.searchText || "";
        const matched = !keyword || haystack.includes(keyword);
        row.style.display = matched ? "" : "none";
        if (matched) {
          visibleCount += 1;
        }
      });
      if (counter) {
        counter.textContent = keyword ? `显示 ${visibleCount} / ${total}` : `共 ${total} 个岗位`;
      }
      if (empty) {
        empty.hidden = visibleCount > 0;
      }
    };

    input?.addEventListener("input", applyFilter);
    applyFilter();
  });
}

function buildTungeeCompanyDetailUrl(externalCompanyId) {
  if (!externalCompanyId) {
    return "";
  }
  return `https://sales.tungee.com/enterprise-details/${externalCompanyId}/enterprise-information/basic-information`;
}

function buildTungeeCompanyBusinessInfoUrl(externalCompanyId) {
  if (!externalCompanyId) {
    return "";
  }
  return `https://sales.tungee.com/enterprise-details/${externalCompanyId}/enterprise-information/bussinesss-information`;
}

function parseNumericValue(value) {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : null;
}

function compactText(value, maxLength = 120) {
  const text = String(value || "").trim();
  if (!text) {
    return "";
  }
  if (text.length <= maxLength) {
    return text;
  }
  return `${text.slice(0, Math.max(0, maxLength - 1)).trim()}…`;
}

function normalizeSearchText(value) {
  return String(value ?? "")
    .toLowerCase()
    .replace(/\s+/g, " ")
    .trim();
}

function hasMeaningfulValue(value) {
  if (Array.isArray(value)) {
    return value.some((entry) => hasMeaningfulValue(entry));
  }
  if (value === null || value === undefined) {
    return false;
  }
  const text = String(value).trim();
  return text !== "" && text !== "-";
}

function normalizeConfidenceValue(value) {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value > 1 ? value / 100 : value;
  }
  const raw = String(value || "").trim();
  if (!raw) {
    return null;
  }
  if (raw.endsWith("%")) {
    const percent = Number(raw.slice(0, -1));
    return Number.isFinite(percent) ? percent / 100 : null;
  }
  const numeric = Number(raw);
  if (Number.isFinite(numeric)) {
    return numeric > 1 ? numeric / 100 : numeric;
  }
  if (raw.includes("高")) {
    return 0.85;
  }
  if (raw.includes("中")) {
    return 0.6;
  }
  if (raw.includes("低")) {
    return 0.35;
  }
  return null;
}

function deriveFollowDecision({ status, research, contactList = [], primaryEntryPoint = "", followupSuggestions = [] }) {
  const hasContacts = contactList.length > 0;
  const hasResearchSignal =
    hasMeaningfulValue(primaryEntryPoint) ||
    hasMeaningfulValue(research?.data_status_summary) ||
    followupSuggestions.length > 0;
  const researchReady = research?.status === "completed";

  if (researchReady && hasResearchSignal && hasContacts) {
    return {
      level: "high",
      label: "高",
      conclusion: "可优先触达",
      tone: "good",
      summary: "AI 详研已给出较明确切入口，且当前已有可用联系人，可以优先推进首轮触达。",
    };
  }
  if (researchReady && hasResearchSignal) {
    return {
      level: "mid",
      label: "中",
      conclusion: "继续推进",
      tone: "warn",
      summary: "AI 详研已形成主切口，但联系人信息仍需补强，建议先补齐触达对象后推进。",
    };
  }
  if (status === "completed" && hasContacts) {
    return {
      level: "mid",
      label: "中",
      conclusion: "持续观察",
      tone: "info",
      summary: "基础资料和联系人已经具备，建议等待 AI 详研补齐判断，再决定推进节奏。",
    };
  }
  return {
    level: "low",
    label: "低",
    conclusion: "暂缓推进",
    tone: "muted",
    summary: "当前可支撑的判断仍偏少，建议先等待 AI 详研完成或继续补齐关键信息。",
  };
}

function contactDisplayName(contact) {
  return contact?.name || contact?.contactName || "-";
}

function contactDisplayPosition(contact) {
  return contact?.position || contact?.jobTitle || "-";
}

function contactDisplayValue(contact) {
  return String(contact?.phone || contact?.contact_label || "").trim();
}

function hasRenderableContact(contact) {
  return hasMeaningfulValue(contactDisplayValue(contact)) || Boolean(normalizeUrl(contact?.source_url));
}

function isPhoneLike(value) {
  const text = String(value || "").trim();
  const digitCount = (text.match(/\d/g) || []).length;
  return text && !text.includes("@") && digitCount >= 7 && /^[\d*+\-()\s]+$/.test(text);
}

const PRIMARY_CONTACT_KEYWORDS = ["信息", "IT", "技术", "数据", "数字化", "CIO", "CTO", "信息化"];
const SECONDARY_CONTACT_KEYWORDS = ["运营", "销售", "市场", "负责人", "总监", "经理"];

function contactRoleTier(position) {
  const text = String(position || "").trim();
  if (!text) {
    return 0;
  }
  if (PRIMARY_CONTACT_KEYWORDS.some((keyword) => text.toLowerCase().includes(keyword.toLowerCase()))) {
    return 2;
  }
  if (SECONDARY_CONTACT_KEYWORDS.some((keyword) => text.includes(keyword))) {
    return 1;
  }
  return 0;
}

function contactRoleLabel(position) {
  const tier = contactRoleTier(position);
  if (tier === 2) {
    return "优先联系";
  }
  if (tier === 1) {
    return "可作为备选";
  }
  return "";
}

function contactQuality(contact) {
  const hasPhone = isPhoneLike(contactDisplayValue(contact));
  const hasSourceUrl = Boolean(normalizeUrl(contact?.source_url));
  if (contact?.is_hot && hasPhone) {
    return {
      label: "联系质量高",
      tone: "good",
    };
  }
  if (hasPhone || hasSourceUrl) {
    return {
      label: "联系质量中",
      tone: "info",
    };
  }
  if (hasMeaningfulValue(contactDisplayValue(contact))) {
    return {
      label: "联系质量低",
      tone: "muted",
    };
  }
  return null;
}

function contactReasons(contact) {
  const reasons = [];
  if (contact?.is_hot) {
    reasons.push("HOT 联系人");
  }
  const tier = contactRoleTier(contactDisplayPosition(contact));
  if (tier === 2) {
    reasons.push("岗位高度相关");
  } else if (tier === 1) {
    reasons.push("可作为业务备选");
  }
  if (isPhoneLike(contactDisplayValue(contact))) {
    reasons.push("联系方式完整");
  }
  if (normalizeUrl(contact?.source_url)) {
    reasons.push("存在来源链接");
  }
  return reasons.slice(0, 4);
}

function sortContactsForPriority(contacts = []) {
  return contacts
    .map((contact, index) => ({ ...contact, _index: index }))
    .sort((left, right) => {
      if (Boolean(right.is_hot) !== Boolean(left.is_hot)) {
        return Number(Boolean(right.is_hot)) - Number(Boolean(left.is_hot));
      }
      const roleGap = contactRoleTier(contactDisplayPosition(right)) - contactRoleTier(contactDisplayPosition(left));
      if (roleGap !== 0) {
        return roleGap;
      }
      const phoneGap = Number(isPhoneLike(contactDisplayValue(right))) - Number(isPhoneLike(contactDisplayValue(left)));
      if (phoneGap !== 0) {
        return phoneGap;
      }
      const sourceGap = Number(Boolean(normalizeUrl(right.source_url))) - Number(Boolean(normalizeUrl(left.source_url)));
      if (sourceGap !== 0) {
        return sourceGap;
      }
      return left._index - right._index;
    });
}

function uniqueItems(items = []) {
  const seen = new Set();
  return items.filter((item) => {
    const text = String(item || "").trim();
    if (!text || seen.has(text)) {
      return false;
    }
    seen.add(text);
    return true;
  });
}

function splitResearchDataSummary(summary) {
  const text = String(summary || "").trim();
  if (!text) {
    return {
      systemSummary: "",
      identitySummary: "",
      completenessSummary: "",
      generalSummary: "",
      dynamicItems: [],
    };
  }

  const normalizeSectionBody = (value) =>
    String(value || "")
      .replace(/^\s+|\s+$/g, "")
      .replace(/\n{3,}/g, "\n\n");
  const dynamicPattern = /战略动态|近期重大动态|近期动态|重大动态|合作动态|产品规划|业务动态|融资动态|资本动态|里程碑/i;
  const systemPattern = /系统现状|本地库命中|数据现状|数字化现状|数字化建设|系统建设|建设进展|IT现状|IT能力|数据平台|数据中台|数据仓库|已上线系统/i;
  const identityPattern = /企业身份识别|主体识别|工商核验|名称核验|工商信息|基础信息/i;
  const completenessPattern = /信息完整度|资料完整度|数据完整度|完整度评估/i;
  const identityContentPattern = /主体已确认|统一社会信用代码|成立时间|注册资本|实缴资本|法定代表人|总部所在地|注册地址|员工规模|社保人数/i;
  const completenessContentPattern = /工商信息完整度|系统\/数字化信息|财务数据|合规记录|未公开披露|已整改完成|部分缺失/i;
  const systemContentPattern = /CDP|CRM|ERP|OA|BI|MIS|MES|SRM|WMS|TMS|数据平台|数据中台|数据仓库|数字化|智能运营|数据分析|营销自动化|已上线系统|本地库命中|厂商/i;

  const headingPatterns = [/【([^】]+)】/g, /(?:^|\n)\*\*([^*\n]+?)\*\*(?=\n|$)/g, /(?:^|\n)#{1,4}\s*([^\n#]+?)\s*(?=\n|$)/g];
  const headingMatches = headingPatterns.flatMap((pattern) =>
    [...text.matchAll(pattern)].map((match) => ({
      label: String(match[1] || "").trim(),
      start: match.index ?? 0,
      contentStart: (match.index ?? 0) + match[0].length,
    })),
  );
  const matches = headingMatches
    .filter((match) => match.label)
    .sort((left, right) => left.start - right.start)
    .filter((match, index, items) => index === 0 || match.start !== items[index - 1].start || match.label !== items[index - 1].label);

  const sections = matches
    .map((match, index) => {
      const nextStart = matches[index + 1]?.start ?? text.length;
      return {
        label: match.label,
        body: normalizeSectionBody(text.slice(match.contentStart, nextStart)),
      };
    })
    .filter((section) => section.label && section.body);

  const normalizeSections = (items) =>
    items
      .map((section) => section.body)
      .filter(Boolean)
      .join("\n\n");

  if (!sections.length) {
    const blocks = text
      .split(/\n\s*\n+/)
      .map((block) => normalizeSectionBody(block))
      .filter(Boolean);
    const systemBlocks = blocks.filter((block) => systemContentPattern.test(block) && !dynamicPattern.test(block));
    const identityBlocks = blocks.filter((block) => identityContentPattern.test(block));
    const completenessBlocks = blocks.filter((block) => completenessContentPattern.test(block));
    const dynamicItems = blocks.filter((block) => dynamicPattern.test(block));
    const generalBlocks = blocks.filter(
      (block) =>
        !systemBlocks.includes(block) &&
        !identityBlocks.includes(block) &&
        !completenessBlocks.includes(block) &&
        !dynamicItems.includes(block),
    );
    const generalSummary = generalBlocks.join("\n\n");
    const fallbackSystemSummary = systemBlocks.length
      ? systemBlocks.join("\n\n")
      : identityBlocks.length || completenessBlocks.length || dynamicItems.length
        ? generalSummary
        : text;
    return {
      systemSummary: fallbackSystemSummary,
      identitySummary: identityBlocks.join("\n\n"),
      completenessSummary: completenessBlocks.join("\n\n"),
      generalSummary: fallbackSystemSummary === generalSummary ? "" : generalSummary,
      dynamicItems,
    };
  }

  const systemSections = sections.filter((section) => systemPattern.test(section.label));
  const identitySections = sections.filter((section) => identityPattern.test(section.label));
  const completenessSections = sections.filter((section) => completenessPattern.test(section.label));
  const dynamicSections = sections.filter((section) => dynamicPattern.test(section.label));
  const neutralSections = sections.filter(
    (section) =>
      !dynamicPattern.test(section.label) &&
      !systemPattern.test(section.label) &&
      !identityPattern.test(section.label) &&
      !completenessPattern.test(section.label),
  );
  const systemSummary = systemSections.length ? normalizeSections(systemSections) : neutralSections.length === 1 ? normalizeSections(neutralSections) : "";
  const identitySummary = normalizeSections(identitySections);
  const completenessSummary = normalizeSections(completenessSections);
  const generalSummary = !systemSections.length && neutralSections.length === 1 ? "" : normalizeSections(neutralSections);
  const dynamicItems = dynamicSections.map((section) => section.body);

  return {
    systemSummary,
    identitySummary,
    completenessSummary,
    generalSummary,
    dynamicItems,
  };
}

function buildRiskTags({ contactList, research, nameCalibration, status }) {
  const tags = [];
  if (!contactList.length) {
    tags.push("暂无有效联系方式");
  }
  if (!research) {
    tags.push("未生成 AI 详研");
  }
  const confidence = normalizeConfidenceValue(research?.name_resolution_confidence ?? nameCalibration?.confidence);
  if (confidence !== null && confidence < 0.7) {
    tags.push("名称待核验");
  }
  if (["failed", "session_expired", "not_found"].includes(status)) {
    tags.push(`状态：${statusLabel(status)}`);
  }
  return uniqueItems(tags).slice(0, 3);
}

function renderChip(text, tone = "soft") {
  if (!hasMeaningfulValue(text)) {
    return "";
  }
  return `<span class="detail-chip detail-chip--${tone}">${escapeHtml(text)}</span>`;
}

function renderChipGroup(items = [], tone = "soft") {
  const chips = items.map((item) => renderChip(item, tone)).filter(Boolean);
  if (!chips.length) {
    return "";
  }
  return `<div class="detail-chip-row">${chips.join("")}</div>`;
}

function renderList(items = [], emptyText = "暂无信息") {
  if (!items.length) {
    return `<p class="detail-empty">${escapeHtml(emptyText)}</p>`;
  }
  return `
    <ul class="detail-list">
      ${items
        .map((item) => `<li>${escapeHtml(item)}</li>`)
        .join("")}
    </ul>
  `;
}

function splitDetailLabelText(item, fallbackLabel = "要点") {
  const text = String(item || "").trim();
  if (!text) {
    return {
      label: fallbackLabel,
      value: "",
    };
  }
  const separatorIndex = text.indexOf("：");
  if (separatorIndex === -1) {
    return {
      label: fallbackLabel,
      value: text,
    };
  }
  const label = text.slice(0, separatorIndex).trim();
  const value = text.slice(separatorIndex + 1).trim();
  return {
    label: label || fallbackLabel,
    value: value || text,
  };
}

function renderSignalList(items = [], emptyText = "暂无信息", { fallbackLabel = "线索" } = {}) {
  if (!items.length) {
    return `<p class="detail-empty">${escapeHtml(emptyText)}</p>`;
  }
  return `
    <div class="detail-signal-list">
      ${items
        .map((item) => {
          const { label, value } = splitDetailLabelText(item, fallbackLabel);
          return `
            <article class="detail-signal">
              <span class="detail-signal__label">${escapeHtml(label)}</span>
              <p class="detail-signal__text detail-copy">${escapeHtml(value)}</p>
            </article>
          `;
        })
        .join("")}
    </div>
  `;
}

function renderStepList(items = [], emptyText = "暂无信息", { fallbackLabel = "动作建议" } = {}) {
  if (!items.length) {
    return `<p class="detail-empty">${escapeHtml(emptyText)}</p>`;
  }
  return `
    <ol class="detail-step-list">
      ${items
        .map((item) => {
          const { label, value } = splitDetailLabelText(item, fallbackLabel);
          return `
            <li class="detail-step-list__item">
              <div class="detail-step-list__content">
                <span class="detail-step-list__label">${escapeHtml(label)}</span>
                <p class="detail-step-list__text detail-copy">${escapeHtml(value)}</p>
              </div>
            </li>
          `;
        })
        .join("")}
    </ol>
  `;
}

function renderStatCard(label, value, helper = "") {
  return `
    <article class="detail-stat-card">
      <div class="detail-stat-label">${escapeHtml(label)}</div>
      <div class="detail-stat-value">${escapeHtml(value || "-")}</div>
      ${helper ? `<div class="detail-stat-helper">${escapeHtml(helper)}</div>` : ""}
    </article>
  `;
}

function renderKeyValueGrid(items = [], emptyText = "暂无信息") {
  const rows = items.filter((item) => hasMeaningfulValue(item?.value));
  if (!rows.length) {
    return `<p class="detail-empty">${escapeHtml(emptyText)}</p>`;
  }
  return `
    <div class="kv-grid detail-kv-grid">
      ${rows
        .map(
          (item) => `
            <div class="kv-item">
              <span class="kv-label">${escapeHtml(item.label || "-")}</span>
              <span class="kv-value">${escapeHtml(formatFieldValue(item.value))}</span>
            </div>
          `,
        )
        .join("")}
    </div>
  `;
}

function renderEvidenceBlock(title, contentHtml) {
  return `
    <div class="detail-evidence-block">
      <h5>${escapeHtml(title)}</h5>
      ${contentHtml}
    </div>
  `;
}

function renderContactCard(contact, { primary = false } = {}) {
  if (!contact) {
    return "";
  }
  const value = contactDisplayValue(contact) || "-";
  const quality = contactQuality(contact);
  const roleLabel = contactRoleLabel(contactDisplayPosition(contact));
  const reasons = contactReasons(contact);
  return `
    <article class="contact-card${primary ? " contact-card--primary" : ""}">
      <div class="contact-card__header">
        <div>
          <h5 class="contact-card__name">${escapeHtml(contactDisplayName(contact))}</h5>
          <p class="contact-card__position">${escapeHtml(contactDisplayPosition(contact))}</p>
        </div>
        <div class="contact-card__badges">
          ${contact.is_hot ? '<span class="status-pill status-pill--hot">HOT</span>' : ""}
          ${roleLabel ? renderChip(roleLabel, primary ? "good" : "soft") : ""}
          ${quality ? renderChip(quality.label, quality.tone) : ""}
        </div>
      </div>
      <p class="contact-card__phone">${escapeHtml(value)}</p>
      <div class="contact-card__meta">
        <span>来源：${escapeHtml(contact.source || "-")}</span>
        ${contact.source_url ? renderExternalLink(contact.source_url, "查看来源") : ""}
      </div>
      ${renderChipGroup(reasons, primary ? "signal" : "soft")}
    </article>
  `;
}

function firstMeaningfulValue(...values) {
  return values.find((value) => hasMeaningfulValue(value)) || "";
}

function shortenOpaqueId(value, length = 8) {
  const raw = String(value || "").trim();
  if (!raw) {
    return "";
  }
  const normalized = raw.replace(/[^a-zA-Z0-9]/g, "");
  return (normalized || raw).slice(0, length).toUpperCase();
}

function formatShortDate(value) {
  if (!value) {
    return "";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return String(value || "")
      .trim()
      .replace(/\s.+$/, "")
      .replaceAll("-", ".");
  }
  const parts = new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(date);
  const get = (type) => parts.find((part) => part.type === type)?.value || "";
  return `${get("year")}.${get("month")}.${get("day")}`;
}

function splitTagText(value, { limit = 4 } = {}) {
  const rawItems = Array.isArray(value) ? value : [value];
  return uniqueItems(
    rawItems
      .flatMap((item) => String(item || "").split(/[、，,；;|｜\n]/))
      .map((entry) => entry.trim())
      .filter(Boolean),
  ).slice(0, limit);
}

function deriveRevenueMeterWidth(value) {
  const text = String(value || "").trim();
  if (!text) {
    return 36;
  }
  if (/千亿|1000亿/.test(text)) {
    return 92;
  }
  if (/百亿|100亿|200亿|500亿/.test(text)) {
    return 84;
  }
  if (/50亿|20亿/.test(text)) {
    return 72;
  }
  if (/10亿/.test(text)) {
    return 62;
  }
  if (/亿/.test(text)) {
    return 54;
  }
  if (/千万/.test(text)) {
    return 40;
  }
  if (/百万/.test(text)) {
    return 30;
  }
  return 48;
}

function contactUpdatedAt(contact) {
  return firstMeaningfulValue(
    contact?.updated_at,
    contact?.updatedAt,
    contact?.fetched_at,
    contact?.created_at,
    contact?.createdAt,
  );
}

function renderSvgIcon(name, className = "") {
  const classAttr = className ? ` class="${escapeHtml(className)}"` : "";
  const icons = {
    company: `
      <svg${classAttr} viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M4.5 19.5V6.5a1 1 0 0 1 1-1H10v4l3-2.25L16 9V4.5h2.5a1 1 0 0 1 1 1v14H4.5Z" fill="currentColor"></path>
      </svg>
    `,
    users: `
      <svg${classAttr} viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M8.25 11a3.25 3.25 0 1 0 0-6.5 3.25 3.25 0 0 0 0 6.5Z" fill="currentColor"></path>
        <path d="M16.75 10.5a2.75 2.75 0 1 0 0-5.5 2.75 2.75 0 0 0 0 5.5Z" fill="currentColor" opacity="0.78"></path>
        <path d="M3.75 18.75a4.5 4.5 0 0 1 9 0" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"></path>
        <path d="M13 18.75a3.75 3.75 0 0 1 7.25-1.25" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" opacity="0.78"></path>
      </svg>
    `,
    search: `
      <svg${classAttr} viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <circle cx="11" cy="11" r="6.5" stroke="currentColor" stroke-width="1.9"></circle>
        <path d="m16 16 4 4" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"></path>
      </svg>
    `,
    phone: `
      <svg${classAttr} viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M7.7 5.25h2.15c.27 0 .5.18.57.44l.74 2.78a.66.66 0 0 1-.19.66l-1.32 1.19a12.9 12.9 0 0 0 4.03 4.03l1.19-1.32a.66.66 0 0 1 .66-.19l2.78.74c.26.07.44.3.44.57v2.15c0 .35-.28.63-.63.65A11.96 11.96 0 0 1 6.4 6a.63.63 0 0 1 .65-.75Z" fill="currentColor"></path>
      </svg>
    `,
    chat: `
      <svg${classAttr} viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M13.75 5.25c3.45 0 6.25 2.22 6.25 4.96 0 1.27-.62 2.43-1.66 3.3l.48 2.24-2.36-.98a7.4 7.4 0 0 1-2.71.5c-3.45 0-6.25-2.22-6.25-4.96s2.8-5.06 6.25-5.06Z" fill="currentColor"></path>
        <path d="M9.5 9.75c-2.9 0-5.25 1.88-5.25 4.2 0 .95.4 1.83 1.08 2.52L4.9 18.5l1.94-.82c.8.28 1.68.42 2.66.42" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" opacity="0.82"></path>
      </svg>
    `,
    copy: `
      <svg${classAttr} viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <rect x="8.25" y="8.25" width="10.5" height="11" rx="2.1" stroke="currentColor" stroke-width="1.8"></rect>
        <path d="M6.5 14.5H5.9A1.9 1.9 0 0 1 4 12.6V5.9A1.9 1.9 0 0 1 5.9 4h6.7A1.9 1.9 0 0 1 14.5 5.9v.6" stroke="currentColor" stroke-width="1.8"></path>
      </svg>
    `,
    system: `
      <svg${classAttr} viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <rect x="4.5" y="5.25" width="15" height="5.5" rx="1.4" fill="currentColor"></rect>
        <rect x="4.5" y="13.25" width="15" height="5.5" rx="1.4" fill="currentColor" opacity="0.78"></rect>
        <circle cx="8" cy="8" r="1" fill="white"></circle>
        <circle cx="8" cy="16" r="1" fill="white"></circle>
        <path d="M11.25 8h4.75M11.25 16h4.75" stroke="white" stroke-width="1.4" stroke-linecap="round"></path>
      </svg>
    `,
    file: `
      <svg${classAttr} viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M7 3.75h6.25l3.75 3.75V19A1.75 1.75 0 0 1 15.25 20.75h-8.5A1.75 1.75 0 0 1 5 19V5.5A1.75 1.75 0 0 1 6.75 3.75H7Z" stroke="currentColor" stroke-width="1.8"></path>
        <path d="M13 3.75V8h4.25" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"></path>
        <path d="M8.25 12h7.5M8.25 15.5h5.25" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"></path>
      </svg>
    `,
    contacts: `
      <svg${classAttr} viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <rect x="5" y="3.75" width="14" height="16.5" rx="2.2" stroke="currentColor" stroke-width="1.8"></rect>
        <circle cx="12" cy="9" r="2.4" fill="currentColor"></circle>
        <path d="M8.5 16.1a3.5 3.5 0 0 1 7 0" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"></path>
        <path d="M16.9 6.5h.85M16.9 10h.85M16.9 13.5h.85" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"></path>
      </svg>
    `,
    jobs: `
      <svg${classAttr} viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <rect x="6" y="4.75" width="12" height="15.5" rx="2.2" stroke="currentColor" stroke-width="1.8"></rect>
        <path d="M9 3.75h6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"></path>
        <path d="M9 9.5h6M9 13h6M9 16.5h4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"></path>
      </svg>
    `,
    trash: `
      <svg${classAttr} viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M5.75 7.25h12.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"></path>
        <path d="M9.25 7.25V5.9a1.15 1.15 0 0 1 1.15-1.15h3.2a1.15 1.15 0 0 1 1.15 1.15v1.35" stroke="currentColor" stroke-width="1.8"></path>
        <path d="M8 9.5v7.25a1.5 1.5 0 0 0 1.5 1.5h5a1.5 1.5 0 0 0 1.5-1.5V9.5" stroke="currentColor" stroke-width="1.8"></path>
        <path d="M10.5 11.25v4.75M13.5 11.25v4.75" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"></path>
      </svg>
    `,
    chevron: `
      <svg${classAttr} viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="m6.75 9.25 5.25 5.5 5.25-5.5" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"></path>
      </svg>
    `,
  };
  return icons[name] || "";
}

function renderDetailAccordion({ title, badge = "", icon = "file", contentHtml = "", collapsed = false } = {}) {
  if (!String(contentHtml || "").trim()) {
    return "";
  }
  return `
    <section class="detail-section detail-accordion" data-collapsed="${collapsed ? "true" : "false"}">
      <div class="detail-section__header detail-accordion__header">
        <div class="detail-accordion__title-group">
          <span class="detail-accordion__icon" aria-hidden="true">${renderSvgIcon(icon, "detail-svg-icon")}</span>
          <h4 class="detail-section__title detail-accordion__title">${escapeHtml(title)}</h4>
          ${badge ? `<span class="detail-accordion__badge">${escapeHtml(badge)}</span>` : ""}
        </div>
        <button class="detail-accordion__toggle" type="button" data-action="toggle-detail-section" aria-expanded="${collapsed ? "false" : "true"}">
          ${renderSvgIcon("chevron", "detail-accordion__chevron")}
        </button>
      </div>
      <div class="detail-section__content"${collapsed ? ' hidden="hidden"' : ""}>
        ${contentHtml}
      </div>
    </section>
  `;
}

function renderEventTimeline(events = [], fallbackItems = []) {
  if (events.length) {
    return `
      <div class="detail-timeline">
        ${events
          .slice(0, 3)
          .map((event) => {
            const eventText = [event.title, event.summary].filter(Boolean).join("，");
            return `
              <article class="detail-timeline__item">
                <span class="detail-timeline__dot" aria-hidden="true"></span>
                <div class="detail-timeline__content">
                  ${
                    hasMeaningfulValue(event.published_at)
                      ? `<span class="detail-timeline__date">${escapeHtml(formatShortDate(event.published_at))}</span>`
                      : ""
                  }
                  <p class="detail-timeline__text detail-copy">${escapeHtml(eventText || "暂无事件描述")}</p>
                </div>
              </article>
            `;
          })
          .join("")}
      </div>
    `;
  }
  if (fallbackItems.length) {
    return `
      <div class="detail-timeline detail-timeline--plain">
        ${fallbackItems
          .slice(0, 3)
          .map(
            (item) => `
              <article class="detail-timeline__item">
                <span class="detail-timeline__dot" aria-hidden="true"></span>
                <div class="detail-timeline__content">
                  <p class="detail-timeline__text detail-copy">${escapeHtml(item)}</p>
                </div>
              </article>
            `,
          )
          .join("")}
      </div>
    `;
  }
  return `<p class="detail-empty">暂无近期重大动态</p>`;
}

function renderDetailModal(payload) {
  const modal = document.getElementById("detail-modal");
  const kicker = document.getElementById("detail-modal-kicker");
  const title = document.getElementById("detail-modal-title");
  const meta = document.getElementById("detail-modal-meta");
  const body = document.getElementById("detail-modal-body");
  if (!modal || !title || !meta || !body || !payload) {
    return;
  }

  const { item } = payload;
  const exportFields = item.result?.export_fields || {};
  const research = item.research || null;
  const profile = item.result?.company_snapshot?.profile || {};
  const profileSources = item.result?.company_snapshot?.profile_sources || [];
  const events = item.result?.company_snapshot?.events || [];
  const nameCalibration = item.result?.company_snapshot?.name_calibration || {};
  const contactSnapshot = item.result?.contact_snapshot || {};
  const contactList = (contactSnapshot.contacts || []).filter((contact) => hasRenderableContact(contact));
  const recruitmentSnapshot = item.result?.recruitment_snapshot || {};
  const recruitings = recruitmentSnapshot.recruitings || [];
  const relatedRecruitings = recruitmentSnapshot.related_recruitings || [];
  const statusText = item.status || "-";
  const companyTitle = item.matched_company_name || item.input_company_name;
  const sortedContacts = sortContactsForPriority(contactList);
  const primaryContact = sortedContacts[0] || null;
  const backupContacts = sortedContacts.slice(1, 3);
  const followupSuggestions = Array.isArray(research?.followup_suggestions)
    ? research.followup_suggestions.filter((entry) => hasMeaningfulValue(entry))
    : [];
  const firstContactScript = research?.first_contact_script || {};
  const wechatAddLine = String(firstContactScript.wechat_add_line || "").trim();
  const adviceContext = research?.raw_response?.advice_context || research?.raw_response?.advice?._local_context || {};
  const adviceSourceDocs = Array.isArray(adviceContext?.documents) ? adviceContext.documents : [];
  const vendorMatches = Array.isArray(adviceContext?.vendor_matches)
    ? adviceContext.vendor_matches.filter(
        (match) =>
          hasMeaningfulValue(match?.vendor_name) ||
          hasMeaningfulValue(match?.vendor_category) ||
          hasMeaningfulValue(match?.client_name) ||
          hasMeaningfulValue(match?.source_url),
      )
    : [];
  const rawKnowledgeReferences =
    Array.isArray(firstContactScript.knowledge_references) && firstContactScript.knowledge_references.length
      ? firstContactScript.knowledge_references
      : adviceSourceDocs;
  const knowledgeReferences = Array.isArray(rawKnowledgeReferences)
    ? rawKnowledgeReferences.filter(
        (doc) => hasMeaningfulValue(doc?.title) || hasMeaningfulValue(doc?.path) || hasMeaningfulValue(doc?.snippet),
      )
    : [];
  const knowledgeSearchNote = String(firstContactScript.knowledge_search_note || adviceContext?.search_note || "").trim();
  const knowledgeSearchStatus = String(
    firstContactScript.knowledge_search_status ||
      adviceContext?.search_status ||
      (knowledgeReferences.length ? "matched" : ""),
  ).trim();
  const summarySections = splitResearchDataSummary(research?.data_status_summary);
  const systemSummaryText = summarySections.systemSummary;
  const companyStatusText = [summarySections.identitySummary, summarySections.completenessSummary, summarySections.generalSummary]
    .filter((entry) => hasMeaningfulValue(entry))
    .join("\n\n");
  const companyStatusKicker = summarySections.identitySummary && summarySections.completenessSummary
    ? "主体核验与信息完整度"
    : summarySections.identitySummary
      ? "主体核验"
      : summarySections.completenessSummary
        ? "信息完整度"
        : "补充说明";
  const summaryDynamicItems = summarySections.dynamicItems;
  const knowledgeStatusHint = knowledgeReferences.length
    ? `知识库：已引用 ${knowledgeReferences.length} 条本地内容`
    : knowledgeSearchNote || (knowledgeSearchStatus === "no_match" ? "知识库：已尝试检索，但未找到合适内容" : "");
  const primaryEntryPoint = String(
    research?.bi_entry_opportunity ||
      profile.bi_entry_opportunity ||
      systemSummaryText ||
      profile.systems_live ||
      exportFields["已上线系统"] ||
      "",
  ).trim();
  const decision = deriveFollowDecision({
    status: statusText,
    research,
    contactList,
    primaryEntryPoint,
    followupSuggestions,
  });
  const researchStatusMeta = getResearchStatusMeta(item, research);
  const primarySuggestion = followupSuggestions[0] || "";
  const nextStepSuggestions = followupSuggestions.slice(1, 3);
  const leadCode = shortenOpaqueId(item.public_id || item.external_company_id || payload.job?.public_id);
  const industryLabel = firstMeaningfulValue(profile.industry_nbs_small, exportFields["客户行业"], exportFields["行业"]);
  const locationLabel = [exportFields["客户省份"], exportFields["城市"]].filter((entry) => hasMeaningfulValue(entry)).join(" · ");
  const heroChips = uniqueItems(
    [
      industryLabel,
      locationLabel,
      `建议：${decision.conclusion}`,
      leadCode ? `线索 ID: ${leadCode}` : "",
    ].filter(Boolean),
  ).slice(0, 4);
  const financeGrowth = firstMeaningfulValue(profile.revenue_growth, exportFields["客户营收增长情况"]);
  const financeStatus = firstMeaningfulValue(profile.is_ipo, profile.is_listed, exportFields["是否IPO"], exportFields["是否上市"]);
  const systemLabel = firstMeaningfulValue(profile.systems_live, exportFields["已上线系统"], systemSummaryText);
  const customerSegments = splitTagText(firstMeaningfulValue(profile.customer_segment, exportFields["客户客群"]));
  const recruitingHighlights = uniqueItems([
    ...splitTagText(exportFields["招聘代表岗位"], { limit: 4 }),
    ...relatedRecruitings.map((jobEntry) => String(jobEntry.title || "").trim()).filter(Boolean),
  ]).slice(0, 3);
  const detailWhyNowItems = uniqueItems(
    [
      profile.hiring_summary
        ? `招聘信号：${profile.hiring_summary}`
        : typeof recruitmentSnapshot.it_related_count === "number"
          ? `在招 IT/数据岗位 ${recruitmentSnapshot.it_related_count} 个`
          : "",
      profile.digital_projects ? `项目动态：${profile.digital_projects}` : "",
      events[0] ? `重大事件：${[events[0].title, events[0].summary].filter(Boolean).join("：")}` : "",
    ].filter(Boolean),
  ).slice(0, 3);
  const timelineFallback = uniqueItems(
    [
      events[0] ? [events[0].title, events[0].summary].filter(Boolean).join("，") : "",
      ...summaryDynamicItems,
      profile.digital_projects || "",
      profile.hiring_summary || "",
      typeof recruitmentSnapshot.recruiting_total === "number" ? `在招职位：${recruitmentSnapshot.recruiting_total} 个` : "",
    ].filter(Boolean),
  ).slice(0, 3);
  const detailRelatedLinks = collectRelatedLinks({ item, research, profileSources, events, contactList, recruitings });
  const detailRiskTags = buildRiskTags({ contactList, research, nameCalibration, status: statusText });
  const detailOfficialFullName = nameCalibration.official_full_name || research?.official_full_name || "";
  const detailEvidenceCount =
    detailRelatedLinks.length +
    profileSources.length +
    (research?.field_results || []).length +
    (research?.competitors || []).length +
    (Object.keys(nameCalibration).length ? 1 : 0) +
    Object.keys(exportFields).length;
  const scriptQuote = String(
    firstMeaningfulValue(wechatAddLine, firstContactScript.opening_line, primarySuggestion, decision.summary),
  ).trim();
  const talkingPoints = uniqueItems([
    ...((Array.isArray(firstContactScript.call_talking_points) ? firstContactScript.call_talking_points : []).filter(Boolean)),
    ...((Array.isArray(firstContactScript.qualification_questions) ? firstContactScript.qualification_questions : []).filter(Boolean)),
    ...nextStepSuggestions,
    ...detailWhyNowItems,
  ]).slice(0, 4);
  const backupSummary = backupContacts
    .map((contact) => {
      const name = contactDisplayName(contact);
      const position = contactDisplayPosition(contact);
      return `
        <span class="detail-mini-chip">
          <strong>${escapeHtml(name)}</strong>
          <span>${escapeHtml(position)}</span>
        </span>
      `;
    })
    .join("");
  const evidenceBlocks = [
    Object.keys(nameCalibration).length
      ? renderEvidenceBlock(
          "名称校准",
          renderKeyValueGrid([
            { label: "输入初始名称", value: nameCalibration.input_name },
            { label: "官方全称", value: nameCalibration.official_full_name },
            { label: "高概率候选名称", value: (nameCalibration.candidates || []).join("；") },
            { label: "可信度", value: nameCalibration.confidence },
          ]),
        )
      : "",
    detailRelatedLinks.length
      ? renderEvidenceBlock(
          `相关链接（${detailRelatedLinks.length}）`,
          `
            <div class="table-wrap detail-table-wrap">
              <table class="records-table detail-raw-table">
                <thead>
                  <tr><th>名称</th><th>类型</th><th>链接</th></tr>
                </thead>
                <tbody>
                  ${detailRelatedLinks
                    .map(
                      (link) => `
                        <tr>
                          <td>${escapeHtml(link.label || "-")}</td>
                          <td>${escapeHtml(link.type || "-")}</td>
                          <td>${renderExternalLink(link.url, link.url || "查看链接")}</td>
                        </tr>
                      `,
                    )
                    .join("")}
                </tbody>
              </table>
            </div>
          `,
        )
      : "",
    profileSources.length
      ? renderEvidenceBlock(
          `画像来源（${profileSources.length}）`,
          `
            <div class="table-wrap detail-table-wrap">
              <table class="records-table detail-raw-table">
                <thead>
                  <tr><th>字段</th><th>值</th><th>证据</th><th>来源</th><th>可信度</th></tr>
                </thead>
                <tbody>
                  ${profileSources
                    .map(
                      (source) => `
                        <tr>
                          <td>${escapeHtml(source.field_name || "-")}</td>
                          <td>${escapeHtml(source.field_value || "-")}</td>
                          <td><div class="detail-copy">${escapeHtml(source.evidence_text || "-")}</div></td>
                          <td>${renderExternalLink(source.source_url, source.source_title || "查看来源")}</td>
                          <td>${escapeHtml(source.confidence || "-")}</td>
                        </tr>
                      `,
                    )
                    .join("")}
                </tbody>
              </table>
            </div>
          `,
        )
      : "",
    (research?.field_results || []).length
      ? renderEvidenceBlock(
          `AI 字段证据（${research.field_results.length}）`,
          `
            <div class="table-wrap detail-table-wrap">
              <table class="records-table detail-raw-table">
                <thead>
                  <tr><th>字段</th><th>值</th><th>证据</th><th>来源</th><th>可信度</th></tr>
                </thead>
                <tbody>
                  ${research.field_results
                    .map(
                      (field) => `
                        <tr>
                          <td>${escapeHtml(field.field_name || "-")}</td>
                          <td>${escapeHtml(field.field_value || "-")}</td>
                          <td><div class="detail-copy">${escapeHtml(field.evidence_text || "-")}</div></td>
                          <td>${renderExternalLink(field.url, field.source || "查看来源")}</td>
                          <td>${escapeHtml(field.confidence || "-")}</td>
                        </tr>
                      `,
                    )
                    .join("")}
                </tbody>
              </table>
            </div>
          `,
        )
      : "",
    (research?.competitors || []).length
      ? renderEvidenceBlock(
          `竞品证据（${research.competitors.length}）`,
          `
            <div class="table-wrap detail-table-wrap">
              <table class="records-table detail-raw-table">
                <thead>
                  <tr><th>竞品</th><th>判断依据</th><th>来源</th><th>可信度</th></tr>
                </thead>
                <tbody>
                  ${research.competitors
                    .map(
                      (competitor) => `
                        <tr>
                          <td>${escapeHtml(competitor.name || "-")}</td>
                          <td><div class="detail-copy">${escapeHtml(competitor.reason || "-")}</div></td>
                          <td>${renderExternalLink(competitor.url, competitor.source || "查看来源")}</td>
                          <td>${escapeHtml(competitor.confidence || "-")}</td>
                        </tr>
                      `,
                    )
                    .join("")}
                </tbody>
              </table>
            </div>
          `,
        )
      : "",
    Object.keys(exportFields).length
      ? renderEvidenceBlock(`完整字段（${Object.keys(exportFields).length}）`, renderExportFields(item.result))
      : "",
  ].filter(Boolean);

  kicker.textContent = `查询详情 · ${statusLabel(statusText)}`;
  title.replaceChildren();
  const detailTitleText = companyTitle || "查询详情";
  const detailCompanyDetailUrl = buildTungeeCompanyDetailUrl(item.external_company_id);
  if (detailCompanyDetailUrl) {
    const titleLink = document.createElement("a");
    titleLink.className = "detail-modal__title-link";
    titleLink.href = detailCompanyDetailUrl;
    titleLink.target = "_blank";
    titleLink.rel = "noopener noreferrer";
    titleLink.textContent = detailTitleText;
    title.append(titleLink);
  } else {
    title.textContent = detailTitleText;
  }
  const detailMetaParts = [];
  if (detailOfficialFullName && detailOfficialFullName !== companyTitle) {
    detailMetaParts.push(`官方全称：${detailOfficialFullName}`);
  }
  if (detailRiskTags.length) {
    detailMetaParts.push(`提醒：${detailRiskTags.join(" / ")}`);
  }
  meta.textContent = detailMetaParts.join(" · ");
  meta.hidden = detailMetaParts.length === 0;
  modal.dataset.mode = "company";

  body.innerHTML = `
    <div class="detail-view">
      ${
        item.error_message
          ? `<div class="detail-alert">失败原因：${escapeHtml(item.error_message)}</div>`
          : ""
      }
      <section class="detail-view__hero">
        <div class="detail-view__identity">
          <div class="detail-view__logo" aria-hidden="true">
            ${renderSvgIcon("company", "detail-svg-icon detail-svg-icon--company")}
          </div>
          <div class="detail-view__identity-copy">
            <h1 class="detail-view__title">${escapeHtml(detailTitleText)}</h1>
            ${
              heroChips.length
                ? `<div class="detail-view__meta-row">${heroChips
                    .map((chip) => `<span class="detail-view__meta-chip">${escapeHtml(chip)}</span>`)
                    .join("")}</div>`
                : ""
            }
            ${
              hasMeaningfulValue(primarySuggestion || decision.summary)
                ? `<p class="detail-view__summary">${escapeHtml(primarySuggestion || decision.summary)}</p>`
                : ""
            }
          </div>
        </div>
      </section>

      <div class="detail-view__layout">
        <div class="detail-view__main">
          <section class="detail-board detail-board--wide">
            <div class="detail-board__heading">
              <h2>业务画像与商业模式</h2>
            </div>
            <div class="detail-board__grid detail-board__grid--business">
              <article class="detail-board__metric">
                <span class="detail-board__label">客户产品/服务</span>
                <p class="detail-board__value detail-copy">${escapeHtml(firstMeaningfulValue(profile.product_services, exportFields["客户产品/服务"]) || "待补充")}</p>
              </article>
              <article class="detail-board__metric">
                <span class="detail-board__label">商业模式</span>
                <p class="detail-board__value detail-copy">${escapeHtml(firstMeaningfulValue(profile.business_model, exportFields["商业模式"]) || "待补充")}</p>
              </article>
              <article class="detail-board__metric detail-board__metric--full">
                <span class="detail-board__label">核心客群</span>
                ${
                  customerSegments.length
                    ? `<div class="detail-mini-chip-row">${customerSegments.map((segment) => `<span class="detail-segment-chip">${escapeHtml(segment)}</span>`).join("")}</div>`
                    : `<p class="detail-empty">暂无核心客群信息</p>`
                }
              </article>
            </div>
            ${
              companyStatusText
                ? `
              <div class="detail-board__footnote">
                <span class="detail-board__footnote-kicker">${escapeHtml(companyStatusKicker)}</span>
                <p class="detail-copy">${escapeHtml(companyStatusText)}</p>
              </div>
            `
                : ""
            }
            <div class="detail-board__footnote">
              <span class="detail-board__footnote-kicker">AI详研</span>
              <p>${escapeHtml([researchStatusMeta.label, primaryEntryPoint || systemSummaryText || "暂无主切口"].filter(Boolean).join(" · "))}</p>
            </div>
          </section>

          <div class="detail-view__double">
            <section class="detail-board detail-board--finance">
              <div class="detail-board__heading">
                <h2>财务与资本状况</h2>
              </div>
              <div class="detail-finance">
                <div class="detail-finance__row">
                  <span>营收规模</span>
                  <strong>${escapeHtml(firstMeaningfulValue(profile.revenue_scale, exportFields["客户收入规模"]) || "待补充")}</strong>
                </div>
                <div class="detail-finance__meter" aria-hidden="true">
                  <span style="width: ${deriveRevenueMeterWidth(firstMeaningfulValue(profile.revenue_scale, exportFields["客户收入规模"]))}%"></span>
                </div>
                <div class="detail-finance__growth">
                  <span>营收增长率</span>
                  <strong class="${financeGrowth && String(financeGrowth).trim().startsWith("-") ? "" : "is-positive"}">${escapeHtml(financeGrowth || "待补充")}</strong>
                </div>
                <div class="detail-finance__row detail-finance__row--foot">
                  <span>上市/IPO状态</span>
                  <strong>${escapeHtml(financeStatus || "待补充")}</strong>
                </div>
              </div>
            </section>

            <section class="detail-board detail-board--ability">
              <div class="detail-board__heading">
                <h2>数字化与IT能力</h2>
              </div>
              <div class="detail-ability-list">
                <article class="detail-ability-item">
                  <span class="detail-ability-item__icon" aria-hidden="true">${renderSvgIcon("system", "detail-svg-icon")}</span>
                  <div class="detail-ability-item__copy">
                    <span class="detail-board__label">系统现状</span>
                    <p class="detail-board__value detail-copy">${escapeHtml(systemLabel || "待补充")}</p>
                    ${
                      vendorMatches.length
                        ? `
                          <div class="detail-ability-item__extra">
                            <span class="detail-board__label">本地命中来源</span>
                            ${renderVendorMatchList(vendorMatches)}
                          </div>
                        `
                        : ""
                    }
                  </div>
                </article>
                <article class="detail-ability-item">
                  <span class="detail-ability-item__icon" aria-hidden="true">${renderSvgIcon("search", "detail-svg-icon")}</span>
                  <div class="detail-ability-item__copy">
                    <span class="detail-board__label">相关招聘信息</span>
                    ${
                      recruitingHighlights.length
                        ? `<div class="detail-link-row">${recruitingHighlights.map((titleItem) => `<span class="detail-link-chip">${escapeHtml(titleItem)}</span>`).join("")}</div>`
                        : `<p class="detail-empty">暂无重点招聘岗位</p>`
                    }
                  </div>
                </article>
              </div>
              ${
                hasMeaningfulValue(primaryEntryPoint) || timelineFallback.length
                  ? `
                <div class="detail-board__footnote">
                  <span class="detail-board__footnote-kicker">推荐切口</span>
                  <p>${escapeHtml(primaryEntryPoint || timelineFallback[0] || "待补充")}</p>
                </div>
              `
                  : ""
              }
            </section>
          </div>

          <section class="detail-board detail-board--timeline">
            <div class="detail-board__heading">
              <h2>近期重大动态</h2>
            </div>
            ${renderEventTimeline(events, timelineFallback)}
          </section>
        </div>

        <aside class="detail-view__side">
          <section class="detail-side-card detail-side-card--contact">
            <div class="detail-side-card__header detail-side-card__header--filled">
              <h2>${renderSvgIcon("users", "detail-svg-icon")}核心联系人</h2>
              <span class="detail-side-card__action" aria-hidden="true">${renderSvgIcon("search", "detail-svg-icon")}</span>
            </div>
            <div class="detail-side-card__body">
              ${
                primaryContact
                  ? `
                <article class="detail-contact-highlight">
                  <div class="detail-contact-highlight__avatar">${escapeHtml(contactDisplayName(primaryContact).slice(0, 1) || "?")}</div>
                  <div class="detail-contact-highlight__copy">
                    <h3>${escapeHtml(contactDisplayName(primaryContact))}</h3>
                    <p>${escapeHtml(contactDisplayPosition(primaryContact))}</p>
                    <span class="detail-contact-highlight__value">${escapeHtml(contactDisplayValue(primaryContact) || "待补充")}</span>
                    ${
                      hasMeaningfulValue(primaryContact.source)
                        ? `<span class="detail-contact-highlight__source">来源：${escapeHtml(primaryContact.source)}</span>`
                        : ""
                    }
                  </div>
                  <div class="detail-contact-highlight__actions" aria-hidden="true">
                    <span>${renderSvgIcon("phone", "detail-svg-icon")}</span>
                    <span>${renderSvgIcon("chat", "detail-svg-icon")}</span>
                  </div>
                </article>
                ${
                  backupSummary
                    ? `
                  <div class="detail-contact-highlight__backups">
                    <span class="detail-board__label">备选联系人</span>
                    <div class="detail-mini-chip-row">${backupSummary}</div>
                  </div>
                `
                    : ""
                }
              `
                  : `<p class="detail-empty">暂无有效联系人，建议先补齐触达对象后再推进。</p>`
              }
            </div>
          </section>

          <section class="detail-side-card detail-side-card--script">
            <div class="detail-board__heading detail-board__heading--accent">
              <h2>话术建议</h2>
            </div>
            <div class="detail-script-block">
              <div class="detail-script-block__head">
                <span class="detail-board__label">加微信话术建议</span>
                ${
                  scriptQuote
                    ? `
                  <button class="detail-copy-btn" type="button" data-action="copy-detail-text" data-copy-text="${escapeHtml(scriptQuote)}">
                    ${renderSvgIcon("copy", "detail-svg-icon")}
                    <span>复制</span>
                  </button>
                `
                    : ""
                }
              </div>
              <div class="detail-script-quote">
                <p class="detail-copy">${escapeHtml(scriptQuote || "暂无可复制话术，建议先围绕近期动态与招聘信号切入。")}</p>
              </div>
            </div>
            <div class="detail-script-block">
              <span class="detail-board__label">电话沟通要点（详细）</span>
              <div class="detail-script-points">
                ${renderList(talkingPoints, "暂无详细沟通要点")}
              </div>
            </div>
            ${
              hasMeaningfulValue(firstContactScript.why_now) ||
              hasMeaningfulValue(firstContactScript.opening_line) ||
              hasMeaningfulValue(wechatAddLine) ||
              (Array.isArray(firstContactScript.call_talking_points) && firstContactScript.call_talking_points.length) ||
              (Array.isArray(firstContactScript.qualification_questions) && firstContactScript.qualification_questions.length) ||
              hasMeaningfulValue(firstContactScript.closing_transition)
                ? `
              <div class="detail-script-block detail-script-block--full">
                <div class="detail-script-block__head">
                  <span class="detail-board__label">首次触达话术（完整内容）</span>
                </div>
                <div class="detail-script-full">
                  ${
                    hasMeaningfulValue(firstContactScript.why_now)
                      ? `
                    <div class="contact-script-card__full-block">
                      <span class="contact-script-card__label">为何现在联系</span>
                      <p class="contact-script-card__value">${escapeHtml(firstContactScript.why_now)}</p>
                    </div>
                  `
                      : ""
                  }
                  ${
                    hasMeaningfulValue(firstContactScript.opening_line)
                      ? `
                    <div class="contact-script-card__full-block">
                      <span class="contact-script-card__label">开场白</span>
                      <p class="contact-script-card__value">${escapeHtml(firstContactScript.opening_line)}</p>
                    </div>
                  `
                      : ""
                  }
                  ${
                    hasMeaningfulValue(wechatAddLine)
                      ? `
                    <div class="contact-script-card__full-block">
                      <span class="contact-script-card__label">加微信话术</span>
                      <p class="contact-script-card__value">${escapeHtml(wechatAddLine)}</p>
                    </div>
                  `
                      : ""
                  }
                  ${
                    Array.isArray(firstContactScript.call_talking_points) && firstContactScript.call_talking_points.length
                      ? `
                    <div class="contact-script-card__full-block">
                      <span class="contact-script-card__label">完整电话重点</span>
                      ${renderList(firstContactScript.call_talking_points, "暂无建议")}
                    </div>
                  `
                      : ""
                  }
                  ${
                    Array.isArray(firstContactScript.qualification_questions) && firstContactScript.qualification_questions.length
                      ? `
                    <div class="contact-script-card__full-block">
                      <span class="contact-script-card__label">完整追问清单</span>
                      ${renderList(firstContactScript.qualification_questions, "暂无建议")}
                    </div>
                  `
                      : ""
                  }
                  ${
                    hasMeaningfulValue(firstContactScript.closing_transition)
                      ? `
                    <div class="contact-script-card__full-block">
                      <span class="contact-script-card__label">收尾推进</span>
                      <p class="contact-script-card__value">${escapeHtml(firstContactScript.closing_transition)}</p>
                    </div>
                  `
                      : ""
                  }
                </div>
              </div>
            `
                : ""
            }
            ${
              hasMeaningfulValue(knowledgeStatusHint)
                ? `<p class="detail-script-note">${escapeHtml(knowledgeStatusHint)}</p>`
                : ""
            }
            ${
              knowledgeReferences.length || hasMeaningfulValue(knowledgeSearchNote)
                ? `
              <div class="detail-script-block detail-script-block--sources">
                <div class="detail-script-block__head">
                  <span class="detail-board__label">知识库引用原文</span>
                  <span class="detail-script-source-meta">${escapeHtml(knowledgeReferences.length ? `已引用 ${knowledgeReferences.length} 条` : "已尝试检索")}</span>
                </div>
                ${
                  hasMeaningfulValue(knowledgeSearchNote)
                    ? `<p class="detail-script-search-note">${escapeHtml(knowledgeSearchNote)}</p>`
                    : ""
                }
                ${
                  knowledgeReferences.length
                    ? `
                  <div class="contact-script-source-list">
                    ${knowledgeReferences
                      .map(
                        (doc) => `
                          <article class="contact-script-source">
                            <div class="contact-script-source__header">
                              <div class="contact-script-source__header-main">
                                <span class="pill pill--soft">${escapeHtml(doc.group || "doc")}</span>
                                <span class="contact-script-source__title">${escapeHtml(doc.title || doc.path || "未命名文档")}</span>
                              </div>
                              ${
                                doc.path
                                  ? `
                                <button
                                  class="contact-script-source__expand-btn"
                                  type="button"
                                  data-action="open-knowledge-document"
                                  data-doc-title="${escapeHtml(doc.title || doc.path || "未命名文档")}"
                                  data-doc-path="${escapeHtml(doc.path || "")}"
                                  data-doc-chunk-id="${escapeHtml(doc.chunk_id || "")}"
                                >查看全文</button>
                              `
                                  : ""
                              }
                            </div>
                            ${
                              doc.path
                                ? `<p class="contact-script-source__path">${escapeHtml(doc.path)}</p>`
                                : ""
                            }
                            <p class="contact-script-source__snippet">${escapeHtml(doc.snippet || "")}</p>
                          </article>
                        `,
                      )
                      .join("")}
                  </div>
                `
                    : ""
                }
              </div>
            `
                : ""
            }
          </section>
        </aside>
      </div>

      <div class="detail-data-divider">
        <span>全量底层数据资产</span>
      </div>

      <div class="detail-accordion-stack">
        ${
          detailEvidenceCount
            ? renderDetailAccordion({
                title: "证据与原始资料",
                badge: `${detailEvidenceCount} 份数据凭证`,
                icon: "file",
                collapsed: true,
                contentHtml: `<div class="detail-evidence-stack">${evidenceBlocks.join("")}</div>`,
              })
            : ""
        }
        ${
          contactList.length
            ? renderDetailAccordion({
                title: "联系人全表（完整数据）",
                badge: `共 ${contactList.length} 位联系人`,
                icon: "contacts",
                collapsed: false,
                contentHtml: `
                  <div class="table-wrap detail-table-wrap">
                    <table class="records-table detail-raw-table">
                      <thead>
                        <tr>
                          <th>姓名</th>
                          <th>职位</th>
                          <th>联系方式</th>
                          <th>更新时间</th>
                          <th>数据来源</th>
                        </tr>
                      </thead>
                      <tbody>
                        ${sortedContacts
                          .map(
                            (contact) => `
                              <tr>
                                <td>${escapeHtml(contactDisplayName(contact))}</td>
                                <td>${escapeHtml(contactDisplayPosition(contact))}</td>
                                <td>${escapeHtml(contactDisplayValue(contact) || "-")}</td>
                                <td>${escapeHtml(contactUpdatedAt(contact) || "-")}</td>
                                <td>${hasMeaningfulValue(contact.source) ? escapeHtml(contact.source) : renderExternalLink(contact.source_url, "查看来源")}</td>
                              </tr>
                            `,
                          )
                          .join("")}
                      </tbody>
                    </table>
                  </div>
                `,
              })
            : ""
        }
        ${
          recruitings.length
            ? renderDetailAccordion({
                title: "招聘原文（需求深度挖掘）",
                badge: `${recruitings.length} 个核心岗位`,
                icon: "jobs",
                collapsed: true,
                contentHtml: `
                  <p class="muted">已抓取 ${recruitmentSnapshot.recruiting_fetched_count || recruitings.length} 条 / 总计 ${
                    recruitmentSnapshot.recruiting_total || recruitings.length
                  } 条。${recruitmentSnapshot.keyword ? `关键词：${escapeHtml(recruitmentSnapshot.keyword)}` : "关键词：全部"}</p>
                  <div class="recruitment-filter" data-role="recruitment-filter">
                    <div class="records-toolbar records-toolbar--detail">
                      <input type="text" placeholder="搜索岗位名、城市、学历/经验或 JD 关键词" data-action="filter-recruitings" />
                      <span class="pill pill--soft" data-role="recruiting-filter-count">共 ${recruitings.length} 个岗位</span>
                    </div>
                    <p class="detail-note" data-role="recruiting-filter-empty" hidden>没有匹配的岗位，试试更短的关键词。</p>
                    <div class="table-wrap detail-table-wrap">
                      <table class="records-table detail-raw-table">
                        <thead>
                          <tr>
                            <th>岗位</th>
                            <th>城市</th>
                            <th>薪资</th>
                            <th>学历/经验</th>
                            <th>发布时间</th>
                            <th>来源</th>
                            <th>JD</th>
                          </tr>
                        </thead>
                        <tbody>
                          ${recruitings
                            .map(
                              (jobEntry) => `
                                <tr data-role="recruiting-row" data-search-text="${escapeHtml(buildRecruitingSearchText(jobEntry))}">
                                  <td>${escapeHtml(jobEntry.title || "-")}</td>
                                  <td>${escapeHtml(jobEntry.city || jobEntry.district || "-")}</td>
                                  <td>${escapeHtml(
                                    jobEntry.salary_min || jobEntry.salary_max
                                      ? `${jobEntry.salary_min || "-"}-${jobEntry.salary_max || "-"} ${jobEntry.salary_currency || ""}`.trim()
                                      : "-",
                                  )}</td>
                                  <td>${escapeHtml(
                                    [jobEntry.education, jobEntry.seniority_min ? `${jobEntry.seniority_min}${jobEntry.seniority_max ? `-${jobEntry.seniority_max}` : "+"}年` : ""]
                                      .filter(Boolean)
                                      .join(" / ") || "-",
                                  )}</td>
                                  <td>${escapeHtml(jobEntry.published_at || "-")}</td>
                                  <td>${renderExternalLink(jobEntry.source_url, jobEntry.source || "查看原文")}</td>
                                  <td><div class="detail-copy">${escapeHtml(jobEntry.desc || "-")}</div></td>
                                </tr>
                              `,
                            )
                            .join("")}
                        </tbody>
                      </table>
                    </div>
                  </div>
                `,
              })
            : ""
        }
      </div>
    </div>
  `;

  bindRecruitingSearch(body);
  modal.hidden = false;
  document.body.style.overflow = "hidden";
  modal.querySelector(".detail-modal__dialog")?.scrollTo({ top: 0 });
  return;
  const decisionSignals = uniqueItems(
    [
      research?.bi_entry_opportunity || profile.bi_entry_opportunity
        ? `BI 切入机会：${research?.bi_entry_opportunity || profile.bi_entry_opportunity}`
        : "",
      research?.data_status_summary || profile.data_status
        ? `数据现状：${research?.data_status_summary || profile.data_status}`
        : "",
      profile.digital_projects ? `项目动态：${profile.digital_projects}` : "",
      profile.hiring_summary
        ? `招聘信号：${profile.hiring_summary}`
        : typeof recruitmentSnapshot.it_related_count === "number"
          ? `IT/数据相关岗位：${recruitmentSnapshot.it_related_count} 个`
          : "",
      events[0] ? `重大事件：${[events[0].title, events[0].summary].filter(Boolean).join("：")}` : "",
    ].filter(Boolean),
  ).slice(0, 4);
  const whyNowAdviceItems = uniqueItems(
    [
      profile.hiring_summary
        ? `招聘信号：${profile.hiring_summary}`
        : typeof recruitmentSnapshot.it_related_count === "number"
          ? `在招 IT/数据岗位 ${recruitmentSnapshot.it_related_count} 个`
          : "",
      profile.digital_projects ? `项目动态：${profile.digital_projects}` : "",
      events[0] ? `重大事件：${[events[0].title, events[0].summary].filter(Boolean).join("：")}` : "",
    ].filter(Boolean),
  ).slice(0, 3);
  const dynamicSummary = uniqueItems(
    [
      events[0] ? `近期事件：${events[0].title || events[0].summary}` : "",
      typeof recruitmentSnapshot.recruiting_total === "number" ? `在招职位：${recruitmentSnapshot.recruiting_total} 个` : "",
      (research?.competitors || []).length
        ? `主要竞品：${
            (research?.competitors || [])
              .map((entry) => entry.name)
              .filter(Boolean)
              .join("、")
          }`
        : "",
    ].filter(Boolean),
  ).slice(0, 3);
  const riskTags = buildRiskTags({ contactList, research, nameCalibration, status: statusText });
  const summaryChips = uniqueItems(
    [
      profile.industry_nbs_small || exportFields["客户行业"] || exportFields["行业"] || "",
      exportFields["城市"] || "",
      exportFields["规模"] || "",
      profile.is_listed ? `上市状态：${profile.is_listed}` : "",
    ].filter(Boolean),
  ).slice(0, 4);
  const relatedLinks = collectRelatedLinks({ item, research, profileSources, events, contactList, recruitings });
  const officialFullName = nameCalibration.official_full_name || research?.official_full_name || "";
  const metaParts = [];
  if (officialFullName && officialFullName !== companyTitle) {
    metaParts.push(`官方全称：${officialFullName}`);
  }
  const evidenceCount =
    relatedLinks.length +
    profileSources.length +
    (research?.field_results || []).length +
    (research?.competitors || []).length +
    (Object.keys(nameCalibration).length ? 1 : 0);
  const backgroundProfileItems = [
    { label: "客户行业", value: profile.industry_nbs_small || exportFields["客户行业"] || exportFields["行业"] },
    { label: "产品/服务", value: profile.product_services },
    { label: "商业模式", value: profile.business_model },
    { label: "客户客群", value: profile.customer_segment },
    { label: "是否上市", value: profile.is_listed },
    { label: "是否IPO", value: profile.is_ipo },
    { label: "收入规模", value: profile.revenue_scale },
    { label: "利润规模", value: profile.profit_scale },
    { label: "营收增长", value: profile.revenue_growth },
  ].filter((entry) => hasMeaningfulValue(entry.value));
  const showContactSection = sortedContacts.length > 0;
  const hasContactScript =
    hasMeaningfulValue(firstContactScript.why_now) ||
    hasMeaningfulValue(firstContactScript.opening_line) ||
    (Array.isArray(firstContactScript.call_talking_points) && firstContactScript.call_talking_points.length > 0) ||
    (Array.isArray(firstContactScript.qualification_questions) && firstContactScript.qualification_questions.length > 0) ||
    hasMeaningfulValue(firstContactScript.closing_transition);
  const showOutreachSection =
    hasMeaningfulValue(primaryEntryPoint) ||
    whyNowAdviceItems.length > 0 ||
    followupSuggestions.length > 0 ||
    hasContactScript ||
    hasMeaningfulValue(wechatAddLine);
  const showBackgroundSection =
    backgroundProfileItems.length > 0 ||
    dynamicSummary.length > 0 ||
    hasMeaningfulValue(profile.systems_live) ||
    hasMeaningfulValue(exportFields["招聘代表岗位"]);
  const heroStatCards = [
    renderStatCard("AI详研", researchStatusMeta.label, researchStatusMeta.helper),
    renderStatCard(
      "优先联系人",
      primaryContact ? (contactDisplayValue(primaryContact) || "待补充") : "待补充",
      primaryContact
        ? [contactDisplayName(primaryContact), contactDisplayPosition(primaryContact)].filter(Boolean).join(" / ")
        : "暂无有效联系方式",
    ),
    renderStatCard(
      "在招职位",
      recruitmentSnapshot.recruiting_total ?? "-",
      typeof recruitmentSnapshot.it_related_count === "number" ? `IT/数据相关岗位 ${recruitmentSnapshot.it_related_count} 个` : "",
    ),
    renderStatCard(
      "近期动态",
      events[0]?.title || "待补充",
      events[0]?.published_at ? formatDateTime(events[0].published_at) : "",
    ),
  ];
  const outreachActionItems = nextStepSuggestions.length ? nextStepSuggestions : primarySuggestion ? [primarySuggestion] : [];
  const outreachOverviewChips = uniqueItems(
    [
      hasMeaningfulValue(primaryEntryPoint) ? "已识别主切入口" : "",
      primarySuggestion ? "含一句话触达建议" : "",
      hasMeaningfulValue(wechatAddLine) ? "含加微信话术" : "",
      nextStepSuggestions.length ? `下一步动作 ${nextStepSuggestions.length} 条` : "",
      whyNowAdviceItems.length ? `触发信号 ${whyNowAdviceItems.length} 条` : "",
      hasContactScript ? "已生成首次触达话术" : "",
    ].filter(Boolean),
  ).slice(0, 4);
  const outreachHeroTitle = hasMeaningfulValue(primaryEntryPoint)
    ? "先围绕这条主线建立对话"
    : primarySuggestion
      ? "先用这条建议启动触达"
      : hasMeaningfulValue(wechatAddLine)
        ? "先用这句微信话术破冰"
      : "先围绕当前变化试探需求";
  const outreachHeroFallback = !hasMeaningfulValue(primaryEntryPoint) && !primarySuggestion && !hasMeaningfulValue(wechatAddLine)
    ? "当前暂无单一主切口，可先结合近期项目、招聘或重大事件变化，确认对方是否处在数据建设或经营分析推进阶段。"
    : "";
  const outreachSideCards = [
    outreachActionItems.length
      ? `
        <article class="detail-panel outreach-panel">
          <div class="outreach-panel__header">
            <h5 class="detail-panel__title">下一步动作</h5>
            <p class="outreach-panel__hint">建议按顺序推进，让触达更像一次确认而不是泛聊。</p>
          </div>
          ${renderStepList(
            outreachActionItems,
            "暂无明确建议，可先围绕主切入口确认当前项目状态。",
            { fallbackLabel: nextStepSuggestions.length ? "下一步动作" : "触达建议" },
          )}
        </article>
      `
      : "",
    whyNowAdviceItems.length
      ? `
        <article class="detail-panel outreach-panel">
          <div class="outreach-panel__header">
            <h5 class="detail-panel__title">为什么现在联系</h5>
            <p class="outreach-panel__hint">只保留当前最能支撑触达时机的变化信号。</p>
          </div>
          ${renderSignalList(whyNowAdviceItems, "暂无足够的触发信号", { fallbackLabel: "联系信号" })}
        </article>
      `
      : "",
  ].filter(Boolean).join("");
  const outreachPlaybook =
    hasMeaningfulValue(primaryEntryPoint) ||
    primarySuggestion ||
    hasMeaningfulValue(wechatAddLine) ||
    outreachActionItems.length ||
    whyNowAdviceItems.length
      ? `
        <div class="outreach-playbook${outreachSideCards ? "" : " outreach-playbook--solo"}">
          <article class="outreach-hero-card">
            <div class="outreach-hero-card__header">
              <div class="outreach-hero-card__heading">
                <span class="outreach-kicker">主切口</span>
                <h5 class="outreach-hero-card__title">${outreachHeroTitle}</h5>
              </div>
              ${renderChipGroup(outreachOverviewChips, "info")}
            </div>
            ${
              hasMeaningfulValue(primaryEntryPoint) || outreachHeroFallback
                ? `
              <div class="outreach-hero-card__entry">
                <p class="outreach-hero-card__entry-text detail-copy">${escapeHtml(primaryEntryPoint || outreachHeroFallback)}</p>
              </div>
            `
                : ""
            }
            ${
              primarySuggestion
                ? `
              <div class="outreach-hero-card__message">
                <span class="outreach-block__label">一句话触达建议</span>
                <p class="outreach-block__text detail-copy">${escapeHtml(primarySuggestion)}</p>
              </div>
            `
                : ""
            }
            ${
              hasMeaningfulValue(wechatAddLine)
                ? `
              <div class="outreach-hero-card__microcopy">
                <div class="outreach-hero-card__microcopy-header">
                  <span class="outreach-block__label">加微信话术</span>
                  <span class="outreach-hero-card__microcopy-meta">25 字内</span>
                </div>
                <p class="outreach-block__text detail-copy">${escapeHtml(wechatAddLine)}</p>
              </div>
            `
                : ""
            }
          </article>
          ${outreachSideCards ? `<div class="outreach-playbook__side">${outreachSideCards}</div>` : ""}
        </div>
      `
      : "";
  const contactScriptCard = hasContactScript
    ? `
      <article class="detail-panel detail-panel--accent contact-script-card">
        <div class="contact-script-card__header">
          <div>
            <h5 class="detail-panel__title">首次触达话术</h5>
            <p class="detail-note">左侧先看摘要，再按需展开完整话术与依据。</p>
            ${
              hasMeaningfulValue(knowledgeStatusHint)
                ? `<p class="detail-note">${escapeHtml(knowledgeStatusHint)}</p>`
                : ""
            }
          </div>
          <button class="ghost-btn" type="button" data-action="toggle-contact-script" aria-expanded="false">展开完整话术</button>
        </div>
        <div class="contact-script-card__layout">
          <div class="contact-script-card__summary-column">
            ${
              hasMeaningfulValue(firstContactScript.why_now)
                ? `
              <div class="contact-script-card__item">
                <span class="contact-script-card__label">为何现在联系</span>
                <div class="contact-script-card__scroll">
                  <p class="contact-script-card__value">${escapeHtml(firstContactScript.why_now)}</p>
                </div>
              </div>
            `
                : ""
            }
            ${
              hasMeaningfulValue(firstContactScript.opening_line)
                ? `
              <div class="contact-script-card__item">
                <span class="contact-script-card__label">开场白</span>
                <div class="contact-script-card__scroll">
                  <p class="contact-script-card__value">${escapeHtml(firstContactScript.opening_line)}</p>
                </div>
              </div>
            `
                : ""
            }
            ${
              Array.isArray(firstContactScript.call_talking_points) && firstContactScript.call_talking_points.length
                ? `
              <div class="contact-script-card__item">
                <span class="contact-script-card__label">首通电话聊什么</span>
                ${renderList(firstContactScript.call_talking_points.slice(0, 2), "暂无建议")}
              </div>
            `
                : ""
            }
            ${
              Array.isArray(firstContactScript.qualification_questions) && firstContactScript.qualification_questions.length
                ? `
              <div class="contact-script-card__item">
                <span class="contact-script-card__label">建议追问</span>
                ${renderList(firstContactScript.qualification_questions.slice(0, 2), "暂无建议")}
              </div>
            `
                : ""
            }
          </div>
          <div class="contact-script-card__expanded-column" hidden data-expanded="false">
            <div class="contact-script-card__expanded">
          ${
            Array.isArray(firstContactScript.call_talking_points) && firstContactScript.call_talking_points.length
              ? `
            <div class="contact-script-card__full-block">
              <span class="contact-script-card__label">完整电话重点</span>
              ${renderList(firstContactScript.call_talking_points, "暂无建议")}
            </div>
          `
              : ""
          }
          ${
            Array.isArray(firstContactScript.qualification_questions) && firstContactScript.qualification_questions.length
              ? `
            <div class="contact-script-card__full-block">
              <span class="contact-script-card__label">完整追问清单</span>
              ${renderList(firstContactScript.qualification_questions, "暂无建议")}
            </div>
          `
              : ""
          }
          ${
            hasMeaningfulValue(firstContactScript.closing_transition)
              ? `
            <div class="contact-script-card__full-block">
              <span class="contact-script-card__label">收尾推进</span>
              <p class="contact-script-card__value">${escapeHtml(firstContactScript.closing_transition)}</p>
            </div>
          `
              : ""
          }
          ${
            knowledgeReferences.length || hasMeaningfulValue(knowledgeSearchNote)
              ? `
            <div class="contact-script-card__full-block">
              <div class="contact-script-card__sources-header">
                <span class="contact-script-card__label">知识库依据</span>
                <span class="detail-note">${escapeHtml(knowledgeReferences.length ? `已引用 ${knowledgeReferences.length} 条` : "已尝试检索")}</span>
              </div>
              ${
                hasMeaningfulValue(knowledgeSearchNote)
                  ? `<p class="contact-script-card__value">${escapeHtml(knowledgeSearchNote)}</p>`
                  : ""
              }
              ${
                knowledgeReferences.length
                  ? `
                <div class="contact-script-source-list">
                  ${knowledgeReferences
                    .map(
                      (doc) => `
                        <article class="contact-script-source">
                          <div class="contact-script-source__header">
                            <span class="pill pill--soft">${escapeHtml(doc.group || "doc")}</span>
                            <span class="contact-script-source__title">${escapeHtml(doc.title || doc.path || "未命名文档")}</span>
                          </div>
                          ${
                            doc.path
                              ? `<p class="contact-script-source__path">${escapeHtml(doc.path)}</p>`
                              : ""
                          }
                          <p class="contact-script-source__snippet">${escapeHtml(doc.snippet || "")}</p>
                        </article>
                      `,
                    )
                    .join("")}
                </div>
              `
                  : ""
              }
            </div>
          `
              : ""
          }
            </div>
          </div>
        </div>
      </article>
    `
    : "";
  const backgroundCards = [
    backgroundProfileItems.length
      ? `
        <article class="detail-panel">
          <h5 class="detail-panel__title">客户背景</h5>
          ${renderKeyValueGrid(backgroundProfileItems, "暂无客户背景信息")}
        </article>
      `
      : "",
    dynamicSummary.length || hasMeaningfulValue(profile.systems_live) || hasMeaningfulValue(exportFields["招聘代表岗位"])
      ? `
        <article class="detail-panel">
          <h5 class="detail-panel__title">动态摘要</h5>
          ${renderList(dynamicSummary, "暂无动态摘要")}
          ${
            hasMeaningfulValue(profile.systems_live) || hasMeaningfulValue(exportFields["招聘代表岗位"])
              ? `
            <div class="detail-note" style="margin-top: 12px;">
              ${hasMeaningfulValue(profile.systems_live) ? `已上线系统：${escapeHtml(profile.systems_live)}` : ""}
              ${
                hasMeaningfulValue(exportFields["招聘代表岗位"])
                  ? `${hasMeaningfulValue(profile.systems_live) ? " · " : ""}招聘代表岗位：${escapeHtml(exportFields["招聘代表岗位"])}`
                  : ""
              }
            </div>
          `
              : ""
          }
        </article>
      `
      : "",
  ].filter(Boolean);

  kicker.textContent = `查询详情 · ${statusLabel(statusText)}`;
  title.replaceChildren();
  const titleText = companyTitle || "查询详情";
  const companyDetailUrl = buildTungeeCompanyDetailUrl(item.external_company_id);
  if (companyDetailUrl) {
    const titleLink = document.createElement("a");
    titleLink.className = "detail-modal__title-link";
    titleLink.href = companyDetailUrl;
    titleLink.target = "_blank";
    titleLink.rel = "noopener noreferrer";
    titleLink.textContent = titleText;
    title.append(titleLink);
  } else {
    title.textContent = titleText;
  }
  meta.textContent = metaParts.join(" · ");
  meta.hidden = metaParts.length === 0;

  body.innerHTML = `
    ${
      item.error_message
        ? `<div class="detail-alert">失败原因：${escapeHtml(item.error_message)}</div>`
        : ""
    }
    <section class="detail-hero">
      <div class="detail-hero__header">
        <div class="detail-hero__title-wrap">
          <div class="detail-badge-row">
            ${renderStatusPill(statusText, { translated: true })}
            <span class="detail-badge detail-badge--${escapeHtml(decision.tone)}">建议跟进：${escapeHtml(decision.label)}</span>
            <span class="detail-badge detail-badge--signal">${escapeHtml(decision.conclusion)}</span>
          </div>
          <p class="detail-hero__summary">${escapeHtml(decision.summary)}</p>
        </div>
      </div>
      ${renderChipGroup(summaryChips)}
      ${renderChipGroup(riskTags, "risk")}
      <div class="detail-stats-grid">
        ${heroStatCards.join("")}
      </div>
    </section>
    <section class="detail-section detail-section--main">
      <div class="detail-section__header">
        <div>
          <h4 class="detail-section__title">跟进判断</h4>
          <p class="detail-section__subtitle">先看 AI 详研结论、关键跟进信号和当前阻断项。</p>
        </div>
      </div>
      <div class="detail-card-grid">
        <article class="detail-panel detail-panel--accent">
          <h5 class="detail-panel__title">AI详研摘要</h5>
          <p class="detail-panel__text detail-copy">${escapeHtml(primarySuggestion || systemSummaryText || primaryEntryPoint || "AI详研生成后会在这里展示核心摘要")}</p>
        </article>
        <article class="detail-panel">
          <h5 class="detail-panel__title">主判断依据</h5>
          ${renderList(decisionSignals, "暂无足够的跟进信号")}
        </article>
        <article class="detail-panel">
          <h5 class="detail-panel__title">风险提醒</h5>
          ${renderList(riskTags, "当前没有明显阻断项")}
        </article>
      </div>
    </section>

    ${
      showContactSection
        ? `
      <section class="detail-section detail-section--main">
        <div class="detail-section__header">
          <div>
            <h4 class="detail-section__title">联系人优先级</h4>
            <p class="detail-section__subtitle">先确定首联系人，再决定是否需要备用联系人补位。</p>
          </div>
        </div>
        <div class="contact-priority">
          ${renderContactCard(primaryContact, { primary: true })}
          ${
            backupContacts.length
              ? `
            <div class="contact-card__backups">
              ${backupContacts.map((contact) => renderContactCard(contact)).join("")}
            </div>
          `
              : '<div class="detail-note">当前没有更多高质量备选联系人，可先从首联系人切入。</div>'
          }
        </div>
      </section>
    `
        : ""
    }

    ${
      showOutreachSection
        ? `
      <section class="detail-section detail-section--main">
        <div class="detail-section__header">
          <div>
            <h4 class="detail-section__title">触达组织建议</h4>
            <p class="detail-section__subtitle">先看主切口和推进动作，再按需展开完整触达话术，阅读路径更接近真实跟进节奏。</p>
          </div>
        </div>
        <div class="outreach-section-body">
          ${outreachPlaybook}
          ${contactScriptCard}
        </div>
      </section>
    `
        : ""
    }

    ${
      showBackgroundSection
        ? `
      <section class="detail-section detail-section--main">
        <div class="detail-section__header">
          <div>
            <h4 class="detail-section__title">背景与动态摘要</h4>
            <p class="detail-section__subtitle">保留背景价值，但只展示摘要，不让它和前面的决策层抢注意力。</p>
          </div>
        </div>
        <div class="detail-card-grid">
          ${backgroundCards.join("")}
        </div>
      </section>
    `
        : ""
    }

    ${
      evidenceCount
        ? renderCollapsibleSection(
            `证据与原始资料（${evidenceCount}）`,
            `
              <div class="detail-evidence-stack">
                ${
                  Object.keys(nameCalibration).length
                    ? renderEvidenceBlock(
                        "名称校准",
                        renderKeyValueGrid([
                          { label: "输入初始名称", value: nameCalibration.input_name },
                          { label: "官方全称", value: nameCalibration.official_full_name },
                          { label: "高概率候选名称", value: (nameCalibration.candidates || []).join("；") },
                          { label: "可信度", value: nameCalibration.confidence },
                        ]),
                      )
                    : ""
                }
                ${
                  relatedLinks.length
                    ? renderEvidenceBlock(
                        "相关链接",
                        `
                          <div class="table-wrap">
                            <table class="records-table">
                              <thead>
                                <tr><th>名称</th><th>类型</th><th>链接</th></tr>
                              </thead>
                              <tbody>
                                ${relatedLinks
                                  .map(
                                    (link) => `
                                      <tr>
                                        <td>${escapeHtml(link.label || "-")}</td>
                                        <td>${escapeHtml(link.type || "-")}</td>
                                        <td>${renderExternalLink(link.url, link.url || "查看链接")}</td>
                                      </tr>
                                    `,
                                  )
                                  .join("")}
                              </tbody>
                            </table>
                          </div>
                        `,
                      )
                    : ""
                }
                ${
                  profileSources.length
                    ? renderEvidenceBlock(
                        `画像来源（${profileSources.length}）`,
                        `
                          <div class="table-wrap">
                            <table class="records-table">
                              <thead>
                                <tr><th>字段</th><th>值</th><th>证据</th><th>来源</th><th>可信度</th></tr>
                              </thead>
                              <tbody>
                                ${profileSources
                                  .map(
                                    (source) => `
                                      <tr>
                                        <td>${escapeHtml(source.field_name || "-")}</td>
                                        <td>${escapeHtml(source.field_value || "-")}</td>
                                        <td><div class="detail-copy">${escapeHtml(source.evidence_text || "-")}</div></td>
                                        <td>${renderExternalLink(source.source_url, source.source_title || "查看来源")}</td>
                                        <td>${escapeHtml(source.confidence || "-")}</td>
                                      </tr>
                                    `,
                                  )
                                  .join("")}
                              </tbody>
                            </table>
                          </div>
                        `,
                      )
                    : ""
                }
                ${
                  (research?.field_results || []).length
                    ? renderEvidenceBlock(
                        `AI 字段证据（${research.field_results.length}）`,
                        `
                          <div class="table-wrap">
                            <table class="records-table">
                              <thead>
                                <tr><th>字段</th><th>值</th><th>证据</th><th>来源</th><th>可信度</th></tr>
                              </thead>
                              <tbody>
                                ${research.field_results
                                  .map(
                                    (field) => `
                                      <tr>
                                        <td>${escapeHtml(field.field_name || "-")}</td>
                                        <td>${escapeHtml(field.field_value || "-")}</td>
                                        <td><div class="detail-copy">${escapeHtml(field.evidence_text || "-")}</div></td>
                                        <td>${renderExternalLink(field.url, field.source || "查看来源")}</td>
                                        <td>${escapeHtml(field.confidence || "-")}</td>
                                      </tr>
                                    `,
                                  )
                                  .join("")}
                              </tbody>
                            </table>
                          </div>
                        `,
                      )
                    : ""
                }
                ${
                  (research?.competitors || []).length
                    ? renderEvidenceBlock(
                        `竞品证据（${research.competitors.length}）`,
                        `
                          <div class="table-wrap">
                            <table class="records-table">
                              <thead>
                                <tr><th>竞品</th><th>判断依据</th><th>来源</th><th>可信度</th></tr>
                              </thead>
                              <tbody>
                                ${research.competitors
                                  .map(
                                    (competitor) => `
                                      <tr>
                                        <td>${escapeHtml(competitor.name || "-")}</td>
                                        <td><div class="detail-copy">${escapeHtml(competitor.reason || "-")}</div></td>
                                        <td>${renderExternalLink(competitor.url, competitor.source || "查看来源")}</td>
                                        <td>${escapeHtml(competitor.confidence || "-")}</td>
                                      </tr>
                                    `,
                                  )
                                  .join("")}
                              </tbody>
                            </table>
                          </div>
                        `,
                      )
                    : ""
                }
              </div>
            `,
            { collapsed: true },
          )
        : ""
    }
    ${
      contactList.length
        ? renderCollapsibleSection(
            `联系人全表（${contactList.length}）`,
            `
              <div class="table-wrap">
                <table class="records-table">
                  <thead>
                    <tr>
                      <th>标记</th>
                      <th>姓名</th>
                      <th>职位</th>
                      <th>联系方式</th>
                      <th>来源</th>
                    </tr>
                  </thead>
                  <tbody>
                    ${sortedContacts
                      .map(
                        (contact) => `
                          <tr>
                            <td>${contact.is_hot ? '<span class="status-pill status-pill--hot">HOT</span>' : "-"}</td>
                            <td>${escapeHtml(contactDisplayName(contact))}</td>
                            <td>${escapeHtml(contactDisplayPosition(contact))}</td>
                            <td>${escapeHtml(contactDisplayValue(contact) || "-")}</td>
                            <td>${escapeHtml(contact.source || "-")}</td>
                          </tr>
                        `,
                      )
                      .join("")}
                  </tbody>
                </table>
              </div>
            `,
            { collapsed: true },
          )
        : ""
    }
    ${
      recruitings.length
        ? renderCollapsibleSection(
            `招聘原文（${recruitings.length}）`,
            `
          <p class="muted">已抓取 ${recruitmentSnapshot.recruiting_fetched_count || recruitings.length} 条 / 总计 ${
              recruitmentSnapshot.recruiting_total || recruitings.length
            } 条，当前最多展示前 100 条。${recruitmentSnapshot.keyword ? `关键词：${escapeHtml(recruitmentSnapshot.keyword)}` : "关键词：全部"}</p>
          <div class="recruitment-filter" data-role="recruitment-filter">
            <div class="records-toolbar records-toolbar--detail">
              <input type="text" placeholder="搜索岗位名、城市、学历/经验或 JD 关键词" data-action="filter-recruitings" />
              <span class="pill pill--soft" data-role="recruiting-filter-count">共 ${recruitings.length} 个岗位</span>
            </div>
            <p class="detail-note" data-role="recruiting-filter-empty" hidden>没有匹配的岗位，试试更短的关键词。</p>
            <div class="table-wrap">
              <table class="records-table">
                <thead>
                  <tr>
                    <th>岗位</th>
                    <th>城市</th>
                    <th>薪资</th>
                    <th>学历/经验</th>
                    <th>发布时间</th>
                    <th>来源</th>
                    <th>JD</th>
                  </tr>
                </thead>
                <tbody>
                  ${recruitings
                    .map(
                      (job) => `
                        <tr data-role="recruiting-row" data-search-text="${escapeHtml(buildRecruitingSearchText(job))}">
                          <td>${escapeHtml(job.title || "-")}</td>
                          <td>${escapeHtml(job.city || job.district || "-")}</td>
                          <td>${escapeHtml(
                            job.salary_min || job.salary_max
                              ? `${job.salary_min || "-"}-${job.salary_max || "-"} ${job.salary_currency || ""}`.trim()
                              : "-",
                          )}</td>
                          <td>${escapeHtml(
                            [job.education, job.seniority_min ? `${job.seniority_min}${job.seniority_max ? `-${job.seniority_max}` : "+"}年` : ""]
                              .filter(Boolean)
                              .join(" / ") || "-",
                          )}</td>
                          <td>${escapeHtml(job.published_at || "-")}</td>
                          <td>${renderExternalLink(job.source_url, job.source || "查看原文")}</td>
                          <td><div class="detail-copy">${escapeHtml(job.desc || "-")}</div></td>
                        </tr>
                      `,
                    )
                    .join("")}
                </tbody>
              </table>
            </div>
          </div>
        `,
            { collapsed: true },
          )
        : ""
    }
    ${
      Object.keys(exportFields).length
        ? renderCollapsibleSection(
            `完整字段（${Object.keys(exportFields).length}）`,
            renderExportFields(item.result),
            { collapsed: true },
          )
        : ""
    }
  `;

  body.querySelectorAll('[data-action="toggle-contact-script"]').forEach((button) => {
    button.addEventListener("click", () => {
      const card = button.closest(".contact-script-card");
      const expandedColumn = card?.querySelector(".contact-script-card__expanded-column");
      if (!card || !expandedColumn) {
        return;
      }
      const nextExpanded = expandedColumn.hidden;
      expandedColumn.hidden = !expandedColumn.hidden;
      expandedColumn.dataset.expanded = nextExpanded ? "true" : "false";
      button.setAttribute("aria-expanded", nextExpanded ? "true" : "false");
      card.dataset.expanded = nextExpanded ? "true" : "false";
      button.textContent = nextExpanded ? "收起完整话术" : "展开完整话术";
    });
  });
  bindRecruitingSearch(body);

  modal.hidden = false;
  document.body.style.overflow = "hidden";
}

function closeDetailModal() {
  const modal = document.getElementById("detail-modal");
  if (!modal) {
    return;
  }
  closeKnowledgeDocumentModal();
  modal.hidden = true;
  document.body.style.overflow = "";
}

function closeKnowledgeDocumentModal() {
  const modal = document.getElementById("knowledge-doc-modal");
  if (!modal) {
    return;
  }
  modal.hidden = true;
}

let knowledgeDocumentMarkdownRenderer = null;

function getKnowledgeDocumentMarkdownRenderer() {
  if (knowledgeDocumentMarkdownRenderer) {
    return knowledgeDocumentMarkdownRenderer;
  }
  if (typeof window.markdownit !== "function") {
    return null;
  }
  const renderer = window.markdownit({
    html: false,
    breaks: true,
    linkify: true,
    typographer: false,
  });
  const defaultLinkOpen =
    renderer.renderer.rules.link_open ||
    function renderDefault(tokens, idx, options, env, self) {
      return self.renderToken(tokens, idx, options);
    };
  renderer.renderer.rules.link_open = function renderLinkOpen(tokens, idx, options, env, self) {
    const token = tokens[idx];
    if (token.attrIndex("target") < 0) {
      token.attrPush(["target", "_blank"]);
    } else {
      token.attrs[token.attrIndex("target")][1] = "_blank";
    }
    if (token.attrIndex("rel") < 0) {
      token.attrPush(["rel", "noopener noreferrer"]);
    } else {
      token.attrs[token.attrIndex("rel")][1] = "noopener noreferrer";
    }
    return defaultLinkOpen(tokens, idx, options, env, self);
  };
  knowledgeDocumentMarkdownRenderer = renderer;
  return renderer;
}

function setKnowledgeDocumentStatus(node, message) {
  if (!node) {
    return;
  }
  node.dataset.state = "status";
  node.textContent = message;
}

function renderKnowledgeDocumentMarkdown(node, rawText, fallbackMessage) {
  if (!node) {
    return;
  }
  const markdown = String(rawText || "").trim();
  if (!markdown) {
    setKnowledgeDocumentStatus(node, fallbackMessage);
    return;
  }

  const renderer = getKnowledgeDocumentMarkdownRenderer();
  if (!renderer) {
    node.dataset.state = "plain";
    node.textContent = markdown;
    return;
  }

  const renderedHtml = renderer.render(markdown);
  const sanitizedHtml =
    window.DOMPurify && typeof window.DOMPurify.sanitize === "function"
      ? window.DOMPurify.sanitize(renderedHtml)
      : renderedHtml;
  node.dataset.state = "markdown";
  node.innerHTML = sanitizedHtml;
}

async function openKnowledgeDocumentModal({ title, path, chunkId = "" } = {}) {
  if (!path) {
    window.alert("当前引用缺少文档路径，暂时无法查看全文。");
    return;
  }
  const modal = document.getElementById("knowledge-doc-modal");
  const titleNode = document.getElementById("knowledge-doc-modal-title");
  const metaNode = document.getElementById("knowledge-doc-modal-meta");
  const chunkSection = document.getElementById("knowledge-doc-modal-chunk");
  const chunkNode = document.getElementById("knowledge-doc-modal-chunk-text");
  const fullTextNode = document.getElementById("knowledge-doc-modal-full-text");
  if (!modal || !titleNode || !metaNode || !chunkSection || !chunkNode || !fullTextNode) {
    return;
  }

  titleNode.textContent = title || "查看全文";
  metaNode.textContent = path;
  metaNode.hidden = !path;
  chunkSection.hidden = true;
  chunkNode.textContent = "";
  delete chunkNode.dataset.state;
  setKnowledgeDocumentStatus(fullTextNode, "正在加载全文…");
  modal.hidden = false;

  try {
    const payload = await apiFetch(
      buildApiUrl("/api/research/knowledge-document", {
        path,
        chunk_id: chunkId || undefined,
      }),
    );
    const document = payload.document || {};
    const chunkText = String(document.chunk_text || "").trim();
    const fullText = String(document.full_text || "").trim();
    if (chunkText) {
      renderKnowledgeDocumentMarkdown(chunkNode, chunkText, "未读取到命中原文段落。");
      chunkSection.hidden = false;
    }
    renderKnowledgeDocumentMarkdown(fullTextNode, fullText, "未读取到完整文档内容。");
  } catch (error) {
    setKnowledgeDocumentStatus(fullTextNode, error.message || "全文加载失败，请稍后重试。");
  }
}

function bindKnowledgeDocumentModal() {
  const modal = document.getElementById("knowledge-doc-modal");
  if (!modal || modal.dataset.bound === "true") {
    return;
  }
  modal.dataset.bound = "true";
  modal.querySelectorAll('[data-action="close-knowledge-doc-modal"]').forEach((button) => {
    button.addEventListener("click", closeKnowledgeDocumentModal);
  });
}

function bindDetailModal() {
  const modal = document.getElementById("detail-modal");
  if (!modal || modal.dataset.bound === "true") {
    return;
  }
  modal.dataset.bound = "true";
  bindKnowledgeDocumentModal();
  modal.querySelectorAll('[data-action="close-detail-modal"]').forEach((button) => {
    button.addEventListener("click", closeDetailModal);
  });
  modal.addEventListener("click", (event) => {
    const copyButton = event.target.closest('[data-action="copy-detail-text"]');
    if (copyButton) {
      const text = copyButton.dataset.copyText || "";
      if (!text) {
        return;
      }
      const originalText = copyButton.dataset.originalText || copyButton.textContent || "复制";
      copyButton.dataset.originalText = originalText;
      const writeTask = navigator.clipboard?.writeText
        ? navigator.clipboard.writeText(text)
        : Promise.reject(new Error("clipboard unavailable"));
      writeTask
        .then(() => {
          copyButton.textContent = "已复制";
          window.setTimeout(() => {
            copyButton.textContent = copyButton.dataset.originalText || "复制";
          }, 1200);
        })
        .catch(() => {
          window.alert("当前浏览器不支持直接复制，请手动复制。");
      });
      return;
    }
    const knowledgeButton = event.target.closest('[data-action="open-knowledge-document"]');
    if (knowledgeButton) {
      void openKnowledgeDocumentModal({
        title: knowledgeButton.dataset.docTitle || "",
        path: knowledgeButton.dataset.docPath || "",
        chunkId: knowledgeButton.dataset.docChunkId || "",
      });
      return;
    }
    const toggle = event.target.closest('[data-action="toggle-detail-section"]');
    if (!toggle) {
      return;
    }
    const section = toggle.closest(".detail-section");
    const content = section?.querySelector(".detail-section__content");
    if (!section || !content) {
      return;
    }
    const collapsed = section.dataset.collapsed === "true";
    section.dataset.collapsed = collapsed ? "false" : "true";
    content.hidden = !collapsed;
    toggle.setAttribute("aria-expanded", collapsed ? "true" : "false");
  });
  document.addEventListener("keydown", (event) => {
    const knowledgeModal = document.getElementById("knowledge-doc-modal");
    if (event.key === "Escape" && knowledgeModal && !knowledgeModal.hidden) {
      closeKnowledgeDocumentModal();
      return;
    }
    if (event.key === "Escape" && !modal.hidden) {
      closeDetailModal();
    }
  });
}

function filterRecentJobs(jobs) {
  const search = normalizeSearchText(recentJobState.search);
  const status = recentJobState.status;
  return jobs
    .map((job) => {
      const filteredItems = (job.items || []).filter((item) => {
        const matchesStatus = status === "all" || item.status === status;
        const exportFields = item.result?.export_fields || {};
        const haystack = [
          item.input_company_name,
          item.matched_company_name,
          item.result?.export_fields?.["公司名称"],
          exportFields["招聘代表岗位"],
          exportFields["客户招聘信息"],
          exportFields["在招职位数"],
          exportFields["IT团队规模"],
          job.recruiting_keyword,
        ]
          .filter(Boolean)
          .join(" ")
          .toLowerCase();
        const matchesSearch = !search || haystack.includes(search);
        return matchesStatus && matchesSearch;
      });
      return {
        ...job,
        items: filteredItems,
        summary: filteredItems.reduce((acc, item) => {
          acc[item.status] = (acc[item.status] || 0) + 1;
          return acc;
        }, {}),
        submitted_count: filteredItems.length,
      };
    })
    .filter((job) => (job.items || []).length > 0);
}

function renderPagination(totalCount) {
  const container = document.getElementById("job-pagination");
  if (!container) {
    return;
  }
  if (totalCount === 0) {
    container.innerHTML = "";
    return;
  }
  const totalPages = Math.max(1, Math.ceil(totalCount / recentJobState.pageSize));
  if (recentJobState.page > totalPages) {
    recentJobState.page = totalPages;
  }
  container.innerHTML = `
    <span class="pagination-meta">共 ${totalCount} 个批次，第 ${recentJobState.page} / ${totalPages} 页</span>
    <div class="pagination-actions">
      <button class="secondary-btn" type="button" id="job-page-prev" ${recentJobState.page <= 1 ? "disabled" : ""}>上一页</button>
      <button class="secondary-btn" type="button" id="job-page-next" ${recentJobState.page >= totalPages ? "disabled" : ""}>下一页</button>
    </div>
  `;
  container.querySelector("#job-page-prev")?.addEventListener("click", () => {
    if (recentJobState.page > 1) {
      recentJobState.page -= 1;
      void reloadConsoleQueryJobs().catch(() => {});
    }
  });
  container.querySelector("#job-page-next")?.addEventListener("click", () => {
    if (recentJobState.page < totalPages) {
      recentJobState.page += 1;
      void reloadConsoleQueryJobs().catch(() => {});
    }
  });
}

function renderRecentJobs(emptyText = "还没有记录。") {
  const container = document.getElementById("job-list");
  if (!container) {
    return;
  }
  const filteredJobs = filterRecentJobs(recentJobState.jobs);
  scheduleResearchListAutoRefresh(hasInFlightResearchItems(filteredJobs));
  renderPagination(recentJobState.search.trim() ? filteredJobs.length : recentJobState.total);
  if (!filteredJobs.length) {
    renderEmpty(container, emptyText);
    return;
  }
  renderJobCards(container, filteredJobs, { showUser: false });
}

function renderHistoryPagination(totalCount) {
  const container = document.getElementById("history-job-pagination");
  if (!container) {
    return;
  }
  if (totalCount === 0) {
    container.innerHTML = "";
    return;
  }
  const totalPages = Math.max(1, Math.ceil(totalCount / historyJobState.pageSize));
  if (historyJobState.page > totalPages) {
    historyJobState.page = totalPages;
  }
  container.innerHTML = `
    <span class="pagination-meta">共 ${totalCount} 个批次，第 ${historyJobState.page} / ${totalPages} 页</span>
    <div class="pagination-actions">
      <button class="secondary-btn" type="button" id="history-job-page-prev" ${historyJobState.page <= 1 ? "disabled" : ""}>上一页</button>
      <button class="secondary-btn" type="button" id="history-job-page-next" ${historyJobState.page >= totalPages ? "disabled" : ""}>下一页</button>
    </div>
  `;
  container.querySelector("#history-job-page-prev")?.addEventListener("click", () => {
    if (historyJobState.page > 1) {
      historyJobState.page -= 1;
      void loadHistoryJobs().catch(() => {});
    }
  });
  container.querySelector("#history-job-page-next")?.addEventListener("click", () => {
    if (historyJobState.page < totalPages) {
      historyJobState.page += 1;
      void loadHistoryJobs().catch(() => {});
    }
  });
}

function renderHistoryJobs(emptyText = "还没有记录。") {
  const container = document.getElementById("history-job-list");
  if (!container) {
    return;
  }
  scheduleResearchListAutoRefresh(hasInFlightResearchItems(historyJobState.jobs));
  renderHistoryPagination(historyJobState.total);
  if (!historyJobState.jobs.length) {
    renderEmpty(container, emptyText);
    return;
  }
  renderJobCards(container, historyJobState.jobs, { showUser: false });
}

function renderAdminPagination(totalCount) {
  const container = document.getElementById("admin-job-pagination");
  if (!container) {
    return;
  }
  if (totalCount === 0) {
    container.innerHTML = "";
    return;
  }
  const totalPages = Math.max(1, Math.ceil(totalCount / adminJobState.pageSize));
  if (adminJobState.page > totalPages) {
    adminJobState.page = totalPages;
  }
  container.innerHTML = `
    <span class="pagination-meta">第 ${adminJobState.page} / ${totalPages} 页</span>
    <div class="pagination-actions">
      <button class="secondary-btn" type="button" id="admin-job-page-prev" ${adminJobState.page <= 1 ? "disabled" : ""}>上一页</button>
      <button class="secondary-btn" type="button" id="admin-job-page-next" ${adminJobState.page >= totalPages ? "disabled" : ""}>下一页</button>
    </div>
  `;
  container.querySelector("#admin-job-page-prev")?.addEventListener("click", () => {
    if (adminJobState.page > 1) {
      adminJobState.page -= 1;
      void loadAdminJobs().catch(() => {});
    }
  });
  container.querySelector("#admin-job-page-next")?.addEventListener("click", () => {
    if (adminJobState.page < totalPages) {
      adminJobState.page += 1;
      void loadAdminJobs().catch(() => {});
    }
  });
}

function renderAdminJobs(emptyText = "还没有记录。") {
  const container = document.getElementById("admin-job-list");
  if (!container) {
    return;
  }
  scheduleResearchListAutoRefresh(hasInFlightResearchItems(adminJobState.jobs));
  renderAdminPagination(adminJobState.total);
  if (!adminJobState.jobs.length) {
    renderEmpty(container, emptyText);
    return;
  }
  renderJobCards(container, adminJobState.jobs, { showUser: true });
}

function bindRecentJobControls() {
  const searchInput = document.getElementById("job-search-input");
  const statusSelect = document.getElementById("job-status-filter");
  searchInput?.addEventListener("input", (event) => {
    recentJobState.search = event.target.value || "";
    recentJobState.page = 1;
    if (recentJobState.searchTimer) {
      window.clearTimeout(recentJobState.searchTimer);
    }
    recentJobState.searchTimer = window.setTimeout(() => {
      renderRecentJobs("当前页没有匹配的岗位或公司。");
      recentJobState.searchTimer = null;
    }, 250);
  });
  statusSelect?.addEventListener("change", (event) => {
    if (recentJobState.searchTimer) {
      window.clearTimeout(recentJobState.searchTimer);
      recentJobState.searchTimer = null;
    }
    recentJobState.status = event.target.value || "all";
    recentJobState.page = 1;
    void reloadConsoleQueryJobs().catch(() => {});
  });
}

async function reloadConsoleQueryJobs({ silent = false, skipSessionCheck = false } = {}) {
  const container = document.getElementById("job-list");
  if (!container) {
    return;
  }
  if (!silent) {
    renderLoadingState(container, "正在加载最近查询记录…", { cardCount: 2 });
  }
  const statusPayload = skipSessionCheck ? latestTungeeStatusPayload : await loadTungeeStatus();
  if (!statusPayload?.connected || statusPayload?.ok === false) {
    clearDetailPayloadCache({ admin: false });
    recentJobState.jobs = [];
    recentJobState.total = 0;
    renderRecentJobs("登录探迹账号后可查看当前账号的查询记录。");
    return;
  }
  const payload = await apiFetch(
    buildApiUrl("/api/query-jobs", {
      page: recentJobState.page,
      page_size: recentJobState.pageSize,
      item_status: recentJobState.status !== "all" ? recentJobState.status : undefined,
    }),
  );
  const totalPages = Number(payload.pagination?.total_pages || 0);
  if (totalPages > 0 && recentJobState.page > totalPages) {
    recentJobState.page = totalPages;
    return reloadConsoleQueryJobs({ silent, skipSessionCheck });
  }
  clearDetailPayloadCache({ admin: false });
  recentJobState.jobs = payload.jobs || [];
  applyPaginationState(recentJobState, payload.pagination);
  renderRecentJobs();
}

function renderJobCards(container, jobs, { showUser = false } = {}) {
  clearBusyState(container);
  if (!jobs.length) {
    renderEmpty(container, "还没有记录。");
    return;
  }

  container.innerHTML = jobs
    .map((job) => {
      const triggerUser = String(job.username || "").trim() || "-";
      const syncAccount = formatTungeeAccountLabel({
        name: job.tungee_name,
        mobile: job.tungee_mobile,
        fallback: "未识别",
      });
      const adminSummary = renderStatusSummary(job.summary || {});
      const jobCount = Number(job.submitted_count || (job.items || []).length || 0);
      const jobStatus = renderStatusPill(job.status, { translated: showUser });
      const items = (job.items || [])
        .map((item) => {
          const fields = item.result?.export_fields || {};
          const researchAction = getResearchActionMeta(item.research || null);
          return `
            <tr>
              <td>
                <div class="table-cell-main">${escapeHtml(item.input_company_name || "-")}</div>
              </td>
              <td>${renderStatusPill(item.status, { translated: showUser })}</td>
              <td>${escapeHtml(item.matched_company_name || "-")}</td>
              <td>${escapeHtml(formatFieldValue(fields["城市"]))}</td>
              <td>
                <div class="row-actions">
                  <button class="${showUser ? "ghost-btn" : "secondary-btn"}" type="button" data-action="view-detail" data-job-id="${job.public_id}" data-item-id="${item.public_id}">查看详情</button>
                  ${
                    showUser
                      ? ""
                      : `<button class="ghost-btn" type="button" data-action="run-research" data-item-id="${item.public_id}" data-default-text="${escapeHtml(researchAction.defaultText)}" data-research-status="${escapeHtml(researchAction.status)}" data-running-text="${escapeHtml(researchAction.runningText)}" ${researchAction.disabled ? "disabled" : ""}>${escapeHtml(researchAction.text)}</button>`
                  }
                  ${
                    showUser
                      ? ""
                      : `<button class="ghost-btn" type="button" aria-label="删除" data-action="delete-item" data-item-id="${item.public_id}" ${canDeleteRecord(item) ? "" : "disabled"}>${renderSvgIcon("trash", "detail-svg-icon")}</button>`
                  }
                </div>
              </td>
            </tr>
          `;
        })
        .join("");
      if (showUser) {
        return `
        <article class="list-card list-card--admin">
          <div class="list-card__header list-card__header--admin">
            <div class="list-card__identity">
              <div class="list-card__title-row list-card__title-row--admin">
                <h3>${escapeHtml(formatDateTime(job.created_at))}</h3>
                ${jobStatus}
              </div>
              <div class="list-card__meta">
                <span>触发人：${escapeHtml(triggerUser)}</span>
                <span>同步账号：${escapeHtml(syncAccount)}</span>
                <span>共 ${escapeHtml(jobCount)} 家企业</span>
              </div>
            </div>
            <div class="list-card__summary">
              ${adminSummary || `<span class="summary-pill">暂无状态汇总</span>`}
            </div>
          </div>
          <div class="table-wrap table-wrap--admin">
            <table class="records-table records-table--jobs">
              <thead>
                <tr>
                  <th>输入公司名</th>
                  <th>状态</th>
                  <th>命中公司</th>
                  <th>城市</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>${items}</tbody>
            </table>
          </div>
        </article>
      `;
      }
      return `
        <article class="list-card">
          <div class="list-card__header">
            <div class="list-card__identity">
              <div class="list-card__title-row">
                <h3>查询记录</h3>
                <span class="muted">查询时间：${escapeHtml(formatDateTime(job.created_at))}</span>
              </div>
              <p class="muted list-card__submeta">同步账号：${escapeHtml(syncAccount)} · 触发人：${escapeHtml(triggerUser)}</p>
            </div>
            <div class="button-row">
              <button class="secondary-btn" type="button" data-action="export-job" data-job-id="${job.public_id}" data-format="csv">导出 CSV</button>
              <button class="ghost-btn" type="button" data-action="export-job" data-job-id="${job.public_id}" data-format="xlsx">导出 XLSX</button>
            </div>
          </div>
          <div class="table-wrap">
            <table class="records-table records-table--jobs">
              <thead>
                <tr>
                  <th>输入公司名</th>
                  <th>状态</th>
                  <th>命中公司</th>
                  <th>城市</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>${items}</tbody>
            </table>
          </div>
        </article>
      `;
    })
    .join("");

  bindDetailModal();
  syncResearchButtons();
  container.querySelectorAll('[data-action="export-job"]').forEach((button) => {
    button.addEventListener("click", () => {
      setButtonLoading(button, true, "准备中…");
      openJobExport(button.dataset.jobId, button.dataset.format);
      window.setTimeout(() => setButtonLoading(button, false), 800);
    });
  });
  container.querySelectorAll('[data-action="view-detail"]').forEach((button) => {
    button.addEventListener("click", async () => {
      try {
        const payload = await withButtonLoading(button, "加载中…", () =>
          fetchJobDetailForItem(button.dataset.jobId, button.dataset.itemId, { admin: showUser }),
        );
        renderDetailModal(payload);
      } catch (error) {
        alert(error.message);
      }
    });
  });
  container.querySelectorAll('[data-action="delete-item"]').forEach((button) => {
    button.addEventListener("click", async () => {
      if (!window.confirm("确认删除这条查询记录吗？删除后不可恢复。")) {
        return;
      }
      try {
        await withButtonLoading(button, "删除中…", () =>
          apiFetch(`/api/query-jobs/items/${button.dataset.itemId}`, {
            method: "DELETE",
          }),
        );
        await reloadConsoleQueryJobs();
      } catch (error) {
        alert(error.message);
      }
    });
  });
  container.querySelectorAll('[data-action="run-research"]').forEach((button) => {
    button.addEventListener("click", async () => {
      const queryItemId = button.dataset.itemId;
      try {
        setResearchUiState(queryItemId, { loading: true, text: "启动中…" });
        await apiFetch("/api/research/run", {
          method: "POST",
          body: JSON.stringify({ query_item_public_id: queryItemId }),
        });
        await pollResearchProgress(queryItemId, {
          timeoutMs: 300000,
          onProgress: (_research, _stageText, percent) => {
            setResearchUiState(queryItemId, {
              loading: true,
              percent,
              text: `详研中 ${percent}%`,
            });
          },
        });
        await reloadConsoleQueryJobs();
      } catch (error) {
        if (error.message === "AI详研进行中，暂不支持重跑") {
          await reloadConsoleQueryJobs();
        }
        alert(error.message);
      } finally {
        setResearchUiState(queryItemId, null);
      }
    });
  });
}

async function logout() {
  window.location.href = "/console";
}

function bindLogout() {
  document.querySelectorAll('[data-action="logout"]').forEach((button) => {
    button.addEventListener("click", logout);
  });
}

function initAdminGatePage() {
  const form = document.getElementById("admin-gate-form");
  const message = document.getElementById("admin-gate-message");
  form?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(form);
    const submitButton = form.querySelector('button[type="submit"]');
    try {
      await withButtonLoading(submitButton, "验证中…", () =>
        apiFetch("/api/admin/gate/login", {
          method: "POST",
          body: JSON.stringify({ password: formData.get("password") }),
        }),
      );
      window.location.href = "/admin";
    } catch (error) {
      message.textContent = error.message;
    }
  });
}

function initLoginPage() {
  const form = document.getElementById("login-form");
  const message = document.getElementById("login-message");
  form?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(form);
    const submitButton = form.querySelector('button[type="submit"]');
    try {
      await withButtonLoading(submitButton, "登录中…", () =>
        apiFetch("/api/auth/login", {
          method: "POST",
          body: JSON.stringify({
            username: formData.get("username"),
            password: formData.get("password"),
          }),
        }),
      );
      window.location.href = "/console";
    } catch (error) {
      message.textContent = error.message;
    }
  });
}

async function loadHistoryJobs({ silent = false } = {}) {
  const container = document.getElementById("history-job-list");
  if (!container) {
    return;
  }
  if (!silent) {
    renderLoadingState(container, "正在加载历史记录…", { cardCount: 2 });
  }
  try {
    const payload = await apiFetch(
      buildApiUrl("/api/query-jobs", {
        page: historyJobState.page,
        page_size: historyJobState.pageSize,
      }),
    );
    const totalPages = Number(payload.pagination?.total_pages || 0);
    if (totalPages > 0 && historyJobState.page > totalPages) {
      historyJobState.page = totalPages;
      return loadHistoryJobs({ silent });
    }
    clearDetailPayloadCache({ admin: false });
    historyJobState.jobs = payload.jobs || [];
    applyPaginationState(historyJobState, payload.pagination);
    renderHistoryJobs();
  } catch (error) {
    historyJobState.jobs = [];
    historyJobState.total = 0;
    renderHistoryJobs(error.message || "加载失败");
    throw error;
  }
}

async function loadAdminJobs({ silent = false } = {}) {
  const container = document.getElementById("admin-job-list");
  if (!container) {
    return;
  }
  if (!silent) {
    renderLoadingState(container, "正在加载全量查询记录…", { cardCount: 3 });
  }
  const payload = await apiFetch(
    buildApiUrl("/api/admin/query-jobs", {
      page: adminJobState.page,
      page_size: adminJobState.pageSize,
    }),
  );
  const totalPages = Number(payload.pagination?.total_pages || 0);
  if (totalPages > 0 && adminJobState.page > totalPages) {
    adminJobState.page = totalPages;
    return loadAdminJobs({ silent });
  }
  clearDetailPayloadCache({ admin: true });
  adminJobState.jobs = payload.jobs || [];
  applyPaginationState(adminJobState, payload.pagination);
  setAdminQueryCount(adminJobState.total);
  renderAdminJobs();
}

function initConsolePage() {
  const form = document.getElementById("query-job-form");
  const message = document.getElementById("query-job-message");
  const submitButton = form?.querySelector('button[type="submit"]');
  const viewContextButton = document.getElementById("view-tungee-context-button");
  renderStatusLoading(document.getElementById("tungee-session-status"), "正在校验探迹会话…");
  renderLoadingState(document.getElementById("job-list"), "正在加载最近查询记录…", { cardCount: 2 });
  bindDetailModal();

  const load = async () => {
    await reloadConsoleQueryJobs();
  };
  load().catch((error) => {
    setFormMessage(message, error.message || "加载查询记录失败");
  });

  form?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(form);
    const companyNames = String(formData.get("company_names") || "")
      .split("\n")
      .map((item) => item.trim())
      .filter(Boolean);
    if (companyNames.length > 10) {
      setFormMessage(message, "单次最多查询 10 家公司");
      return;
    }
    try {
      setConsoleJobAutoRefreshIndicator(true, "已收到创建请求，正在校验探迹会话…", "loading");
      const statusPayload = await loadTungeeStatus();
      if (!statusPayload?.connected || statusPayload?.ok === false) {
        setFormMessage(message, "当前探迹会话不可用，请先同步浏览器里的探迹登录态。");
        flashConsoleJobAutoRefreshIndicator("探迹会话不可用，请先同步浏览器登录态", "error", 3200);
        return;
      }
      let targetCompanyNames = [...companyNames];
      let resolvedMatches = [];
      let prefetchedResults = [];
      try {
        const pluginReady = await waitForPluginReady(1500);
        if (pluginReady) {
          setFormMessage(message, "正在通过浏览器插件执行企业搜索…", "neutral");
          setConsoleJobAutoRefreshIndicator(true, "已开始创建查询批次，正在匹配企业信息…", "loading");
          const searchPayload = await requestPluginCompanySearch(companyNames);
          resolvedMatches = Array.isArray(searchPayload?.resolved_matches) ? searchPayload.resolved_matches : [];
          prefetchedResults = Array.isArray(searchPayload?.prefetched_results) ? searchPayload.prefetched_results : [];
          const unresolvedCompanyNames = companyNames.filter(
            (name) => !resolvedMatches.find((item) => item.input_company_name === name),
          );
          if (resolvedMatches.length) {
            targetCompanyNames = resolvedMatches.map((item) => item.input_company_name).filter(Boolean);
            prefetchedResults = prefetchedResults.filter((item) =>
              targetCompanyNames.includes(String(item?.input_company_name || "").trim()),
            );
            if (unresolvedCompanyNames.length) {
              setFormMessage(
                message,
                `已自动跳过未命中公司：${unresolvedCompanyNames.join("、")}；本次继续查询 ${targetCompanyNames.length} 家。`,
                "neutral",
              );
            }
          } else if (companyNames.length) {
            throw new Error(summarizePluginSearchFailure(searchPayload, companyNames));
          }
        }
      } catch (error) {
        throw new Error(`浏览器搜索未完成：${error.message || "未知错误"}`);
      }
      setConsoleJobAutoRefreshIndicator(true, `企业已匹配，正在创建查询批次（${targetCompanyNames.length} 家）…`, "loading");
      setFullscreenLoading(
        true,
        `正在创建查询批次（${targetCompanyNames.length} 家公司），后台处理中…`,
        "正在创建查询批次",
      );
      const payload = await withButtonLoading(submitButton, "创建中…", () =>
        apiFetch("/api/query-jobs", {
          method: "POST",
          body: JSON.stringify({
            company_names: targetCompanyNames,
            resolved_matches: resolvedMatches,
            prefetched_results: prefetchedResults,
          }),
        }),
      );
      form.reset();
      startConsoleJobAutoRefresh(payload.job, message);
    } catch (error) {
      setFormMessage(message, error.message || "创建查询批次失败");
      flashConsoleJobAutoRefreshIndicator(error.message || "创建查询批次失败", "error", 3200);
    } finally {
      setFullscreenLoading(false);
    }
  });

  bindTungeeSessionControls("query-job-message");
  bindRecentJobControls();
  initTungeePluginAutoSync(message);
  viewContextButton?.addEventListener("click", renderTungeeContextModal);
}

function normalizeOptionalFormValue(value) {
  const text = String(value || "").trim();
  return text || null;
}

function summarizePluginSearchFailure(searchPayload, companyNames) {
  const rawResults = Array.isArray(searchPayload?.raw_results) ? searchPayload.raw_results : [];
  if (!rawResults.length) {
    return `浏览器搜索没有返回可用结果：${companyNames.join("、")}`;
  }
  const resolvedMatches = Array.isArray(searchPayload?.resolved_matches) ? searchPayload.resolved_matches : [];
  const unresolved = companyNames.filter((name) => !resolvedMatches.find((item) => item.input_company_name === name));
  const unresolvedSummary = unresolved.length ? `未命中：${unresolved.join("、")}。` : "";
  const firstFailure = rawResults.find((item) => item.ok === false || Number(item.status || 0) >= 400);
  if (firstFailure?.payload?.outerMsg || firstFailure?.payload?.msg || firstFailure?.payload?.errorCode) {
    return `${unresolvedSummary}${firstFailure.payload.outerMsg || firstFailure.payload.msg || firstFailure.payload.errorCode}`;
  }
  if (firstFailure?.payload?.raw) {
    return `${unresolvedSummary}${String(firstFailure.payload.raw).slice(0, 120)}`;
  }
  if (firstFailure?.status) {
    return `${unresolvedSummary}浏览器搜索请求返回状态 ${firstFailure.status}`;
  }
  return unresolvedSummary || "浏览器搜索未返回可用匹配结果";
}

function waitForPluginReady(timeoutMs = 3000) {
  return new Promise((resolve) => {
    if (document.documentElement.dataset.tungeeSessionSyncInstalled === "1") {
      resolve(true);
      return;
    }
    const requestId = `tungee-plugin-ping-${Date.now()}-${Math.random().toString(36).slice(2)}`;
    let settled = false;
    function cleanup() {
      window.removeEventListener("message", handleMessage);
    }
    function finish(value) {
      if (settled) {
        return;
      }
      settled = true;
      cleanup();
      resolve(value);
    }
    function handleMessage(event) {
      if (event.source !== window) {
        return;
      }
      const data = event.data || {};
      if (
        data.source === "tungee-session-sync-extension" &&
        data.type === "ready" &&
        (!data.requestId || data.requestId === requestId)
      ) {
        finish(true);
      }
    }
    window.addEventListener("message", handleMessage);
    window.postMessage(
      {
        source: "bussiness-console",
        type: "TUNGEE_PLUGIN_PING",
        requestId,
      },
      window.location.origin,
    );
    window.setTimeout(() => finish(document.documentElement.dataset.tungeeSessionSyncInstalled === "1"), timeoutMs);
  });
}

function requestPluginSync(timeoutMs = 30000) {
  return new Promise((resolve, reject) => {
    const requestId = `tungee-plugin-sync-${Date.now()}-${Math.random().toString(36).slice(2)}`;
    let settled = false;
    function cleanup() {
      window.removeEventListener("message", handleMessage);
    }
    function finishSuccess(payload) {
      if (settled) {
        return;
      }
      settled = true;
      cleanup();
      resolve(payload);
    }
    function finishFailure(error) {
      if (settled) {
        return;
      }
      settled = true;
      cleanup();
      reject(error);
    }
    function handleMessage(event) {
      if (event.source !== window) {
        return;
      }
      const data = event.data || {};
      if (
        data.source === "tungee-session-sync-extension" &&
        data.type === "sync-result" &&
        data.requestId === requestId
      ) {
        if (data.payload?.ok === false) {
          finishFailure(new Error(data.payload?.message || "插件同步失败"));
          return;
        }
        finishSuccess(data.payload || {});
      }
    }
    window.addEventListener("message", handleMessage);
    window.postMessage(
      {
        source: "bussiness-console",
        type: "TUNGEE_PLUGIN_SYNC_REQUEST",
        requestId,
        localApiBase: window.location.origin,
      },
      window.location.origin,
    );
    window.setTimeout(() => finishFailure(new Error("等待插件同步结果超时，请确认浏览器里已打开探迹企业详情页。")), timeoutMs);
  });
}

function requestPluginCompanySearch(companyNames, timeoutMs = 60000) {
  return new Promise((resolve, reject) => {
    const requestId = `tungee-plugin-search-${Date.now()}-${Math.random().toString(36).slice(2)}`;
    let settled = false;
    function cleanup() {
      window.removeEventListener("message", handleMessage);
    }
    function finishSuccess(payload) {
      if (settled) {
        return;
      }
      settled = true;
      cleanup();
      resolve(payload);
    }
    function finishFailure(error) {
      if (settled) {
        return;
      }
      settled = true;
      cleanup();
      reject(error);
    }
    function handleMessage(event) {
      if (event.source !== window) {
        return;
      }
      const data = event.data || {};
      if (
        data.source === "tungee-session-sync-extension" &&
        data.type === "search-result" &&
        data.requestId === requestId
      ) {
        if (data.payload?.ok === false) {
          finishFailure(new Error(data.payload?.message || "插件搜索失败"));
          return;
        }
        finishSuccess(data.payload || {});
      }
    }
    window.addEventListener("message", handleMessage);
    window.postMessage(
      {
        source: "bussiness-console",
        type: "TUNGEE_PLUGIN_SEARCH_REQUEST",
        requestId,
        companyNames,
      },
      window.location.origin,
    );
    window.setTimeout(() => finishFailure(new Error("等待插件搜索结果超时，请确认浏览器里已打开探迹企业详情页。")), timeoutMs);
  });
}

function initTungeePluginAutoSync(messageElement) {
  const statusElement = document.getElementById("tungee-plugin-sync-status");
  const syncButton = document.getElementById("sync-from-browser-button");

  function setPluginSyncStatus(mainText, metaText, tone = "neutral") {
    if (!statusElement) {
      return;
    }
    statusElement.dataset.tone = tone;
    statusElement.innerHTML = `
      <span class="plugin-sync-banner__label">${escapeHtml(mainText)}</span>
      <span class="plugin-sync-banner__text">${escapeHtml(metaText)}</span>
    `;
  }

  function waitForPluginReady(timeoutMs = 3000) {
    return new Promise((resolve) => {
      if (document.documentElement.dataset.tungeeSessionSyncInstalled === "1") {
        resolve(true);
        return;
      }
      const requestId = `tungee-plugin-ping-${Date.now()}-${Math.random().toString(36).slice(2)}`;
      let settled = false;
      function cleanup() {
        window.removeEventListener("message", handleMessage);
      }
      function finish(value) {
        if (settled) {
          return;
        }
        settled = true;
        cleanup();
        resolve(value);
      }
      function handleMessage(event) {
        if (event.source !== window) {
          return;
        }
        const data = event.data || {};
        if (
          data.source === "tungee-session-sync-extension" &&
          data.type === "ready" &&
          (!data.requestId || data.requestId === requestId)
        ) {
          finish(true);
        }
      }
      window.addEventListener("message", handleMessage);
      window.postMessage(
        {
          source: "bussiness-console",
          type: "TUNGEE_PLUGIN_PING",
          requestId,
        },
        window.location.origin,
      );
      window.setTimeout(() => finish(document.documentElement.dataset.tungeeSessionSyncInstalled === "1"), timeoutMs);
    });
  }

  function requestPluginSync(timeoutMs = 30000) {
    return new Promise((resolve, reject) => {
      const requestId = `tungee-plugin-sync-${Date.now()}-${Math.random().toString(36).slice(2)}`;
      let settled = false;
      function cleanup() {
        window.removeEventListener("message", handleMessage);
      }
      function finishSuccess(payload) {
        if (settled) {
          return;
        }
        settled = true;
        cleanup();
        resolve(payload);
      }
      function finishFailure(error) {
        if (settled) {
          return;
        }
        settled = true;
        cleanup();
        reject(error);
      }
      function handleMessage(event) {
        if (event.source !== window) {
          return;
        }
        const data = event.data || {};
        if (
          data.source === "tungee-session-sync-extension" &&
          data.type === "sync-result" &&
          data.requestId === requestId
        ) {
          if (data.payload?.ok === false) {
            finishFailure(new Error(data.payload?.message || "插件同步失败"));
            return;
          }
          finishSuccess(data.payload || {});
        }
      }
      window.addEventListener("message", handleMessage);
      window.postMessage(
        {
          source: "bussiness-console",
          type: "TUNGEE_PLUGIN_SYNC_REQUEST",
          requestId,
          localApiBase: window.location.origin,
        },
        window.location.origin,
      );
      window.setTimeout(() => finishFailure(new Error("等待插件同步结果超时，请确认浏览器里已打开探迹企业详情页。")), timeoutMs);
    });
  }

  function requestPluginCompanySearch(companyNames, timeoutMs = 60000) {
    return new Promise((resolve, reject) => {
      const requestId = `tungee-plugin-search-${Date.now()}-${Math.random().toString(36).slice(2)}`;
      let settled = false;
      function cleanup() {
        window.removeEventListener("message", handleMessage);
      }
      function finishSuccess(payload) {
        if (settled) {
          return;
        }
        settled = true;
        cleanup();
        resolve(payload);
      }
      function finishFailure(error) {
        if (settled) {
          return;
        }
        settled = true;
        cleanup();
        reject(error);
      }
      function handleMessage(event) {
        if (event.source !== window) {
          return;
        }
        const data = event.data || {};
        if (
          data.source === "tungee-session-sync-extension" &&
          data.type === "search-result" &&
          data.requestId === requestId
        ) {
          if (data.payload?.ok === false) {
            finishFailure(new Error(data.payload?.message || "插件搜索失败"));
            return;
          }
          finishSuccess(data.payload || {});
        }
      }
      window.addEventListener("message", handleMessage);
      window.postMessage(
        {
          source: "bussiness-console",
          type: "TUNGEE_PLUGIN_SEARCH_REQUEST",
          requestId,
          companyNames,
        },
        window.location.origin,
      );
      window.setTimeout(() => finishFailure(new Error("等待插件搜索结果超时，请确认浏览器里已打开探迹企业详情页。")), timeoutMs);
    });
  }

  async function runPluginSync({ auto = false } = {}) {
    if (syncButton) {
      setButtonLoading(syncButton, true, auto ? "自动同步中…" : "同步中…");
    }
    try {
      const ready = await waitForPluginReady(auto ? 1000 : 1800);
      if (!ready) {
        setPluginSyncStatus(
          "未检测到浏览器同步插件",
          "请先在 chrome://extensions 里重新加载仓库内的探迹同步插件，然后硬刷新当前 /console 页面；加载后，打开一个探迹企业详情页，本页会自动或手动触发同步。",
          "bad",
        );
        if (!auto) {
          setFormMessage(messageElement, "未检测到探迹同步插件。请先在 chrome://extensions 里重新加载扩展，再硬刷新当前页面。");
        }
        return;
      }
      setPluginSyncStatus(
        "浏览器同步插件已连接",
        auto ? "正在自动同步当前浏览器里的探迹登录态…" : "正在同步当前浏览器里的探迹登录态…",
        "good",
      );
      const statusPayload = await loadTungeeStatus().catch(() => null);
      if (auto && statusPayload?.connected && statusPayload?.sales_headers_ready) {
        setPluginSyncStatus(
          "浏览器登录状态已同步",
          "当前页面优先使用浏览器的探迹登录状态，无需手动输入探迹账号密码。",
          "good",
        );
        return;
      }
      const payload = await requestPluginSync();
      setPluginSyncStatus(
        "浏览器登录态已同步",
        "当前页面会优先复用浏览器里的探迹登录态，无需再手动输入探迹账号密码。",
        "good",
      );
      setFormMessage(
        messageElement,
        auto ? "已自动从浏览器同步探迹登录态" : "已从浏览器同步探迹登录态",
        "success",
      );
      if (payload?.sales_headers_ready === false) {
        setFormMessage(messageElement, "插件同步完成，但动态请求头仍未补齐，请确认当前浏览器里探迹详情页已正常加载。");
      }
      await reloadConsoleQueryJobs();
    } catch (error) {
      setPluginSyncStatus(
        "浏览器同步失败",
        error.message || "请确认当前浏览器里已经登录探迹，并且至少打开了一个企业详情页。",
        "bad",
      );
      if (!auto) {
        setFormMessage(messageElement, `插件同步失败：${error.message || "未知错误"}`);
      }
    } finally {
      if (syncButton) {
        setButtonLoading(syncButton, false);
      }
    }
  }

  setPluginSyncStatus(
    "优先使用浏览器同步插件",
    "正在检测是否已安装插件；如果插件可用，本页会自动尝试同步浏览器里的探迹登录态。",
    "neutral",
  );
  syncButton?.addEventListener("click", () => runPluginSync({ auto: false }));
  window.setTimeout(() => {
    runPluginSync({ auto: true });
  }, 0);
}

function renderBooleanPill(label, ready, { warn = false } = {}) {
  const tone = ready ? "good" : warn ? "warn" : "bad";
  return `<span class="pill pill--${tone}">${escapeHtml(label)}</span>`;
}

function renderTungeeContextSummary(summary = {}) {
  const sourceLabel = summary.source === "browser_sync" ? "浏览器同步" : "其他来源";
  const currentHeaders = summary.headers?.current || {};
  const searchHeaders = summary.headers?.search || {};
  const cookies = summary.cookies || {};
  const currentHeaderPills = [
    renderBooleanPill(`当前头 PID`, Boolean(currentHeaders["x-tonxis-pid"])),
    renderBooleanPill(`当前头 SID`, Boolean(currentHeaders["x-tonxis-sid"])),
    renderBooleanPill(`当前头 SIGN`, Boolean(currentHeaders["x-tonxis-signature"])),
  ].join("");
  const searchHeaderPills = [
    renderBooleanPill(`搜索头 PID`, Boolean(searchHeaders["x-tonxis-pid"]), { warn: true }),
    renderBooleanPill(`搜索头 SID`, Boolean(searchHeaders["x-tonxis-sid"]), { warn: true }),
    renderBooleanPill(`搜索头 SIGN`, Boolean(searchHeaders["x-tonxis-signature"]), { warn: true }),
  ].join("");
  const cookiePills = [
    renderBooleanPill("搜索Cookie头", Boolean(summary.sales_search_cookie_header_present), { warn: true }),
    renderBooleanPill("accountCenterSessionId", Boolean(cookies.accountCenterSessionId), { warn: true }),
    renderBooleanPill("remember_token", Boolean(cookies.remember_token), { warn: true }),
    renderBooleanPill("CGISessionId", Boolean(cookies.CGISessionId)),
    renderBooleanPill("doncusSessionId", Boolean(cookies.doncusSessionId)),
    renderBooleanPill("_tx_pid", Boolean(cookies._tx_pid)),
    renderBooleanPill("_tx_sid", Boolean(cookies._tx_sid)),
    renderBooleanPill("_tx_cid", Boolean(cookies._tx_cid), { warn: true }),
    renderBooleanPill("_tx_uid", Boolean(cookies._tx_uid), { warn: true }),
    renderBooleanPill("SecurityCenterDuId", Boolean(cookies.SecurityCenterDuId), { warn: true }),
  ].join("");
  return `
    <div class="toolbar-status-details">
      <div class="toolbar-status-detail-row">
        <span class="toolbar-status-detail-label">来源</span>
        <span class="toolbar-status-detail-value">${escapeHtml(sourceLabel)}</span>
      </div>
      <div class="toolbar-status-detail-row">
        <span class="toolbar-status-detail-label">当前请求头</span>
        <div class="toolbar-status-pill-row">${currentHeaderPills}</div>
      </div>
      <div class="toolbar-status-detail-row">
        <span class="toolbar-status-detail-label">搜索请求头</span>
        <div class="toolbar-status-pill-row">${searchHeaderPills}</div>
      </div>
      <div class="toolbar-status-detail-row">
        <span class="toolbar-status-detail-label">关键 Cookie</span>
        <div class="toolbar-status-pill-row">${cookiePills}</div>
      </div>
    </div>
  `;
}

function renderTungeeContextOverview(summary = {}) {
  const sourceLabel = summary.source === "browser_sync" ? "浏览器同步" : "其他来源";
  return `
    <div class="toolbar-status-overview">
      ${renderBooleanPill(sourceLabel, true)}
      ${renderBooleanPill("当前头完整", Boolean(summary.sales_headers_ready))}
      ${renderBooleanPill("搜索头完整", Boolean(summary.sales_search_headers_ready), { warn: true })}
      ${renderBooleanPill("搜索 Cookie", Boolean(summary.sales_search_cookie_header_present), { warn: true })}
    </div>
  `;
}

function openInfoModal({ kicker, title, meta, bodyHtml }) {
  const modal = document.getElementById("detail-modal");
  const kickerNode = document.getElementById("detail-modal-kicker");
  const titleNode = document.getElementById("detail-modal-title");
  const metaNode = document.getElementById("detail-modal-meta");
  const bodyNode = document.getElementById("detail-modal-body");
  if (!modal || !kickerNode || !titleNode || !metaNode || !bodyNode) {
    return;
  }
  modal.dataset.mode = "info";
  kickerNode.textContent = kicker || "详情";
  titleNode.textContent = title || "详情";
  metaNode.textContent = meta || "";
  metaNode.hidden = !meta;
  bodyNode.innerHTML = bodyHtml || "";
  modal.hidden = false;
  document.body.style.overflow = "hidden";
}

function renderTungeeContextModal() {
  if (!latestTungeeStatusPayload) {
    return;
  }
  const payload = latestTungeeStatusPayload;
  const syncAccount = formatTungeeAccountLabel({
    name: getTungeeProfileName(payload.profile),
    mobile: getTungeeProfileMobile(payload.profile) || payload.tungee_mobile,
    fallback: "未识别",
  });
  openInfoModal({
    kicker: "探迹会话",
    title: "浏览器同步详情",
    meta: `状态：${payload.session?.status || "-"} · 来源：${payload.context_summary?.source === "browser_sync" ? "浏览器同步" : "其他"}`,
    bodyHtml: `
      <section class="detail-section">
        <div class="detail-section__header">
          <div>
            <h4 class="detail-section__title">会话摘要</h4>
          </div>
        </div>
        <div class="detail-section__content">
          <div class="detail-note">同步账号：${escapeHtml(syncAccount)}</div>
          <div class="detail-note">过期：${escapeHtml(formatDateTime(payload.session?.expires_at))}</div>
          <div class="detail-note">最近校验：${escapeHtml(formatDateTime(payload.session?.last_verified_at))}</div>
          <div class="detail-note">动态头：${escapeHtml(payload.sales_headers_ready ? "已补齐" : "未补齐")}</div>
        </div>
      </section>
      <section class="detail-section">
        <div class="detail-section__header">
          <div>
            <h4 class="detail-section__title">同步结果</h4>
          </div>
        </div>
        <div class="detail-section__content">
          ${renderTungeeContextSummary(payload.context_summary || {})}
        </div>
      </section>
    `,
  });
}

async function loadTungeeStatus() {
  const container = document.getElementById("tungee-session-status");
  renderStatusLoading(container, "正在校验探迹会话…");
  let payload;
  try {
    payload = await apiFetch("/api/tungee/session/status");
  } catch (error) {
    clearBusyState(container);
    container.innerHTML = `
      <div class="toolbar-status-card">
        <span class="toolbar-status-main status-bad">会话状态加载失败</span>
        <span class="toolbar-status-meta">${escapeHtml(error.message || "请稍后重试")}</span>
      </div>
    `;
    throw error;
  }
  if (!payload.connected) {
    latestTungeeStatusPayload = payload;
    clearBusyState(container);
    container.innerHTML = `
      <div class="toolbar-status-card">
        <span class="toolbar-status-main status-bad">会话不可用</span>
        <span class="toolbar-status-meta">${payload.session?.status === "expired" ? "探迹会话已过期，请重新同步浏览器登录态。" : "当前还没有可用的探迹会话。"}</span>
      </div>
    `;
    setQueryFormEnabled(false, "当前探迹会话不可用，请先同步浏览器里的探迹登录态。");
    return payload;
  }
  if (payload.ok === false) {
    latestTungeeStatusPayload = payload;
    clearBusyState(container);
    container.innerHTML = `
      <div class="toolbar-status-card">
        <span class="toolbar-status-main status-bad">会话校验失败</span>
        <span class="toolbar-status-meta">${payload.message || "当前探迹会话校验失败，请重新同步浏览器登录态。"}</span>
      </div>
    `;
    setQueryFormEnabled(false, payload.message || "当前探迹会话不可用，请先同步浏览器里的探迹登录态。");
    return payload;
  }
  latestTungeeStatusPayload = payload;
  clearBusyState(container);
  const syncAccount = formatTungeeAccountLabel({
    name: getTungeeProfileName(payload.profile),
    mobile: getTungeeProfileMobile(payload.profile) || payload.tungee_mobile,
    fallback: "未识别",
  });
  container.innerHTML = `
    <div class="toolbar-status-card toolbar-status-card--compact toolbar-status-card--inline">
      <span class="toolbar-status-prefix">当前状态：</span>
      <span class="toolbar-status-main status-good">会话可用</span>
      <span class="toolbar-status-divider">|</span>
      <span class="toolbar-status-meta">同步账号：${escapeHtml(syncAccount)}</span>
    </div>
  `;
  setQueryFormEnabled(true);
  return payload;
}

function initTungeeConnectPage() {
  const message = document.getElementById("tungee-login-message");
  const refreshButton = document.getElementById("refresh-session-button");
  const deleteButton = document.getElementById("delete-session-button");

  loadTungeeStatus().catch((error) => {
    document.getElementById("tungee-session-status").innerHTML = `<p class="status-bad">${error.message}</p>`;
  });

  refreshButton?.addEventListener("click", async () => {
    try {
      await withButtonLoading(refreshButton, "刷新中…", () => loadTungeeStatus());
      message.textContent = "已刷新会话状态";
    } catch (error) {
      message.textContent = error.message;
    }
  });

  deleteButton?.addEventListener("click", async () => {
    try {
      await withButtonLoading(deleteButton, "删除中…", () => apiFetch("/api/tungee/session", { method: "DELETE" }));
      message.textContent = "已删除探迹会话";
      await loadTungeeStatus();
    } catch (error) {
      message.textContent = error.message;
    }
  });
  initTungeePluginAutoSync(message);
}

function initHistoryPage() {
  const button = document.getElementById("refresh-history-button");
  const load = () => loadHistoryJobs();
  renderLoadingState(document.getElementById("history-job-list"), "正在加载历史记录…", { cardCount: 2 });
  load();
  button?.addEventListener("click", () => withButtonLoading(button, "刷新中…", load));
}

async function loadAdminSessions() {
  const container = document.getElementById("admin-session-list");
  const payload = await apiFetch("/api/admin/tungee-sessions");
  const sessions = payload.sessions || [];
  if (!sessions.length) {
    renderEmpty(container, "暂无探迹会话。");
    return;
  }
  container.innerHTML = sessions
    .map(
      (session) => `
      <article class="list-card">
        <h3>${session.username}</h3>
        <p class="muted">状态：${session.status}</p>
        <p class="muted">过期：${formatDateTime(session.expires_at)}</p>
        <p class="muted">最近校验：${formatDateTime(session.last_verified_at)}</p>
      </article>
    `,
    )
    .join("");
}

async function loadMoonshotSettingStatus() {
  const statusEl = document.getElementById("moonshot-settings-status");
  if (!statusEl) {
    return;
  }
  setPillState(statusEl, "检测中…", "neutral");
  try {
    const payload = await apiFetch("/api/admin/settings/moonshot");
    setPillState(statusEl, payload.configured ? "已配置" : "未配置", payload.configured ? "good" : "warn");
  } catch (error) {
    setPillState(statusEl, "检测失败", "bad");
    throw error;
  }
}

function initAdminPage() {
  const settingsModal = document.getElementById("admin-settings-modal");
  const settingsForm = document.getElementById("moonshot-settings-form");
  const settingsMessage = document.getElementById("moonshot-settings-message");
  const testButton = document.getElementById("test-moonshot-key-button");
  const apiKeyInput = document.getElementById("moonshot-api-key");
  const submitButton = settingsForm?.querySelector('button[type="submit"]');
  document.querySelectorAll('[data-action="open-admin-settings-modal"]').forEach((button) => {
    button.addEventListener("click", () => {
      setFormMessage(settingsMessage, "");
      setAdminSettingsModalVisible(true);
      apiKeyInput?.focus();
    });
  });
  settingsModal?.querySelectorAll('[data-action="close-admin-settings-modal"]').forEach((button) => {
    button.addEventListener("click", () => {
      setAdminSettingsModalVisible(false);
    });
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && settingsModal && !settingsModal.hidden) {
      setAdminSettingsModalVisible(false);
    }
  });
  const load = async () => {
    try {
      await loadMoonshotSettingStatus();
    } catch (error) {
      setFormMessage(settingsMessage, error.message, "error");
    }
    await loadAdminJobs();
  };
  load().catch((error) => {
    adminJobState.jobs = [];
    adminJobState.total = 0;
    setAdminQueryCount(0);
    renderAdminJobs();
    setFormMessage(settingsMessage, error.message, "error");
  });

  testButton?.addEventListener("click", async () => {
    try {
      const payload = await withButtonLoading(testButton, "测试中…", () =>
        apiFetch("/api/admin/settings/moonshot/test", {
          method: "POST",
          body: JSON.stringify({ api_key: apiKeyInput?.value || "" }),
        }),
      );
      setFormMessage(settingsMessage, `连接测试成功，模型：${payload.result?.model || "-"}`, "success");
    } catch (error) {
      setFormMessage(settingsMessage, error.message, "error");
    }
  });

  settingsForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(settingsForm);
    try {
      await withButtonLoading(submitButton, "保存中…", () =>
        apiFetch("/api/admin/settings/moonshot", {
          method: "POST",
          body: JSON.stringify({ api_key: formData.get("api_key") }),
        }),
      );
      setFormMessage(settingsMessage, "Kimi 配置已保存", "success");
      settingsForm.reset();
      await loadMoonshotSettingStatus();
      adminJobState.page = 1;
      window.setTimeout(() => {
        setAdminSettingsModalVisible(false);
        setFormMessage(settingsMessage, "");
      }, 300);
    } catch (error) {
      setFormMessage(settingsMessage, error.message, "error");
    }
  });
}

function bindTungeeSessionControls(messageId) {
  const message = document.getElementById(messageId) || document.getElementById("tungee-login-message");
  const refreshButton = document.getElementById("refresh-session-button");
  const deleteButton = document.getElementById("delete-session-button");

  refreshButton?.addEventListener("click", async () => {
    try {
      await withButtonLoading(refreshButton, "刷新中…", () => loadTungeeStatus());
      if (message) {
        message.textContent = "已刷新会话状态";
      }
    } catch (error) {
      if (message) {
        message.textContent = error.message;
      }
    }
  });

  deleteButton?.addEventListener("click", async () => {
    try {
      await withButtonLoading(deleteButton, "删除中…", () => apiFetch("/api/tungee/session", { method: "DELETE" }));
      if (message) {
        message.textContent = "已删除探迹会话";
      }
      await reloadConsoleQueryJobs();
    } catch (error) {
      if (message) {
        message.textContent = error.message;
      }
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  switch (window.BUSSINESS_PAGE) {
    case "login":
      initLoginPage();
      break;
    case "admin-gate":
      initAdminGatePage();
      break;
    case "console":
      initConsolePage();
      break;
    case "tungee-connect":
      initTungeeConnectPage();
      break;
    case "history":
      initHistoryPage();
      break;
    case "admin":
      initAdminPage();
      break;
    default:
      break;
  }
});
