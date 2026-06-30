from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.v5_provider_offline_soak_config import get_offline_soak_provider
from provider_offline_soak.provider_offline_soak_report import generate_provider_offline_soak_report
from provider_offline_soak.soak_coverage_validator import validate_soak_coverage
from provider_offline_soak.soak_runner import run_soak_scenario
from provider_offline_soak.soak_safety_validator import build_soak_safety_summary
from provider_offline_soak.stability_gate import evaluate_all_stability_gates


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate V5.25 provider offline soak summary.")
    parser.add_argument("--provider", default=get_offline_soak_provider())
    parser.add_argument("--scenario", default=None)
    parser.add_argument("--check", default="all", choices=["all", "safety", "gate", "coverage"])
    args = parser.parse_args()

    if args.check == "safety":
        check_result = build_soak_safety_summary()
    elif args.check == "gate":
        check_result = evaluate_all_stability_gates(args.provider)
    elif args.check == "coverage":
        check_result = validate_soak_coverage(args.provider)
    elif args.scenario:
        check_result = run_soak_scenario(args.provider, args.scenario)
    else:
        check_result = None

    report = generate_provider_offline_soak_report(provider=args.provider, scenario=args.scenario, check=args.check)
    if check_result is not None:
        report["check_result"] = check_result
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if report["verdict"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
