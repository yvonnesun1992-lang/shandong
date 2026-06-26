from __future__ import annotations

import pandas as pd

from trading.paper_broker import PaperBroker
from trading.performance import calculate_performance_metrics
from trading.risk_limits import RiskLimits
from trading.signal_to_order import SignalToOrderConverter


class PaperTradingRunner:
    def __init__(self, initial_cash: float = 100_000.0) -> None:
        self.broker = PaperBroker(initial_cash=initial_cash)
        self.converter = SignalToOrderConverter()
        self.risk_limits = RiskLimits()
        self.initial_cash = float(initial_cash)

    def run(self, market_data: pd.DataFrame, signal_fn) -> dict:
        data = market_data.copy()
        data["datetime"] = pd.to_datetime(data["datetime"])
        data = data.sort_values("datetime").reset_index(drop=True)
        equity_curve = []
        for _, row in data.iterrows():
            symbol = str(row.get("symbol", "AAPL")).upper()
            market_price = float(row["close"])
            self.broker.account.update_market_price(symbol, market_price)
            self.risk_limits.update_equity(self.broker.account.calculate_equity())
            signal = signal_fn(row, self.broker.account)
            order = self.converter.convert(signal, self.broker.account, market_price)
            if order is not None:
                decision = self.risk_limits.validate_order(order, self.broker.account, market_price)
                if decision["approved"]:
                    self.broker.execute_order(order, market_price)
            self.broker.account.update_market_price(symbol, market_price)
            summary = self.broker.get_account_summary()
            equity_curve.append({"datetime": row["datetime"], "equity": summary["equity"], "cash": summary["cash"]})
        trade_history = self.broker.get_trade_history()
        return {
            "equity_curve": equity_curve,
            "trade_history": trade_history,
            "final_account_summary": self.broker.get_account_summary(),
            "performance_metrics": calculate_performance_metrics(equity_curve, trade_history, self.initial_cash),
            "safety": {
                "broker_connection": False,
                "real_trading": False,
                "real_account": False,
                "payment": False,
                "production_deployment": False,
            },
        }
