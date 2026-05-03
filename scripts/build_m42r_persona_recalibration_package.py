from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[1]
DEFAULT_M41_INVENTORY = "deliveries/archive/milestones/milestone41r_source_material_inventory/milestone41r_source_material_inventory_v2.json"
DEFAULT_OUTPUT_DIR = "deliveries/archive/milestones/milestone42r_persona_recalibration"
DEFAULT_REVIEW_MD = "docs/03-执行与校验/Milestone 42R-ICP画像体系重校准-v1.md"
PERSONA_DIR = Path("/Users/clairelu2026/26M3-Obsidian-潜客池/潜客池/02-画像")

BOUNDARY_GROUPS = [
    ("retail_high_sku_brand", "retail_multi_store", "品牌全渠道 SKU 复杂度 vs 门店网络经营复杂度"),
    ("fnb_chain_beverage_coffee", "fnb_chain_standardized", "茶饮咖啡高频门店 vs 标准化连锁餐饮"),
    ("cbec_multi_platform_brand", "cbec_platform_operator", "跨境品牌经营主体 vs 平台/代运营服务商"),
    ("mfg_multi_factory_group", "mfg_rnd_sales_complex", "多工厂运营管控 vs 研产销/订单交付复杂度"),
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M42R persona evidence map and refresh proposals.")
    parser.add_argument("--m41-inventory", default=DEFAULT_M41_INVENTORY)
    parser.add_argument("--persona-dir", default=str(PERSONA_DIR))
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--review-md", default=DEFAULT_REVIEW_MD)
    return parser


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: str | Path, payload: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: str | Path, text: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def _read_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _persona_files(persona_dir: Path) -> list[dict[str, Any]]:
    files = []
    for path in sorted(persona_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        first_heading = ""
        for line in text.splitlines():
            if line.startswith("#"):
                first_heading = line.lstrip("#").strip()
                break
        files.append({
            "persona_id": path.stem,
            "persona_file": str(path),
            "display_name": first_heading or path.stem,
            "definition_excerpt": re.sub(r"\s+", " ", text[:500]).strip(),
        })
    return files


def _is_primary_learning_material(item: dict[str, Any]) -> bool:
    return item.get("file_type") in {"md", "pdf", "docx", "doc", "pptx", "ppt"} and item.get("learnability_status") != "supporting_attachment"


def _source_strength(item: dict[str, Any]) -> str:
    if item.get("already_formal_asset") or item.get("learnability_status") == "already_asset":
        return "formal_asset_or_transformed_source"
    if item.get("learnability_status") == "learnable_now":
        return "queued_primary_source"
    if item.get("learnability_status") == "needs_triage":
        return "triage_primary_source"
    return "weak_or_excluded"


def _build_evidence_map(personas: list[dict[str, Any]], materials: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_persona: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in materials:
        persona = item.get("persona_guess") or "unknown"
        if persona == "unknown" or not _is_primary_learning_material(item):
            continue
        by_persona[persona].append(item)

    rows = []
    for persona in personas:
        persona_id = persona["persona_id"]
        evidence_items = by_persona.get(persona_id, [])
        strength_counts = Counter(_source_strength(i) for i in evidence_items)
        examples = []
        for item in sorted(evidence_items, key=lambda i: (i.get("priority", "P9"), i.get("material_title", "")))[:8]:
            examples.append({
                "material_id": item.get("material_id"),
                "title": item.get("material_title"),
                "source_root": item.get("source_root"),
                "source_locator": item.get("material_path_or_url"),
                "learnability_status": item.get("learnability_status"),
                "source_strength": _source_strength(item),
                "matched_keywords": item.get("matched_keywords") or [],
            })
        if len(evidence_items) >= 3 and (strength_counts.get("formal_asset_or_transformed_source", 0) + strength_counts.get("queued_primary_source", 0)) >= 1:
            support_status = "source_supported"
        elif len(evidence_items) >= 1:
            support_status = "needs_source_validation"
        else:
            support_status = "source_gap"
        rows.append({
            "persona_id": persona_id,
            "display_name": persona.get("display_name"),
            "persona_file": persona.get("persona_file"),
            "support_status": support_status,
            "evidence_count": len(evidence_items),
            "strength_counts": dict(strength_counts),
            "representative_evidence": examples,
        })
    return rows


def _build_refresh_proposals(evidence_map: list[dict[str, Any]]) -> list[dict[str, Any]]:
    proposals = []
    for row in evidence_map:
        status = row["support_status"]
        if status == "source_supported":
            proposal = "keep_definition_with_evidence_binding"
            rationale = "已有真实客户案例/解决方案材料支撑，建议先绑定 evidence map，再在人工评审后决定是否微调定义。"
        elif status == "needs_source_validation":
            proposal = "do_not_change_registry_collect_more_source"
            rationale = "已有少量材料但不足以刷新画像定义；先补真实案例或解决方案来源。"
        else:
            proposal = "mark_needs_source_validation"
            rationale = "当前 M41R 原素材未找到足够支撑，不应继续用该画像大规模筛潜客。"
        proposals.append({
            "persona_id": row["persona_id"],
            "proposal_type": proposal,
            "current_support_status": status,
            "evidence_count": row["evidence_count"],
            "rationale": rationale,
            "registry_write_enabled": False,
        })
    return proposals


def _build_boundary_questions(evidence_map: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {row["persona_id"]: row for row in evidence_map}
    questions = []
    for left, right, topic in BOUNDARY_GROUPS:
        if left not in by_id or right not in by_id:
            continue
        questions.append({
            "question_id": f"m42r_boundary_{left}__{right}",
            "topic": topic,
            "left_persona": left,
            "right_persona": right,
            "left_evidence_count": by_id[left]["evidence_count"],
            "right_evidence_count": by_id[right]["evidence_count"],
            "decision_needed": "当候选同时命中两边时，优先使用哪个主画像，或是否保留 secondary_persona。",
            "status": "open_boundary_question",
        })
    for row in evidence_map:
        if row["support_status"] == "source_gap":
            questions.append({
                "question_id": f"m42r_source_gap_{row['persona_id']}",
                "topic": "画像缺少真实来源支撑",
                "persona_id": row["persona_id"],
                "decision_needed": "补真实客户案例/解决方案之前，不建议作为 M44R 新潜客主筛选画像。",
                "status": "source_gap_question",
            })
    return questions


def _build_source_gap_queue(evidence_map: list[dict[str, Any]]) -> list[dict[str, Any]]:
    queue = []
    for row in evidence_map:
        if row["support_status"] == "source_supported":
            continue
        queue.append({
            "gap_id": f"m42r_gap_{row['persona_id']}",
            "persona_id": row["persona_id"],
            "support_status": row["support_status"],
            "evidence_count": row["evidence_count"],
            "required_source_type": ["真实客户案例", "解决方案", "权威行业研究", "客户公开演讲/公开案例"],
            "forbidden_source_type": ["潜客摘要反推", "旧潜客档案字段", "未证实销售判断"],
            "next_action": "补齐真实来源后再刷新画像定义 proposal。",
        })
    return queue


def _render_md(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Milestone 42R-ICP画像体系重校准-v1",
        "",
        "## 结论",
        "",
        f"- 画像总数：`{summary['persona_count']}`",
        f"- 来源支撑画像：`{summary['source_supported_count']}`",
        f"- 需补源验证画像：`{summary['needs_source_validation_count']}`",
        f"- 来源缺口画像：`{summary['source_gap_count']}`",
        f"- 边界问题：`{summary['boundary_question_count']}`",
        "",
        "## 关键边界",
        "",
        "- 本轮只生成 `persona_definition_refresh_proposal`，不覆盖正式画像 registry。",
        "- 画像证据只能来自 M41R 的真实客户案例、解决方案、权威材料清单。",
        "- 潜客产出不能反向成为画像正例或知识资产来源。",
        "",
        "## 下一步",
        "",
        "- M43R：落地新可信潜客 intake schema 和校验器。",
        "- M44R：仅用 `source_supported` 或已人工确认的画像做首批 20-30 家 evidence-first 试运行。",
    ]
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    m41 = _read_json(args.m41_inventory)
    materials = m41.get("materials") or []
    personas = _persona_files(Path(args.persona_dir))
    evidence_map = _build_evidence_map(personas, materials)
    proposals = _build_refresh_proposals(evidence_map)
    boundary_questions = _build_boundary_questions(evidence_map)
    source_gaps = _build_source_gap_queue(evidence_map)
    status_counts = Counter(row["support_status"] for row in evidence_map)
    summary = {
        "persona_count": len(personas),
        "source_supported_count": status_counts.get("source_supported", 0),
        "needs_source_validation_count": status_counts.get("needs_source_validation", 0),
        "source_gap_count": status_counts.get("source_gap", 0),
        "boundary_question_count": len(boundary_questions),
        "source_gap_queue_count": len(source_gaps),
        "registry_write_enabled": False,
        "knowledge_asset_write_enabled": False,
        "prospect_generation_enabled": False,
        "no_write_proof_ok": True,
    }
    payload = {
        "batch_id": "milestone42r_persona_recalibration_package_v1",
        "generated_at": _now(),
        "inputs": {
            "m41_inventory": str(Path(args.m41_inventory)),
            "persona_dir": str(Path(args.persona_dir)),
        },
        "summary": summary,
        "persona_evidence_map": evidence_map,
        "persona_definition_refresh_proposal": proposals,
        "persona_boundary_questions": boundary_questions,
        "source_gap_queue": source_gaps,
    }
    output_dir = Path(args.output_dir)
    _write_json(output_dir / "milestone42r_persona_recalibration_package_v1.json", payload)
    _write_json(output_dir / "milestone42r_persona_evidence_map_v1.json", {"generated_at": payload["generated_at"], "summary": summary, "items": evidence_map})
    _write_json(output_dir / "milestone42r_persona_definition_refresh_proposal_v1.json", {"generated_at": payload["generated_at"], "summary": summary, "items": proposals})
    _write_json(output_dir / "milestone42r_persona_boundary_questions_v1.json", {"generated_at": payload["generated_at"], "summary": summary, "items": boundary_questions})
    _write_json(output_dir / "milestone42r_source_gap_queue_v1.json", {"generated_at": payload["generated_at"], "summary": summary, "items": source_gaps})
    _write_text(args.review_md, _render_md(payload))
    print(json.dumps({"output_dir": str(output_dir), "review_md": args.review_md, "summary": summary}, ensure_ascii=False, indent=2))
    ok = len(personas) > 0 and summary["no_write_proof_ok"] and not summary["registry_write_enabled"] and not summary["knowledge_asset_write_enabled"]
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
