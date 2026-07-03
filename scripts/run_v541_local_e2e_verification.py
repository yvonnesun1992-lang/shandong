from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.v5_local_e2e_config import get_local_e2e_status
from local_e2e_verification.api_smoke_test_matrix import run_api_smoke_tests, summarize_api_smoke_tests
from local_e2e_verification.backend_smoke_test import run_backend_smoke_test, summarize_backend_smoke_test
from local_e2e_verification.frontend_smoke_test import summarize_frontend_smoke_test, verify_frontend_files
from local_e2e_verification.local_e2e_orchestrator import run_local_e2e_verification, summarize_local_e2e_verification
from local_e2e_verification.local_launcher_verification import (
    summarize_local_launcher_verification,
    verify_local_launcher_plan,
    verify_local_launcher_scripts,
)
from local_e2e_verification.log_write_verification import summarize_log_verification, verify_log_read, verify_log_write
from local_e2e_verification.report_generation_verification import generate_local_e2e_verification_report, summarize_report_generation
from local_e2e_verification.safety_boundary_verification import build_local_e2e_safety_summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V5.41 local e2e verification.")
    parser.add_argument("--check", choices=["launcher", "backend", "frontend", "api", "logs", "report", "safety", "status"])
    args = parser.parse_args()
    if args.check == "launcher":
        payload = summarize_local_launcher_verification({"plan": verify_local_launcher_plan(), "scripts": verify_local_launcher_scripts()})
    elif args.check == "backend":
        payload = summarize_backend_smoke_test(run_backend_smoke_test())
    elif args.check == "frontend":
        payload = summarize_frontend_smoke_test(verify_frontend_files())
    elif args.check == "api":
        payload = summarize_api_smoke_tests(run_api_smoke_tests())
    elif args.check == "logs":
        payload = summarize_log_verification({"write": verify_log_write(), "read": verify_log_read()})
    elif args.check == "report":
        payload = summarize_report_generation(generate_local_e2e_verification_report())
    elif args.check == "safety":
        payload = build_local_e2e_safety_summary()
    elif args.check == "status":
        payload = get_local_e2e_status()
    else:
        payload = summarize_local_e2e_verification(run_local_e2e_verification())
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
    return 1 if payload.get("verdict") == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
