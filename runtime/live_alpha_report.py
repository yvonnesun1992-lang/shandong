from __future__ import annotations

from pathlib import Path

from runtime.live_paper_alpha_runner import run_live_paper_alpha_staging


def generate_live_alpha_report(mode: str = "mock_live", ticks: int = 100, output_path: str | Path = "reports/v5_7_live_alpha_signal_integration_report.md") -> dict:
    summary = run_live_paper_alpha_staging(mode=mode, max_ticks=ticks)
    verdict = _verdict(summary)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_render_report(summary, verdict), encoding="utf-8")
    return {"path": path.as_posix(), "verdict": verdict, "summary": summary}


def _verdict(summary: dict) -> str:
    if not summary.get("success") or summary.get("health_status") == "FAILED":
        return "FAIL"
    if summary.get("warnings"):
        return "WARNING"
    return "PASS"


def _render_report(summary: dict, verdict: str) -> str:
    return f"""# V5.7 Live Alpha Signal Integration Report

## Live Alpha Run
- Live data mode: {summary.get("mode")}
- Requested mode: {summary.get("requested_mode")}
- Symbols: {', '.join(summary.get("symbols", []))}
- Feature buffer readiness: {summary.get("buffer_status", {}).get("ready", {})}
- Signals generated: {summary.get("signals_generated")}
- BUY count: {summary.get("buy_signals")}
- SELL count: {summary.get("sell_signals")}
- HOLD count: {summary.get("hold_signals")}
- Orders submitted: {summary.get("orders_submitted")}
- Orders filled: {summary.get("orders_filled")}
- Final equity: {summary.get("final_equity")}
- Health status: {summary.get("health_status")}

## Warnings
{_render_list(summary.get("warnings", []))}

## Errors
{_render_list(summary.get("errors", []))}

## Safety Boundary
- Current stage uses market data or mock live data with simulated paper trading
- Current stage is driven by V5 alpha signal adapter
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
