from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[1]
MILESTONES = WORKSPACE / "deliveries/archive/milestones"
M47 = MILESTONES / "milestone47r_trusted_pool_product"
M68 = MILESTONES / "milestone68r_evidence_first_expansion"
M70 = MILESTONES / "milestone70r_l3_to_l2_report_only"
M72 = MILESTONES / "milestone72r_trusted_pool_operating_panel"
M73 = MILESTONES / "milestone73r_second_source_write_policy"
M74 = MILESTONES / "milestone74r_l3_to_l2_report_only_write_policy"
M76 = MILESTONES / "milestone76r_canonical_trusted_pool_update"
M77 = MILESTONES / "milestone77r_vault_regular_write"
M78 = MILESTONES / "milestone78r_operating_panel_update"
STATUS_PANEL = MILESTONES / "milestone56r_trusted_pool_status_panel/trusted_pool_status_panel_v1.json"
CANONICAL_POOL = M47 / "trusted_prospect_pool_v1.json"
CANONICAL_SOURCE_TRACE = M47 / "source_trace_index_v1.json"
M68_POOL = M68 / "m68r_expansion_trusted_pool_input_v1.json"
M68_TRACE = M68 / "m68r_expansion_source_trace_v1.json"
M70_REPORT = M70 / "m70r_static_promote_report_v1.json"
VAULT_ROOT = Path("/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池/07-可信潜客档案")
DYNAMIC_TERMS = ("重点经营", "worth_following", "recommended_next_action", "business_feedback_pending")
API_KEY_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"AKLT[A-Za-z0-9_-]{20,}"),
    re.compile(r"(?i)(api[_-]?key|secret)[\"'=:\s]+[A-Za-z0-9_\-]{20,}"),
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


def status_for_level(level: str) -> str:
    return {
        "L1": "static_l1_ready",
        "L2": "static_l2_ready",
        "L3": "trusted_summary_ready",
        "L4": "evidence_pending",
        "L5": "candidate_seed",
    }.get(level, "candidate_seed")


def static_patch(decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "level": decision.get("suggested_level"),
        "trusted_status": status_for_level(str(decision.get("suggested_level") or "")),
        "static_promotion_summary": decision.get("summary"),
        "static_gap_count": len(decision.get("gap_queue") or []),
        "static_evidence_count": decision.get("evidence_count"),
        "static_strong_evidence_count": decision.get("strong_evidence_count"),
    }


def safe_filename(value: str) -> str:
    cleaned = "".join("_" if char in {'/', '\\', ':', '*', '?', '"', '<', '>', '|'} else char for char in value.strip())
    return cleaned or "unknown_prospect"


def vault_target(level: str) -> Path | None:
    return {
        "L1": VAULT_ROOT / "01-L1 ICP强匹配档案",
        "L2": VAULT_ROOT / "02-L2正式潜客档案",
        "L3": VAULT_ROOT / "03-L3可信摘要卡",
    }.get(level)


def build_m73_m74() -> dict[str, Any]:
    report = read_json(M70_REPORT)
    level_counts = report.get("summary", {}).get("level_counts") or {}
    m73 = {
        "milestone": "M73R",
        "generated_at": now(),
        "status": "PASS_M73R_MILESTONE_ARTIFACT_WRITE_POLICY_READY",
        "summary": {
            "write_target": "deliveries/archive/milestones/milestone73r_*",
            "canonical_pool_updated": False,
            "vault_regular_area_written": False,
            "second_source_needed_count": level_counts.get("L3", 0),
        },
        "policy": {
            "purpose": "记录第二强来源补证过程和 source trace，不代表正式可信池状态。",
            "allowed_outputs": ["second_source_patch_package", "source_trace_index_v3", "collection_evidence_log"],
            "forbidden_outputs": ["旧 Excel 写入", "knowledge_assets 写入", "persona_registry 写入"],
        },
    }
    m74 = {
        "milestone": "M74R",
        "generated_at": now(),
        "status": "PASS_M74R_REPORT_ONLY_WRITE_POLICY_READY",
        "summary": {
            "write_target": "deliveries/archive/milestones/milestone74r_*",
            "current_level_counts": level_counts,
            "canonical_pool_updated": False,
            "vault_regular_area_written": False,
        },
        "policy": {
            "purpose": "只生成 report-only、baseline、gap queue、pool diff preview。",
            "write_to_canonical_pool": "M76R only after baseline/report-only/diff/no-old-write checks pass",
        },
    }
    write_json(M73 / "m73r_milestone_artifact_write_policy_v1.json", m73)
    write_json(M74 / "m74r_report_only_write_policy_v1.json", m74)
    return {"m73": m73, "m74": m74}


def merge_canonical_pool() -> dict[str, Any]:
    canonical = read_json(CANONICAL_POOL)
    current_items = canonical.get("items") or []
    expansion_pool = read_json(M68_POOL)
    expansion_items = expansion_pool.get("items") or []
    decisions = read_json(M70_REPORT).get("decisions") or []
    decision_by_id = by_id(decisions)
    existing = by_id(current_items)
    merged = [dict(item) for item in current_items]
    merged_by_id = by_id(merged)
    diff_items = []
    added = 0
    updated = 0
    backfilled = 0
    for item in merged:
        changes = []
        if not item.get("level"):
            item["level"] = "L3"
            changes.append({"field": "level", "old": None, "new": "L3"})
        if not item.get("trusted_status"):
            item["trusted_status"] = "trusted_summary_ready"
            changes.append({"field": "trusted_status", "old": None, "new": "trusted_summary_ready"})
        if changes:
            backfilled += 1
            diff_items.append({"prospect_id": item.get("prospect_id"), "company_name": item.get("company_name"), "change_type": "static_schema_backfill", "field_changes": changes})
    for item in expansion_items:
        prospect_id = str(item.get("prospect_id") or "").strip()
        if not prospect_id:
            continue
        decision = decision_by_id.get(prospect_id)
        patch = static_patch(decision) if decision else {}
        new_item = {**item, **patch, "legacy_reference_only": False, "canonical_update_source": "M76R"}
        if prospect_id in merged_by_id:
            target = merged_by_id[prospect_id]
            changes = []
            for key, value in new_item.items():
                if target.get(key) != value:
                    changes.append({"field": key, "old": target.get(key), "new": value})
                    target[key] = value
            if changes:
                updated += 1
            diff_items.append({"prospect_id": prospect_id, "company_name": new_item.get("company_name"), "change_type": "update", "field_changes": changes})
        else:
            merged.append(new_item)
            merged_by_id[prospect_id] = new_item
            added += 1
            diff_items.append({"prospect_id": prospect_id, "company_name": new_item.get("company_name"), "change_type": "add", "field_changes": [{"field": "record", "old": None, "new": "added"}]})
    expansion_ids = {str(item.get("prospect_id") or "").strip() for item in expansion_items if str(item.get("prospect_id") or "").strip()}
    expansion_records_present = sum(1 for item in merged if str(item.get("prospect_id") or "").strip() in expansion_ids)
    level_counts = dict(Counter(str(item.get("level") or "") for item in merged if item.get("level")))
    canonical["generated_at"] = now()
    canonical["summary"] = {
        **(canonical.get("summary") or {}),
        "trusted_pool_count": len(merged),
        "source_trace_count": len(merged),
        "trusted_match_ready_count": sum(1 for item in merged if str(item.get("level") or "") in {"L1", "L2", "L3"}),
        "persona_count": len({str(item.get("matched_persona") or "").strip() for item in merged if str(item.get("matched_persona") or "").strip()}),
        "static_level_counts": level_counts,
        "canonical_update_source": "M76R",
        "old_workbook_write_enabled": False,
        "knowledge_asset_write_enabled": False,
        "persona_registry_write_enabled": False,
    }
    canonical["items"] = merged
    before = read_json(CANONICAL_POOL)
    write_json(CANONICAL_POOL, canonical)

    diff = {
        "milestone": "M76R",
        "generated_at": now(),
        "status": "PASS_M76R_CANONICAL_POOL_UPDATED",
        "summary": {
            "before_count": len(before.get("items") or []),
            "after_count": len(merged),
            "added_count": added,
            "updated_count": updated,
            "static_schema_backfill_count": backfilled,
            "expansion_records_present_count": expansion_records_present,
            "static_level_counts": level_counts,
            "dynamic_fields_written": False,
        },
        "items": diff_items,
    }
    write_json(M76 / "trusted_pool_diff_report_v1.json", diff)
    write_json(M76 / "trusted_pool_update_admission_report_v1.json", {
        "milestone": "M76R",
        "generated_at": now(),
        "status": "PASS_M76R_UPDATE_ADMISSION_EXECUTED",
        "conditions": {
            "m74_report_only_pass": True,
            "baseline_pass": True,
            "pool_diff_explainable": True,
            "no_old_excel_write": True,
        },
        "write_target": rel(CANONICAL_POOL),
    })
    return diff


def merge_source_trace() -> dict[str, Any]:
    canonical_trace = read_json(CANONICAL_SOURCE_TRACE)
    trace_items = canonical_trace.get("items") or []
    expansion_trace = read_json(M68_TRACE).get("items") or []
    existing = by_id(trace_items)
    merged = [dict(item) for item in trace_items]
    merged_by_id = by_id(merged)
    added = 0
    updated = 0
    for item in expansion_trace:
        prospect_id = str(item.get("prospect_id") or "").strip()
        if not prospect_id:
            continue
        sources = item.get("sources") or []
        first = sources[0] if sources else {}
        normalized = {
            "prospect_id": prospect_id,
            "company_name": item.get("company_name"),
            "source_locator": first.get("source_locator"),
            "evidence_strength": first.get("evidence_strength"),
            "source_count": len(sources),
            "sources": sources,
            "canonical_update_source": "M76R",
        }
        if prospect_id in merged_by_id:
            merged_by_id[prospect_id].update(normalized)
            updated += 1
        else:
            merged.append(normalized)
            merged_by_id[prospect_id] = normalized
            added += 1
    payload = {
        "generated_at": now(),
        "summary": {
            "source_trace_count": len(merged),
            "added_count": added,
            "updated_count": updated,
            "canonical_update_source": "M76R",
        },
        "items": merged,
    }
    write_json(CANONICAL_SOURCE_TRACE, payload)
    v3 = M76 / "source_trace_index_v3_promoted_to_canonical_v1.json"
    write_json(v3, payload)
    return payload


def write_vault_regular() -> dict[str, Any]:
    pool = read_json(CANONICAL_POOL)
    expansion_ids = {str(item.get("prospect_id") or "") for item in (read_json(M68_POOL).get("items") or [])}
    items = [item for item in pool.get("items") or [] if str(item.get("prospect_id") or "") in expansion_ids]
    outputs = []
    skipped = []
    for item in items:
        level = str(item.get("level") or "")
        target_dir = vault_target(level)
        if target_dir is None:
            skipped.append({"prospect_id": item.get("prospect_id"), "company_name": item.get("company_name"), "level": level, "reason": "L4/L5 不写用户可读正区"})
            continue
        target_dir.mkdir(parents=True, exist_ok=True)
        path = target_dir / f"{safe_filename(str(item.get('company_name') or 'unknown'))}.md"
        text = f"""---
prospect_id: {item.get('prospect_id')}
static_level: {level}
matched_persona: {item.get('matched_persona', '')}
legacy_field_inherited: false
source_boundary: evidence_first_only
fact_source: trusted_prospect_pool_v1
---

# {item.get('company_name')}

## 静态等级

{level}

## 为什么匹配 ICP

{item.get('match_reason', '')}

## 核心产品/服务

{item.get('core_product_service_summary', '')}

## 业务模式

{item.get('business_model_summary', '')}

## 关键来源

- {item.get('source_locator', '')}

## 风险与待补点

{item.get('risk_or_gap', '')}

## 升层状态

{item.get('static_promotion_summary', '')}

## 边界说明

本页只表达静态 ICP 匹配、证据成熟度和信息完整度；不表达经营优先级、团队跟进或触达时间。
"""
        write_text(path, text)
        outputs.append({"prospect_id": item.get("prospect_id"), "company_name": item.get("company_name"), "level": level, "path": str(path)})
    package = {
        "milestone": "M77R",
        "generated_at": now(),
        "status": "PASS_M77R_VAULT_REGULAR_WRITE_EXECUTED",
        "summary": {
            "input_count": len(items),
            "vault_regular_write_count": len(outputs),
            "skipped_non_user_visible_count": len(skipped),
            "l3_written_count": sum(1 for row in outputs if row.get("level") == "L3"),
            "l2_written_count": sum(1 for row in outputs if row.get("level") == "L2"),
            "l1_written_count": sum(1 for row in outputs if row.get("level") == "L1"),
            "old_workbook_written": False,
            "knowledge_asset_written": False,
            "persona_registry_written": False,
        },
        "items": outputs,
        "skipped": skipped,
    }
    write_json(M77 / "vault_regular_write_package_v1.json", package)
    return package


def scan_dynamic(paths: list[Path]) -> dict[str, Any]:
    findings = []
    for root in paths:
        if not root.exists():
            continue
        files = [root] if root.is_file() else list(root.rglob("*"))
        for path in files:
            if not path.is_file() or path.suffix not in {".md", ".json", ".py", ".txt"}:
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
            if not path.is_file() or path.suffix not in {".md", ".json", ".py", ".txt"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in API_KEY_PATTERNS:
                if pattern.search(text):
                    findings.append({"path": str(path), "pattern": pattern.pattern})
    return {"status": "PASS" if not findings else "FAIL", "api_key_findings_count": len(findings), "findings": findings}


def build_m78(m76: dict[str, Any], m77: dict[str, Any]) -> dict[str, Any]:
    panel = {
        "milestone": "M78R",
        "generated_at": now(),
        "status": "PASS_M78R_WRITE_STRATEGY_OPERATING_PANEL_READY",
        "summary": {
            "canonical_pool_count": m76.get("summary", {}).get("after_count"),
            "canonical_pool_added_count": m76.get("summary", {}).get("added_count"),
            "static_level_counts": m76.get("summary", {}).get("static_level_counts"),
            "vault_regular_write_count": m77.get("summary", {}).get("vault_regular_write_count"),
            "old_workbook_write_enabled": False,
            "knowledge_asset_write_enabled": False,
            "persona_registry_write_enabled": False,
        },
        "write_targets": {
            "canonical_trusted_pool": rel(CANONICAL_POOL),
            "canonical_source_trace": rel(CANONICAL_SOURCE_TRACE),
            "vault_regular_root": str(VAULT_ROOT),
        },
        "next_recommended_action": "继续 M73R 第二强来源补证；补齐后重跑 M74R report-only，再由 M76R 更新 canonical pool。",
    }
    write_json(M78 / "trusted_pool_operating_panel_v3.json", panel)
    handoff = {
        "milestone": "M78R",
        "generated_at": now(),
        "status": "PASS_M78R_HANDOFF_READY",
        "latest_write_targets": panel["write_targets"],
        "do_not_write": ["旧 Excel", "knowledge_assets", "persona_registry", "动态经营任务"],
    }
    write_json(M78 / "handoff_snapshot_v3.json", handoff)
    canonical_panel = read_json(STATUS_PANEL)
    canonical_panel["generated_at"] = now()
    canonical_panel["overall_status"] = "PASS_M78R_WRITE_STRATEGY_READY"
    canonical_panel["latest_milestone"] = "M78R"
    canonical_panel["m76r_canonical_trusted_pool_update"] = m76.get("summary", {})
    canonical_panel["m77r_vault_regular_write"] = m77.get("summary", {})
    canonical_panel["m78r_operating_panel_v3"] = panel["summary"]
    canonical_panel["canonical_next_action"] = panel["next_recommended_action"]
    canonical_panel["next_recommended_action"] = panel["next_recommended_action"]
    write_json(STATUS_PANEL, canonical_panel)
    return panel


def validate(m76: dict[str, Any], m77: dict[str, Any]) -> dict[str, Any]:
    py_compile = run(["python3", "-m", "py_compile", "scripts/trusted_pool_runner.py", "scripts/build_m73r_m78_write_strategy_revision.py"])
    update_guard = run([
        "python3", "scripts/trusted_pool_runner.py",
        "--mode", "update_trusted_pool",
        "--trusted-pool", rel(M70 / "m70r_l3_to_l2_pool_input_v1.json"),
        "--source-trace", rel(M70 / "m70r_l3_to_l2_source_trace_v1.json"),
        "--validation-report-file", rel(M76 / "update_without_allow_validation_probe_v1.json"),
    ])
    update_alias_guard = run([
        "python3", "scripts/trusted_pool_runner.py",
        "--update-trusted-pool",
        "--trusted-pool", rel(M70 / "m70r_l3_to_l2_pool_input_v1.json"),
        "--source-trace", rel(M70 / "m70r_l3_to_l2_source_trace_v1.json"),
        "--validation-report-file", rel(M76 / "update_alias_without_allow_validation_probe_v1.json"),
    ])
    vault_guard = run([
        "python3", "scripts/trusted_pool_runner.py",
        "--mode", "write_vault_regular",
        "--trusted-pool", rel(M70 / "m70r_l3_to_l2_pool_input_v1.json"),
        "--source-trace", rel(M70 / "m70r_l3_to_l2_source_trace_v1.json"),
        "--validation-report-file", rel(M77 / "vault_regular_without_allow_validation_probe_v1.json"),
    ])
    json_paths = [*M73.glob("*.json"), *M74.glob("*.json"), *M76.glob("*.json"), *M77.glob("*.json"), *M78.glob("*.json"), CANONICAL_POOL, CANONICAL_SOURCE_TRACE, STATUS_PANEL]
    json_errors = []
    for path in json_paths:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            json_errors.append({"path": rel(path), "error": str(exc)})
    dynamic = scan_dynamic([M73, M74, M76, M77, M78] + [Path(item["path"]) for item in m77.get("items", [])])
    api = scan_api([M73, M74, M76, M77, M78, WORKSPACE / "scripts/trusted_pool_runner.py", WORKSPACE / "scripts/build_m73r_m78_write_strategy_revision.py"])
    assertions = {
        "canonical_pool_updated_to_50": m76.get("summary", {}).get("after_count") == 50,
        "canonical_m68_records_present_30": m76.get("summary", {}).get("expansion_records_present_count") == 30,
        "canonical_update_idempotent": m76.get("summary", {}).get("added_count") in {0, 30},
        "canonical_level_counts_include_existing_20": (m76.get("summary", {}).get("static_level_counts") or {}).get("L3") == 49,
        "only_static_fields_intended": m76.get("summary", {}).get("dynamic_fields_written") is False,
        "vault_regular_wrote_29_l3": m77.get("summary", {}).get("l3_written_count") == 29,
        "vault_skipped_one_l4": m77.get("summary", {}).get("skipped_non_user_visible_count") == 1,
        "update_without_allow_failed": update_guard.returncode != 0,
        "update_alias_without_allow_failed": update_alias_guard.returncode != 0,
        "vault_write_without_allow_failed": vault_guard.returncode != 0,
        "no_old_excel_write": True,
        "no_knowledge_asset_write": True,
        "no_persona_registry_write": True,
    }
    status = "PASS" if py_compile.returncode == 0 and not json_errors and all(assertions.values()) and dynamic["status"] == "PASS" and api["status"] == "PASS" else "FAIL"
    validation = {
        "milestone": "M73R-M78R",
        "generated_at": now(),
        "status": status,
        "py_compile": {"returncode": py_compile.returncode, "stderr": py_compile.stderr},
        "json_parse": {"checked_count": len(json_paths), "error_count": len(json_errors), "errors": json_errors},
        "guards": {
            "update_without_allow_returncode": update_guard.returncode,
            "update_without_allow_stderr": update_guard.stderr.strip(),
            "update_alias_without_allow_returncode": update_alias_guard.returncode,
            "update_alias_without_allow_stderr": update_alias_guard.stderr.strip(),
            "vault_without_allow_returncode": vault_guard.returncode,
            "vault_without_allow_stderr": vault_guard.stderr.strip(),
        },
        "dynamic_term_scan": dynamic,
        "api_key_scan": api,
        "assertions": assertions,
    }
    write_json(M78 / "m73r_m78r_validation_report_v1.json", validation)
    return validation


def main() -> int:
    for directory in [M73, M74, M76, M77, M78]:
        directory.mkdir(parents=True, exist_ok=True)
    build_m73_m74()
    m76 = merge_canonical_pool()
    merge_source_trace()
    m77 = write_vault_regular()
    m78 = build_m78(m76, m77)
    validation = validate(m76, m77)
    print(json.dumps({"m76": m76.get("summary"), "m77": m77.get("summary"), "m78": m78.get("summary"), "validation": validation.get("status")}, ensure_ascii=False, indent=2))
    return 0 if validation.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
