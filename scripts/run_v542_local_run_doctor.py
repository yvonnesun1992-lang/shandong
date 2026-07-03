from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.v5_local_run_doctor_config import get_local_run_doctor_status
from local_run_doctor.backend_diagnosis import summarize_backend_diagnosis
from local_run_doctor.browser_diagnosis import diagnose_browser_targets
from local_run_doctor.command_availability_doctor import run_command_availability_doctor
from local_run_doctor.frontend_diagnosis import summarize_frontend_diagnosis
from local_run_doctor.human_friendly_fix_guide import build_fix_guide
from local_run_doctor.local_run_doctor_orchestrator import run_local_run_doctor, summarize_local_run_doctor
from local_run_doctor.local_run_doctor_report import generate_local_run_doctor_report
from local_run_doctor.local_run_doctor_safety_validator import build_local_run_doctor_safety_summary
from local_run_doctor.port_diagnosis import diagnose_default_ports


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V5.42 local run doctor checks.")
    parser.add_argument("--check", choices=["status", "commands", "ports", "backend", "frontend", "browser", "fix-guide", "safety", "report"])
    args = parser.parse_args()
    if args.check == "status":
        payload = get_local_run_doctor_status()
    elif args.check == "commands":
        payload = run_command_availability_doctor()
    elif args.check == "ports":
        payload = diagnose_default_ports()
    elif args.check == "backend":
        payload = summarize_backend_diagnosis()
    elif args.check == "frontend":
        payload = summarize_frontend_diagnosis()
    elif args.check == "browser":
        payload = diagnose_browser_targets()
    elif args.check == "fix-guide":
        payload = build_fix_guide(run_local_run_doctor())
    elif args.check == "safety":
        payload = build_local_run_doctor_safety_summary()
    elif args.check == "report":
        payload = generate_local_run_doctor_report()
    else:
        payload = summarize_local_run_doctor(run_local_run_doctor())
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 1 if payload.get("verdict") == "FAIL" or payload.get("safe") is False else 0


if __name__ == "__main__":
    raise SystemExit(main())
