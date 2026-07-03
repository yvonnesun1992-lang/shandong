from __future__ import annotations

import os


VERSION = "V5.43"
GUIDED_SETUP_MODE = "guided_setup_only"


def _env_bool(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def get_guided_setup_mode() -> str:
    return GUIDED_SETUP_MODE


def get_guided_setup_status() -> dict:
    warnings: list[str] = []
    requested_mode = os.getenv("SHANDONG_V5_GUIDED_SETUP_MODE", "").strip()
    if requested_mode and requested_mode != GUIDED_SETUP_MODE:
        warnings.append("guided setup mode override requested but blocked in V5.43")
    requested_flags = {
        "SHANDONG_V5_ENABLE_GUIDED_SETUP_RUNTIME": "guided setup runtime requested but blocked in V5.43",
        "SHANDONG_V5_ENABLE_AUTO_INSTALL": "auto install requested but blocked in V5.43",
        "SHANDONG_V5_ENABLE_EXTERNAL_NETWORK": "external network requested but blocked in V5.43",
        "SHANDONG_V5_ENABLE_SYSTEM_PATH_MODIFY": "system path modify requested but blocked in V5.43",
        "SHANDONG_V5_ENABLE_ADMIN_PERMISSION": "admin permission requested but blocked in V5.43",
        "SHANDONG_V5_ENABLE_LONG_RUNNING_PROCESS_START": "long running process start requested but blocked in V5.43",
        "SHANDONG_V5_ENABLE_SANDBOX_API": "sandbox api requested but blocked in V5.43",
        "SHANDONG_V5_ENABLE_SECRET_READ": "secret read requested but blocked in V5.43",
        "SHANDONG_V5_ENABLE_ACCOUNT_READ": "account read requested but blocked in V5.43",
        "SHANDONG_V5_ENABLE_ORDER_SUBMISSION": "order submission requested but blocked in V5.43",
        "SHANDONG_V5_ENABLE_REAL_MONEY": "real money requested but blocked in V5.43",
    }
    for env_name, message in requested_flags.items():
        if _env_bool(env_name):
            warnings.append(message)
    return {
        "version": VERSION,
        "guided_setup_mode": get_guided_setup_mode(),
        "guided_setup_only": True,
        "localhost_only": True,
        "guided_setup_runtime_enabled": False,
        "auto_install_enabled": False,
        "external_network_enabled": False,
        "system_path_modify_enabled": False,
        "admin_permission_required": False,
        "long_running_process_start_enabled": False,
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
