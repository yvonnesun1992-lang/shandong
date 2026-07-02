from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.v5_read_only_stability_gate_config import get_read_only_stability_gate_provider, get_read_only_stability_gate_status
from sandbox_read_only_stability_gate.audit_stability_check import check_audit_stability
from sandbox_read_only_stability_gate.fault_evidence_collector import collect_fault_evidence
from sandbox_read_only_stability_gate.order_path_stability_check import check_order_path_stability
from sandbox_read_only_stability_gate.redaction_stability_check import check_redaction_stability
from sandbox_read_only_stability_gate.replay_evidence_collector import collect_replay_evidence
from sandbox_read_only_stability_gate.sandbox_read_only_stability_gate_report import generate_sandbox_read_only_stability_gate_report
from sandbox_read_only_stability_gate.schema_stability_check import check_schema_stability
from sandbox_read_only_stability_gate.stability_gate_decision import build_stability_gate_decision
from sandbox_read_only_stability_gate.stability_gate_orchestrator import run_read_only_stability_gate, summarize_stability_gate
from sandbox_read_only_stability_gate.stability_gate_safety_validator import build_stability_gate_safety_summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V5.36 read-only stability gate checks.")
    parser.add_argument("--provider", default=None)
    parser.add_argument("--check", choices=["all", "replay", "fault", "redaction", "schema", "order-path", "decision", "safety"], default="all")
    args = parser.parse_args()
    provider = args.provider or get_read_only_stability_gate_provider()

    if args.check == "replay":
        payload = {**collect_replay_evidence(provider), "verdict": "PASS"}
    elif args.check == "fault":
        payload = {**collect_fault_evidence(provider), "verdict": "PASS"}
    elif args.check == "redaction":
        payload = {**check_redaction_stability(provider), "verdict": "PASS"}
    elif args.check == "schema":
        payload = {**check_schema_stability(provider), "verdict": "PASS"}
    elif args.check == "order-path":
        payload = {**check_order_path_stability(provider), "verdict": "PASS"}
    elif args.check == "decision":
        payload = {**build_stability_gate_decision(provider), "verdict": "WARNING"}
    elif args.check == "safety":
        payload = {**build_stability_gate_safety_summary(), "provider": provider, "verdict": "WARNING"}
    else:
        report = generate_sandbox_read_only_stability_gate_report(provider=provider, check=args.check)
        payload = {
            **report,
            "status": get_read_only_stability_gate_status(),
            "summary": summarize_stability_gate(run_read_only_stability_gate(provider)),
        }

    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload.get("verdict") in {"PASS", "WARNING"} else 1


if __name__ == "__main__":
    sys.exit(main())
