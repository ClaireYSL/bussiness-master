from __future__ import annotations

import argparse
import json
from pathlib import Path

import sys

WORKSPACE = Path(__file__).resolve().parents[1]
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from shared.static_pool import render_promote_review_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render a normalized Markdown review for a promote batch.")
    parser.add_argument("--summary-file", required=True, help="Promote summary JSON.")
    parser.add_argument("--output-file", required=True, help="Markdown review output.")
    return parser

def load_json(path: str | Path) -> dict[str, object]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    args = build_parser().parse_args()
    payload = load_json(args.summary_file)
    Path(args.output_file).write_text(render_promote_review_markdown(payload), encoding="utf-8")
    print(json.dumps({"output_file": args.output_file, "item_count": len(payload.get("items") or [])}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
