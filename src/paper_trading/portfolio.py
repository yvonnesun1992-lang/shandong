from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PAPER_PORTFOLIO_PATH = PROJECT_ROOT / "config" / "paper_portfolio.json"


def _empty_portfolio(initial_cash: float = 100000.0) -> dict[str, Any]:
    if initial_cash < 0:
        raise ValueError("Initial cash cannot be negative.")
    return {"cash": float(initial_cash), "positions": {}, "trades": []}


def _normalize_symbol(symbol: str, market: str) -> str:
    clean_symbol = str(symbol).strip()
    if not clean_symbol:
        raise ValueError("Symbol cannot be empty.")
    if market.lower() == "us":
        return clean_symbol.upper()
    return clean_symbol


def _validate_price_quantity(price: float, quantity: int) -> tuple[float, int]:
    trade_price = float(price)
    trade_quantity = int(quantity)
    if trade_price <= 0:
        raise ValueError("Price must be greater than 0.")
    if trade_quantity <= 0:
        raise ValueError("Quantity must be greater than 0.")
    return trade_price, trade_quantity


def _validate_portfolio(portfolio: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(portfolio, dict):
        raise ValueError("Paper portfolio must be a JSON object.")
    cash = float(portfolio.get("cash", 0.0))
    if cash < 0:
        raise ValueError("Paper portfolio cash cannot be negative.")
    positions = portfolio.get("positions", {})
    trades = portfolio.get("trades", [])
    if not isinstance(positions, dict):
        raise ValueError("Paper portfolio positions must be an object.")
    if not isinstance(trades, list):
        raise ValueError("Paper portfolio trades must be a list.")
    for symbol, position in positions.items():
        if not isinstance(position, dict):
            raise ValueError(f"Paper position for {symbol} must be an object.")
        quantity = int(position.get("quantity", 0))
        avg_cost = float(position.get("avg_cost", 0.0))
        if quantity < 0:
            raise ValueError(f"Paper position quantity cannot be negative for {symbol}.")
        if avg_cost <= 0:
            raise ValueError(f"Paper position average cost must be greater than 0 for {symbol}.")
    return {"cash": cash, "positions": positions, "trades": trades}


def _write_portfolio(portfolio: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(portfolio, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _ensure_portfolio_file(path: Path) -> None:
    if not path.exists():
        _write_portfolio(_empty_portfolio(), path)


def load_paper_portfolio(path: str | Path = DEFAULT_PAPER_PORTFOLIO_PATH) -> dict[str, Any]:
    portfolio_path = Path(path)
    _ensure_portfolio_file(portfolio_path)
    try:
        data = json.loads(portfolio_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid paper portfolio JSON in {portfolio_path}: {error}") from error
    return _validate_portfolio(data)


def save_paper_portfolio(portfolio: dict[str, Any], path: str | Path = DEFAULT_PAPER_PORTFOLIO_PATH) -> None:
    clean_portfolio = _validate_portfolio(portfolio)
    _write_portfolio(clean_portfolio, Path(path))


def reset_paper_portfolio(
    initial_cash: float = 100000.0,
    path: str | Path = DEFAULT_PAPER_PORTFOLIO_PATH,
) -> dict[str, Any]:
    portfolio = _empty_portfolio(initial_cash)
    save_paper_portfolio(portfolio, path)
    return portfolio


def _trade_record(action: str, symbol: str, market: str, price: float, quantity: int) -> dict[str, Any]:
    amount = price * quantity
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "symbol": symbol,
        "market": market.lower(),
        "price": price,
        "quantity": quantity,
        "amount": amount,
    }


def buy_paper_position(
    symbol: str,
    price: float,
    quantity: int,
    market: str = "us",
    path: str | Path = DEFAULT_PAPER_PORTFOLIO_PATH,
) -> dict[str, Any]:
    clean_market = market.lower()
    clean_symbol = _normalize_symbol(symbol, clean_market)
    trade_price, trade_quantity = _validate_price_quantity(price, quantity)
    amount = trade_price * trade_quantity
    portfolio = load_paper_portfolio(path)
    if portfolio["cash"] < amount:
        raise ValueError("Not enough paper cash for this buy order.")

    positions = portfolio["positions"]
    current = positions.get(clean_symbol)
    if current:
        old_quantity = int(current["quantity"])
        old_cost = float(current["avg_cost"])
        new_quantity = old_quantity + trade_quantity
        new_avg_cost = ((old_quantity * old_cost) + amount) / new_quantity
    else:
        new_quantity = trade_quantity
        new_avg_cost = trade_price

    positions[clean_symbol] = {
        "symbol": clean_symbol,
        "market": clean_market,
        "quantity": new_quantity,
        "avg_cost": new_avg_cost,
    }
    portfolio["cash"] = portfolio["cash"] - amount
    portfolio["trades"].append(_trade_record("BUY", clean_symbol, clean_market, trade_price, trade_quantity))
    save_paper_portfolio(portfolio, path)
    return portfolio


def sell_paper_position(
    symbol: str,
    price: float,
    quantity: int,
    market: str = "us",
    path: str | Path = DEFAULT_PAPER_PORTFOLIO_PATH,
) -> dict[str, Any]:
    clean_market = market.lower()
    clean_symbol = _normalize_symbol(symbol, clean_market)
    trade_price, trade_quantity = _validate_price_quantity(price, quantity)
    portfolio = load_paper_portfolio(path)
    positions = portfolio["positions"]
    current = positions.get(clean_symbol)
    if not current:
        raise ValueError(f"No paper position found for {clean_symbol}.")

    current_quantity = int(current["quantity"])
    if current_quantity < trade_quantity:
        raise ValueError("Not enough paper position quantity to sell.")

    remaining_quantity = current_quantity - trade_quantity
    if remaining_quantity == 0:
        del positions[clean_symbol]
    else:
        current["quantity"] = remaining_quantity

    amount = trade_price * trade_quantity
    portfolio["cash"] = portfolio["cash"] + amount
    portfolio["trades"].append(_trade_record("SELL", clean_symbol, clean_market, trade_price, trade_quantity))
    save_paper_portfolio(portfolio, path)
    return portfolio


def calculate_portfolio_summary(
    portfolio: dict[str, Any],
    latest_prices: dict[str, float] | None = None,
) -> dict[str, Any]:
    clean_portfolio = _validate_portfolio(portfolio)
    prices = latest_prices or {}
    positions = clean_portfolio["positions"]
    position_rows = []
    positions_value = 0.0
    total_cost = 0.0

    for symbol, position in positions.items():
        quantity = int(position["quantity"])
        avg_cost = float(position["avg_cost"])
        latest_price = float(prices.get(symbol, avg_cost))
        market_value = latest_price * quantity
        cost_value = avg_cost * quantity
        unrealized_pnl = market_value - cost_value
        unrealized_pnl_pct = unrealized_pnl / cost_value if cost_value else 0.0
        positions_value += market_value
        total_cost += cost_value
        position_rows.append(
            {
                "symbol": symbol,
                "market": position.get("market", ""),
                "quantity": quantity,
                "avg_cost": avg_cost,
                "latest_price": latest_price,
                "market_value": market_value,
                "unrealized_pnl": unrealized_pnl,
                "unrealized_pnl_pct": unrealized_pnl_pct,
            }
        )

    cash = clean_portfolio["cash"]
    total_assets = cash + positions_value
    unrealized_pnl = positions_value - total_cost
    return {
        "cash": cash,
        "positions_value": positions_value,
        "total_assets": total_assets,
        "unrealized_pnl": unrealized_pnl,
        "position_count": len(position_rows),
        "positions": position_rows,
    }


def get_trade_history(portfolio: dict[str, Any]) -> list[dict[str, Any]]:
    clean_portfolio = _validate_portfolio(portfolio)
    return list(clean_portfolio["trades"])
