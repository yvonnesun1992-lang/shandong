from __future__ import annotations

from pathlib import Path

from config.v5_local_launcher_config import get_local_frontend_url
from local_launcher.launcher_log_manager import read_recent_launcher_logs
from product_home.init import boundary


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def build_runtime_visibility_summary() -> dict:
    mac_script = PROJECT_ROOT / "scripts" / "start_shandong_mac.command"
    windows_script = PROJECT_ROOT / "scripts" / "start_shandong_windows.bat"
    logs = read_recent_launcher_logs(limit=1)
    runtime_items = [
        {"name": "backend visible", "status": "placeholder", "label": "Backend localhost check"},
        {"name": "frontend visible", "status": "placeholder", "label": "Frontend localhost check"},
        {"name": "local launcher available", "status": "ok"},
        {"name": "Mac launcher script available", "status": "ok" if mac_script.exists() else "missing"},
        {"name": "Windows launcher script available", "status": "ok" if windows_script.exists() else "missing"},
        {"name": "browser URL", "status": "ok", "value": get_local_frontend_url()},
        {"name": "last launcher log placeholder", "status": "available" if logs else "empty"},
    ]
    warnings = [item["name"] for item in runtime_items if item["status"] == "missing"]
    warnings.append("node/pnpm warning placeholder: run V5.39 launcher checks for live details")
    return {"runtime_visible": not any(item["status"] == "missing" for item in runtime_items), "runtime_items": runtime_items, "warnings": warnings, **boundary()}
