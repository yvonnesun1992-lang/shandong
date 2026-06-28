from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sandbox_sim.sandbox_robustness_report import generate_sandbox_robustness_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V5.12 local sandbox robustness suite.")
    parser.add_argument("--scenario", default="full_fill")
    parser.add_argument("--ticks", type=int, default=1000)
    parser.add_argument("--symbols", default="")
    parser.add_argument("--all-scenarios", action="store_true")
    args = parser.parse_args()

    result = generate_sandbox_robustness_report(scenario=args.scenario, ticks=args.ticks, all_scenarios=args.all_scenarios)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["verdict"] in {"PASS", "WARNING"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
