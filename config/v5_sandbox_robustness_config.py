from __future__ import annotations

import os


DEFAULT_SYMBOLS = ["AAPL", "MSFT", "NVDA", "SPY", "QQQ"]
DEFAULT_SCENARIOS = [
    "full_fill",
    "partial_fill",
    "reject",
    "cancel",
    "latency",
    "disconnect",
    "insufficient_cash",
    "invalid_symbol",
    "risk_rejected",
]
VALID_MODES = {"disabled", "local_robustness", "stress_robustness"}


def get_sandbox_robustness_mode() -> str:
    value = os.getenv("SHANDONG_V5_SANDBOX_ROBUSTNESS_MODE", "local_robustness").strip().lower()
    return value if value in VALID_MODES else "local_robustness"


def get_sandbox_robustness_symbols() -> list[str]:
    raw = os.getenv("SHANDONG_V5_SANDBOX_ROBUSTNESS_SYMBOLS")
    if not raw:
        return DEFAULT_SYMBOLS.copy()
    symbols = [item.strip().upper() for item in raw.split(",") if item.strip()]
    return symbols or DEFAULT_SYMBOLS.copy()


def get_sandbox_robustness_scenarios() -> list[str]:
    raw = os.getenv("SHANDONG_V5_SANDBOX_ROBUSTNESS_SCENARIOS")
    if not raw:
        return DEFAULT_SCENARIOS.copy()
    scenarios = [item.strip().lower() for item in raw.split(",") if item.strip()]
    return scenarios or DEFAULT_SCENARIOS.copy()


def get_sandbox_robustness_status() -> dict:
    mode = get_sandbox_robustness_mode()
    return {
        "version": "V5.12",
        "sandbox_robustness_mode": mode,
        "local_robustness": mode != "disabled",
        "symbols": get_sandbox_robustness_symbols(),
        "scenarios": get_sandbox_robustness_scenarios(),
        "real_sandbox_api_enabled": False,
        "real_broker_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "simulation_only": True,
    }
