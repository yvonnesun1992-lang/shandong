from __future__ import annotations

from pathlib import Path

from config.v5_live_data_config import get_live_data_status
from runtime.live_paper_staging_runner import run_live_paper_staging


def generate_live_paper_report(mode: str = "mock_live", ticks: int = 20, output_path: str | Path = "reports/v5_6_live_paper_staging_report.md") -> dict:
    summary = run_live_paper_staging(mode=mode, max_ticks=ticks)
    status = get_live_data_status()
    verdict = _verdict(summary)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_render_report(status, summary, verdict), encoding="utf-8")
    return {"path": path.as_posix(), "verdict": verdict, "summary": summary}


def _verdict(summary: dict) -> str:
    if not summary.get("success") or summary.get("health_status") == "FAILED":
        return "FAIL"
    if summary.get("warnings"):
        return "WARNING"
    return "PASS"


def _render_report(status: dict, summary: dict, verdict: str) -> str:
    latest_tick = summary.get("latest_tick", {})
    return f"""# V5.6 Live Paper Trading Staging Report

## Live Data
- Live data mode: {summary.get("mode")}
- Requested mode: {summary.get("requested_mode")}
- Live data provider: {status.get("live_data_provider")}
- Symbols: {', '.join(summary.get("symbols", []))}
- Ticks processed: {summary.get("ticks_processed")}
- Latest tick timestamp: {latest_tick.get("datetime", '')}

## Paper Portfolio
- Final equity: {summary.get("final_equity")}
- Health status: {summary.get("health_status")}
- Risk kill switch triggered: {summary.get("risk_kill_switch_triggered")}

## Warnings
{_render_list(summary.get("warnings", []))}

## Errors
{_render_list(summary.get("errors", []))}

## Safety Boundary
- Current stage uses market data with simulated paper trading
- Current stage does not connect to a broker
- Current stage does not place real orders
- Current stage does not use real capital
- Current stage is not production live trading
- Current stage does not change alpha model or factor logic

## Final Verdict
{verdict}
"""


def _render_list(values: list) -> str:
    if not values:
        return "- None"
    return "\n".join(f"- {item}" for item in values)
