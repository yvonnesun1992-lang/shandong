from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


def plot_equity_curve(equity_curve: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 4))
    frame = _with_datetime(equity_curve)
    ax.plot(frame["datetime"], frame["total_equity"], label="Total equity", color="#2563eb")
    ax.set_title("Equity Curve")
    ax.set_xlabel("Date")
    ax.set_ylabel("Equity")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    return fig


def plot_drawdown_curve(equity_curve: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 4))
    frame = _with_datetime(equity_curve)
    equity = pd.to_numeric(frame["total_equity"], errors="coerce").ffill().bfill().fillna(0)
    peak = equity.cummax()
    drawdown = ((peak - equity) / peak.replace(0, pd.NA)).fillna(0)
    ax.plot(frame["datetime"], drawdown, label="Drawdown", color="#dc2626")
    ax.set_title("Drawdown Curve")
    ax.set_xlabel("Date")
    ax.set_ylabel("Drawdown")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    return fig


def plot_trade_markers(price_data: pd.DataFrame, trades: pd.DataFrame, symbol: str):
    fig, ax = plt.subplots(figsize=(10, 4))
    prices = _with_datetime(price_data)
    ax.plot(prices["datetime"], prices["close"], label=f"{symbol} close", color="#111827")
    if trades is not None and not trades.empty:
        trade_frame = trades.copy()
        trade_frame["timestamp"] = pd.to_datetime(trade_frame["timestamp"])
        buys = trade_frame[trade_frame["action"] == "BUY"]
        sells = trade_frame[trade_frame["action"] == "SELL"]
        ax.scatter(buys["timestamp"], buys["price"], marker="^", color="#16a34a", label="BUY")
        ax.scatter(sells["timestamp"], sells["price"], marker="v", color="#dc2626", label="SELL")
    ax.set_title("Trade Markers")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    return fig


def plot_strategy_comparison(results: dict[str, pd.DataFrame]):
    fig, ax = plt.subplots(figsize=(10, 4))
    for name, equity_curve in results.items():
        frame = _with_datetime(equity_curve)
        ax.plot(frame["datetime"], frame["total_equity"], label=name)
    ax.set_title("Strategy Comparison")
    ax.set_xlabel("Date")
    ax.set_ylabel("Equity")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    return fig


def plot_regime_overlay(equity_curve: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 4))
    frame = _with_datetime(equity_curve)
    ax.plot(frame["datetime"], frame["total_equity"], label="Total equity", color="#111827")
    colors = {"bull": "#dcfce7", "bear": "#fee2e2", "sideways": "#e0f2fe"}
    if "regime" in frame:
        for regime, group in frame.groupby("regime"):
            ax.scatter(group["datetime"], group["total_equity"], s=18, label=str(regime), color=_point_color(str(regime)))
            for timestamp in group["datetime"]:
                ax.axvline(timestamp, color=colors.get(str(regime), "#f3f4f6"), alpha=0.05)
    ax.set_title("Regime Overlay")
    ax.set_xlabel("Date")
    ax.set_ylabel("Equity")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    return fig


def plot_strategy_contribution(contributions: dict[str, float]):
    fig, ax = plt.subplots(figsize=(8, 4))
    names = list(contributions.keys())
    values = [float(contributions[name]) for name in names]
    colors = ["#16a34a" if value >= 0 else "#dc2626" for value in values]
    ax.bar(names, values, color=colors)
    ax.axhline(0, color="#111827", linewidth=0.8)
    ax.set_title("Strategy Contribution")
    ax.set_xlabel("Strategy")
    ax.set_ylabel("Weighted vote contribution")
    ax.grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    return fig


def plot_risk_exposure(equity_curve: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 4))
    frame = _with_datetime(equity_curve)
    risk_score = pd.to_numeric(frame.get("risk_score", 0), errors="coerce").fillna(0)
    ax.plot(frame["datetime"], risk_score, label="Risk score", color="#f97316")
    if "exposure" in frame:
        ax2 = ax.twinx()
        ax2.plot(frame["datetime"], frame["exposure"], label="Exposure", color="#2563eb", alpha=0.7)
        ax2.set_ylabel("Exposure")
    ax.set_title("Risk Exposure")
    ax.set_xlabel("Date")
    ax.set_ylabel("Risk score")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    return fig


def _with_datetime(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["datetime"] = pd.to_datetime(result["datetime"])
    return result.sort_values("datetime").reset_index(drop=True)


def _point_color(regime: str) -> str:
    return {"bull": "#16a34a", "bear": "#dc2626", "sideways": "#0284c7"}.get(regime, "#6b7280")
