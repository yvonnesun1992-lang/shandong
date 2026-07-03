from __future__ import annotations

from local_launcher.backend_launcher import build_backend_command, launch_backend
from local_launcher.browser_opener import build_browser_open_target, open_browser
from local_launcher.environment_checker import run_environment_check
from local_launcher.frontend_launcher import build_frontend_command, launch_frontend
from local_launcher.init import boundary
from local_launcher.launcher_log_manager import build_launcher_log_event, write_launcher_log
from local_launcher.local_launcher_safety_validator import validate_local_launcher_safety
from local_launcher.port_checker import check_launcher_ports


def build_local_launcher_plan() -> dict:
    environment = run_environment_check()
    ports = check_launcher_ports()
    plan = {
        "launcher_plan_ready": environment["environment_ready"],
        "dry_run": True,
        "environment": environment,
        "ports": ports,
        "backend_command": build_backend_command(),
        "frontend_command": build_frontend_command(),
        "browser_target": build_browser_open_target(),
        "errors": environment.get("errors", []),
        "warnings": environment.get("warnings", []) + ports.get("warnings", []),
        **boundary(),
    }
    safety = validate_local_launcher_safety(plan)
    plan["safety"] = safety
    plan["verdict"] = "FAIL" if plan["errors"] or not safety["safe"] else "WARNING" if plan["warnings"] else "PASS"
    return plan


def run_local_launcher(dry_run: bool = True) -> dict:
    plan = build_local_launcher_plan()
    result = {
        **plan,
        "dry_run": dry_run,
        "backend": launch_backend(dry_run=dry_run),
        "frontend": launch_frontend(dry_run=dry_run),
        "browser": open_browser(dry_run=dry_run),
    }
    safety = validate_local_launcher_safety(result)
    result["safety"] = safety
    result["verdict"] = "FAIL" if result["errors"] or not safety["safe"] else "WARNING" if result["warnings"] else "PASS"
    write_launcher_log(build_launcher_log_event("local_launcher", result["verdict"], {"dry_run": dry_run, "verdict": result["verdict"]}))
    return result


def summarize_local_launcher_result(result: dict) -> dict:
    return {
        "verdict": result.get("verdict", "FAIL"),
        "dry_run": result.get("dry_run", True),
        "launcher_plan_ready": result.get("launcher_plan_ready", False),
        "backend_command": result.get("backend_command", []),
        "frontend_command": result.get("frontend_command", []),
        "browser_target": result.get("browser_target", ""),
        "warnings": result.get("warnings", []),
        "errors": result.get("errors", []),
        **boundary(),
    }
