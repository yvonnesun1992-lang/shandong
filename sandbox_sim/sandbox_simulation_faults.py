from __future__ import annotations


SUPPORTED_FAULTS = {
    "broker_disconnect",
    "network_latency",
    "duplicate_order_ack",
    "missing_fill_report",
    "stale_market_price",
    "partial_fill_stuck",
    "cancel_reject",
    "risk_reject",
}


def build_sandbox_fault(fault: str, active: bool = True) -> dict:
    selected = fault if fault in SUPPORTED_FAULTS else "unknown_fault"
    return {
        "fault": selected,
        "active": bool(active),
        "simulation_only": True,
        "broker_connected": False,
        "real_order_submitted": False,
        "network_called": False,
        "external_service_called": False,
    }


def list_sandbox_faults() -> list[dict]:
    return [build_sandbox_fault(item, active=False) for item in sorted(SUPPORTED_FAULTS)]
