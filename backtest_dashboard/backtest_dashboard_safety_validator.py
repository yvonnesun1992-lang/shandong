from __future__ import annotations

import json

from config.v5_backtest_dashboard_config import get_backtest_dashboard_status


REQUIRED_FALSE_KEYS = [
    "real_trading_enabled",
    "broker_connected",
    "sandbox_api_enabled",
    "secret_read_enabled",
    "account_read_enabled",
    "balance_read_enabled",
    "position_read_enabled",
    "order_preview_enabled",
    "order_submission_enabled",
    "real_money_enabled",
]

BLOCKED_TERMS = [
    "alpaca_trade_api",
    "ib_insync",
    "tigeropen",
    "robin_stocks",
    "api_key=demo",
    "secret_value=demo",
    "password=demo",
    "real_account_id",
    "real_order_id",
    "raw provider payload",
    "https://",
    "http://",
]


def validate_backtest_dashboard_safety(payload: dict | list | str | None = None) -> dict:
    status = get_backtest_dashboard_status()
    findings: list[str] = []
    if status["backtest_dashboard_only"] is not True:
        findings.append("backtest_dashboard_only must remain true")
    if status["localhost_only"] is not True:
        findings.append("localhost_only must remain true")
    for key in REQUIRED_FALSE_KEYS:
        if status.get(key) is not False:
            findings.append(f"{key} must remain false")
    if payload is not None:
        text = json.dumps(payload, ensure_ascii=False, default=str).lower() if not isinstance(payload, str) else payload.lower()
        for term in BLOCKED_TERMS:
            if term in text and "127.0.0.1" not in text and "localhost" not in text:
                findings.append(f"blocked term detected: {term}")
                break
        for key in REQUIRED_FALSE_KEYS:
            if f'"{key}": true' in text:
                findings.append(f"{key} unexpectedly true")
    return {
        "safe": not findings,
        "findings": findings,
        "backtest_dashboard_only": True,
        "localhost_only": True,
        **{key: False for key in REQUIRED_FALSE_KEYS},
        "paper_trading": True,
    }


def build_backtest_dashboard_safety_summary() -> dict:
    return validate_backtest_dashboard_safety(get_backtest_dashboard_status())
