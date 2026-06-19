from __future__ import annotations

import csv
import io
from typing import Any


RESEARCH_DISCLAIMER = "仅供投资研究，不构成投资建议，不代表未来收益。"
COMPARISON_COLUMNS = [
    "report_id",
    "generated_at",
    "strategy_name",
    "research_view",
    "quality_score",
    "quality_level",
    "total_return",
    "max_drawdown",
    "symbol_count",
    "overfit_risk_level",
    "overall_stress_level",
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


def _get_quality_score(report: dict, key_metrics: dict, quality_summary: dict) -> float:
    return _safe_float(
        quality_summary.get("total_quality_score", key_metrics.get("quality_score")),
        0.0,
    )


def _extract_row(report: dict, index: int) -> dict:
    report = _nested_dict(report)
    key_metrics = _nested_dict(report.get("key_metrics"))
    quality_summary = _nested_dict(report.get("quality_summary"))
    module_summaries = _nested_dict(report.get("module_summaries"))
    out_of_sample = _nested_dict(module_summaries.get("out_of_sample"))
    stress = _nested_dict(module_summaries.get("stress"))
    symbols = _safe_list(report.get("symbols"))

    quality_score = _get_quality_score(report, key_metrics, quality_summary)
    quality_level = quality_summary.get("quality_level", key_metrics.get("quality_level", "N/A"))
    report_id = str(report.get("report_id") or f"unarchived_report_{index + 1}")
    return {
        "report_id": report_id,
        "generated_at": str(report.get("generated_at") or ""),
        "strategy_name": str(report.get("strategy_name") or "N/A"),
        "research_view": str(report.get("research_view") or "Neutral"),
        "quality_score": quality_score,
        "quality_level": str(quality_level or "N/A"),
        "total_return": _safe_float(key_metrics.get("total_return"), 0.0),
        "max_drawdown": _safe_float(key_metrics.get("max_drawdown"), 0.0),
        "symbol_count": len([symbol for symbol in symbols if str(symbol).strip()]),
        "overfit_risk_level": str(out_of_sample.get("overfit_risk_level") or "N/A"),
        "overall_stress_level": str(stress.get("overall_stress_level") or "N/A"),
    }


def _extract_risk_row(report: dict, comparison_row: dict) -> dict:
    report = _nested_dict(report)
    highlights = [str(item) for item in _safe_list(report.get("risk_highlights")) if str(item).strip()]
    if not highlights:
        highlights = ["暂未发现高等级风险，但仍需结合更多样本继续研究。"]
    return {
        "report_id": comparison_row["report_id"],
        "strategy_name": comparison_row["strategy_name"],
        "risk_count": len(highlights),
        "risk_highlights": "；".join(highlights),
    }


def _research_priority(best_row: dict | None, cautious_count: int) -> str:
    if not best_row:
        return "历史报告数量不足，暂无法形成对比结论。"
    if cautious_count:
        return (
            f"{best_row['strategy_name']} 质量分相对更高，更值得进一步研究；"
            f"同时有 {cautious_count} 份报告需要谨慎观察。"
        )
    return f"{best_row['strategy_name']} 质量分相对更高，更值得进一步研究。"


def compare_strategy_research_reports(reports: list[dict]) -> dict:
    """Compare archived strategy research reports without recalculating strategies."""
    clean_reports = [_nested_dict(report) for report in (reports or [])][:5]
    comparison_rows = [_extract_row(report, index) for index, report in enumerate(clean_reports)]
    risk_rows = [
        _extract_risk_row(report, comparison_rows[index])
        for index, report in enumerate(clean_reports)
        if index < len(comparison_rows)
    ]

    warnings = []
    if len(reports or []) > 5:
        warnings.append("最多对比 5 份报告，已使用前 5 份报告。")
    if len(comparison_rows) < 2:
        warnings.append("至少需要 2 份历史策略研究报告后才能形成稳定对比。")

    best_row = max(
        comparison_rows,
        key=lambda row: (row["quality_score"], row["max_drawdown"]),
        default=None,
    )
    highest_return_row = max(comparison_rows, key=lambda row: row["total_return"], default=None)
    lowest_drawdown_row = max(comparison_rows, key=lambda row: row["max_drawdown"], default=None)
    cautious_count = sum(1 for row in comparison_rows if row["research_view"] == "Cautious")

    summary = {
        "report_count": len(comparison_rows),
        "best_report_id": best_row["report_id"] if best_row else "",
        "best_strategy_name": best_row["strategy_name"] if best_row else "",
        "best_quality_score": best_row["quality_score"] if best_row else 0.0,
        "best_quality_level": best_row["quality_level"] if best_row else "N/A",
        "highest_return_report_id": highest_return_row["report_id"] if highest_return_row else "",
        "highest_total_return": highest_return_row["total_return"] if highest_return_row else 0.0,
        "lowest_drawdown_report_id": lowest_drawdown_row["report_id"] if lowest_drawdown_row else "",
        "lowest_max_drawdown": lowest_drawdown_row["max_drawdown"] if lowest_drawdown_row else 0.0,
        "cautious_report_count": cautious_count,
        "research_priority": _research_priority(best_row, cautious_count),
        "disclaimer": RESEARCH_DISCLAIMER,
    }

    return {
        "comparison_summary": summary,
        "comparison_rows": comparison_rows,
        "risk_rows": risk_rows,
        "best_report_id": summary["best_report_id"],
        "best_strategy_name": summary["best_strategy_name"],
        "best_quality_score": summary["best_quality_score"],
        "lowest_drawdown_report_id": summary["lowest_drawdown_report_id"],
        "highest_return_report_id": summary["highest_return_report_id"],
        "warnings": warnings,
        "disclaimer": RESEARCH_DISCLAIMER,
    }


def export_strategy_report_comparison_csv(comparison_rows: list[dict]) -> bytes:
    """Export strategy report comparison rows as UTF-8-SIG CSV bytes."""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=COMPARISON_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    for row in comparison_rows or []:
        writer.writerow({column: row.get(column, "") for column in COMPARISON_COLUMNS})
    return output.getvalue().encode("utf-8-sig")
