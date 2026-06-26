from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime
from typing import Iterable


class SignalEngine:
    """Merge strategy outputs into one actionable signal per symbol."""

    def merge_signals(self, signals: Iterable[dict], symbols: Iterable[str] | None = None) -> list[dict]:
        grouped: dict[str, list[dict]] = defaultdict(list)
        for signal in signals:
            symbol = str(signal.get("symbol", "")).upper().strip()
            action = str(signal.get("action", "HOLD")).upper()
            if not symbol or action == "HOLD":
                continue
            grouped[symbol].append(
                {
                    "symbol": symbol,
                    "action": action if action in {"BUY", "SELL"} else "HOLD",
                    "strength": float(signal.get("strength", 0.0) or 0.0),
                    "timestamp": signal.get("timestamp") or datetime.utcnow(),
                }
            )

        merged = []
        for symbol, items in grouped.items():
            strongest = max(items, key=lambda item: (item["strength"], 1 if item["action"] == "SELL" else 0))
            merged.append(strongest)

        if not merged and symbols:
            now = datetime.now(UTC)
            return [{"symbol": str(symbol).upper(), "action": "HOLD", "strength": 0.0, "timestamp": now} for symbol in symbols]
        return sorted(merged, key=lambda item: item["symbol"])
