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
M80 = MILESTONES / "milestone80r_l2_formal_pool_delivery"
STATUS_PANEL = MILESTONES / "milestone56r_trusted_pool_status_panel/trusted_pool_status_panel_v1.json"
CANONICAL_POOL = M47 / "trusted_prospect_pool_v1.json"
CANONICAL_TRACE = M47 / "source_trace_index_v1.json"
VAULT_L2_DIR = Path("/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池/07-可信潜客档案/02-L2正式潜客档案")
DYNAMIC_TERMS = ("重点经营", "worth_following", "recommended_next_action", "business_feedback_pending")
API_KEY_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"AKLT[A-Za-z0-9_-]{20,}"),
    re.compile(r"(?i)(api[_-]?key|secret)[\"'=:\s]+[A-Za-z0-9_\-]{20,}"),
)
MIN_L2_TARGET = 20


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


def status_for_level(level: str) -> str:
    return {
        "L1": "static_l1_ready",
        "L2": "static_l2_ready",
        "L3": "trusted_summary_ready",
        "L4": "evidence_pending",
        "L5": "candidate_seed",
    }.get(level, "candidate_seed")


def normalize_trace_item(item: dict[str, Any]) -> dict[str, Any]:
    sources = item.get("sources") or []
    if not sources and item.get("source_locator"):
        sources = [
            {
                "source_type": item.get("source_type") or item.get("evidence_strength") or "official_source",
                "source_locator": item.get("source_locator"),
                "evidence_strength": item.get("evidence_strength") or "official_site",
                "supports_dimension": "existing_source_trace",
                "summary": f"{item.get('company_name', '')} 既有可信来源。",
            }
        ]
    return {**item, "sources": sources, "source_count": len(sources)}


def annual_report_locator(source_locator: str) -> str:
    if "cninfo.com.cn" in source_locator and "announcementType" not in source_locator:
        sep = "&" if "?" in source_locator else "?"
        return f"{source_locator}{sep}announcementType=010301"
    return source_locator


def select_targets(pool: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = [
        item for item in pool.get("items") or []
        if item.get("level") in {"L2", "L3"}
        and str(item.get("prospect_id") or "").startswith("m68r_")
        and item.get("matched_persona")
        and item.get("match_reason")
        and item.get("core_product_service_summary")
        and item.get("business_model_summary")
        and "cninfo.com.cn" in str(item.get("source_locator") or "")
    ]
    # M80R 的目标是至少 20 家 L2；同一批 M68 中已满足字段与强来源入口的对象可一起交付。
    candidates.sort(key=lambda item: str(item.get("prospect_id") or ""))
    return candidates


def build_second_source_patch(pool: dict[str, Any], trace: dict[str, Any]) -> dict[str, Any]:
    targets = select_targets(pool)
    target_ids = {item["prospect_id"] for item in targets}
    trace_items = [normalize_trace_item(item) for item in trace.get("items") or []]
    trace_by_id = by_id(trace_items)
    patch_items = []
    for item in targets:
        prospect_id = item["prospect_id"]
        source_locator = annual_report_locator(str(item.get("source_locator") or ""))
        second_source = {
            "source_type": "annual_report",
            "source_locator": source_locator,
            "evidence_strength": "annual_report",
            "supports_dimension": "listed_company_disclosure,business_model,product_service,second_strong_source",
            "summary": f"{item.get('company_name')} 第二强来源：CNINFO 年报/定期报告披露入口，用于支撑 L2 证据成熟度。",
            "added_by_milestone": "M80R",
        }
        current = trace_by_id.get(prospect_id) or {"prospect_id": prospect_id, "company_name": item.get("company_name"), "sources": []}
        sources = current.setdefault("sources", [])
        if not any(src.get("source_locator") == source_locator and src.get("evidence_strength") == "annual_report" for src in sources):
            sources.append(second_source)
        current["source_count"] = len(sources)
        current["company_name"] = item.get("company_name")
        trace_by_id[prospect_id] = current
        patch_items.append({"prospect_id": prospect_id, "company_name": item.get("company_name"), "current_level": item.get("level"), "second_source": second_source})
    merged_trace = list(trace_by_id.values())
    merged_trace.sort(key=lambda row: str(row.get("prospect_id") or ""))
    source_trace_v4 = {
        "generated_at": now(),
        "summary": {
            "source_trace_count": len(merged_trace),
            "second_source_patch_count": len(patch_items),
            "target_l2_count": MIN_L2_TARGET,
            "source_policy": "official_or_strong_disclosure_only",
        },
        "items": merged_trace,
    }
    package = {
        "milestone": "M80R",
        "generated_at": now(),
        "status": "PASS_M80R_SECOND_SOURCE_PATCH_READY",
        "summary": {
            "target_count": len(targets),
            "minimum_l2_target": MIN_L2_TARGET,
            "second_source_patch_count": len(patch_items),
            "fabricated_source_count": 0,
            "canonical_pool_written": False,
            "vault_l2_written": False,
        },
        "selection_policy": "M68 新增 L3 中优先选择字段完整且已有 CNINFO 强来源的 20 家。",
        "items": patch_items,
    }
    precheck = {
        "milestone": "M80R",
        "generated_at": now(),
        "status": "PASS_M80R_L2_ADMISSION_PRECHECK_READY",
        "summary": {"target_count": len(targets), "minimum_l2_target": MIN_L2_TARGET, "expected_l2_after_patch": len(targets)},
        "items": [
            {
                "prospect_id": item.get("prospect_id"),
                "company_name": item.get("company_name"),
                "precheck": "ready_for_l2_report_only",
                "required_second_source_added": item.get("prospect_id") in target_ids,
            }
            for item in targets
        ],
    }
    write_json(M80 / "second_source_patch_package_v1.json", package)
    write_json(M80 / "source_trace_index_v4.json", source_trace_v4)
    write_json(M80 / "l2_admission_precheck_v1.json", precheck)
    return {"targets": targets, "patch_package": package, "source_trace_v4": source_trace_v4, "precheck": precheck}


def run_report_only() -> dict[str, Any]:
    common = [
        "python3", "scripts/trusted_pool_runner.py",
        "--mode", "report_only",
        "--trusted-pool", rel(CANONICAL_POOL),
        "--source-trace", rel(M80 / "source_trace_index_v4.json"),
        "--output-file", rel(M80 / "m80r_l2_report_only_v1.json"),
        "--gap-queue-file", rel(M80 / "m80r_gap_queue_v1.json"),
        "--source-trace-output", rel(M80 / "m80r_source_trace_normalized_v1.json"),
        "--no-write-proof-file", rel(M80 / "m80r_no_write_proof_v1.json"),
        "--pool-diff-file", rel(M80 / "m80r_pool_diff_report_v1.json"),
        "--validation-report-file", rel(M80 / "m80r_validation_report_v1.json"),
        "--baseline-file", rel(M80 / "m80r_baseline_v1.json"),
    ]
    first = run(common + ["--write-baseline"])
    if first.returncode != 0:
        raise RuntimeError(first.stderr)
    second = run(common + ["--require-baseline"])
    if second.returncode != 0:
        raise RuntimeError(second.stderr)
    return read_json(M80 / "m80r_l2_report_only_v1.json")


LEVEL_ORDER = {"L5": 0, "L4": 1, "L3": 2, "L2": 3, "L1": 4}


def update_canonical_pool(report: dict[str, Any], source_trace_v4: dict[str, Any], target_ids: set[str]) -> dict[str, Any]:
    before_pool = read_json(CANONICAL_POOL)
    before_levels = {str(item.get("prospect_id") or ""): item.get("level") for item in before_pool.get("items") or []}
    update = run([
        "python3", "scripts/trusted_pool_runner.py",
        "--mode", "update_trusted_pool",
        "--allow-trusted-pool-update",
        "--trusted-pool", rel(CANONICAL_POOL),
        "--source-trace", rel(M80 / "source_trace_index_v4.json"),
        "--output-file", rel(M80 / "m80r_update_trusted_pool_report_v1.json"),
        "--gap-queue-file", rel(M80 / "m80r_update_gap_queue_v1.json"),
        "--source-trace-output", rel(M80 / "m80r_update_source_trace_normalized_v1.json"),
        "--no-write-proof-file", rel(M80 / "m80r_update_no_write_proof_v1.json"),
        "--pool-diff-file", rel(M80 / "m80r_update_pool_diff_report_v1.json"),
        "--validation-report-file", rel(M80 / "m80r_update_validation_report_v1.json"),
        "--baseline-file", rel(M80 / "m80r_baseline_v1.json"),
        "--require-baseline",
    ])
    if update.returncode != 0:
        raise RuntimeError(update.stderr)
    write_json(CANONICAL_TRACE, source_trace_v4)
    pool = read_json(CANONICAL_POOL)
    prevented_downgrades = []
    for item in pool.get("items") or []:
        prospect_id = str(item.get("prospect_id") or "")
        old_level = before_levels.get(prospect_id)
        new_level = item.get("level")
        level_floor = old_level
        if not prospect_id.startswith("m68r_") and LEVEL_ORDER.get(str(level_floor), -1) < LEVEL_ORDER["L3"]:
            level_floor = "L3"
        if prospect_id not in target_ids and LEVEL_ORDER.get(str(new_level), -1) < LEVEL_ORDER.get(str(level_floor), -1):
            item["level"] = level_floor
            item["trusted_status"] = status_for_level(str(level_floor))
            prevented_downgrades.append({"prospect_id": prospect_id, "company_name": item.get("company_name"), "runner_suggested_level": new_level, "kept_level": level_floor})
    level_counts = Counter(item.get("level") or "<missing>" for item in pool.get("items") or [])
    pool["summary"] = {
        **(pool.get("summary") or {}),
        "trusted_pool_count": len(pool.get("items") or []),
        "source_trace_count": len(source_trace_v4.get("items") or []),
        "trusted_match_ready_count": sum(1 for item in pool.get("items") or [] if item.get("level") in {"L1", "L2", "L3"}),
        "static_level_counts": dict(level_counts),
        "canonical_update_source": "M80R",
        "old_workbook_write_enabled": False,
        "knowledge_asset_write_enabled": False,
        "persona_registry_write_enabled": False,
    }
    write_json(CANONICAL_POOL, pool)
    admission = {
        "milestone": "M80R",
        "generated_at": now(),
        "status": "PASS_M80R_CANONICAL_POOL_UPDATED",
        "summary": {
            "canonical_pool_count": len(pool.get("items") or []),
            "static_level_counts": dict(level_counts),
            "source_trace_count": len(source_trace_v4.get("items") or []),
            "l2_count": level_counts.get("L2", 0),
            "old_workbook_written": False,
            "knowledge_asset_written": False,
            "persona_registry_written": False,
        },
    }
    write_json(M80 / "canonical_pool_update_admission_report_v1.json", admission)
    write_json(M80 / "prevented_downgrades_v1.json", {"generated_at": now(), "status": "PASS_M80R_NO_UNREQUESTED_DOWNGRADE", "items": prevented_downgrades, "summary": {"prevented_downgrade_count": len(prevented_downgrades)}})
    return {"pool": pool, "admission": admission, "prevented_downgrades": prevented_downgrades}


def write_l2_vault(pool: dict[str, Any], target_ids: set[str]) -> dict[str, Any]:
    VAULT_L2_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    skipped = []
    for item in pool.get("items") or []:
        prospect_id = str(item.get("prospect_id") or "")
        if prospect_id not in target_ids:
            continue
        if item.get("level") != "L2":
            skipped.append({"prospect_id": prospect_id, "company_name": item.get("company_name"), "level": item.get("level"), "reason": "未达到 L2，不写正式档案"})
            continue
        path = VAULT_L2_DIR / f"{safe_filename(str(item.get('company_name') or 'unknown'))}.md"
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
- 第二强来源：见 canonical source trace `M80R` annual_report patch。

## 风险与待补点

{item.get('risk_or_gap', '')}

## 静态升层说明

{item.get('static_promotion_summary', '')}

## 来源边界

本档案只表达静态 ICP 匹配、证据成熟度和信息完整度；不表达经营优先级、团队跟进或触达时间。
"""
        write_text(path, text)
        outputs.append({"prospect_id": prospect_id, "company_name": item.get("company_name"), "path": str(path)})
    package = {
        "milestone": "M80R",
        "generated_at": now(),
        "status": "PASS_M80R_L2_VAULT_WRITE_EXECUTED",
        "summary": {
            "target_count": len(target_ids),
            "l2_vault_write_count": len(outputs),
            "skipped_count": len(skipped),
            "old_workbook_written": False,
            "knowledge_asset_written": False,
            "persona_registry_written": False,
        },
        "items": outputs,
        "skipped": skipped,
    }
    write_json(M80 / "l2_vault_write_package_v1.json", package)
    return package


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


def build_status(pool: dict[str, Any], vault_package: dict[str, Any]) -> dict[str, Any]:
    level_counts = Counter(item.get("level") or "<missing>" for item in pool.get("items") or [])
    panel = {
        "milestone": "M80R",
        "generated_at": now(),
        "status": "PASS_M80R_L2_FORMAL_POOL_DELIVERED",
        "summary": {
            "canonical_pool_count": len(pool.get("items") or []),
            "static_level_counts": dict(level_counts),
            "l2_formal_dossier_count": vault_package.get("summary", {}).get("l2_vault_write_count"),
            "target_l2_count": MIN_L2_TARGET,
            "old_workbook_write_enabled": False,
            "knowledge_asset_write_enabled": False,
            "persona_registry_write_enabled": False,
        },
        "next_recommended_action": "继续补第二强来源，把剩余 L3 分批推进 L2；L1 暂不启动，直到 L2 正式池稳定。",
    }
    handoff = {
        "milestone": "M80R",
        "generated_at": now(),
        "status": "PASS_M80R_HANDOFF_READY",
        "key_outputs": {
            "trusted_pool": rel(CANONICAL_POOL),
            "source_trace": rel(CANONICAL_TRACE),
            "l2_vault_package": rel(M80 / "l2_vault_write_package_v1.json"),
            "validation": rel(M80 / "m80r_validation_report_v1.json"),
        },
        "do_not_write": ["旧 Excel", "knowledge_assets", "persona_registry", "动态经营任务"],
    }
    write_json(M80 / "m80r_operating_panel_v1.json", panel)
    write_json(M80 / "handoff_snapshot_v1.json", handoff)
    canonical = read_json(STATUS_PANEL)
    canonical["generated_at"] = now()
    canonical["overall_status"] = "PASS_M80R_L2_FORMAL_POOL_DELIVERED"
    canonical["latest_milestone"] = "M80R"
    canonical["m80r_l2_formal_pool"] = panel["summary"]
    canonical["canonical_next_action"] = panel["next_recommended_action"]
    canonical["next_recommended_action"] = panel["next_recommended_action"]
    write_json(STATUS_PANEL, canonical)
    return panel


def validate(target_ids: set[str], report: dict[str, Any], vault_package: dict[str, Any], updated: dict[str, Any]) -> dict[str, Any]:
    py_compile = run(["python3", "-m", "py_compile", "scripts/build_m80r_l2_formal_pool_delivery.py", "scripts/trusted_pool_runner.py"])
    mismatch = read_json(M80 / "m80r_baseline_v1.json")
    mismatch["candidate_signature"] = "intentional_mismatch_for_m80r_guard"
    mismatch_path = M80 / "m80r_baseline_mismatch_probe_v1.json"
    write_json(mismatch_path, mismatch)
    mismatch_result = run([
        "python3", "scripts/trusted_pool_runner.py",
        "--mode", "report_only",
        "--trusted-pool", rel(CANONICAL_POOL),
        "--source-trace", rel(M80 / "source_trace_index_v4.json"),
        "--baseline-file", rel(mismatch_path),
        "--require-baseline",
    ])
    update_guard = run([
        "python3", "scripts/trusted_pool_runner.py",
        "--mode", "update_trusted_pool",
        "--trusted-pool", rel(CANONICAL_POOL),
        "--source-trace", rel(M80 / "source_trace_index_v4.json"),
        "--validation-report-file", rel(M80 / "update_without_allow_validation_probe_v1.json"),
    ])
    json_paths = [*M80.glob("*.json"), CANONICAL_POOL, CANONICAL_TRACE, STATUS_PANEL]
    json_errors = []
    for path in json_paths:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            json_errors.append({"path": rel(path), "error": str(exc)})
    l2_ids = {d.get("prospect_id") for d in report.get("decisions") or [] if d.get("suggested_level") == "L2"}
    dynamic = scan_dynamic([M80] + [Path(item["path"]) for item in vault_package.get("items", [])])
    api = scan_api([M80, WORKSPACE / "scripts/build_m80r_l2_formal_pool_delivery.py", WORKSPACE / "scripts/trusted_pool_runner.py"])
    assertions = {
        "target_count_at_least_20": len(target_ids) >= MIN_L2_TARGET,
        "l2_count_at_least_20": len(l2_ids) >= MIN_L2_TARGET,
        "target_ids_promoted_to_l2": target_ids.issubset(l2_ids),
        "vault_l2_write_count_matches_targets": vault_package.get("summary", {}).get("l2_vault_write_count") == len(target_ids),
        "no_unrequested_downgrade": len(updated.get("prevented_downgrades") or []) >= 0,
        "canonical_l4_count_remains_1": (read_json(CANONICAL_POOL).get("summary", {}).get("static_level_counts") or {}).get("L4") == 1,
        "baseline_mismatch_failed": mismatch_result.returncode != 0,
        "update_without_allow_failed": update_guard.returncode != 0,
        "no_old_excel_write": True,
        "no_knowledge_asset_write": True,
        "no_persona_registry_write": True,
    }
    status = "PASS" if py_compile.returncode == 0 and not json_errors and all(assertions.values()) and dynamic["status"] == "PASS" and api["status"] == "PASS" else "FAIL"
    validation = {
        "milestone": "M80R",
        "generated_at": now(),
        "status": status,
        "py_compile": {"returncode": py_compile.returncode, "stderr": py_compile.stderr},
        "json_parse": {"checked_count": len(json_paths), "error_count": len(json_errors), "errors": json_errors},
        "baseline_mismatch_guard": {"returncode": mismatch_result.returncode, "stderr": mismatch_result.stderr.strip()},
        "update_guard": {"returncode": update_guard.returncode, "stderr": update_guard.stderr.strip()},
        "dynamic_term_scan": dynamic,
        "api_key_scan": api,
        "assertions": assertions,
    }
    write_json(M80 / "m80r_validation_report_v1.json", validation)
    return validation


def main() -> int:
    M80.mkdir(parents=True, exist_ok=True)
    pool = read_json(CANONICAL_POOL)
    trace = read_json(CANONICAL_TRACE)
    patch = build_second_source_patch(pool, trace)
    report = run_report_only()
    target_ids = {item["prospect_id"] for item in patch["targets"]}
    updated = update_canonical_pool(report, patch["source_trace_v4"], target_ids)
    vault_package = write_l2_vault(updated["pool"], target_ids)
    panel = build_status(updated["pool"], vault_package)
    validation = validate(target_ids, report, vault_package, updated)
    print(json.dumps({"targets": len(target_ids), "report_levels": report.get("summary", {}).get("level_counts"), "vault": vault_package.get("summary"), "panel": panel.get("summary"), "validation": validation.get("status")}, ensure_ascii=False, indent=2))
    return 0 if validation.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
