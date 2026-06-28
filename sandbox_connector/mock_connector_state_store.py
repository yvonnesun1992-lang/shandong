from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime


BLOCKED_KEYS = {"account_id", "broker_order_id", "real_order_id", "raw_provider_response", "authorization"}
BLOCKED_MARKERS = ("secret=", "token=", "password=", "api_key=", "authorization:")


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


class MockConnectorStateStore:
    def __init__(self) -> None:
        self._orders: dict[str, dict] = {}
        self._idempotency: dict[str, dict] = {}

    def save_order(self, order: dict) -> dict:
        clean = sanitize_mock_state(order)
        order_id = str(clean.get("client_order_id") or clean.get("mock_order_id") or f"mock-order-{len(self._orders) + 1}")
        clean["client_order_id"] = order_id
        clean.setdefault("saved_at", utc_now())
        self._orders[order_id] = clean
        return deepcopy(clean)

    def get_order(self, client_order_id: str) -> dict:
        return deepcopy(self._orders.get(client_order_id, {}))

    def list_orders(self) -> list[dict]:
        return [deepcopy(item) for item in self._orders.values()]

    def save_idempotency_key(self, key: str, response: dict) -> dict:
        clean = sanitize_mock_state(response)
        self._idempotency[str(key)] = clean
        return deepcopy(clean)

    def get_idempotency_response(self, key: str) -> dict:
        return deepcopy(self._idempotency.get(str(key), {}))

    def has_idempotency_key(self, key: str) -> bool:
        return str(key) in self._idempotency


def sanitize_mock_state(payload: object) -> object:
    if isinstance(payload, dict):
        clean = {}
        for key, value in payload.items():
            if str(key).lower() in BLOCKED_KEYS:
                continue
            clean[key] = sanitize_mock_state(value)
        return clean
    if isinstance(payload, list):
        return [sanitize_mock_state(item) for item in payload]
    if isinstance(payload, str):
        lowered = payload.lower()
        if any(marker in lowered for marker in BLOCKED_MARKERS):
            return "[redacted]"
    return payload
