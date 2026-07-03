from __future__ import annotations

import os
from urllib.parse import urlparse


VERSION = "V5.39"
LOCAL_LAUNCHER_MODE = "local_launcher_only"
DEFAULT_BACKEND_HOST = "127.0.0.1"
DEFAULT_BACKEND_PORT = 8000
DEFAULT_FRONTEND_HOST = "127.0.0.1"
DEFAULT_FRONTEND_PORT = 3000
LOCAL_HOSTS = {"localhost", "127.0.0.1"}


def _env_bool(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name, "").strip()
    if not value:
        return default
    try:
        parsed = int(value)
    except ValueError:
        return default
    return parsed if 1 <= parsed <= 65535 else default


def _safe_host(name: str, default: str, warnings: list[str]) -> str:
    requested = os.getenv(name, "").strip().lower()
    if not requested:
        return default
    parsed = urlparse(requested)
    host = parsed.hostname or requested.split(":", 1)[0]
    if host in LOCAL_HOSTS:
        return "127.0.0.1" if host == "127.0.0.1" else "localhost"
    label = "backend" if "BACKEND" in name else "frontend"
    warnings.append(f"{label} host override requested but forced to localhost")
    return default


def get_local_launcher_mode() -> str:
    return LOCAL_LAUNCHER_MODE


def get_local_launcher_status() -> dict:
    warnings: list[str] = []
    requested_mode = os.getenv("SHANDONG_V5_LOCAL_LAUNCHER_MODE", "").strip()
    if requested_mode and requested_mode != LOCAL_LAUNCHER_MODE:
        warnings.append("local launcher mode override requested but blocked in V5.39")

    backend_host = _safe_host("SHANDONG_V5_BACKEND_HOST", DEFAULT_BACKEND_HOST, warnings)
    frontend_host = _safe_host("SHANDONG_V5_FRONTEND_HOST", DEFAULT_FRONTEND_HOST, warnings)
    backend_port = _env_int("SHANDONG_V5_BACKEND_PORT", DEFAULT_BACKEND_PORT)
    frontend_port = _env_int("SHANDONG_V5_FRONTEND_PORT", DEFAULT_FRONTEND_PORT)

    requested_flags = {
        "SHANDONG_V5_ENABLE_LOCAL_LAUNCHER_RUNTIME": "local launcher runtime requested but blocked by default in V5.39 dry-run mode",
        "SHANDONG_V5_ENABLE_SANDBOX_API": "sandbox api requested but blocked in V5.39",
        "SHANDONG_V5_ENABLE_SECRET_READ": "secret read requested but blocked in V5.39",
        "SHANDONG_V5_ENABLE_ACCOUNT_READ": "account read requested but blocked in V5.39",
        "SHANDONG_V5_ENABLE_ORDER_SUBMISSION": "order submission requested but blocked in V5.39",
        "SHANDONG_V5_ENABLE_REAL_MONEY": "real money requested but blocked in V5.39",
    }
    for env_name, message in requested_flags.items():
        if _env_bool(env_name):
            warnings.append(message)

    return {
        "version": VERSION,
        "local_launcher_mode": get_local_launcher_mode(),
        "local_launcher_only": True,
        "local_launcher_runtime_enabled": False,
        "backend_launch_allowed": True,
        "frontend_launch_allowed": True,
        "browser_open_allowed": True,
        "localhost_only": True,
        "backend_host": backend_host,
        "backend_port": backend_port,
        "frontend_host": frontend_host,
        "frontend_port": frontend_port,
        "backend_url": f"http://{backend_host}:{backend_port}",
        "frontend_url": f"http://{frontend_host}:{frontend_port}",
        "broker_connected": False,
        "sandbox_api_enabled": False,
        "secret_read_enabled": False,
        "account_read_enabled": False,
        "balance_read_enabled": False,
        "position_read_enabled": False,
        "order_preview_enabled": False,
        "order_submission_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "warnings": warnings,
    }


def get_local_backend_url() -> str:
    return get_local_launcher_status()["backend_url"]


def get_local_frontend_url() -> str:
    return get_local_launcher_status()["frontend_url"]
