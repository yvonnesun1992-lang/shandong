from __future__ import annotations

from guided_setup.init import boundary


def build_mac_command_blocks() -> list[dict]:
    return [
        {"title": "Mac setup commands", "commands": ["cd path/to/shandong", "python scripts/run_v542_local_run_doctor.py", "node -v", "npm -v", "npm install -g pnpm", "cd web/frontend", "pnpm install", "pnpm dev --hostname 127.0.0.1 --port 3000"], "auto_run_allowed": False},
        {"title": "Mac backend terminal", "commands": ["python -m uvicorn src.api.v2.server:create_v2_api_app --factory --host 127.0.0.1 --port 8000"], "auto_run_allowed": False},
    ]


def build_windows_command_blocks() -> list[dict]:
    return [
        {"title": "Windows setup commands", "commands": [r"cd path\to\shandong", r"python scripts\run_v542_local_run_doctor.py", "node -v", "npm -v", "npm install -g pnpm", r"cd web\frontend", "pnpm install", "pnpm dev --hostname 127.0.0.1 --port 3000"], "auto_run_allowed": False},
        {"title": "Windows backend PowerShell", "commands": ["python -m uvicorn src.api.v2.server:create_v2_api_app --factory --host 127.0.0.1 --port 8000"], "auto_run_allowed": False},
    ]


def build_command_copy_blocks() -> dict:
    blocks = build_mac_command_blocks() + build_windows_command_blocks()
    return {"command_blocks": blocks, "mac_command_blocks": build_mac_command_blocks(), "windows_command_blocks": build_windows_command_blocks(), **boundary()}
