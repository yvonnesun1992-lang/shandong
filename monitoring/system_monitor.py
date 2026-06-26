from __future__ import annotations


class SystemMonitor:
    def __init__(self) -> None:
        self.pnl_stream: list[dict] = []
        self.trades_log: list[dict] = []
        self.signal_log: list[dict] = []
        self.error_log: list[dict] = []
        self.regime_state: dict = {"state": "unknown", "confidence": 0.0}

    def record_signals(self, signals: list[dict]) -> None:
        self.signal_log.extend(signals)
        if signals:
            self.regime_state = {"state": signals[0].get("regime", "unknown"), "confidence": 0.0}

    def record_fills(self, fills: list[dict]) -> None:
        self.trades_log.extend(fills)

    def record_portfolio(self, snapshot: dict) -> None:
        self.pnl_stream.append(snapshot)

    def record_error(self, message: str, context: dict | None = None) -> None:
        self.error_log.append({"message": message, "context": context or {}})

    def dashboard_data(self) -> dict:
        equity = [float(item.get("equity", 0.0)) for item in self.pnl_stream]
        peak = 0.0
        drawdown = []
        for value in equity:
            peak = max(peak, value)
            drawdown.append((peak - value) / peak if peak else 0.0)
        exposure = [
            float(item.get("holdings", 0.0)) / float(item.get("equity", 1.0))
            if float(item.get("equity", 0.0)) else 0.0
            for item in self.pnl_stream
        ]
        return {
            "equity_curve": equity,
            "drawdown_curve": drawdown,
            "exposure_curve": exposure,
            "signal_count": len(self.signal_log),
            "trade_count": len(self.trades_log),
            "error_count": len(self.error_log),
            "regime_state": self.regime_state,
        }
