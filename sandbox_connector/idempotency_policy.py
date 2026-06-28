from __future__ import annotations

import hashlib


def generate_idempotency_key(payload: dict) -> str:
    client_order_id = str(payload.get("client_order_id", "unknown"))
    action = str(payload.get("action", "submit"))
    created_at = str(payload.get("created_at", ""))[:16]
    source = f"{client_order_id}:{action}:{created_at}"
    return "idem_" + hashlib.sha256(source.encode("utf-8")).hexdigest()[:24]


def validate_idempotency_key(key: str) -> dict:
    return {"valid": key.startswith("idem_") and len(key) >= 12, "contract_only": True}


def build_idempotency_policy() -> dict:
    return {
        "stable_fields": ["client_order_id", "action", "timestamp_bucket"],
        "duplicate_error_code": "ORDER_DUPLICATE",
        "key_contains_credentials": False,
        "key_contains_real_account": False,
        "key_contains_real_order": False,
        "contract_only": True,
    }


def detect_duplicate_request(key: str, seen_keys: set[str]) -> dict:
    duplicate = key in seen_keys
    return {"duplicate_detected": duplicate, "error_code": "ORDER_DUPLICATE" if duplicate else None, "contract_only": True}
