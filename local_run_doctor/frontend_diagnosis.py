from __future__ import annotations

import json
from pathlib import Path

from local_run_doctor.init import boundary


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_ROOT = PROJECT_ROOT / "web" / "frontend"


def diagnose_frontend_files() -> dict:
    home = FRONTEND_ROOT / "app" / "page.tsx"
    api_client = FRONTEND_ROOT / "app" / "lib" / "apiClient.ts"
    text = home.read_text(encoding="utf-8") if home.exists() else ""
    return {
        "home_page_exists": home.exists(),
        "api_client_exists": api_client.exists(),
        "home_page_productized": "Shandong Quant System" in text,
        "warnings": [] if home.exists() else ["home page missing"],
        "errors": [],
        **boundary(),
    }


def diagnose_frontend_package_json() -> dict:
    package = FRONTEND_ROOT / "package.json"
    valid = False
    if package.exists():
        try:
            data = json.loads(package.read_text(encoding="utf-8"))
            valid = bool(data.get("scripts", {}).get("dev"))
        except json.JSONDecodeError:
            valid = False
    return {
        "package_json_exists": package.exists(),
        "package_json_valid": valid,
        "pnpm_lock_exists": (FRONTEND_ROOT / "pnpm-lock.yaml").exists(),
        "warnings": [] if package.exists() else ["frontend package.json missing"],
        "errors": [],
        **boundary(),
    }


def diagnose_frontend_node_modules() -> dict:
    exists = (FRONTEND_ROOT / "node_modules").exists()
    return {"node_modules_exists": exists, "warnings": [] if exists else ["frontend dependencies are not installed"], "errors": [], **boundary()}


def build_frontend_install_command() -> str:
    return "cd web/frontend && pnpm install"


def build_frontend_start_command() -> str:
    return "cd web/frontend && pnpm dev --hostname 127.0.0.1 --port 3000"


def summarize_frontend_diagnosis() -> dict:
    files = diagnose_frontend_files()
    package = diagnose_frontend_package_json()
    modules = diagnose_frontend_node_modules()
    ready = files["home_page_exists"] and files["api_client_exists"] and files["home_page_productized"] and package["package_json_exists"]
    warnings = files.get("warnings", []) + package.get("warnings", []) + modules.get("warnings", [])
    return {
        "frontend_ready": ready,
        "package_json_exists": package["package_json_exists"],
        "home_page_exists": files["home_page_exists"],
        "home_page_productized": files["home_page_productized"],
        "node_modules_exists": modules["node_modules_exists"],
        "pnpm_lock_exists": package["pnpm_lock_exists"],
        "frontend_install_command": build_frontend_install_command(),
        "frontend_start_command": build_frontend_start_command(),
        "warnings": warnings,
        "errors": [],
        **boundary(),
    }
