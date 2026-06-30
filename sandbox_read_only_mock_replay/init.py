from __future__ import annotations


def boundary() -> dict:
    return {
        "version": "V5.34",
        "read_only_mock_replay_only": True,
        "mock_replay_runtime_enabled": False,
        "sandbox_api_enabled": False,
        "secret_read_enabled": False,
        "account_read_enabled": False,
        "position_read_enabled": False,
        "balance_read_enabled": False,
        "order_preview_enabled": False,
        "order_submission_enabled": False,
        "broker_connected": False,
        "real_money_enabled": False,
        "paper_trading": True,
    }
