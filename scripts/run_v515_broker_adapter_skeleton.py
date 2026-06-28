from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from broker_adapter.adapter_registry import build_default_registry
from broker_adapter.broker_adapter_report import generate_broker_adapter_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V5.15 broker adapter skeleton checks.")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--test", default="mock")
    args = parser.parse_args()

    if args.list:
        registry = build_default_registry()
        result = generate_broker_adapter_report("mock")
        result["adapters"] = registry.list_adapters()
    else:
        result = generate_broker_adapter_report(args.test)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["verdict"] in {"PASS", "WARNING"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
