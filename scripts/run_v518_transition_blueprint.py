from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from transition.transition_blueprint_report import generate_transition_blueprint_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V5.18 transition blueprint checks.")
    parser.add_argument("--check", default="all", choices=["all", "safety", "sandbox-checklist", "real-order-blocker"])
    args = parser.parse_args()
    result = generate_transition_blueprint_report(args.check)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["verdict"] in {"PASS", "WARNING"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
