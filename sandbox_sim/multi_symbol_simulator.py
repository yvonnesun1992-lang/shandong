from __future__ import annotations

import random

from config.v5_sandbox_robustness_config import DEFAULT_SYMBOLS
from sandbox_sim.sandbox_simulation_broker import SandboxSimulationBroker


def build_symbol_ticks(symbols: list[str] | None = None, ticks: int = 100, seed: int = 42) -> list[dict]:
    selected = symbols or DEFAULT_SYMBOLS
    rng = random.Random(seed)
    output = []
    for index in range(max(0, ticks)):
        symbol = selected[index % len(selected)]
        output.append({"symbol": symbol, "price": round(100 + rng.random() * 10 + index * 0.01, 4), "timestamp": f"T{index:05d}"})
    return output


def run_multi_symbol_simulation(symbols: list[str] | None = None, scenario: str = "full_fill", ticks: int = 100, seed: int = 42) -> dict:
    selected = symbols or DEFAULT_SYMBOLS
    broker = SandboxSimulationBroker(scenario=_base_scenario(scenario))
    ticks_payload = build_symbol_ticks(selected, ticks, seed)
    submitted = set()
    for symbol in selected:
        broker.submit_order({"symbol": symbol, "side": "BUY", "quantity": 10, "order_type": "MARKET"})
        submitted.add(symbol)
    for tick in ticks_payload:
        broker.step_market(tick)
    orders = broker.get_recent_orders()
    fills = broker.get_recent_fills()
    return {
        "symbols": selected,
        "ticks_processed": ticks,
        "orders": orders,
        "fills": fills,
        "orders_by_symbol": {symbol: sum(1 for order in orders if order["symbol"] == symbol) for symbol in selected},
        "fills_by_symbol": {symbol: sum(1 for fill in fills if fill["symbol"] == symbol) for symbol in selected},
        "rejects_by_symbol": {symbol: sum(1 for order in orders if order["symbol"] == symbol and order["status"] == "REJECTED") for symbol in selected},
        "cancels_by_symbol": {symbol: sum(1 for order in orders if order["symbol"] == symbol and order["status"] == "CANCELED") for symbol in selected},
        "lifecycle_by_symbol": {symbol: [order["status"] for order in orders if order["symbol"] == symbol] for symbol in selected},
        "equity_contribution": {symbol: broker.get_account()["equity"] / max(len(selected), 1) for symbol in selected},
        "account": broker.get_account(),
        "audit_summary": {"events": len(broker.audit), "simulation_only": True},
        "simulation_only": True,
        "broker_connected": False,
        "real_order_submitted": False,
        "real_money_enabled": False,
        "real_orders_enabled": False,
        "paper_trading": True,
    }


def summarize_multi_symbol_result(result: dict) -> dict:
    return {
        "symbols": result.get("symbols", []),
        "total_orders": sum(result.get("orders_by_symbol", {}).values()),
        "total_fills": sum(result.get("fills_by_symbol", {}).values()),
        "total_rejects": sum(result.get("rejects_by_symbol", {}).values()),
        "total_cancels": sum(result.get("cancels_by_symbol", {}).values()),
        "simulation_only": True,
    }


def _base_scenario(scenario: str) -> str:
    mapping = {
        "latency_partial_fill": "partial_fill",
        "disconnect_missing_fill_report": "disconnect",
        "partial_fill_stuck_manual_reject": "partial_fill",
        "risk_reject_audit_delay": "risk_rejected",
        "stale_market_price_cancel": "cancel",
    }
    return mapping.get(scenario, scenario)
