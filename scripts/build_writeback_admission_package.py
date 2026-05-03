from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_PROMOTE = "deliveries/archive/milestones/milestone14_2_intake_quality_unblock/milestone14_2_intake_quality_promote_v1.json"
DEFAULT_GATE = "deliveries/archive/repairs/milestone14_2_intake_quality_gate_check_v1.json"
DEFAULT_FACT_PATCH = "configs/execution_batches/milestone14_2_intake_quality_facts_v1.json"
DEFAULT_RUN_SUMMARY = "deliveries/archive/milestones/milestone17_writeback_admission/milestone17_writeback_admission_run_summary_v1.json"
DEFAULT_OUTPUT_JSON = "deliveries/archive/milestones/milestone17_writeback_admission/milestone17_writeback_admission_package_v1.json"
DEFAULT_OUTPUT_MD = "docs/03-执行与校验/Milestone 17-写回候选准入试点复盘-v1.md"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build non-mutating write-back admission package for allow candidates.")
    parser.add_argument("--promote-file", default=DEFAULT_PROMOTE)
    parser.add_argument("--gate-file", default=DEFAULT_GATE)
    parser.add_argument("--fact-patch-file", default=DEFAULT_FACT_PATCH)
    parser.add_argument("--run-summary-file", default=DEFAULT_RUN_SUMMARY)
    parser.add_argument("--output-json", default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", default=DEFAULT_OUTPUT_MD)
    return parser


def _clean(value: object) -> str:
    return str(value or "").strip()


def _load_json(path: str) -> dict[str, Any]:
    target = Path(path)
    if not target.exists():
        return {}
    return json.loads(target.read_text(encoding="utf-8"))


def _write_json(path: str, payload: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: str, text: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def _gate_decision(item: dict[str, Any]) -> str:
    gate = item.get("promotion_gate") if isinstance(item.get("promotion_gate"), dict) else {}
    return _clean(gate.get("decision"))


def _render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Milestone 17-写回候选准入试点复盘-v1",
        "",
        "## 摘要",
        "",
        f"- allow 候选：`{summary['allow_candidate_count']}`",
        f"- gate：`{'PASS' if summary['gate_ok'] else 'FAIL'}`",
        f"- 本轮真实写回：`{summary['writeback_executed']}`",
        f"- 建议动作：{summary['recommended_action']}",
        "",
        "## 候选清单",
        "",
    ]
    for item in payload["candidates"]:
        lines.append(f"- `{item['account_id']}` {item['account_name']}：`{item['persona']}`，{item['writeback_admission_note']}")
    lines.extend(
        [
            "",
            "## 安全边界",
            "",
            "- 本包只证明这些对象在 patch 叠加后具备写回准入，不自动修改工作簿。",
            "- 若用户确认真实写回，必须使用现有 baseline 与 `--require-report-baseline`，并在写回后重新执行 workbook integrity。",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = build_parser().parse_args()
    promote = _load_json(args.promote_file)
    gate = _load_json(args.gate_file)
    fact_patch = _load_json(args.fact_patch_file)
    run_summary = _load_json(args.run_summary_file)
    fact_by_id = {_clean(item.get("account_id")): item for item in fact_patch.get("accounts") or [] if isinstance(item, dict)}

    candidates = []
    for item in promote.get("results") or []:
        if not isinstance(item, dict) or _gate_decision(item) != "allow":
            continue
        account_id = _clean(item.get("account_id"))
        fact = fact_by_id.get(account_id, {})
        candidates.append(
            {
                "account_id": account_id,
                "account_name": _clean(item.get("account_canonical_name")),
                "persona": _clean(item.get("persona_tag")),
                "target_level": _clean(item.get("target_level")),
                "source_evidence_count": len(fact.get("evidence_rows") or []),
                "writeback_admission_note": "patch 叠加后 allow；真实写回需用户确认，且应保留 pending_review 到 active 的业务确认边界。",
            }
        )
    promote_write = ((run_summary.get("promote") or {}).get("write_back") or {}) if run_summary else {}
    writeback_executed = bool(promote_write.get("enabled"))
    promoted = int(promote_write.get("promoted") or 0)
    skipped = int(promote_write.get("skipped") or 0)
    payload = {
        "batch_id": "milestone17_writeback_admission_package_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_files": {
            "promote_file": args.promote_file,
            "gate_file": args.gate_file,
            "fact_patch_file": args.fact_patch_file,
        },
        "summary": {
            "allow_candidate_count": len(candidates),
            "decision_counts": dict(Counter(_gate_decision(item) for item in promote.get("results") or [] if isinstance(item, dict))),
            "gate_ok": bool(gate.get("ok")),
            "writeback_executed": writeback_executed,
            "promoted": promoted,
            "skipped": skipped,
            "recommended_action": "M17 已完成真实写回；下一步进入写回后复核和 M18 运营化。" if writeback_executed else "暂停在准入包，不执行真实 write_back；如要落表，需要用户单独确认。",
        },
        "candidates": candidates,
    }
    _write_json(args.output_json, payload)
    _write_text(args.output_md, _render_markdown(payload))
    print(json.dumps({"output_json": args.output_json, "output_md": args.output_md, "summary": payload["summary"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
