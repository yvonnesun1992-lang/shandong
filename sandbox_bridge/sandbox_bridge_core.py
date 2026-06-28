from __future__ import annotations

from sandbox_bridge.request_transformer import transform_submit_order
from sandbox_bridge.response_normalizer import normalize_order_response
from sandbox_bridge.sanitizer import bridge_boundary, sanitize_bridge_payload


class SandboxBridgeCore:
    def __init__(self) -> None:
        self.state = "DISCONNECTED"

    def connect(self) -> dict:
        self.state = "CONNECTED_SIMULATED"
        return {"state": self.state, "simulated_connection": True, **bridge_boundary()}

    def disconnect(self) -> dict:
        self.state = "DISCONNECTED"
        return {"state": self.state, **bridge_boundary()}

    def is_connected(self) -> bool:
        return False

    def send_request(self, request: dict) -> dict:
        transformed = self.transform_request(request)
        return {"sent": False, "transformed": transformed, **bridge_boundary()}

    def receive_response(self, response: dict) -> dict:
        return self.transform_response(response)

    def transform_request(self, request: dict | None = None) -> dict:
        clean = sanitize_bridge_payload(request or {})
        return transform_submit_order(clean)

    def transform_response(self, response: dict | None = None) -> dict:
        clean = sanitize_bridge_payload(response or {})
        return normalize_order_response(clean)

    def status(self) -> dict:
        return {"state": self.state, "connected": False, **bridge_boundary()}
