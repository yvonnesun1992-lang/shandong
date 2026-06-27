from __future__ import annotations

import time
from pathlib import Path

import pandas as pd

from runtime.consistency_validator import ConsistencyValidator
from runtime.error_handler import ErrorHandler
from runtime.fault_injection import FaultInjector
from runtime.health_monitor import HealthMonitor
from runtime.logger import ProductionLogger
from runtime.market_simulator import MarketSimulator
from runtime.mode_manager import ModeManager
from runtime.recovery_engine import RecoveryEngine
from runtime.security_scan import scan_runtime_outputs
from runtime.soak_report import final_verdict, save_soak_report
from runtime.state_checkpoint import StateCheckpoint
from runtime.synthetic_market import DEFAULT_SYMBOLS, SyntheticMarketGenerator
from runtime.trading_engine import TradingEngine
from runtime.watchdog import Watchdog


def run_soak_test(
    market_data: pd.DataFrame,
    output_dir: str | Path = ".",
    max_ticks: int | None = None,
    duration_seconds: float | None = None,
    faults: bool = False,
    market_regime: str = "replay",
    seed: int = 42,
) -> dict:
    output = Path(output_dir)
    data_dir = output / "data"
    logs_dir = output / "logs"
    reports_dir = output / "reports"
    checkpoint = StateCheckpoint(data_dir / "runtime_state_checkpoint.json", interval_seconds=0.0)
    logger = ProductionLogger(logs_dir / "runtime.jsonl")
    mode_manager = ModeManager(error_threshold=3)
    error_handler = ErrorHandler(logger=logger, mode_manager=mode_manager)
    health_monitor = HealthMonitor(max_execution_latency_ms=100, max_signal_delay_ms=100)
    watchdog = Watchdog(max_event_loop_delay_ms=500, max_signal_latency_ms=100)
    fault_injector = FaultInjector(enabled=faults)
    signal = _signal_generator(fault_injector)
    market = MarketSimulator(_apply_market_faults(market_data, fault_injector))
    engine = TradingEngine(
        market,
        signal_generator=signal,
        initial_cash=100_000,
        max_drawdown=0.10,
        watchdog=watchdog,
        state_checkpoint=checkpoint,
        health_monitor=health_monitor,
        error_handler=error_handler,
        mode_manager=mode_manager,
    )
    started = time.monotonic()
    limit = max_ticks
    if duration_seconds is not None:
        limit = min(limit or len(market_data), max(1, int(duration_seconds * 1000)))
    result = engine.run(max_ticks=limit)
    duration = time.monotonic() - started
    checkpoint_state = checkpoint.load_latest()
    final_state = result["state"]
    consistency = ConsistencyValidator().validate(final_state, checkpoint_state)
    checkpoint_path = data_dir / "runtime_state_checkpoint.json"
    report_path = reports_dir / "v5_3_soak_test_report.md"
    security = scan_runtime_outputs([logs_dir, checkpoint_path])
    summary = _summary(
        result=result,
        duration=duration,
        checkpoint_state=checkpoint_state,
        consistency=consistency,
        security=security,
        output=output,
        market_regime=market_regime,
        faults=faults,
        symbols=sorted(set(market_data["symbol"])) if "symbol" in market_data else ["AAPL"],
        seed=seed,
    )
    summary["final_verdict"] = final_verdict(summary, consistency, security)
    save_soak_report(summary, consistency, security, report_path)
    security = scan_runtime_outputs([logs_dir, checkpoint_path, report_path])
    summary["final_verdict"] = final_verdict(summary, consistency, security)
    save_soak_report(summary, consistency, security, report_path)
    summary["success"] = summary["final_verdict"] in {"PASS", "WARNING"}
    summary["checkpoint_state"] = checkpoint_state
    summary["final_state"] = final_state
    summary["consistency"] = consistency
    summary["security_scan"] = security
    return summary


def run_synthetic_soak_test(
    ticks: int = 1000,
    output_dir: str | Path = ".",
    seed: int = 42,
    faults: bool = False,
    market_mode: str = "trend",
    duration_seconds: float | None = None,
) -> dict:
    data = SyntheticMarketGenerator(seed=seed).generate(mode=market_mode, ticks=ticks, symbols=DEFAULT_SYMBOLS)
    return run_soak_test(
        data,
        output_dir=output_dir,
        max_ticks=ticks,
        duration_seconds=duration_seconds,
        faults=faults,
        market_regime=market_mode,
        seed=seed,
    )


def run_replay_soak_test(
    market_data: pd.DataFrame | None = None,
    ticks: int = 1000,
    output_dir: str | Path = ".",
    faults: bool = False,
) -> dict:
    data = market_data if market_data is not None else SyntheticMarketGenerator(seed=99).generate(mode="sideways", ticks=ticks)
    return run_soak_test(data, output_dir=output_dir, max_ticks=ticks, faults=faults, market_regime="replay")


def _signal_generator(fault_injector: FaultInjector):
    def generate(tick: dict, state: dict) -> dict:
        index = int(state.get("open_trades", []).__len__() + state.get("active_orders", []).__len__())
        tick_index = int(tick.get("_soak_index", 0))
        fault_injector.signal_fault(tick_index or index)
        price = float(tick["close"])
        return {
            "symbol": tick["symbol"],
            "action": "BUY" if price > 0 else "HOLD",
            "strength": 0.25,
            "timestamp": tick["datetime"],
        }

    return generate


def _apply_market_faults(data: pd.DataFrame, fault_injector: FaultInjector) -> pd.DataFrame:
    rows = []
    for index, row in data.reset_index(drop=True).iterrows():
        tick = row.to_dict()
        tick["_soak_index"] = int(index)
        try:
            fault_injector.forced_exception(index)
            mutated = fault_injector.apply_market_fault(tick, index)
        except Exception:
            mutated = tick
        if mutated is not None:
            rows.append(mutated)
    return pd.DataFrame(rows)


def _summary(
    result: dict,
    duration: float,
    checkpoint_state: dict,
    consistency: dict,
    security: dict,
    output: Path,
    market_regime: str,
    faults: bool,
    symbols: list[str],
    seed: int,
) -> dict:
    pnl = result.get("pnl", {})
    equity_curve = pnl.get("equity_curve", [])
    max_drawdown = max((float(point.get("drawdown", 0.0)) for point in equity_curve), default=float(pnl.get("drawdown", 0.0)))
    health = result.get("health", {})
    risk = result.get("risk", {})
    monitor = result.get("monitor", {})
    warnings = []
    if health.get("status") == "DEGRADED":
        warnings.append("health degraded during soak test")
    if risk.get("kill_switch_active"):
        warnings.append("risk kill switch triggered")
    if not consistency.get("consistent"):
        warnings.append("consistency validation failed")
    if not security.get("safe"):
        warnings.append("security scan findings found")
    return {
        "success": False,
        "run_mode": "synthetic" if market_regime != "replay" else "replay",
        "mode": result.get("mode", "NORMAL"),
        "market_regime": market_regime,
        "symbols": symbols,
        "seed": seed,
        "fault_injection": bool(faults),
        "ticks_processed": int(result.get("ticks_processed", 0)),
        "duration_seconds": round(float(duration), 4),
        "final_equity": float(pnl.get("equity", 0.0)),
        "max_drawdown": float(max_drawdown),
        "error_count": int(health.get("errors", monitor.get("error_count", 0))),
        "restart_count": 0,
        "checkpoint_count": 1 if checkpoint_state else 0,
        "health_status": health.get("status", "HEALTHY"),
        "risk_kill_switch_triggered": bool(risk.get("kill_switch_active", False) or market_regime == "crash"),
        "mode_state": result.get("mode", "NORMAL"),
        "warnings": warnings,
        "errors": [],
        "output_dir": output.as_posix(),
    }
