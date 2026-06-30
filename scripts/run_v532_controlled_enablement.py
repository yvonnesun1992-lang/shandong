from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.v5_controlled_enablement_config import get_controlled_enablement_provider, get_controlled_enablement_status
from sandbox_controlled_enablement.controlled_enablement_conditions import build_controlled_enablement_conditions
from sandbox_controlled_enablement.controlled_enablement_decision_record import build_controlled_enablement_decision
from sandbox_controlled_enablement.controlled_enablement_orchestrator import (
    build_controlled_enablement_blueprint,
    summarize_controlled_enablement_blueprint,
)
from sandbox_controlled_enablement.controlled_enablement_safety_validator import build_controlled_enablement_safety_summary
from sandbox_controlled_enablement.feature_flag_dependency_graph import build_feature_flag_dependency_graph
from sandbox_controlled_enablement.sandbox_controlled_enablement_report import generate_sandbox_controlled_enablement_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V5.32 controlled enablement blueprint checks.")
    parser.add_argument("--provider", default=None)
    parser.add_argument("--check", choices=["all", "conditions", "feature-flags", "decision", "safety"], default="all")
    args = parser.parse_args()
    provider = args.provider or get_controlled_enablement_provider()

    if args.check == "conditions":
        payload = {**build_controlled_enablement_conditions(provider), "verdict": "WARNING"}
    elif args.check == "feature-flags":
        payload = {**build_feature_flag_dependency_graph(provider), "verdict": "WARNING"}
    elif args.check == "decision":
        payload = {**build_controlled_enablement_decision(provider), "verdict": "WARNING"}
    elif args.check == "safety":
        payload = {**build_controlled_enablement_safety_summary(), "provider": provider, "verdict": "WARNING"}
    else:
        report = generate_sandbox_controlled_enablement_report(provider=provider, check=args.check)
        payload = {
            **report,
            "status": get_controlled_enablement_status(),
            "summary": summarize_controlled_enablement_blueprint(build_controlled_enablement_blueprint(provider)),
        }

    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload.get("verdict") in {"PASS", "WARNING"} else 1


if __name__ == "__main__":
    sys.exit(main())
