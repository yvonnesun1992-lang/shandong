from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from brand_system.brand_orchestrator import build_brand_system_status
from brand_system.brand_safety_validator import build_brand_safety_summary
from brand_system.design_system import get_design_system
from config.v5_brand_system_config import get_brand_status
from runtime.brand_consistency_check import run_brand_consistency_check


BANNER = """=================================
Shandong Quantitative System
Institutional Quant Platform
Version V5
================================="""


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V5.44 brand system checks.")
    parser.add_argument("--check", choices=["status", "design", "consistency", "safety"])
    args = parser.parse_args()

    if args.check == "status":
        payload = get_brand_status()
    elif args.check == "design":
        payload = get_design_system()
    elif args.check == "consistency":
        payload = run_brand_consistency_check()
    elif args.check == "safety":
        payload = build_brand_safety_summary()
    else:
        payload = build_brand_system_status()

    print(BANNER, file=sys.stderr)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if payload.get("verdict") == "FAIL" or payload.get("safe") is False else 0


if __name__ == "__main__":
    raise SystemExit(main())
