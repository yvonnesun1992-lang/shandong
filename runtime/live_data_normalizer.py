from __future__ import annotations

from datetime import UTC, datetime
from math import isfinite
from typing import Any


REQUIRED_FIELDS = ("datetime", "symbol", "open", "high", "low", "close", "volume", "source")


def normalize_live_ticks(ticks: list[dict]) -> dict:
    valid_ticks = []
    invalid_ticks = []
    for tick in ticks or []:
        normalized, reason = normalize_live_tick(tick)
        if reason:
            invalid_ticks.append({"symbol": str(tick.get("symbol", "")), "reason": reason})
        else:
            valid_ticks.append(normalized)
    valid_ticks.sort(key=lambda item: (item["datetime"], item["symbol"]))
    return {"valid_ticks": valid_ticks, "invalid_ticks": invalid_ticks}


def normalize_live_tick(tick: dict[str, Any]) -> tuple[dict, str]:
    try:
        symbol = str(tick.get("symbol", "")).strip().upper()
        if not symbol:
            return {}, "missing symbol"
        timestamp = _timestamp(tick.get("datetime"))
        close = _number(tick.get("close"))
        if close <= 0:
            return {}, "invalid close"
        open_price = _number(tick.get("open", close))
        high = _number(tick.get("high", close))
        low = _number(tick.get("low", close))
        volume = _number(tick.get("volume", 0.0))
        values = [open_price, high, low, close, volume]
        if not all(isfinite(value) for value in values):
            return {}, "non-finite value"
        return (
            {
                "datetime": timestamp,
                "symbol": symbol,
                "open": float(open_price),
                "high": float(max(high, open_price, close)),
                "low": float(min(low, open_price, close)),
                "close": float(close),
                "volume": float(max(volume, 0.0)),
                "source": str(tick.get("source", "unknown")),
            },
            "",
        )
    except Exception:
        return {}, "normalization failed"


def _number(value: Any) -> float:
    number = float(value)
    if not isfinite(number):
        raise ValueError("non-finite")
    return number


def _timestamp(value: Any) -> str:
    if value:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    else:
        parsed = datetime.now(UTC)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.replace(microsecond=0).isoformat()
