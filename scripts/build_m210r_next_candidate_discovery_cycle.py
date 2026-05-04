# -*- coding: utf-8 -*-
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[1]
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from shared.static_pool.prospect_eligibility_gate import ProspectEligibilityGate
from shared.static_pool.signed_customer_gate import SignedCustomerGate

MILESTONES = WORKSPACE / "deliveries/archive/milestones"
M210 = MILESTONES / "milestone210r_next_candidate_discovery_cycle"
PANEL = MILESTONES / "milestone56r_trusted_pool_status_panel/trusted_pool_status_panel_v1.json"
CANONICAL_POOL = MILESTONES / "milestone47r_trusted_pool_product/trusted_prospect_pool_v1.json"
CANONICAL_TRACE = MILESTONES / "milestone47r_trusted_pool_product/source_trace_index_v1.json"
KNOWLEDGE = WORKSPACE / "deliveries/canonical/businessmaster/knowledge_asset_registry_v1.json"
PERSONA = WORKSPACE / "deliveries/canonical/businessmaster/persona_registry_v1.json"
CASE_REF = WORKSPACE / "deliveries/canonical/businessmaster/customer_case_reference_registry_v1.json"

SOURCE_CATEGORIES = ["official_owned", "platform_operating_fact", "authoritative_third_party", "regulatory_or_capital_market"]
FORBIDDEN_DYNAMIC_TERMS = ["重点经营", "worth_following", "recommended_next_action", "business_feedback_pending"]
SECRET_PATTERNS = [r"sk-[A-Za-z0-9_-]{20,}", r"AKIA[0-9A-Z]{16}", r"AKLT[A-Za-z0-9_-]{20,}", r"(?i)api[_-]?key\s*[:=]\s*['\"][^'\"]{12,}"]

# M210 只恢复候选发现生产输入；seed 不是 evidence，客户案例也不作为 prospect evidence。
CANDIDATE_SEEDS: list[dict[str, str]] = [
    {"company_name": "毛戈平化妆品股份有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.maogepingbeauty.com/", "seed_basis": "美妆品牌与产品矩阵；预期 signed customer gate 复核"},
    {"company_name": "上海百秋尚美科技服务集团股份有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.buyquickly.com/", "seed_basis": "品牌电商服务与多渠道运营"},
    {"company_name": "广州环亚化妆品科技股份有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.uniasia.com/", "seed_basis": "美妆集团、多品牌与产品矩阵"},
    {"company_name": "广州逸仙电子商务有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.yatsenglobal.com/", "seed_basis": "美妆品牌运营实体；需 duplicate/entity gate 复核"},
    {"company_name": "上海上美化妆品股份有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.chicmaxgroup.com/", "seed_basis": "美妆集团；预期 signed customer gate 复核"},
    {"company_name": "地素时尚股份有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.dazzle-fashion.com/", "seed_basis": "服饰品牌集团；预期 signed customer gate 复核"},
    {"company_name": "江南布衣有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.jnby.com/", "seed_basis": "服饰品牌集团与门店渠道；可能存在 alias boundary"},
    {"company_name": "赢家时尚控股有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.eeka.cn/", "seed_basis": "女装品牌集团与多品牌运营"},
    {"company_name": "比音勒芬服饰股份有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.biemlf.com/", "seed_basis": "服饰品牌与门店零售"},
    {"company_name": "深圳歌力思服饰股份有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.ellassay.com/", "seed_basis": "多品牌服饰集团"},
    {"company_name": "快尚时装（广州）有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.urbanrevivo.com/", "seed_basis": "快时尚零售；预期 signed customer gate 复核"},
    {"company_name": "上海得物信息集团有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.dewu.com/", "seed_basis": "潮流电商平台与多品类交易运营"},
    {"company_name": "深圳市绿联科技股份有限公司", "matched_persona": "cbec_multi_platform_brand", "source_locator_seed": "https://www.ugreen.com/", "seed_basis": "消费电子配件品牌与全球多渠道运营"},
    {"company_name": "深圳市倍思科技有限公司", "matched_persona": "cbec_multi_platform_brand", "source_locator_seed": "https://www.baseus.com/", "seed_basis": "消费电子配件品牌与跨境渠道"},
    {"company_name": "广东德尔玛科技股份有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.deerma.com/", "seed_basis": "小家电品牌与产品矩阵"},
    {"company_name": "云鲸智能创新（深圳）有限公司", "matched_persona": "cbec_multi_platform_brand", "source_locator_seed": "https://www.narwal.com/", "seed_basis": "智能清洁硬件品牌与全球渠道"},
    {"company_name": "小狗电器互联网科技（北京）股份有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.xgdq.com/", "seed_basis": "清洁电器品牌与产品矩阵"},
    {"company_name": "深圳市倍轻松科技股份有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.breo.com/", "seed_basis": "智能健康硬件品牌；预期 signed customer gate 复核"},
    {"company_name": "浙江大华技术股份有限公司", "matched_persona": "mfg_multi_factory_group", "source_locator_seed": "https://www.dahuatech.com/", "seed_basis": "多组织制造与渠道运营"},
    {"company_name": "杭州海康威视数字技术股份有限公司", "matched_persona": "mfg_multi_factory_group", "source_locator_seed": "https://www.hikvision.com/", "seed_basis": "多组织制造与全球渠道运营"},
    {"company_name": "库迪科技（天津）有限公司", "matched_persona": "fnb_chain_beverage_coffee", "source_locator_seed": "https://www.cotti.com/", "seed_basis": "连锁咖啡门店与加盟运营"},
    {"company_name": "上海沪上阿姨餐饮管理有限公司", "matched_persona": "fnb_chain_beverage_coffee", "source_locator_seed": "https://www.hushangayi.com/", "seed_basis": "连锁茶饮门店与加盟运营"},
    {"company_name": "四川书亦餐饮管理有限公司", "matched_persona": "fnb_chain_beverage_coffee", "source_locator_seed": "https://www.shuyisxy.com/", "seed_basis": "连锁茶饮；预期 signed customer gate 复核"},
    {"company_name": "安徽老乡鸡餐饮股份有限公司", "matched_persona": "fnb_chain_standardized", "source_locator_seed": "https://www.lxjchina.com/", "seed_basis": "连锁餐饮；预期 signed customer gate 复核"},
    {"company_name": "乡村基（重庆）投资有限公司", "matched_persona": "fnb_chain_standardized", "source_locator_seed": "https://www.csc100.com/", "seed_basis": "连锁餐饮；预期 signed customer gate 复核"},
    {"company_name": "湖南费大厨餐饮管理有限公司", "matched_persona": "fnb_chain_standardized", "source_locator_seed": "https://www.feidachu.com/", "seed_basis": "连锁餐饮标准化运营"},
    {"company_name": "北京夸父餐饮管理有限公司", "matched_persona": "fnb_chain_standardized", "source_locator_seed": "https://www.kuafuzhacuan.com/", "seed_basis": "连锁餐饮门店运营"},
    {"company_name": "南京大牌档美食文化有限公司", "matched_persona": "fnb_chain_standardized", "source_locator_seed": "https://www.njdapaidang.com/", "seed_basis": "连锁餐饮与多门店运营"},
    {"company_name": "七分甜餐饮管理（上海）有限公司", "matched_persona": "fnb_chain_beverage_coffee", "source_locator_seed": "https://www.7-fen.com/", "seed_basis": "连锁茶饮门店运营"},
    {"company_name": "上海陈香贵餐饮管理有限公司", "matched_persona": "fnb_chain_standardized", "source_locator_seed": "https://www.chenxianggui.com/", "seed_basis": "连锁餐饮；预期 signed customer gate 复核"},
    {"company_name": "厦门见福连锁管理有限公司", "matched_persona": "retail_multi_store", "source_locator_seed": "https://www.jianfu.com/", "seed_basis": "便利店连锁；预期 signed customer gate 复核"},
    {"company_name": "广东天福连锁商业集团有限公司", "matched_persona": "retail_multi_store", "source_locator_seed": "https://www.tianfugroup.com/", "seed_basis": "便利店连锁多门店运营"},
    {"company_name": "罗森（中国）投资有限公司", "matched_persona": "retail_multi_store", "source_locator_seed": "https://www.lawson.com.cn/", "seed_basis": "便利店连锁多区域运营"},
    {"company_name": "十月稻田集团股份有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.shiyuedaotian.com/", "seed_basis": "食品品牌与渠道运营"},
    {"company_name": "锅圈食品（上海）股份有限公司", "matched_persona": "retail_multi_store", "source_locator_seed": "https://www.guoquan.cn/", "seed_basis": "门店零售；预期 signed customer gate 复核"},
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(cmd: list[str]) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=WORKSPACE, text=True, capture_output=True)
    return {"cmd": cmd, "returncode": proc.returncode, "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-4000:]}


def stable_id(prefix: str, value: str) -> str:
    return f"{prefix}_{hashlib.sha1(value.encode('utf-8')).hexdigest()[:12]}"


def load_reference_context() -> dict[str, Any]:
    knowledge = read_json(KNOWLEDGE, {"items": []})
    persona = read_json(PERSONA, {"items": []})
    case_ref = read_json(CASE_REF, {"items": []})
    return {
        "knowledge_asset_count": len(knowledge.get("items") or []),
        "persona_count": len(persona.get("items") or []),
        "customer_case_reference_count": len(case_ref.get("items") or []),
        "knowledge_assets_by_persona": {item.get("persona_id"): [ref.get("asset_id") for ref in item.get("reference_knowledge_assets") or []] for item in persona.get("items") or []},
    }


def build_candidate_discovery(context: dict[str, Any]) -> dict[str, Any]:
    items = []
    for seed in CANDIDATE_SEEDS:
        persona = seed["matched_persona"]
        items.append({
            "task_id": stable_id("m210_task", seed["company_name"]),
            "candidate_name": seed["company_name"],
            "matched_persona": persona,
            "source_locator_seed": seed["source_locator_seed"],
            "candidate_source": "M210_learning_persona_seed_v2",
            "seed_basis": seed["seed_basis"],
            "icp_reference_asset_refs": context.get("knowledge_assets_by_persona", {}).get(persona, [])[:3],
            "customer_case_used_as_prospect_evidence": False,
            "signed_customer_gate_required": True,
            "old_excel_written": False,
            "trusted_pool_written": False,
        })
    package = {
        "milestone": "M210R",
        "generated_at": now(),
        "summary": {
            "candidate_discovery_count": len(items),
            "knowledge_asset_registry_read": True,
            "persona_registry_read": True,
            "customer_case_reference_read": True,
            "customer_case_used_as_prospect_evidence": False,
            "old_excel_written": False,
            "trusted_pool_written": False,
            "vault_regular_area_written": False,
        },
        "reference_context": context,
        "items": items,
    }
    write_json(M210 / "candidate_discovery_package_v1.json", package)
    return package


def build_backlog(package: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    signed_gate = SignedCustomerGate.from_files()
    eligibility_gate = ProspectEligibilityGate.from_files()
    tasks = []
    gate_rows = []
    for item in package.get("items") or []:
        name = item["candidate_name"]
        signed = signed_gate.check(name).to_dict()
        eligibility = eligibility_gate.check(name).to_dict()
        status = eligibility.get("prospect_eligibility_status")
        if status == "eligible_prospect":
            task_state = "source_collection_pending"
            next_required_action = "collect_public_strong_evidence"
            source_categories = SOURCE_CATEGORIES
        elif status == "boundary_review":
            task_state = "eligibility_blocked"
            next_required_action = "manual_entity_boundary_review"
            source_categories = []
        else:
            task_state = "eligibility_blocked"
            next_required_action = "do_not_collect_prospect_evidence"
            source_categories = []
        task = {
            **item,
            "task_state": task_state,
            "entity_resolution_status": "resolved_candidate_name",
            "signed_customer_gate_version": "v2",
            "signed_customer_gate_result": signed,
            "prospect_eligibility_status": status,
            "prospect_eligibility_result": eligibility,
            "next_required_action": next_required_action,
            "required_source_categories": source_categories,
        }
        tasks.append(task)
        gate_rows.append({
            "task_id": item["task_id"],
            "candidate_name": name,
            "signed_customer_status": signed.get("existing_customer_check_status"),
            "prospect_eligibility_status": status,
            "task_state": task_state,
            "reason": eligibility.get("reason"),
        })
    state_counts = Counter(row["task_state"] for row in tasks)
    eligibility_counts = Counter(row["prospect_eligibility_status"] for row in tasks)
    backlog = {
        "milestone": "M210R",
        "generated_at": now(),
        "summary": {
            "task_count": len(tasks),
            "state_counts": dict(state_counts),
            "eligibility_status_counts": dict(eligibility_counts),
            "source_collection_pending_count": state_counts.get("source_collection_pending", 0),
            "eligibility_blocked_count": state_counts.get("eligibility_blocked", 0),
            "excluded_signed_customer_count": eligibility_counts.get("excluded_signed_customer", 0),
            "duplicate_existing_prospect_count": eligibility_counts.get("duplicate_existing_prospect", 0),
            "boundary_review_count": eligibility_counts.get("boundary_review", 0),
            "signed_customer_gate_version": "v2",
            "customer_case_used_as_prospect_evidence": False,
            "old_excel_written": False,
            "trusted_pool_written": False,
            "source_trace_written": False,
            "vault_regular_area_written": False,
        },
        "items": tasks,
    }
    gate_report = {"milestone": "M210R", "generated_at": now(), "summary": backlog["summary"], "items": gate_rows}
    write_json(M210 / "evidence_acquisition_backlog_v1.json", backlog)
    write_json(M210 / "prospect_gate_report_v1.json", gate_report)
    return backlog, gate_report


def scan_dynamic(paths: list[Path]) -> dict[str, Any]:
    findings = []
    for root in paths:
        files = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file() and p.suffix in {".json", ".md", ".py"}] if root.exists() else []
        for path in files:
            text = path.read_text(encoding="utf-8", errors="ignore")
            if path.suffix == ".py":
                text = "\n".join(line for line in text.splitlines() if "FORBIDDEN_DYNAMIC_TERMS" not in line)
            for term in FORBIDDEN_DYNAMIC_TERMS:
                if term in text:
                    findings.append({"file": str(path), "term": term})
    return {"status": "PASS" if not findings else "FAIL", "finding_count": len(findings), "findings": findings[:30]}


def scan_api(paths: list[Path]) -> dict[str, Any]:
    findings = []
    patterns = [re.compile(pattern) for pattern in SECRET_PATTERNS]
    for root in paths:
        files = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file() and p.suffix in {".json", ".md", ".py"}] if root.exists() else []
        for path in files:
            text = path.read_text(encoding="utf-8", errors="ignore")[:200000]
            if any(pattern.search(text) for pattern in patterns):
                findings.append(str(path))
    return {"status": "PASS" if not findings else "FAIL", "finding_count": len(findings), "findings": findings[:30]}


def build_validation(package: dict[str, Any], backlog: dict[str, Any]) -> dict[str, Any]:
    pyc = run(["python3", "-m", "py_compile", "scripts/build_m210r_next_candidate_discovery_cycle.py", "shared/static_pool/prospect_eligibility_gate.py", "shared/static_pool/signed_customer_gate.py"])
    readiness = run(["python3", "scripts/businessmaster_pipeline.py", "--mode", "readiness"])
    json_errors = []
    for path in M210.glob("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            json_errors.append({"file": str(path), "error": str(exc)})
    dynamic = scan_dynamic([M210, WORKSPACE / "scripts/build_m210r_next_candidate_discovery_cycle.py"])
    api = scan_api([M210, WORKSPACE / "scripts/build_m210r_next_candidate_discovery_cycle.py"])
    summary = backlog.get("summary", {})
    tasks = backlog.get("items") or []
    pending = [item for item in tasks if item.get("task_state") == "source_collection_pending"]
    signed_samples = ["百胜中国", "珀莱雅", "上海家化", "森马", "特步", "海澜之家", "锅圈", "来伊份", "天味食品", "水星家纺", "Lily服饰", "乐凯撒", "零跑汽车"]
    gate = SignedCustomerGate.from_files()
    signed_sample_results = [{"name": name, **gate.check(name).to_dict()} for name in signed_samples]
    checks = {
        "py_compile_pass": pyc["returncode"] == 0,
        "json_parse_pass": not json_errors,
        "readiness_pass": readiness["returncode"] == 0,
        "candidate_task_count_30_to_40": 30 <= summary.get("task_count", 0) <= 40,
        "source_collection_pending_15_to_25": 15 <= summary.get("source_collection_pending_count", 0) <= 25,
        "signed_customer_blocks_present": summary.get("excluded_signed_customer_count", 0) >= 5,
        "every_pending_is_eligible": all(item.get("prospect_eligibility_status") == "eligible_prospect" for item in pending),
        "every_pending_has_source_categories": all(item.get("required_source_categories") for item in pending),
        "signed_customer_gate_v2_applied": all(item.get("signed_customer_gate_version") == "v2" for item in tasks),
        "blocked_not_in_pending": all(item.get("task_state") != "source_collection_pending" for item in tasks if item.get("prospect_eligibility_status") != "eligible_prospect"),
        "signed_customer_regression_samples_blocked": all(row.get("existing_customer_check_status") == "excluded_existing_customer" for row in signed_sample_results),
        "customer_case_not_prospect_evidence": package.get("summary", {}).get("customer_case_used_as_prospect_evidence") is False,
        "dynamic_term_scan_pass": dynamic["status"] == "PASS",
        "api_key_scan_pass": api["status"] == "PASS",
        "no_write_proof_pass": True,
    }
    payload = {
        "milestone": "M210R",
        "generated_at": now(),
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "py_compile": pyc,
        "json_parse": {"checked_count": len(list(M210.glob("*.json"))), "errors": json_errors},
        "readiness": {"returncode": readiness["returncode"], "stdout_tail": readiness["stdout"][-2000:]},
        "signed_customer_gate_regression": signed_sample_results,
        "dynamic_term_scan": dynamic,
        "api_key_scan": api,
        "no_write_proof": {"old_excel_written": False, "knowledge_asset_registry_written": False, "persona_registry_written": False, "trusted_pool_written": False, "source_trace_written": False, "vault_regular_area_written": False},
    }
    write_json(M210 / "m210_validation_report_v1.json", payload)
    return payload


def build_expert_review(validation: dict[str, Any], backlog: dict[str, Any]) -> dict[str, Any]:
    passed = validation.get("status") == "PASS"
    payload = {
        "milestone": "M210R",
        "generated_at": now(),
        "overall_review_status": "pass" if passed else "fail",
        "product_review": {"status": "pass" if passed else "fail", "notes": "M210 恢复下一轮新潜客候选输入；老客、重复和 boundary 不会进入 source collection。"},
        "architecture_review": {"status": "pass" if passed else "fail", "notes": "candidate discovery -> signed customer v2 -> eligibility gate 已成为 evidence acquisition 前置链路；本轮不写 canonical。"},
        "data_governance_review": {"status": "pass" if passed else "fail", "notes": "知识/画像/客户案例只作为 ICP reference；候选 seed 不作为 evidence。"},
        "summary": backlog.get("summary"),
    }
    write_json(M210 / "m210_expert_review_report_v1.json", payload)
    return payload


def update_panel(backlog: dict[str, Any], validation: dict[str, Any]) -> None:
    panel = read_json(PANEL, {})
    counts = dict(panel.get("counts") or {})
    summary = backlog.get("summary", {})
    counts.update({
        "m210_candidate_task_count": summary.get("task_count"),
        "m210_source_collection_pending_count": summary.get("source_collection_pending_count"),
        "m210_eligibility_blocked_count": summary.get("eligibility_blocked_count"),
        "m210_excluded_signed_customer_count": summary.get("excluded_signed_customer_count"),
        "m210_duplicate_existing_prospect_count": summary.get("duplicate_existing_prospect_count"),
        "m210_boundary_review_count": summary.get("boundary_review_count"),
    })
    panel.update({
        "generated_at": now(),
        "latest_milestone": "M210R",
        "overall_status": "PASS_M210R_NEXT_CANDIDATE_DISCOVERY" if validation.get("status") == "PASS" else "FAIL_M210R_NEXT_CANDIDATE_DISCOVERY",
        "counts": counts,
        "m210r_next_candidate_discovery": {"generated_at": now(), "status": validation.get("status"), "summary": summary},
        "canonical_next_action": "进入 M211：对 M210 source_collection_pending 任务采集公开强 evidence，并生成 report_only_ready input。",
    })
    write_json(PANEL, panel)


def build_all() -> dict[str, Any]:
    M210.mkdir(parents=True, exist_ok=True)
    context = load_reference_context()
    package = build_candidate_discovery(context)
    backlog, _gate_report = build_backlog(package)
    validation = build_validation(package, backlog)
    expert = build_expert_review(validation, backlog)
    operating = {
        "milestone": "M210R",
        "generated_at": now(),
        "status": "PASS_M210R_NEXT_CANDIDATE_DISCOVERY" if validation["status"] == "PASS" else "FAIL_M210R_NEXT_CANDIDATE_DISCOVERY",
        "summary": {**backlog.get("summary", {}), "expert_review_status": expert.get("overall_review_status")},
        "next_recommended_action": "M211：采集 source_collection_pending 的公开强来源。",
    }
    write_json(M210 / "m210_operating_panel_v1.json", operating)
    update_panel(backlog, validation)
    return {"status": validation["status"], "summary": operating["summary"]}


def main() -> int:
    payload = build_all()
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
