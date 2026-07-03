from __future__ import annotations

from local_run_doctor.init import boundary


def build_mac_fix_guide(diagnosis: dict) -> list[str]:
    return [
        "Mac fix guide",
        "1. Install Node.js LTS if Node is missing.",
        "2. Reopen Terminal after installing Node.js.",
        "3. Go to the shandong project folder.",
        "4. Run python scripts/run_v541_local_e2e_verification.py.",
        "5. Run python scripts/run_v539_local_launcher.py --run.",
        "6. Open http://127.0.0.1:3000.",
    ]


def build_windows_fix_guide(diagnosis: dict) -> list[str]:
    return [
        "Windows fix guide",
        "1. Install Node.js LTS if Node is missing.",
        "2. Reopen PowerShell after installing Node.js.",
        "3. Go to the shandong project folder.",
        "4. Run python scripts/run_v541_local_e2e_verification.py.",
        "5. Run python scripts/run_v539_local_launcher.py --run.",
        "6. Open http://127.0.0.1:3000.",
    ]


def build_fix_guide(diagnosis: dict) -> dict:
    steps = []
    if not diagnosis.get("node_available", True):
        steps.append("Install Node.js LTS, then reopen your terminal.")
    if not diagnosis.get("pnpm_available", True):
        steps.append("Run npm install -g pnpm after Node.js is available.")
    if not diagnosis.get("frontend_node_modules_exists", True):
        steps.append("Run cd web/frontend && pnpm install.")
    if not diagnosis.get("frontend_port_open", False):
        steps.append("Run cd web/frontend && pnpm dev --hostname 127.0.0.1 --port 3000.")
    if not diagnosis.get("backend_port_open", False):
        steps.append("Run python -m uvicorn src.api.v2.server:create_v2_api_app --factory --host 127.0.0.1 --port 8000.")
    steps.append("Open http://127.0.0.1:3000 after both local servers are running.")
    return {
        "recommended_next_steps": steps,
        "mac_fix_guide": build_mac_fix_guide(diagnosis),
        "windows_fix_guide": build_windows_fix_guide(diagnosis),
        **boundary(),
    }
