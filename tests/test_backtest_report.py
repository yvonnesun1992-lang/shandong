from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd
import pytest

from src.reports.backtest_report import (
    delete_backtest_report,
    export_report_summary_csv,
    generate_report_id,
    list_backtest_reports,
    load_backtest_report,
    save_backtest_report,
)


def sample_summary() -> dict:
    return {
        "total_return": 0.12,
        "annualized_return": 0.18,
        "max_drawdown": -0.08,
        "number_of_trades": 4,
        "final_portfolio_value": 112000.0,
    }


def test_generate_report_id_is_safe_and_unique():
    first = generate_report_id()
    second = generate_report_id()

    assert first
    assert first != second
    assert re.fullmatch(r"[A-Za-z0-9_-]+", first)
    assert "/" not in first
    assert "\\" not in first
    assert ".." not in first


def test_save_summary_only_report(tmp_path):
    report = save_backtest_report(
        "single_stock_backtest",
        {"symbol": "NVDA"},
        sample_summary(),
        output_dir=tmp_path,
    )

    path = tmp_path / f"{report['report_id']}.json"
    assert path.exists()
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["report_type"] == "single_stock_backtest"
    assert loaded["summary"]["final_portfolio_value"] == 112000.0
    assert loaded["equity_curve"] == []
    assert loaded["trades"] == []


def test_save_report_with_equity_curve_and_trades(tmp_path):
    equity_curve = pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-01-01", "2026-01-02"]),
            "total_value": [100000.0, 101000.0],
        }
    )
    trades = pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-01-02"]),
            "symbol": ["NVDA"],
            "action": ["BUY"],
            "amount": [10000.0],
        }
    )

    report = save_backtest_report(
        "portfolio_backtest",
        {"watchlist": ["NVDA"]},
        sample_summary(),
        equity_curve=equity_curve,
        trades=trades,
        output_dir=tmp_path,
    )

    loaded = load_backtest_report(report["report_id"], tmp_path)
    assert loaded["equity_curve"][0]["date"] == "2026-01-01T00:00:00"
    assert loaded["trades"][0]["symbol"] == "NVDA"


def test_list_backtest_reports_empty(tmp_path):
    reports = list_backtest_reports(tmp_path)

    assert reports.empty


def test_list_backtest_reports_has_key_columns(tmp_path):
    save_backtest_report("portfolio_backtest", {}, sample_summary(), output_dir=tmp_path)

    reports = list_backtest_reports(tmp_path)

    assert not reports.empty
    assert {
        "report_id",
        "created_at",
        "report_type",
        "total_return",
        "annualized_return",
        "max_drawdown",
        "number_of_trades",
        "final_portfolio_value",
    }.issubset(reports.columns)


def test_load_missing_report_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_backtest_report("missing_report", tmp_path)


def test_load_invalid_json_raises(tmp_path):
    (tmp_path / "broken.json").write_text("{bad json", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid"):
        load_backtest_report("broken", tmp_path)


def test_delete_backtest_report(tmp_path):
    report = save_backtest_report("portfolio_backtest", {}, sample_summary(), output_dir=tmp_path)

    delete_backtest_report(report["report_id"], tmp_path)

    assert not (tmp_path / f"{report['report_id']}.json").exists()


def test_delete_missing_report_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        delete_backtest_report("missing_report", tmp_path)


def test_report_id_path_traversal_is_rejected(tmp_path):
    with pytest.raises(ValueError):
        load_backtest_report("../outside", tmp_path)


def test_export_report_summary_csv(tmp_path):
    report = save_backtest_report("portfolio_backtest", {}, sample_summary(), output_dir=tmp_path)

    csv_text = export_report_summary_csv(tmp_path)

    assert "report_id" in csv_text
    assert report["report_id"] in csv_text
    assert "final_portfolio_value" in csv_text


def test_sensitive_keys_are_not_saved(tmp_path):
    with pytest.raises(ValueError, match="API keys"):
        save_backtest_report(
            "portfolio_backtest",
            {"api_key": "bad"},
            sample_summary(),
            output_dir=tmp_path,
        )


def test_report_module_does_not_reference_broker_or_order_clients():
    import src.reports.backtest_report as backtest_report

    names = set(save_backtest_report.__code__.co_names)
    module_text = Path(backtest_report.__file__).read_text(encoding="utf-8")

    forbidden = ["IBKR", "富途", "Alpaca", "Robinhood", "broker order", "place_order", "real trade"]
    assert "place_order" not in names
    assert "broker_order" not in names
    for word in forbidden:
        assert word not in module_text
