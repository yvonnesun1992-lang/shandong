from __future__ import annotations

from pathlib import Path

from strategy_center.strategy_center_orchestrator import build_strategy_center_dashboard, summarize_strategy_center


REPORT_PATH = Path("reports/v5_46_strategy_center_report.md")


def generate_strategy_center_report(path: str | Path = REPORT_PATH) -> dict:
    dashboard = build_strategy_center_dashboard()
    summary = summarize_strategy_center(dashboard)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# V5.46 Strategy Center Report",
        "",
        "Mode: strategy_center_only",
        "Current capability: backtest and paper trading entry points only.",
        "No broker connection. No sandbox API. No secret/account/balance/position read. No order submission. No real money.",
        "",
        f"Catalog count: {summary['catalog_count']}",
        f"Category count: {summary['category_count']}",
        f"Recommended strategies: {', '.join(item['display_name'] for item in dashboard['recommended_strategies'])}",
        "",
        "Search/filter capability: keyword search plus risk, market, type, user, backtest, paper-trading, and category filters.",
        "Strategy cards: include risk level, suitable market, backtest preview, and paper trading action.",
        "Strategy detail model: includes introduction, fit, unsuitable users, logic, backtest, risk, recent records, actions, and collapsed advanced code entry.",
        "Education copy: explains backtest, paper trading, drawdown, win rate, Sharpe, and why real trading is disabled.",
        "Missing future requirements: connect real provider only after separate approvals, credential vault, sandbox read-only gates, and explicit production safety review.",
        "",
        f"Verdict: {summary['verdict']}",
    ]
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "path": target.as_posix(),
        "summary": summary,
        "strategy_center_only": True,
        "localhost_only": True,
        "paper_trading": True,
        "real_trading_enabled": False,
    }
