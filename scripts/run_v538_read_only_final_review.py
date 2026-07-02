from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.v5_read_only_final_review_config import get_read_only_final_review_provider, get_read_only_final_review_status
from sandbox_read_only_final_review.evidence_review_matrix import build_evidence_review_matrix
from sandbox_read_only_final_review.final_review_decision import build_final_review_decision
from sandbox_read_only_final_review.final_review_orchestrator import build_read_only_final_review, summarize_read_only_final_review
from sandbox_read_only_final_review.final_review_safety_validator import build_final_review_safety_summary
from sandbox_read_only_final_review.missing_requirement_register import build_missing_requirement_register
from sandbox_read_only_final_review.risk_acceptance_matrix import build_risk_acceptance_matrix
from sandbox_read_only_final_review.sandbox_read_only_final_review_report import generate_sandbox_read_only_final_review_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V5.38 read-only final review checks.")
    parser.add_argument("--provider", default=None)
    parser.add_argument("--check", choices=["all", "evidence", "risks", "missing", "decision", "safety"], default="all")
    args = parser.parse_args()
    provider = args.provider or get_read_only_final_review_provider()

    if args.check == "evidence":
        payload = {**build_evidence_review_matrix(provider), "verdict": "WARNING"}
    elif args.check == "risks":
        payload = {**build_risk_acceptance_matrix(provider), "verdict": "WARNING"}
    elif args.check == "missing":
        payload = {**build_missing_requirement_register(provider), "verdict": "WARNING"}
    elif args.check == "decision":
        payload = {**build_final_review_decision(provider), "verdict": "WARNING"}
    elif args.check == "safety":
        payload = {**build_final_review_safety_summary(), "provider": provider, "verdict": "WARNING"}
    else:
        report = generate_sandbox_read_only_final_review_report(provider=provider, check=args.check)
        payload = {
            **report,
            "status": get_read_only_final_review_status(),
            "summary": summarize_read_only_final_review(build_read_only_final_review(provider)),
        }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload.get("verdict") in {"PASS", "WARNING"} else 1


if __name__ == "__main__":
    sys.exit(main())
