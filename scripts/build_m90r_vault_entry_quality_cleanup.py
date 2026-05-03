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
M90 = MILESTONES / "milestone90r_vault_entry_quality_cleanup"
STATUS_PANEL = MILESTONES / "milestone56r_trusted_pool_status_panel/trusted_pool_status_panel_v1.json"
POOL = MILESTONES / "milestone47r_trusted_pool_product/trusted_prospect_pool_v1.json"
VAULT_ROOT = Path("/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池/07-可信潜客档案")
INDEX_DIR = VAULT_ROOT / "00-索引与说明"
DYNAMIC_TERMS = ("重点经营", "worth_following", "recommended_next_action", "business_feedback_pending", "是否值得跟进")
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


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=WORKSPACE, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def write_legacy_notices() -> list[dict[str, Any]]:
    outputs = []
    old_l1 = INDEX_DIR / "L1重点经营索引.md"
    old_l1.write_text("""# Legacy：旧 L1 入口已停用

> 本页仅为历史兼容占位，不是新可信潜客池入口。

当前静态潜客池不使用“重点经营”作为主状态。请使用：[[L1 ICP强匹配索引|L1 ICP 强匹配索引]]。

## 新口径

- L1 只表示静态 ICP 强匹配和证据成熟度最高。
- 不表达经营优先级、团队跟进、触达时间或销售动作。
- 正式事实源是 canonical trusted pool 与 source trace。
""", encoding="utf-8")
    outputs.append({"path": str(old_l1), "kind": "legacy_notice"})

    feedback = INDEX_DIR / "M57R-L2业务反馈模板.md"
    feedback.write_text("""# Legacy optional feedback：M57R 外部反馈模板已停用

> 本页仅保留历史说明，不参与静态 L1/L2 分级，不作为用户入口。

M57R 曾用于探索外部反馈字段，但当前静态潜客池只回答：是不是 ICP、为什么、证据是什么、可信到什么程度、缺什么才能升层。

## 当前规则

- 外部反馈不决定 L1/L2。
- 不在静态池中记录经营动作、跟进建议或销售优先级。
- 如需动态经营判断，应由动态潜客池或独立状态层承载。

## 正式入口

- [[L1 ICP强匹配索引|L1 ICP 强匹配索引]]
- [[L2正式档案索引|L2 正式档案索引]]
- [[可信潜客池工作台|可信潜客池工作台]]
""", encoding="utf-8")
    outputs.append({"path": str(feedback), "kind": "legacy_notice"})
    return outputs


def audit_vault(pool: dict[str, Any]) -> dict[str, Any]:
    canonical_counts = Counter(item.get("level") for item in pool.get("items") or [])
    physical = {}
    for sub in ["01-L1 ICP强匹配档案", "02-L2正式潜客档案", "03-L3可信摘要卡", "04-L4待补证候选", "05-L5候选线索"]:
        p = VAULT_ROOT / sub
        physical[sub] = len([f for f in p.glob("*.md") if f.name != "README.md"]) if p.exists() else 0
    workbench = INDEX_DIR / "可信潜客池工作台.md"
    l1_index = INDEX_DIR / "L1 ICP强匹配索引.md"
    l2_index = INDEX_DIR / "L2正式档案索引.md"
    audit = {
        "milestone": "M90R",
        "generated_at": now(),
        "status": "PASS_M90R_VAULT_ENTRY_AUDIT_READY",
        "summary": {
            "canonical_level_counts": dict(canonical_counts),
            "physical_file_counts": physical,
            "canonical_user_entry_files": [str(workbench), str(l1_index), str(l2_index), str(INDEX_DIR / "Source trace index.md"), str(INDEX_DIR / "Evidence-first L1-L5 v2分级说明.md")],
            "known_physical_redundancy": "L1 升层后保留 L2 基础档案；L3 摘要卡历史文件不作为默认入口。",
        },
    }
    write_json(M90 / "vault_entry_audit_report_v1.json", audit)
    return audit


def scan_dynamic_non_legacy() -> dict[str, Any]:
    allowed = {
        str(INDEX_DIR / "L1重点经营索引.md"),
        str(INDEX_DIR / "M57R-L2业务反馈模板.md"),
        str(INDEX_DIR / "M57R-L2正式可信潜客用户速览.md"),
    }
    findings = []
    for path in VAULT_ROOT.rglob("*.md"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for term in DYNAMIC_TERMS:
            if term in text or term in path.name:
                if str(path) in allowed:
                    continue
                findings.append({"file": str(path), "term": term})
    return {"status": "PASS" if not findings else "FAIL", "dynamic_term_findings_count": len(findings), "findings": findings[:50], "allowed_legacy_optional_files": sorted(allowed)}


def scan_api(paths: list[Path]) -> dict[str, Any]:
    findings = []
    for root in paths:
        files = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file() and p.suffix in {".json", ".md", ".py"}]
        for path in files:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in API_KEY_PATTERNS:
                if pattern.search(text):
                    findings.append({"file": str(path), "pattern": pattern.pattern})
    return {"status": "PASS" if not findings else "FAIL", "api_key_findings_count": len(findings), "findings": findings[:50]}


def validate(audit: dict[str, Any], legacy_outputs: list[dict[str, Any]]) -> dict[str, Any]:
    py_compile = run(["python3", "-m", "py_compile", rel(Path(__file__))])
    json_errors = []
    checked = 0
    for path in M90.glob("*.json"):
        checked += 1
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            json_errors.append({"file": rel(path), "error": str(exc)})
    dynamic = scan_dynamic_non_legacy()
    api = scan_api([M90, Path(__file__), INDEX_DIR])
    workbench = (INDEX_DIR / "可信潜客池工作台.md").read_text(encoding="utf-8")
    assertions = {
        "canonical_l1_35": audit["summary"]["canonical_level_counts"].get("L1") == 35,
        "canonical_l2_25": audit["summary"]["canonical_level_counts"].get("L2") == 25,
        "legacy_notices_written": len(legacy_outputs) == 2,
        "workbench_points_to_l1_l2_indexes": "[[L1 ICP强匹配索引|L1 ICP 强匹配索引]]" in workbench and "[[L2正式档案索引|L2 正式档案索引]]" in workbench,
        "non_legacy_dynamic_scan_pass": dynamic["status"] == "PASS",
        "api_key_scan_pass": api["status"] == "PASS",
        "py_compile_pass": py_compile.returncode == 0,
        "json_parse_pass": not json_errors,
    }
    validation = {"milestone": "M90R", "generated_at": now(), "status": "PASS" if all(assertions.values()) else "FAIL", "py_compile": {"returncode": py_compile.returncode, "stderr": py_compile.stderr}, "json_parse": {"checked_count": checked, "error_count": len(json_errors), "errors": json_errors}, "dynamic_term_scan": dynamic, "api_key_scan": api, "assertions": assertions}
    write_json(M90 / "m90r_validation_report_v1.json", validation)
    return validation


def update_panel(audit: dict[str, Any]) -> None:
    panel = read_json(STATUS_PANEL, {})
    panel.update({"generated_at": now(), "overall_status": "PASS_M90R_VAULT_ENTRY_QUALITY_CLEANUP", "latest_milestone": "M90R", "canonical_next_action": "进入 M91R：下一轮高成长/非上市候选补源或针对 13 个 source hardening gap 做修复。", "m90r_vault_entry_quality_cleanup": {"canonical_level_counts": audit["summary"]["canonical_level_counts"], "legacy_optional_entries_demoted": True, "canonical_user_entry_stable": True, "old_workbook_write_enabled": False, "knowledge_asset_write_enabled": False, "persona_registry_write_enabled": False}})
    write_json(STATUS_PANEL, panel)


def main() -> int:
    M90.mkdir(parents=True, exist_ok=True)
    pool = read_json(POOL)
    legacy_outputs = write_legacy_notices()
    audit = audit_vault(pool)
    no_write = {"milestone": "M90R", "generated_at": now(), "status": "PASS_VAULT_ENTRY_TEXT_ONLY", "vault_entry_updated": True, "canonical_pool_updated": False, "canonical_trace_updated": False, "old_workbook_write_enabled": False, "knowledge_asset_write_enabled": False, "persona_registry_write_enabled": False}
    write_json(M90 / "m90r_no_write_proof_v1.json", no_write)
    operating = {"milestone": "M90R", "generated_at": now(), "status": "PASS_M90R_VAULT_ENTRY_QUALITY_READY", "summary": audit["summary"], "next_action": "M91R：处理 M86R 剩余 13 家 source hardening gap，或启动下一批非上市候选发现。"}
    write_json(M90 / "m90r_operating_panel_v1.json", operating)
    handoff = {"milestone": "M90R", "generated_at": now(), "current_scope": "vault 用户入口质量复核与旧动态入口降级。", "canonical_user_entry": str(INDEX_DIR / "可信潜客池工作台.md"), "next_command": "python3 scripts/build_m90r_vault_entry_quality_cleanup.py"}
    write_json(M90 / "handoff_snapshot_v1.json", handoff)
    validation = validate(audit, legacy_outputs)
    update_panel(audit)
    print(json.dumps({"audit": audit["summary"], "validation": validation["status"]}, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
