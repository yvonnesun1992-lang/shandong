from __future__ import annotations

from sandbox_sim.sandbox_simulation_broker import SUPPORTED_SCENARIOS, SandboxSimulationBroker
from sandbox_sim.sandbox_simulation_faults import build_sandbox_fault


def build_sandbox_simulation_engine(scenario: str = "full_fill") -> SandboxSimulationBroker:
    return SandboxSimulationBroker(scenario=scenario)


def run_sandbox_simulation_once(scenario: str = "full_fill", tick: dict | None = None) -> dict:
    broker = build_sandbox_simulation_engine(scenario)
    tick_payload = tick or {"symbol": "AAPL", "price": 100.0, "timestamp": "2026-01-01T09:31:00Z"}
    order = broker.submit_order({"symbol": tick_payload["symbol"], "side": "BUY", "quantity": 10, "order_type": "MARKET"})
    broker.step_market(tick_payload)
    return _build_result(broker, scenario, ticks_processed=1, approval_requests=1, signals_generated=1, fault=None, first_order=order)


def run_sandbox_simulation_session(scenario: str = "full_fill", max_ticks: int = 100) -> dict:
    selected = scenario if scenario in SUPPORTED_SCENARIOS else "full_fill"
    broker = build_sandbox_simulation_engine(selected)
    ticks = max(0, int(max_ticks))
    signals = 0
    approvals = 0
    first_order: dict | None = None
    for index in range(ticks):
        tick = {"symbol": "AAPL", "price": 100.0 + index * 0.1, "timestamp": f"2026-01-01T09:{30 + index:02d}:00Z"}
        if index == 0:
            first_order = broker.submit_order({"symbol": "AAPL", "side": "BUY", "quantity": 10, "order_type": "MARKET"})
            signals += 1
            approvals += 1
        broker.step_market(tick)
    fault = build_sandbox_fault("broker_disconnect") if selected == "disconnect" else None
    return _build_result(broker, selected, ticks_processed=ticks, approval_requests=approvals, signals_generated=signals, fault=fault, first_order=first_order)


def _build_result(
    broker: SandboxSimulationBroker,
    scenario: str,
    ticks_processed: int,
    approval_requests: int,
    signals_generated: int,
    fault: dict | None,
    first_order: dict | None,
) -> dict:
    orders = broker.get_recent_orders()
    fills = broker.get_recent_fills()
    rejects = [order for order in orders if order["status"] == "REJECTED"]
    cancels = [order for order in orders if order["status"] == "CANCELED"]
    account = broker.get_account()
    warnings = []
    if scenario in {"latency", "disconnect", "partial_fill", "reject"}:
        warnings.append(f"simulated {scenario} scenario")
    return {
        "success": True,
        "scenario": scenario,
        "ticks_processed": ticks_processed,
        "signals_generated": signals_generated,
        "approval_requests": approval_requests,
        "simulated_orders": len(orders),
        "simulated_fills": len(fills),
        "simulated_rejects": len(rejects),
        "simulated_cancels": len(cancels),
        "final_equity": account["equity"],
        "account": account,
        "positions": broker.get_positions(),
        "orders": orders,
        "fills": fills,
        "first_order": first_order,
        "fault": fault,
        "audit_summary": {"events": len(broker.audit), "simulation_only": True},
        "simulation_only": True,
        "real_sandbox_api_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_order_submitted": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "warnings": warnings,
        "errors": [],
    }
