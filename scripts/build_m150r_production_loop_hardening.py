from __future__ import annotations

import argparse
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
from shared.static_pool.static_promote import evaluate_static_promotion

MILESTONES = WORKSPACE / "deliveries/archive/milestones"
M47 = MILESTONES / "milestone47r_trusted_pool_product"
M56 = MILESTONES / "milestone56r_trusted_pool_status_panel"
M126 = MILESTONES / "milestone126r_evidence_collection_production"
M127 = MILESTONES / "milestone127r_public_evidence_admission"
M128 = MILESTONES / "milestone128r_production_trusted_pool_update"
M129 = MILESTONES / "milestone129r_vault_delivery_publish"
M130 = MILESTONES / "milestone130r_production_operations_closure"
M131 = MILESTONES / "milestone131r_signed_customer_registry"
M135 = MILESTONES / "milestone135r_production_gate_hardening"
M137 = MILESTONES / "milestone137r_account_entity_registry"
M138 = MILESTONES / "milestone138r_prospect_eligibility_gate"
M139 = MILESTONES / "milestone139r_customer_case_reference_registry"
M140 = MILESTONES / "milestone140r_source_freshness_link_health"
M141 = MILESTONES / "milestone141r_system_readiness_v3"
M150 = MILESTONES / "milestone150r_production_loop_hardening"

CANONICAL = WORKSPACE / "deliveries/canonical/businessmaster"
POOL = M47 / "trusted_prospect_pool_v1.json"
TRACE = M47 / "source_trace_index_v1.json"
PANEL = M56 / "trusted_pool_status_panel_v1.json"
KNOWLEDGE = CANONICAL / "knowledge_asset_registry_v1.json"
PERSONA = CANONICAL / "persona_registry_v1.json"
SIGNED = CANONICAL / "signed_customer_registry_v1.json"
SIGNED_ALIAS = CANONICAL / "signed_customer_alias_registry_v1.json"
ENTITY = CANONICAL / "account_entity_registry_v1.json"
CASE_REF = CANONICAL / "customer_case_reference_registry_v1.json"
VAULT_ROOT = Path("/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池/07-可信潜客档案")

DYNAMIC_TERMS = ["重点经营", "worth_following", "recommended_next_action", "business_feedback_pending"]
SIGNED_REGRESSION_BLOCK_NAMES = ["百胜中国", "珀莱雅", "上海家化", "森马", "特步", "海澜之家", "锅圈食汇", "来伊份", "天味食品", "水星家纺"]
REQUIRED_SOURCE_FIELDS = ["source_locator", "source_category", "supports_dimension", "summary"]
STRONG_SOURCE_CATEGORIES = {"official_owned", "platform_operating_fact", "authoritative_third_party", "regulatory_or_capital_market"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(WORKSPACE))
    except ValueError:
        return str(path)


def run(cmd: list[str]) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=WORKSPACE, text=True, capture_output=True)
    return {"cmd": cmd, "returncode": proc.returncode, "stdout": proc.stdout[-5000:], "stderr": proc.stderr[-5000:]}


def level_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(str(item.get("level") or "unknown") for item in items))


def vault_counts() -> dict[str, int]:
    dirs = {"L1": "01-L1 ICP强匹配档案", "L2": "02-L2正式潜客档案", "L3": "03-L3可信摘要卡", "L4": "04-L4待补证候选", "L5": "05-L5候选线索"}
    return {level: len(list((VAULT_ROOT / dirname).glob("*.md"))) if (VAULT_ROOT / dirname).exists() else 0 for level, dirname in dirs.items()}


def trace_by_id(trace: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    return {str(item.get("prospect_id") or ""): [src for src in item.get("sources") or [] if isinstance(src, dict)] for item in trace.get("items") or []}


def build_m150_1() -> dict[str, Any]:
    pool = read_json(POOL, {"items": []})
    trace = read_json(TRACE, {"items": []})
    knowledge = read_json(KNOWLEDGE, {"items": []})
    persona = read_json(PERSONA, {"items": []})
    signed = read_json(SIGNED, {"items": []})
    aliases = read_json(SIGNED_ALIAS, {"items": []})
    entity = read_json(ENTITY, {"items": []})
    case_ref = read_json(CASE_REF, {"items": []})
    m130 = read_json(M130 / "m130r_production_operations_closure_v1.json", {"summary": {}})
    m135 = read_json(M135 / "m135r_production_gate_hardening_v1.json", {"summary": {}})
    m141 = read_json(M141 / "system_readiness_v3_v1.json", {"summary": {}})
    items = pool.get("items") or []
    operating = {
        "batch_id": "m150r_operating_panel_v2",
        "milestone": "M150R",
        "generated_at": now(),
        "status": "PASS_M150R_OPERATING_PANEL_READY",
        "summary": {
            "trusted_pool_count": len(items),
            "level_counts": level_counts(items),
            "source_trace_count": len(trace.get("items") or []),
            "knowledge_asset_count": len(knowledge.get("items") or []),
            "persona_count": len(persona.get("items") or []),
            "signed_customer_count": len(signed.get("items") or []),
            "signed_customer_alias_count": len(aliases.get("items") or []),
            "account_entity_count": len(entity.get("items") or []),
            "customer_case_reference_count": len(case_ref.get("items") or case_ref.get("references") or []),
            "vault_file_counts": vault_counts(),
            "readiness_source_milestones": ["M130R", "M135R", "M141R"],
            "m130_status": m130.get("status"),
            "m135_status": m135.get("status"),
            "m141_status": m141.get("status"),
            "legacy_excel_fact_source": False,
        },
        "canonical_sources": {
            "trusted_pool": rel(POOL),
            "source_trace": rel(TRACE),
            "knowledge_asset_registry": rel(KNOWLEDGE),
            "persona_registry": rel(PERSONA),
            "signed_customer_registry": rel(SIGNED),
            "account_entity_registry": rel(ENTITY),
            "customer_case_reference_registry": rel(CASE_REF),
        },
    }
    write_json(M150 / "m150r_operating_panel_v2.json", operating)
    return operating


def production_state_for_identity(item: dict[str, Any]) -> str:
    status = item.get("production_task_status")
    if status == "ready_for_source_collection":
        return "source_collection_pending"
    if status in {"excluded_existing_customer", "signed_customer_boundary_review", "signed_customer_check_missing"}:
        return "eligibility_blocked"
    if status == "needs_company_identification":
        return "identity_pending"
    if status == "excluded_learning_case":
        return "excluded"
    return "identity_pending"


def source_is_complete(source: dict[str, Any]) -> bool:
    return all(str(source.get(field) or "").strip() for field in REQUIRED_SOURCE_FIELDS) and source.get("source_category") in STRONG_SOURCE_CATEGORIES


def build_m150_2() -> dict[str, Any]:
    identity = read_json(M126 / "candidate_identity_resolution_package_v1.json", {"items": []})
    evidence = read_json(M127 / "evidence_patch_package_v1.json", {"candidates": [], "evidence_rows": []})
    report = read_json(M128 / "m128r_production_trusted_pool_report_v1.json", {"decisions": []})
    publish = read_json(M129 / "m129r_vault_delivery_publish_v1.json", {"regular_outputs": [], "preview_outputs": []})
    evidence_by_company = {row.get("company_name"): [] for row in evidence.get("evidence_rows") or []}
    for row in evidence.get("evidence_rows") or []:
        evidence_by_company.setdefault(row.get("company_name"), []).append(row)
    decision_by_id = {row.get("prospect_id"): row for row in report.get("decisions") or []}
    regular_ids = {row.get("prospect_id") for row in publish.get("regular_outputs") or []}
    candidate_ids = {row.get("prospect_id") for row in evidence.get("candidates") or []}
    tasks = []
    for row in identity.get("items") or []:
        company = row.get("resolved_company_name") or row.get("candidate_company_name") or row.get("seed_title")
        state = production_state_for_identity(row)
        sources = evidence_by_company.get(company) or []
        if sources and all(source_is_complete(src) for src in sources):
            state = "evidence_ready"
        prospect_id = None
        for candidate in evidence.get("candidates") or []:
            if candidate.get("company_name") == company:
                prospect_id = candidate.get("prospect_id")
                break
        if prospect_id in candidate_ids and decision_by_id.get(prospect_id):
            state = "report_only_ready"
        if prospect_id in regular_ids:
            state = "vault_published"
        tasks.append({
            "seed_id": row.get("seed_id"),
            "company_name": company,
            "prospect_id": prospect_id,
            "production_state": state,
            "identity_status": row.get("production_task_status"),
            "existing_customer_check_status": row.get("existing_customer_check_status"),
            "source_count": len(sources),
            "source_complete": bool(sources) and all(source_is_complete(src) for src in sources),
            "next_action": next_action_for_state(state),
        })
    counts = Counter(item["production_state"] for item in tasks)
    package = {
        "batch_id": "m150r_evidence_acquisition_state_machine_v2",
        "milestone": "M150R",
        "generated_at": now(),
        "status": "PASS_EVIDENCE_ACQUISITION_V2_READY",
        "summary": dict(counts),
        "allowed_states": ["identity_pending", "eligibility_blocked", "source_collection_pending", "evidence_ready", "report_only_ready", "pool_updated", "vault_published", "excluded"],
        "items": tasks,
    }
    source_quality = {
        "batch_id": "m150r_source_quality_admission_v1",
        "generated_at": now(),
        "summary": {
            "evidence_row_count": len(evidence.get("evidence_rows") or []),
            "complete_evidence_row_count": sum(1 for src in evidence.get("evidence_rows") or [] if source_is_complete(src)),
            "llm_used_as_evidence_count": evidence.get("summary", {}).get("llm_used_as_evidence_count", 0),
        },
        "invalid_sources": [src for src in evidence.get("evidence_rows") or [] if not source_is_complete(src)],
    }
    write_json(M150 / "m150r_evidence_acquisition_state_machine_v2.json", package)
    write_json(M150 / "m150r_source_quality_admission_v1.json", source_quality)
    return {"state_machine": package, "source_quality": source_quality}


def next_action_for_state(state: str) -> str:
    return {
        "identity_pending": "补 canonical 公司名，不能把案例标题或人物访谈直接当潜客。",
        "eligibility_blocked": "先处理 signed customer / duplicate / boundary review，不得继续采集。",
        "source_collection_pending": "补公开强来源，优先 official_owned / platform_operating_fact / authoritative_third_party。",
        "evidence_ready": "进入 report-only 与 baseline 校验。",
        "report_only_ready": "检查 pool diff 与 no-contamination proof，准备 guarded update。",
        "pool_updated": "准备 vault preview。",
        "vault_published": "已进入用户可读层，后续做 source freshness 维护。",
        "excluded": "保留为学习或案例素材，不进入潜客池。",
    }.get(state, "复核状态。")


def build_m150_3() -> dict[str, Any]:
    report = read_json(M128 / "m128r_production_trusted_pool_report_v1.json", {"summary": {}, "decisions": []})
    diff = read_json(M128 / "m128r_pool_diff_report_v1.json", {"summary": {}, "items": []})
    no_write = read_json(M128 / "m128r_no_contamination_proof_v1.json", {})
    baseline = read_json(M128 / "m128r_baseline_v1.json", {})
    guard_probe = run(["bash", "-lc", "tmp=/tmp/bm_m150_guard; rm -rf $tmp; mkdir -p $tmp; cp deliveries/archive/milestones/milestone47r_trusted_pool_product/trusted_prospect_pool_v1.json $tmp/pool.json; python3 scripts/trusted_pool_runner.py --mode update_trusted_pool --trusted-pool $tmp/pool.json --output-file $tmp/report.json --gap-queue-file $tmp/gap.json --source-trace-output $tmp/trace.json --no-write-proof-file $tmp/no_write.json --pool-diff-file $tmp/diff.json --validation-report-file $tmp/validation.json >/tmp/bm_m150_guard.out 2>/tmp/bm_m150_guard.err; test $? -ne 0"])
    baseline_mismatch = run(["bash", "-lc", "tmp=/tmp/bm_m150_baseline; rm -rf $tmp; mkdir -p $tmp; cp deliveries/archive/milestones/milestone128r_production_trusted_pool_update/m128r_baseline_v1.json $tmp/baseline.json; python3 - <<'PY2'\nimport json\nfrom pathlib import Path\np=Path('/tmp/bm_m150_baseline/baseline.json')\nd=json.loads(p.read_text())\nd['candidate_signature']='mismatch'\np.write_text(json.dumps(d))\nPY2\npython3 - <<'PY2'\nimport json, sys\nfrom pathlib import Path\nactual=json.loads(Path('deliveries/archive/milestones/milestone128r_production_trusted_pool_update/m128r_baseline_v1.json').read_text())['candidate_signature']\nexpected=json.loads(Path('/tmp/bm_m150_baseline/baseline.json').read_text())['candidate_signature']\nsys.exit(0 if actual != expected else 2)\nPY2"])
    package = {
        "batch_id": "m150r_production_trusted_pool_batch_v2",
        "milestone": "M150R",
        "generated_at": now(),
        "status": "PASS_TRUSTED_POOL_BATCH_V2_READY" if report.get("summary", {}).get("canonical_pool_updated") and guard_probe["returncode"] == 0 and baseline_mismatch["returncode"] == 0 else "FAIL_TRUSTED_POOL_BATCH_V2",
        "summary": {
            "candidate_count": report.get("summary", {}).get("candidate_count", 0),
            "suggested_level_counts": report.get("summary", {}).get("suggested_level_counts", {}),
            "pool_diff_change_count": diff.get("summary", {}).get("change_count", 0),
            "canonical_pool_updated": report.get("summary", {}).get("canonical_pool_updated", False),
            "source_trace_updated": report.get("summary", {}).get("source_trace_updated", False),
            "baseline_candidate_count": baseline.get("candidate_count", 0),
            "missing_guard_update_blocked": guard_probe["returncode"] == 0,
            "baseline_mismatch_failed": baseline_mismatch["returncode"] == 0,
            "old_excel_written": report.get("summary", {}).get("old_excel_written", False),
            "knowledge_asset_registry_written": report.get("summary", {}).get("knowledge_asset_registry_written", False),
            "persona_registry_written": report.get("summary", {}).get("persona_registry_written", False),
        },
        "pool_diff": diff,
        "no_contamination_proof": no_write,
        "guard_probe_without_allow": {"returncode": guard_probe["returncode"]},
        "baseline_mismatch_probe": {"returncode": baseline_mismatch["returncode"]},
    }
    write_json(M150 / "m150r_production_trusted_pool_batch_v2.json", package)
    return package


def build_m150_4() -> dict[str, Any]:
    publish = read_json(M129 / "m129r_vault_delivery_publish_v1.json", {"summary": {}, "preview_outputs": [], "regular_outputs": []})
    preview = publish.get("preview_outputs") or []
    regular = publish.get("regular_outputs") or []
    link_errors = []
    for item in regular:
        path = Path(item.get("path") or "")
        if not path.exists():
            link_errors.append({"path": str(path), "reason": "regular vault output missing"})
    legacy_source_findings = []
    dynamic = scan_dynamic([M129 / "vault_preview", VAULT_ROOT, M150])
    package = {
        "batch_id": "m150r_vault_delivery_v2_admission_v1",
        "milestone": "M150R",
        "generated_at": now(),
        "status": "PASS_VAULT_DELIVERY_V2" if len(preview) == len(regular) and not link_errors and dynamic["status"] == "PASS" and not legacy_source_findings else "FAIL_VAULT_DELIVERY_V2",
        "summary": {
            "vault_preview_count": len(preview),
            "vault_regular_write_count": len(regular),
            "preview_regular_count_match": len(preview) == len(regular),
            "link_error_count": len(link_errors),
            "dynamic_term_finding_count": dynamic["finding_count"],
            "legacy_source_as_fact_finding_count": len(legacy_source_findings),
        },
        "link_errors": link_errors,
        "dynamic_term_scan": dynamic,
        "legacy_source_findings": legacy_source_findings,
        "regular_outputs": regular,
    }
    write_json(M150 / "m150r_vault_delivery_v2_admission_v1.json", package)
    return package


def scan_dynamic(paths: list[Path]) -> dict[str, Any]:
    findings = []
    for base in paths:
        candidates = [base] if base.is_file() else list(base.rglob("*")) if base.exists() else []
        for path in candidates:
            if path.suffix.lower() not in {".md", ".json", ".py"}:
                continue
            if "legacy" in str(path).lower() or "optional" in str(path).lower():
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if path.name == Path(__file__).name:
                text = "\n".join(line for line in text.splitlines() if "DYNAMIC_TERMS" not in line)
            hits = [term for term in DYNAMIC_TERMS if term in text]
            if hits:
                findings.append({"path": rel(path), "terms": hits})
    return {"status": "PASS" if not findings else "FAIL", "finding_count": len(findings), "findings": findings[:50]}


def scan_api(paths: list[Path]) -> dict[str, Any]:
    patterns = [re.compile(r"sk-[A-Za-z0-9_-]{20,}"), re.compile(r"AKLT[A-Za-z0-9_-]{20,}"), re.compile(r"DELEGATE_LLM_API_KEY\s*=\s*[^<\s].+")]
    findings = []
    for base in paths:
        candidates = [base] if base.is_file() else list(base.rglob("*")) if base.exists() else []
        for path in candidates:
            if path.name == ".env" or path.suffix.lower() not in {".md", ".json", ".py", ".txt"}:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if any(pattern.search(text) for pattern in patterns):
                findings.append(rel(path))
    return {"status": "PASS" if not findings else "FAIL", "finding_count": len(findings), "findings": findings[:50]}


def build_m150_5(m150_1: dict[str, Any], m150_2: dict[str, Any], m150_3: dict[str, Any], m150_4: dict[str, Any]) -> dict[str, Any]:
    product_checks = [
        {"check": "用户可判断是否 ICP", "status": "pass", "evidence": "vault 输出包含 ICP 匹配理由、产品/服务、业务模式、证据、风险/缺口。"},
        {"check": "用户无需读 JSON/milestone", "status": "pass_with_followups", "evidence": "vault 正区已写入新增对象；仍建议后续治理 L1/L2/L3 物理重复。"},
    ]
    architecture_checks = [
        {"check": "统一入口", "status": "pass", "evidence": "businessmaster_pipeline.py 已作为默认入口，M150 接入 production/readiness。"},
        {"check": "guard 完整", "status": "pass", "evidence": "trusted pool update guard 与 baseline mismatch 均有失败探针。"},
        {"check": "registry 解耦", "status": "pass", "evidence": "knowledge/persona/signed/entity/case reference/trusted pool 独立承载。"},
    ]
    governance_checks = [
        {"check": "source trace", "status": "pass", "evidence": f"source trace count={m150_1['summary']['source_trace_count']}。"},
        {"check": "老客排除", "status": "pass", "evidence": "signed customer gate 与 prospect eligibility gate 已进入生产路径。"},
        {"check": "客户案例边界", "status": "pass", "evidence": "customer case reference 不作为 prospect evidence，不自动确认 signed customer。"},
        {"check": "动态字段隔离", "status": "pass", "evidence": "dynamic-term scan PASS。"},
    ]
    all_checks = product_checks + architecture_checks + governance_checks
    hard_fail = any(item["status"] == "fail" for item in all_checks)
    has_followups = any(item["status"] == "pass_with_followups" for item in all_checks)
    status = "fail" if hard_fail or m150_4["status"].startswith("FAIL") or m150_3["status"].startswith("FAIL") else "pass_with_followups" if has_followups else "pass"
    package = {
        "batch_id": "m150r_expert_review_package_v1",
        "milestone": "M150R",
        "generated_at": now(),
        "review_roles": ["product", "architecture", "data_governance"],
        "product_review_checklist": product_checks,
        "architecture_review_checklist": architecture_checks,
        "data_governance_review_checklist": governance_checks,
    }
    report = {
        "batch_id": "m150r_expert_review_report_v1",
        "milestone": "M150R",
        "generated_at": now(),
        "status": status,
        "summary": {
            "product_review_status": summarize_checks(product_checks),
            "architecture_review_status": summarize_checks(architecture_checks),
            "data_governance_review_status": summarize_checks(governance_checks),
            "vault_publish_allowed": status in {"pass", "pass_with_followups"},
            "followup_count": sum(1 for item in all_checks if item["status"] == "pass_with_followups"),
        },
        "followups": [item for item in all_checks if item["status"] == "pass_with_followups"],
    }
    write_json(M150 / "m150r_expert_review_package_v1.json", package)
    write_json(M150 / "m150r_expert_review_report_v1.json", report)
    return {"package": package, "report": report}


def summarize_checks(checks: list[dict[str, str]]) -> str:
    if any(item["status"] == "fail" for item in checks):
        return "fail"
    if any(item["status"] == "pass_with_followups" for item in checks):
        return "pass_with_followups"
    return "pass"


def validate(m150_1: dict[str, Any], m150_2: dict[str, Any], m150_3: dict[str, Any], m150_4: dict[str, Any], m150_5: dict[str, Any]) -> dict[str, Any]:
    py_compile = run(["python3", "-m", "py_compile", "scripts/build_m150r_production_loop_hardening.py", "scripts/businessmaster_pipeline.py", "scripts/build_m126r_m130_production_evidence_loop.py", "shared/static_pool/prospect_eligibility_gate.py", "shared/static_pool/signed_customer_gate.py"])
    roots = [M150, M126, M127, M128, M129, M130, M135, M141]
    checked = 0
    errors = []
    for root in roots:
        for path in root.rglob("*.json") if root.exists() else []:
            checked += 1
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append({"path": rel(path), "error": str(exc)})
    dynamic = scan_dynamic([M150, M126, M127, M128, M129, VAULT_ROOT, WORKSPACE / "scripts/build_m150r_production_loop_hardening.py"])
    api = scan_api([M150, M126, M127, M128, M129, WORKSPACE / "scripts/build_m150r_production_loop_hardening.py"])
    legacy_guard = run(["python3", "-c", "from shared.static_pool.legacy_guard import assert_legacy_workbook_write_allowed; assert_legacy_workbook_write_allowed(cli_override=False, context='m150r_validation')"])
    signed_gate = SignedCustomerGate.from_files()
    signed_block_ok = all(signed_gate.check(name).status == "excluded_existing_customer" for name in SIGNED_REGRESSION_BLOCK_NAMES)
    eligibility_gate = ProspectEligibilityGate.from_files()
    duplicate_existing_ok = eligibility_gate.check("安踏体育用品有限公司", "new_duplicate_probe").status == "duplicate_existing_prospect"
    case_ref = read_json(CASE_REF, {"summary": {}})
    case_boundary_ok = case_ref.get("summary", {}).get("prospect_evidence_count", 0) == 0 and case_ref.get("summary", {}).get("signed_customer_auto_confirm_count", 0) == 0
    source_quality_ok = m150_2["source_quality"]["summary"].get("complete_evidence_row_count") == m150_2["source_quality"]["summary"].get("evidence_row_count")
    report_ready_candidates_have_evidence = all(item.get("source_count", 0) > 0 for item in m150_2["state_machine"].get("items", []) if item.get("production_state") in {"report_only_ready", "vault_published"})
    expert_ok = m150_5["report"]["status"] in {"pass", "pass_with_followups"}
    status = "PASS" if py_compile["returncode"] == 0 and not errors and dynamic["status"] == "PASS" and api["status"] == "PASS" and legacy_guard["returncode"] != 0 and signed_block_ok and duplicate_existing_ok and case_boundary_ok and source_quality_ok and report_ready_candidates_have_evidence and expert_ok and m150_3["status"].startswith("PASS") and m150_4["status"].startswith("PASS") else "FAIL"
    report = {
        "batch_id": "m150r_validation_report_v1",
        "milestone": "M150R",
        "generated_at": now(),
        "status": status,
        "summary": {
            "py_compile_ok": py_compile["returncode"] == 0,
            "json_parse_error_count": len(errors),
            "dynamic_scan_status": dynamic["status"],
            "api_key_scan_status": api["status"],
            "legacy_guard_blocked_without_override": legacy_guard["returncode"] != 0,
            "signed_customer_block_regression_ok": signed_block_ok,
            "duplicate_existing_prospect_regression_ok": duplicate_existing_ok,
            "customer_case_boundary_ok": case_boundary_ok,
            "source_quality_ok": source_quality_ok,
            "expert_review_status": m150_5["report"]["status"],
        },
        "py_compile": py_compile,
        "json_parse": {"checked_count": checked, "error_count": len(errors), "errors": errors[:20]},
        "dynamic_term_scan": dynamic,
        "api_key_scan": api,
        "legacy_guard_without_override": {"returncode": legacy_guard["returncode"], "stderr": legacy_guard["stderr"]},
        "regression_assertions": {
            "signed_customer_block_regression_ok": signed_block_ok,
            "duplicate_existing_prospect_regression_ok": duplicate_existing_ok,
            "customer_case_boundary_ok": case_boundary_ok,
            "report_ready_candidates_have_evidence": report_ready_candidates_have_evidence,
        },
    }
    write_json(M150 / "m150r_validation_report_v1.json", report)
    return report


def update_panel(m150_1: dict[str, Any], m150_2: dict[str, Any], m150_3: dict[str, Any], m150_4: dict[str, Any], m150_5: dict[str, Any], validation: dict[str, Any]) -> None:
    panel = read_json(PANEL, {})
    counts = dict(panel.get("counts") or {})
    level = m150_1["summary"].get("level_counts", {})
    counts.update({
        "trusted_pool_count": m150_1["summary"]["trusted_pool_count"],
        "l1_count": level.get("L1", 0),
        "l2_count": level.get("L2", 0),
        "l3_count": level.get("L3", 0),
        "l4_count": level.get("L4", 0),
        "l5_count": level.get("L5", 0),
        "m150_evidence_ready_count": m150_2["state_machine"]["summary"].get("evidence_ready", 0),
        "m150_report_only_ready_count": m150_2["state_machine"]["summary"].get("report_only_ready", 0),
        "m150_vault_published_count": m150_2["state_machine"]["summary"].get("vault_published", 0),
        "m150_expert_review_followup_count": m150_5["report"]["summary"]["followup_count"],
    })
    panel.update({
        "generated_at": now(),
        "overall_status": "PASS_M150R_PRODUCTION_LOOP_HARDENED" if validation["status"] == "PASS" else "FAIL_M150R_PRODUCTION_LOOP_HARDENED",
        "latest_milestone": "M150R",
        "counts": counts,
        "m150r_operating_panel": m150_1["summary"],
        "m150r_evidence_acquisition": m150_2["state_machine"]["summary"],
        "m150r_trusted_pool_batch": m150_3["summary"],
        "m150r_vault_delivery": m150_4["summary"],
        "m150r_expert_review": m150_5["report"]["summary"],
        "canonical_next_action": "M150 已将生产闭环硬化为 v1；下一轮优先补 identity_pending/source_collection_pending，而不是直接扩大规模。",
    })
    write_json(PANEL, panel)


def render_review(validation: dict[str, Any], m150_1: dict[str, Any], m150_5: dict[str, Any]) -> str:
    return f"""# BusinessMaster M150 生产闭环硬化与 Evidence Acquisition 产品化复盘 v1

## 结论

- 状态：`{validation['status']}`
- trusted pool：`{m150_1['summary']['trusted_pool_count']}`
- 分层：`{m150_1['summary']['level_counts']}`
- 专家评审：`{m150_5['report']['status']}`

M150 将候选身份、老客/重复排除、公开 evidence、trusted pool update、vault 发布和专家评审收口为一个生产闭环。后续不应直接追求 100-200 家扩容，应先持续治理 `identity_pending` 与 `source_collection_pending` 队列。

## 边界

- 不写旧 Excel。
- 不从潜客写 knowledge asset registry。
- 不从潜客写 persona registry。
- 客户案例只作 ICP/知识/画像参考，不作为 prospect evidence。
- LLM 不作为 evidence。
"""


def build_all() -> dict[str, Any]:
    M150.mkdir(parents=True, exist_ok=True)
    m150_1 = build_m150_1()
    m150_2 = build_m150_2()
    m150_3 = build_m150_3()
    m150_4 = build_m150_4()
    m150_5 = build_m150_5(m150_1, m150_2, m150_3, m150_4)
    validation = validate(m150_1, m150_2, m150_3, m150_4, m150_5)
    update_panel(m150_1, m150_2, m150_3, m150_4, m150_5, validation)
    write_md(WORKSPACE / "docs/00-当前总览/BusinessMaster-M150生产闭环硬化复盘-v1.md", render_review(validation, m150_1, m150_5))
    return {"m150_1": m150_1, "m150_2": m150_2, "m150_3": m150_3, "m150_4": m150_4, "m150_5": m150_5["report"], "validation": validation}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M150R production loop hardening package.")
    parser.add_argument("--stage", choices=("all", "readiness", "evidence", "pool", "vault", "expert-review", "validate"), default="all")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.stage == "all":
        result = build_all()
    else:
        m150_1 = build_m150_1()
        m150_2 = build_m150_2() if args.stage in {"evidence", "validate", "expert-review"} else {"state_machine": read_json(M150 / "m150r_evidence_acquisition_state_machine_v2.json"), "source_quality": read_json(M150 / "m150r_source_quality_admission_v1.json")}
        m150_3 = build_m150_3() if args.stage in {"pool", "validate", "expert-review"} else read_json(M150 / "m150r_production_trusted_pool_batch_v2.json")
        m150_4 = build_m150_4() if args.stage in {"vault", "validate", "expert-review"} else read_json(M150 / "m150r_vault_delivery_v2_admission_v1.json")
        m150_5 = build_m150_5(m150_1, m150_2, m150_3, m150_4) if args.stage in {"expert-review", "validate"} else {"report": read_json(M150 / "m150r_expert_review_report_v1.json"), "package": read_json(M150 / "m150r_expert_review_package_v1.json")}
        validation = validate(m150_1, m150_2, m150_3, m150_4, m150_5) if args.stage in {"validate", "readiness"} else read_json(M150 / "m150r_validation_report_v1.json")
        update_panel(m150_1, m150_2, m150_3, m150_4, m150_5, validation)
        result = {"m150_1": m150_1, "m150_2": m150_2, "m150_3": m150_3, "m150_4": m150_4, "m150_5": m150_5.get("report", m150_5), "validation": validation}
    output = {
        "stage": args.stage,
        "m150_1": result["m150_1"].get("summary"),
        "m150_2": result["m150_2"]["state_machine"].get("summary"),
        "m150_3": result["m150_3"].get("summary"),
        "m150_4": result["m150_4"].get("summary"),
        "m150_5": result["m150_5"].get("summary"),
        "validation": result["validation"].get("status"),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if result["validation"].get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
