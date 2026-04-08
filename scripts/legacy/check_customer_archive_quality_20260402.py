from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
import time
from collections import Counter
from pathlib import Path
from zipfile import BadZipFile

from openpyxl import load_workbook


ROOT = Path.home()
WORKSPACE = Path(__file__).resolve().parents[2]
VAULT = ROOT / "Documents/Obsidian-Codex/潜客池"

PROFILE_XLSX = VAULT / "潜客档案库.xlsx"
MAIN_XLSX = VAULT / "静态潜客主表.xlsx"
L3_DIR = VAULT / "07-L3以上客户档案"

NORMALIZE_SCRIPT = WORKSPACE / "scripts/normalize_customer_fact_fields_20260402.py"

TARGET_LEVELS = {"L1", "L2", "L3"}
FACT_PLACEHOLDER = "待补官网/年报/IR口径"
MARKET_PLACEHOLDER = "待补公司级市场参考"
EVENT_PLACEHOLDER = "待补更强官方披露"


def safe_load_workbook(path: Path, **kwargs):
    last_error = None
    for attempt in range(6):
        try:
            return load_workbook(path, **kwargs)
        except (EOFError, BadZipFile) as exc:
            last_error = exc
            time.sleep(0.5 * (attempt + 1))
    raise last_error


def load_name_filter() -> set[str]:
    raw = os.environ.get("ACCOUNT_NAMES", "").strip()
    file_path = os.environ.get("ACCOUNT_NAMES_FILE", "").strip()
    names: set[str] = set()
    if raw:
        names.update(x.strip() for x in raw.split(",") if x.strip())
    if file_path:
        path = Path(file_path)
        if path.exists():
            payload = json.loads(path.read_text())
            if isinstance(payload, dict):
                items = payload.get("account_names") or payload.get("accounts") or []
            else:
                items = payload
            for item in items:
                if isinstance(item, dict):
                    name = str(item.get("account_canonical_name") or item.get("name") or "").strip()
                else:
                    name = str(item).strip()
                if name:
                    names.add(name)
    return names


def load_normalize_module():
    spec = importlib.util.spec_from_file_location("normalize_customer_fact_fields_20260402", NORMALIZE_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def read_sheet(path: Path, sheet: str):
    wb = safe_load_workbook(path, read_only=True, data_only=True)
    ws = wb[sheet]
    headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
    idx = {h: i for i, h in enumerate(headers)}
    rows = [row for row in ws.iter_rows(min_row=2, values_only=True)]
    return headers, idx, rows


def page_text(path: Path) -> str:
    return path.read_text()


def count_section(files: list[Path], header: str) -> int:
    token = f"\n{header}\n"
    return sum(1 for f in files if token in page_text(f))


def collect_metrics():
    normalize = load_normalize_module()
    name_filter = load_name_filter()
    _, pi, prows = read_sheet(PROFILE_XLSX, "account_profiles")
    l3plus_rows = [
        r
        for r in prows
        if str(r[pi["静态潜客记录成熟度"]] or "") in TARGET_LEVELS
        and (not name_filter or str(r[pi["account_canonical_name"]] or "").strip() in name_filter)
    ]

    expected_file_names = {
        f"{str(r[pi['account_canonical_name']] or '').replace('/', '／').replace(':', '：')}.md"
        for r in l3plus_rows
    }
    files = [f for f in sorted(L3_DIR.rglob("*.md")) if not name_filter or f.name in expected_file_names]

    product_counter = Counter(str(r[pi["公司产品与服务概述"]] or "").strip() for r in l3plus_rows)
    business_counter = Counter(str(r[pi["商业模式概述"]] or "").strip() for r in l3plus_rows)
    customer_counter = Counter(str(r[pi["核心客户客群"]] or "").strip() for r in l3plus_rows)
    sturdiness_counter = Counter(str(r[pi["信息扎实度"]] or "").strip() for r in l3plus_rows)

    high_with_low_facts = []
    per_account = []
    for r in l3plus_rows:
        aid = str(r[pi["account_id"]] or "")
        name = str(r[pi["account_canonical_name"]] or "")
        level = str(r[pi["静态潜客记录成熟度"]] or "")
        sturdiness = str(r[pi["信息扎实度"]] or "")
        fields = {
            "公司产品与服务概述": str(r[pi["公司产品与服务概述"]] or "").strip(),
            "商业模式概述": str(r[pi["商业模式概述"]] or "").strip(),
            "核心客户客群": str(r[pi["核心客户客群"]] or "").strip(),
            "已上线系统概况": str(r[pi["已上线系统概况"]] or "").strip(),
            "数字化项目动态": str(r[pi["数字化项目动态"]] or "").strip(),
            "招聘代表岗位": str(r[pi["招聘代表岗位"]] or "").strip(),
            "近一年重大事件": str(r[pi["近一年重大事件"]] or "").strip(),
        }
        company_fact_count = sum(
            1 for v in fields.values() if not normalize.is_placeholder(v)
        )
        core_fact_count = sum(
            1
            for k in ("公司产品与服务概述", "商业模式概述", "核心客户客群")
            if not normalize.is_placeholder(fields[k])
        )
        if sturdiness in {"高", "中高"} and core_fact_count < 2:
            high_with_low_facts.append(
                {
                    "account_id": aid,
                    "name": name,
                    "level": level,
                    "sturdiness": sturdiness,
                    "core_fact_count": core_fact_count,
                    "company_fact_count": company_fact_count,
                }
            )
        per_account.append(
            {
                "account_id": aid,
                "name": name,
                "level": level,
                "sturdiness": sturdiness,
                "product_ready": not normalize.is_placeholder(fields["公司产品与服务概述"]),
                "business_ready": not normalize.is_placeholder(fields["商业模式概述"]),
                "customer_ready": not normalize.is_placeholder(fields["核心客户客群"]),
                "source_ready": bool(str(r[pi["primary_source_refs"]] or "").strip()),
            }
        )

    generic_market_pages = 0
    generic_assets_pages = 0
    sample_market_lines = []
    for f in files:
        txt = page_text(f)
        if "## 6. 相关资产与状态\n" in txt:
            generic_assets_pages += 1
        m = re.search(r"### 2\.\d+ 市场参考\n(.*?)(?:\n## |\Z)", txt, re.S)
        if m:
            generic_market_pages += 1
            body = m.group(1).strip()
            if len(sample_market_lines) < 5:
                sample_market_lines.append((f.name, body))

    return {
        "l3plus_rows": len(l3plus_rows),
        "archive_files": len(files),
        "product_top": product_counter.most_common(8),
        "business_top": business_counter.most_common(8),
        "customer_top": customer_counter.most_common(8),
        "sturdiness": dict(sturdiness_counter),
        "market_sections": generic_market_pages,
        "asset_sections": generic_assets_pages,
        "high_with_low_facts": high_with_low_facts[:50],
        "high_with_low_facts_count": len(high_with_low_facts),
        "product_placeholder_count": product_counter[FACT_PLACEHOLDER],
        "business_placeholder_count": business_counter[FACT_PLACEHOLDER],
        "customer_placeholder_count": customer_counter[FACT_PLACEHOLDER],
        "sample_market_lines": sample_market_lines,
        "per_account": per_account,
    }


def main():
    normalize = load_normalize_module()
    metrics = collect_metrics()

    findings = []
    if metrics["archive_files"] != metrics["l3plus_rows"]:
        findings.append(f"L3+ 档案文件数({metrics['archive_files']})与档案库主体数({metrics['l3plus_rows']})不一致。")
    if metrics["high_with_low_facts_count"] > 0:
        findings.append(f"仍有 {metrics['high_with_low_facts_count']} 个档案在核心事实字段不足 2 项时被标成 高/中高。")
    if metrics["product_placeholder_count"] > metrics["l3plus_rows"] * 0.3:
        findings.append("公司产品与服务概述占位仍然偏高，说明公司级事实补强仍需继续推进。")
    if metrics["business_placeholder_count"] > metrics["l3plus_rows"] * 0.6:
        findings.append("商业模式概述占位仍然偏高，说明大量页面还未补到公司级经营事实。")
    if metrics["customer_placeholder_count"] > metrics["l3plus_rows"] * 0.6:
        findings.append("核心客户客群占位仍然偏高，说明客户/渠道信息仍明显不足。")
    top_business = metrics["business_top"][0][0] if metrics["business_top"] else ""
    if top_business not in {"", FACT_PLACEHOLDER} and normalize.is_generic_business_text(top_business):
        findings.append("商业模式概述仍有高频通用句，说明模板化经营描述仍未完全收住。")
    top_customer = metrics["customer_top"][0][0] if metrics["customer_top"] else ""
    if top_customer not in {"", FACT_PLACEHOLDER} and normalize.is_generic_customer_text(top_customer):
        findings.append("核心客户客群仍有高频泛化句，说明客户/渠道字段仍在回落到模板写法。")
    if metrics["market_sections"] > metrics["l3plus_rows"] * 0.2:
        findings.append("市场参考区块展示仍然偏多，说明匹配层信息仍在页面中过度外露。")

    report = {
        "summary": {
            "l3plus_rows": metrics["l3plus_rows"],
            "archive_files": metrics["archive_files"],
            "market_sections": metrics["market_sections"],
            "asset_sections": metrics["asset_sections"],
            "sturdiness": metrics["sturdiness"],
        },
        "top_values": {
            "公司产品与服务概述": metrics["product_top"],
            "商业模式概述": metrics["business_top"],
            "核心客户客群": metrics["customer_top"],
        },
        "findings": findings,
        "samples": {
            "high_with_low_facts": metrics["high_with_low_facts"],
            "market_section_samples": metrics["sample_market_lines"],
        },
        "per_account": metrics["per_account"],
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))
    if findings:
        sys.exit(2)


if __name__ == "__main__":
    main()
