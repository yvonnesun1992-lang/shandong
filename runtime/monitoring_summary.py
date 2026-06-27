from __future__ import annotations

from runtime.monitoring_data_reader import MonitoringDataReader, sanitize_payload


def build_monitoring_summary(reader: MonitoringDataReader | None = None) -> dict:
    reader = reader or MonitoringDataReader()
    checkpoint = reader.read_latest_checkpoint()
    soak_report = reader.read_soak_report()
    logs = reader.get_recent_events(100)
    errors = reader.get_error_events(100)
    trades = reader.get_trade_events(100)
    signals = reader.get_signal_events(100)
    portfolio = checkpoint.get("portfolio", {}) if checkpoint.get("available") else {}
    pnl = checkpoint.get("pnl", {}) if checkpoint.get("available") else {}
    health = checkpoint.get("health", {}) if checkpoint.get("available") else {}
    risk = checkpoint.get("risk", {}) if checkpoint.get("available") else {}
    positions = checkpoint.get("positions", portfolio.get("positions", {})) if checkpoint.get("available") else {}
    warnings = []
    warnings.extend(checkpoint.get("warnings", []))
    warnings.extend(soak_report.get("warnings", []))
    status = str(health.get("status") or ("UNKNOWN" if warnings else "HEALTHY")).upper()
    mode = str(checkpoint.get("mode") or "UNKNOWN").upper()
    summary = {
        "status": status if status in {"HEALTHY", "DEGRADED", "FAILED", "UNKNOWN"} else "UNKNOWN",
        "mode": mode if mode in {"NORMAL", "DEGRADED", "SAFE_MODE", "UNKNOWN"} else "UNKNOWN",
        "paper_trading": True,
        "real_trading": False,
        "broker_connected": False,
        "latest_equity": float(portfolio.get("equity", pnl.get("equity", 0.0)) or 0.0),
        "cash": float(portfolio.get("cash", 0.0) or 0.0),
        "position_value": float(portfolio.get("position_value", 0.0) or 0.0),
        "open_positions": _position_list(positions),
        "recent_signals": signals,
        "recent_trades": trades,
        "recent_errors": errors,
        "risk": risk,
        "health": health,
        "last_checkpoint_at": str(checkpoint.get("checkpoint_saved_at", "")),
        "last_log_at": _last_log_at(logs),
        "soak_report": soak_report,
        "warnings": warnings,
    }
    return sanitize_payload(summary)


def _position_list(positions: dict) -> list[dict]:
    return [
        {"symbol": str(symbol), **(details if isinstance(details, dict) else {"quantity": details})}
        for symbol, details in sorted((positions or {}).items())
    ]


def _last_log_at(logs: list[dict]) -> str:
    if not logs:
        return ""
    return str(logs[-1].get("timestamp", ""))
