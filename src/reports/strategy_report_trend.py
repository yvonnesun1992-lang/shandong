from __future__ import annotations

import csv
import io
from collections import Counter
from typing import Any


RESEARCH_DISCLAIMER = "仅供投资研究，不构成投资建议，不代表未来收益。"
TREND_COLUMNS = [
    "report_id",
    "generated_at",
    "saved_at",
    "strategy_name",
    "research_view",
    "quality_score",
    "quality_level",
    "total_return",
    "max_drawdown",
    "overfit_risk_level",
    "overall_stress_level",
    "symbol_count",
]


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_list(value: Any) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _nested_dict(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


def _report_time(report: dict) -> str:
    return str(report.get("generated_at") or report.get("saved_at") or "")


def _choose_strategy_name(reports: list[dict], requested_name: str | None) -> str:
    if requested_name:
        return str(requested_name).strip()
    names = [str(report.get("strategy_name") or "N/A") for report in reports]
    valid_names = [name for name in names if name and name != "N/A"]
    if not valid_names:
        return "N/A"
    counts = Counter(valid_names)
    max_count = max(counts.values())
    candidates = {name for name, count in counts.items() if count == max_count}
    for report in sorted(reports, key=_report_time, reverse=True):
        name = str(report.get("strategy_name") or "N/A")
        if name in candidates:
            return name
    return valid_names[0]


def _extract_trend_row(report: dict, index: int) -> dict:
    report = _nested_dict(report)
    key_metrics = _nested_dict(report.get("key_metrics"))
    quality_summary = _nested_dict(report.get("quality_summary"))
    module_summaries = _nested_dict(report.get("module_summaries"))
    out_of_sample = _nested_dict(module_summaries.get("out_of_sample"))
    stress = _nested_dict(module_summaries.get("stress"))
    symbols = _safe_list(report.get("symbols"))

    quality_score = _safe_float(
        quality_summary.get("total_quality_score", key_metrics.get("quality_score")),
        0.0,
    )
    quality_level = quality_summary.get("quality_level", key_metrics.get("quality_level", "N/A"))
    return {
        "report_id": str(report.get("report_id") or f"unarchived_report_{index + 1}"),
        "generated_at": str(report.get("generated_at") or ""),
        "saved_at": str(report.get("saved_at") or ""),
        "strategy_name": str(report.get("strategy_name") or "N/A"),
        "research_view": str(report.get("research_view") or "Neutral"),
        "quality_score": quality_score,
        "quality_level": str(quality_level or "N/A"),
        "total_return": _safe_float(key_metrics.get("total_return"), 0.0),
        "max_drawdown": _safe_float(key_metrics.get("max_drawdown"), 0.0),
        "overfit_risk_level": str(out_of_sample.get("overfit_risk_level") or "N/A"),
        "overall_stress_level": str(stress.get("overall_stress_level") or "N/A"),
        "symbol_count": len([symbol for symbol in symbols if str(symbol).strip()]),
    }


def _extract_risk_row(report: dict, trend_row: dict) -> dict:
    report = _nested_dict(report)
    highlights = [str(item) for item in _safe_list(report.get("risk_highlights")) if str(item).strip()]
    if not highlights:
        highlights = ["暂未发现高等级风险，但仍需结合更多样本继续研究。"]
    return {
        "report_id": trend_row["report_id"],
        "strategy_name": trend_row["strategy_name"],
        "risk_count": len(highlights),
        "risk_highlights": "；".join(highlights),
    }


def _trend_view(report_count: int, quality_change: float, drawdown_change: float) -> str:
    if report_count < 2:
        return "Insufficient"
    drawdown_worsened = drawdown_change < -0.05
    if quality_change > 5 and not drawdown_worsened:
        return "Improving"
    if quality_change < -5 or drawdown_worsened:
        return "Deteriorating"
    return "Stable"


def _trend_note(trend_view: str) -> str:
    if trend_view == "Improving":
        return "研究质量改善。"
    if trend_view == "Deteriorating":
        return "研究质量走弱。"
    if trend_view == "Insufficient":
        return "需要更多同策略历史报告后再观察趋势。"
    return "需要继续观察。"


def build_strategy_report_trend(reports: list[dict], strategy_name: str | None = None) -> dict:
    """Build a research-only trend view from archived strategy research reports."""
    clean_reports = [_nested_dict(report) for report in reports or []]
    selected_strategy = _choose_strategy_name(clean_reports, strategy_name)
    if selected_strategy and selected_strategy != "N/A":
        clean_reports = [
            report for report in clean_reports if str(report.get("strategy_name") or "N/A") == selected_strategy
        ]
    clean_reports = sorted(clean_reports, key=_report_time)

    trend_rows = [_extract_trend_row(report, index) for index, report in enumerate(clean_reports)]
    risk_trend_rows = [
        _extract_risk_row(report, trend_rows[index])
        for index, report in enumerate(clean_reports)
        if index < len(trend_rows)
    ]

    warnings = []
    if len(trend_rows) < 2:
        warnings.append("至少需要 2 份同策略历史策略研究报告后才能分析趋势。")

    first_row = trend_rows[0] if trend_rows else {}
    latest_row = trend_rows[-1] if trend_rows else {}
    quality_change = _safe_float(latest_row.get("quality_score")) - _safe_float(first_row.get("quality_score"))
    total_return_change = _safe_float(latest_row.get("total_return")) - _safe_float(first_row.get("total_return"))
    drawdown_change = _safe_float(latest_row.get("max_drawdown")) - _safe_float(first_row.get("max_drawdown"))
    trend_view = _trend_view(len(trend_rows), quality_change, drawdown_change)

    trend_summary = {
        "strategy_name": selected_strategy or str(latest_row.get("strategy_name") or "N/A"),
        "report_count": len(trend_rows),
        "first_report_id": first_row.get("report_id", ""),
        "latest_report_id": latest_row.get("report_id", ""),
        "first_quality_score": _safe_float(first_row.get("quality_score")),
        "latest_quality_score": _safe_float(latest_row.get("quality_score")),
        "quality_score_change": quality_change,
        "first_total_return": _safe_float(first_row.get("total_return")),
        "latest_total_return": _safe_float(latest_row.get("total_return")),
        "total_return_change": total_return_change,
        "first_max_drawdown": _safe_float(first_row.get("max_drawdown")),
        "latest_max_drawdown": _safe_float(latest_row.get("max_drawdown")),
        "max_drawdown_change": drawdown_change,
        "latest_research_view": latest_row.get("research_view", "N/A"),
        "latest_overfit_risk_level": latest_row.get("overfit_risk_level", "N/A"),
        "latest_overall_stress_level": latest_row.get("overall_stress_level", "N/A"),
        "trend_view": trend_view,
        "trend_note": _trend_note(trend_view),
        "disclaimer": RESEARCH_DISCLAIMER,
    }

    return {
        "trend_summary": trend_summary,
        "trend_rows": trend_rows,
        "risk_trend_rows": risk_trend_rows,
        "warnings": warnings,
        "disclaimer": RESEARCH_DISCLAIMER,
    }


def export_strategy_report_trend_csv(trend_rows: list[dict]) -> bytes:
    """Export strategy report trend rows as UTF-8-SIG CSV bytes."""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=TREND_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    for row in trend_rows or []:
        writer.writerow({column: row.get(column, "") for column in TREND_COLUMNS})
    return output.getvalue().encode("utf-8-sig")
