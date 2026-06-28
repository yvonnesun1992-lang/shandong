from __future__ import annotations

from broker_adapter.adapter_factory import create_broker_adapter
from sandbox_bridge.sanitizer import bridge_boundary, sanitize_bridge_payload


def select_backend(request: dict | None = None) -> dict:
    request = request or {}
    preferred = str(request.get("preferred") or request.get("backend") or "bridge")
    backend = preferred if preferred in {"mock", "bridge", "ibkr_skeleton", "alpaca_skeleton", "futu_skeleton", "tiger_skeleton", "schwab_skeleton"} else "bridge"
    return {"backend": backend, **bridge_boundary()}


def route_request(request: dict) -> dict:
    clean = sanitize_bridge_payload(request)
    backend = select_backend(clean)["backend"]
    if backend == "mock":
        adapter = create_broker_adapter("mock")
        response = adapter.submit_order(
            {
                "client_order_id": clean.get("client_order_id", "bridge-client"),
                "idempotency_key": clean.get("idempotency_key", "bridge-idem"),
                "symbol": clean.get("symbol", "AAPL"),
                "side": clean.get("side", "BUY"),
                "quantity": clean.get("quantity", 1),
                "order_type": "MARKET",
                "created_at": "bridge-simulated",
            }
        )
        return {"backend": "mock", "response": response, **bridge_boundary()}
    if backend.endswith("_skeleton"):
        adapter = create_broker_adapter(backend)
        response = adapter.submit_order(clean)
        return {"backend": backend, **response, **bridge_boundary()}
    return {"backend": "bridge", "status": "bridge_simulated_route", **bridge_boundary()}
