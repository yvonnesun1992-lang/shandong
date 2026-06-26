from __future__ import annotations

import math

import numpy as np
import pandas as pd

from broker.paper_broker import PaperBroker
from feature_engine.factors import calculate_factors
from regime.regime_detector import RegimeDetector
from risk.risk_engine import RiskEngine


class BacktestEngine:
    def __init__(
        self,
        initial_cash: float = 100_000.0,
        trade_fraction: float = 0.1,
        regime_detector: RegimeDetector | None = None,
        risk_engine: RiskEngine | None = None,
    ) -> None:
        self.initial_cash = float(initial_cash)
        self.trade_fraction = float(trade_fraction)
        self.regime_detector = regime_detector or RegimeDetector()
        self.risk_engine = risk_engine or RiskEngine()

    def run(self, data: pd.DataFrame, strategy, symbol: str) -> dict:
        frame = self._prepare_data(data)
        factors = calculate_factors(frame)
        broker = PaperBroker(initial_cash=self.initial_cash)
        equity_rows = []
        strategy_contribution: dict[str, float] = {}

        for index in range(len(frame)):
            current = frame.iloc[index]
            history = frame.iloc[: index + 1].copy()
            factor_history = factors.iloc[: index + 1].copy()
            regime = self.regime_detector.detect(history) if len(history) >= 20 else {"state": "sideways", "confidence": 0.0}
            signal = self._generate_signal(strategy, history, symbol, regime)
            price = float(current["close"])
            timestamp = current["datetime"]
            portfolio_snapshot = broker.update_portfolio({symbol: price}, timestamp=timestamp)
            portfolio_value = float(portfolio_snapshot["total_equity"])
            current_positions_value = {symbol: broker.positions.get(symbol, 0) * price}
            volatility = float(factor_history["realized_vol_20d"].iloc[-1]) if "realized_vol_20d" in factor_history else 0.0
            risk_decision = {"risk_score": 0.0, "approved_value": 0.0, "exposure_multiplier": 1.0}

            if signal["action"] == "BUY" and broker.positions.get(symbol, 0) == 0:
                budget = broker.cash * self.trade_fraction
                risk_decision = self.risk_engine.evaluate_order(
                    symbol=symbol,
                    action="BUY",
                    desired_value=budget,
                    portfolio_value=portfolio_value,
                    current_positions=current_positions_value,
                    equity_curve=[row["total_equity"] for row in equity_rows],
                    volatility=volatility,
                )
                shares = max(int(risk_decision["approved_value"] // max(price, 1e-12)), 0)
                if shares > 0:
                    broker.place_order(symbol, "BUY", price=price, shares=shares, timestamp=timestamp)
            elif signal["action"] == "SELL" and broker.positions.get(symbol, 0) > 0:
                broker.place_order(symbol, "SELL", price=price, shares=broker.positions[symbol], timestamp=timestamp)

            self._accumulate_strategy_contribution(strategy_contribution, signal)
            snapshot = broker.update_portfolio({symbol: price}, timestamp=timestamp)
            equity_rows.append(
                {
                    "datetime": timestamp,
                    "cash": snapshot["cash"],
                    "holdings_value": snapshot["holdings_value"],
                    "total_equity": snapshot["total_equity"],
                    "regime": regime["state"],
                    "risk_score": risk_decision.get("risk_score", 0.0),
                    "exposure": snapshot["holdings_value"] / snapshot["total_equity"] if snapshot["total_equity"] else 0.0,
                }
            )

        equity_curve = pd.DataFrame(equity_rows)
        trades = pd.DataFrame(broker.trades)
        metrics = calculate_metrics(equity_curve, trades, self.initial_cash)
        return {
            "equity_curve": equity_curve,
            "trades": trades,
            "metrics": metrics,
            "portfolio": broker.update_portfolio({symbol: float(frame["close"].iloc[-1])}),
            "regime_breakdown": calculate_regime_breakdown(equity_curve),
            "strategy_contribution": strategy_contribution,
            "risk_exposure": equity_curve[["datetime", "risk_score", "exposure"]].copy() if not equity_curve.empty else pd.DataFrame(),
        }

    @staticmethod
    def _prepare_data(data: pd.DataFrame) -> pd.DataFrame:
        frame = data.copy()
        frame["datetime"] = pd.to_datetime(frame["datetime"])
        for column in ["open", "high", "low", "close", "volume"]:
            frame[column] = pd.to_numeric(frame[column], errors="coerce").ffill().bfill().fillna(0)
        return frame.sort_values("datetime").reset_index(drop=True)

    @staticmethod
    def _generate_signal(strategy, history: pd.DataFrame, symbol: str, regime: dict) -> dict:
        try:
            return strategy.generate_signal(history, symbol, regime)
        except TypeError:
            return strategy.generate_signal(history, symbol)

    @staticmethod
    def _accumulate_strategy_contribution(contribution: dict[str, float], signal: dict) -> None:
        strategy_signals = signal.get("strategy_signals", {})
        weights = signal.get("weights", {})
        for name, item in strategy_signals.items():
            direction = 1 if item.get("action") == "BUY" else -1 if item.get("action") == "SELL" else 0
            contribution[name] = contribution.get(name, 0.0) + direction * float(item.get("strength", 0.0)) * float(weights.get(name, 1.0))


def calculate_metrics(equity_curve: pd.DataFrame, trades: pd.DataFrame, initial_cash: float) -> dict:
    if equity_curve.empty:
        return {
            "total_return": 0.0,
            "annual_return": 0.0,
            "max_drawdown": 0.0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "calmar_ratio": 0.0,
            "turnover": 0.0,
            "risk_adjusted_return": 0.0,
            "win_rate": 0.0,
            "number_of_trades": 0,
        }

    equity = pd.to_numeric(equity_curve["total_equity"], errors="coerce").ffill().bfill().fillna(initial_cash)
    total_return = float(equity.iloc[-1] / initial_cash - 1) if initial_cash else 0.0
    daily_returns = equity.pct_change().replace([np.inf, -np.inf], np.nan).fillna(0)
    years = max(len(equity) / 252, 1 / 252)
    annual_return = float((1 + total_return) ** (1 / years) - 1) if total_return > -1 else -1.0

    peak = equity.cummax()
    drawdown = ((peak - equity) / peak.replace(0, np.nan)).fillna(0)
    max_drawdown = float(drawdown.max())
    std = float(daily_returns.std(ddof=0))
    sharpe = float(daily_returns.mean() / std * math.sqrt(252)) if std > 0 else 0.0
    downside = daily_returns[daily_returns < 0]
    downside_std = float(downside.std(ddof=0))
    sortino = float(daily_returns.mean() / downside_std * math.sqrt(252)) if downside_std > 0 else 0.0
    calmar = float(annual_return / max_drawdown) if max_drawdown > 0 else 0.0
    if not trades.empty and "gross_value" in trades:
        traded_value = float(trades["gross_value"].sum())
    elif not trades.empty and {"price", "shares"} <= set(trades.columns):
        traded_value = float((trades["price"] * trades["shares"]).sum())
    else:
        traded_value = 0.0
    average_equity = float(equity.mean()) if not equity.empty else initial_cash
    turnover = float(traded_value / max(average_equity, 1e-12))
    risk_adjusted_return = float(total_return / (1 + max_drawdown + std))

    win_rate = _win_rate(trades)
    return {
        "total_return": total_return,
        "annual_return": annual_return,
        "max_drawdown": max_drawdown,
        "sharpe_ratio": sharpe,
        "sortino_ratio": sortino,
        "calmar_ratio": calmar,
        "turnover": turnover,
        "risk_adjusted_return": risk_adjusted_return,
        "win_rate": win_rate,
        "number_of_trades": int(len(trades)),
    }


def calculate_regime_breakdown(equity_curve: pd.DataFrame) -> dict:
    if equity_curve.empty or "regime" not in equity_curve:
        return {}
    frame = equity_curve.copy()
    frame["returns"] = pd.to_numeric(frame["total_equity"], errors="coerce").pct_change().fillna(0)
    breakdown = {}
    for regime, group in frame.groupby("regime"):
        breakdown[str(regime)] = {
            "days": int(len(group)),
            "total_return": float((1 + group["returns"]).prod() - 1),
            "average_risk_score": float(group["risk_score"].mean()) if "risk_score" in group else 0.0,
        }
    return breakdown


def _win_rate(trades: pd.DataFrame) -> float:
    if trades.empty or "action" not in trades:
        return 0.0
    buys = []
    wins = 0
    closed = 0
    for _, trade in trades.iterrows():
        if trade["action"] == "BUY":
            buys.append(float(trade["price"]))
        elif trade["action"] == "SELL" and buys:
            entry = buys.pop(0)
            wins += 1 if float(trade["price"]) > entry else 0
            closed += 1
    return float(wins / closed) if closed else 0.0
