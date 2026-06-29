from __future__ import annotations


def boundary() -> dict:
    return {
        "version": "V5.23",
        "offline_replay_only": True,
        "replay_runtime_enabled": False,
        "sandbox_api_enabled": False,
        "account_read_enabled": False,
        "order_submission_enabled": False,
        "broker_connected": False,
        "real_money_enabled": False,
        "paper_trading": True,
    }
