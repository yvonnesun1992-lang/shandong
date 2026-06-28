from __future__ import annotations


def build_order_response(client_order_id: str = "planned_client_order") -> dict:
    return {
        "client_order_id": client_order_id,
        "provider_order_ref": "planned_ref",
        "status": "CONTRACT_ONLY",
        "accepted_at": None,
        "filled_quantity": 0,
        "avg_fill_price": 0.0,
        "reason": "connector runtime disabled",
        "raw_response_available": False,
        "sanitized": True,
    }


def build_account_response() -> dict:
    return {"provider": "none", "account_mode": "contract_only", "buying_power": 0, "cash": 0, "equity": 0, "positions_count": 0, "sanitized": True}


def build_position_response(symbol: str = "AAPL") -> dict:
    return {"symbol": symbol, "quantity": 0, "avg_price": 0, "market_value": 0, "unrealized_pnl": 0, "sanitized": True}


def build_response_schema_contract() -> dict:
    return {
        "order_response": build_order_response(),
        "account_response": build_account_response(),
        "position_response": build_position_response(),
        "contract_only": True,
    }


def sanitize_response(payload: dict) -> dict:
    clean = {}
    for key, value in payload.items():
        if key == "raw_provider_response":
            continue
        clean[key] = "[redacted]" if _blocked(value) else value
    clean["sanitized"] = True
    return clean


def validate_response_contract(payload: dict) -> dict:
    errors = []
    if payload.get("provider_order_ref") != "planned_ref":
        errors.append("provider_order_ref must be planned_ref")
    if payload.get("raw_response_available") is not False:
        errors.append("raw response must not be available")
    return {"valid": not errors, "errors": errors, "contract_only": True}


def _blocked(value: object) -> bool:
    text = str(value).lower()
    return any(term in text for term in ["secret=", "token=", "password=", "api_key=", "authorization:"])
