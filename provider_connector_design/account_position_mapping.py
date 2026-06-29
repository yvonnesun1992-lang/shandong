from __future__ import annotations

from provider_connector_design import boundary


def build_account_position_mapping(provider: str) -> dict:
    return {
        "provider": provider,
        "account_mapping": {
            "account_status": "account_status_placeholder",
            "cash_balance": "cash_balance_placeholder",
            "buying_power": "buying_power_placeholder",
            "margin_status": "margin_status_placeholder",
        },
        "position_mapping": {
            "position_symbol": "position_symbol_placeholder",
            "position_quantity": "position_quantity_placeholder",
            "average_cost": "average_cost_placeholder",
            "market_value": "market_value_placeholder",
            "unrealized_pnl": "unrealized_pnl_placeholder",
            "currency": "currency_placeholder",
            "timestamp": "timestamp_placeholder",
        },
        "real_account_read_enabled": False,
        "sandbox_account_read_enabled": False,
        **boundary(),
    }
