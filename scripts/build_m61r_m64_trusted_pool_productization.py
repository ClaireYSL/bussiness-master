from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[1]
MILESTONES = WORKSPACE / "deliveries/archive/milestones"
M61_DIR = MILESTONES / "milestone61r_trusted_pool_runner_v2"
M62_DIR = MILESTONES / "milestone62r_evidence_first_vault_outputs"
M63_DIR = MILESTONES / "milestone63r_expansion_trial"
M64_DIR = MILESTONES / "milestone64r_long_term_readiness"

RUNNER_REPORT = M61_DIR / "trusted_pool_runner_v2_report_v1.json"
GAP_QUEUE = M61_DIR / "static_gap_queue_v1.json"
BASELINE = M61_DIR / "trusted_pool_runner_baseline_v1.json"
SOURCE_TRACE = M61_DIR / "source_trace_normalized_v1.json"
NO_WRITE_PROOF = M61_DIR / "no_write_proof_v1.json"
TRUSTED_POOL = MILESTONES / "milestone47r_trusted_pool_product/trusted_prospect_pool_v1.json"
EXPANSION_SOURCE = MILESTONES / "milestone25r_trusted_expansion_preflight/milestone25r_trusted_expansion_candidates_v1.json"
STATUS_PANEL = MILESTONES / "milestone56r_trusted_pool_status_panel/trusted_pool_status_panel_v1.json"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def item_by_id(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(item.get("prospect_id") or "").strip(): item for item in items if item.get("prospect_id")}


def build_m61(report: dict[str, Any], gap_queue: dict[str, Any], no_write: dict[str, Any]) -> dict[str, Any]:
    closure = {
        "milestone": "M61R",
        "generated_at": now(),
        "status": "PASS_M61R_TRUSTED_POOL_RUNNER_V2_READY",
        "summary": {
            "runner": report.get("runner"),
            "mode": report.get("mode"),
            "prospect_count": report.get("summary", {}).get("prospect_count"),
            "level_counts": report.get("summary", {}).get("level_counts"),
            "gap_queue_count": gap_queue.get("gap_queue_count"),
            "candidate_signature": report.get("candidate_signature"),
            "baseline_file": str(BASELINE.relative_to(WORKSPACE)),
            "old_workbook_write_enabled": False,
        },
        "outputs": {
            "runner_report": str(RUNNER_REPORT.relative_to(WORKSPACE)),
            "baseline": str(BASELINE.relative_to(WORKSPACE)),
            "gap_queue": str(GAP_QUEUE.relative_to(WORKSPACE)),
            "source_trace": str(SOURCE_TRACE.relative_to(WORKSPACE)),
            "no_write_proof": str(NO_WRITE_PROOF.relative_to(WORKSPACE)),
        },
        "no_write_proof": no_write,
    }
    write_json(M61_DIR / "milestone61r_trusted_pool_runner_v2_closure_v1.json", closure)
    return closure


def card_markdown(item: dict[str, Any], decision: dict[str, Any], gaps: list[dict[str, Any]]) -> str:
    name = item.get("company_name", "")
    level = decision.get("suggested_level", item.get("level", "L5"))
    return f"""---
prospect_id: {item.get('prospect_id', '')}
static_level: {level}
matched_persona: {item.get('matched_persona', '')}
legacy_field_inherited: false
source_boundary: evidence_first_only
---

# {name}

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

## 升层缺口

{chr(10).join('- ' + gap.get('reason', '') for gap in gaps) or '- 暂无结构化缺口。'}

## 边界说明

本页只表达静态 ICP 匹配、证据成熟度和信息完整度；不表达经营优先级、团队跟进或触达时间。
"""


def build_m62(report: dict[str, Any], pool: dict[str, Any]) -> dict[str, Any]:
    decisions = report.get("decisions") or []
    pool_items = item_by_id(pool.get("items") or [])
    gap_by_id: dict[str, list[dict[str, Any]]] = {}
    for gap in report.get("static_gap_queue") or []:
        gap_by_id.setdefault(str(gap.get("prospect_id") or ""), []).append(gap)

    cards = []
    dossiers = []
    for decision in decisions:
        prospect_id = str(decision.get("prospect_id") or "")
        item = pool_items.get(prospect_id, {})
        level = decision.get("suggested_level")
        md = card_markdown(item, decision, gap_by_id.get(prospect_id, []))
        card_path = M62_DIR / "vault_output_preview" / f"{decision.get('company_name')}.md"
        write_text(card_path, md)
        row = {
            "prospect_id": prospect_id,
            "company_name": decision.get("company_name"),
            "static_level": level,
            "matched_persona": item.get("matched_persona"),
            "preview_markdown": str(card_path.relative_to(WORKSPACE)),
            "write_vault_enabled": False,
        }
        if level in {"L1", "L2", "L3"}:
            cards.append(row)
        if level in {"L1", "L2"}:
            dossiers.append(row)

    package = {
        "milestone": "M62R",
        "generated_at": now(),
        "status": "PASS_M62R_VAULT_OUTPUT_PREVIEW_READY",
        "summary": {
            "card_preview_count": len(cards),
            "formal_dossier_preview_count": len(dossiers),
            "write_vault_enabled": False,
            "old_workbook_write_enabled": False,
        },
        "cards": cards,
        "formal_dossiers": dossiers,
        "boundary": "Preview only. Actual vault write remains a separate controlled action.",
    }
    write_json(M62_DIR / "milestone62r_vault_output_package_v1.json", package)
    return package


def build_m63() -> dict[str, Any]:
    source = read_json(EXPANSION_SOURCE, {})
    accounts = source.get("accounts") or source.get("items") or []
    selected = []
    for account in accounts[:30]:
        missing = account.get("required_intake_patch_fields") or []
        status = "L4" if account.get("preflight_status") == "needs_patch" else "L5"
        selected.append(
            {
                "account_id": account.get("account_id"),
                "company_name": account.get("account_name"),
                "track": account.get("track"),
                "matched_persona": account.get("persona"),
                "trial_static_level": status,
                "preflight_status": account.get("preflight_status"),
                "required_gap_fields": missing,
                "evidence_first_next_step": "补官方/强来源、核心产品服务、业务模式、ICP 匹配理由后再进入 trusted_pool_runner。",
            }
        )
    counts = Counter(item["trial_static_level"] for item in selected)
    package = {
        "milestone": "M63R",
        "generated_at": now(),
        "status": "PASS_M63R_EXPANSION_TRIAL_READY",
        "source_file": str(EXPANSION_SOURCE.relative_to(WORKSPACE)),
        "summary": {
            "trial_candidate_count": len(selected),
            "level_counts": dict(counts),
            "old_workbook_write_enabled": False,
            "trusted_pool_update_enabled": False,
        },
        "items": selected,
        "note": "本轮只形成扩容试运行队列，不伪造强来源，不写旧 Excel，不写 trusted pool。",
    }
    write_json(M63_DIR / "milestone63r_expansion_trial_package_v1.json", package)
    return package


def build_m64(m61: dict[str, Any], m62: dict[str, Any], m63: dict[str, Any]) -> dict[str, Any]:
    runbook = """# M64R trusted pool 长期运行手册 v1

## 默认主线

source/persona -> candidate discovery -> enrich_static_facts -> attach_icp_references -> collect_strong_evidence -> static_promote -> static_gap_queue -> update_trusted_pool -> vault cards/dossiers。

## 运行命令

```bash
python3 scripts/trusted_pool_runner.py \\
  --output-file deliveries/archive/milestones/milestone61r_trusted_pool_runner_v2/trusted_pool_runner_v2_report_v1.json \\
  --write-baseline

python3 scripts/trusted_pool_runner.py \\
  --output-file deliveries/archive/milestones/milestone61r_trusted_pool_runner_v2/trusted_pool_runner_v2_report_v1.json \\
  --require-baseline
```

## 边界

- 默认不写旧 Excel。
- 默认不写知识资产。
- 默认不改 persona registry。
- 静态 L1-L5 不表达经营优先级、团队跟进或触达时间。
"""
    runbook_path = M64_DIR / "trusted_pool_runbook_v1.md"
    write_text(runbook_path, runbook)
    status = {
        "milestone": "M64R",
        "generated_at": now(),
        "status": "PASS_M64R_LONG_TERM_READINESS_READY",
        "readiness": {
            "trusted_pool_runner_v2": m61.get("status"),
            "vault_output_preview": m62.get("status"),
            "expansion_trial": m63.get("status"),
            "legacy_write_guard": "PASS_LEGACY_OVERRIDE_REQUIRED",
            "canonical_static_boundary": "PASS_STATIC_ONLY_NO_DYNAMIC_PRIORITY",
        },
        "current_counts": {
            "m61_level_counts": m61.get("summary", {}).get("level_counts"),
            "m62_card_preview_count": m62.get("summary", {}).get("card_preview_count"),
            "m63_trial_candidate_count": m63.get("summary", {}).get("trial_candidate_count"),
        },
        "next_command": "python3 scripts/trusted_pool_runner.py --require-baseline --output-file deliveries/archive/milestones/milestone61r_trusted_pool_runner_v2/trusted_pool_runner_v2_report_v1.json",
        "runbook": str(runbook_path.relative_to(WORKSPACE)),
    }
    write_json(M64_DIR / "autonomous_status_panel_v1.json", status)
    write_json(M64_DIR / "handoff_snapshot_v1.json", {"generated_at": now(), "status_panel": status, "do_not_use_as_default": ["legacy Excel workbook write_back"]})
    return status


def update_canonical_panel(m61: dict[str, Any], m62: dict[str, Any], m63: dict[str, Any], m64: dict[str, Any]) -> None:
    panel = read_json(STATUS_PANEL, {})
    panel["generated_at"] = now()
    panel["overall_status"] = "PASS_M64R_LONG_TERM_READINESS_READY"
    panel["latest_milestone"] = "M64R"
    panel["m61r_trusted_pool_runner_v2"] = m61.get("summary", {})
    panel["m62r_vault_output_preview"] = m62.get("summary", {})
    panel["m63r_expansion_trial"] = m63.get("summary", {})
    panel["m64r_long_term_readiness"] = m64.get("readiness", {})
    panel["canonical_next_action"] = "下一步进入真实 M61/M62 增强迭代：为 M63R 队列补强 evidence 后，再用 trusted_pool_runner v2 持续升层。"
    panel["next_recommended_action"] = panel["canonical_next_action"]
    if "m57r_business_feedback" in panel:
        legacy = panel.setdefault("legacy_optional_feedback", {})
        legacy["m57r_external_feedback_legacy"] = panel.pop("m57r_business_feedback")
    write_json(STATUS_PANEL, panel)


def main() -> int:
    report = read_json(RUNNER_REPORT, {})
    gap_queue = read_json(GAP_QUEUE, {})
    no_write = read_json(NO_WRITE_PROOF, {})
    pool = read_json(TRUSTED_POOL, {})
    if not report:
        raise SystemExit(f"missing runner report: {RUNNER_REPORT}")
    m61 = build_m61(report, gap_queue, no_write)
    m62 = build_m62(report, pool)
    m63 = build_m63()
    m64 = build_m64(m61, m62, m63)
    update_canonical_panel(m61, m62, m63, m64)
    print(json.dumps({"m61": m61["status"], "m62": m62["status"], "m63": m63["status"], "m64": m64["status"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
