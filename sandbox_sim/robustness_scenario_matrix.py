from __future__ import annotations


BASE_SCENARIOS = [
    ("full_fill", [], "filled"),
    ("partial_fill", ["partial_fill_stuck"], "partial_warning"),
    ("reject", ["risk_reject"], "rejected"),
    ("cancel", ["cancel_reject"], "canceled_or_warning"),
    ("latency", ["network_latency"], "accepted_pending"),
    ("disconnect", ["broker_disconnect"], "rejected_warning"),
    ("insufficient_cash", ["risk_reject"], "rejected"),
    ("invalid_symbol", ["risk_reject"], "rejected"),
    ("risk_rejected", ["risk_reject"], "rejected"),
]
COMBINED_SCENARIOS = [
    ("latency_partial_fill", ["network_latency", "partial_fill_stuck"], "warning"),
    ("latency_cancel_reject", ["network_latency", "cancel_reject"], "warning"),
    ("disconnect_missing_fill_report", ["broker_disconnect", "missing_fill_report"], "warning"),
    ("duplicate_order_ack_partial_fill", ["duplicate_order_ack", "partial_fill_stuck"], "warning"),
    ("risk_reject_audit_delay", ["risk_reject", "audit_delay"], "warning"),
    ("stale_market_price_cancel", ["stale_market_price", "cancel_reject"], "warning"),
    ("partial_fill_stuck_manual_reject", ["partial_fill_stuck", "manual_reject"], "warning"),
]


def build_robustness_scenario_matrix() -> dict:
    scenarios = [_scenario(name, "base", faults, outcome) for name, faults, outcome in BASE_SCENARIOS]
    scenarios.extend(_scenario(name, "combined", faults, outcome) for name, faults, outcome in COMBINED_SCENARIOS)
    return {"scenarios": scenarios, "simulation_only": True, "broker_connected": False, "real_order_submitted": False}


def list_scenarios() -> list[dict]:
    return build_robustness_scenario_matrix()["scenarios"]


def get_scenario_by_name(name: str) -> dict:
    for scenario in list_scenarios():
        if scenario["name"] == name:
            return scenario
    return _scenario(name, "unknown", [], "warning")


def _scenario(name: str, category: str, faults: list[str], expected_outcome: str) -> dict:
    return {
        "name": name,
        "category": category,
        "faults": faults,
        "expected_outcome": expected_outcome,
        "simulation_only": True,
        "real_order_submitted": False,
        "broker_connected": False,
        "real_money_enabled": False,
    }
