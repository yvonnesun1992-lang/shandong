from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd
import pytest

from src.reports.daily_research_report import (
    build_daily_research_report,
    daily_report_to_markdown,
    delete_daily_research_report,
    export_daily_report_summary_csv,
    generate_daily_report_id,
    list_daily_research_reports,
    load_daily_research_report,
    save_daily_research_report,
)


def sample_trend_scores() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"symbol": "NVDA", "score": 95, "status": "Strong trend", "close": 100.0, "rsi14": 65.0},
            {"symbol": "MSFT", "score": 78, "status": "Watchlist", "close": 200.0, "rsi14": 55.0},
            {"symbol": "AMD", "score": 45, "status": "Neutral", "close": 80.0, "rsi14": 48.0},
            {"symbol": "TSLA", "score": 25, "status": "Weak", "close": 150.0, "rsi14": 35.0},
        ]
    )


def test_generate_daily_report_id_is_safe_and_unique():
    first = generate_daily_report_id()
    second = generate_daily_report_id()

    assert first
    assert first != second
    assert re.fullmatch(r"[A-Za-z0-9_-]+", first)
    assert "/" not in first
    assert "\\" not in first
    assert ".." not in first


def test_build_daily_research_report_from_trend_scores():
    report = build_daily_research_report("us", "us_default", sample_trend_scores())

    assert report["market"] == "us"
    assert report["watchlist_name"] == "us_default"
    assert report["disclaimer"]
    assert report["market_summary"]["total_symbols"] == 4
    assert report["market_summary"]["strong_trend_count"] == 1
    assert report["market_summary"]["watchlist_count"] == 1
    assert report["market_summary"]["neutral_count"] == 1
    assert report["market_summary"]["weak_count"] == 1
    assert report["market_summary"]["average_score"] == pytest.approx(60.75)
    assert len(report["top_symbols"]) <= 5
    assert report["top_symbols"][0]["symbol"] == "NVDA"
    assert report["risk_symbols"][0]["symbol"] == "TSLA"


def test_build_daily_research_report_handles_empty_trend_scores():
    empty_scores = pd.DataFrame(columns=["symbol", "score", "status", "close", "rsi14"])

    report = build_daily_research_report("us", "empty", empty_scores)

    assert report["market_summary"]["total_symbols"] == 0
    assert report["market_summary"]["average_score"] == 0.0
    assert report["notes"]


def test_daily_report_to_markdown_contains_key_sections():
    report = build_daily_research_report("us", "us_default", sample_trend_scores())

    markdown = daily_report_to_markdown(report)

    assert isinstance(markdown, str)
    assert "# 每日量化研究报告" in markdown
    assert "免责声明" in markdown
    assert "Top 趋势股票" in markdown
    assert "风险观察股票" in markdown


def test_save_daily_research_report(tmp_path):
    report = build_daily_research_report("us", "us_default", sample_trend_scores())

    saved = save_daily_research_report(report, tmp_path)

    path = tmp_path / f"{saved['report_id']}.json"
    assert path.exists()
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["report_id"] == saved["report_id"]


def test_list_daily_research_reports_empty(tmp_path):
    reports = list_daily_research_reports(tmp_path)

    assert reports.empty


def test_list_daily_research_reports_has_key_columns(tmp_path):
    report = build_daily_research_report("cn", "cn_default", sample_trend_scores())
    save_daily_research_report(report, tmp_path)

    reports = list_daily_research_reports(tmp_path)

    assert not reports.empty
    assert {"report_id", "created_at", "market", "watchlist_name"}.issubset(reports.columns)


def test_load_daily_research_report(tmp_path):
    report = build_daily_research_report("us", "us_default", sample_trend_scores())
    saved = save_daily_research_report(report, tmp_path)

    loaded = load_daily_research_report(saved["report_id"], tmp_path)

    assert loaded["report_id"] == saved["report_id"]


def test_load_missing_daily_report_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_daily_research_report("missing_report", tmp_path)


def test_load_invalid_daily_json_raises(tmp_path):
    (tmp_path / "broken.json").write_text("{bad json", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid"):
        load_daily_research_report("broken", tmp_path)


def test_delete_daily_research_report(tmp_path):
    report = build_daily_research_report("us", "us_default", sample_trend_scores())
    saved = save_daily_research_report(report, tmp_path)

    delete_daily_research_report(saved["report_id"], tmp_path)

    assert not (tmp_path / f"{saved['report_id']}.json").exists()


def test_delete_missing_daily_report_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        delete_daily_research_report("missing_report", tmp_path)


def test_daily_report_path_traversal_is_rejected(tmp_path):
    with pytest.raises(ValueError):
        load_daily_research_report("../outside", tmp_path)


def test_export_daily_report_summary_csv(tmp_path):
    report = build_daily_research_report("us", "us_default", sample_trend_scores())
    saved = save_daily_research_report(report, tmp_path)

    csv_text = export_daily_report_summary_csv(tmp_path)

    assert "report_id" in csv_text
    assert "market" in csv_text
    assert "watchlist_name" in csv_text
    assert saved["report_id"] in csv_text


def test_sensitive_keys_are_not_saved(tmp_path):
    with pytest.raises(ValueError, match="API keys"):
        build_daily_research_report(
            "us",
            "us_default",
            sample_trend_scores(),
            data_source_summary={"api_key": "bad"},
        )


def test_daily_report_module_does_not_reference_broker_or_ai_clients():
    import src.reports.daily_research_report as daily_research_report

    module_text = Path(daily_research_report.__file__).read_text(encoding="utf-8")
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
