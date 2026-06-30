from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.v5_sandbox_readiness_evidence_config import get_evidence_provider
from provider_sandbox_evidence.evidence_safety_validator import build_evidence_safety_summary
from provider_sandbox_evidence.provider_sandbox_evidence_report import generate_sandbox_readiness_evidence_report
from provider_sandbox_evidence.readiness_gap_analyzer import analyze_readiness_gaps
from provider_sandbox_evidence.sandbox_entry_gate import evaluate_sandbox_entry_gate


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate V5.26 sandbox readiness evidence summary.")
    parser.add_argument("--provider", default=get_evidence_provider())
    parser.add_argument("--check", default="all", choices=["all", "gate", "safety", "gaps"])
    args = parser.parse_args()

    if args.check == "gate":
        check_result = evaluate_sandbox_entry_gate(args.provider)
    elif args.check == "safety":
        check_result = build_evidence_safety_summary()
    elif args.check == "gaps":
        check_result = analyze_readiness_gaps(args.provider)
    else:
        check_result = None
    report = generate_sandbox_readiness_evidence_report(provider=args.provider, check=args.check)
    if check_result is not None:
        report["check_result"] = check_result
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if report["verdict"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
