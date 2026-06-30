from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.v5_read_only_fault_injection_config import get_read_only_fault_injection_provider, get_read_only_fault_injection_status
from sandbox_read_only_fault_injection.fault_injection_orchestrator import run_read_only_fault_injection, summarize_fault_injection
from sandbox_read_only_fault_injection.fault_injection_safety_validator import build_fault_injection_safety_summary
from sandbox_read_only_fault_injection.order_path_intrusion_detector import detect_all_order_path_intrusions
from sandbox_read_only_fault_injection.redaction_failure_detector import detect_all_redaction_failures
from sandbox_read_only_fault_injection.sandbox_read_only_fault_injection_report import generate_sandbox_read_only_fault_injection_report
from sandbox_read_only_fault_injection.stale_snapshot_detector import detect_all_stale_snapshots


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V5.35 read-only fault injection checks.")
    parser.add_argument("--provider", default=None)
    parser.add_argument("--check", choices=["all", "redaction", "stale", "order-intrusion", "safety"], default="all")
    args = parser.parse_args()
    provider = args.provider or get_read_only_fault_injection_provider()

    if args.check == "redaction":
        payload = {**detect_all_redaction_failures(provider), "verdict": "WARNING"}
    elif args.check == "stale":
        payload = {**detect_all_stale_snapshots(provider), "verdict": "WARNING"}
    elif args.check == "order-intrusion":
        payload = {**detect_all_order_path_intrusions(provider), "verdict": "WARNING"}
    elif args.check == "safety":
        payload = {**build_fault_injection_safety_summary(), "provider": provider, "verdict": "WARNING"}
    else:
        report = generate_sandbox_read_only_fault_injection_report(provider=provider, check=args.check)
        payload = {
            **report,
            "status": get_read_only_fault_injection_status(),
            "summary": summarize_fault_injection(run_read_only_fault_injection(provider)),
        }

    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload.get("verdict") in {"PASS", "WARNING"} else 1


if __name__ == "__main__":
    sys.exit(main())
