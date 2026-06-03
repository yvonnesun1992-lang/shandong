from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.data.sample_data import load_sample_ohlcv
from src.workflows.daily_workflow import run_daily_research_workflow
from src.workflows.run_log import save_workflow_run_log


def sample_fetch_data(market: str, symbol: str) -> pd.DataFrame:
    if symbol == "FAIL":
        raise ValueError("sample fetch failed")
    if market == "cn":
        return load_sample_ohlcv("cn", "300308")
    return load_sample_ohlcv("us", "NVDA")


def failing_fetch_data(market: str, symbol: str) -> pd.DataFrame:
    raise ValueError(f"no data for {market}:{symbol}")


def test_daily_workflow_empty_symbols_raise(tmp_path):
    with pytest.raises(ValueError, match="symbols cannot be empty"):
        run_daily_research_workflow("us", "us_default", [], sample_fetch_data, output_dir=tmp_path)


def test_daily_workflow_single_symbol_generates_report(tmp_path):
    result = run_daily_research_workflow("us", "us_default", ["NVDA"], sample_fetch_data, output_dir=tmp_path)

    assert result["success"] is True
    assert result["report_id"]
    assert Path(result["report_path"]).exists()
    assert result["success_symbols"] == ["NVDA"]
    assert result["failed_symbols"] == []
    assert result["run_id"]
    assert result["started_at"]
    assert result["finished_at"]
    assert result["elapsed_seconds"] >= 0
    assert result["success_count"] == 1
    assert result["failed_count"] == 0
    assert result["summary"]["average_score"] >= 0
    assert not result["trend_scores"].empty
    assert result["data_sources"]["NVDA"] == "sample"
    assert result["warnings"] == ["NVDA used local sample fallback data."]


def test_daily_workflow_partial_failure_still_generates_report(tmp_path):
    result = run_daily_research_workflow("us", "mixed", ["NVDA", "FAIL"], sample_fetch_data, output_dir=tmp_path)

    assert result["success"] is True
    assert result["report_id"]
    assert result["success_symbols"] == ["NVDA"]
    assert result["failed_symbols"][0]["symbol"] == "FAIL"
    assert "sample fetch failed" in result["failed_symbols"][0]["error"]
    assert Path(result["report_path"]).exists()


def test_daily_workflow_all_failures_do_not_save_empty_report(tmp_path):
    result = run_daily_research_workflow("us", "broken", ["NVDA", "MSFT"], failing_fetch_data, output_dir=tmp_path)

    assert result["success"] is False
    assert result["report_id"] is None
    assert result["report_path"] is None
    assert result["success_symbols"] == []
    assert result["success_count"] == 0
    assert result["failed_count"] == 2
    assert result["error_message"]
    assert len(result["failed_symbols"]) == 2
    assert list(tmp_path.glob("*.json")) == []


def test_daily_workflow_failure_result_can_be_saved_as_run_log(tmp_path):
    report_dir = tmp_path / "reports"
    log_dir = tmp_path / "logs"
    result = run_daily_research_workflow(
        "us",
        "broken",
        ["NVDA"],
        failing_fetch_data,
        output_dir=report_dir,
    )

    saved_log = save_workflow_run_log(result, log_dir)

    assert result["success"] is False
    assert saved_log["success"] is False
    assert saved_log["failed_count"] == 1
    assert list(report_dir.glob("*.json")) == []
    assert (log_dir / f"{saved_log['run_id']}.json").exists()


def test_daily_workflow_result_contains_expected_fields(tmp_path):
    result = run_daily_research_workflow("cn", "cn_default", ["300308"], sample_fetch_data, output_dir=tmp_path)

    assert {"report_id", "summary", "success_symbols", "failed_symbols", "data_sources"}.issubset(result)
    assert result["market"] == "cn"
    assert result["total_symbols"] == 1
    assert result["report"]["market"] == "cn"
    assert result["trend_scores"].iloc[0]["data_source"] == "sample"


def test_daily_workflow_rejects_invalid_market(tmp_path):
    with pytest.raises(ValueError, match="market must be"):
        run_daily_research_workflow("hk", "watchlist", ["000001"], sample_fetch_data, output_dir=tmp_path)


def test_daily_workflow_module_does_not_reference_broker_or_ai_clients():
    import src.workflows.daily_workflow as daily_workflow

    module_text = Path(daily_workflow.__file__).read_text(encoding="utf-8")
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
    ]

    for word in forbidden:
        assert word not in module_text


def test_daily_workflow_does_not_save_sensitive_keys(tmp_path):
    result = run_daily_research_workflow("us", "us_default", ["NVDA"], sample_fetch_data, output_dir=tmp_path)

    report_text = Path(result["report_path"]).read_text(encoding="utf-8").lower()
    forbidden = ["api_key", "secret", "password", "token"]
    for word in forbidden:
        assert word not in report_text
