from __future__ import annotations

from sandbox_connector.mock_connector_state_store import MockConnectorStateStore, utc_now
from sandbox_connector.mock_response_factory import (
    build_mock_account_response,
    build_mock_error_response,
    build_mock_order_response,
    build_mock_positions_response,
    sanitize_mock_response,
)
from sandbox_connector.request_schema_contract import validate_submit_order_request


class MockSandboxConnector:
    connector_runtime_enabled = False
    mock_only = True

    def __init__(self, state_store: MockConnectorStateStore | None = None) -> None:
        self.state_store = state_store or MockConnectorStateStore()

    def get_account(self) -> dict:
        return build_mock_account_response()

    def get_positions(self) -> dict:
        return build_mock_positions_response()

    def submit_order(self, request: dict) -> dict:
        clean_request = sanitize_mock_response(request)
        validation = validate_submit_order_request(clean_request)
        if not validation["valid"]:
            response = build_mock_error_response("REJECTED", "; ".join(validation["errors"]))
            self.state_store.save_order({**clean_request, **response, "saved_at": utc_now()})
            return response
        idem_key = str(clean_request.get("idempotency_key") or "")
        if idem_key and self.state_store.has_idempotency_key(idem_key):
            duplicate = {**self.state_store.get_idempotency_response(idem_key), "status": "MOCK_DUPLICATE", "scenario": "duplicate"}
            self.state_store.save_order(duplicate)
            return duplicate
        response = build_mock_order_response(clean_request, str(clean_request.get("scenario") or "accepted"))
        self.state_store.save_order(response)
        if idem_key:
            self.state_store.save_idempotency_key(idem_key, response)
        return response

    def cancel_order(self, request: dict) -> dict:
        clean_request = sanitize_mock_response(request)
        existing = self.state_store.get_order(str(clean_request.get("client_order_id") or ""))
        scenario = "cancel_accepted" if existing else "cancel_rejected"
        response = build_mock_order_response({**existing, **clean_request, "quantity": existing.get("quantity", 0)}, scenario)
        self.state_store.save_order(response)
        return response

    def get_order_status(self, request: dict) -> dict:
        clean_request = sanitize_mock_response(request)
        order = self.state_store.get_order(str(clean_request.get("client_order_id") or ""))
        if not order:
            return build_mock_error_response("NOT_FOUND", "mock order not found")
        return sanitize_mock_response({**order, "mock_only": True, "broker_connected": False})

    def get_recent_orders(self) -> dict:
        return {
            "orders": self.state_store.list_orders(),
            "order_count": len(self.state_store.list_orders()),
            "mock_only": True,
            "broker_connected": False,
            "real_orders_enabled": False,
            "real_money_enabled": False,
            "paper_trading": True,
            "sanitized": True,
        }

    def health_check(self) -> dict:
        return {
            "status": "ok",
            "mock_only": True,
            "real_connector_runtime_enabled": False,
            "real_sandbox_api_enabled": False,
            "broker_connected": False,
            "real_orders_enabled": False,
            "real_money_enabled": False,
            "paper_trading": True,
            "sanitized": True,
        }
