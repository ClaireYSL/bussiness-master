from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from openpyxl import load_workbook


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Repair accounts_main.account_id by mapping account_canonical_name to profile.")
    parser.add_argument("--main-file", required=True, help="Main workbook path.")
    parser.add_argument("--profile-file", required=True, help="Profile workbook path.")
    parser.add_argument("--governance-file", required=True, help="Governance workbook path (reserved for audit context).")
    parser.add_argument("--output-file", required=True, help="Audit report JSON output path.")
    parser.add_argument("--write-back", action="store_true", help="Apply account_id changes to main workbook.")
    parser.add_argument(
        "--fill-missing-generated",
        action="store_true",
        help="Generate deterministic account_id for unresolved names to improve coverage.",
    )
    parser.add_argument("--sheet-name", default="accounts_main", help="Main workbook sheet name.")
    return parser


def _clean(value: object) -> str:
    return str(value or "").strip()


def _parse_dt(value: object) -> datetime:
    text = _clean(value)
    if not text:
        return datetime(1970, 1, 1, tzinfo=timezone.utc)
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(text).astimezone(timezone.utc)
    except ValueError:
        return datetime(1970, 1, 1, tzinfo=timezone.utc)


def _build_profile_index(profile_file: Path) -> tuple[dict[str, str], dict[str, list[dict[str, str]]]]:
    wb = load_workbook(profile_file, read_only=True, data_only=True)
    ws = wb["account_profiles"]
    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    idx = {str(value): i for i, value in enumerate(headers) if value}
    name_candidates: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in ws.iter_rows(min_row=2, values_only=True):
        account_id = _clean(row[idx["account_id"]])
        account_name = _clean(row[idx["account_canonical_name"]])
        if not account_id or not account_name:
            continue
        last_profiled_at = _clean(row[idx.get("last_profiled_at", -1)]) if "last_profiled_at" in idx else ""
        name_candidates[account_name].append(
            {
                "account_id": account_id,
                "last_profiled_at": last_profiled_at,
            }
        )
    latest_map: dict[str, str] = {}
    for name, candidates in name_candidates.items():
        best = sorted(
            candidates,
            key=lambda item: (_parse_dt(item.get("last_profiled_at")), item.get("account_id") or ""),
            reverse=True,
        )[0]
        latest_map[name] = _clean(best.get("account_id"))
    return latest_map, name_candidates


def _build_alias_index(governance_file: Path) -> dict[str, str]:
    wb = load_workbook(governance_file, read_only=True, data_only=True)
    ws = wb["alias_registry"]
    headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    idx = {str(value): i for i, value in enumerate(headers) if value}
    required = {"canonical_account_id", "canonical_name", "alias_name"}
    if not required.issubset(set(idx.keys())):
        wb.close()
        return {}

    mapping: dict[str, str] = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        canonical_id = _clean(row[idx["canonical_account_id"]])
        canonical_name = _clean(row[idx["canonical_name"]])
        alias_name = _clean(row[idx["alias_name"]])
        status = _clean(row[idx.get("status", -1)]).lower() if "status" in idx else "active"
        if not canonical_id or status in {"inactive", "deleted"}:
            continue
        for key in {_norm_name(canonical_name), _norm_name(alias_name)}:
            if key:
                mapping[key] = canonical_id
    wb.close()
    return mapping


def _backup(path: Path) -> str:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = path.with_name(f"{path.stem}.idrepair_backup_{stamp}{path.suffix}")
    shutil.copy2(path, dst)
    return str(dst)


def _norm_name(value: str) -> str:
    text = _clean(value)
    for old, new in [("（", "("), ("）", ")"), (" ", ""), ("　", "")]:
        text = text.replace(old, new)
    return text


def _generated_account_id(name: str) -> str:
    digest = hashlib.sha1(_norm_name(name).encode("utf-8")).hexdigest()[:10]
    return f"acc_gen_{digest}"


def main() -> int:
    args = build_parser().parse_args()
    main_file = Path(args.main_file)
    profile_file = Path(args.profile_file)
    governance_file = Path(args.governance_file)
    latest_map, name_candidates = _build_profile_index(profile_file)
    alias_map = _build_alias_index(governance_file)

    main_wb = load_workbook(main_file)
    ws = main_wb[args.sheet_name]
    headers = [cell.value for cell in ws[1]]
    idx = {str(value): i + 1 for i, value in enumerate(headers) if value}
    if "account_id" not in idx or "account_canonical_name" not in idx:
        raise ValueError("main sheet missing required headers: account_id/account_canonical_name")

    before_nonempty = 0
    after_nonempty = 0
    updated_rows = 0
    unchanged_rows = 0
    unresolved_rows = 0
    collision_rows = 0
    gaps: list[dict[str, object]] = []
    selected_from_collision: list[dict[str, object]] = []
    generated_rows = 0
    generated_ids: set[str] = set()
    chosen_ids: dict[int, str] = {}
    mapping_source_counter: Counter[str] = Counter()
    generated_to_mapped_rows = 0

    for row in range(2, ws.max_row + 1):
        name = _clean(ws.cell(row, idx["account_canonical_name"]).value)
        if not name:
            continue
        old_id = _clean(ws.cell(row, idx["account_id"]).value)
        if old_id:
            before_nonempty += 1
        picked_id = _clean(latest_map.get(name))
        mapping_source = ""
        candidates = name_candidates.get(name) or []
        if len({item["account_id"] for item in candidates}) > 1:
            collision_rows += 1
            selected_from_collision.append(
                {
                    "row": row,
                    "account_name": name,
                    "picked_account_id": picked_id,
                    "candidate_count": len(candidates),
                    "candidates": candidates,
                }
            )
        if picked_id:
            mapping_source = "profile_latest"
        else:
            picked_id = _clean(alias_map.get(_norm_name(name)))
            if picked_id:
                mapping_source = "governance_alias"
        if not picked_id:
            if args.fill_missing_generated:
                picked_id = _generated_account_id(name)
                if picked_id in generated_ids:
                    # Extremely rare digest collision fallback.
                    picked_id = f"{picked_id}_{row}"
                generated_ids.add(picked_id)
                generated_rows += 1
                mapping_source = "generated"
            else:
                unresolved_rows += 1
                gaps.append({"row": row, "account_name": name, "reason": "missing_profile_or_alias_mapping"})
                continue
        mapping_source_counter[mapping_source] += 1
        chosen_ids[row] = picked_id
        if old_id.startswith("acc_gen_") and picked_id and not picked_id.startswith("acc_gen_"):
            generated_to_mapped_rows += 1
        if args.write_back and old_id != picked_id:
            ws.cell(row, idx["account_id"]).value = picked_id
            updated_rows += 1
        elif old_id == picked_id:
            unchanged_rows += 1

    id_to_names: dict[str, set[str]] = defaultdict(set)
    for row in range(2, ws.max_row + 1):
        name = _clean(ws.cell(row, idx["account_canonical_name"]).value)
        aid = _clean(ws.cell(row, idx["account_id"]).value if args.write_back else chosen_ids.get(row))
        if name and aid:
            id_to_names[aid].add(name)
            after_nonempty += 1
    duplicate_id_conflicts = [
        {"account_id": aid, "name_count": len(names), "names": sorted(names)}
        for aid, names in sorted(id_to_names.items())
        if len(names) > 1
    ]

    backup_file = ""
    if args.write_back:
        backup_file = _backup(main_file)
        main_wb.save(main_file)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "main_file": str(main_file),
            "profile_file": str(profile_file),
            "governance_file": str(governance_file),
            "sheet_name": args.sheet_name,
            "write_back": bool(args.write_back),
            "fill_missing_generated": bool(args.fill_missing_generated),
        },
        "backup_file": backup_file,
        "summary": {
            "rows_total": ws.max_row - 1,
            "before_nonempty_account_id": before_nonempty,
            "after_nonempty_account_id": after_nonempty,
            "coverage_ratio": round((after_nonempty / max(ws.max_row - 1, 1)), 6),
            "updated_rows": updated_rows,
            "unchanged_rows": unchanged_rows,
            "unresolved_rows": unresolved_rows,
            "generated_rows": generated_rows,
            "generated_to_mapped_rows": generated_to_mapped_rows,
            "collision_rows": collision_rows,
            "duplicate_id_conflict_count": len(duplicate_id_conflicts),
        },
        "mapping_source_distribution": dict(mapping_source_counter),
        "selected_from_collision": selected_from_collision,
        "duplicate_id_conflicts": duplicate_id_conflicts,
        "id_repair_gap": gaps,
        "field_stats": dict(Counter(item["reason"] for item in gaps)),
    }
    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "output_file": str(output_path),
                "coverage_ratio": payload["summary"]["coverage_ratio"],
                "updated_rows": updated_rows,
                "unresolved_rows": unresolved_rows,
                "duplicate_id_conflict_count": len(duplicate_id_conflicts),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
