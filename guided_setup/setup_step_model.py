from __future__ import annotations

from guided_setup.init import boundary


def _step(step_id: str, title: str, description: str, why_needed: str, mac_command: str = "", windows_command: str = "") -> dict:
    return {
        "step_id": step_id,
        "title": title,
        "description": description,
        "mac_command": mac_command,
        "windows_command": windows_command,
        "user_action_required": True,
        "auto_run_allowed": False,
        "status": "pending",
        "why_needed": why_needed,
    }


def build_setup_steps() -> list[dict]:
    return [
        _step("open_terminal", "Open terminal", "Open Terminal on Mac or PowerShell on Windows.", "Commands must be run by the user."),
        _step("enter_project", "Enter project directory", "Go to the shandong project folder.", "The commands need the project files.", "cd path/to/shandong", r"cd path\to\shandong"),
        _step("check_python", "Check Python", "Confirm Python can run local scripts.", "Python runs the backend and doctor scripts.", "python --version", "python --version"),
        _step("install_node", "Install Node.js LTS manually", "Install Node.js LTS if Node is missing.", "Node.js runs the frontend web app."),
        _step("reopen_terminal", "Reopen terminal", "Close and reopen your terminal after installing Node.js.", "New tools need a refreshed PATH."),
        _step("check_node_npm", "Check Node and npm", "Confirm Node and npm are available.", "npm is included with Node.js.", "node -v && npm -v", "node -v; npm -v"),
        _step("install_pnpm", "Install pnpm manually", "Install pnpm using npm.", "pnpm installs and runs frontend dependencies.", "npm install -g pnpm", "npm install -g pnpm"),
        _step("install_frontend", "Install frontend dependencies", "Install frontend packages.", "The frontend cannot start without dependencies.", "cd web/frontend && pnpm install", r"cd web\frontend; pnpm install"),
        _step("start_backend", "Start backend", "Start the local API server.", "The frontend calls local backend APIs.", "python -m uvicorn src.api.v2.server:create_v2_api_app --factory --host 127.0.0.1 --port 8000", "python -m uvicorn src.api.v2.server:create_v2_api_app --factory --host 127.0.0.1 --port 8000"),
        _step("start_frontend", "Start frontend", "Start the local web server.", "This serves http://127.0.0.1:3000.", "cd web/frontend && pnpm dev --hostname 127.0.0.1 --port 3000", r"cd web\frontend; pnpm dev --hostname 127.0.0.1 --port 3000"),
        _step("open_browser", "Open browser", "Open the product home page.", "This is the page the user wants to see.", "open http://127.0.0.1:3000", "start http://127.0.0.1:3000"),
        _step("verify_product_home", "Verify Product Home Dashboard", "Confirm the Shandong Quant System home page loads.", "This proves the local setup is running."),
    ]


def build_mac_setup_steps() -> list[dict]:
    return [{**step, "platform": "mac"} for step in build_setup_steps()]


def build_windows_setup_steps() -> list[dict]:
    return [{**step, "platform": "windows"} for step in build_setup_steps()]


def mark_setup_steps_status(requirements: dict) -> dict:
    detected = requirements.get("detected_requirements", {})
    steps = []
    for step in build_setup_steps():
        status = "pending"
        if step["step_id"] == "check_python" and detected.get("python_available"):
            status = "done"
        elif step["step_id"] == "install_node" and not detected.get("node_available", False):
            status = "blocked"
        elif step["step_id"] == "install_pnpm" and detected.get("node_available") and not detected.get("pnpm_available"):
            status = "blocked"
        elif step["step_id"] == "install_frontend" and not detected.get("frontend_node_modules_exists", False):
            status = "warning"
        elif step["step_id"] == "start_backend" and not detected.get("backend_port_8000_open", False):
            status = "warning"
        elif step["step_id"] == "start_frontend" and not detected.get("frontend_port_3000_open", False):
            status = "warning"
        steps.append({**step, "status": status})
    return {"steps": steps, "mac_steps": build_mac_setup_steps(), "windows_steps": build_windows_setup_steps(), **boundary()}
