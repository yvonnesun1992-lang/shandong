from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


def generate_factor_report(score_table: pd.DataFrame, ic_results: dict, portfolio_result: dict) -> dict:
    table = score_table.copy()
    markdown = ["# Quant Factor Research Report", "", "## Factor Performance Table", ""]
    if table.empty:
        markdown.append("No factors available.")
    else:
        markdown.append(table.to_markdown(index=False))
    markdown.extend(
        [
            "",
            "## Summary",
            "",
            "- IC, IR, Sharpe proxy, and stability are calculated from local research data.",
            "- Factor portfolio returns are simulated only; no broker connection or real trading is used.",
            "- The analysis uses forward returns aligned after factor timestamps to avoid look-ahead bias.",
        ]
    )
    return {
        "markdown": "\n".join(markdown),
        "figures": {
            "ic_curve": plot_ic_curve(ic_results),
            "factor_ranking": plot_factor_ranking(table),
            "cumulative_factor_returns": plot_cumulative_factor_returns(portfolio_result),
        },
    }


def plot_ic_curve(ic_results: dict):
    fig, ax = plt.subplots(figsize=(9, 4))
    for factor, result in ic_results.items():
        series = result.get("ic_series", pd.Series(dtype=float))
        if not series.empty:
            ax.plot(pd.to_datetime(series.index), series.values, label=factor)
    ax.axhline(0, color="#111827", linewidth=0.8)
    ax.set_title("IC Curve")
    ax.set_xlabel("Date")
    ax.set_ylabel("IC")
    ax.grid(True, alpha=0.25)
    if ax.lines:
        ax.legend()
    fig.tight_layout()
    return fig


def plot_factor_ranking(score_table: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 4))
    if not score_table.empty:
        table = score_table.sort_values("score", ascending=True)
        ax.barh(table["factor"], table["score"], color="#2563eb")
    ax.set_title("Factor Ranking")
    ax.set_xlabel("Score")
    ax.grid(True, axis="x", alpha=0.25)
    fig.tight_layout()
    return fig


def plot_cumulative_factor_returns(portfolio_result: dict):
    fig, ax = plt.subplots(figsize=(9, 4))
    returns = portfolio_result.get("portfolio_returns", pd.Series(dtype=float)).fillna(0)
    cumulative = (1 + returns).cumprod() - 1
    if not cumulative.empty:
        ax.plot(pd.to_datetime(cumulative.index), cumulative.values, color="#16a34a", label="Factor portfolio")
        ax.legend()
    ax.set_title("Cumulative Factor Returns")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative return")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    return fig
