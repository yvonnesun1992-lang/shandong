from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from integration_test.integration_test_report import generate_integration_test_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V5.17 integration test harness checks.")
    parser.add_argument("--scenario", default="normal_flow")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()
    result = generate_integration_test_report(scenario=args.scenario, all_scenarios=args.all)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["verdict"] in {"PASS", "WARNING"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
