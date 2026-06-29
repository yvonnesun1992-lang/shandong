from __future__ import annotations


MOCK_CONTRACT_BOUNDARY = {
    "version": "V5.22",
    "mock_contract_only": True,
    "mock_contract_runtime_enabled": False,
    "sandbox_api_enabled": False,
    "account_read_enabled": False,
    "order_submission_enabled": False,
    "broker_connected": False,
    "real_money_enabled": False,
    "paper_trading": True,
}


def boundary() -> dict:
    return MOCK_CONTRACT_BOUNDARY.copy()
