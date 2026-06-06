from __future__ import annotations

from typing import Any

import pandas as pd


def _count_status(trend_scores: pd.DataFrame, status: str) -> int:
    if trend_scores is None or trend_scores.empty or "状态" not in trend_scores.columns:
        return 0
    return int((trend_scores["状态"] == status).sum())


def _average_score(trend_scores: pd.DataFrame) -> float:
    if trend_scores is None or trend_scores.empty or "趋势分数" not in trend_scores.columns:
        return 0.0
    scores = pd.to_numeric(trend_scores["趋势分数"], errors="coerce").dropna()
    if scores.empty:
        return 0.0
    return float(scores.mean())


def _latest_value(records: Any, key: str, default: str = "") -> str:
    if records is None:
        return default
    if isinstance(records, pd.DataFrame):
        if records.empty or key not in records.columns:
            return default
        value = records.iloc[0].get(key, default)
        return default if pd.isna(value) else str(value)
    if isinstance(records, list) and records:
        first = records[0]
        if isinstance(first, dict):
            value = first.get(key, default)
            return default if value is None else str(value)
    return default


def build_home_summary(
    market: str,
    watchlist_name: str,
    symbols: list[str],
    trend_scores=None,
    paper_portfolio_summary: dict | None = None,
    health_summary: dict | None = None,
    latest_workflow_runs=None,
    latest_reports=None,
) -> dict:
    """Build a dashboard home summary without reading files or calling services."""
    if trend_scores is None:
        trend_scores = pd.DataFrame()
    if not isinstance(trend_scores, pd.DataFrame):
        trend_scores = pd.DataFrame(trend_scores)

    paper_summary = paper_portfolio_summary or {}
    health = health_summary or {}
    notes: list[str] = []
    if trend_scores.empty:
        notes.append("趋势评分暂不可用。")
    if not paper_summary:
        notes.append("模拟账户摘要暂不可用。")
    if not health:
        notes.append("系统健康状态暂不可用。")

    return {
        "market": market,
        "watchlist_name": watchlist_name,
        "symbol_count": len(symbols or []),
        "strong_trend_count": _count_status(trend_scores, "Strong trend"),
        "watchlist_count": _count_status(trend_scores, "Watchlist"),
        "neutral_count": _count_status(trend_scores, "Neutral"),
        "weak_count": _count_status(trend_scores, "Weak"),
        "average_score": _average_score(trend_scores),
        "paper_total_value": float(paper_summary.get("total_assets", paper_summary.get("total_value", 0.0)) or 0.0),
        "paper_cash": float(paper_summary.get("cash", 0.0) or 0.0),
        "paper_positions_value": float(paper_summary.get("positions_value", 0.0) or 0.0),
        "paper_unrealized_pnl": float(paper_summary.get("unrealized_pnl", 0.0) or 0.0),
        "health_status": str(health.get("overall_status", health.get("status", "unknown")) or "unknown"),
        "latest_workflow_status": _latest_value(latest_workflow_runs, "status", "unknown"),
        "latest_report_id": _latest_value(latest_reports, "report_id", ""),
        "notes": notes,
    }
