from __future__ import annotations

import subprocess
from pathlib import Path

from config.v5_local_launcher_config import get_local_launcher_status
from local_launcher.init import boundary


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def build_frontend_command() -> list[str]:
    status = get_local_launcher_status()
    return ["pnpm", "dev", "--hostname", "127.0.0.1", "--port", str(status["frontend_port"])]


def launch_frontend(dry_run: bool = True) -> dict:
    command = build_frontend_command()
    payload = {
        "dry_run": dry_run,
        "frontend_command": command,
        "working_directory": "web/frontend",
        "status": "dry_run" if dry_run else "started",
        **boundary(),
    }
    if not dry_run:
        process = subprocess.Popen(command, cwd=PROJECT_ROOT / "web/frontend")
        payload["pid"] = process.pid
    return payload


def check_frontend_health_placeholder() -> dict:
    return {"frontend_health_check": "placeholder", "url": get_local_launcher_status()["frontend_url"], **boundary()}
