from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import sys

WORKSPACE = Path(__file__).resolve().parents[1]
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from shared.static_pool import check_workbook_integrity


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check workbook zip/CRC integrity by deep-reading sheets.")
    parser.add_argument("--main-file", required=True, help="Main workbook path.")
    parser.add_argument("--profile-file", required=True, help="Profile workbook path.")
    parser.add_argument("--governance-file", required=True, help="Governance workbook path.")
    parser.add_argument("--output-file", required=True, help="Where to write integrity report JSON.")
    parser.add_argument("--shallow", action="store_true", help="Only open workbook metadata, skip row-level deep scan.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    files = [Path(args.main_file), Path(args.profile_file), Path(args.governance_file)]
    report = check_workbook_integrity(files, deep_scan=not args.shallow)
    payload = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "report": report,
    }
    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output_file": str(output_path), "ok": report.get("ok")}, ensure_ascii=False, indent=2))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

