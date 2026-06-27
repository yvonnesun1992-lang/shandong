from __future__ import annotations

import json
from pathlib import Path

from config.v5_live_data_config import get_live_data_poll_interval, get_live_data_status
from runtime.event_bus import EventBus
from runtime.live_alpha_signal_adapter import LiveAlphaSignalAdapter
from runtime.live_data_normalizer import normalize_live_ticks
from runtime.live_feature_buffer import LiveFeatureBuffer
from runtime.live_market_data import YFinancePollingAdapter, build_live_market_data_adapter
from runtime.risk_gate import RiskGate
from runtime.state_checkpoint import StateCheckpoint
from trading.paper_broker import PaperBroker
from trading.risk_limits import RiskLimits
from trading.signal_to_order import SignalToOrderConverter


def build_live_alpha_paper_engine(mode: str = "mock_live", symbols: list[str] | None = None) -> dict:
    status = get_live_data_status()
    selected_symbols = symbols or status["symbols"]
    return {
        "adapter": build_live_market_data_adapter(mode, selected_symbols),
        "feature_buffer": LiveFeatureBuffer(min_window=60, max_window=300),
        "signal_adapter": LiveAlphaSignalAdapter(min_window=60),
        "broker": PaperBroker(initial_cash=100_000.0),
        "risk_gate": RiskGate(RiskLimits(max_drawdown=0.10), EventBus()),
        "converter": SignalToOrderConverter(),
        "symbols": selected_symbols,
        "mode": mode,
    }


def run_live_paper_alpha_once(mode: str = "mock_live", symbols: list[str] | None = None) -> dict:
    return run_live_paper_alpha_staging(mode=mode, max_ticks=1, symbols=symbols, dry_run_once=True)


def run_live_paper_alpha_staging(
    mode: str = "mock_live",
    max_ticks: int = 100,
    symbols: list[str] | None = None,
    dry_run_once: bool = False,
    log_path: str | Path = "logs/runtime.jsonl",
    checkpoint_path: str | Path = "data/runtime_state_checkpoint.json",
) -> dict:
    engine = build_live_alpha_paper_engine(mode=mode, symbols=symbols)
    adapter = engine["adapter"]
    buffer: LiveFeatureBuffer = engine["feature_buffer"]
    signal_adapter: LiveAlphaSignalAdapter = engine["signal_adapter"]
    broker: PaperBroker = engine["broker"]
    risk_gate: RiskGate = engine["risk_gate"]
    converter: SignalToOrderConverter = engine["converter"]
    iterations = 1 if dry_run_once else max(1, int(max_ticks))
    warnings: list[str] = []
    errors: list[str] = []
    latest_signals: list[dict] = []
    ticks_processed = 0
    orders_submitted = 0
    orders_filled = 0
    hold_signals = 0
    buy_signals = 0
    sell_signals = 0
    for _ in range(iterations):
        try:
            raw_ticks = adapter.get_latest_ticks()
            normalized = normalize_live_ticks(raw_ticks)
            if isinstance(adapter, YFinancePollingAdapter) and adapter.warning and adapter.warning not in warnings:
                warnings.append(adapter.warning)
            for invalid in normalized["invalid_ticks"]:
                warnings.append(f"invalid tick skipped: {invalid.get('symbol', '')}".strip())
            for tick in normalized["valid_ticks"]:
                ticks_processed += 1
                buffer.append_tick(tick)
                broker.account.update_market_price(tick["symbol"], tick["close"])
                signal = signal_adapter.generate_signal(tick["symbol"], buffer.get_symbol_frame(tick["symbol"]))
                latest_signals.append(signal)
                if signal.get("warning"):
                    warning = str(signal["warning"])
                    if warning not in warnings:
                        warnings.append(warning)
                action = str(signal.get("action", "HOLD")).upper()
                if action == "HOLD":
                    hold_signals += 1
                elif action == "BUY":
                    buy_signals += 1
                elif action == "SELL":
                    sell_signals += 1
                order = converter.convert(signal, broker.account, float(tick["close"]))
                if order is not None:
                    decision = risk_gate.pre_trade_check(order, broker.account, float(tick["close"]))
                    if decision.get("approved"):
                        orders_submitted += 1
                        execution = broker.execute_order(order, market_price=float(tick["close"]))
                        if execution.status == "FILLED":
                            orders_filled += 1
                            _append_log(log_path, {"event_type": "ORDER_FILLED", "symbol": execution.symbol, "side": execution.side, "timestamp": signal["timestamp"]})
                    else:
                        warnings.append("risk gate rejected paper order")
                _append_log(log_path, {"event_type": "SIGNAL_GENERATED", "symbol": signal["symbol"], "action": signal["action"], "timestamp": signal["timestamp"], "source": "v5_alpha"})
        except Exception as exc:
            errors.append(type(exc).__name__)
    summary = broker.get_account_summary()
    result = {
        "success": not errors,
        "mode": "mock_live" if warnings and mode == "yfinance_polling" else mode,
        "requested_mode": mode,
        "poll_interval_seconds": get_live_data_poll_interval(),
        "ticks_processed": ticks_processed,
        "signals_generated": len(latest_signals),
        "orders_submitted": orders_submitted,
        "orders_filled": orders_filled,
        "hold_signals": hold_signals,
        "buy_signals": buy_signals,
        "sell_signals": sell_signals,
        "symbols": engine["symbols"],
        "latest_signals": latest_signals[-20:],
        "buffer_status": buffer.status(),
        "paper_trading": True,
        "real_trading": False,
        "broker_connected": False,
        "real_money_enabled": False,
        "final_equity": float(summary["equity"]),
        "portfolio": summary,
        "health_status": "HEALTHY" if ticks_processed and not errors else "DEGRADED" if ticks_processed else "FAILED",
        "warnings": _dedupe(warnings),
        "errors": errors,
    }
    StateCheckpoint(path=checkpoint_path, interval_seconds=0).save(
        {
            "portfolio": {"cash": summary["cash"], "equity": summary["equity"], "realized_pnl": summary["realized_pnl"]},
            "positions": summary["positions"],
            "pnl": {"equity_curve": [summary["equity"]], "realized_pnl": summary["realized_pnl"], "unrealized_pnl": summary["unrealized_pnl"]},
            "mode": "LIVE_ALPHA_PAPER",
            "health": {"status": result["health_status"], "errors": len(errors)},
            "risk": {"kill_switch_active": False},
            "latest_signals": result["latest_signals"],
        },
        force=True,
    )
    return result


def _append_log(path: str | Path, payload: dict) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    safe = dict(payload)
    safe["paper_trading"] = True
    safe["real_trading"] = False
    safe["broker_connected"] = False
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(safe, ensure_ascii=False, default=str) + "\n")


def _dedupe(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result
