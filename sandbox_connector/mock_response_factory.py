from __future__ import annotations

from datetime import UTC, datetime

from sandbox_connector.mock_connector_state_store import sanitize_mock_state


SCENARIO_TO_STATUS = {
    "accepted": "MOCK_ACCEPTED",
    "filled": "MOCK_FILLED",
    "partial_fill": "MOCK_PARTIALLY_FILLED",
    "rejected": "MOCK_REJECTED",
    "duplicate": "MOCK_DUPLICATE",
    "rate_limited": "MOCK_RATE_LIMITED",
    "cancel_accepted": "MOCK_CANCELED",
    "cancel_rejected": "MOCK_REJECTED",
    "provider_unavailable": "MOCK_REJECTED",
    "timeout": "MOCK_EXPIRED",
    "manual_approval_required": "MOCK_REJECTED",
    "kill_switch_active": "MOCK_REJECTED",
}


def build_mock_order_response(request: dict, scenario: str = "accepted") -> dict:
    scenario_name = scenario if scenario in SCENARIO_TO_STATUS else "accepted"
    quantity = int(request.get("quantity", 0) or 0)
    status = SCENARIO_TO_STATUS[scenario_name]
    filled_quantity = _filled_quantity(status, quantity)
    response = {
        "version": "V5.14",
        "scenario": scenario_name,
        "client_order_id": str(request.get("client_order_id") or "mock-client-order"),
        "provider_order_ref": f"mock_ref_{scenario_name}_{str(request.get('symbol') or 'SYMBOL').lower()}",
        "symbol": str(request.get("symbol") or "AAPL").upper(),
        "side": str(request.get("side") or "BUY").upper(),
        "quantity": quantity,
        "status": status,
        "accepted_at": _now() if status in {"MOCK_ACCEPTED", "MOCK_PARTIALLY_FILLED", "MOCK_FILLED"} else None,
        "filled_quantity": filled_quantity,
        "avg_fill_price": 100.0 if filled_quantity else 0.0,
        "reason": _scenario_reason(scenario_name),
        "raw_response_available": False,
        "sanitized": True,
        "mock_only": True,
        "real_order_submitted": False,
        "real_connector_runtime_enabled": False,
        "real_sandbox_api_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
    }
    return sanitize_mock_response(response)


def build_mock_account_response() -> dict:
    return {
        "provider": "mock",
        "account_mode": "local_mock",
        "buying_power": 100000.0,
        "cash": 100000.0,
        "equity": 100000.0,
        "positions_count": 0,
        "sanitized": True,
        "mock_only": True,
        "broker_connected": False,
        "real_money_enabled": False,
        "paper_trading": True,
    }


def build_mock_positions_response() -> dict:
    return {
        "positions": [],
        "positions_count": 0,
        "sanitized": True,
        "mock_only": True,
        "broker_connected": False,
        "real_money_enabled": False,
        "paper_trading": True,
    }


def build_mock_error_response(error_code: str, message: str | None = None) -> dict:
    return {
        "version": "V5.14",
        "error_code": str(error_code).upper(),
        "message": message or _error_message(str(error_code).upper()),
        "sanitized": True,
        "mock_only": True,
        "real_order_submitted": False,
        "real_connector_runtime_enabled": False,
        "real_sandbox_api_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
    }


def sanitize_mock_response(payload: dict) -> dict:
    clean = sanitize_mock_state(payload)
    if isinstance(clean, dict):
        clean.pop("raw_provider_response", None)
        clean["sanitized"] = True
    return clean


def _filled_quantity(status: str, quantity: int) -> int:
    if status == "MOCK_FILLED":
        return quantity
    if status == "MOCK_PARTIALLY_FILLED":
        return max(1, quantity // 2) if quantity else 0
    return 0


def _scenario_reason(scenario: str) -> str:
    return {
        "accepted": "mock accepted",
        "filled": "mock filled",
        "partial_fill": "mock partial fill",
        "rejected": "mock rejected",
        "duplicate": "mock duplicate",
        "rate_limited": "mock rate limit",
        "cancel_accepted": "mock cancel accepted",
        "cancel_rejected": "mock cancel rejected",
        "provider_unavailable": "mock provider unavailable",
        "timeout": "mock timeout",
        "manual_approval_required": "mock manual approval required",
        "kill_switch_active": "mock kill switch active",
    }.get(scenario, "mock response")


def _error_message(error_code: str) -> str:
    return {
        "RATE_LIMITED": "mock rate limit response",
        "TIMEOUT": "mock timeout response",
        "PROVIDER_UNAVAILABLE": "mock provider unavailable",
        "REJECTED": "mock rejected",
    }.get(error_code, "mock error response")


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()
