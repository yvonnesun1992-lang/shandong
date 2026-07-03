from __future__ import annotations

import subprocess

from config.v5_local_launcher_config import get_local_launcher_status
from local_launcher.init import boundary


def build_backend_command() -> list[str]:
    status = get_local_launcher_status()
    return [
        "python",
        "-m",
        "uvicorn",
        "src.api.v2.server:create_v2_api_app",
        "--factory",
        "--host",
        "127.0.0.1",
        "--port",
        str(status["backend_port"]),
    ]


def launch_backend(dry_run: bool = True) -> dict:
    command = build_backend_command()
    payload = {"dry_run": dry_run, "backend_command": command, "status": "dry_run" if dry_run else "started", **boundary()}
    if not dry_run:
        process = subprocess.Popen(command)
        payload["pid"] = process.pid
    return payload


def check_backend_health_placeholder() -> dict:
    return {"backend_health_check": "placeholder", "url": get_local_launcher_status()["backend_url"], **boundary()}
