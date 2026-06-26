from __future__ import annotations

import pandas as pd


def test_buy_fill_reduces_cash_and_increases_position():
    from trading.order import Order
    from trading.paper_broker import PaperBroker

    broker = PaperBroker(initial_cash=10_000)
    order = Order(symbol="AAPL", side="BUY", quantity=10, order_type="MARKET")
    result = broker.execute_order(order, market_price=100)

    assert result.status == "FILLED"
    assert broker.account.cash < 10_000
    assert broker.get_positions()["AAPL"]["quantity"] == 10


def test_sell_fill_increases_cash_and_reduces_position():
    from trading.order import Order
    from trading.paper_broker import PaperBroker

    broker = PaperBroker(initial_cash=10_000)
    broker.execute_order(Order(symbol="AAPL", side="BUY", quantity=10, order_type="MARKET"), market_price=100)
    cash_after_buy = broker.account.cash
    result = broker.execute_order(Order(symbol="AAPL", side="SELL", quantity=4, order_type="MARKET"), market_price=110)

    assert result.status == "FILLED"
    assert broker.account.cash > cash_after_buy
    assert broker.get_positions()["AAPL"]["quantity"] == 6


def test_buy_rejected_when_cash_insufficient():
    from trading.order import Order
    from trading.paper_broker import PaperBroker

    broker = PaperBroker(initial_cash=100)
    result = broker.execute_order(Order(symbol="AAPL", side="BUY", quantity=10, order_type="MARKET"), market_price=100)

    assert result.status == "REJECTED"
    assert result.reason == "INSUFFICIENT_CASH"
    assert broker.account.cash == 100


def test_sell_rejected_when_position_insufficient():
    from trading.order import Order
    from trading.paper_broker import PaperBroker

    broker = PaperBroker(initial_cash=10_000)
    result = broker.execute_order(Order(symbol="AAPL", side="SELL", quantity=1, order_type="MARKET"), market_price=100)

    assert result.status == "REJECTED"
    assert result.reason == "INSUFFICIENT_POSITION"
    assert broker.get_positions() == {}


def test_fee_and_slippage_are_calculated_for_buy_and_sell():
    from trading.order import Order
    from trading.paper_broker import PaperBroker

    broker = PaperBroker(initial_cash=10_000, fee_rate=0.001, slippage_rate=0.0005)
    buy = broker.execute_order(Order(symbol="AAPL", side="BUY", quantity=10, order_type="MARKET"), market_price=100)
    sell = broker.execute_order(Order(symbol="AAPL", side="SELL", quantity=5, order_type="MARKET"), market_price=100)

    assert round(buy.execution_price, 4) == 100.05
    assert round(buy.fee, 4) == 1.0005
    assert round(buy.cash_effect, 4) == -1001.5005
    assert round(sell.execution_price, 4) == 99.95
    assert round(sell.fee, 4) == 0.4998
    assert round(sell.cash_effect, 4) == 499.2502


def test_trade_history_records_all_filled_trades():
    from trading.order import Order
    from trading.paper_broker import PaperBroker

    broker = PaperBroker(initial_cash=10_000)
    broker.execute_order(Order(symbol="AAPL", side="BUY", quantity=10, order_type="MARKET"), market_price=100)
    broker.execute_order(Order(symbol="AAPL", side="SELL", quantity=5, order_type="MARKET"), market_price=101)

    history = broker.get_trade_history()
    assert len(history) == 2
    assert all(trade["status"] == "FILLED" for trade in history)


def test_equity_uses_cash_plus_marked_positions():
    from trading.order import Order
    from trading.paper_broker import PaperBroker

    broker = PaperBroker(initial_cash=10_000)
    broker.execute_order(Order(symbol="AAPL", side="BUY", quantity=10, order_type="MARKET"), market_price=100)
    broker.account.update_market_price("AAPL", 120)
    summary = broker.get_account_summary()

    assert summary["cash"] < 10_000
    assert round(summary["position_value"], 2) == 1200
    assert round(summary["equity"], 2) == round(summary["cash"] + 1200, 2)
    assert summary["unrealized_pnl"] > 0


def test_signal_to_order_respects_hold_and_risk_sizing():
    from trading.paper_account import PaperAccount
    from trading.signal_to_order import SignalToOrderConverter

    account = PaperAccount(initial_cash=100_000)
    converter = SignalToOrderConverter(max_order_pct=0.10, max_asset_pct=0.20)

    hold = converter.convert({"symbol": "AAPL", "action": "HOLD", "strength": 0.5}, account, market_price=100)
    buy = converter.convert({"symbol": "AAPL", "action": "BUY", "strength": 1.0}, account, market_price=100)

    assert hold is None
    assert buy is not None
    assert buy.side == "BUY"
    assert buy.quantity == 100


def test_risk_limit_blocks_oversized_order():
    from trading.order import Order
    from trading.paper_account import PaperAccount
    from trading.risk_limits import RiskLimits

    account = PaperAccount(initial_cash=100_000)
    risk = RiskLimits(max_order_value=0.10, max_position_per_asset=0.20)
    order = Order(symbol="AAPL", side="BUY", quantity=200, order_type="MARKET")

    decision = risk.validate_order(order, account, market_price=100)

    assert decision["approved"] is False
    assert decision["reason"] == "MAX_ORDER_VALUE"


def test_paper_trading_runner_completes_closed_loop():
    from trading.paper_trading_runner import PaperTradingRunner

    market_data = _market_data()

    def signal_fn(row, account):
        return {
            "symbol": "AAPL",
            "action": "BUY" if row["close"] > 100 else "HOLD",
            "strength": 0.5,
            "timestamp": row["datetime"],
        }

    runner = PaperTradingRunner(initial_cash=50_000)
    result = runner.run(market_data, signal_fn=signal_fn)

    assert len(result["equity_curve"]) == len(market_data)
    assert result["final_account_summary"]["equity"] > 0
    assert result["performance_metrics"]["number_of_trades"] >= 1
    assert result["safety"]["broker_connection"] is False
    assert result["safety"]["real_trading"] is False


def _market_data() -> pd.DataFrame:
    dates = pd.date_range("2026-01-01", periods=30, freq="D")
    close = [100 + idx for idx in range(len(dates))]
    return pd.DataFrame(
        {
            "datetime": dates,
            "open": close,
            "high": [value + 1 for value in close],
            "low": [value - 1 for value in close],
            "close": close,
            "volume": [1000 + idx for idx in range(len(dates))],
        }
    )
