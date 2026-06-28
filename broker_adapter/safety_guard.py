from __future__ import annotations

import json


SENSITIVE_MARKERS = ("api_key=", "secret=", "token=", "password=", "authorization:", "oauth")


def validate_adapter_safety(adapter_name: str, config: dict | None = None) -> dict:
    config = config or {}
    text = json.dumps(config, default=str).lower()
    errors = []
    if config.get("real_connection") is True:
        errors.append("real connection blocked")
    if any(marker in text for marker in SENSITIVE_MARKERS):
        errors.append("sensitive runtime config blocked")
    if config.get("oauth_attempt") is True:
        errors.append("oauth attempt blocked")
    if adapter_name != "mock" and config.get("mode", "skeleton_only") != "skeleton_only":
        errors.append("non-mock adapters must remain skeleton only")
    return {
        "safe": not errors,
        "errors": errors,
        "blocked_real_connection": True,
        "reason": "V5.15 skeleton only stage",
        "adapter": adapter_name,
        "skeleton_only": adapter_name != "mock",
        "real_connection": False,
        "real_orders": False,
        "paper_trading": True,
    }


def build_safety_guard_status() -> dict:
    adapters = ["mock", "ibkr_skeleton", "alpaca_skeleton", "futu_skeleton", "tiger_skeleton", "schwab_skeleton"]
    checks = {name: validate_adapter_safety(name, {"mode": "skeleton_only"}) for name in adapters}
    return {
        "version": "V5.15",
        "safe": all(item["safe"] for item in checks.values()),
        "checks": checks,
        "blocked_real_connection": True,
        "reason": "V5.15 skeleton only stage",
        "skeleton_only": True,
        "real_connection": False,
        "paper_trading": True,
    }
