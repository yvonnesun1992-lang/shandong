from __future__ import annotations

from pathlib import Path

from product_home.init import boundary


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def build_backtest_summary() -> dict:
    reports = sorted((PROJECT_ROOT / "reports").glob("*backtest*.md"))
    return {
        "backtest_module_available": (PROJECT_ROOT / "backtest").exists() or (PROJECT_ROOT / "src" / "backtest").exists(),
        "latest_backtest_report_placeholder": reports[-1].name if reports else "No local backtest report found",
        "latest_performance_placeholder": "Use local backtest reports for current metrics",
        "latest_warnings_placeholder": [],
        "no_live_trading": True,
        **boundary(),
    }
