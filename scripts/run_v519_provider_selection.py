from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.v5_provider_selection_config import get_candidate_providers
from provider_selection.provider_selection_report import generate_provider_selection_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V5.19 provider selection checks.")
    parser.add_argument("--provider", default=None)
    parser.add_argument("--ranking", action="store_true")
    parser.add_argument("--check", default="all", choices=["all", "safety"])
    args = parser.parse_args()
    provider = args.provider or get_candidate_providers()[0]
    result = generate_provider_selection_report(provider=provider, ranking_only=args.ranking, check=args.check)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["verdict"] in {"PASS", "WARNING"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
