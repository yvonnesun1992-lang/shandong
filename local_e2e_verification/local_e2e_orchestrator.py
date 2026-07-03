from __future__ import annotations

from local_e2e_verification.api_smoke_test_matrix import run_api_smoke_tests
from local_e2e_verification.backend_smoke_test import run_backend_smoke_test
from local_e2e_verification.frontend_smoke_test import verify_frontend_files
from local_e2e_verification.init import boundary
from local_e2e_verification.local_launcher_verification import (
    summarize_local_launcher_verification,
    verify_local_launcher_plan,
    verify_local_launcher_scripts,
)
from local_e2e_verification.log_write_verification import summarize_log_verification, verify_log_read, verify_log_write
from local_e2e_verification.report_generation_verification import generate_local_e2e_verification_report
from local_e2e_verification.safety_boundary_verification import build_local_e2e_safety_summary, verify_local_e2e_safety


def run_local_e2e_verification() -> dict:
    launcher = summarize_local_launcher_verification({"plan": verify_local_launcher_plan(), "scripts": verify_local_launcher_scripts()})
    backend = run_backend_smoke_test()
    frontend = verify_frontend_files()
    api = run_api_smoke_tests()
    log_summary = summarize_log_verification({"write": verify_log_write(), "read": verify_log_read()})
    report = generate_local_e2e_verification_report()
    safety = build_local_e2e_safety_summary()
    payload = {
        "local_e2e_ready": all([
            launcher["local_launcher_verified"],
            backend["backend_smoke_passed"],
            frontend["frontend_smoke_passed"],
            api["api_smoke_passed"],
            log_summary["log_write_passed"],
            report["report_generated"],
            safety["safe"],
        ]),
        "launcher_verified": launcher["local_launcher_verified"],
        "backend_smoke_passed": backend["backend_smoke_passed"],
        "frontend_smoke_passed": frontend["frontend_smoke_passed"],
        "api_smoke_passed": api["api_smoke_passed"],
        "log_write_passed": log_summary["log_write_passed"],
        "report_generated": report["report_generated"],
        "safety_passed": safety["safe"],
        "launcher": launcher,
        "backend": backend,
        "frontend": frontend,
        "api": api,
        "logs": log_summary,
        "report": report,
        "safety": safety,
        "warnings": launcher.get("warnings", []) + backend.get("warnings", []) + frontend.get("warnings", []) + api.get("warnings", []) + log_summary.get("warnings", []),
        "errors": launcher.get("errors", []) + backend.get("errors", []) + frontend.get("errors", []) + api.get("errors", []) + log_summary.get("errors", []),
        **boundary(),
    }
    final_safety = verify_local_e2e_safety(payload)
    payload["safety_validation"] = final_safety
    if payload["errors"] or not final_safety["safe"]:
        payload["verdict"] = "FAIL"
    elif payload["warnings"]:
        payload["verdict"] = "WARNING"
    else:
        payload["verdict"] = "PASS"
    return payload


def summarize_local_e2e_verification(result: dict) -> dict:
    return {
        "local_e2e_ready": result.get("local_e2e_ready", False),
        "launcher_verified": result.get("launcher_verified", False),
        "backend_smoke_passed": result.get("backend_smoke_passed", False),
        "frontend_smoke_passed": result.get("frontend_smoke_passed", False),
        "api_smoke_passed": result.get("api_smoke_passed", False),
        "log_write_passed": result.get("log_write_passed", False),
        "report_generated": result.get("report_generated", False),
        "safety_passed": result.get("safety_passed", False),
        "warnings": result.get("warnings", []),
        "errors": result.get("errors", []),
        "verdict": result.get("verdict", "FAIL"),
        **boundary(),
    }
