from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.v5_provider_fault_injection_config import get_fault_injection_provider
from provider_fault_injection.fault_recovery_validator import validate_all_fault_recovery
from provider_fault_injection.fault_replay_runner import run_fault_scenario
from provider_fault_injection.fault_safety_validator import build_fault_safety_summary
from provider_fault_injection.provider_fault_injection_report import generate_provider_fault_injection_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate V5.24 provider fault injection summary.")
    parser.add_argument("--provider", default=get_fault_injection_provider())
    parser.add_argument("--scenario", default=None)
    parser.add_argument("--check", default="all", choices=["all", "safety", "recovery"])
    args = parser.parse_args()

    if args.check == "safety":
        check_result = build_fault_safety_summary()
    elif args.check == "recovery":
        check_result = validate_all_fault_recovery(args.provider)
    elif args.scenario:
        check_result = run_fault_scenario(args.provider, args.scenario)
    else:
        check_result = None

    report = generate_provider_fault_injection_report(provider=args.provider, scenario=args.scenario, check=args.check)
    if check_result is not None:
        report["check_result"] = check_result
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if report["verdict"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
