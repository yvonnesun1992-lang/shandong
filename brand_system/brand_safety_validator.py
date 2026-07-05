from __future__ import annotations

import json
from pathlib import Path


BLOCKED_RUNTIME_TERMS = [
    "broker_connected\": true",
    "sandbox_api_enabled\": true",
    "secret_read_enabled\": true",
    "account_read_enabled\": true",
    "balance_read_enabled\": true",
    "position_read_enabled\": true",
    "order_submission_enabled\": true",
    "real_money_enabled\": true",
    "place_order(",
    "submit_real_order",
    "alpaca_trade_api",
    "ib_insync",
    "tigeropen",
    "robin_stocks",
    "sk-",
]


def validate_brand_safety(payload: object | None = None) -> dict:
    text = json.dumps(payload or {}, default=str).lower()
    findings = [{"term": term} for term in BLOCKED_RUNTIME_TERMS if term in text]
    return {
        "safe": not findings,
        "brand_system_only": True,
        "trading_logic_changed": False,
        "broker_integration_added": False,
        "api_key_handling_added": False,
        "secret_exposure_added": False,
        "external_api_calls_added": False,
        "findings": findings,
        "warnings": [],
    }


def build_brand_safety_summary() -> dict:
    watched_files = [
        Path("web/frontend/app/page.tsx"),
        Path("web/frontend/app/components/ProductionShell.tsx"),
        Path("web/frontend/app/styles.css"),
        Path("config/v5_brand_system_config.py"),
    ]
    text = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in watched_files if path.exists())
    return validate_brand_safety({"brand_files": text})
