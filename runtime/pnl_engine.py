from __future__ import annotations

import pandas as pd


class PnLEngine:
    def __init__(self) -> None:
        self.equity_curve: list[dict] = []
        self.peak_equity = 0.0
        self.initial_equity: float | None = None
        self.drawdown = 0.0
        self.realized_pnl = 0.0
        self.unrealized_pnl = 0.0

    def update(self, account_summary: dict, timestamp) -> dict:
        equity = float(account_summary.get("equity", 0.0))
        if self.initial_equity is None:
            self.initial_equity = equity
        self.peak_equity = max(self.peak_equity, equity)
        self.drawdown = (self.peak_equity - equity) / self.peak_equity if self.peak_equity else 0.0
        self.realized_pnl = float(account_summary.get("realized_pnl", 0.0))
        self.unrealized_pnl = equity - float(self.initial_equity or 0.0) - self.realized_pnl
        if "unrealized_pnl" in account_summary:
            self.unrealized_pnl = float(account_summary["unrealized_pnl"])
        point = {"timestamp": pd.Timestamp(timestamp), "equity": equity, "drawdown": self.drawdown}
        self.equity_curve.append(point)
        return self.snapshot()

    def snapshot(self) -> dict:
        equity = self.equity_curve[-1]["equity"] if self.equity_curve else 0.0
        return {
            "equity": float(equity),
            "realized_pnl": float(self.realized_pnl),
            "unrealized_pnl": float(self.unrealized_pnl),
            "drawdown": float(self.drawdown),
            "equity_curve": list(self.equity_curve),
        }

