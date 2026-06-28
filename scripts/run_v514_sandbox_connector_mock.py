from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sandbox_connector.mock_connector_report import generate_mock_connector_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V5.14 sandbox connector mock checks.")
    parser.add_argument("--scenario", default="accepted")
    parser.add_argument("--all-scenarios", action="store_true")
    args = parser.parse_args()
    result = generate_mock_connector_report(scenario=args.scenario, all_scenarios=args.all_scenarios)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["verdict"] in {"PASS", "WARNING"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
