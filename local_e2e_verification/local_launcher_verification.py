from __future__ import annotations

from pathlib import Path

from local_launcher.local_launcher_orchestrator import build_local_launcher_plan
from local_e2e_verification.init import boundary


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def verify_local_launcher_plan() -> dict:
    plan = build_local_launcher_plan()
    checks = [
        {"name": "plan generated", "ok": bool(plan)},
        {"name": "backend command localhost", "ok": "127.0.0.1" in " ".join(plan.get("backend_command", []))},
        {"name": "frontend command localhost", "ok": "127.0.0.1" in " ".join(plan.get("frontend_command", []))},
        {"name": "browser target local", "ok": "127.0.0.1" in plan.get("browser_target", "") or "localhost" in plan.get("browser_target", "")},
        {"name": "dry_run default", "ok": plan.get("dry_run") is True},
    ]
    errors = [item["name"] for item in checks if not item["ok"]]
    return {"local_launcher_verified": not errors, "checks": checks, "warnings": plan.get("warnings", []), "errors": errors, "plan": plan, **boundary()}


def verify_local_launcher_scripts() -> dict:
    scripts = [
        "scripts/run_v539_local_launcher.py",
        "scripts/start_shandong_mac.command",
        "scripts/start_shandong_windows.bat",
    ]
    checks = [{"path": path, "ok": (PROJECT_ROOT / path).exists()} for path in scripts]
    errors = [item["path"] for item in checks if not item["ok"]]
    return {"local_launcher_scripts_verified": not errors, "checks": checks, "warnings": [], "errors": errors, **boundary()}


def summarize_local_launcher_verification(result: dict) -> dict:
    plan = result.get("plan", {})
    scripts = result.get("scripts", {})
    errors = plan.get("errors", []) + scripts.get("errors", [])
    warnings = plan.get("warnings", []) + scripts.get("warnings", [])
    return {"local_launcher_verified": not errors, "warnings": warnings, "errors": errors, **boundary()}
