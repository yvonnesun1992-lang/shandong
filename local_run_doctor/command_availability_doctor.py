from __future__ import annotations

import shutil

from local_run_doctor.init import boundary


def check_command_available(command: str) -> dict:
    available = shutil.which(command) is not None
    return {"command": command, "available": available, **boundary()}


def check_python_available() -> dict:
    return {"python_available": shutil.which("python") is not None or shutil.which("python3") is not None, **boundary()}


def check_node_available() -> dict:
    return {"node_available": shutil.which("node") is not None, **boundary()}


def check_npm_available() -> dict:
    return {"npm_available": shutil.which("npm") is not None, **boundary()}


def check_pnpm_available() -> dict:
    return {"pnpm_available": shutil.which("pnpm") is not None, **boundary()}


def run_command_availability_doctor() -> dict:
    python_available = check_python_available()["python_available"]
    node_available = check_node_available()["node_available"]
    npm_available = check_npm_available()["npm_available"]
    pnpm_available = check_pnpm_available()["pnpm_available"]
    missing = []
    if not python_available:
        missing.append("python")
    if not node_available:
        missing.append("node")
    if not npm_available:
        missing.append("npm")
    if not pnpm_available:
        missing.append("pnpm")
    warnings = [f"{command} unavailable" for command in missing]
    return {
        "python_available": python_available,
        "node_available": node_available,
        "npm_available": npm_available,
        "pnpm_available": pnpm_available,
        "missing_commands": missing,
        "warnings": warnings,
        "errors": [],
        **boundary(),
    }
