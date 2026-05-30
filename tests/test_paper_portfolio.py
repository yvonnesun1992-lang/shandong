from __future__ import annotations

from pathlib import Path

import pytest

from src.paper_trading import portfolio as paper_portfolio
from src.paper_trading.portfolio import (
    buy_paper_position,
    calculate_portfolio_summary,
    get_trade_history,
    load_paper_portfolio,
    reset_paper_portfolio,
    sell_paper_position,
)


def test_missing_portfolio_file_creates_default(tmp_path):
    path = tmp_path / "config" / "paper_portfolio.json"

    portfolio = load_paper_portfolio(path)

    assert path.exists()
    assert portfolio["cash"] == 100000.0
    assert portfolio["positions"] == {}
    assert portfolio["trades"] == []


def test_reset_paper_portfolio_resets_cash_positions_and_trades(tmp_path):
    path = tmp_path / "paper_portfolio.json"
    buy_paper_position("NVDA", 100.0, 2, path=path)

    portfolio = reset_paper_portfolio(50000.0, path)

    assert portfolio == {"cash": 50000.0, "positions": {}, "trades": []}


def test_buy_paper_position_updates_cash_position_and_trade(tmp_path):
    path = tmp_path / "paper_portfolio.json"

    portfolio = buy_paper_position(" nvda ", 100.0, 3, "us", path)

    assert portfolio["cash"] == 99700.0
    assert portfolio["positions"]["NVDA"]["quantity"] == 3
    assert portfolio["positions"]["NVDA"]["avg_cost"] == 100.0
    assert portfolio["trades"][0]["action"] == "BUY"
    assert portfolio["trades"][0]["amount"] == 300.0


def test_buy_paper_position_rejects_insufficient_cash(tmp_path):
    path = tmp_path / "paper_portfolio.json"
    reset_paper_portfolio(100.0, path)

    with pytest.raises(ValueError, match="Not enough paper cash"):
        buy_paper_position("NVDA", 101.0, 1, path=path)


@pytest.mark.parametrize("price", [0, -1])
def test_buy_paper_position_rejects_invalid_price(tmp_path, price):
    with pytest.raises(ValueError, match="Price must be greater than 0"):
        buy_paper_position("NVDA", price, 1, path=tmp_path / "paper_portfolio.json")


@pytest.mark.parametrize("quantity", [0, -1])
def test_buy_paper_position_rejects_invalid_quantity(tmp_path, quantity):
    with pytest.raises(ValueError, match="Quantity must be greater than 0"):
        buy_paper_position("NVDA", 100.0, quantity, path=tmp_path / "paper_portfolio.json")


def test_sell_paper_position_updates_cash_and_quantity(tmp_path):
    path = tmp_path / "paper_portfolio.json"
    buy_paper_position("NVDA", 100.0, 3, path=path)

    portfolio = sell_paper_position("NVDA", 110.0, 1, path=path)

    assert portfolio["cash"] == 99810.0
    assert portfolio["positions"]["NVDA"]["quantity"] == 2
    assert portfolio["trades"][-1]["action"] == "SELL"


def test_sell_paper_position_rejects_excess_quantity(tmp_path):
    path = tmp_path / "paper_portfolio.json"
    buy_paper_position("NVDA", 100.0, 1, path=path)

    with pytest.raises(ValueError, match="Not enough paper position"):
        sell_paper_position("NVDA", 100.0, 2, path=path)


def test_sell_paper_position_removes_zero_quantity_position(tmp_path):
    path = tmp_path / "paper_portfolio.json"
    buy_paper_position("NVDA", 100.0, 1, path=path)

    portfolio = sell_paper_position("NVDA", 100.0, 1, path=path)

    assert "NVDA" not in portfolio["positions"]


def test_save_paper_portfolio_rejects_negative_position_quantity(tmp_path):
    portfolio = {
        "cash": 100000.0,
        "positions": {"NVDA": {"symbol": "NVDA", "market": "us", "quantity": -1, "avg_cost": 100.0}},
        "trades": [],
    }

    with pytest.raises(ValueError, match="quantity cannot be negative"):
        paper_portfolio.save_paper_portfolio(portfolio, tmp_path / "paper_portfolio.json")


def test_multiple_buys_update_average_cost(tmp_path):
    path = tmp_path / "paper_portfolio.json"
    buy_paper_position("NVDA", 100.0, 1, path=path)

    portfolio = buy_paper_position("NVDA", 200.0, 3, path=path)

    assert portfolio["positions"]["NVDA"]["quantity"] == 4
    assert portfolio["positions"]["NVDA"]["avg_cost"] == 175.0


def test_calculate_portfolio_summary_uses_latest_prices(tmp_path):
    path = tmp_path / "paper_portfolio.json"
    portfolio = buy_paper_position("NVDA", 100.0, 2, path=path)

    summary = calculate_portfolio_summary(portfolio, {"NVDA": 120.0})

    assert summary["cash"] == 99800.0
    assert summary["positions_value"] == 240.0
    assert summary["total_assets"] == 100040.0
    assert summary["unrealized_pnl"] == 40.0
    assert summary["positions"][0]["unrealized_pnl_pct"] == 0.2


def test_get_trade_history_returns_trades(tmp_path):
    path = tmp_path / "paper_portfolio.json"
    portfolio = buy_paper_position("NVDA", 100.0, 1, path=path)

    trades = get_trade_history(portfolio)

    assert len(trades) == 1
    assert trades[0]["symbol"] == "NVDA"


def test_portfolio_file_does_not_save_secret_fields(tmp_path):
    path = tmp_path / "paper_portfolio.json"
    buy_paper_position("NVDA", 100.0, 1, path=path)

    text = path.read_text(encoding="utf-8").lower()

    assert "api_key" not in text
    assert "secret" not in text
    assert "password" not in text
    assert "token" not in text


def test_paper_trading_module_does_not_import_broker_clients():
    source = Path(paper_portfolio.__file__).read_text(encoding="utf-8").lower()

    assert "yfinance" not in source
    assert "akshare" not in source
    assert "alpaca" not in source
    assert "robinhood" not in source
    assert "ibkr" not in source
    assert "place_order" not in source
    assert "submit_order" not in source
