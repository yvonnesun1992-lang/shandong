from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from provider_mock_contract.provider_mock_contract_report import generate_provider_mock_contract_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate V5.22 provider mock contract summary.")
    parser.add_argument("--provider", default=None, help="Provider to render in the mock contract tests.")
    parser.add_argument("--check", default="all", choices=["all", "safety", "schema", "state-machine"], help="Mock contract section to emphasize.")
    args = parser.parse_args()

    result = generate_provider_mock_contract_report(provider=args.provider, check=args.check)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["verdict"] in {"PASS", "WARNING"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
