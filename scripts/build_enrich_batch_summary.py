from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from shared.static_pool import build_enrich_summary_payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a normalized summary package for an enrich batch.")
    parser.add_argument("--config-file", required=True, help="Enrich batch config JSON.")
    parser.add_argument("--enrich-result-file", required=True, help="Enrich result JSON.")
    parser.add_argument("--output-file", required=True, help="Summary output JSON.")
    return parser


def load_json(path: str | Path) -> dict[str, object]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    args = build_parser().parse_args()
    config = load_json(args.config_file)
    enrich = load_json(args.enrich_result_file)
    payload = build_enrich_summary_payload(
        config,
        enrich,
        config_path=str(args.config_file),
        enrich_result_path=str(args.enrich_result_file),
    )
    Path(args.output_file).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output_file": args.output_file, "summary": payload.get("summary") or {}}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
