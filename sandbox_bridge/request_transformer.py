from __future__ import annotations

from sandbox_bridge.sanitizer import bridge_boundary, sanitize_bridge_payload


def transform_submit_order(request: dict) -> dict:
    clean = sanitize_bridge_payload(request)
    return {
        "request_type": "submit_order",
        "sandbox_internal_format": True,
        "symbol": str(clean.get("symbol") or "AAPL").upper(),
        "side": str(clean.get("side") or "BUY").upper(),
        "quantity": int(clean.get("quantity", 0) or 0),
        "client_order_id": str(clean.get("client_order_id") or "bridge-client-order"),
        **bridge_boundary(),
    }


def transform_cancel_order(request: dict) -> dict:
    clean = sanitize_bridge_payload(request)
    return {"request_type": "cancel_order", "sandbox_internal_format": True, "client_order_id": str(clean.get("client_order_id") or "bridge-client-order"), **bridge_boundary()}


def transform_account_request(request: dict | None = None) -> dict:
    return {"request_type": "account", "sandbox_internal_format": True, **bridge_boundary()}


def transform_position_request(request: dict | None = None) -> dict:
    clean = sanitize_bridge_payload(request or {})
    return {"request_type": "positions", "sandbox_internal_format": True, "symbol": str(clean.get("symbol") or "ALL").upper(), **bridge_boundary()}
