from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.v5_pre_sandbox_approval_config import get_pre_sandbox_approval_provider, get_pre_sandbox_approval_status
from pre_sandbox_approval.approval_gate_evaluator import build_approval_gate_summary
from pre_sandbox_approval.approval_safety_validator import build_approval_safety_summary
from pre_sandbox_approval.evidence_requirement_validator import validate_evidence_requirements
from pre_sandbox_approval.pre_sandbox_approval_report import generate_pre_sandbox_approval_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V5.28 pre-sandbox operator approval gate review.")
    parser.add_argument("--provider", default=None)
    parser.add_argument("--check", choices=["all", "evidence", "gate", "safety"], default="all")
    args = parser.parse_args()

    provider = args.provider or get_pre_sandbox_approval_provider()
    if args.check == "evidence":
        payload = {"verdict": "WARNING", **validate_evidence_requirements(provider)}
    elif args.check == "gate":
        payload = {"verdict": "WARNING", **build_approval_gate_summary(provider)}
    elif args.check == "safety":
        payload = {"verdict": "WARNING", **build_approval_safety_summary()}
    else:
        payload = generate_pre_sandbox_approval_report(provider=provider, check=args.check)
    payload["status"] = get_pre_sandbox_approval_status()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
