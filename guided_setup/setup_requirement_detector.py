from __future__ import annotations

from guided_setup.init import boundary
from local_run_doctor.backend_diagnosis import summarize_backend_diagnosis
from local_run_doctor.command_availability_doctor import run_command_availability_doctor
from local_run_doctor.frontend_diagnosis import summarize_frontend_diagnosis
from local_run_doctor.port_diagnosis import diagnose_default_ports


def _blocker(detected: dict) -> str:
    if not detected["node_available"]:
        return "Node.js is not installed or not available in PATH"
    if not detected["npm_available"]:
        return "npm is not available"
    if not detected["pnpm_available"]:
        return "pnpm is not installed"
    if not detected["frontend_node_modules_exists"]:
        return "frontend dependencies are not installed"
    if not detected["frontend_port_3000_open"]:
        return "frontend dev server is not running"
    if not detected["backend_port_8000_open"] and detected["backend_code_valid_placeholder"]:
        return "backend code is valid but backend process is not running"
    return "local setup appears ready"


def detect_setup_requirements() -> dict:
    commands = run_command_availability_doctor()
    ports = diagnose_default_ports()
    backend = summarize_backend_diagnosis()
    frontend = summarize_frontend_diagnosis()
    detected = {
        "python_available": commands["python_available"],
        "node_available": commands["node_available"],
        "npm_available": commands["npm_available"],
        "pnpm_available": commands["pnpm_available"],
        "frontend_node_modules_exists": frontend["node_modules_exists"],
        "backend_code_valid_placeholder": backend["backend_ready"],
        "frontend_files_present_placeholder": frontend["frontend_ready"],
        "product_home_present_placeholder": frontend["home_page_productized"],
        "frontend_port_3000_open": ports["frontend_port_open"],
        "backend_port_8000_open": ports["backend_port_open"],
    }
    missing = [key for key, value in detected.items() if value is False]
    setup_ready = not missing
    return {
        "setup_ready": setup_ready,
        "missing_requirements": missing,
        "detected_requirements": detected,
        "likely_blocker": _blocker(detected),
        **boundary(),
    }


def summarize_setup_requirements(result: dict) -> dict:
    return {
        "setup_ready": result.get("setup_ready", False),
        "missing_requirements": result.get("missing_requirements", []),
        "likely_blocker": result.get("likely_blocker", ""),
        **boundary(),
    }
