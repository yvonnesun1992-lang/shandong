from __future__ import annotations


def boundary() -> dict:
    return {
        "version": "V5.42",
        "local_run_doctor_only": True,
        "localhost_only": True,
        "doctor_runtime_enabled": False,
        "auto_fix_enabled": False,
        "install_dependencies_enabled": False,
        "external_network_enabled": False,
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
    }
