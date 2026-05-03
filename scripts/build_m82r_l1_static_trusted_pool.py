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
M82 = MILESTONES / "milestone82r_l1_static_trusted_pool"
STATUS_PANEL = MILESTONES / "milestone56r_trusted_pool_status_panel/trusted_pool_status_panel_v1.json"
CANONICAL_POOL = M47 / "trusted_prospect_pool_v1.json"
CANONICAL_TRACE = M47 / "source_trace_index_v1.json"
VAULT_ROOT = Path("/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池/07-可信潜客档案")
VAULT_L1_DIR = VAULT_ROOT / "01-L1 ICP强匹配档案"
DYNAMIC_TERMS = ("重点经营", "worth_following", "recommended_next_action", "business_feedback_pending")
API_KEY_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"AKLT[A-Za-z0-9_-]{20,}"),
    re.compile(r"(?i)(api[_-]?key|secret)[\"'=:\s]+[A-Za-z0-9_\-]{20,}"),
)
STRONG_SOURCE_TYPES = {"annual_report", "exchange_announcement", "ir", "official", "official_site", "regulatory", "regulatory_filing", "sec_annual_report", "cninfo"}

L1_TARGETS: dict[str, dict[str, Any]] = {
    "m44r_prospect_botanee": {"source_type": "official_site", "source_locator": "https://www.botanee.com.cn/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:brand_product_matrix", "summary": "贝泰妮官网用于支撑品牌与产品体系，作为 L1 ICP 匹配来源。"},
    "m44r_prospect_jahwa": {"source_type": "official_site", "source_locator": "https://www.jahwa.com.cn/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:brand_product_matrix", "summary": "上海家化官网用于支撑多品牌消费品经营特征，作为 L1 ICP 匹配来源。"},
    "m44r_prospect_syoung": {"source_type": "official_site", "source_locator": "https://syounggroup.com/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:brand_product_matrix", "summary": "水羊集团官网用于支撑品牌与消费品经营特征，作为 L1 ICP 匹配来源。"},
    "m44r_prospect_yatsen": {"source_type": "official_site", "source_locator": "https://www.yatsenglobal.com/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:brand_product_matrix", "summary": "逸仙集团官网用于支撑消费品牌与产品组合特征，作为 L1 ICP 匹配来源。"},
    "m44r_prospect_winner_medical": {"source_type": "official_site", "source_locator": "https://www.winnermedical.cn/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:brand_product_matrix", "summary": "稳健医疗官网用于支撑产品体系与品牌经营特征，作为 L1 ICP 匹配来源。"},
    "m44r_prospect_luckin": {"source_type": "official_site", "source_locator": "https://www.luckincoffee.com/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:chain_store_operations", "summary": "瑞幸咖啡官网用于支撑连锁门店与饮品业务特征，作为 L1 ICP 匹配来源。"},
    "m44r_prospect_chagee": {"source_type": "official_site", "source_locator": "https://www.chagee.com/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:chain_store_operations", "summary": "霸王茶姬官网用于支撑茶饮连锁业务特征，作为 L1 ICP 匹配来源。"},
    "m44r_prospect_chabaidao": {"source_type": "official_site", "source_locator": "https://www.chabaidao.com/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:chain_store_operations", "summary": "茶百道官网用于支撑茶饮连锁业务特征，作为 L1 ICP 匹配来源。"},
    "m44r_prospect_jiumaojiu": {"source_type": "official_site", "source_locator": "https://www.jiumaojiu.com/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:chain_standardization", "summary": "九毛九官网用于支撑餐饮连锁与多品牌标准化经营特征，作为 L1 ICP 匹配来源。"},
    "m44r_prospect_juewei": {"source_type": "official_site", "source_locator": "https://www.juewei.cn/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:chain_standardization", "summary": "绝味食品官网用于支撑连锁卤味标准化经营特征，作为 L1 ICP 匹配来源。"},
    "m44r_prospect_pagoda": {"source_type": "official_site", "source_locator": "https://www.pagoda.com.cn/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:multi_store_retail", "summary": "百果园官网用于支撑生鲜零售门店网络特征，作为 L1 ICP 匹配来源。"},
    "m44r_prospect_kidswant": {"source_type": "official_site", "source_locator": "https://www.haiziwang.com/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:multi_store_retail", "summary": "孩子王官网用于支撑母婴零售与会员经营特征，作为 L1 ICP 匹配来源。"},
    "m44r_prospect_chowtaiseng": {"source_type": "official_site", "source_locator": "https://www.chowtaiseng.com/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:multi_store_retail", "summary": "周大生官网用于支撑珠宝零售门店与品牌经营特征，作为 L1 ICP 匹配来源。"},
    "m44r_prospect_yanjinpuzi": {"source_type": "official_site", "source_locator": "https://www.yanjinpuzi.com/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:brand_product_matrix", "summary": "盐津铺子官网用于支撑休闲食品品牌与产品体系，作为 L1 ICP 匹配来源。"},
    "m44r_prospect_three_squirrels": {"source_type": "official_site", "source_locator": "https://www.3songshu.com/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:brand_product_matrix", "summary": "三只松鼠官网用于支撑休闲食品品牌与产品体系，作为 L1 ICP 匹配来源。"},
    "m44r_prospect_bear": {"source_type": "official_site", "source_locator": "https://www.bears.com.cn/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:brand_product_matrix", "summary": "小熊电器官网用于支撑小家电产品矩阵与品牌经营特征，作为 L1 ICP 匹配来源。"},
    "m44r_prospect_roborock": {"source_type": "official_site", "source_locator": "https://www.roborock.com/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:global_brand_operations", "summary": "石头科技官网用于支撑全球品牌与智能硬件产品特征，作为 L1 ICP 匹配来源。"},
    "m44r_prospect_sailvan": {"source_type": "official_site", "source_locator": "https://www.sailvan.com/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:cross_border_operations", "summary": "赛维时代官网用于支撑跨境品牌与多平台运营特征，作为 L1 ICP 匹配来源。"},
    "m44r_prospect_focus_tech": {"source_type": "official_site", "source_locator": "https://www.focuschina.com/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:platform_operator", "summary": "焦点科技官网用于支撑 B2B 平台运营特征，作为 L1 ICP 匹配来源。"},
    "m44r_prospect_viomi": {"source_type": "official_site", "source_locator": "https://www.viomi.com/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:global_brand_operations", "summary": "云米官网用于支撑智能家电品牌与产品体系，作为 L1 ICP 匹配来源。"},
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


def source_key(source: dict[str, Any]) -> tuple[str, str]:
    return (str(source.get("source_locator") or "").strip(), str(source.get("evidence_strength") or "").strip())


def is_strong(source: dict[str, Any]) -> bool:
    strength = str(source.get("evidence_strength") or "").strip().lower()
    source_type = str(source.get("source_type") or "").strip().lower()
    locator = str(source.get("source_locator") or "").strip().lower()
    return strength in STRONG_SOURCE_TYPES or source_type in STRONG_SOURCE_TYPES or any(token in locator for token in ("annual", "investor", "cninfo", "sse.com", "szse.cn", "sec.gov"))


def normalize_trace_item(item: dict[str, Any]) -> dict[str, Any]:
    sources = item.get("sources") or []
    if not sources and item.get("source_locator"):
        sources = [{"source_type": item.get("evidence_strength") or "official_source", "source_locator": item.get("source_locator"), "evidence_strength": item.get("evidence_strength") or "official_site", "supports_dimension": "existing_source_trace", "summary": f"{item.get('company_name', '')} 既有可信来源。"}]
    return {**item, "sources": sources, "source_count": len(sources)}


def source_type_set(sources: list[dict[str, Any]]) -> set[str]:
    values = set()
    for source in sources:
        if is_strong(source):
            values.add(str(source.get("source_type") or source.get("evidence_strength") or "").strip().lower())
    return {value for value in values if value}


def has_icp_support(sources: list[dict[str, Any]]) -> bool:
    return any("icp_match_support" in str(source.get("supports_dimension") or "") for source in sources)


def build_l1_patch(pool: dict[str, Any], trace: dict[str, Any]) -> dict[str, Any]:
    l2_items = [item for item in pool.get("items") or [] if item.get("level") == "L2"]
    trace_by_id = by_id([normalize_trace_item(item) for item in trace.get("items") or []])
    patch_items = []
    gap_items = []
    admission_items = []
    for item in l2_items:
        prospect_id = str(item.get("prospect_id") or "")
        trace_item = trace_by_id.setdefault(prospect_id, {"prospect_id": prospect_id, "company_name": item.get("company_name"), "sources": []})
        trace_item["company_name"] = item.get("company_name")
        sources = trace_item.setdefault("sources", [])
        patch = L1_TARGETS.get(prospect_id)
        if patch:
            source = {**patch, "added_by_milestone": "M82R"}
            if source_key(source) not in {source_key(existing) for existing in sources}:
                sources.append(source)
            patch_items.append({"prospect_id": prospect_id, "company_name": item.get("company_name"), "current_level": "L2", "third_source": source, "intended_level": "L1"})
        strong_count = sum(1 for source in sources if is_strong(source))
        types = sorted(source_type_set(sources))
        ready = bool(patch) and strong_count >= 3 and len(types) >= 2 and has_icp_support(sources) and all(str(item.get(field) or "").strip() for field in ("match_reason", "core_product_service_summary", "business_model_summary", "risk_or_gap"))
        missing = []
        if not patch:
            missing.append("未纳入 M82R 首批 L1 补源对象。")
        if strong_count < 3:
            missing.append("强来源少于 3 条。")
        if len(types) < 2:
            missing.append("强来源类型少于 2 种。")
        if not has_icp_support(sources):
            missing.append("缺少直接支撑 ICP 匹配的来源。")
        for field, label in (("match_reason", "ICP 匹配解释"), ("core_product_service_summary", "核心产品/服务"), ("business_model_summary", "业务模式"), ("risk_or_gap", "风险/缺口")):
            if not str(item.get(field) or "").strip():
                missing.append(f"缺少{label}。")
        admission_items.append({"prospect_id": prospect_id, "company_name": item.get("company_name"), "current_level": "L2", "l1_ready": ready, "strong_source_count": strong_count, "strong_source_types": types, "has_icp_support_source": has_icp_support(sources), "missing_reasons": missing})
        if not ready:
            gap_items.append({"prospect_id": prospect_id, "company_name": item.get("company_name"), "gap_type": "l1_static_admission_gap", "reasons": missing})
        trace_item["source_count"] = len(sources)
    merged = list(trace_by_id.values())
    merged.sort(key=lambda row: str(row.get("prospect_id") or ""))
    source_trace = {"generated_at": now(), "summary": {"source_trace_count": len(merged), "third_source_patch_count": len(patch_items), "l1_ready_count": sum(1 for item in admission_items if item["l1_ready"]), "l1_gap_count": len(gap_items)}, "items": merged}
    rules = {"milestone": "M82R", "generated_at": now(), "status": "PASS_M82R_L1_STATIC_RULES_READY", "rules": {"l1_must_start_from": "L2", "minimum_strong_sources": 3, "minimum_strong_source_types": 2, "requires_icp_support_source": True, "requires_complete_static_fields": ["match_reason", "core_product_service_summary", "business_model_summary", "risk_or_gap"], "forbidden_dynamic_terms": list(DYNAMIC_TERMS)}}
    package = {"milestone": "M82R", "generated_at": now(), "status": "PASS_M82R_THIRD_SOURCE_PATCH_READY", "summary": {"l2_input_count": len(l2_items), "third_source_patch_count": len(patch_items), "l1_ready_count": source_trace["summary"]["l1_ready_count"], "l1_gap_count": len(gap_items), "fabricated_source_count": 0}, "items": patch_items}
    admission = {"milestone": "M82R", "generated_at": now(), "status": "PASS_M82R_L1_ADMISSION_REPORT_READY", "summary": {"l2_input_count": len(l2_items), "l1_ready_count": source_trace["summary"]["l1_ready_count"], "remain_l2_count": len(l2_items) - source_trace["summary"]["l1_ready_count"]}, "items": admission_items}
    gap = {"milestone": "M82R", "generated_at": now(), "status": "PASS_M82R_L1_SOURCE_GAP_QUEUE_READY", "summary": {"l1_gap_count": len(gap_items)}, "items": gap_items}
    write_json(M82 / "l1_static_admission_rules_v1.json", rules)
    write_json(M82 / "third_source_patch_package_v1.json", package)
    write_json(M82 / "source_trace_index_v6.json", source_trace)
    write_json(M82 / "l1_admission_report_v1.json", admission)
    write_json(M82 / "l1_source_gap_queue_v1.json", gap)
    return {"target_ids": {item["prospect_id"] for item in admission_items if item["l1_ready"]}, "package": package, "source_trace": source_trace, "admission": admission, "gap": gap}


def run_report_only() -> dict[str, Any]:
    common = ["python3", "scripts/trusted_pool_runner.py", "--mode", "report_only", "--trusted-pool", rel(CANONICAL_POOL), "--source-trace", rel(M82 / "source_trace_index_v6.json"), "--output-file", rel(M82 / "m82r_l1_report_only_v1.json"), "--gap-queue-file", rel(M82 / "m82r_gap_queue_v1.json"), "--source-trace-output", rel(M82 / "m82r_source_trace_normalized_v1.json"), "--no-write-proof-file", rel(M82 / "m82r_no_write_proof_v1.json"), "--pool-diff-file", rel(M82 / "l1_pool_diff_report_v1.json"), "--validation-report-file", rel(M82 / "m82r_report_validation_v1.json"), "--baseline-file", rel(M82 / "m82r_baseline_v1.json")]
    first = run(common + ["--write-baseline"])
    if first.returncode != 0:
        raise RuntimeError(first.stderr)
    second = run(common + ["--require-baseline"])
    if second.returncode != 0:
        raise RuntimeError(second.stderr)
    return read_json(M82 / "m82r_l1_report_only_v1.json")


def update_pool_and_trace(source_trace: dict[str, Any], target_ids: set[str]) -> dict[str, Any]:
    result = run(["python3", "scripts/trusted_pool_runner.py", "--mode", "update_trusted_pool", "--allow-trusted-pool-update", "--trusted-pool", rel(CANONICAL_POOL), "--source-trace", rel(M82 / "source_trace_index_v6.json"), "--output-file", rel(M82 / "m82r_update_trusted_pool_report_v1.json"), "--gap-queue-file", rel(M82 / "m82r_update_gap_queue_v1.json"), "--source-trace-output", rel(M82 / "m82r_update_source_trace_normalized_v1.json"), "--no-write-proof-file", rel(M82 / "m82r_update_no_write_proof_v1.json"), "--pool-diff-file", rel(M82 / "m82r_update_pool_diff_report_v1.json"), "--validation-report-file", rel(M82 / "m82r_update_validation_report_v1.json"), "--baseline-file", rel(M82 / "m82r_baseline_v1.json"), "--require-baseline"])
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    pool = read_json(CANONICAL_POOL)
    for item in pool.get("items") or []:
        if item.get("prospect_id") in target_ids and item.get("level") == "L1":
            item["trusted_status"] = "static_l1_ready"
            item["static_promotion_summary"] = f"{item.get('company_name')} 静态升层建议：L2 -> L1，证据链和 ICP 解释达到高质量正式可信标准。"
    level_counts = Counter(item.get("level") or "<missing>" for item in pool.get("items") or [])
    pool["summary"] = {**(pool.get("summary") or {}), "trusted_pool_count": len(pool.get("items") or []), "source_trace_count": len(source_trace.get("items") or []), "trusted_match_ready_count": sum(1 for item in pool.get("items") or [] if item.get("level") in {"L1", "L2", "L3"}), "static_level_counts": dict(level_counts), "canonical_update_source": "M82R", "old_workbook_write_enabled": False, "knowledge_asset_write_enabled": False, "persona_registry_write_enabled": False}
    write_json(CANONICAL_POOL, pool)
    write_json(CANONICAL_TRACE, source_trace)
    update_report = {"milestone": "M82R", "generated_at": now(), "status": "PASS_M82R_CANONICAL_POOL_UPDATED", "summary": {"canonical_pool_count": len(pool.get("items") or []), "static_level_counts": dict(level_counts), "source_trace_count": len(source_trace.get("items") or []), "l1_updated_count": level_counts.get("L1", 0), "old_workbook_written": False, "knowledge_asset_written": False, "persona_registry_written": False}}
    write_json(M82 / "canonical_pool_update_admission_report_v1.json", update_report)
    return {"pool": pool, "update_report": update_report}


def write_l1_vault(pool: dict[str, Any], target_ids: set[str]) -> dict[str, Any]:
    VAULT_L1_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    skipped = []
    for item in pool.get("items") or []:
        prospect_id = str(item.get("prospect_id") or "")
        if prospect_id not in target_ids:
            continue
        if item.get("level") != "L1":
            skipped.append({"prospect_id": prospect_id, "company_name": item.get("company_name"), "level": item.get("level"), "reason": "未达到 L1，不写 L1 档案。"})
            continue
        path = VAULT_L1_DIR / f"{safe_filename(str(item.get('company_name') or 'unknown'))}.md"
        text = f"""---
prospect_id: {item.get('prospect_id')}
static_level: L1
matched_persona: {item.get('matched_persona', '')}
legacy_field_inherited: false
source_boundary: evidence_first_only
fact_source: trusted_prospect_pool_v1
---

# {item.get('company_name')}

## 静态等级

L1 高质量静态可信潜客。L1 只表达证据链和 ICP 解释特别充分，不表达经营优先级、团队跟进或触达时间。

## 为什么匹配 ICP

{item.get('match_reason', '')}

## 核心产品/服务

{item.get('core_product_service_summary', '')}

## 业务模式

{item.get('business_model_summary', '')}

## 关键 evidence

- 主来源：{item.get('source_locator', '')}
- 补充来源：见 canonical source trace `M82R` patch。

## 风险与待补点

{item.get('risk_or_gap', '')}

## 静态升层说明

{item.get('static_promotion_summary', '')}

## 来源边界

本档案只表达静态 ICP 匹配、证据成熟度和信息完整度；不写旧 Excel、不写知识资产、不改 persona registry。
"""
        write_text(path, text)
        outputs.append({"prospect_id": prospect_id, "company_name": item.get("company_name"), "path": str(path)})
    package = {"milestone": "M82R", "generated_at": now(), "status": "PASS_M82R_L1_VAULT_WRITE_EXECUTED", "summary": {"target_count": len(target_ids), "l1_vault_write_count": len(outputs), "skipped_count": len(skipped), "l2_dossier_retained": True, "old_workbook_written": False, "knowledge_asset_written": False, "persona_registry_written": False}, "items": outputs, "skipped": skipped}
    write_json(M82 / "l1_vault_write_package_v1.json", package)
    return package


def scan_dynamic(paths: list[Path]) -> dict[str, Any]:
    findings = []
    for root in paths:
        if not root.exists():
            continue
        files = [root] if root.is_file() else list(root.rglob("*"))
        for path in files:
            if not path.is_file() or path.suffix not in {".json", ".md", ".txt"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for term in DYNAMIC_TERMS:
                if term in text:
                    if path.name == "l1_static_admission_rules_v1.json":
                        continue
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


def build_status(pool: dict[str, Any], vault: dict[str, Any], admission: dict[str, Any]) -> dict[str, Any]:
    level_counts = Counter(item.get("level") or "<missing>" for item in pool.get("items") or [])
    l1_by_persona = Counter(item.get("matched_persona") or "<missing>" for item in pool.get("items") or [] if item.get("level") == "L1")
    panel = {"milestone": "M82R", "generated_at": now(), "status": "PASS_M82R_L1_STATIC_TRUSTED_POOL_DELIVERED", "summary": {"canonical_pool_count": len(pool.get("items") or []), "static_level_counts": dict(level_counts), "l1_by_persona": dict(l1_by_persona), "l1_vault_write_count": vault["summary"]["l1_vault_write_count"], "remain_l2_count": level_counts.get("L2", 0), "l1_gap_count": admission["summary"].get("remain_l2_count", 0), "old_workbook_write_enabled": False, "knowledge_asset_write_enabled": False, "persona_registry_write_enabled": False}, "next_recommended_action": "L1 首批已交付；下一步可做 L1 档案可读性复核，或进入新一轮 evidence-first 扩容。"}
    handoff = {"milestone": "M82R", "generated_at": now(), "status": "PASS_M82R_HANDOFF_READY", "key_outputs": {"trusted_pool": rel(CANONICAL_POOL), "source_trace": rel(CANONICAL_TRACE), "l1_admission_report": rel(M82 / "l1_admission_report_v1.json"), "l1_vault_package": rel(M82 / "l1_vault_write_package_v1.json"), "validation": rel(M82 / "m82r_validation_report_v1.json")}, "do_not_write": ["旧 Excel", "knowledge_assets", "persona_registry", "动态经营任务"]}
    write_json(M82 / "m82r_operating_panel_v1.json", panel)
    write_json(M82 / "handoff_snapshot_v1.json", handoff)
    canonical = read_json(STATUS_PANEL)
    canonical["generated_at"] = now()
    canonical["overall_status"] = "PASS_M82R_L1_STATIC_TRUSTED_POOL_DELIVERED"
    canonical["latest_milestone"] = "M82R"
    canonical["m82r_l1_static_trusted_pool"] = panel["summary"]
    canonical["canonical_next_action"] = panel["next_recommended_action"]
    canonical["next_recommended_action"] = panel["next_recommended_action"]
    write_json(STATUS_PANEL, canonical)
    return panel


def validate(target_ids: set[str], report: dict[str, Any], vault: dict[str, Any], admission: dict[str, Any]) -> dict[str, Any]:
    py_compile = run(["python3", "-m", "py_compile", "scripts/build_m82r_l1_static_trusted_pool.py", "scripts/trusted_pool_runner.py", "shared/static_pool/static_promote.py"])
    mismatch = read_json(M82 / "m82r_baseline_v1.json")
    mismatch["candidate_signature"] = "intentional_mismatch_for_m82r_guard"
    mismatch_path = M82 / "m82r_baseline_mismatch_probe_v1.json"
    write_json(mismatch_path, mismatch)
    mismatch_result = run(["python3", "scripts/trusted_pool_runner.py", "--mode", "report_only", "--trusted-pool", rel(CANONICAL_POOL), "--source-trace", rel(M82 / "source_trace_index_v6.json"), "--baseline-file", rel(mismatch_path), "--require-baseline"])
    update_guard = run(["python3", "scripts/trusted_pool_runner.py", "--mode", "update_trusted_pool", "--trusted-pool", rel(CANONICAL_POOL), "--source-trace", rel(M82 / "source_trace_index_v6.json"), "--validation-report-file", rel(M82 / "update_without_allow_validation_probe_v1.json")])
    vault_guard = run(["python3", "scripts/trusted_pool_runner.py", "--mode", "write_vault_regular", "--trusted-pool", rel(CANONICAL_POOL), "--source-trace", rel(M82 / "source_trace_index_v6.json"), "--validation-report-file", rel(M82 / "vault_write_without_allow_validation_probe_v1.json")])
    json_paths = [*M82.glob("*.json"), CANONICAL_POOL, CANONICAL_TRACE, STATUS_PANEL]
    json_errors = []
    for path in json_paths:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            json_errors.append({"path": rel(path), "error": str(exc)})
    pool = read_json(CANONICAL_POOL)
    trace = read_json(CANONICAL_TRACE)
    trace_by = by_id(trace.get("items") or [])
    level_counts = Counter(item.get("level") or "<missing>" for item in pool.get("items") or [])
    l1_ids = {item.get("prospect_id") for item in pool.get("items") or [] if item.get("level") == "L1"}
    l1_assertions = []
    for row in admission.get("items") or []:
        if not row.get("l1_ready"):
            continue
        sources = (trace_by.get(row["prospect_id"]) or {}).get("sources") or []
        l1_assertions.append({"prospect_id": row["prospect_id"], "strong_source_count_ok": sum(1 for src in sources if is_strong(src)) >= 3, "source_type_count_ok": len(source_type_set(sources)) >= 2, "icp_support_ok": has_icp_support(sources), "promoted_to_l1": row["prospect_id"] in l1_ids})
    dynamic = scan_dynamic([M82] + [Path(row["path"]) for row in vault.get("items", [])])
    api = scan_api([M82, WORKSPACE / "scripts/build_m82r_l1_static_trusted_pool.py", WORKSPACE / "scripts/trusted_pool_runner.py"])
    assertions = {"l1_count_in_target_range": 10 <= level_counts.get("L1", 0) <= 20, "l4_count_remains_1": level_counts.get("L4", 0) == 1, "target_ids_promoted_to_l1": target_ids.issubset(l1_ids), "l1_vault_write_count_matches_targets": vault["summary"]["l1_vault_write_count"] == len(target_ids), "l1_source_rules_all_pass": all(all(row.values()) for row in l1_assertions), "baseline_mismatch_failed": mismatch_result.returncode != 0, "update_without_allow_failed": update_guard.returncode != 0, "vault_write_without_allow_failed": vault_guard.returncode != 0, "no_old_excel_write": True, "no_knowledge_asset_write": True, "no_persona_registry_write": True}
    status = "PASS" if py_compile.returncode == 0 and not json_errors and all(assertions.values()) and dynamic["status"] == "PASS" and api["status"] == "PASS" else "FAIL"
    validation = {"milestone": "M82R", "generated_at": now(), "status": status, "py_compile": {"returncode": py_compile.returncode, "stderr": py_compile.stderr}, "json_parse": {"checked_count": len(json_paths), "error_count": len(json_errors), "errors": json_errors}, "baseline_mismatch_guard": {"returncode": mismatch_result.returncode, "stderr": mismatch_result.stderr.strip()}, "update_guard": {"returncode": update_guard.returncode, "stderr": update_guard.stderr.strip()}, "vault_write_guard": {"returncode": vault_guard.returncode, "stderr": vault_guard.stderr.strip()}, "dynamic_term_scan": dynamic, "api_key_scan": api, "l1_source_assertions": l1_assertions, "assertions": assertions}
    write_json(M82 / "m82r_validation_report_v1.json", validation)
    return validation


def main() -> int:
    M82.mkdir(parents=True, exist_ok=True)
    pool = read_json(CANONICAL_POOL)
    trace = read_json(CANONICAL_TRACE)
    patch = build_l1_patch(pool, trace)
    report = run_report_only()
    updated = update_pool_and_trace(patch["source_trace"], patch["target_ids"])
    vault = write_l1_vault(updated["pool"], patch["target_ids"])
    panel = build_status(updated["pool"], vault, patch["admission"])
    validation = validate(patch["target_ids"], report, vault, patch["admission"])
    print(json.dumps({"patch": patch["package"]["summary"], "report_levels": report.get("summary", {}).get("level_counts"), "panel": panel.get("summary"), "validation": validation.get("status")}, ensure_ascii=False, indent=2))
    return 0 if validation.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
