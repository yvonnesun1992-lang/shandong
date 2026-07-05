from __future__ import annotations


def get_product_ui_status() -> dict:
    return {
        "version": "V5.45",
        "product_ui_mode": "product_ui_only",
        "product_ui_only": True,
        "localhost_only": True,
        "ui_mode_locked": True,
        "paper_trading": True,
        "broker_connected": False,
        "sandbox_api_enabled": False,
        "secret_read_enabled": False,
        "account_read_enabled": False,
        "balance_read_enabled": False,
        "position_read_enabled": False,
        "order_submission_enabled": False,
        "real_money_enabled": False,
        "alpha_model_changed": False,
        "factor_logic_changed": False,
        "strategy_logic_changed": False,
        "warnings": [],
    }


def boundary() -> dict:
    return get_product_ui_status()

