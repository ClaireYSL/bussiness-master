from __future__ import annotations

from typing import Any


def _clean(value: object) -> str:
    return str(value or "").strip()


def build_enrich_summary_payload(
    config: dict[str, object],
    enrich: dict[str, object],
    *,
    config_path: str = "",
    enrich_result_path: str = "",
) -> dict[str, object]:
    write_back = enrich.get("write_back") or {}
    items: list[dict[str, object]] = []
    summary = {
        "account_count": 0,
        "ready_for_promote": 0,
        "observation": 0,
        "formal_candidate": 0,
        "minimum_fact_pass": 0,
        "minimum_fact_partial": 0,
        "minimum_fact_fail": 0,
        "official_source_available": 0,
        "official_source_missing": 0,
        "queue_items_created": int(write_back.get("queue_items_created") or 0),
        "evidence_items_created": int(write_back.get("evidence_items_created") or 0),
    }

    for result in enrich.get("results") or []:
        candidate_type = _clean(result.get("candidate_type"))
        minimum_fact_status = _clean(result.get("minimum_fact_status"))
        official_source_status = _clean(result.get("official_source_status"))
        ready = bool(result.get("enrich_ready_for_promote"))
        issue_messages = [
            _clean(issue.get("message")) for issue in (result.get("issues") or []) if _clean(issue.get("message"))
        ]
        warning_messages = [
            _clean(warning.get("message")) for warning in (result.get("warnings") or []) if _clean(warning.get("message"))
        ]
        item = {
            "account_id": _clean(result.get("account_id")),
            "account_name": _clean(result.get("account_canonical_name")),
            "track": _clean(result.get("primary_track")),
            "current_level": _clean(result.get("current_level")),
            "suggested_maturity": _clean(result.get("suggested_maturity")),
            "persona_tag": _clean(result.get("persona_tag")),
            "secondary_persona_tags": result.get("secondary_persona_tags") or [],
            "candidate_type": candidate_type,
            "review_status": _clean(result.get("review_status")),
            "required_queue_type": _clean(result.get("required_queue_type")),
            "minimum_fact_status": minimum_fact_status,
            "official_source_status": official_source_status,
            "enrich_ready_for_promote": ready,
            "validation_gap": _clean(result.get("validation_gap")),
            "knowledge_asset_count": len(result.get("knowledge_asset_refs") or []),
            "talk_track_count": len(result.get("talk_track_refs") or []),
            "issue_messages": issue_messages,
            "warning_messages": warning_messages,
            "summary": _clean(result.get("summary")),
        }
        items.append(item)
        summary["account_count"] += 1
        if ready:
            summary["ready_for_promote"] += 1
        if candidate_type == "observation":
            summary["observation"] += 1
        if candidate_type == "formal_candidate":
            summary["formal_candidate"] += 1
        if minimum_fact_status == "pass":
            summary["minimum_fact_pass"] += 1
        elif minimum_fact_status == "partial":
            summary["minimum_fact_partial"] += 1
        elif minimum_fact_status == "fail":
            summary["minimum_fact_fail"] += 1
        if official_source_status == "available":
            summary["official_source_available"] += 1
        elif official_source_status == "missing":
            summary["official_source_missing"] += 1

    return {
        "batch_id": _clean(config.get("batch_id") or enrich.get("batch_id")),
        "goal": _clean(config.get("goal") or enrich.get("goal")),
        "rectification_file": _clean(enrich.get("rectification_file") or config.get("rectification_file")),
        "selection": enrich.get("selection") or {"account_ids": list(config.get("account_ids") or [])},
        "source_files": {
            "config_file": config_path,
            "enrich_result_file": enrich_result_path,
        },
        "summary": summary,
        "write_back": write_back,
        "items": items,
    }


def render_enrich_review_markdown(payload: dict[str, Any]) -> str:
    summary = payload.get("summary") or {}
    items = payload.get("items") or []
    lines = [
        f"# {payload.get('batch_id')} enrich复盘-v1",
        "",
        "## 批次概览",
        "",
        f"- 目标：`{_clean(payload.get('goal'))}`",
        f"- 样本数：`{summary.get('account_count', 0)}`",
        f"- 可进入 promote：`{summary.get('ready_for_promote', 0)}`",
        f"- 候选类型：`formal_candidate={summary.get('formal_candidate', 0)} / observation={summary.get('observation', 0)}`",
        (
            f"- 最小事实：`pass={summary.get('minimum_fact_pass', 0)} / "
            f"partial={summary.get('minimum_fact_partial', 0)} / fail={summary.get('minimum_fact_fail', 0)}`"
        ),
        f"- 官方源状态：`available={summary.get('official_source_available', 0)} / missing={summary.get('official_source_missing', 0)}`",
        (
            f"- 写回治理：`queue_items_created={summary.get('queue_items_created', 0)} / "
            f"evidence_items_created={summary.get('evidence_items_created', 0)}`"
        ),
        "",
        "## 分对象复盘",
        "",
    ]
    for item in items:
        lines.extend(
            [
                f"### {_clean(item.get('account_name'))} / `{_clean(item.get('account_id'))}`",
                "",
                (
                    f"- 主线 / 画像：`{_clean(item.get('track'))} / {_clean(item.get('persona_tag'))}`"
                    f"；次级画像={len(item.get('secondary_persona_tags') or [])}"
                ),
                f"- 层级建议：`{_clean(item.get('current_level'))} -> {_clean(item.get('suggested_maturity'))}`",
                (
                    f"- enrich 判定：`{_clean(item.get('candidate_type'))}`，"
                    f"`minimum_fact={_clean(item.get('minimum_fact_status'))}`，"
                    f"`official_source={_clean(item.get('official_source_status'))}`，"
                    f"`ready_for_promote={item.get('enrich_ready_for_promote')}`"
                ),
                f"- review 状态：`{_clean(item.get('review_status'))}`；建议队列=`{_clean(item.get('required_queue_type'))}`",
                (
                    f"- 知识挂接：`knowledge_assets={item.get('knowledge_asset_count', 0)} / "
                    f"talk_tracks={item.get('talk_track_count', 0)}`"
                ),
                f"- 结论：{_clean(item.get('summary'))}",
            ]
        )
        validation_gap = _clean(item.get("validation_gap"))
        if validation_gap:
            lines.append(f"- 待验证项：{validation_gap}")
        issue_messages = item.get("issue_messages") or []
        warning_messages = item.get("warning_messages") or []
        if issue_messages:
            lines.extend(["- 阻塞项：", *[f"- {message}" for message in issue_messages]])
        if warning_messages:
            lines.extend(["- 风险项：", *[f"- {message}" for message in warning_messages]])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
