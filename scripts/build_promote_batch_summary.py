from __future__ import annotations

import argparse
import json
from pathlib import Path

import sys

WORKSPACE = Path(__file__).resolve().parents[1]
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from shared.static_pool import build_promote_summary_payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a normalized summary package for a promote batch.")
    parser.add_argument("--config-file", required=True, help="Promote batch config JSON.")
    parser.add_argument("--promote-result-file", required=True, help="Promote result JSON.")
    parser.add_argument("--output-file", required=True, help="Summary output JSON.")
    return parser

def load_json(path: str | Path) -> dict[str, object]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    args = build_parser().parse_args()
    config = load_json(args.config_file)
    promote = load_json(args.promote_result_file)

    payload = build_promote_summary_payload(
        config,
        promote,
        config_path=str(args.config_file),
        promote_result_path=str(args.promote_result_file),
    )
    Path(args.output_file).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output_file": args.output_file, "summary": payload.get("summary") or {}}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
