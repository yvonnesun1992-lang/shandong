from __future__ import annotations

from sandbox_bridge.sanitizer import bridge_boundary, sanitize_bridge_payload


def normalize_order_response(response: dict) -> dict:
    clean = sanitize_bridge_payload(response)
    return {
        "response_type": "order",
        "status": str(clean.get("status") or "bridge_simulated").upper(),
        "provider_order_ref": str(clean.get("provider_order_ref") or "bridge_simulated_ref"),
        "raw_response_available": False,
        **bridge_boundary(),
    }


def normalize_account_response(response: dict) -> dict:
    clean = sanitize_bridge_payload(response)
    return {"response_type": "account", "cash": float(clean.get("cash", 0) or 0), "equity": float(clean.get("equity", clean.get("cash", 0)) or 0), **bridge_boundary()}


def normalize_position_response(response: dict) -> dict:
    clean = sanitize_bridge_payload(response)
    return {"response_type": "positions", "positions": clean.get("positions", []), **bridge_boundary()}


def normalize_error_response(response: dict) -> dict:
    clean = sanitize_bridge_payload(response)
    return {
        "response_type": "error",
        "message": str(clean.get("message") or "bridge sanitized error"),
        "error_code": str(clean.get("error_code") or "UNKNOWN_ERROR"),
        "raw_response_available": False,
        **bridge_boundary(),
    }
