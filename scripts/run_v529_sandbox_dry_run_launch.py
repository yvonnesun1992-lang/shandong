from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.v5_sandbox_dry_run_launch_config import get_dry_run_launch_provider, get_dry_run_launch_status
from sandbox_dry_run_launch.go_no_go_gate import build_go_no_go_summary
from sandbox_dry_run_launch.launch_safety_validator import build_launch_safety_summary
from sandbox_dry_run_launch.preflight_checklist import build_preflight_checklist
from sandbox_dry_run_launch.sandbox_dry_run_launch_report import generate_sandbox_dry_run_launch_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V5.29 sandbox dry-run launch plan review.")
    parser.add_argument("--provider", default=None)
    parser.add_argument("--check", choices=["all", "preflight", "gate", "safety"], default="all")
    args = parser.parse_args()

    provider = args.provider or get_dry_run_launch_provider()
    if args.check == "preflight":
        payload = {"verdict": "WARNING", **build_preflight_checklist(provider)}
    elif args.check == "gate":
        payload = {"verdict": "WARNING", **build_go_no_go_summary(provider)}
    elif args.check == "safety":
        payload = {"verdict": "WARNING", **build_launch_safety_summary()}
    else:
        payload = generate_sandbox_dry_run_launch_report(provider=provider, check=args.check)
    payload["status"] = get_dry_run_launch_status()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 1 if payload.get("verdict") == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
