from __future__ import annotations

from sandbox_sim.order_lifecycle_simulator import OrderLifecycleSimulator
from sandbox_sim.simulated_sandbox_account import SimulatedSandboxAccount
from sandbox_sim.simulated_sandbox_order import SimulatedSandboxFill, SimulatedSandboxOrder


SUPPORTED_SCENARIOS = [
    "full_fill",
    "partial_fill",
    "reject",
    "cancel",
    "latency",
    "disconnect",
    "insufficient_cash",
    "invalid_symbol",
    "risk_rejected",
]


class SandboxSimulationBroker:
    def __init__(self, scenario: str = "full_fill", account: SimulatedSandboxAccount | None = None) -> None:
        self.scenario = scenario if scenario in SUPPORTED_SCENARIOS else "full_fill"
        self.account = account or SimulatedSandboxAccount()
        self.lifecycle = OrderLifecycleSimulator()
        self.orders: dict[str, SimulatedSandboxOrder] = {}
        self.fills: list[SimulatedSandboxFill] = []
        self.audit: list[dict] = []

    def get_account(self) -> dict:
        return self.account.get_account_snapshot()

    def get_positions(self) -> list[dict]:
        return self.account.get_positions_snapshot()

    def submit_order(self, order_intent: dict) -> dict:
        symbol = str(order_intent.get("symbol", "")).upper()
        side = str(order_intent.get("side", "BUY")).upper()
        quantity = int(order_intent.get("quantity", 0) or 0)
        order = SimulatedSandboxOrder.create(symbol=symbol, side=side, quantity=quantity, order_type=str(order_intent.get("order_type", "MARKET")))
        if not symbol or quantity <= 0 or self.scenario in {"invalid_symbol", "risk_rejected"}:
            order.set_status("REJECTED", self.scenario)
        self.orders[order.sandbox_order_id] = order
        self.audit.append({"event": "simulated_order_created", "sandbox_order_id": order.sandbox_order_id, "simulation_only": True})
        payload = order.to_dict()
        payload.update({"real_order_submitted": False, "broker_connected": False, "real_money_enabled": False})
        return payload

    def cancel_order(self, sandbox_order_id: str) -> dict:
        order = self.orders[sandbox_order_id]
        if order.status in {"FILLED", "REJECTED", "CANCELED"}:
            return {**order.to_dict(), "cancel_accepted": False}
        self.lifecycle.transition(order, "ACCEPTED") if order.status == "NEW" else None
        self.lifecycle.transition(order, "CANCELED", "simulated cancel")
        self.audit.append({"event": "simulated_cancel", "sandbox_order_id": sandbox_order_id, "simulation_only": True})
        return {**order.to_dict(), "cancel_accepted": True}

    def get_order_status(self, sandbox_order_id: str) -> dict:
        return self.orders[sandbox_order_id].to_dict()

    def step_market(self, tick: dict) -> dict:
        symbol = str(tick.get("symbol", "AAPL")).upper()
        price = float(tick.get("price", 100.0) or 100.0)
        self.account.update_market_price(symbol, price)
        processed = 0
        for order in list(self.orders.values()):
            if order.status != "NEW" or order.symbol != symbol:
                continue
            processed += 1
            self._process_order(order, price)
        return {"processed_orders": processed, "simulation_only": True, "broker_connected": False, "real_order_submitted": False}

    def get_recent_orders(self) -> list[dict]:
        return [order.to_dict() for order in self.orders.values()]

    def get_recent_fills(self) -> list[dict]:
        return [fill.to_dict() for fill in self.fills]

    def _process_order(self, order: SimulatedSandboxOrder, price: float) -> None:
        if self.scenario == "disconnect":
            order.set_status("REJECTED", "simulated disconnect")
            return
        if self.scenario == "reject":
            order.set_status("REJECTED", "simulated reject")
            return
        if self.scenario == "insufficient_cash" and order.side == "BUY":
            order.set_status("REJECTED", "simulated insufficient cash")
            return
        self.lifecycle.transition(order, "ACCEPTED")
        if self.scenario == "latency":
            return
        if self.scenario == "cancel":
            self.lifecycle.transition(order, "CANCELED", "simulated cancel scenario")
            return
        fill_qty = max(1, order.quantity // 2) if self.scenario == "partial_fill" else order.quantity
        fill = SimulatedSandboxFill.create(order.sandbox_order_id, order.symbol, order.side, fill_qty, price, commission=round(price * fill_qty * 0.001, 6))
        self.fills.append(fill)
        self.account.apply_fill(fill)
        if self.scenario == "partial_fill" and fill_qty < order.quantity:
            self.lifecycle.transition(order, "PARTIALLY_FILLED")
        else:
            self.lifecycle.transition(order, "FILLED")
        self.audit.append({"event": "simulated_fill", "sandbox_order_id": order.sandbox_order_id, "quantity": fill_qty, "simulation_only": True})
