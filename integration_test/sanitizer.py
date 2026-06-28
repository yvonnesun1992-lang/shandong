from __future__ import annotations

BLOCKED_KEYS = {"account_id", "broker_order_id", "real_order_id", "raw_provider_response", "authorization"}
BLOCKED_MARKERS = ("secret=", "token=", "password=", "api_key=", "authorization:")


def integration_boundary() -> dict:
    return {
        "integration_only": True,
        "simulation_only": True,
        "broker_connected": False,
        "real_orders_enabled": False,
        "network_call_attempted": False,
        "paper_trading": True,
        "sanitized": True,
    }


def sanitize_integration_payload(payload: object) -> object:
    if isinstance(payload, dict):
        clean = {}
        for key, value in payload.items():
            if str(key).lower() in BLOCKED_KEYS:
                continue
            clean[key] = sanitize_integration_payload(value)
        return clean
    if isinstance(payload, list):
        return [sanitize_integration_payload(item) for item in payload]
    if isinstance(payload, str):
        lowered = payload.lower()
        if any(marker in lowered for marker in BLOCKED_MARKERS):
            return "[redacted]"
    return payload
