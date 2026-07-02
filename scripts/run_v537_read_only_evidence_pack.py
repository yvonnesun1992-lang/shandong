from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.v5_read_only_evidence_pack_config import get_read_only_evidence_pack_provider, get_read_only_evidence_pack_status
from sandbox_read_only_evidence_pack.evidence_completeness_check import check_evidence_completeness
from sandbox_read_only_evidence_pack.evidence_pack_decision import build_evidence_pack_decision
from sandbox_read_only_evidence_pack.evidence_pack_orchestrator import build_read_only_evidence_pack, summarize_read_only_evidence_pack
from sandbox_read_only_evidence_pack.evidence_pack_safety_validator import build_evidence_pack_safety_summary
from sandbox_read_only_evidence_pack.evidence_source_collector import collect_evidence_sources
from sandbox_read_only_evidence_pack.order_blocking_evidence_pack import build_order_blocking_evidence_pack
from sandbox_read_only_evidence_pack.redaction_evidence_pack import build_redaction_evidence_pack
from sandbox_read_only_evidence_pack.sandbox_read_only_evidence_pack_report import generate_sandbox_read_only_evidence_pack_report
from sandbox_read_only_evidence_pack.schema_evidence_pack import build_schema_evidence_pack


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V5.37 read-only evidence pack checks.")
    parser.add_argument("--provider", default=None)
    parser.add_argument(
        "--check",
        choices=["all", "sources", "completeness", "redaction", "schema", "order-blocking", "decision", "safety"],
        default="all",
    )
    args = parser.parse_args()
    provider = args.provider or get_read_only_evidence_pack_provider()

    if args.check == "sources":
        payload = {**collect_evidence_sources(provider), "verdict": "PASS"}
    elif args.check == "completeness":
        payload = {**check_evidence_completeness(provider), "verdict": "WARNING"}
    elif args.check == "redaction":
        payload = {**build_redaction_evidence_pack(provider), "verdict": "PASS"}
    elif args.check == "schema":
        payload = {**build_schema_evidence_pack(provider), "verdict": "PASS"}
    elif args.check == "order-blocking":
        payload = {**build_order_blocking_evidence_pack(provider), "verdict": "PASS"}
    elif args.check == "decision":
        payload = {**build_evidence_pack_decision(provider), "verdict": "WARNING"}
    elif args.check == "safety":
        payload = {**build_evidence_pack_safety_summary(), "provider": provider, "verdict": "WARNING"}
    else:
        report = generate_sandbox_read_only_evidence_pack_report(provider=provider, check=args.check)
        payload = {
            **report,
            "status": get_read_only_evidence_pack_status(),
            "summary": summarize_read_only_evidence_pack(build_read_only_evidence_pack(provider)),
        }

    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload.get("verdict") in {"PASS", "WARNING"} else 1


if __name__ == "__main__":
    sys.exit(main())
