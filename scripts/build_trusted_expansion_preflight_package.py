from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_M19 = "deliveries/archive/milestones/milestone19_expansion_feedback/milestone19_expansion_feedback_package_v1.json"
DEFAULT_M22R_CANDIDATES = "deliveries/archive/milestones/milestone22r_trusted_writeback_admission/milestone22r_trusted_writeback_candidates_v1.json"
DEFAULT_M24R = "deliveries/archive/milestones/milestone24r_knowledge_source_governance/milestone24r_knowledge_source_governance_package_v1.json"
DEFAULT_OUTPUT_DIR = "deliveries/archive/milestones/milestone25r_trusted_expansion_preflight"
DEFAULT_REVIEW_MD = "docs/03-执行与校验/Milestone 25R-可信扩容预检复盘-v1.md"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build M25R expansion preflight package without write-back or unsafe fact generation.")
    parser.add_argument("--m19-package", default=DEFAULT_M19)
    parser.add_argument("--exclude-candidate-file", default=DEFAULT_M22R_CANDIDATES)
    parser.add_argument("--source-governance-file", default=DEFAULT_M24R)
    parser.add_argument("--target-size", type=int, default=50)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--review-md", default=DEFAULT_REVIEW_MD)
    return parser


def _clean(value: object) -> str:
    return str(value or "").strip()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(path: str | Path, payload: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: str | Path, text: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def _excluded_ids(payload: dict[str, Any]) -> set[str]:
    return {_clean(item.get("account_id")) for item in payload.get("accounts") or [] if isinstance(item, dict) and _clean(item.get("account_id"))}


def _preflight_status(item: dict[str, Any]) -> str:
    status = _clean(item.get("preflight_status"))
    blocking = set(item.get("blocking_codes") or [])
    if status == "executable_now":
        return "executable_now"
    if status == "needs_intake_patch" or blocking & {"missing_field", "official_source_missing", "evidence_thin", "generic_admission"}:
        return "needs_patch"
    return "not_ready"


def _requirements(item: dict[str, Any]) -> list[str]:
    blocking = set(item.get("blocking_codes") or [])
    reqs = []
    if "missing_field" in blocking or _preflight_status(item) == "needs_patch":
        reqs.extend(["公司产品与服务概述", "商业模式概述", "admission_reason_summary"])
    if "official_source_missing" in blocking or _preflight_status(item) == "needs_patch":
        reqs.append("official_or_high_confidence_source")
    if "evidence_thin" in blocking:
        reqs.append("additional_strong_evidence")
    if not reqs:
        reqs.append("manual_preflight_review")
    return sorted(set(reqs))


def _candidate(item: dict[str, Any]) -> dict[str, Any]:
    status = _preflight_status(item)
    return {
        "account_id": _clean(item.get("account_id")),
        "account_name": _clean(item.get("account_name")),
        "track": _clean(item.get("track")),
        "persona": _clean(item.get("persona")),
        "current_level": _clean(item.get("current_level") or "L5"),
        "target_level": _clean(item.get("target_level") or "L3"),
        "preflight_status": status,
        "latest_decision": _clean(item.get("latest_decision")),
        "blocking_codes": item.get("blocking_codes") or [],
        "warning_codes": item.get("warning_codes") or [],
        "required_intake_patch_fields": _requirements(item),
        "selection_reason": "M25R 扩容预检候选；进入 report-only 前必须补齐官方来源和最小核心字段。",
    }


def _render_md(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Milestone 25R-可信扩容预检复盘-v1",
        "",
        "## 摘要",
        "",
        f"- 预检候选：`{summary['candidate_count']}`",
        f"- 分层：`{summary['preflight_status_counts']}`",
        f"- report-only：`{summary['report_only_status']}`",
        f"- 来源治理前置：`{summary['source_governance_ok']}`",
        "",
        "## 结论",
        "",
        "- 本轮只做扩容预检，不生成伪 fact patch。",
        "- 下一步应先补官方来源和最小核心字段，再执行 enrich/promote report-only。",
        "- 本轮未执行真实 write_back。",
        "",
        "## 候选清单",
        "",
    ]
    for item in payload["trusted_expansion_candidates"]:
        lines.append(f"- `{item['preflight_status']}` `{item['account_id']}` {item['account_name']}：需补 `{','.join(item['required_intake_patch_fields'])}`")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    m19 = _load_json(args.m19_package)
    excluded = _excluded_ids(_load_json(args.exclude_candidate_file))
    governance = _load_json(args.source_governance_file)
    source_governance_ok = bool((governance.get("summary") or {}).get("no_write_proof_ok"))

    picked = []
    for item in m19.get("next_batch_candidates") or []:
        if not isinstance(item, dict):
            continue
        account_id = _clean(item.get("account_id"))
        if not account_id or account_id in excluded:
            continue
        picked.append(_candidate(item))
        if len(picked) >= args.target_size:
            break

    requirements = [
        {
            "account_id": item["account_id"],
            "account_name": item["account_name"],
            "required_fields": item["required_intake_patch_fields"],
            "allowed_source_types": ["official_website", "cninfo", "annual_report", "announcement", "ir", "regulatory_disclosure"],
            "forbidden_source_types": ["trusted_prospect_card", "candidate_summary", "llm_candidate_summary"],
            "patch_status": "not_started",
        }
        for item in picked
    ]
    status_counts = Counter(item["preflight_status"] for item in picked)
    summary = {
        "candidate_count": len(picked),
        "target_size": args.target_size,
        "preflight_status_counts": dict(status_counts),
        "track_counts": dict(Counter(item["track"] for item in picked)),
        "persona_counts": dict(Counter(item["persona"] for item in picked)),
        "source_governance_ok": source_governance_ok,
        "report_only_status": "not_run_pre_patch_required",
        "report_only_run_summary_file": "",
        "gate_check_file": "",
        "true_writeback_executed": False,
    }
    output_dir = Path(args.output_dir)
    payload = {
        "batch_id": "milestone25r_trusted_expansion_preflight_package_v1",
        "generated_at": _now(),
        "source_files": {
            "m19_package": args.m19_package,
            "exclude_candidate_file": args.exclude_candidate_file,
            "source_governance_file": args.source_governance_file,
        },
        "policy": {
            "true_writeback_executed": False,
            "report_only_requires_intake_patch_first": True,
            "do_not_generate_generic_facts": True,
            "formal_knowledge_write_enabled": False,
        },
        "summary": summary,
        "trusted_expansion_candidates": picked,
        "intake_patch_requirements": requirements,
    }
    _write_json(output_dir / "milestone25r_trusted_expansion_preflight_package_v1.json", payload)
    _write_json(output_dir / "milestone25r_trusted_expansion_candidates_v1.json", {"batch_id": "milestone25r_trusted_expansion_candidates_v1", "accounts": picked})
    _write_json(output_dir / "milestone25r_intake_patch_requirements_v1.json", {"batch_id": "milestone25r_intake_patch_requirements_v1", "items": requirements})
    _write_text(args.review_md, _render_md(payload))
    print(json.dumps({"output_json": str(output_dir / "milestone25r_trusted_expansion_preflight_package_v1.json"), "review_md": args.review_md, "summary": summary}, ensure_ascii=False, indent=2))
    return 0 if len(picked) == args.target_size and source_governance_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
