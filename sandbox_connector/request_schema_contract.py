from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from sandbox_connector.idempotency_policy import generate_idempotency_key


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


@dataclass
class SubmitOrderRequest:
    client_order_id: str
    idempotency_key: str
    symbol: str
    side: str
    quantity: int
    order_type: str = "MARKET"
    limit_price: float | None = None
    time_in_force: str = "DAY"
    approved_simulated_id: str = "planned_approval"
    risk_check_id: str = "planned_risk_check"
    paper_order_ref: str = "planned_paper_order"
    created_at: str = field(default_factory=_now)

    @classmethod
    def create(cls, symbol: str, side: str, quantity: int) -> "SubmitOrderRequest":
        created_at = _now()
        payload = {"client_order_id": f"client-{symbol.lower()}-{created_at[:10]}", "action": "submit", "created_at": created_at}
        return cls(
            client_order_id=payload["client_order_id"],
            idempotency_key=generate_idempotency_key(payload),
            symbol=symbol.upper(),
            side=side.upper(),
            quantity=int(quantity),
            created_at=created_at,
        )

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def build_request_schema_contract() -> dict:
    return {
        "submit_order_request": list(SubmitOrderRequest.create("AAPL", "BUY", 1).to_dict().keys()),
        "cancel_order_request": ["client_order_id", "idempotency_key", "reason", "created_at"],
        "order_status_request": ["client_order_id", "idempotency_key", "created_at"],
        "contract_only": True,
    }


def validate_submit_order_request(payload: dict) -> dict:
    required = {"client_order_id", "idempotency_key", "symbol", "side", "quantity", "order_type", "created_at"}
    errors = [f"missing {field}" for field in sorted(required - set(payload))]
    if int(payload.get("quantity", 0) or 0) <= 0:
        errors.append("quantity must be positive")
    return {"valid": not errors, "errors": errors, "contract_only": True}


def sanitize_request(payload: dict) -> dict:
    return {key: ("[redacted]" if _blocked(value) else value) for key, value in payload.items() if key not in {"account_id", "broker_order_id"}}


def _blocked(value: object) -> bool:
    text = str(value).lower()
    return any(term in text for term in ["secret=", "token=", "password=", "api_key=", "authorization:"])
