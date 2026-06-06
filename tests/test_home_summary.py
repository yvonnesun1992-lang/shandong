from __future__ import annotations

import inspect

import pandas as pd

from src.ui.home import build_home_summary


def test_build_home_summary_handles_empty_data():
    summary = build_home_summary("美股", "us_default", [])

    assert summary["market"] == "美股"
    assert summary["watchlist_name"] == "us_default"
    assert summary["symbol_count"] == 0
    assert summary["health_status"] == "unknown"
    assert summary["average_score"] == 0.0
    assert summary["notes"]


def test_build_home_summary_counts_trend_statuses():
    trend_scores = pd.DataFrame(
        [
            {"股票代码": "NVDA", "趋势分数": 90, "状态": "Strong trend"},
            {"股票代码": "MSFT", "趋势分数": 70, "状态": "Watchlist"},
            {"股票代码": "AMD", "趋势分数": 30, "状态": "Weak"},
        ]
    )

    summary = build_home_summary("美股", "us_default", ["NVDA", "MSFT", "AMD"], trend_scores=trend_scores)

    assert summary["strong_trend_count"] == 1
    assert summary["watchlist_count"] == 1
    assert summary["weak_count"] == 1
    assert summary["average_score"] == 190 / 3


def test_build_home_summary_reads_paper_summary():
    paper_summary = {
        "cash": 90000.0,
        "positions_value": 12000.0,
        "total_assets": 102000.0,
        "unrealized_pnl": 2000.0,
    }

    summary = build_home_summary("美股", "us_default", ["NVDA"], paper_portfolio_summary=paper_summary)

    assert summary["paper_cash"] == 90000.0
    assert summary["paper_positions_value"] == 12000.0
    assert summary["paper_total_value"] == 102000.0
    assert summary["paper_unrealized_pnl"] == 2000.0


def test_build_home_summary_reads_latest_workflow_and_report():
    workflow_runs = pd.DataFrame([{"status": "success", "run_id": "run_1"}])
    reports = pd.DataFrame([{"report_id": "report_1"}])

    summary = build_home_summary(
        "美股",
        "us_default",
        ["NVDA"],
        health_summary={"overall_status": "ok"},
        latest_workflow_runs=workflow_runs,
        latest_reports=reports,
    )

    assert summary["health_status"] == "ok"
    assert summary["latest_workflow_status"] == "success"
    assert summary["latest_report_id"] == "report_1"


def test_home_summary_has_no_trading_or_ai_calls():
    source = inspect.getsource(build_home_summary)
    forbidden = [
        "IBKR",
        "富途",
        "Alpaca",
        "Robinhood",
        "broker order",
        "place_order",
        "real trade",
        "OpenAI API",
        "AI prediction",
        "api_key",
        "secret",
        "password",
        "token",
    ]
    for word in forbidden:
        assert word not in source
