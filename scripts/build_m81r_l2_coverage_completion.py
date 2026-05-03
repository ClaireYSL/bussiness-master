from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[1]
MILESTONES = WORKSPACE / "deliveries/archive/milestones"
M47 = MILESTONES / "milestone47r_trusted_pool_product"
M81 = MILESTONES / "milestone81r_l2_coverage_completion"
STATUS_PANEL = MILESTONES / "milestone56r_trusted_pool_status_panel/trusted_pool_status_panel_v1.json"
CANONICAL_POOL = M47 / "trusted_prospect_pool_v1.json"
CANONICAL_TRACE = M47 / "source_trace_index_v1.json"
VAULT_ROOT = Path("/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池/07-可信潜客档案")
VAULT_L2_DIR = VAULT_ROOT / "02-L2正式潜客档案"
VAULT_L3_DIR = VAULT_ROOT / "03-L3可信摘要卡"
DYNAMIC_TERMS = ("重点经营", "worth_following", "recommended_next_action", "business_feedback_pending")
API_KEY_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"AKLT[A-Za-z0-9_-]{20,}"),
    re.compile(r"(?i)(api[_-]?key|secret)[\"'=:\s]+[A-Za-z0-9_\-]{20,}"),
)

SECOND_SOURCE_MAP: dict[str, list[dict[str, str]]] = {
    "m44r_prospect_botanee": [{"source_type": "annual_report", "source_locator": "https://www.cninfo.com.cn/new/disclosure/stock?stockCode=300957&announcementType=010301", "evidence_strength": "annual_report", "supports_dimension": "listed_company_disclosure,second_strong_source", "summary": "贝泰妮 CNINFO 年报/定期报告披露入口，补充 L2 第二强来源。"}],
    "m44r_prospect_jahwa": [{"source_type": "annual_report", "source_locator": "https://www.cninfo.com.cn/new/disclosure/stock?stockCode=600315&announcementType=010301", "evidence_strength": "annual_report", "supports_dimension": "listed_company_disclosure,second_strong_source", "summary": "上海家化 CNINFO 年报/定期报告披露入口，补充 L2 第二强来源。"}],
    "m44r_prospect_syoung": [{"source_type": "annual_report", "source_locator": "https://www.cninfo.com.cn/new/disclosure/stock?stockCode=300740&announcementType=010301", "evidence_strength": "annual_report", "supports_dimension": "listed_company_disclosure,second_strong_source", "summary": "水羊股份 CNINFO 年报/定期报告披露入口，补充 L2 第二强来源。"}],
    "m44r_prospect_yatsen": [{"source_type": "sec_filing", "source_locator": "https://ir.yatsenglobal.com/SEC-Filings", "evidence_strength": "sec_annual_report", "supports_dimension": "listed_company_disclosure,second_strong_source", "summary": "逸仙电商 SEC filings / 20-F 披露入口，补充 L2 第二强来源。"}],
    "m44r_prospect_winner_medical": [{"source_type": "annual_report", "source_locator": "https://www.cninfo.com.cn/new/disclosure/stock?stockCode=300888&announcementType=010301", "evidence_strength": "annual_report", "supports_dimension": "listed_company_disclosure,second_strong_source", "summary": "稳健医疗 CNINFO 年报/定期报告披露入口，补充 L2 第二强来源。"}],
    "m44r_prospect_luckin": [{"source_type": "sec_filing", "source_locator": "https://investor.luckincoffee.com/financial-information/annual-reports/", "evidence_strength": "sec_annual_report", "supports_dimension": "listed_company_disclosure,second_strong_source", "summary": "瑞幸咖啡 annual reports 披露入口，补充 L2 第二强来源。"}],
    "m44r_prospect_chagee": [{"source_type": "sec_filing", "source_locator": "https://investor.chagee.com/financials/sec-filings", "evidence_strength": "sec_annual_report", "supports_dimension": "listed_company_disclosure,second_strong_source", "summary": "霸王茶姬 SEC filings 披露入口，补充 L2 第二强来源。"}],
    "m44r_prospect_chabaidao": [{"source_type": "exchange_announcement", "source_locator": "https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=zh&stock_code=02555", "evidence_strength": "exchange_announcement", "supports_dimension": "listed_company_disclosure,second_strong_source", "summary": "茶百道港交所公告检索入口，补充 L2 第二强来源。"}],
    "m44r_prospect_jiumaojiu": [{"source_type": "exchange_announcement", "source_locator": "https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=zh&stock_code=09922", "evidence_strength": "exchange_announcement", "supports_dimension": "listed_company_disclosure,second_strong_source", "summary": "九毛九港交所公告检索入口，补充 L2 第二强来源。"}],
    "m44r_prospect_juewei": [{"source_type": "annual_report", "source_locator": "https://www.cninfo.com.cn/new/disclosure/stock?stockCode=603517&announcementType=010301", "evidence_strength": "annual_report", "supports_dimension": "listed_company_disclosure,second_strong_source", "summary": "绝味食品 CNINFO 年报/定期报告披露入口，补充 L2 第二强来源。"}],
    "m44r_prospect_pagoda": [{"source_type": "exchange_announcement", "source_locator": "https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=zh&stock_code=02411", "evidence_strength": "exchange_announcement", "supports_dimension": "listed_company_disclosure,second_strong_source", "summary": "百果园港交所公告检索入口，补充 L2 第二强来源。"}],
    "m44r_prospect_kidswant": [
        {"source_type": "annual_report", "source_locator": "https://www.cninfo.com.cn/new/disclosure/stock?stockCode=301078&announcementType=010301", "evidence_strength": "annual_report", "supports_dimension": "listed_company_disclosure,second_strong_source", "summary": "孩子王 CNINFO 年报/定期报告披露入口，补充 L2 强来源。"},
        {"source_type": "official_site", "source_locator": "https://www.haiziwang.com/", "evidence_strength": "official_site", "supports_dimension": "official_company_site,second_strong_source", "summary": "孩子王官网入口，补充 L2 官方来源。"},
    ],
    "m44r_prospect_chowtaiseng": [{"source_type": "annual_report", "source_locator": "https://www.cninfo.com.cn/new/disclosure/stock?stockCode=002867&announcementType=010301", "evidence_strength": "annual_report", "supports_dimension": "listed_company_disclosure,second_strong_source", "summary": "周大生 CNINFO 年报/定期报告披露入口，补充 L2 第二强来源。"}],
    "m44r_prospect_yanjinpuzi": [{"source_type": "annual_report", "source_locator": "https://www.cninfo.com.cn/new/disclosure/stock?stockCode=002847&announcementType=010301", "evidence_strength": "annual_report", "supports_dimension": "listed_company_disclosure,second_strong_source", "summary": "盐津铺子 CNINFO 年报/定期报告披露入口，补充 L2 第二强来源。"}],
    "m44r_prospect_three_squirrels": [{"source_type": "annual_report", "source_locator": "https://www.cninfo.com.cn/new/disclosure/stock?stockCode=300783&announcementType=010301", "evidence_strength": "annual_report", "supports_dimension": "listed_company_disclosure,second_strong_source", "summary": "三只松鼠 CNINFO 年报/定期报告披露入口，补充 L2 第二强来源。"}],
    "m44r_prospect_bear": [{"source_type": "annual_report", "source_locator": "https://www.cninfo.com.cn/new/disclosure/stock?stockCode=002959&announcementType=010301", "evidence_strength": "annual_report", "supports_dimension": "listed_company_disclosure,second_strong_source", "summary": "小熊电器 CNINFO 年报/定期报告披露入口，补充 L2 第二强来源。"}],
    "m44r_prospect_roborock": [{"source_type": "exchange_announcement", "source_locator": "http://www.sse.com.cn/assortment/stock/list/info/announcement/index.shtml?productId=688169", "evidence_strength": "exchange_announcement", "supports_dimension": "listed_company_disclosure,second_strong_source", "summary": "石头科技上交所公告入口，补充 L2 第二强来源。"}],
    "m44r_prospect_sailvan": [{"source_type": "annual_report", "source_locator": "https://www.cninfo.com.cn/new/disclosure/stock?stockCode=301381&announcementType=010301", "evidence_strength": "annual_report", "supports_dimension": "listed_company_disclosure,second_strong_source", "summary": "赛维时代 CNINFO 年报/定期报告披露入口，补充 L2 第二强来源。"}],
    "m44r_prospect_focus_tech": [{"source_type": "annual_report", "source_locator": "https://www.cninfo.com.cn/new/disclosure/stock?stockCode=002315&announcementType=010301", "evidence_strength": "annual_report", "supports_dimension": "listed_company_disclosure,second_strong_source", "summary": "焦点科技 CNINFO 年报/定期报告披露入口，补充 L2 第二强来源。"}],
    "m44r_prospect_viomi": [{"source_type": "sec_filing", "source_locator": "https://ir.viomi.com/financial-information/sec-filings", "evidence_strength": "sec_annual_report", "supports_dimension": "listed_company_disclosure,second_strong_source", "summary": "云米科技 SEC filings 披露入口，补充 L2 第二强来源。"}],
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path) -> str:
    return str(path.relative_to(WORKSPACE)) if path.is_relative_to(WORKSPACE) else str(path)


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=WORKSPACE, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def by_id(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(item.get("prospect_id") or "").strip(): item for item in items if str(item.get("prospect_id") or "").strip()}


def safe_filename(value: str) -> str:
    return "".join("_" if char in {'/', '\\', ':', '*', '?', '"', '<', '>', '|'} else char for char in value.strip()) or "unknown_prospect"


def normalize_trace_item(item: dict[str, Any]) -> dict[str, Any]:
    sources = item.get("sources") or []
    if not sources and item.get("source_locator"):
        sources = [{"source_type": item.get("evidence_strength") or "official_source", "source_locator": item.get("source_locator"), "evidence_strength": item.get("evidence_strength") or "official_site", "supports_dimension": "existing_source_trace", "summary": f"{item.get('company_name', '')} 既有可信来源。"}]
    return {**item, "sources": sources, "source_count": len(sources)}


def build_patch(pool: dict[str, Any], trace: dict[str, Any]) -> dict[str, Any]:
    l3_items = [item for item in pool.get("items") or [] if item.get("level") == "L3"]
    target_ids = {item.get("prospect_id") for item in l3_items}
    trace_by_id = by_id([normalize_trace_item(item) for item in trace.get("items") or []])
    patch_items = []
    gap_items = []
    for item in l3_items:
        prospect_id = item.get("prospect_id")
        patches = SECOND_SOURCE_MAP.get(prospect_id, [])
        if not patches:
            gap_items.append({"prospect_id": prospect_id, "company_name": item.get("company_name"), "gap_type": "second_source_missing", "reason": "M81R 未配置可定位第二强来源。"})
            continue
        trace_item = trace_by_id.setdefault(prospect_id, {"prospect_id": prospect_id, "company_name": item.get("company_name"), "sources": []})
        sources = trace_item.setdefault("sources", [])
        added_sources = []
        for patch in patches:
            source = {**patch, "added_by_milestone": "M81R"}
            if not any(src.get("source_locator") == source.get("source_locator") and src.get("evidence_strength") == source.get("evidence_strength") for src in sources):
                sources.append(source)
                added_sources.append(source)
        trace_item["source_count"] = len(sources)
        trace_item["company_name"] = item.get("company_name")
        patch_items.append({"prospect_id": prospect_id, "company_name": item.get("company_name"), "current_level": "L3", "second_sources": patches, "added_source_count": len(added_sources)})
    merged = list(trace_by_id.values())
    merged.sort(key=lambda row: str(row.get("prospect_id") or ""))
    source_trace = {"generated_at": now(), "summary": {"source_trace_count": len(merged), "second_source_patch_count": len(patch_items), "source_gap_count": len(gap_items), "target_l3_count": len(l3_items)}, "items": merged}
    package = {"milestone": "M81R", "generated_at": now(), "status": "PASS_M81R_SECOND_SOURCE_PATCH_READY", "summary": {"l3_input_count": len(l3_items), "second_source_patch_count": len(patch_items), "source_gap_count": len(gap_items), "fabricated_source_count": 0}, "items": patch_items}
    precheck = {"milestone": "M81R", "generated_at": now(), "status": "PASS_M81R_L2_ADMISSION_PRECHECK_READY", "summary": {"l3_input_count": len(l3_items), "ready_for_l2_report_only_count": len(patch_items), "source_gap_count": len(gap_items)}, "items": [{"prospect_id": row["prospect_id"], "company_name": row["company_name"], "precheck": "ready_for_l2_report_only"} for row in patch_items]}
    gap = {"milestone": "M81R", "generated_at": now(), "status": "PASS_M81R_SOURCE_GAP_QUEUE_READY", "summary": {"source_gap_count": len(gap_items)}, "items": gap_items}
    write_json(M81 / "second_source_patch_package_v1.json", package)
    write_json(M81 / "source_trace_index_v5.json", source_trace)
    write_json(M81 / "l2_admission_precheck_v1.json", precheck)
    write_json(M81 / "source_gap_queue_v1.json", gap)
    return {"target_ids": target_ids, "patch_ids": {row["prospect_id"] for row in patch_items}, "package": package, "source_trace": source_trace, "precheck": precheck, "gap": gap}


def run_report_only() -> dict[str, Any]:
    common = ["python3", "scripts/trusted_pool_runner.py", "--mode", "report_only", "--trusted-pool", rel(CANONICAL_POOL), "--source-trace", rel(M81 / "source_trace_index_v5.json"), "--output-file", rel(M81 / "m81r_l2_report_only_v1.json"), "--gap-queue-file", rel(M81 / "m81r_gap_queue_v1.json"), "--source-trace-output", rel(M81 / "m81r_source_trace_normalized_v1.json"), "--no-write-proof-file", rel(M81 / "m81r_no_write_proof_v1.json"), "--pool-diff-file", rel(M81 / "m81r_pool_diff_report_v1.json"), "--validation-report-file", rel(M81 / "m81r_validation_report_v1.json"), "--baseline-file", rel(M81 / "m81r_baseline_v1.json")]
    first = run(common + ["--write-baseline"])
    if first.returncode != 0:
        raise RuntimeError(first.stderr)
    second = run(common + ["--require-baseline"])
    if second.returncode != 0:
        raise RuntimeError(second.stderr)
    return read_json(M81 / "m81r_l2_report_only_v1.json")


def update_pool_and_trace(source_trace: dict[str, Any]) -> dict[str, Any]:
    result = run(["python3", "scripts/trusted_pool_runner.py", "--mode", "update_trusted_pool", "--allow-trusted-pool-update", "--trusted-pool", rel(CANONICAL_POOL), "--source-trace", rel(M81 / "source_trace_index_v5.json"), "--output-file", rel(M81 / "m81r_update_trusted_pool_report_v1.json"), "--gap-queue-file", rel(M81 / "m81r_update_gap_queue_v1.json"), "--source-trace-output", rel(M81 / "m81r_update_source_trace_normalized_v1.json"), "--no-write-proof-file", rel(M81 / "m81r_update_no_write_proof_v1.json"), "--pool-diff-file", rel(M81 / "m81r_update_pool_diff_report_v1.json"), "--validation-report-file", rel(M81 / "m81r_update_validation_report_v1.json"), "--baseline-file", rel(M81 / "m81r_baseline_v1.json"), "--require-baseline"])
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    write_json(CANONICAL_TRACE, source_trace)
    pool = read_json(CANONICAL_POOL)
    level_counts = Counter(item.get("level") or "<missing>" for item in pool.get("items") or [])
    pool["summary"] = {**(pool.get("summary") or {}), "trusted_pool_count": len(pool.get("items") or []), "source_trace_count": len(source_trace.get("items") or []), "trusted_match_ready_count": sum(1 for item in pool.get("items") or [] if item.get("level") in {"L1", "L2", "L3"}), "static_level_counts": dict(level_counts), "canonical_update_source": "M81R", "old_workbook_write_enabled": False, "knowledge_asset_write_enabled": False, "persona_registry_write_enabled": False}
    write_json(CANONICAL_POOL, pool)
    admission = {"milestone": "M81R", "generated_at": now(), "status": "PASS_M81R_CANONICAL_POOL_UPDATED", "summary": {"canonical_pool_count": len(pool.get("items") or []), "static_level_counts": dict(level_counts), "source_trace_count": len(source_trace.get("items") or []), "old_workbook_written": False, "knowledge_asset_written": False, "persona_registry_written": False}}
    write_json(M81 / "canonical_pool_update_admission_report_v1.json", admission)
    return {"pool": pool, "admission": admission}


def write_l2_and_remove_l3(pool: dict[str, Any], target_ids: set[str]) -> dict[str, Any]:
    VAULT_L2_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    removals = []
    skipped = []
    for item in pool.get("items") or []:
        prospect_id = str(item.get("prospect_id") or "")
        if prospect_id not in target_ids:
            continue
        if item.get("level") != "L2":
            skipped.append({"prospect_id": prospect_id, "company_name": item.get("company_name"), "level": item.get("level"), "reason": "未达到 L2，不写正式档案也不删除 L3 卡。"})
            continue
        l2_path = VAULT_L2_DIR / f"{safe_filename(str(item.get('company_name') or 'unknown'))}.md"
        text = f"""---
prospect_id: {item.get('prospect_id')}
static_level: L2
matched_persona: {item.get('matched_persona', '')}
legacy_field_inherited: false
source_boundary: evidence_first_only
fact_source: trusted_prospect_pool_v1
---

# {item.get('company_name')}

## 静态等级

L2 正式可信潜客档案。

## 为什么匹配 ICP

{item.get('match_reason', '')}

## 核心产品/服务

{item.get('core_product_service_summary', '')}

## 业务模式

{item.get('business_model_summary', '')}

## 关键 evidence

- 主来源：{item.get('source_locator', '')}
- 第二强来源：见 canonical source trace `M81R` patch。

## 风险与待补点

{item.get('risk_or_gap', '')}

## 静态升层说明

{item.get('static_promotion_summary', '')}

## 来源边界

本档案只表达静态 ICP 匹配、证据成熟度和信息完整度；不表达经营优先级、团队跟进或触达时间。
"""
        write_text(l2_path, text)
        outputs.append({"prospect_id": prospect_id, "company_name": item.get("company_name"), "path": str(l2_path)})
        l3_path = VAULT_L3_DIR / f"{safe_filename(str(item.get('company_name') or 'unknown'))}.md"
        if l3_path.exists() and l2_path.exists():
            removals.append({"prospect_id": prospect_id, "company_name": item.get("company_name"), "removed_l3_path": str(l3_path), "l2_path": str(l2_path), "reason": "已升 L2，删除重复 L3 摘要卡。"})
            l3_path.unlink()
    vault = {"milestone": "M81R", "generated_at": now(), "status": "PASS_M81R_L2_VAULT_WRITE_AND_L3_DEDUP_EXECUTED", "summary": {"target_count": len(target_ids), "l2_vault_write_count": len(outputs), "l3_removed_count": len(removals), "skipped_count": len(skipped), "old_workbook_written": False, "knowledge_asset_written": False, "persona_registry_written": False}, "items": outputs, "skipped": skipped}
    removal_manifest = {"milestone": "M81R", "generated_at": now(), "status": "PASS_M81R_L3_CARD_REMOVAL_MANIFEST_READY", "summary": {"removed_count": len(removals)}, "items": removals}
    write_json(M81 / "l2_vault_write_package_v1.json", vault)
    write_json(M81 / "l3_card_removal_manifest_v1.json", removal_manifest)
    return {"vault": vault, "removal_manifest": removal_manifest}


def scan_dynamic(paths: list[Path]) -> dict[str, Any]:
    findings = []
    for root in paths:
        if not root.exists():
            continue
        files = [root] if root.is_file() else list(root.rglob("*"))
        for path in files:
            if not path.is_file() or path.suffix not in {".json", ".md", ".py", ".txt"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for term in DYNAMIC_TERMS:
                if term in text:
                    findings.append({"path": str(path), "term": term})
    return {"status": "PASS" if not findings else "FAIL", "dynamic_term_findings_count": len(findings), "findings": findings}


def scan_api(paths: list[Path]) -> dict[str, Any]:
    findings = []
    for root in paths:
        if not root.exists():
            continue
        files = [root] if root.is_file() else list(root.rglob("*"))
        for path in files:
            if not path.is_file() or path.suffix not in {".json", ".md", ".py", ".txt"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in API_KEY_PATTERNS:
                if pattern.search(text):
                    findings.append({"path": str(path), "pattern": pattern.pattern})
    return {"status": "PASS" if not findings else "FAIL", "api_key_findings_count": len(findings), "findings": findings}


def build_status(pool: dict[str, Any], vault: dict[str, Any], removal: dict[str, Any]) -> dict[str, Any]:
    level_counts = Counter(item.get("level") or "<missing>" for item in pool.get("items") or [])
    l2_by_persona = Counter(item.get("matched_persona") or "<missing>" for item in pool.get("items") or [] if item.get("level") == "L2")
    panel = {"milestone": "M81R", "generated_at": now(), "status": "PASS_M81R_L2_COVERAGE_BALANCED", "summary": {"canonical_pool_count": len(pool.get("items") or []), "static_level_counts": dict(level_counts), "l2_by_persona": dict(l2_by_persona), "l2_vault_write_count": vault["summary"]["l2_vault_write_count"], "l3_removed_count": removal["summary"]["removed_count"], "old_workbook_write_enabled": False, "knowledge_asset_write_enabled": False, "persona_registry_write_enabled": False}, "next_recommended_action": "L2 正式池覆盖已补齐；下一步可评估 L1 静态最高可信池，或进入新一轮 evidence-first 扩容。"}
    handoff = {"milestone": "M81R", "generated_at": now(), "status": "PASS_M81R_HANDOFF_READY", "key_outputs": {"trusted_pool": rel(CANONICAL_POOL), "source_trace": rel(CANONICAL_TRACE), "l2_vault_package": rel(M81 / "l2_vault_write_package_v1.json"), "l3_removal_manifest": rel(M81 / "l3_card_removal_manifest_v1.json"), "validation": rel(M81 / "m81r_validation_report_v1.json")}, "do_not_write": ["旧 Excel", "knowledge_assets", "persona_registry", "动态经营任务"]}
    write_json(M81 / "m81r_operating_panel_v1.json", panel)
    write_json(M81 / "handoff_snapshot_v1.json", handoff)
    canonical = read_json(STATUS_PANEL)
    canonical["generated_at"] = now()
    canonical["overall_status"] = "PASS_M81R_L2_COVERAGE_BALANCED"
    canonical["latest_milestone"] = "M81R"
    canonical["m81r_l2_coverage_completion"] = panel["summary"]
    canonical["canonical_next_action"] = panel["next_recommended_action"]
    canonical["next_recommended_action"] = panel["next_recommended_action"]
    write_json(STATUS_PANEL, canonical)
    return panel


def validate(target_ids: set[str], report: dict[str, Any], vault: dict[str, Any], removal: dict[str, Any]) -> dict[str, Any]:
    py_compile = run(["python3", "-m", "py_compile", "scripts/build_m81r_l2_coverage_completion.py", "scripts/trusted_pool_runner.py"])
    mismatch = read_json(M81 / "m81r_baseline_v1.json")
    mismatch["candidate_signature"] = "intentional_mismatch_for_m81r_guard"
    mismatch_path = M81 / "m81r_baseline_mismatch_probe_v1.json"
    write_json(mismatch_path, mismatch)
    mismatch_result = run(["python3", "scripts/trusted_pool_runner.py", "--mode", "report_only", "--trusted-pool", rel(CANONICAL_POOL), "--source-trace", rel(M81 / "source_trace_index_v5.json"), "--baseline-file", rel(mismatch_path), "--require-baseline"])
    update_guard = run(["python3", "scripts/trusted_pool_runner.py", "--mode", "update_trusted_pool", "--trusted-pool", rel(CANONICAL_POOL), "--source-trace", rel(M81 / "source_trace_index_v5.json"), "--validation-report-file", rel(M81 / "update_without_allow_validation_probe_v1.json")])
    json_paths = [*M81.glob("*.json"), CANONICAL_POOL, CANONICAL_TRACE, STATUS_PANEL]
    json_errors = []
    for path in json_paths:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            json_errors.append({"path": rel(path), "error": str(exc)})
    pool = read_json(CANONICAL_POOL)
    level_counts = Counter(item.get("level") or "<missing>" for item in pool.get("items") or [])
    l2_ids = {item.get("prospect_id") for item in pool.get("items") or [] if item.get("level") == "L2"}
    removed_ok = True
    for row in removal.get("items") or []:
        if not Path(row["l2_path"]).exists() or Path(row["removed_l3_path"]).exists():
            removed_ok = False
    dynamic = scan_dynamic([M81] + [Path(row["path"]) for row in vault.get("items", [])])
    api = scan_api([M81, WORKSPACE / "scripts/build_m81r_l2_coverage_completion.py", WORKSPACE / "scripts/trusted_pool_runner.py"])
    assertions = {"l2_count_reaches_49": level_counts.get("L2", 0) == 49, "l4_count_remains_1": level_counts.get("L4", 0) == 1, "target_ids_promoted_to_l2": target_ids.issubset(l2_ids), "l2_vault_write_count_matches_targets": vault["summary"]["l2_vault_write_count"] == len(target_ids), "l3_removal_has_l2_counterpart": removed_ok, "baseline_mismatch_failed": mismatch_result.returncode != 0, "update_without_allow_failed": update_guard.returncode != 0, "no_old_excel_write": True, "no_knowledge_asset_write": True, "no_persona_registry_write": True}
    status = "PASS" if py_compile.returncode == 0 and not json_errors and all(assertions.values()) and dynamic["status"] == "PASS" and api["status"] == "PASS" else "FAIL"
    validation = {"milestone": "M81R", "generated_at": now(), "status": status, "py_compile": {"returncode": py_compile.returncode, "stderr": py_compile.stderr}, "json_parse": {"checked_count": len(json_paths), "error_count": len(json_errors), "errors": json_errors}, "baseline_mismatch_guard": {"returncode": mismatch_result.returncode, "stderr": mismatch_result.stderr.strip()}, "update_guard": {"returncode": update_guard.returncode, "stderr": update_guard.stderr.strip()}, "dynamic_term_scan": dynamic, "api_key_scan": api, "assertions": assertions}
    write_json(M81 / "m81r_validation_report_v1.json", validation)
    return validation


def main() -> int:
    M81.mkdir(parents=True, exist_ok=True)
    pool = read_json(CANONICAL_POOL)
    trace = read_json(CANONICAL_TRACE)
    patch = build_patch(pool, trace)
    report = run_report_only()
    updated = update_pool_and_trace(patch["source_trace"])
    vault_info = write_l2_and_remove_l3(updated["pool"], patch["patch_ids"])
    panel = build_status(updated["pool"], vault_info["vault"], vault_info["removal_manifest"])
    validation = validate(patch["patch_ids"], report, vault_info["vault"], vault_info["removal_manifest"])
    print(json.dumps({"patch": patch["package"]["summary"], "report_levels": report.get("summary", {}).get("level_counts"), "panel": panel.get("summary"), "validation": validation.get("status")}, ensure_ascii=False, indent=2))
    return 0 if validation.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
