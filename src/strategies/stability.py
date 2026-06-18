from __future__ import annotations

import statistics
from typing import Any

import pandas as pd


RESEARCH_DISCLAIMER = "仅供投资研究，不构成投资建议，不代表未来收益。"


def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clean_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "window_name": str(result.get("window_name", "")).strip() or "Unnamed window",
        "total_return": _safe_float(result.get("total_return")),
        "annualized_return": _safe_float(result.get("annualized_return")),
        "max_drawdown": _safe_float(result.get("max_drawdown")),
        "number_of_trades": int(_safe_float(result.get("number_of_trades"), 0.0)),
        "final_portfolio_value": _safe_float(result.get("final_portfolio_value")),
        "status": str(result.get("status", "success")).strip().lower() or "success",
        "error": str(result.get("error", "")).strip(),
    }


def _bounded_score(value: float) -> float:
    return max(0.0, min(float(value), 1.0))


def _return_consistency_score(total_returns: list[float]) -> float:
    if not total_returns:
        return 0.0
    positive_ratio = sum(1 for value in total_returns if value > 0) / len(total_returns)
    if len(total_returns) == 1:
        dispersion_penalty = 0.0
    else:
        dispersion_penalty = min(statistics.pstdev(total_returns), 1.0)
    return _bounded_score(positive_ratio * (1.0 - dispersion_penalty))


def _drawdown_consistency_score(max_drawdowns: list[float]) -> float:
    if not max_drawdowns:
        return 0.0
    worst_drawdown = abs(min(max_drawdowns))
    if len(max_drawdowns) == 1:
        dispersion_penalty = 0.0
    else:
        dispersion_penalty = min(statistics.pstdev(max_drawdowns), 1.0)
    return _bounded_score(1.0 - min(worst_drawdown + dispersion_penalty, 1.0))


def _stability_level(checks: list[dict], success_windows: int, min_windows: int) -> str:
    if success_windows < min_windows:
        return "Low"
    fail_count = sum(1 for check in checks if check.get("status") == "fail")
    warn_count = sum(1 for check in checks if check.get("status") == "warn")
    if fail_count > 0 or warn_count >= 3:
        return "Low"
    if warn_count > 0:
        return "Medium"
    return "High"


def build_strategy_stability_report(
    backtest_results: list[dict],
    min_windows: int = 3,
) -> dict:
    """Analyze existing multi-window backtest summaries without changing strategy logic."""
    min_windows = max(int(min_windows or 0), 1)
    warnings = [RESEARCH_DISCLAIMER]
    window_results = [_clean_result(result) for result in backtest_results or []]
    failed_windows = [row for row in window_results if row["status"] != "success"]
    successful = [row for row in window_results if row["status"] == "success"]

    window_count = len(window_results)
    success_windows = len(successful)
    failed_window_count = len(failed_windows)
    total_returns = [row["total_return"] for row in successful]
    max_drawdowns = [row["max_drawdown"] for row in successful]
    positive_return_windows = sum(1 for value in total_returns if value > 0)
    negative_return_windows = sum(1 for value in total_returns if value < 0)
    average_total_return = sum(total_returns) / len(total_returns) if total_returns else 0.0
    worst_total_return = min(total_returns) if total_returns else 0.0
    best_total_return = max(total_returns) if total_returns else 0.0
    average_max_drawdown = sum(max_drawdowns) / len(max_drawdowns) if max_drawdowns else 0.0
    worst_max_drawdown = min(max_drawdowns) if max_drawdowns else 0.0
    return_consistency_score = _return_consistency_score(total_returns)
    drawdown_consistency_score = _drawdown_consistency_score(max_drawdowns)
    positive_ratio = positive_return_windows / success_windows if success_windows else 0.0
    return_range = best_total_return - worst_total_return if total_returns else 0.0

    if not window_results:
        warnings.append("没有可用于稳定性评估的窗口结果。")
    if success_windows < min_windows:
        warnings.append("成功窗口数量少于最低要求，样本数量不足。")
    if failed_window_count > 0:
        warnings.append("部分窗口回测失败，需关注数据质量或窗口样本风险。")
    if worst_max_drawdown < -0.25:
        warnings.append("最差回撤超过 25%，回撤风险较高。")
    if return_range > 0.35:
        warnings.append("不同窗口收益差异较大，收益稳定性不足。")

    checks = [
        {
            "name": "样本数量风险",
            "status": "fail" if success_windows < min_windows else "pass",
            "message": f"成功窗口 {success_windows} 个，最低要求 {min_windows} 个。",
        },
        {
            "name": "收益稳定性",
            "status": "pass" if positive_ratio >= 0.7 and return_range <= 0.35 else "warn",
            "message": f"正收益窗口占比 {positive_ratio:.2%}，收益区间差 {return_range:.2%}。",
        },
        {
            "name": "回撤稳定性",
            "status": "fail" if worst_max_drawdown < -0.25 else "pass",
            "message": f"最差最大回撤 {worst_max_drawdown:.2%}。",
        },
        {
            "name": "胜率稳定性",
            "status": "pass" if positive_ratio >= 0.7 else "warn",
            "message": f"正收益窗口 {positive_return_windows} 个，负收益窗口 {negative_return_windows} 个。",
        },
        {
            "name": "数据质量风险",
            "status": "warn" if failed_window_count > 0 else "pass",
            "message": f"失败窗口 {failed_window_count} 个。",
        },
    ]
    stability_level = _stability_level(checks, success_windows, min_windows)

    return {
        "summary": {
            "window_count": window_count,
            "success_windows": success_windows,
            "failed_windows": failed_window_count,
            "positive_return_windows": positive_return_windows,
            "negative_return_windows": negative_return_windows,
            "average_total_return": average_total_return,
            "worst_total_return": worst_total_return,
            "best_total_return": best_total_return,
            "average_max_drawdown": average_max_drawdown,
            "worst_max_drawdown": worst_max_drawdown,
            "return_consistency_score": return_consistency_score,
            "drawdown_consistency_score": drawdown_consistency_score,
            "stability_level": stability_level,
            "disclaimer": RESEARCH_DISCLAIMER,
        },
        "window_results": window_results,
        "failed_windows": failed_windows,
        "warnings": warnings,
        "checks": checks,
    }


def _window_name(start_date, end_date, index: int) -> str:
    if start_date is not None and end_date is not None:
        return f"{pd.to_datetime(start_date).date()} to {pd.to_datetime(end_date).date()}"
    return f"Window {index}"


def _date_bounds(data: pd.DataFrame) -> tuple[Any, Any]:
    if "date" not in data.columns or data.empty:
        return None, None
    dates = pd.to_datetime(data["date"], errors="coerce").dropna()
    if dates.empty:
        return None, None
    return dates.iloc[0], dates.iloc[-1]


def split_backtest_windows(
    data,
    window_size: int = 120,
    step_size: int = 60,
) -> list[dict]:
    """Split prepared DataFrame or portfolio price-data dict into row-based windows."""
    window_size = int(window_size or 0)
    step_size = int(step_size or 0)
    if window_size <= 0 or step_size <= 0:
        return []

    if isinstance(data, pd.DataFrame):
        if len(data) < window_size:
            return []
        windows = []
        for index, start in enumerate(range(0, len(data) - window_size + 1, step_size), start=1):
            window_data = data.iloc[start : start + window_size].copy().reset_index(drop=True)
            start_date, end_date = _date_bounds(window_data)
            windows.append(
                {
                    "window_name": _window_name(start_date, end_date, index),
                    "start_date": str(pd.to_datetime(start_date).date()) if start_date is not None else None,
                    "end_date": str(pd.to_datetime(end_date).date()) if end_date is not None else None,
                    "data": window_data,
                }
            )
        return windows

    if isinstance(data, dict):
        clean_data = {str(symbol): frame for symbol, frame in data.items() if isinstance(frame, pd.DataFrame)}
        if not clean_data:
            return []
        max_rows = max(len(frame) for frame in clean_data.values())
        if max_rows < window_size:
            return []
        windows = []
        for index, start in enumerate(range(0, max_rows - window_size + 1, step_size), start=1):
            window_frames = {}
            start_dates = []
            end_dates = []
            for symbol, frame in clean_data.items():
                if len(frame) < start + window_size:
                    continue
                window_frame = frame.iloc[start : start + window_size].copy().reset_index(drop=True)
                if window_frame.empty:
                    continue
                start_date, end_date = _date_bounds(window_frame)
                if start_date is not None:
                    start_dates.append(start_date)
                if end_date is not None:
                    end_dates.append(end_date)
                window_frames[symbol] = window_frame
            if not window_frames:
                continue
            start_date = min(start_dates) if start_dates else None
            end_date = max(end_dates) if end_dates else None
            windows.append(
                {
                    "window_name": _window_name(start_date, end_date, index),
                    "start_date": str(pd.to_datetime(start_date).date()) if start_date is not None else None,
                    "end_date": str(pd.to_datetime(end_date).date()) if end_date is not None else None,
                    "data": window_frames,
                }
            )
        return windows

    return []
