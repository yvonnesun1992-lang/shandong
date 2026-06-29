from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.v5_provider_offline_replay_config import get_offline_replay_provider
from provider_offline_replay.provider_offline_replay_report import generate_provider_offline_replay_report
from provider_offline_replay.replay_consistency_validator import validate_all_replay_consistency
from provider_offline_replay.replay_runner import run_replay_scenario
from provider_offline_replay.replay_safety_validator import build_replay_safety_summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate V5.23 provider offline replay summary.")
    parser.add_argument("--provider", default=get_offline_replay_provider())
    parser.add_argument("--scenario", default=None)
    parser.add_argument("--check", default="all", choices=["all", "safety", "consistency"])
    args = parser.parse_args()

    if args.check == "safety":
        check_result = build_replay_safety_summary()
    elif args.check == "consistency":
        check_result = validate_all_replay_consistency(args.provider)
    elif args.scenario:
        check_result = run_replay_scenario(args.provider, args.scenario)
    else:
        check_result = None

    report = generate_provider_offline_replay_report(provider=args.provider, scenario=args.scenario, check=args.check)
    if check_result is not None:
        report["check_result"] = check_result
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if report["verdict"] == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
