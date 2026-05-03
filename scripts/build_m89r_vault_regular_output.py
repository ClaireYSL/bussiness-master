from __future__ import annotations

import json
import re
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[1]
MILESTONES = WORKSPACE / "deliveries/archive/milestones"
M89 = MILESTONES / "milestone89r_vault_regular_output"
STATUS_PANEL = MILESTONES / "milestone56r_trusted_pool_status_panel/trusted_pool_status_panel_v1.json"
POOL = MILESTONES / "milestone47r_trusted_pool_product/trusted_prospect_pool_v1.json"
TRACE = MILESTONES / "milestone47r_trusted_pool_product/source_trace_index_v1.json"
VAULT_ROOT = Path("/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池/07-可信潜客档案")
INDEX_DIR = VAULT_ROOT / "00-索引与说明"
L1_DIR = VAULT_ROOT / "01-L1 ICP强匹配档案"
L2_DIR = VAULT_ROOT / "02-L2正式潜客档案"
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


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=WORKSPACE, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def safe_filename(value: str) -> str:
    return "".join("_" if ch in {'/', '\\', ':', '*', '?', '"', '<', '>', '|'} else ch for ch in value.strip()) or "unknown_prospect"


def trace_by_id(trace: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item.get("prospect_id"): item for item in trace.get("items") or [] if item.get("prospect_id")}


def key_sources(trace_item: dict[str, Any]) -> list[dict[str, Any]]:
    seen = set()
    out = []
    for source in trace_item.get("sources") or []:
        locator = source.get("source_locator") or ""
        if not locator or locator in seen:
            continue
        seen.add(locator)
        out.append(source)
    return out[:5]


def dossier_text(item: dict[str, Any], trace_item: dict[str, Any]) -> str:
    level = item.get("level") or "L3"
    if level == "L1":
        level_text = "L1 高质量静态可信潜客。L1 只表达证据链和 ICP 解释特别充分，不表达经营优先级、团队跟进或触达时间。"
    elif level == "L2":
        level_text = "L2 正式可信潜客档案。"
    else:
        level_text = f"{level} 静态可信等级。"
    source_lines = []
    for source in key_sources(trace_item):
        category = source.get("source_category") or "unknown"
        source_type = source.get("source_type") or source.get("evidence_strength") or "source"
        locator = source.get("source_locator") or ""
        summary = source.get("summary") or ""
        source_lines.append(f"- `{category}` · `{source_type}` · {locator}\n  - {summary}")
    sources = "\n".join(source_lines) if source_lines else f"- 主来源：{item.get('source_locator', '')}"
    return f"""---
prospect_id: {item.get('prospect_id', '')}
static_level: {level}
matched_persona: {item.get('matched_persona', '')}
trusted_status: {item.get('trusted_status', '')}
legacy_field_inherited: false
source_boundary: evidence_first_only
fact_source: trusted_prospect_pool_v1
canonical_update_source: {item.get('canonical_update_source', '')}
---

# {item.get('company_name', '')}

## 静态等级

{level_text}

## 为什么匹配 ICP

{item.get('match_reason', '')}

## 核心产品/服务

{item.get('core_product_service_summary', '')}

## 业务模式

{item.get('business_model_summary', '')}

## 关键 evidence

{sources}

## 风险与待补点

{item.get('risk_or_gap', '')}

## 静态升层说明

{item.get('static_promotion_summary', '')}

## 来源边界

本档案只表达静态 ICP 匹配、证据成熟度和信息完整度；不表达经营优先级、团队跟进或触达时间。事实源以 canonical trusted pool 与 source trace 为准，不继承旧主表或旧档案字段。
"""


def write_dossiers(pool: dict[str, Any], trace: dict[str, Any]) -> list[dict[str, Any]]:
    by_trace = trace_by_id(trace)
    outputs = []
    new_items = [item for item in pool.get("items") or [] if item.get("canonical_update_source") == "M88R_from_M86R_hardened_ready"]
    for item in new_items:
        level = item.get("level")
        target_dir = L1_DIR if level == "L1" else L2_DIR if level == "L2" else None
        if target_dir is None:
            continue
        target_dir.mkdir(parents=True, exist_ok=True)
        path = target_dir / f"{safe_filename(item.get('company_name', ''))}.md"
        before_exists = path.exists()
        path.write_text(dossier_text(item, by_trace.get(item.get("prospect_id"), {})), encoding="utf-8")
        outputs.append({"prospect_id": item.get("prospect_id"), "company_name": item.get("company_name"), "level": level, "path": str(path), "action": "overwrite" if before_exists else "create"})
    return outputs


def index_link(item: dict[str, Any]) -> str:
    level = item.get("level")
    folder = "01-L1 ICP强匹配档案" if level == "L1" else "02-L2正式潜客档案"
    return f"- [[../{folder}/{item.get('company_name')}.md|{item.get('company_name')}]] · `{item.get('matched_persona', '')}` · `{item.get('trusted_status', '')}`"


def write_indexes(pool: dict[str, Any], trace: dict[str, Any]) -> list[dict[str, Any]]:
    items = pool.get("items") or []
    level_counts = Counter(item.get("level") for item in items)
    l1 = sorted([item for item in items if item.get("level") == "L1"], key=lambda x: x.get("company_name", ""))
    l2 = sorted([item for item in items if item.get("level") == "L2"], key=lambda x: x.get("company_name", ""))
    l4 = sorted([item for item in items if item.get("level") == "L4"], key=lambda x: x.get("company_name", ""))
    persona_counts = Counter(item.get("matched_persona") for item in items)

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    l1_index = INDEX_DIR / "L1 ICP强匹配索引.md"
    l1_index.write_text("# L1 ICP强匹配索引\n\n> L1 是静态池最高可信层级，只表达 ICP 强匹配与证据成熟度，不表达经营优先级。\n\n" + f"- 当前 L1 档案数：`{len(l1)}`\n\n" + "\n".join(index_link(item) for item in l1) + "\n", encoding="utf-8")
    written.append({"path": str(l1_index), "kind": "l1_index", "count": len(l1)})

    l2_index = INDEX_DIR / "L2正式档案索引.md"
    l2_index.write_text("# L2正式档案索引\n\n> L2 是正式可给用户阅读的静态可信潜客档案，表达 ICP 匹配与证据成熟度，不表达经营优先级。\n\n" + f"- 当前 L2 档案数：`{len(l2)}`\n\n" + "\n".join(index_link(item) for item in l2) + "\n", encoding="utf-8")
    written.append({"path": str(l2_index), "kind": "l2_index", "count": len(l2)})

    source_index = INDEX_DIR / "Source trace index.md"
    source_lines = ["# Source trace index", "", "> 只追踪新可信池 evidence 来源，不追踪旧主表或旧档案库字段。", ""]
    for trace_item in sorted(trace.get("items") or [], key=lambda x: x.get("company_name", "")):
        sources = key_sources(trace_item)
        if not sources:
            continue
        source = sources[0]
        source_lines.append(f"- `{trace_item.get('prospect_id')}` · {trace_item.get('company_name')} · `{source.get('source_type') or source.get('evidence_strength')}` · {source.get('source_locator')}")
    source_index.write_text("\n".join(source_lines) + "\n", encoding="utf-8")
    written.append({"path": str(source_index), "kind": "source_trace_index", "count": len(trace.get("items") or [])})

    workbench = INDEX_DIR / "可信潜客池工作台.md"
    persona_lines = "\n".join(f"- `{persona}`：`{count}`" for persona, count in sorted(persona_counts.items()))
    workbench.write_text(f"""# 可信潜客池工作台

> Evidence-first L1-L5 v2。当前主状态只表达静态 ICP 匹配与证据成熟度。

## 当前新可信池状态

- L1 ICP 强匹配档案：`{level_counts.get('L1', 0)}`
- L2 正式潜客档案：`{level_counts.get('L2', 0)}`
- L3 可信摘要卡：`{level_counts.get('L3', 0)}`
- L4 待补证候选：`{level_counts.get('L4', 0)}`
- L5 候选线索：`{level_counts.get('L5', 0)}`
- trusted pool 总数：`{len(items)}`

## 用户怎么读

1. 先看 [[L1 ICP强匹配索引|L1 ICP 强匹配索引]]，这是静态证据链和 ICP 解释最充分的一层。
2. 再看 [[L2正式档案索引|L2 正式档案索引]]，这是正式可读可信潜客池基础层。
3. L3/L4/L5 主要用于补证和升层，不作为正式档案入口。

## 画像分布

{persona_lines}

## 当前边界

- 本 vault 不判断是否现在经营、由谁跟进、何时触达。
- 外部反馈可作为补充观察，但不决定静态 L1/L2 分级。
- 旧主表、旧档案库和旧共享版只作 legacy reference，不作为新事实源。
- 正式事实源是 canonical trusted pool 与 source trace。

## 默认入口

- [[L1 ICP强匹配索引|L1 ICP 强匹配索引]]
- [[L2正式档案索引|L2 正式档案索引]]
- [[Source trace index|Source trace index]]
- [[Evidence-first L1-L5 v2分级说明|Evidence-first L1-L5 v2 分级说明]]
""", encoding="utf-8")
    written.append({"path": str(workbench), "kind": "workbench", "count": len(items)})
    return written


def scan_terms(files: list[Path]) -> dict[str, Any]:
    findings = []
    for path in files:
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for term in DYNAMIC_TERMS:
            if term in text:
                findings.append({"file": str(path), "term": term})
    return {"status": "PASS" if not findings else "FAIL", "dynamic_term_findings_count": len(findings), "findings": findings}


def scan_api(files: list[Path]) -> dict[str, Any]:
    findings = []
    for path in files:
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in API_KEY_PATTERNS:
            if pattern.search(text):
                findings.append({"file": str(path), "pattern": pattern.pattern})
    return {"status": "PASS" if not findings else "FAIL", "api_key_findings_count": len(findings), "findings": findings}


def validate(outputs: list[dict[str, Any]], indexes: list[dict[str, Any]]) -> dict[str, Any]:
    py_compile = run(["python3", "-m", "py_compile", rel(Path(__file__))])
    all_files = [Path(row["path"]) for row in outputs + indexes]
    dynamic = scan_terms(all_files)
    api = scan_api(all_files + [Path(__file__)])
    level_counts = Counter(row["level"] for row in outputs)
    assertions = {
        "new_output_count_11": len(outputs) == 11,
        "new_l1_output_count_4": level_counts.get("L1", 0) == 4,
        "new_l2_output_count_7": level_counts.get("L2", 0) == 7,
        "all_output_files_exist": all(Path(row["path"]).exists() for row in outputs),
        "indexes_written": len(indexes) == 4,
        "no_dynamic_terms_in_new_outputs": dynamic["status"] == "PASS",
        "api_key_scan_pass": api["status"] == "PASS",
        "py_compile_pass": py_compile.returncode == 0,
    }
    validation = {"milestone": "M89R", "generated_at": now(), "status": "PASS" if all(assertions.values()) else "FAIL", "py_compile": {"returncode": py_compile.returncode, "stderr": py_compile.stderr}, "dynamic_term_scan": dynamic, "api_key_scan": api, "assertions": assertions}
    write_json(M89 / "m89r_validation_report_v1.json", validation)
    return validation


def update_panel(outputs: list[dict[str, Any]]) -> None:
    panel = read_json(STATUS_PANEL, {})
    counts = Counter(row["level"] for row in outputs)
    panel.update({"generated_at": now(), "overall_status": "PASS_M89R_VAULT_REGULAR_OUTPUT_WRITTEN", "latest_milestone": "M89R", "canonical_next_action": "进入 M90R：整理 L1/L2 用户入口质量与下一批非上市候选补源。", "m89r_vault_regular_output": {"written_count": len(outputs), "l1_written_count": counts.get("L1", 0), "l2_written_count": counts.get("L2", 0), "vault_regular_written": True, "old_workbook_write_enabled": False, "knowledge_asset_write_enabled": False, "persona_registry_write_enabled": False}})
    write_json(STATUS_PANEL, panel)


def main() -> int:
    M89.mkdir(parents=True, exist_ok=True)
    pool = read_json(POOL)
    trace = read_json(TRACE)
    outputs = write_dossiers(pool, trace)
    indexes = write_indexes(pool, trace)
    manifest = {"milestone": "M89R", "generated_at": now(), "status": "PASS_M89R_VAULT_WRITE_MANIFEST_READY", "summary": {"written_count": len(outputs), "l1_written_count": sum(1 for row in outputs if row["level"] == "L1"), "l2_written_count": sum(1 for row in outputs if row["level"] == "L2"), "index_written_count": len(indexes), "old_workbook_write_enabled": False, "knowledge_asset_write_enabled": False, "persona_registry_write_enabled": False}, "outputs": outputs, "indexes": indexes}
    write_json(M89 / "vault_regular_write_manifest_v1.json", manifest)
    no_write = {"milestone": "M89R", "generated_at": now(), "status": "PASS_VAULT_ONLY_WRITE", "vault_regular_written": True, "canonical_pool_updated": False, "canonical_trace_updated": False, "old_workbook_write_enabled": False, "knowledge_asset_write_enabled": False, "persona_registry_write_enabled": False}
    write_json(M89 / "m89r_no_write_proof_v1.json", no_write)
    operating = {"milestone": "M89R", "generated_at": now(), "status": "PASS_M89R_VAULT_REGULAR_OUTPUT_COMPLETE", "summary": manifest["summary"], "next_action": "M90R：质量抽样、入口复核和下一批非上市候选补源规划。"}
    write_json(M89 / "m89r_operating_panel_v1.json", operating)
    handoff = {"milestone": "M89R", "generated_at": now(), "current_scope": "M88R 新增 11 家 canonical 候选写入 vault 正区。", "vault_regular_written": True, "next_command": "python3 scripts/build_m89r_vault_regular_output.py"}
    write_json(M89 / "handoff_snapshot_v1.json", handoff)
    validation = validate(outputs, indexes)
    update_panel(outputs)
    print(json.dumps({"manifest": manifest["summary"], "validation": validation["status"]}, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
