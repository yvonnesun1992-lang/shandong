from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sandbox_bridge.sandbox_bridge_report import generate_sandbox_bridge_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V5.16 sandbox bridge checks.")
    parser.add_argument("--test", default="route", choices=["route", "transform", "normalize"])
    args = parser.parse_args()
    result = generate_sandbox_bridge_report(args.test)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["verdict"] in {"PASS", "WARNING"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
