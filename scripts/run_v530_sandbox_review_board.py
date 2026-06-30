from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.v5_sandbox_review_board_config import get_review_board_provider, get_review_board_status
from sandbox_review_board.evidence_review_matrix import build_evidence_review_matrix
from sandbox_review_board.go_no_go_decision_record import build_go_no_go_decision
from sandbox_review_board.review_board_safety_validator import build_review_board_safety_summary
from sandbox_review_board.risk_acceptance_matrix import build_risk_acceptance_matrix
from sandbox_review_board.sandbox_review_board_report import generate_sandbox_review_board_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V5.30 sandbox readiness review board packet.")
    parser.add_argument("--provider", default=None)
    parser.add_argument("--check", choices=["all", "evidence", "risks", "decision", "safety"], default="all")
    args = parser.parse_args()

    provider = args.provider or get_review_board_provider()
    if args.check == "evidence":
        payload = {"verdict": "WARNING", **build_evidence_review_matrix(provider)}
    elif args.check == "risks":
        payload = {"verdict": "WARNING", **build_risk_acceptance_matrix(provider)}
    elif args.check == "decision":
        payload = {"verdict": "WARNING", **build_go_no_go_decision(provider)}
    elif args.check == "safety":
        payload = {"verdict": "WARNING", **build_review_board_safety_summary()}
    else:
        payload = generate_sandbox_review_board_report(provider=provider, check=args.check)
    payload["status"] = get_review_board_status()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 1 if payload.get("verdict") == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
