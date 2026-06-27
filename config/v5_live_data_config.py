from __future__ import annotations

import os


VALID_LIVE_DATA_MODES = {"disabled", "mock_live", "yfinance_polling", "provider_planned"}
VALID_LIVE_DATA_PROVIDERS = {"mock", "yfinance", "provider_planned"}


def get_live_data_mode() -> str:
    mode = os.getenv("SHANDONG_V5_LIVE_DATA_MODE", "mock_live").strip().lower()
    if mode not in VALID_LIVE_DATA_MODES:
        return "mock_live"
    return "mock_live" if mode == "provider_planned" else mode


def get_live_data_provider() -> str:
    provider = os.getenv("SHANDONG_V5_LIVE_DATA_PROVIDER", "mock").strip().lower()
    if provider not in VALID_LIVE_DATA_PROVIDERS:
        return "mock"
    return "mock" if provider == "provider_planned" else provider


def get_live_data_symbols() -> list[str]:
    raw = os.getenv("SHANDONG_V5_LIVE_DATA_SYMBOLS", "AAPL,MSFT,NVDA,SPY,QQQ")
    symbols = [item.strip().upper() for item in raw.split(",") if item.strip()]
    return symbols or ["AAPL", "MSFT", "NVDA", "SPY", "QQQ"]


def get_live_data_poll_interval() -> int:
    try:
        value = int(float(os.getenv("SHANDONG_V5_LIVE_DATA_POLL_INTERVAL_SECONDS", "60")))
    except ValueError:
        return 60
    return max(1, min(value, 3600))


def get_live_data_status() -> dict:
    mode = get_live_data_mode()
    provider = get_live_data_provider()
    if mode == "yfinance_polling":
        provider = "yfinance"
    if mode in {"mock_live", "disabled"}:
        provider = "mock"
    return {
        "version": "V5.6",
        "live_data_mode": mode,
        "live_data_provider": provider,
        "symbols": get_live_data_symbols(),
        "poll_interval_seconds": get_live_data_poll_interval(),
        "live_market_data": mode != "disabled",
        "paper_trading": True,
        "real_trading": False,
        "broker_connected": False,
        "real_money_enabled": False,
        "production_live_trading": False,
    }
