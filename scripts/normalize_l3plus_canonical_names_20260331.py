from __future__ import annotations

import re
import signal
import os
from pathlib import Path

import akshare as ak
from openpyxl import load_workbook


TODAY = "2026-03-31"
ROOT = Path("/Users/clairaipartner")
WORKSPACE = ROOT / ".openclaw/workspace-main/bussiness-master"
VAULT = ROOT / "Documents/Obsidian-Codex/潜客池"

MAIN_XLSX = VAULT / "静态潜客主表.xlsx"
PROFILE_XLSX = VAULT / "潜客档案库.xlsx"
MEMORY_PATH = WORKSPACE / "memory/2026-03-31.md"

CODE_PAT_AID = re.compile(r"acc_(?:cn_)?(\d{6})$")
CODE_PAT_REF = re.compile(r"(?:sz|sh|bj)(\d{6})", re.I)
FULL_NAME_TOKENS = ("股份有限公司", "有限公司", "有限责任公司")
REQUEST_TIMEOUT = 8
MAX_ITEMS = int(os.environ.get("MAX_ITEMS", "25"))


class FetchTimeout(Exception):
    pass


def _timeout_handler(signum, frame):
    raise FetchTimeout("cninfo fetch timeout")


def is_full_name(name: str) -> bool:
    return any(token in name for token in FULL_NAME_TOKENS)


def extract_code(account_id: str, refs: str) -> str | None:
    match = CODE_PAT_AID.search(account_id)
    if match:
        return match.group(1)
    match = CODE_PAT_REF.search(refs or "")
    if match:
        return match.group(1)
    return None


def fetch_company_name(code: str) -> str | None:
    try:
        signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(REQUEST_TIMEOUT)
        df = ak.stock_profile_cninfo(symbol=code)
        signal.alarm(0)
    except Exception:
        signal.alarm(0)
        return None
    if df is None or df.empty:
        return None
    name = str(df.iloc[0].get("公司名称") or "").strip()
    return name or None


def main() -> None:
    main_wb = load_workbook(MAIN_XLSX)
    main_ws = main_wb["accounts_main"]
    mh = [c.value for c in main_ws[1]]
    mi = {h: i + 1 for i, h in enumerate(mh)}

    profile_wb = load_workbook(PROFILE_XLSX)
    profile_ws = profile_wb["account_profiles"]
    ph = [c.value for c in profile_ws[1]]
    pi = {h: i + 1 for i, h in enumerate(ph)}

    main_rows = {}
    for r in range(2, main_ws.max_row + 1):
        aid = str(main_ws.cell(r, mi["account_id"]).value or "")
        if aid:
            main_rows[aid] = r

    updated = []
    unresolved = []

    candidates = []
    for r in range(2, profile_ws.max_row + 1):
        aid = str(profile_ws.cell(r, pi["account_id"]).value or "")
        level = str(profile_ws.cell(r, pi["静态潜客记录成熟度"]).value or "")
        name = str(profile_ws.cell(r, pi["account_canonical_name"]).value or "").strip()
        refs = str(profile_ws.cell(r, pi["primary_source_refs"]).value or "")
        if level not in ("L1", "L2", "L3"):
            continue
        if not name or is_full_name(name):
            continue

        code = extract_code(aid, refs)
        if not code:
            unresolved.append((aid, name, "no_code"))
            continue
        candidates.append((r, aid, level, name, refs, code))

    for r, aid, level, name, refs, code in candidates[:MAX_ITEMS]:
        company_name = fetch_company_name(code)
        if not company_name:
            unresolved.append((aid, name, f"fetch_failed:{code}"))
            continue
        if company_name == name:
            continue

        profile_ws.cell(r, pi["account_canonical_name"]).value = company_name
        profile_ws.cell(r, pi["last_profiled_at"]).value = TODAY
        validation_gap = str(profile_ws.cell(r, pi["validation_gap"]).value or "")
        if "公司全称已按上市公司基础资料统一校正" not in validation_gap:
            gap_prefix = "公司全称已按上市公司基础资料统一校正。"
            profile_ws.cell(r, pi["validation_gap"]).value = (
                f"{gap_prefix}{validation_gap}" if validation_gap else gap_prefix
            )

        mr = main_rows.get(aid)
        if mr:
            main_ws.cell(mr, mi["account_canonical_name"]).value = company_name
            if "validation_gap" in mi:
                validation_gap_main = str(main_ws.cell(mr, mi["validation_gap"]).value or "")
                if "公司全称已按上市公司基础资料统一校正" not in validation_gap_main:
                    gap_prefix = "公司全称已按上市公司基础资料统一校正。"
                    main_ws.cell(mr, mi["validation_gap"]).value = (
                        f"{gap_prefix}{validation_gap_main}" if validation_gap_main else gap_prefix
                    )

        updated.append((aid, name, company_name, code))

    main_wb.save(MAIN_XLSX)
    profile_wb.save(PROFILE_XLSX)

    with MEMORY_PATH.open("a", encoding="utf-8") as f:
        f.write(
            f"\n- 对 `L3+` 客户档案名称做了一轮公司全称标准化，成功校正 `{len(updated)}` 个简称主体；仍有 `{len(unresolved)}` 个对象暂未能自动反查全称。\n"
        )

    print(
        {
            "candidate_total": len(candidates),
            "batch_target": min(len(candidates), MAX_ITEMS),
            "updated": len(updated),
            "unresolved": len(unresolved),
            "sample_updated": updated[:20],
            "sample_unresolved": unresolved[:20],
        }
    )


if __name__ == "__main__":
    main()
