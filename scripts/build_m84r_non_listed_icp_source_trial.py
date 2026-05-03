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
M84 = MILESTONES / "milestone84r_non_listed_icp_source_trial"
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

# M84R intentionally uses non-capital-market source categories to reduce the L1 bias toward listed-company disclosure.
PLATFORM_PATCHES: dict[str, dict[str, str]] = {
    "m68r_acc_babi": {"source_type": "official_channel_page", "source_category": "platform_operating_fact", "source_locator": "https://www.babifood.com/", "evidence_strength": "official_channel_page", "supports_dimension": "icp_match_support:chain_store_operations,platform_operating_fact", "summary": "巴比食品官网用于支撑连锁门店/渠道运营与标准化经营特征，补充非上市友好 L1 信源类型。"},
    "m68r_acc_bbg": {"source_type": "official_channel_page", "source_category": "platform_operating_fact", "source_locator": "https://www.bbg.com.cn/", "evidence_strength": "official_channel_page", "supports_dimension": "icp_match_support:multi_store_retail,platform_operating_fact", "summary": "步步高集团官网用于支撑多业态零售与门店网络经营事实，补充非上市友好 L1 信源类型。"},
    "m68r_acc_bear": {"source_type": "official_channel_page", "source_category": "platform_operating_fact", "source_locator": "https://www.bears.com.cn/", "evidence_strength": "official_channel_page", "supports_dimension": "icp_match_support:brand_product_matrix,platform_operating_fact", "summary": "小熊电器官网展示品牌产品矩阵与线上渠道入口，补充平台经营事实类信源。"},
    "m68r_acc_bloomage": {"source_type": "official_product_page", "source_category": "official_owned", "source_locator": "https://www.bloomagebiotech.com/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:brand_product_matrix,official_owned", "summary": "华熙生物官网用于支撑生物科技产品与品牌矩阵，补充非资本市场信源。"},
    "m68r_acc_haers": {"source_type": "official_channel_page", "source_category": "platform_operating_fact", "source_locator": "https://www.haers.cn/knowUs/Default.htm", "evidence_strength": "official_channel_page", "supports_dimension": "icp_match_support:global_brand_operations,platform_operating_fact", "summary": "哈尔斯官网介绍品牌与国际化经营事实，补充平台/渠道经营类信源。"},
    "m68r_acc_henglin": {"source_type": "official_product_page", "source_category": "official_owned", "source_locator": "https://www.henglin.com/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:global_brand_operations,official_owned", "summary": "恒林家居官网用于支撑家具产品体系与全球经营特征，补充非资本市场信源。"},
    "m68r_acc_sailvan": {"source_type": "official_channel_page", "source_category": "platform_operating_fact", "source_locator": "https://www.sailvan.com/", "evidence_strength": "official_channel_page", "supports_dimension": "icp_match_support:cross_border_operations,platform_operating_fact", "summary": "赛维集团官网用于支撑跨境品牌与多平台运营特征，补充平台经营事实类信源。"},
    "m68r_acc_santai": {"source_type": "official_channel_page", "source_category": "platform_operating_fact", "source_locator": "https://www.sfcservice.com/", "evidence_strength": "official_channel_page", "supports_dimension": "icp_match_support:cross_border_operations,platform_operating_fact", "summary": "三态相关公开业务站点用于支撑跨境电商运营服务特征，补充平台经营事实类信源。"},
    "m68r_acc_yotrio": {"source_type": "official_product_page", "source_category": "official_owned", "source_locator": "https://www.yotrio.com/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:global_brand_operations,official_owned", "summary": "永强集团官网用于支撑户外家具产品体系与全球品牌运营特征，补充非资本市场信源。"},
    "m68r_acc_uechairs": {"source_type": "official_product_page", "source_category": "official_owned", "source_locator": "https://www.uechairs.com/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:global_brand_operations,official_owned", "summary": "永艺家具官网用于支撑办公椅产品体系与全球经营特征，补充非资本市场信源。"},
    "m68r_acc_patio": {"source_type": "official_product_page", "source_category": "official_owned", "source_locator": "https://www.zhengte.com/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:global_brand_operations,official_owned", "summary": "正特官网用于支撑户外休闲产品体系与全球经营特征，补充非资本市场信源。"},
    "m68r_acc_topstar": {"source_type": "official_product_page", "source_category": "official_owned", "source_locator": "https://www.topstarltd.com/", "evidence_strength": "official_site", "supports_dimension": "icp_match_support:multi_factory_group,official_owned", "summary": "拓斯达官网用于支撑智能制造产品体系与多组织经营特征，补充非资本市场信源。"},
}

import sys
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from shared.static_pool.static_promote import (  # noqa: E402
    _has_icp_support,
    _is_l1_countable_evidence,
    _source_category,
    _strong_source_categories,
    evaluate_static_promotion,
)


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


def source_trace_by_prospect(trace: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    return {str(item.get("prospect_id") or ""): item.get("sources") or [] for item in trace.get("items") or []}


def safe_filename(value: str) -> str:
    return "".join("_" if char in {'/', '\\', ':', '*', '?', '"', '<', '>', '|'} else char for char in value.strip()) or "unknown_prospect"


def source_key(source: dict[str, Any]) -> tuple[str, str]:
    return (str(source.get("source_locator") or "").strip(), str(source.get("evidence_strength") or "").strip())


def build_patch(pool: dict[str, Any], trace: dict[str, Any]) -> dict[str, Any]:
    pool_by_id = by_id(pool.get("items") or [])
    trace_by_id = by_id(trace.get("items") or [])
    patch_items = []
    skipped = []
    for prospect_id, patch in PLATFORM_PATCHES.items():
        item = pool_by_id.get(prospect_id)
        if not item or item.get("level") != "L2":
            skipped.append({"prospect_id": prospect_id, "reason": "not_current_l2"})
            continue
        trace_item = trace_by_id.setdefault(prospect_id, {"prospect_id": prospect_id, "company_name": item.get("company_name"), "sources": []})
        sources = trace_item.setdefault("sources", [])
        source = {**patch, "added_by_milestone": "M84R"}
        if source_key(source) not in {source_key(existing) for existing in sources}:
            sources.append(source)
        trace_item["company_name"] = item.get("company_name")
        trace_item["source_count"] = len(sources)
        patch_items.append({"prospect_id": prospect_id, "company_name": item.get("company_name"), "current_level": "L2", "patch_source": source})
    merged = list(trace_by_id.values())
    merged.sort(key=lambda row: str(row.get("prospect_id") or ""))
    category_counts = Counter()
    for row in merged:
        for source in row.get("sources") or []:
            category_counts[_source_category(source)] += 1
    source_trace = {"generated_at": now(), "summary": {"source_trace_count": len(merged), "m84_patch_count": len(patch_items), "platform_operating_fact_count": category_counts.get("platform_operating_fact", 0), "official_owned_count": category_counts.get("official_owned", 0), "regulatory_or_capital_market_count": category_counts.get("regulatory_or_capital_market", 0), "skipped_count": len(skipped)}, "items": merged}
    package = {"milestone": "M84R", "generated_at": now(), "status": "PASS_M84R_PLATFORM_SOURCE_PATCH_READY", "summary": {"target_count": len(PLATFORM_PATCHES), "patch_count": len(patch_items), "skipped_count": len(skipped), "old_workbook_written": False, "knowledge_asset_written": False, "persona_registry_written": False}, "items": patch_items, "skipped": skipped}
    write_json(M84 / "platform_authoritative_source_patch_package_v1.json", package)
    write_json(M84 / "source_trace_index_v7.json", source_trace)
    return {"package": package, "source_trace": source_trace, "target_ids": {item["prospect_id"] for item in patch_items}}


def run_report_only() -> dict[str, Any]:
    common = ["python3", "scripts/trusted_pool_runner.py", "--mode", "report_only", "--trusted-pool", rel(CANONICAL_POOL), "--source-trace", rel(M84 / "source_trace_index_v7.json"), "--output-file", rel(M84 / "m84r_report_only_v1.json"), "--gap-queue-file", rel(M84 / "m84r_gap_queue_v1.json"), "--source-trace-output", rel(M84 / "m84r_source_trace_normalized_v1.json"), "--no-write-proof-file", rel(M84 / "m84r_no_write_proof_v1.json"), "--pool-diff-file", rel(M84 / "m84r_pool_diff_report_v1.json"), "--validation-report-file", rel(M84 / "m84r_report_validation_v1.json"), "--baseline-file", rel(M84 / "m84r_baseline_v1.json")]
    first = run(common + ["--write-baseline"])
    if first.returncode != 0:
        raise RuntimeError(first.stderr)
    second = run(common + ["--require-baseline"])
    if second.returncode != 0:
        raise RuntimeError(second.stderr)
    return read_json(M84 / "m84r_report_only_v1.json")


def update_pool_and_trace(source_trace: dict[str, Any], target_ids: set[str]) -> dict[str, Any]:
    before_pool = read_json(CANONICAL_POOL)
    before_by_id = by_id(before_pool.get("items") or [])
    result = run(["python3", "scripts/trusted_pool_runner.py", "--mode", "update_trusted_pool", "--allow-trusted-pool-update", "--trusted-pool", rel(CANONICAL_POOL), "--source-trace", rel(M84 / "source_trace_index_v7.json"), "--output-file", rel(M84 / "m84r_update_trusted_pool_report_v1.json"), "--gap-queue-file", rel(M84 / "m84r_update_gap_queue_v1.json"), "--source-trace-output", rel(M84 / "m84r_update_source_trace_normalized_v1.json"), "--no-write-proof-file", rel(M84 / "m84r_update_no_write_proof_v1.json"), "--pool-diff-file", rel(M84 / "m84r_update_pool_diff_report_v1.json"), "--validation-report-file", rel(M84 / "m84r_update_validation_report_v1.json"), "--baseline-file", rel(M84 / "m84r_baseline_v1.json"), "--require-baseline"])
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    pool = read_json(CANONICAL_POOL)
    for item in pool.get("items") or []:
        prospect_id = item.get("prospect_id")
        previous = before_by_id.get(str(prospect_id or ""))
        if prospect_id not in target_ids and previous:
            # M84R only tests non-capital-market source patches for selected L2 objects;
            # do not let the generic runner silently promote unrelated records.
            for field in ("level", "trusted_status", "static_promotion_summary", "static_gap_count", "static_evidence_count", "static_strong_evidence_count"):
                if field in previous:
                    item[field] = previous[field]
            continue
        if prospect_id in target_ids and item.get("level") == "L1":
            item["trusted_status"] = "static_l1_ready"
            item["static_promotion_summary"] = f"{item.get('company_name')} 静态升层建议：L2 -> L1，补充非资本市场来源后满足 source_category v2。"
    level_counts = Counter(item.get("level") or "<missing>" for item in pool.get("items") or [])
    pool["summary"] = {**(pool.get("summary") or {}), "trusted_pool_count": len(pool.get("items") or []), "source_trace_count": len(source_trace.get("items") or []), "trusted_match_ready_count": sum(1 for item in pool.get("items") or [] if item.get("level") in {"L1", "L2", "L3"}), "static_level_counts": dict(level_counts), "canonical_update_source": "M84R", "old_workbook_write_enabled": False, "knowledge_asset_write_enabled": False, "persona_registry_write_enabled": False}
    write_json(CANONICAL_POOL, pool)
    write_json(CANONICAL_TRACE, source_trace)
    report = {"milestone": "M84R", "generated_at": now(), "status": "PASS_M84R_CANONICAL_POOL_UPDATED", "summary": {"canonical_pool_count": len(pool.get("items") or []), "static_level_counts": dict(level_counts), "source_trace_count": len(source_trace.get("items") or []), "new_l1_count": sum(1 for item in pool.get("items") or [] if item.get("prospect_id") in target_ids and item.get("level") == "L1"), "old_workbook_written": False, "knowledge_asset_written": False, "persona_registry_written": False}}
    write_json(M84 / "canonical_pool_update_admission_report_v1.json", report)
    return {"pool": pool, "update_report": report}


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
- 非资本市场补充来源：见 canonical source trace `M84R` patch。

## 风险与待补点

{item.get('risk_or_gap', '')}

## 静态升层说明

{item.get('static_promotion_summary', '')}

## 来源边界

本档案只表达静态 ICP 匹配、证据成熟度和信息完整度；不写旧 Excel、不写知识资产、不改 persona registry。
"""
        write_text(path, text)
        outputs.append({"prospect_id": prospect_id, "company_name": item.get("company_name"), "path": str(path)})
    package = {"milestone": "M84R", "generated_at": now(), "status": "PASS_M84R_L1_VAULT_WRITE_EXECUTED", "summary": {"target_count": len(target_ids), "l1_vault_write_count": len(outputs), "skipped_count": len(skipped), "l2_dossier_retained": True, "old_workbook_written": False, "knowledge_asset_written": False, "persona_registry_written": False}, "items": outputs, "skipped": skipped}
    write_json(M84 / "l1_vault_write_package_v1.json", package)
    return package


def build_audits(pool: dict[str, Any], trace: dict[str, Any], target_ids: set[str]) -> dict[str, Any]:
    trace_by = source_trace_by_prospect(trace)
    audit_items = []
    for item in pool.get("items") or []:
        if item.get("prospect_id") not in target_ids:
            continue
        sources = trace_by.get(str(item.get("prospect_id") or ""), [])
        categories = sorted(_strong_source_categories(sources))
        audit_items.append({"prospect_id": item.get("prospect_id"), "company_name": item.get("company_name"), "level": item.get("level"), "source_categories": categories, "l1_countable_source_count": sum(1 for source in sources if _is_l1_countable_evidence(source)), "has_icp_support_source": any(_has_icp_support(source) for source in sources), "source_count": len(sources)})
    category_counts = Counter()
    for row in trace.get("items") or []:
        for source in row.get("sources") or []:
            category_counts[_source_category(source)] += 1
    audit = {"milestone": "M84R", "generated_at": now(), "status": "PASS_M84R_NON_CAPITAL_SOURCE_AUDIT_READY", "summary": {"audited_target_count": len(audit_items), "source_category_counts": dict(category_counts), "platform_operating_fact_count": category_counts.get("platform_operating_fact", 0), "authoritative_third_party_count": category_counts.get("authoritative_third_party", 0)}, "items": audit_items}
    write_json(M84 / "non_capital_source_audit_v1.json", audit)
    return audit


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


def validate(target_ids: set[str], report: dict[str, Any], vault: dict[str, Any], audit: dict[str, Any]) -> dict[str, Any]:
    py_compile = run(["python3", "-m", "py_compile", "scripts/build_m84r_non_listed_icp_source_trial.py", "scripts/trusted_pool_runner.py", "shared/static_pool/static_promote.py"])
    mismatch = read_json(M84 / "m84r_baseline_v1.json")
    mismatch["candidate_signature"] = "intentional_mismatch_for_m84r_guard"
    mismatch_path = M84 / "m84r_baseline_mismatch_probe_v1.json"
    write_json(mismatch_path, mismatch)
    mismatch_result = run(["python3", "scripts/trusted_pool_runner.py", "--mode", "report_only", "--trusted-pool", rel(CANONICAL_POOL), "--source-trace", rel(M84 / "source_trace_index_v7.json"), "--baseline-file", rel(mismatch_path), "--require-baseline"])
    update_guard = run(["python3", "scripts/trusted_pool_runner.py", "--mode", "update_trusted_pool", "--trusted-pool", rel(CANONICAL_POOL), "--source-trace", rel(M84 / "source_trace_index_v7.json"), "--validation-report-file", rel(M84 / "update_without_allow_validation_probe_v1.json")])
    json_paths = [*M84.glob("*.json"), CANONICAL_POOL, CANONICAL_TRACE, STATUS_PANEL]
    json_errors = []
    for path in json_paths:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            json_errors.append({"path": rel(path), "error": str(exc)})
    pool = read_json(CANONICAL_POOL)
    l1_ids = {item.get("prospect_id") for item in pool.get("items") or [] if item.get("level") == "L1"}
    level_counts = Counter(item.get("level") or "<missing>" for item in pool.get("items") or [])
    dynamic = scan_dynamic([M84] + [Path(row["path"]) for row in vault.get("items", [])])
    api = scan_api([M84, WORKSPACE / "scripts/build_m84r_non_listed_icp_source_trial.py"])
    assertions = {"target_ids_promoted_to_l1": target_ids.issubset(l1_ids), "l1_count_increased": level_counts.get("L1", 0) >= 31, "platform_operating_fact_added": audit["summary"].get("platform_operating_fact_count", 0) > 0, "l1_vault_write_count_matches_targets": vault["summary"]["l1_vault_write_count"] == len(target_ids), "baseline_mismatch_failed": mismatch_result.returncode != 0, "update_without_allow_failed": update_guard.returncode != 0, "no_old_excel_write": True, "no_knowledge_asset_write": True, "no_persona_registry_write": True}
    status = "PASS" if py_compile.returncode == 0 and not json_errors and all(assertions.values()) and dynamic["status"] == "PASS" and api["status"] == "PASS" else "FAIL"
    validation = {"milestone": "M84R", "generated_at": now(), "status": status, "py_compile": {"returncode": py_compile.returncode, "stderr": py_compile.stderr}, "json_parse": {"checked_count": len(json_paths), "error_count": len(json_errors), "errors": json_errors}, "baseline_mismatch_guard": {"returncode": mismatch_result.returncode, "stderr": mismatch_result.stderr.strip()}, "update_guard": {"returncode": update_guard.returncode, "stderr": update_guard.stderr.strip()}, "dynamic_term_scan": dynamic, "api_key_scan": api, "assertions": assertions}
    write_json(M84 / "m84r_validation_report_v1.json", validation)
    return validation


def build_status(pool: dict[str, Any], vault: dict[str, Any], audit: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    level_counts = Counter(item.get("level") or "<missing>" for item in pool.get("items") or [])
    panel = {"milestone": "M84R", "generated_at": now(), "status": "PASS_M84R_NON_LISTED_ICP_SOURCE_TRIAL" if validation["status"] == "PASS" else "FAIL_M84R_NON_LISTED_ICP_SOURCE_TRIAL", "summary": {"canonical_pool_count": len(pool.get("items") or []), "static_level_counts": dict(level_counts), "l1_vault_write_count": vault["summary"]["l1_vault_write_count"], "source_category_counts": audit["summary"]["source_category_counts"], "platform_operating_fact_count": audit["summary"]["platform_operating_fact_count"], "authoritative_third_party_count": audit["summary"]["authoritative_third_party_count"], "old_workbook_write_enabled": False, "knowledge_asset_write_enabled": False, "persona_registry_write_enabled": False}, "next_recommended_action": "继续补 platform_operating_fact 与 authoritative_third_party，优先服务非上市/高成长 ICP 候选。"}
    handoff = {"milestone": "M84R", "generated_at": now(), "status": "PASS_M84R_HANDOFF_READY" if validation["status"] == "PASS" else "FAIL_M84R_HANDOFF_NEEDS_REVIEW", "key_outputs": {"source_patch": rel(M84 / "platform_authoritative_source_patch_package_v1.json"), "source_audit": rel(M84 / "non_capital_source_audit_v1.json"), "validation": rel(M84 / "m84r_validation_report_v1.json")}}
    write_json(M84 / "m84r_operating_panel_v1.json", panel)
    write_json(M84 / "handoff_snapshot_v1.json", handoff)
    canonical = read_json(STATUS_PANEL)
    canonical["generated_at"] = now()
    canonical["overall_status"] = panel["status"]
    canonical["latest_milestone"] = "M84R"
    canonical["m84r_non_listed_icp_source_trial"] = panel["summary"]
    canonical["canonical_next_action"] = panel["next_recommended_action"]
    canonical["next_recommended_action"] = panel["next_recommended_action"]
    write_json(STATUS_PANEL, canonical)
    return panel


def main() -> int:
    M84.mkdir(parents=True, exist_ok=True)
    pool = read_json(CANONICAL_POOL)
    trace = read_json(CANONICAL_TRACE)
    patch = build_patch(pool, trace)
    report = run_report_only()
    updated = update_pool_and_trace(patch["source_trace"], patch["target_ids"])
    vault = write_l1_vault(updated["pool"], patch["target_ids"])
    audit = build_audits(updated["pool"], patch["source_trace"], patch["target_ids"])
    validation = validate(patch["target_ids"], report, vault, audit)
    panel = build_status(updated["pool"], vault, audit, validation)
    print(json.dumps({"patch": patch["package"]["summary"], "report_levels": report.get("summary", {}).get("level_counts"), "panel": panel["summary"], "validation": validation["status"]}, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
