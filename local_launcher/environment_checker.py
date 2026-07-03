from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from local_launcher.init import boundary


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def check_python_environment() -> dict:
    version = ".".join(str(part) for part in sys.version_info[:3])
    return {"name": "python", "ok": True, "version": version}


def _tool_version(command: list[str]) -> tuple[bool, str]:
    executable = shutil.which(command[0])
    if not executable:
        return False, "not found"
    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True, timeout=5)
    except Exception:
        return False, "unavailable"
    output = (completed.stdout or completed.stderr).strip().splitlines()
    return completed.returncode == 0, output[0] if output else "available"


def check_node_environment() -> dict:
    ok, version = _tool_version(["node", "--version"])
    return {"name": "node", "ok": ok, "version": version}


def check_pnpm_environment() -> dict:
    ok, version = _tool_version(["pnpm", "--version"])
    return {"name": "pnpm", "ok": ok, "version": version}


def check_project_paths(root: Path | None = None) -> dict:
    base = root or PROJECT_ROOT
    expected = [
        "src/api/v2/server.py",
        "web/frontend/package.json",
        "web/frontend/app",
        "scripts",
    ]
    checks = [{"path": item, "ok": (base / item).exists()} for item in expected]
    return {"name": "project_paths", "ok": all(item["ok"] for item in checks), "checks": checks}


def run_environment_check() -> dict:
    checks = [
        check_python_environment(),
        check_node_environment(),
        check_pnpm_environment(),
        check_project_paths(),
    ]
    warnings = [f"{check['name']} unavailable" for check in checks if check["name"] in {"node", "pnpm"} and not check["ok"]]
    errors = [f"{item['path']} missing" for check in checks if check["name"] == "project_paths" for item in check["checks"] if not item["ok"]]
    return {
        "environment_ready": not errors,
        "checks": checks,
        "warnings": warnings,
        "errors": errors,
        **boundary(),
    }
