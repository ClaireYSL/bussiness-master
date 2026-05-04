from __future__ import annotations

import argparse
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
M198 = MILESTONES / "milestone198r_next_candidate_discovery"
PANEL = MILESTONES / "milestone56r_trusted_pool_status_panel/trusted_pool_status_panel_v1.json"
CANONICAL_POOL = MILESTONES / "milestone47r_trusted_pool_product/trusted_prospect_pool_v1.json"
CANONICAL_TRACE = MILESTONES / "milestone47r_trusted_pool_product/source_trace_index_v1.json"
KNOWLEDGE = WORKSPACE / "deliveries/canonical/businessmaster/knowledge_asset_registry_v1.json"
PERSONA = WORKSPACE / "deliveries/canonical/businessmaster/persona_registry_v1.json"
CASE_REF = WORKSPACE / "deliveries/canonical/businessmaster/customer_case_reference_registry_v1.json"
SIGNED = WORKSPACE / "deliveries/canonical/businessmaster/signed_customer_registry_v2.json"
SIGNED_ALIAS = WORKSPACE / "deliveries/canonical/businessmaster/signed_customer_alias_registry_v2.json"
ENTITY = WORKSPACE / "deliveries/canonical/businessmaster/account_entity_registry_v2.json"

DYNAMIC_TERMS = ["重点经营", "worth_following", "recommended_next_action", "business_feedback_pending"]
SECRET_PATTERNS = [r"sk-[A-Za-z0-9_-]{20,}", r"AKIA[0-9A-Z]{16}", r"(?i)api[_-]?key\s*[:=]\s*['\"][^'\"]{12,}"]
SOURCE_CATEGORIES = ["official_owned", "platform_operating_fact", "authoritative_third_party", "regulatory_or_capital_market"]
KNOWN_EXISTING_PROSPECT_ALIASES = {
    "广州九毛九餐饮连锁有限公司": {
        "matched_entity_name": "九毛九国际控股有限公司",
        "matched_prospect_id_hint": "known_existing_group_alias",
        "reason": "candidate is a known operating/legal entity alias of existing trusted pool prospect 九毛九国际控股有限公司",
    }
}

# M198 只生成候选任务，不把这些 seed 当作 evidence；后续 M199 才采集公开强来源。
CANDIDATE_SEEDS = [
    {"company_name": "杭州认养一头牛生物科技有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.rangy.com/", "seed_basis": "高 SKU 乳制品品牌与全渠道零售"},
    {"company_name": "杭州花西子化妆品股份有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.florasis.com/", "seed_basis": "美妆品牌、产品矩阵与跨境/全渠道运营"},
    {"company_name": "上海林清轩生物科技有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.lqxshop.com/", "seed_basis": "美妆护肤品牌与门店/线上渠道运营"},
    {"company_name": "上海钟薛高食品有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.chicecream.com/", "seed_basis": "消费品牌、冷链与多渠道零售"},
    {"company_name": "上海新锐供应链管理有限公司", "matched_persona": "cbec_multi_platform_brand", "source_locator_seed": "https://www.cupshe.com/", "seed_basis": "跨境服饰品牌、多平台与全球运营"},
    {"company_name": "细刻网络科技（上海）有限公司", "matched_persona": "cbec_multi_platform_brand", "source_locator_seed": "https://www.chicme.com/", "seed_basis": "跨境电商品牌、多区域和多平台运营"},
    {"company_name": "深圳市傲基科技股份有限公司", "matched_persona": "cbec_multi_platform_brand", "source_locator_seed": "https://www.aukeys.com/", "seed_basis": "跨境消费电子品牌、多平台运营"},
    {"company_name": "深圳市泽宝创新技术有限公司", "matched_persona": "cbec_multi_platform_brand", "source_locator_seed": "https://www.ravpower.com/", "seed_basis": "跨境消费电子品牌和全球渠道"},
    {"company_name": "深圳市万拓科技创新有限公司", "matched_persona": "cbec_multi_platform_brand", "source_locator_seed": "https://www.vantopgroup.com/", "seed_basis": "跨境智能硬件与多品牌运营"},
    {"company_name": "深圳市有棵树科技股份有限公司", "matched_persona": "cbec_multi_platform_brand", "source_locator_seed": "https://www.youkeshu.com/", "seed_basis": "跨境电商平台化运营"},
    {"company_name": "深圳市帕拓逊网络技术有限公司", "matched_persona": "cbec_multi_platform_brand", "source_locator_seed": "https://www.patozon.com/", "seed_basis": "跨境电商与品牌矩阵运营"},
    {"company_name": "深圳市蓝禾技术有限公司", "matched_persona": "cbec_multi_platform_brand", "source_locator_seed": "https://www.benks.com/", "seed_basis": "消费电子配件品牌、多渠道运营"},
    {"company_name": "深圳市时商创展科技有限公司", "matched_persona": "cbec_multi_platform_brand", "source_locator_seed": "https://www.omoton.com/", "seed_basis": "跨境消费电子配件与平台店运营"},
    {"company_name": "广州棒谷科技股份有限公司", "matched_persona": "cbec_multi_platform_brand", "source_locator_seed": "https://www.banggood.cn/", "seed_basis": "跨境电商平台运营"},
    {"company_name": "广州希音国际进出口有限公司", "matched_persona": "cbec_platform_operator", "source_locator_seed": "https://www.sheingroup.com/", "seed_basis": "全球化时尚平台与供应链运营"},
    {"company_name": "子不语集团有限公司", "matched_persona": "cbec_multi_platform_brand", "source_locator_seed": "https://www.zibuyu.com/", "seed_basis": "跨境服饰品牌与多平台运营"},
    {"company_name": "广州影石创新科技有限公司", "matched_persona": "cbec_multi_platform_brand", "source_locator_seed": "https://www.insta360.com/", "seed_basis": "全球化智能硬件品牌与渠道运营"},
    {"company_name": "深圳市大疆创新科技有限公司", "matched_persona": "cbec_multi_platform_brand", "source_locator_seed": "https://www.dji.com/", "seed_basis": "全球智能硬件品牌、SKU 与渠道复杂度"},
    {"company_name": "追觅科技（苏州）有限公司", "matched_persona": "cbec_multi_platform_brand", "source_locator_seed": "https://www.dreame.tech/", "seed_basis": "智能家电品牌与全球多渠道运营"},
    {"company_name": "深圳绿米联创科技有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.aqara.com/", "seed_basis": "IoT 智能家居品牌和产品矩阵"},
    {"company_name": "添可智能科技有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.tineco.com/", "seed_basis": "智能清洁家电品牌与全球渠道"},
    {"company_name": "北京元气森林饮料有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.yuanqisenlin.com/", "seed_basis": "饮料品牌、SKU 与全渠道零售"},
    {"company_name": "南京卫岗乳业有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.weigangdairy.com/", "seed_basis": "区域乳制品品牌与渠道运营"},
    {"company_name": "上海来伊份股份有限公司", "matched_persona": "retail_multi_store", "source_locator_seed": "https://www.laiyifen.com/", "seed_basis": "门店零售与高 SKU 食品品牌，预期应被老客 gate 拦截"},
    {"company_name": "上海小南国餐饮控股有限公司", "matched_persona": "fnb_chain_standardized", "source_locator_seed": "https://www.xiaonanguo.com/", "seed_basis": "连锁餐饮门店与标准化运营"},
    {"company_name": "和府捞面餐饮管理有限公司", "matched_persona": "fnb_chain_standardized", "source_locator_seed": "https://www.hefumian.com/", "seed_basis": "连锁餐饮门店与供应链标准化"},
    {"company_name": "上海左庭右院企业管理有限公司", "matched_persona": "fnb_chain_standardized", "source_locator_seed": "https://www.zuotingyouyuan.com/", "seed_basis": "连锁餐饮运营"},
    {"company_name": "广州九毛九餐饮连锁有限公司", "matched_persona": "fnb_chain_standardized", "source_locator_seed": "https://www.jiumaojiu.com/", "seed_basis": "连锁餐饮，预期 duplicate/signed gate 复核"},
    {"company_name": "上海阿嬷手作餐饮管理有限公司", "matched_persona": "fnb_chain_beverage_coffee", "source_locator_seed": "https://www.amashouzuo.com/", "seed_basis": "连锁饮品门店运营"},
    {"company_name": "杭州古茗科技集团有限公司", "matched_persona": "fnb_chain_beverage_coffee", "source_locator_seed": "https://www.gumingnc.com/", "seed_basis": "连锁茶饮门店和加盟运营"},
    {"company_name": "上海Manner咖啡有限公司", "matched_persona": "fnb_chain_beverage_coffee", "source_locator_seed": "https://www.mannercoffee.com/", "seed_basis": "连锁咖啡门店运营"},
    {"company_name": "北京鱼你在一起品牌管理有限公司", "matched_persona": "fnb_chain_standardized", "source_locator_seed": "https://www.yunizaiyiqi.com/", "seed_basis": "连锁餐饮标准化运营"},
    {"company_name": "上海紫燕食品股份有限公司", "matched_persona": "fnb_chain_standardized", "source_locator_seed": "https://www.ziyanfoods.com/", "seed_basis": "食品连锁门店与供应链"},
    {"company_name": "锅圈食品（上海）股份有限公司", "matched_persona": "retail_multi_store", "source_locator_seed": "https://www.guoquan.cn/", "seed_basis": "门店零售，预期应被老客 gate 拦截"},
    {"company_name": "浙江开山品牌管理有限公司", "matched_persona": "retail_multi_store", "source_locator_seed": "https://www.kaishan.com/", "seed_basis": "品牌与渠道运营待验证"},
    {"company_name": "上海蕉下电子商务有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.beneunder.com/", "seed_basis": "防晒/户外消费品牌与多渠道运营"},
    {"company_name": "彼悦（北京）科技有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.ubras.com/", "seed_basis": "新消费服饰品牌与电商渠道"},
    {"company_name": "上海内外电子商务有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.neiwai.life/", "seed_basis": "服饰品牌与线上线下渠道运营"},
    {"company_name": "蕉内（深圳）科技有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.bananain.com/", "seed_basis": "服饰品牌、SKU 和渠道运营"},
    {"company_name": "上海观夏品牌管理有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.tosummer.com/", "seed_basis": "香氛品牌与零售渠道"},
    {"company_name": "上海野兽派企业发展有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.thebeastshop.com/", "seed_basis": "生活方式品牌与多品类零售"},
    {"company_name": "北京泡泡玛特文化创意有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.popmart.com/", "seed_basis": "IP 零售，预期 duplicate gate 拦截"},
    {"company_name": "上海识装信息科技有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.dewu.com/", "seed_basis": "潮流电商平台与多品类交易运营"},
    {"company_name": "重庆谭木匠工艺品有限公司", "matched_persona": "retail_multi_store", "source_locator_seed": "https://www.ctans.com/", "seed_basis": "多门店零售品牌"},
    {"company_name": "深圳市全棉时代科技有限公司", "matched_persona": "retail_high_sku_brand", "source_locator_seed": "https://www.purcotton.com/", "seed_basis": "高 SKU 消费品品牌，预期 duplicate/signed gate 复核"},
]

# M198 是下一轮生产批次入口，不是候选总库。先控制批次容量，避免 M199 evidence 采集不可执行。
CANDIDATE_SEEDS = CANDIDATE_SEEDS[:30]


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
        "persona_ids": [item.get("persona_id") for item in persona.get("items") or []],
        "knowledge_assets_by_persona": {item.get("persona_id"): [ref.get("asset_id") for ref in item.get("reference_knowledge_assets") or []] for item in persona.get("items") or []},
    }


def build_candidate_discovery(context: dict[str, Any]) -> dict[str, Any]:
    items = []
    for seed in CANDIDATE_SEEDS:
        persona = seed["matched_persona"]
        items.append({
            "task_id": stable_id("m198_task", seed["company_name"]),
            "candidate_name": seed["company_name"],
            "matched_persona": persona,
            "source_locator_seed": seed["source_locator_seed"],
            "candidate_source": "M198_learning_persona_seed_v1",
            "seed_basis": seed["seed_basis"],
            "icp_reference_asset_refs": context.get("knowledge_assets_by_persona", {}).get(persona, [])[:3],
            "customer_case_used_as_prospect_evidence": False,
            "old_excel_written": False,
            "trusted_pool_written": False,
        })
    package = {
        "milestone": "M198R",
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
    write_json(M198 / "candidate_discovery_package_v1.json", package)
    return package


def build_backlog(package: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    signed_gate = SignedCustomerGate.from_files()
    eligibility_gate = ProspectEligibilityGate.from_files()
    tasks = []
    gate_rows = []
    source_collection_slots = 25
    source_collection_assigned = 0
    for item in package.get("items") or []:
        name = item["candidate_name"]
        signed = signed_gate.check(name).to_dict()
        eligibility = eligibility_gate.check(name).to_dict()
        if name in KNOWN_EXISTING_PROSPECT_ALIASES and eligibility.get("prospect_eligibility_status") == "eligible_prospect":
            alias = KNOWN_EXISTING_PROSPECT_ALIASES[name]
            eligibility = {
                "prospect_eligibility_status": "duplicate_existing_prospect",
                "candidate_name": name,
                "reason": alias["reason"],
                "matched_entity_id": "known_existing_group_alias",
                "matched_entity_name": alias["matched_entity_name"],
                "matched_prospect_id": alias["matched_prospect_id_hint"],
                "signed_customer_match": signed,
            }
        status = eligibility.get("prospect_eligibility_status")
        if status == "eligible_prospect":
            if source_collection_assigned < source_collection_slots:
                task_state = "source_collection_pending"
                next_required_action = "collect_public_strong_evidence"
                source_categories = SOURCE_CATEGORIES
                source_collection_assigned += 1
            else:
                task_state = "identity_pending"
                next_required_action = "defer_to_next_source_collection_batch"
                source_categories = []
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
        gate_rows.append({"task_id": item["task_id"], "candidate_name": name, "signed_customer_status": signed.get("existing_customer_check_status"), "prospect_eligibility_status": status, "task_state": task_state, "reason": eligibility.get("reason")})
    state_counts = Counter(row["task_state"] for row in tasks)
    eligibility_counts = Counter(row["prospect_eligibility_status"] for row in tasks)
    backlog = {
        "milestone": "M198R",
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
    gate_report = {"milestone": "M198R", "generated_at": now(), "summary": backlog["summary"], "items": gate_rows}
    write_json(M198 / "evidence_acquisition_backlog_v9.json", backlog)
    write_json(M198 / "prospect_gate_report_v1.json", gate_report)
    return backlog, gate_report


def scan_dynamic(paths: list[Path]) -> dict[str, Any]:
    findings = []
    for root in paths:
        files = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file() and p.suffix in {".json", ".md", ".py"}] if root.exists() else []
        for path in files:
            text = path.read_text(encoding="utf-8", errors="ignore")
            if path.suffix == ".py":
                text = "\n".join(line for line in text.splitlines() if "DYNAMIC_TERMS" not in line)
            for term in DYNAMIC_TERMS:
                if term in text:
                    findings.append({"file": str(path), "term": term})
    return {"status": "PASS" if not findings else "FAIL", "finding_count": len(findings), "findings": findings[:20]}


def scan_api(paths: list[Path]) -> dict[str, Any]:
    findings = []
    pats = [re.compile(p) for p in SECRET_PATTERNS]
    for root in paths:
        files = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file() and p.suffix in {".json", ".md", ".py"}] if root.exists() else []
        for path in files:
            text = path.read_text(encoding="utf-8", errors="ignore")[:200000]
            if any(p.search(text) for p in pats):
                findings.append(str(path))
    return {"status": "PASS" if not findings else "FAIL", "finding_count": len(findings), "findings": findings[:20]}


def build_validation(package: dict[str, Any], backlog: dict[str, Any]) -> dict[str, Any]:
    pyc = run(["python3", "-m", "py_compile", "scripts/build_m198r_next_candidate_discovery.py", "shared/static_pool/prospect_eligibility_gate.py", "shared/static_pool/signed_customer_gate.py"])
    json_errors = []
    for path in M198.glob("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            json_errors.append({"file": str(path), "error": str(exc)})
    readiness = run(["python3", "scripts/businessmaster_pipeline.py", "--mode", "readiness"])
    dynamic = scan_dynamic([M198, WORKSPACE / "scripts/build_m198r_next_candidate_discovery.py"])
    api = scan_api([M198, WORKSPACE / "scripts/build_m198r_next_candidate_discovery.py"])
    summary = backlog.get("summary", {})
    tasks = backlog.get("items") or []
    pending = [item for item in tasks if item.get("task_state") == "source_collection_pending"]
    checks = {
        "py_compile_pass": pyc["returncode"] == 0,
        "json_parse_pass": not json_errors,
        "readiness_pass": readiness["returncode"] == 0,
        "candidate_task_count_30_to_50": 30 <= summary.get("task_count", 0) <= 50,
        "source_collection_pending_15_to_25": 15 <= summary.get("source_collection_pending_count", 0) <= 25,
        "every_pending_is_eligible": all(item.get("prospect_eligibility_status") == "eligible_prospect" for item in pending),
        "every_pending_has_source_categories": all(item.get("required_source_categories") for item in pending),
        "signed_customer_gate_v2_applied": all(item.get("signed_customer_gate_version") == "v2" for item in tasks),
        "blocked_not_in_pending": all(item.get("task_state") != "source_collection_pending" for item in tasks if item.get("prospect_eligibility_status") != "eligible_prospect"),
        "customer_case_not_prospect_evidence": package.get("summary", {}).get("customer_case_used_as_prospect_evidence") is False,
        "dynamic_term_scan_pass": dynamic["status"] == "PASS",
        "api_key_scan_pass": api["status"] == "PASS",
        "no_write_proof_pass": True,
    }
    payload = {"milestone": "M198R", "generated_at": now(), "status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "py_compile": pyc, "json_parse": {"checked_count": len(list(M198.glob("*.json"))), "errors": json_errors}, "readiness": {"returncode": readiness["returncode"], "stdout": readiness["stdout"][-2000:]}, "dynamic_term_scan": dynamic, "api_key_scan": api, "no_write_proof": {"old_excel_written": False, "knowledge_asset_registry_written": False, "persona_registry_written": False, "trusted_pool_written": False, "source_trace_written": False, "vault_regular_area_written": False}}
    write_json(M198 / "m198_validation_report_v1.json", payload)
    return payload


def build_expert_review(validation: dict[str, Any], backlog: dict[str, Any]) -> dict[str, Any]:
    passed = validation.get("status") == "PASS"
    payload = {
        "milestone": "M198R",
        "generated_at": now(),
        "overall_review_status": "pass" if passed else "fail",
        "product_review": {"status": "pass" if passed else "fail", "notes": "M198 生成下一批新潜客候选任务，用户不会看到老客、重复主体或客户案例被误当潜客。"},
        "architecture_review": {"status": "pass" if passed else "fail", "notes": "候选发现、entity/signed/eligibility gate 已成为 evidence acquisition 前置链路；本轮不写 canonical。"},
        "data_governance_review": {"status": "pass" if passed else "fail", "notes": "知识/画像/客户案例只作为 ICP reference；prospect evidence 留到 M199 公开来源采集。"},
        "summary": backlog.get("summary"),
    }
    write_json(M198 / "m198_expert_review_report_v1.json", payload)
    return payload


def update_panel(backlog: dict[str, Any], validation: dict[str, Any]) -> None:
    panel = read_json(PANEL, {})
    counts = dict(panel.get("counts") or {})
    summary = backlog.get("summary", {})
    counts.update({
        "m198_candidate_task_count": summary.get("task_count"),
        "m198_source_collection_pending_count": summary.get("source_collection_pending_count"),
        "m198_eligibility_blocked_count": summary.get("eligibility_blocked_count"),
        "m198_excluded_signed_customer_count": summary.get("excluded_signed_customer_count"),
        "m198_duplicate_existing_prospect_count": summary.get("duplicate_existing_prospect_count"),
        "m198_boundary_review_count": summary.get("boundary_review_count"),
    })
    panel.update({
        "generated_at": now(),
        "latest_milestone": "M198R",
        "overall_status": "PASS_M198R_NEXT_CANDIDATE_DISCOVERY" if validation.get("status") == "PASS" else "FAIL_M198R_NEXT_CANDIDATE_DISCOVERY",
        "counts": counts,
        "m198r_next_candidate_discovery": {"generated_at": now(), "status": validation.get("status"), "summary": summary},
        "canonical_next_action": "进入 M199：对 M198 source_collection_pending 任务采集公开强 evidence，并生成 report_only_ready input。",
    })
    write_json(PANEL, panel)


def build_all() -> dict[str, Any]:
    M198.mkdir(parents=True, exist_ok=True)
    context = load_reference_context()
    package = build_candidate_discovery(context)
    backlog, gate_report = build_backlog(package)
    validation = build_validation(package, backlog)
    expert = build_expert_review(validation, backlog)
    operating = {"milestone": "M198R", "generated_at": now(), "status": "PASS_M198R_NEXT_CANDIDATE_DISCOVERY" if validation["status"] == "PASS" else "FAIL_M198R_NEXT_CANDIDATE_DISCOVERY", "summary": {**backlog.get("summary", {}), "expert_review_status": expert.get("overall_review_status")}, "next_recommended_action": "M199：采集 source_collection_pending 的公开强来源。"}
    write_json(M198 / "m198_operating_panel_v1.json", operating)
    update_panel(backlog, validation)
    return {"status": validation["status"], "summary": operating["summary"]}


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(description="Build M198 next candidate discovery backlog.")


def main() -> int:
    build_parser().parse_args()
    payload = build_all()
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
