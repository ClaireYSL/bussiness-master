const DEFAULT_LOCAL_API_BASE = "http://127.0.0.1:8000";
const STORAGE_KEY = "tungee_sync.local_api_base";
const STATUS_BOX = document.getElementById("status-box");
const ACTIVE_TAB_INFO = document.getElementById("active-tab-info");
const LOCAL_API_BASE_INPUT = document.getElementById("local-api-base");
const SYNC_BUTTON = document.getElementById("sync-button");
const OPEN_CONSOLE_BUTTON = document.getElementById("open-console-button");

function setStatus(lines) {
  STATUS_BOX.textContent = Array.isArray(lines) ? lines.join("\n") : String(lines || "");
}

function appendStatus(line) {
  const current = STATUS_BOX.textContent ? `${STATUS_BOX.textContent}\n` : "";
  STATUS_BOX.textContent = `${current}${line}`;
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

async function getActiveTab() {
  const tabs = await promisifyChrome(chrome.tabs.query, { active: true, currentWindow: true });
  return tabs[0] || null;
}

function parseEnterpriseId(url) {
  const match = String(url || "").match(/\/enterprise-details\/([^/]+)\//);
  return match ? match[1] : null;
}

async function loadLocalApiBase() {
  const payload = await promisifyChrome(chrome.storage.local.get, [STORAGE_KEY]);
  return payload?.[STORAGE_KEY] || DEFAULT_LOCAL_API_BASE;
}

async function saveLocalApiBase(value) {
  await promisifyChrome(chrome.storage.local.set, { [STORAGE_KEY]: value });
}

async function refreshActiveTabInfo() {
  const activeTab = await getActiveTab();
  if (!activeTab?.url) {
    ACTIVE_TAB_INFO.textContent = "未找到当前标签页。";
    return;
  }
  const enterpriseId = parseEnterpriseId(activeTab.url);
  ACTIVE_TAB_INFO.textContent = enterpriseId
    ? `当前页已就绪：${enterpriseId}`
    : "当前页不是探迹企业详情页，请先打开 sales.tungee.com 的企业详情页。";
}

async function syncContext() {
  const localApiBase = String(LOCAL_API_BASE_INPUT.value || "").trim() || DEFAULT_LOCAL_API_BASE;
  await saveLocalApiBase(localApiBase);

  const activeTab = await getActiveTab();
  appendStatus(`本地 API：${localApiBase}`);
  appendStatus(`当前标签页：${activeTab?.url || "未找到"}`);

  const response = await sendRuntimeMessage({
    type: "syncCurrentTungeeContext",
    localApiBase,
    preferredTabId: activeTab?.id || null,
  });

  if (!response?.ok) {
    throw new Error(response?.message || "同步失败");
  }

  appendStatus(`同步完成：${response.sales_tab_url || "-"}`);
  appendStatus(`动态头状态：${response.sales_headers_ready ? "已补齐" : "未补齐"}`);
}

document.addEventListener("DOMContentLoaded", async () => {
  try {
    LOCAL_API_BASE_INPUT.value = await loadLocalApiBase();
    await refreshActiveTabInfo();
    setStatus("等待开始…");
  } catch (error) {
    setStatus(`初始化失败：${String(error)}`);
  }
});

SYNC_BUTTON.addEventListener("click", async () => {
  SYNC_BUTTON.disabled = true;
  setStatus("开始同步…");
  try {
    await syncContext();
  } catch (error) {
    appendStatus(`失败：${String(error.message || error)}`);
  } finally {
    SYNC_BUTTON.disabled = false;
  }
});

OPEN_CONSOLE_BUTTON.addEventListener("click", async () => {
  const localApiBase = String(LOCAL_API_BASE_INPUT.value || "").trim() || DEFAULT_LOCAL_API_BASE;
  await saveLocalApiBase(localApiBase);
  chrome.tabs.create({ url: `${localApiBase.replace(/\/$/, "")}/console` });
});
