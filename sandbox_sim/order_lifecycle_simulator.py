from __future__ import annotations

from sandbox_sim.simulated_sandbox_order import SimulatedSandboxOrder


BLOCKED_REAL_STATES = {"LIVE_SUBMITTED", "REAL_ORDER_READY", "BROKER_ACCEPTED_REAL"}
ALLOWED_TRANSITIONS = {
    "NEW": {"ACCEPTED", "REJECTED", "EXPIRED"},
    "ACCEPTED": {"PARTIALLY_FILLED", "FILLED", "CANCELED", "EXPIRED"},
    "PARTIALLY_FILLED": {"FILLED", "CANCELED", "EXPIRED"},
    "FILLED": set(),
    "REJECTED": set(),
    "CANCELED": set(),
    "EXPIRED": set(),
}


class OrderLifecycleSimulator:
    def transition(self, order: SimulatedSandboxOrder, target_status: str, reason: str = "") -> dict:
        target = target_status.upper()
        if target in BLOCKED_REAL_STATES:
            return {"accepted": False, "reason": "real broker state blocked", "simulation_only": True}
        if target not in ALLOWED_TRANSITIONS.get(order.status, set()):
            return {"accepted": False, "reason": f"illegal transition {order.status}->{target}", "simulation_only": True}
        order.set_status(target, reason)
        return {"accepted": True, "status": order.status, "simulation_only": True}
