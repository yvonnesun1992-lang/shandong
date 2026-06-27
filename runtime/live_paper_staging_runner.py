from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from config.v5_live_data_config import get_live_data_poll_interval, get_live_data_status
from runtime.live_data_normalizer import normalize_live_ticks
from runtime.live_market_data import MockLiveMarketDataAdapter, YFinancePollingAdapter, build_live_market_data_adapter
from runtime.state_checkpoint import StateCheckpoint
from trading.order import Order
from trading.paper_broker import PaperBroker


def build_live_paper_engine(mode: str = "mock_live", symbols: list[str] | None = None) -> dict:
    status = get_live_data_status()
    selected_symbols = symbols or status["symbols"]
    adapter = build_live_market_data_adapter(mode, selected_symbols)
    broker = PaperBroker(initial_cash=100_000.0)
    return {"adapter": adapter, "broker": broker, "symbols": selected_symbols, "mode": mode}


def run_live_paper_once(mode: str = "mock_live", symbols: list[str] | None = None, broker: PaperBroker | None = None) -> dict:
    engine = build_live_paper_engine(mode=mode, symbols=symbols)
    adapter = engine["adapter"]
    broker = broker or engine["broker"]
    raw_ticks = adapter.get_latest_ticks()
    normalized = normalize_live_ticks(raw_ticks)
    warnings = list(normalized.get("warnings", []))
    if isinstance(adapter, YFinancePollingAdapter) and adapter.warning:
        warnings.append(adapter.warning)
    fills = []
    for tick in normalized["valid_ticks"]:
        broker.account.update_market_price(tick["symbol"], tick["close"])
        order = _paper_observation_order(tick)
        if order:
            result = broker.execute_order(order, market_price=tick["close"])
            fills.append(result.as_dict())
    summary = broker.get_account_summary()
    return {
        "success": True,
        "mode": "mock_live" if warnings and mode == "yfinance_polling" else mode,
        "requested_mode": mode,
        "ticks_processed": len(normalized["valid_ticks"]),
        "symbols": engine["symbols"],
        "latest_tick": normalized["valid_ticks"][-1] if normalized["valid_ticks"] else {},
        "paper_trading": True,
        "real_trading": False,
        "broker_connected": False,
        "real_money_enabled": False,
        "final_equity": float(summary["equity"]),
        "portfolio": summary,
        "fills": fills,
        "health_status": "HEALTHY" if normalized["valid_ticks"] else "DEGRADED",
        "risk_kill_switch_triggered": False,
        "warnings": warnings,
        "errors": [],
    }


def run_live_paper_staging(
    mode: str = "mock_live",
    max_ticks: int = 20,
    symbols: list[str] | None = None,
    dry_run_once: bool = False,
    log_path: str | Path = "logs/runtime.jsonl",
    checkpoint_path: str | Path = "data/runtime_state_checkpoint.json",
) -> dict:
    status = get_live_data_status()
    selected_symbols = symbols or status["symbols"]
    adapter = build_live_market_data_adapter(mode, selected_symbols)
    broker = PaperBroker(initial_cash=100_000.0)
    poll_interval = get_live_data_poll_interval()
    target_iterations = 1 if dry_run_once else max(1, int(max_ticks))
    all_ticks = []
    all_fills = []
    warnings = []
    errors = []
    for _ in range(target_iterations):
        try:
            raw_ticks = adapter.get_latest_ticks()
            normalized = normalize_live_ticks(raw_ticks)
            if isinstance(adapter, YFinancePollingAdapter) and adapter.warning and adapter.warning not in warnings:
                warnings.append(adapter.warning)
            for tick in normalized["valid_ticks"]:
                broker.account.update_market_price(tick["symbol"], tick["close"])
                order = _paper_observation_order(tick)
                if order:
                    execution = broker.execute_order(order, market_price=tick["close"])
                    all_fills.append(execution.as_dict())
                all_ticks.append(tick)
                _append_log(log_path, {"event_type": "MARKET_TICK", "timestamp": tick["datetime"], "symbol": tick["symbol"], "price": tick["close"], "source": tick["source"]})
        except Exception as exc:
            errors.append(type(exc).__name__)
    summary = broker.get_account_summary()
    latest_tick = all_ticks[-1] if all_ticks else {}
    result = {
        "success": not errors,
        "mode": "mock_live" if warnings and mode == "yfinance_polling" else mode,
        "requested_mode": mode,
        "poll_interval_seconds": poll_interval,
        "ticks_processed": len(all_ticks),
        "symbols": selected_symbols,
        "latest_tick": latest_tick,
        "paper_trading": True,
        "real_trading": False,
        "broker_connected": False,
        "real_money_enabled": False,
        "final_equity": float(summary["equity"]),
        "portfolio": summary,
        "fills": all_fills[-20:],
        "health_status": "HEALTHY" if all_ticks and not errors else "DEGRADED" if all_ticks else "FAILED",
        "risk_kill_switch_triggered": False,
        "warnings": warnings,
        "errors": errors,
    }
    StateCheckpoint(path=checkpoint_path, interval_seconds=0).save(
        {
            "portfolio": {"cash": summary["cash"], "equity": summary["equity"], "realized_pnl": summary["realized_pnl"]},
            "positions": summary["positions"],
            "pnl": {"equity_curve": [summary["equity"]], "realized_pnl": summary["realized_pnl"], "unrealized_pnl": summary["unrealized_pnl"]},
            "mode": "LIVE_PAPER_STAGING",
            "health": {"status": result["health_status"], "errors": len(errors)},
            "risk": {"kill_switch_active": False},
        },
        force=True,
    )
    return result


def _paper_observation_order(tick: dict) -> Order | None:
    # Minimal paper-only heartbeat order for runtime plumbing; not a new strategy.
    if tick["symbol"] != "AAPL":
        return None
    return Order(symbol=tick["symbol"], side="BUY", quantity=1, price=tick["close"], timestamp=tick["datetime"])


def _append_log(path: str | Path, payload: dict) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    safe = dict(payload)
    safe["paper_trading"] = True
    safe["real_trading"] = False
    safe["broker_connected"] = False
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(_json_safe(safe), ensure_ascii=False) + "\n")


def _json_safe(value):
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)
