from __future__ import annotations

from typing import Any


def build_order_mapping_plan() -> dict[str, Any]:
    return {
        "mapping_ready": False,
        "planned_fields": [
            "symbol",
            "side",
            "quantity",
            "order_type",
            "limit_price",
            "time_in_force",
            "client_order_reference",
        ],
        "symbol_mapping": "paper symbol maps to future broker symbol after allowlist validation",
        "side_mapping": {"BUY": "future broker buy side", "SELL": "future broker sell side"},
        "quantity_mapping": "paper quantity maps only after position and notional checks",
        "order_type_mapping": {"MARKET": "planned market order", "LIMIT": "planned limit order"},
        "time_in_force_planned": ["DAY", "GTC planned after manual approval"],
        "market_order_planned": True,
        "limit_order_planned": True,
        "unsupported_fields": [
            "broker_account_reference",
            "broker_route",
            "margin_instruction",
            "short_locate",
            "live_execution_destination",
        ],
        "rejected_by_default": True,
        "real_broker_order": None,
        "real_order_generated": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "warnings": [
            "mapping is documentation only",
            "all future broker order conversion remains rejected by default",
        ],
    }


def map_paper_order_to_broker_plan(order: dict[str, Any]) -> dict[str, Any]:
    plan = build_order_mapping_plan()
    plan["paper_order_preview"] = {
        "symbol": str(order.get("symbol", "")),
        "side": str(order.get("side", order.get("action", ""))).upper(),
        "quantity": order.get("quantity"),
        "order_type": str(order.get("order_type", "MARKET")).upper(),
    }
    plan["warnings"] = [*plan["warnings"], "paper order preview was not converted into a broker order"]
    return plan
