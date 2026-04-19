from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sync static-pool-raw-materials from source to target.")
    parser.add_argument("--source", required=True, help="Source raw-materials root.")
    parser.add_argument("--target", required=True, help="Target raw-materials root.")
    parser.add_argument("--delete", action="store_true", help="Delete files in target that do not exist in source.")
    return parser


def _sync_tree(source: Path, target: Path, *, delete: bool) -> dict[str, int]:
    copied = 0
    updated = 0
    deleted = 0
    seen: set[Path] = set()

    for src in source.rglob("*"):
        rel = src.relative_to(source)
        dst = target / rel
        seen.add(rel)
        if src.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists():
            shutil.copy2(src, dst)
            copied += 1
            continue
        src_stat = src.stat()
        dst_stat = dst.stat()
        if src_stat.st_size != dst_stat.st_size or int(src_stat.st_mtime) != int(dst_stat.st_mtime):
            shutil.copy2(src, dst)
            updated += 1

    if delete and target.exists():
        for dst in sorted(target.rglob("*"), reverse=True):
            rel = dst.relative_to(target)
            if rel in seen:
                continue
            if dst.is_file():
                dst.unlink()
                deleted += 1
            elif dst.is_dir():
                try:
                    dst.rmdir()
                except OSError:
                    pass
    return {"copied": copied, "updated": updated, "deleted": deleted}


def main() -> int:
    args = build_parser().parse_args()
    source = Path(args.source).expanduser().resolve()
    target = Path(args.target).expanduser().resolve()
    if not source.exists():
        raise FileNotFoundError(f"source not found: {source}")
    if not source.is_dir():
        raise NotADirectoryError(f"source is not a directory: {source}")
    target.mkdir(parents=True, exist_ok=True)
    stats = _sync_tree(source, target, delete=args.delete)
    print(
        json.dumps(
            {
                "source": str(source),
                "target": str(target),
                "delete": bool(args.delete),
                **stats,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
