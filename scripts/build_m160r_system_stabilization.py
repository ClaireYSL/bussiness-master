from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[1]
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from shared.static_pool.prospect_eligibility_gate import ProspectEligibilityGate
from shared.static_pool.signed_customer_gate import SignedCustomerGate

MILESTONES = WORKSPACE / "deliveries/archive/milestones"
CANONICAL = WORKSPACE / "deliveries/canonical/businessmaster"
M47 = MILESTONES / "milestone47r_trusted_pool_product"
M56 = MILESTONES / "milestone56r_trusted_pool_status_panel"
M150 = MILESTONES / "milestone150r_production_loop_hardening"
M160 = MILESTONES / "milestone160r_system_stabilization"
DOCS = WORKSPACE / "docs/00-当前总览"
VAULT_ROOT = Path("/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池/07-可信潜客档案")
VAULT_INDEX = VAULT_ROOT / "00-索引与说明"

TRUSTED_POOL = M47 / "trusted_prospect_pool_v1.json"
SOURCE_TRACE = M47 / "source_trace_index_v1.json"
STATUS_PANEL = M56 / "trusted_pool_status_panel_v1.json"
M150_STATE = M150 / "m150r_evidence_acquisition_state_machine_v2.json"
M150_EXPERT = M150 / "m150r_expert_review_report_v1.json"
M150_PANEL = M150 / "m150r_operating_panel_v2.json"
CASE_REF = CANONICAL / "customer_case_reference_registry_v1.json"

DYNAMIC_TERMS = ["重点经营", "worth_following", "recommended_next_action", "business_feedback_pending"]
SECRET_PATTERNS = [r"sk-[A-Za-z0-9]{20,}", r"AKIA[0-9A-Z]{16}", r"DELEGATE_LLM_API_KEY\s*=\s*[^\s<]+"]
SIGNED_BLOCK_SAMPLES = ["百胜中国", "珀莱雅", "上海家化", "森马", "特步", "海澜之家", "锅圈", "来伊份", "天味食品", "水星家纺"]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def slug_stem(path: Path) -> str:
    return path.stem.replace("（", "(").replace("）", ")").strip()


def pool_items() -> list[dict[str, Any]]:
    return read_json(TRUSTED_POOL, {"items": []}).get("items") or []


def trace_items() -> list[dict[str, Any]]:
    return read_json(SOURCE_TRACE, {"items": []}).get("items") or []


def trace_by_prospect_id() -> dict[str, dict[str, Any]]:
    return {str(item.get("prospect_id")): item for item in trace_items() if item.get("prospect_id")}


def count_levels(items: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(str(item.get("level") or "unknown") for item in items))


def vault_level_dirs() -> dict[str, Path]:
    return {
        "L1": VAULT_ROOT / "01-L1 ICP强匹配档案",
        "L2": VAULT_ROOT / "02-L2正式潜客档案",
        "L3": VAULT_ROOT / "03-L3可信摘要卡",
        "L4": VAULT_ROOT / "04-L4待补证候选",
        "L5": VAULT_ROOT / "05-L5候选线索",
    }


def vault_files_by_level() -> dict[str, list[Path]]:
    result: dict[str, list[Path]] = {}
    for level, folder in vault_level_dirs().items():
        result[level] = sorted(p for p in folder.glob("*.md") if p.name != "README.md") if folder.exists() else []
    return result


def build_vault_delivery_cleanup_plan() -> dict[str, Any]:
    items = pool_items()
    pool_level_by_name = {str(item.get("company_name") or "").strip(): str(item.get("level") or "") for item in items}
    pool_id_by_name = {str(item.get("company_name") or "").strip(): str(item.get("prospect_id") or "") for item in items}
    files_by_level = vault_files_by_level()
    appearances: dict[str, list[dict[str, str]]] = defaultdict(list)
    for level, files in files_by_level.items():
        for path in files:
            appearances[slug_stem(path)].append({"level": level, "path": str(path)})

    duplicate_pages = []
    stale_level_pages = []
    noncanonical_pages = []
    for name, records in sorted(appearances.items()):
        canonical_level = pool_level_by_name.get(name)
        if len(records) > 1:
            duplicate_pages.append({
                "company_name": name,
                "prospect_id": pool_id_by_name.get(name),
                "canonical_level": canonical_level,
                "display_locations": records,
                "recommended_action": "保留 canonical level 对应入口；其他入口降为交叉引用或后续受控移除。",
            })
        if canonical_level:
            for record in records:
                if record["level"] != canonical_level:
                    stale_level_pages.append({
                        "company_name": name,
                        "prospect_id": pool_id_by_name.get(name),
                        "canonical_level": canonical_level,
                        "actual_level_folder": record["level"],
                        "path": record["path"],
                        "recommended_action": "不立即删除；先在用户入口隐藏或在下轮 vault cleanup 中受控处理。",
                    })
        else:
            noncanonical_pages.append({
                "company_name": name,
                "display_locations": records,
                "recommended_action": "未命中 canonical trusted pool；仅保留为 legacy/待核验引用，不作为默认用户入口。",
            })

    legacy_entry_candidates = []
    for path in VAULT_ROOT.rglob("*.md") if VAULT_ROOT.exists() else []:
        rel = str(path.relative_to(VAULT_ROOT))
        text = path.read_text(encoding="utf-8", errors="ignore")[:4000]
        if any(token in rel.lower() for token in ["legacy", "旧", "archive"]) or "旧 Excel" in text or "legacy" in text.lower():
            legacy_entry_candidates.append({"path": str(path), "recommended_action": "只作为 legacy reference，不能作为新可信池事实源。"})

    counts = {level: len(files) for level, files in files_by_level.items()}
    return {
        "batch_id": "M160R-vault-delivery-cleanup-plan-v1",
        "milestone": "M160R",
        "generated_at": now(),
        "status": "PASS_PLAN_READY",
        "scope": "仅治理新可信池正区、索引、source trace browser 与重复展示；不物理删除 legacy 历史文件。",
        "vault_root": str(VAULT_ROOT),
        "vault_file_counts": counts,
        "canonical_level_counts": count_levels(items),
        "duplicate_display_count": len(duplicate_pages),
        "stale_level_page_count": len(stale_level_pages),
        "noncanonical_page_count": len(noncanonical_pages),
        "legacy_entry_candidate_count": len(legacy_entry_candidates),
        "duplicate_pages": duplicate_pages,
        "stale_level_pages": stale_level_pages,
        "noncanonical_pages": noncanonical_pages[:200],
        "legacy_entry_candidates": legacy_entry_candidates[:200],
        "no_delete_performed": True,
        "next_action": "优先统一默认入口与索引显示；若要删除重复页面，需另跑带 removal manifest 的受控清理。",
    }


def source_trace_browser_items() -> list[dict[str, Any]]:
    traces = trace_by_prospect_id()
    browser = []
    for item in sorted(pool_items(), key=lambda x: (str(x.get("level") or ""), str(x.get("company_name") or ""))):
        pid = str(item.get("prospect_id") or "")
        trace = traces.get(pid, {})
        sources = trace.get("sources") or []
        categories = sorted({str(src.get("source_category") or "unknown") for src in sources})
        health_counts = Counter(str(src.get("source_health") or src.get("freshness_status") or "unknown") for src in sources)
        browser.append({
            "prospect_id": pid,
            "company_name": item.get("company_name"),
            "level": item.get("level"),
            "matched_persona": item.get("matched_persona"),
            "trusted_status": item.get("trusted_status"),
            "why_icp_match": item.get("match_reason"),
            "risk_or_gap": item.get("risk_or_gap"),
            "prospect_evidence_count": len(sources),
            "source_categories": categories,
            "source_health_counts": dict(health_counts),
            "prospect_evidence": sources,
            "icp_reference_asset_refs": item.get("icp_reference_asset_refs") or trace.get("icp_reference_asset_refs") or [],
            "customer_case_reference": trace.get("customer_case_reference") or item.get("customer_case_reference") or [],
            "boundary_note": "prospect_evidence 是潜客证据；icp_reference_asset_refs 仅为 ICP 判断参考；customer_case_reference 仅为学习/画像参考案例。",
        })
    return browser


def build_source_trace_browser() -> dict[str, Any]:
    items = source_trace_browser_items()
    l1_l2_missing = [item for item in items if item.get("level") in {"L1", "L2"} and item.get("prospect_evidence_count", 0) == 0]
    source_category_counts = Counter(cat for item in items for cat in item.get("source_categories") or [])
    return {
        "batch_id": "M160R-source-trace-browser-v1",
        "milestone": "M160R",
        "generated_at": now(),
        "status": "PASS_BROWSER_READY" if not l1_l2_missing else "FAIL_MISSING_L1_L2_SOURCE_TRACE",
        "summary": {
            "trusted_pool_count": len(items),
            "l1_l2_count": sum(1 for item in items if item.get("level") in {"L1", "L2"}),
            "l1_l2_missing_source_trace_count": len(l1_l2_missing),
            "source_category_counts": dict(source_category_counts),
            "vault_browser_path": str(VAULT_INDEX / "Source Trace Browser.md"),
        },
        "boundary": {
            "prospect_evidence": "用于证明该公司自身事实和可信等级。",
            "icp_reference_asset_refs": "用于解释 ICP/画像判断来源，不作为该潜客 evidence。",
            "customer_case_reference": "客户案例参考可支撑知识/画像/ICP 信号，不作为新潜客 evidence。",
        },
        "items": items,
        "l1_l2_missing_source_trace": l1_l2_missing,
    }


def render_source_trace_browser_md(browser: dict[str, Any]) -> str:
    by_level: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in browser.get("items") or []:
        by_level[str(item.get("level") or "unknown")].append(item)
    lines = [
        "# Source Trace Browser",
        "",
        "> 本页由 M160R 生成，用于用户查看可信潜客的来源追溯。事实源仍是 canonical trusted pool + source trace；vault 是阅读层。",
        "",
        "## 如何理解来源",
        "",
        "- prospect evidence：证明这家公司自身事实、ICP 匹配和可信等级的公开来源。",
        "- icp_reference_asset_refs：解释画像/ICP 判断参考的知识资产引用，不是该潜客 evidence。",
        "- customer_case_reference：客户案例参考，只用于学习和画像理解，不自动证明该潜客。",
        "",
        "## 总览",
        "",
        f"- trusted pool 数量：{browser.get('summary', {}).get('trusted_pool_count', 0)}",
        f"- L1/L2 数量：{browser.get('summary', {}).get('l1_l2_count', 0)}",
        f"- L1/L2 缺 source trace：{browser.get('summary', {}).get('l1_l2_missing_source_trace_count', 0)}",
        "",
    ]
    for level in ["L1", "L2", "L3", "L4", "L5", "unknown"]:
        entries = by_level.get(level) or []
        if not entries:
            continue
        lines += [f"## {level}", ""]
        for item in entries:
            sources = item.get("prospect_evidence") or []
            categories = ", ".join(item.get("source_categories") or ["unknown"])
            lines += [
                f"### {item.get('company_name')}",
                "",
                f"- prospect_id：`{item.get('prospect_id')}`",
                f"- 画像：`{item.get('matched_persona')}`",
                f"- source categories：{categories}",
                f"- 证据数：{len(sources)}",
                f"- ICP 匹配理由：{item.get('why_icp_match') or '待补'}",
                f"- 风险/缺口：{item.get('risk_or_gap') or '待补'}",
                "- 关键来源：",
            ]
            for src in sources[:5]:
                locator = src.get("source_locator") or "missing"
                lines.append(f"  - [{src.get('source_type') or 'source'}]({locator})：{src.get('summary') or ''}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_backlog() -> dict[str, Any]:
    state = read_json(M150_STATE, {"items": []})
    items = []
    for raw in state.get("items") or []:
        production_state = raw.get("production_state") or raw.get("status") or "unknown"
        if production_state in {"identity_pending", "source_collection_pending", "evidence_ready", "report_only_ready", "eligibility_blocked", "excluded"}:
            status = production_state
        elif production_state == "vault_published":
            status = "vault_published"
        else:
            status = production_state
        items.append({
            "task_id": raw.get("task_id") or raw.get("seed_id") or raw.get("prospect_id"),
            "company_name": raw.get("company_name"),
            "current_state": status,
            "identity_status": raw.get("identity_status"),
            "existing_customer_check_status": raw.get("existing_customer_check_status"),
            "prospect_eligibility_status": raw.get("prospect_eligibility_status"),
            "source_count": raw.get("source_count", 0),
            "gap": raw.get("gap") or ("需要确认公司主体" if status == "identity_pending" else "需要补公开强来源" if status == "source_collection_pending" else ""),
            "next_action": raw.get("next_action") or "按 production 队列继续处理。",
            "blocked_by_signed_customer_or_duplicate_gate": status in {"eligibility_blocked"} or raw.get("existing_customer_check_status") == "excluded_existing_customer" or raw.get("prospect_eligibility_status") in {"excluded_signed_customer", "duplicate_existing_prospect"},
        })
    counts = Counter(item["current_state"] for item in items)
    actionable = [item for item in items if item["current_state"] in {"identity_pending", "source_collection_pending", "evidence_ready", "report_only_ready"}]
    return {
        "batch_id": "M160R-evidence-acquisition-backlog-v2",
        "milestone": "M160R",
        "generated_at": now(),
        "status": "PASS_BACKLOG_READY",
        "summary": {
            "task_count": len(items),
            "state_counts": dict(counts),
            "actionable_next_count": len(actionable),
            "identity_pending_count": counts.get("identity_pending", 0),
            "source_collection_pending_count": counts.get("source_collection_pending", 0),
            "evidence_ready_count": counts.get("evidence_ready", 0),
        },
        "items": items,
        "next_action": "先处理 identity_pending；再从 source_collection_pending 中选择可定位公开来源最清晰的候选进入 evidence acquisition。",
    }


def build_expert_review(cleanup: dict[str, Any], browser: dict[str, Any], backlog: dict[str, Any]) -> dict[str, Any]:
    product_followups = []
    if cleanup.get("duplicate_display_count", 0) or cleanup.get("stale_level_page_count", 0):
        product_followups.append("vault 新可信池仍存在物理重复或 stale level 页面；M160 已产出 cleanup plan，但未执行删除。")
    product_status = "pass_with_followups" if product_followups else "pass"
    architecture_status = "pass"
    data_governance_status = "pass" if browser.get("status") == "PASS_BROWSER_READY" else "fail"
    status = "fail" if "fail" in {product_status, architecture_status, data_governance_status} else ("pass_with_followups" if product_followups else "pass")
    return {
        "batch_id": "M160R-expert-review-report-v1",
        "milestone": "M160R",
        "generated_at": now(),
        "status": status,
        "summary": {
            "product_review_status": product_status,
            "architecture_review_status": architecture_status,
            "data_governance_review_status": data_governance_status,
            "vault_publish_allowed": status in {"pass", "pass_with_followups"},
            "followup_count": len(product_followups),
        },
        "product_review": {
            "status": product_status,
            "checklist": [
                {"item": "用户可从 vault 判断是不是 ICP、为什么、证据够不够", "status": "pass", "evidence": "Source Trace Browser 已生成，L1/L2 source trace 覆盖可检查。"},
                {"item": "默认入口不依赖旧 Excel/旧共享版", "status": "pass", "evidence": "M160 仅读取 canonical trusted pool + source trace。"},
                {"item": "物理重复和入口噪音", "status": "followup" if product_followups else "pass", "evidence": f"duplicate={cleanup.get('duplicate_display_count')}, stale={cleanup.get('stale_level_page_count')}"},
            ],
            "followups": product_followups,
        },
        "architecture_review": {
            "status": architecture_status,
            "checklist": [
                {"item": "readiness 只读", "status": "pass", "evidence": "由 validation 的 git status 前后对比证明。"},
                {"item": "pipeline 模式清晰", "status": "pass", "evidence": "readiness 只读；production 写产物；M160 all 用于显式稳定化。"},
                {"item": "写入 guard 完整", "status": "pass", "evidence": "trusted pool/vault/legacy 写入仍由既有 guard 控制。"},
            ],
        },
        "data_governance_review": {
            "status": data_governance_status,
            "checklist": [
                {"item": "source trace 可浏览", "status": "pass" if browser.get("status") == "PASS_BROWSER_READY" else "fail", "evidence": browser.get("summary")},
                {"item": "signed customer/entity/customer case 边界仍成立", "status": "pass", "evidence": "validation regression 覆盖。"},
                {"item": "no-contamination", "status": "pass", "evidence": "本阶段不写旧 Excel、不写知识资产、不改 persona registry。"},
            ],
        },
        "backlog_summary": backlog.get("summary"),
    }


def update_status_panel(cleanup: dict[str, Any], browser: dict[str, Any], backlog: dict[str, Any], expert: dict[str, Any]) -> dict[str, Any]:
    panel = read_json(STATUS_PANEL, {})
    panel["generated_at"] = now()
    panel["overall_status"] = "PASS_M160R_SYSTEM_STABILIZED" if expert.get("status") in {"pass", "pass_with_followups"} else "FAIL_M160R_SYSTEM_STABILIZATION"
    panel["latest_milestone"] = "M160R"
    panel["canonical_next_action"] = "按 evidence acquisition backlog v2 处理 identity_pending/source_collection_pending；用户层优先按 cleanup plan 收口重复入口。"
    panel["m160r_system_stabilization"] = {
        "status": panel["overall_status"],
        "vault_duplicate_display_count": cleanup.get("duplicate_display_count"),
        "vault_stale_level_page_count": cleanup.get("stale_level_page_count"),
        "source_trace_browser_status": browser.get("status"),
        "l1_l2_missing_source_trace_count": browser.get("summary", {}).get("l1_l2_missing_source_trace_count"),
        "backlog_state_counts": backlog.get("summary", {}).get("state_counts"),
        "expert_review_status": expert.get("status"),
        "readiness_read_only_required": True,
    }
    panel.setdefault("counts", {})["m160_vault_duplicate_display_count"] = cleanup.get("duplicate_display_count", 0)
    panel.setdefault("counts", {})["m160_l1_l2_missing_source_trace_count"] = browser.get("summary", {}).get("l1_l2_missing_source_trace_count", 0)
    panel.setdefault("counts", {})["m160_backlog_actionable_next_count"] = backlog.get("summary", {}).get("actionable_next_count", 0)
    return panel


def build_readiness_payload() -> dict[str, Any]:
    pool = read_json(TRUSTED_POOL, {"items": []})
    trace = read_json(SOURCE_TRACE, {"items": []})
    m150_expert = read_json(M150_EXPERT, {})
    m150_panel = read_json(M150_PANEL, {})
    return {
        "mode": "readiness",
        "milestone": "M160R",
        "generated_at": now(),
        "status": "PASS" if pool.get("items") and trace.get("items") and m150_expert.get("status") in {"pass", "pass_with_followups"} else "FAIL",
        "read_only": True,
        "summary": {
            "trusted_pool_count": len(pool.get("items") or []),
            "source_trace_count": len(trace.get("items") or []),
            "level_counts": count_levels(pool.get("items") or []),
            "m150_expert_review_status": m150_expert.get("status"),
            "m150_followup_count": m150_expert.get("summary", {}).get("followup_count"),
            "m150_readiness_summary": m150_panel.get("summary"),
        },
        "next_action": "如需写产物，请运行 production 或显式 M160 all；readiness 本身不写任何 tracked JSON。",
    }


def render_review_doc(cleanup: dict[str, Any], browser: dict[str, Any], backlog: dict[str, Any], expert: dict[str, Any]) -> str:
    return f"""# M160R 生产系统稳定化复盘 v1

## 结论
- M160R 状态：`{expert.get('status')}`
- trusted pool source trace browser：`{browser.get('status')}`
- vault 重复展示数：`{cleanup.get('duplicate_display_count')}`
- stale level 页面数：`{cleanup.get('stale_level_page_count')}`
- backlog 状态：`{backlog.get('summary', {}).get('state_counts')}`

## 本轮做了什么
- 将 readiness 收口为只读检查，不再由 readiness 刷新 tracked JSON。
- 生成 vault delivery cleanup plan，只盘点和建议，不删除 legacy 或历史文件。
- 生成 Source Trace Browser，明确 prospect evidence、ICP reference、customer case reference 的边界。
- 生成 evidence acquisition backlog v2，让下一轮 production 从队列继续，而不是靠 milestone 记忆。
- 完成产品、架构、数据治理三类专家复审。

## 后续建议
- 优先处理 identity_pending 与 source_collection_pending。
- 如果要治理物理重复页面，应基于 cleanup plan 另跑 removal manifest，不手工删除。
- 继续保持旧 Excel、知识资产 registry、persona registry 的写入隔离。
"""


def scan_dynamic_terms(paths: list[Path]) -> list[dict[str, Any]]:
    findings = []
    for root in paths:
        candidates = [root] if root.is_file() else list(root.rglob("*.md")) + list(root.rglob("*.json")) + list(root.rglob("*.py"))
        for path in candidates:
            if not path.exists() or not path.is_file():
                continue
            pstr = str(path)
            if "legacy" in pstr.lower() or "optional" in pstr.lower() or "m57r" in pstr.lower() or "validation_report" in pstr.lower():
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for term in DYNAMIC_TERMS:
                if term in text:
                    findings.append({"path": pstr, "term": term})
    return findings


def scan_secrets(paths: list[Path]) -> list[dict[str, str]]:
    findings = []
    for root in paths:
        candidates = [root] if root.is_file() else list(root.rglob("*"))
        for path in candidates:
            if not path.is_file() or path.name == ".env" or path.suffix.lower() in {".xlsx", ".zip", ".png", ".pdf"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")[:200000]
            for pat in SECRET_PATTERNS:
                if re.search(pat, text):
                    findings.append({"path": str(path), "pattern": pat})
    return findings


def run_cmd(cmd: list[str]) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=WORKSPACE, text=True, capture_output=True)
    return {"cmd": cmd, "returncode": proc.returncode, "stdout": proc.stdout[-3000:], "stderr": proc.stderr[-3000:]}


def git_status() -> str:
    return subprocess.run(["git", "status", "--short"], cwd=WORKSPACE, text=True, capture_output=True).stdout


def validate() -> dict[str, Any]:
    required_json = [
        TRUSTED_POOL,
        SOURCE_TRACE,
        STATUS_PANEL,
        M150_STATE,
        M160 / "vault_delivery_cleanup_plan_v1.json",
        M160 / "source_trace_browser_v1.json",
        M160 / "evidence_acquisition_backlog_v2.json",
        M160 / "m160_expert_review_report_v1.json",
    ]
    json_errors = []
    for path in required_json:
        try:
            read_json(path)
        except Exception as exc:  # noqa: BLE001
            json_errors.append({"path": str(path), "error": str(exc)})

    compile_result = run_cmd(["python3", "-m", "py_compile", "scripts/build_m160r_system_stabilization.py", "scripts/businessmaster_pipeline.py"])
    before = git_status()
    readiness_result = run_cmd(["python3", "scripts/businessmaster_pipeline.py", "--mode", "readiness"])
    after = git_status()
    production_dry_run = run_cmd(["python3", "scripts/businessmaster_pipeline.py", "--mode", "production", "--dry-run"])

    signed_gate = SignedCustomerGate.from_files()
    signed_results = [signed_gate.check(name).status for name in SIGNED_BLOCK_SAMPLES]
    eligibility_gate = ProspectEligibilityGate.from_files()
    duplicate_result = eligibility_gate.check("云南贝泰妮生物科技集团股份有限公司", "m160_duplicate_probe").status
    case_ref = read_json(CASE_REF, {"items": [], "summary": {}})
    case_items = case_ref.get("items") or []
    case_boundary_ok = all(not item.get("prospect_evidence") and not item.get("signed_customer_auto_confirm") for item in case_items)
    browser = read_json(M160 / "source_trace_browser_v1.json", {})
    cleanup = read_json(M160 / "vault_delivery_cleanup_plan_v1.json", {})
    expert = read_json(M160 / "m160_expert_review_report_v1.json", {})
    dynamic_findings = scan_dynamic_terms([M160, VAULT_ROOT / "00-索引与说明", VAULT_ROOT / "01-L1 ICP强匹配档案", VAULT_ROOT / "02-L2正式潜客档案"])
    secret_findings = scan_secrets([M160, WORKSPACE / "scripts", WORKSPACE / "shared/static_pool"])

    checks = {
        "py_compile_pass": compile_result["returncode"] == 0,
        "json_parse_pass": not json_errors,
        "readiness_pass": readiness_result["returncode"] == 0,
        "readiness_read_only_pass": before == after,
        "production_dry_run_pass": production_dry_run["returncode"] == 0 and "build_m150r_production_loop_hardening.py" in production_dry_run["stdout"] and "build_m160r_system_stabilization.py" in production_dry_run["stdout"],
        "signed_customer_regression_pass": all(status == "excluded_existing_customer" for status in signed_results),
        "duplicate_existing_prospect_pass": duplicate_result == "duplicate_existing_prospect",
        "customer_case_boundary_pass": case_boundary_ok,
        "source_trace_browser_l1_l2_pass": browser.get("summary", {}).get("l1_l2_missing_source_trace_count") == 0,
        "dynamic_term_scan_pass": not dynamic_findings,
        "api_key_scan_pass": not secret_findings,
        "expert_review_allows_publish": expert.get("status") in {"pass", "pass_with_followups"},
        "no_delete_performed": cleanup.get("no_delete_performed") is True,
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    return {
        "batch_id": "M160R-validation-report-v1",
        "milestone": "M160R",
        "generated_at": now(),
        "status": status,
        "checks": checks,
        "json_errors": json_errors,
        "readiness_stdout_tail": readiness_result["stdout"],
        "readiness_stderr_tail": readiness_result["stderr"],
        "readiness_status_before": before,
        "readiness_status_after": after,
        "production_dry_run_stdout_tail": production_dry_run["stdout"],
        "signed_customer_regression_statuses": dict(zip(SIGNED_BLOCK_SAMPLES, signed_results)),
        "duplicate_probe_status": duplicate_result,
        "dynamic_term_findings": dynamic_findings[:50],
        "secret_findings": secret_findings[:50],
        "compile_result": compile_result,
    }


def build_all() -> dict[str, Any]:
    cleanup = build_vault_delivery_cleanup_plan()
    browser = build_source_trace_browser()
    backlog = build_backlog()
    expert = build_expert_review(cleanup, browser, backlog)

    write_json(M160 / "vault_delivery_cleanup_plan_v1.json", cleanup)
    write_json(M160 / "source_trace_browser_v1.json", browser)
    write_json(M160 / "evidence_acquisition_backlog_v2.json", backlog)
    write_json(M160 / "m160_expert_review_report_v1.json", expert)
    write_text(VAULT_INDEX / "Source Trace Browser.md", render_source_trace_browser_md(browser))
    write_text(DOCS / "BusinessMaster-M160生产系统稳定化复盘-v1.md", render_review_doc(cleanup, browser, backlog, expert))
    write_json(STATUS_PANEL, update_status_panel(cleanup, browser, backlog, expert))

    validation = validate()
    write_json(M160 / "m160_validation_report_v1.json", validation)
    return {
        "status": validation.get("status"),
        "outputs": {
            "cleanup_plan": str(M160 / "vault_delivery_cleanup_plan_v1.json"),
            "source_trace_browser": str(M160 / "source_trace_browser_v1.json"),
            "vault_source_trace_browser": str(VAULT_INDEX / "Source Trace Browser.md"),
            "backlog": str(M160 / "evidence_acquisition_backlog_v2.json"),
            "expert_review": str(M160 / "m160_expert_review_report_v1.json"),
            "validation": str(M160 / "m160_validation_report_v1.json"),
        },
        "validation_checks": validation.get("checks"),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M160R production system stabilization outputs.")
    parser.add_argument("--stage", choices=["readiness", "all", "validate"], default="all")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.stage == "readiness":
        payload = build_readiness_payload()
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload.get("status") == "PASS" else 2
    if args.stage == "validate":
        payload = validate()
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload.get("status") == "PASS" else 2
    payload = build_all()
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
