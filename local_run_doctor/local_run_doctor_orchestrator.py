from __future__ import annotations

from local_run_doctor.backend_diagnosis import summarize_backend_diagnosis
from local_run_doctor.browser_diagnosis import diagnose_browser_targets
from local_run_doctor.command_availability_doctor import run_command_availability_doctor
from local_run_doctor.frontend_diagnosis import summarize_frontend_diagnosis
from local_run_doctor.human_friendly_fix_guide import build_fix_guide
from local_run_doctor.init import boundary
from local_run_doctor.local_run_doctor_safety_validator import validate_local_run_doctor_safety
from local_run_doctor.port_diagnosis import diagnose_default_ports


def _likely_reason(commands: dict, ports: dict, frontend: dict, backend: dict) -> str:
    if not commands.get("node_available", False):
        return "Node.js is not available, so frontend cannot start"
    if not commands.get("pnpm_available", False):
        return "pnpm is not available, so frontend dependencies cannot run"
    if not frontend.get("node_modules_exists", False):
        return "frontend dependencies are not installed"
    if not ports.get("frontend_port_open", False):
        return "frontend dev server is not running on port 3000"
    if not ports.get("backend_port_open", False) and backend.get("backend_ready", False):
        return "backend code is valid but server is not running as a process"
    return "local run targets look reachable"


def run_local_run_doctor() -> dict:
    commands = run_command_availability_doctor()
    ports = diagnose_default_ports()
    backend = summarize_backend_diagnosis()
    frontend = summarize_frontend_diagnosis()
    browser = diagnose_browser_targets()
    base = {
        "local_run_ready": bool(backend["backend_ready"] and frontend["frontend_ready"] and ports["frontend_port_open"]),
        "likely_reason_3000_not_open": _likely_reason(commands, ports, frontend, backend),
        "python_available": commands["python_available"],
        "node_available": commands["node_available"],
        "pnpm_available": commands["pnpm_available"],
        "backend_ready": backend["backend_ready"],
        "frontend_ready": frontend["frontend_ready"],
        "frontend_node_modules_exists": frontend["node_modules_exists"],
        "frontend_port_open": ports["frontend_port_open"],
        "backend_port_open": ports["backend_port_open"],
        "commands": commands,
        "ports": ports,
        "backend": backend,
        "frontend": frontend,
        "browser": browser,
        "warnings": commands.get("warnings", []) + ports.get("suggestions", []) + frontend.get("warnings", []),
        "errors": backend.get("errors", []) + frontend.get("errors", []),
        **boundary(),
    }
    guide = build_fix_guide(base)
    base["recommended_next_steps"] = guide["recommended_next_steps"]
    base["fix_guide"] = guide
    safety = validate_local_run_doctor_safety(base)
    base["safety_validation"] = safety
    if base["errors"] or not safety["safe"]:
        base["verdict"] = "FAIL"
    elif base["warnings"] or not base["local_run_ready"]:
        base["verdict"] = "WARNING"
    else:
        base["verdict"] = "PASS"
    return base


def summarize_local_run_doctor(result: dict) -> dict:
    return {
        "local_run_ready": result.get("local_run_ready", False),
        "likely_reason_3000_not_open": result.get("likely_reason_3000_not_open", ""),
        "python_available": result.get("python_available", False),
        "node_available": result.get("node_available", False),
        "pnpm_available": result.get("pnpm_available", False),
        "backend_ready": result.get("backend_ready", False),
        "frontend_ready": result.get("frontend_ready", False),
        "frontend_port_open": result.get("frontend_port_open", False),
        "backend_port_open": result.get("backend_port_open", False),
        "recommended_next_steps": result.get("recommended_next_steps", []),
        "warnings": result.get("warnings", []),
        "errors": result.get("errors", []),
        "verdict": result.get("verdict", "FAIL"),
        **boundary(),
    }
