from __future__ import annotations

import csv
import io
from collections import defaultdict
from typing import Any

from src.reports.strategy_report_trend import build_strategy_report_trend


RESEARCH_DISCLAIMER = "仅供投资研究，不构成投资建议，不代表未来收益。"
DASHBOARD_COLUMNS = [
    "strategy_name",
    "report_count",
    "latest_report_id",
    "latest_generated_at",
    "latest_research_view",
    "latest_quality_score",
    "latest_quality_level",
    "trend_view",
    "latest_total_return",
    "latest_max_drawdown",
    "latest_overfit_risk_level",
    "latest_overall_stress_level",
    "risk_count",
    "research_priority",
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


def _strategy_name(report: dict, index: int) -> str:
    name = str(report.get("strategy_name") or "").strip()
    return name or f"Unspecified strategy {index + 1}"


def _risk_highlights(report: dict) -> list[str]:
    highlights = [str(item) for item in _safe_list(report.get("risk_highlights")) if str(item).strip()]
    if not highlights:
        highlights = ["暂未发现高等级风险，但仍需结合更多样本继续研究。"]
    return highlights


def _latest_fields(report: dict) -> dict:
    key_metrics = _nested_dict(report.get("key_metrics"))
    quality_summary = _nested_dict(report.get("quality_summary"))
    module_summaries = _nested_dict(report.get("module_summaries"))
    out_of_sample = _nested_dict(module_summaries.get("out_of_sample"))
    stress = _nested_dict(module_summaries.get("stress"))
    quality_score = _safe_float(
        quality_summary.get("total_quality_score", key_metrics.get("quality_score")),
        0.0,
    )
    quality_level = quality_summary.get("quality_level", key_metrics.get("quality_level", "N/A"))
    return {
        "latest_report_id": str(report.get("report_id") or ""),
        "latest_generated_at": str(report.get("generated_at") or report.get("saved_at") or ""),
        "latest_research_view": str(report.get("research_view") or "Neutral"),
        "latest_quality_score": quality_score,
        "latest_quality_level": str(quality_level or "N/A"),
        "latest_total_return": _safe_float(key_metrics.get("total_return"), 0.0),
        "latest_max_drawdown": _safe_float(key_metrics.get("max_drawdown"), 0.0),
        "latest_overfit_risk_level": str(out_of_sample.get("overfit_risk_level") or "N/A"),
        "latest_overall_stress_level": str(stress.get("overall_stress_level") or "N/A"),
    }


def _research_priority(row: dict) -> str:
    if row["report_count"] < 2:
        return "Watch"
    if (
        row["latest_research_view"] == "Cautious"
        or row["trend_view"] == "Deteriorating"
        or row["latest_quality_score"] < 55
    ):
        return "Low"
    if (
        row["latest_quality_score"] >= 75
        and row["trend_view"] in {"Improving", "Stable"}
        and row["latest_research_view"] != "Cautious"
    ):
        return "High"
    if 55 <= row["latest_quality_score"] < 75 or row["trend_view"] == "Stable":
        return "Medium"
    return "Watch"


def _priority_label(priority: str) -> str:
    if priority == "High":
        return "高优先级研究"
    if priority == "Medium":
        return "中优先级观察"
    if priority == "Low":
        return "低优先级复盘"
    return "样本不足"


def _is_risky(row: dict) -> bool:
    return (
        row["latest_research_view"] == "Cautious"
        or row["trend_view"] == "Deteriorating"
        or row["latest_overfit_risk_level"] == "High"
        or row["latest_overall_stress_level"] == "High"
        or row["risk_count"] >= 3
    )


def _strategy_row(strategy_name: str, reports: list[dict]) -> dict:
    ordered_reports = sorted(reports, key=_report_time)
    latest_report = ordered_reports[-1] if ordered_reports else {}
    trend = build_strategy_report_trend(ordered_reports, strategy_name)
    trend_summary = trend.get("trend_summary", {}) or {}
    highlights = _risk_highlights(latest_report)
    row = {
        "strategy_name": strategy_name,
        "report_count": len(ordered_reports),
        **_latest_fields(latest_report),
        "trend_view": str(trend_summary.get("trend_view") or "Insufficient"),
        "risk_count": len(highlights),
    }
    priority = _research_priority(row)
    row["research_priority"] = priority
    row["research_priority_label"] = _priority_label(priority)
    row["risk_highlights"] = "；".join(highlights)
    return row


def build_strategy_research_dashboard(reports: list[dict]) -> dict:
    """Build a research-only dashboard from archived strategy research reports."""
    clean_reports = [_nested_dict(report) for report in reports or []]
    grouped: dict[str, list[dict]] = defaultdict(list)
    for index, report in enumerate(clean_reports):
        grouped[_strategy_name(report, index)].append(report)

    strategy_rows = [_strategy_row(name, items) for name, items in grouped.items()]
    strategy_rows = sorted(
        strategy_rows,
        key=lambda row: (row["latest_quality_score"], row["report_count"], row["strategy_name"]),
        reverse=True,
    )
    priority_rows = sorted(
        strategy_rows,
        key=lambda row: (row["research_priority"], row["latest_quality_score"], row["strategy_name"]),
        reverse=True,
    )
    risk_rows = [row for row in strategy_rows if _is_risky(row)]
    best_row = max(strategy_rows, key=lambda row: row["latest_quality_score"], default={})
    warnings = []
    if not strategy_rows:
        warnings.append("暂无已归档策略研究报告，暂无法生成策略研究看板。")

    dashboard_summary = {
        "strategy_count": len(strategy_rows),
        "total_report_count": len(clean_reports),
        "positive_strategy_count": sum(1 for row in strategy_rows if row["latest_research_view"] == "Positive"),
        "cautious_strategy_count": sum(1 for row in strategy_rows if row["latest_research_view"] == "Cautious"),
        "improving_strategy_count": sum(1 for row in strategy_rows if row["trend_view"] == "Improving"),
        "deteriorating_strategy_count": sum(1 for row in strategy_rows if row["trend_view"] == "Deteriorating"),
        "high_risk_strategy_count": len(risk_rows),
        "best_strategy_name": best_row.get("strategy_name", ""),
        "best_quality_score": _safe_float(best_row.get("latest_quality_score")),
        "best_trend_view": best_row.get("trend_view", "N/A"),
        "disclaimer": RESEARCH_DISCLAIMER,
    }

    return {
        "dashboard_summary": dashboard_summary,
        "strategy_rows": strategy_rows,
        "priority_rows": priority_rows,
        "risk_rows": risk_rows,
        "warnings": warnings,
        "disclaimer": RESEARCH_DISCLAIMER,
    }


def export_strategy_dashboard_csv(strategy_rows: list[dict]) -> bytes:
    """Export strategy dashboard rows as UTF-8-SIG CSV bytes."""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=DASHBOARD_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    for row in strategy_rows or []:
        writer.writerow({column: row.get(column, "") for column in DASHBOARD_COLUMNS})
    return output.getvalue().encode("utf-8-sig")
