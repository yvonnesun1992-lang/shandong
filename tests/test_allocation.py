from __future__ import annotations

import inspect

from src.portfolio.allocation import RESEARCH_DISCLAIMER, build_allocation_plan


# V1.18 raw refresh marker: keep test_allocation.py as real multiline Python.
# V1.18 formatting verification marker 6: remote raw must stay multiline.
def test_build_allocation_plan_with_valid_inputs():
    result = build_allocation_plan(
        symbols=["AAPL", "MSFT", "NVDA"],
        scores={"AAPL": 80, "MSFT": 70, "NVDA": 90},
        prices={"AAPL": 100, "MSFT": 200, "NVDA": 300},
        portfolio_value=100000,
        max_position_pct=0.2,
        cash_buffer_pct=0.1,
    )

    assert result["summary"]["portfolio_value"] == 100000
    assert result["summary"]["investable_value"] == 90000
    assert result["summary"]["cash_buffer"] == 10000
    assert result["summary"]["selected_symbols"] == 3
    assert len(result["allocation"]) == 3
    assert result["failed_symbols"] == []
    assert RESEARCH_DISCLAIMER in result["warnings"]


def test_low_score_symbol_gets_zero_target_weight():
    result = build_allocation_plan(
        symbols=["AAPL", "MSFT"],
        scores={"AAPL": 80, "MSFT": 40},
        prices={"AAPL": 100, "MSFT": 100},
        min_score=60,
    )

    rows = {row["symbol"]: row for row in result["allocation"]}
    assert rows["AAPL"]["target_weight"] > 0
    assert rows["MSFT"]["target_weight"] == 0


def test_target_weight_respects_max_position_pct():
    result = build_allocation_plan(
        symbols=["AAPL", "MSFT", "NVDA"],
        scores={"AAPL": 100, "MSFT": 90, "NVDA": 80},
        prices={"AAPL": 100, "MSFT": 100, "NVDA": 100},
        max_position_pct=0.15,
    )

    for row in result["allocation"]:
        assert row["target_weight"] <= 0.15


def test_cash_buffer_pct_keeps_cash_buffer():
    result = build_allocation_plan(
        symbols=["AAPL"],
        scores={"AAPL": 100},
        prices={"AAPL": 100},
        portfolio_value=200000,
        cash_buffer_pct=0.25,
    )

    assert result["summary"]["cash_buffer"] == 50000
    assert result["summary"]["investable_value"] == 150000


def test_current_positions_calculate_difference_value():
    result = build_allocation_plan(
        symbols=["AAPL"],
        scores={"AAPL": 100},
        prices={"AAPL": 100},
        current_positions={"AAPL": 10},
        portfolio_value=100000,
        max_position_pct=0.2,
        cash_buffer_pct=0.1,
    )

    row = result["allocation"][0]
    assert row["current_shares"] == 10
    assert row["current_value"] == 1000
    assert row["difference_value"] == row["target_value"] - 1000


def test_missing_price_returns_failed_symbol_without_crashing():
    result = build_allocation_plan(
        symbols=["AAPL", "MSFT"],
        scores={"AAPL": 90, "MSFT": 80},
        prices={"AAPL": 100},
    )

    assert result["failed_symbols"] == [{"symbol": "MSFT", "error": "Missing or invalid price."}]
    assert any("MSFT" in warning for warning in result["warnings"])
    assert [row["symbol"] for row in result["allocation"]] == ["AAPL"]


def test_empty_symbol_list_returns_warning_without_crashing():
    result = build_allocation_plan(symbols=[], scores={}, prices={})

    assert result["allocation"] == []
    assert result["failed_symbols"] == []
    assert result["summary"]["selected_symbols"] == 0
    assert any("股票池为空" in warning for warning in result["warnings"])


def test_allocation_module_does_not_reference_trading_or_ai_clients():
    import src.portfolio.allocation as allocation

    source = inspect.getsource(allocation)
    forbidden = [
        "IB" + "KR",
        "富" + "途",
        "Al" + "paca",
        "Robin" + "hood",
        "broker " + "order",
        "place_" + "order",
        "real " + "trade",
        "api_" + "key",
        "sec" + "ret",
        "pass" + "word",
        "tok" + "en",
        "Open" + "AI API",
        "AI " + "prediction",
    ]
    for word in forbidden:
        assert word not in source
