from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[1]
MILESTONES = WORKSPACE / "deliveries/archive/milestones"
STATUS_PANEL = MILESTONES / "milestone56r_trusted_pool_status_panel/trusted_pool_status_panel_v1.json"

MODE_COMMANDS = {
    "readiness": [["python3", "scripts/build_m99r_m105_product_system.py", "--stage", "readiness"]],
    "learn": [["python3", "scripts/build_m91r_m94_learning_system.py"], ["python3", "scripts/build_m99r_m105_product_system.py", "--stage", "learn"]],
    "persona": [["python3", "scripts/build_m91r_m94_learning_system.py"], ["python3", "scripts/build_m99r_m105_product_system.py", "--stage", "persona"]],
    "prospect": [["python3", "scripts/build_m95r_m98_learning_pool_operating_system.py"], ["python3", "scripts/build_m99r_m105_product_system.py", "--stage", "prospect"]],
    "publish": [["python3", "scripts/build_m99r_m105_product_system.py", "--stage", "publish"]],
    "scale-plan": [["python3", "scripts/build_m99r_m105_product_system.py", "--stage", "scale-plan"]],
    "all": [["python3", "scripts/build_m99r_m105_product_system.py", "--stage", "all"]],
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def run(cmd: list[str]) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=WORKSPACE, text=True, capture_output=True)
    return {"cmd": cmd, "returncode": proc.returncode, "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-4000:]}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="BusinessMaster unified product-system pipeline entrypoint.")
    parser.add_argument("--mode", choices=sorted(MODE_COMMANDS), default="readiness")
    parser.add_argument("--dry-run", action="store_true", help="Show commands and current status without running builders.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    commands = MODE_COMMANDS[args.mode]
    panel = read_json(STATUS_PANEL)
    if args.dry_run:
        print(json.dumps({"mode": args.mode, "generated_at": now(), "commands": commands, "current_status": {"latest_milestone": panel.get("latest_milestone"), "overall_status": panel.get("overall_status"), "counts": panel.get("counts")}}, ensure_ascii=False, indent=2))
        return 0
    results = [run(cmd) for cmd in commands]
    status = "PASS" if all(result["returncode"] == 0 for result in results) else "FAIL"
    print(json.dumps({"mode": args.mode, "status": status, "results": results}, ensure_ascii=False, indent=2))
    return 0 if status == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
