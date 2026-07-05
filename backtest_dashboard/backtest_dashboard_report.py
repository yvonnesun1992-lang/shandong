from __future__ import annotations

from pathlib import Path

from backtest_dashboard.backtest_dashboard_orchestrator import build_backtest_dashboard, summarize_backtest_dashboard


REPORT_PATH = Path("reports/v5_47_backtest_dashboard_report.md")


def generate_backtest_dashboard_report(strategy_id: str = "small_cap_momentum", path: str | Path = REPORT_PATH) -> dict:
    dashboard = build_backtest_dashboard(strategy_id)
    summary = summarize_backtest_dashboard(dashboard)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# V5.47 Backtest Dashboard Report",
        "",
        "Mode: backtest_dashboard_only",
        "Current capability: user-friendly backtest result dashboard with paper trading entry only.",
        "No broker connection. No sandbox API. No secret/account/balance/position read. No order submission. No real money.",
        "",
        f"Strategy: {summary['display_name']}",
        f"Conclusion: {summary['conclusion']}",
        f"Risk level: {summary['risk_level']}",
        f"Core metric cards: {summary['core_metric_count']}",
        f"Advanced metric cards: {summary['advanced_metric_count']} (collapsed by default)",
        f"Chart models: {summary['chart_count']}",
        f"Action buttons: {summary['action_count']}",
        "",
        "Result model summary: metadata, core metrics, and advanced metrics are assembled from local placeholder data.",
        "Conclusion engine: explains whether the strategy beat the benchmark, whether drawdown is acceptable, and next action.",
        "Risk analysis: classifies low / medium / high risk from max drawdown.",
        "Action panel: rebacktest, change strategy, paper trading, export report, and attribution entries; real trading is hidden.",
        "Safety validation: locked to backtest dashboard only and paper trading mode.",
        "Missing future requirements: real provider connection requires separate approvals, vaults, read-only gates, and production review.",
        "",
        f"Verdict: {summary['verdict']}",
    ]
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "path": target.as_posix(),
        "summary": summary,
        "backtest_dashboard_only": True,
        "localhost_only": True,
        "paper_trading": True,
        "real_trading_enabled": False,
    }
