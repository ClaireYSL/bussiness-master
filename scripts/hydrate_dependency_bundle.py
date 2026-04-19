from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Hydrate dependency workbook bundle into target directory.")
    parser.add_argument("--bundle-dir", required=True, help="Directory containing bundled workbook files.")
    parser.add_argument("--target-dir", required=True, help="Target directory, e.g. ~/Documents/Obsidian-Codex/潜客池")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    bundle_dir = Path(args.bundle_dir).expanduser().resolve()
    target_dir = Path(args.target_dir).expanduser().resolve()
    if not bundle_dir.exists():
        raise FileNotFoundError(f"bundle dir not found: {bundle_dir}")
    target_dir.mkdir(parents=True, exist_ok=True)

    copied: list[str] = []
    skipped: list[str] = []
    for src in sorted(bundle_dir.glob("*.xlsx")):
        dst = target_dir / src.name
        if dst.exists() and not args.overwrite:
            skipped.append(str(dst))
            continue
        shutil.copy2(src, dst)
        copied.append(str(dst))

    print(
        json.dumps(
            {
                "bundle_dir": str(bundle_dir),
                "target_dir": str(target_dir),
                "copied_count": len(copied),
                "skipped_count": len(skipped),
                "copied": copied,
                "skipped": skipped,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
