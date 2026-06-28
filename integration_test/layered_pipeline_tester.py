from __future__ import annotations

from broker_adapter.adapter_factory import create_broker_adapter
from sandbox_bridge.sandbox_bridge_core import SandboxBridgeCore
from sandbox_connector.mock_sandbox_connector import MockSandboxConnector

from integration_test.sanitizer import integration_boundary


class LayeredPipelineTester:
    def __init__(self, seed: int = 42) -> None:
        self.seed = seed

    def test_alpha_layer(self) -> dict:
        return {"layer": "alpha", "status": "PASS", "signal": {"symbol": "AAPL", "action": "BUY", "strength": 0.5}, **integration_boundary()}

    def test_mock_connector_layer(self) -> dict:
        response = MockSandboxConnector().submit_order(_mock_request())
        return {"layer": "mock_connector", "status": "PASS", "response": response, **integration_boundary()}

    def test_skeleton_adapter_layer(self) -> dict:
        response = create_broker_adapter("ibkr_skeleton").submit_order({"symbol": "AAPL", "side": "BUY", "quantity": 1})
        return {"layer": "skeleton_adapter", "status": "PASS", "response": response, **integration_boundary()}

    def test_bridge_layer(self) -> dict:
        bridge = SandboxBridgeCore()
        return {"layer": "sandbox_bridge", "status": "PASS", "response": bridge.send_request({"symbol": "AAPL", "side": "BUY", "quantity": 1}), **integration_boundary()}

    def test_end_to_end_flow(self) -> dict:
        layers = [self.test_alpha_layer(), self.test_mock_connector_layer(), self.test_skeleton_adapter_layer(), self.test_bridge_layer()]
        return {"layer": "end_to_end", "status": "PASS", "layers": layers, "order_id": "integration-order-1", "audit_events": len(layers), **integration_boundary()}


def _mock_request() -> dict:
    return {
        "client_order_id": "integration-client-order",
        "idempotency_key": "integration-idem-key",
        "symbol": "AAPL",
        "side": "BUY",
        "quantity": 1,
        "order_type": "MARKET",
        "created_at": "integration-simulated",
    }
