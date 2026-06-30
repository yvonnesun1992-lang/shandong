from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.v5_sandbox_preflight_packet_config import get_preflight_packet_provider, get_preflight_packet_status
from sandbox_preflight_packet.artifact_manifest import build_artifact_manifest
from sandbox_preflight_packet.final_decision_record import build_final_preflight_decision
from sandbox_preflight_packet.final_preflight_checklist import build_final_preflight_checklist
from sandbox_preflight_packet.preflight_safety_validator import build_preflight_safety_summary
from sandbox_preflight_packet.sandbox_preflight_packet_report import generate_sandbox_preflight_packet_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V5.31 sandbox final preflight packet.")
    parser.add_argument("--provider", default=None)
    parser.add_argument("--check", choices=["all", "checklist", "artifacts", "decision", "safety"], default="all")
    args = parser.parse_args()

    provider = args.provider or get_preflight_packet_provider()
    if args.check == "checklist":
        payload = {"verdict": "WARNING", **build_final_preflight_checklist(provider)}
    elif args.check == "artifacts":
        payload = {"verdict": "WARNING", **build_artifact_manifest(provider)}
    elif args.check == "decision":
        payload = {"verdict": "WARNING", **build_final_preflight_decision(provider)}
    elif args.check == "safety":
        payload = {"verdict": "WARNING", **build_preflight_safety_summary()}
    else:
        payload = generate_sandbox_preflight_packet_report(provider=provider, check=args.check)
    payload["status"] = get_preflight_packet_status()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 1 if payload.get("verdict") == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
