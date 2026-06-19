from __future__ import annotations

from time import perf_counter

from src.core.standard_report import StandardReportV1, validate_standard_report
from src.reports.strategy_research_report import build_strategy_research_report, strategy_report_to_markdown
from src.reports.strategy_report_archive import save_strategy_research_report
from src.strategies.quality_score import build_backtest_quality_score
from src.strategies.stress_test import build_strategy_stress_report


def generate_full_strategy_report(
    strategy_name: str,
    symbols: list[str],
    backtest_summary: dict,
    quality_summary: dict | None = None,
    risk_summary: dict | None = None,
    stability_summary: dict | None = None,
    out_of_sample_summary: dict | None = None,
    stress_summary: dict | None = None,
    warnings: list[str] | None = None,
    archive: bool = False,
) -> dict:
    """Generate a full research report through one stable local pipeline."""
    started_at = perf_counter()
    clean_strategy_name = str(strategy_name or "").strip() or "Unnamed strategy"
    backtest_summary = backtest_summary or {}
    pipeline_warnings = list(warnings or [])

    if quality_summary is None:
        quality_result = build_backtest_quality_score(
            backtest_summary,
            stability_summary=stability_summary,
            out_of_sample_summary=out_of_sample_summary,
            stress_summary=stress_summary,
        )
        quality_summary = quality_result.get("summary", {})
        pipeline_warnings.extend(quality_result.get("warnings", []))

    if stress_summary is None and backtest_summary:
        stress_summary = build_strategy_stress_report(
            {
                "period_name": "Base",
                "total_return": backtest_summary.get("total_return", 0.0),
                "annualized_return": backtest_summary.get("annualized_return", 0.0),
                "max_drawdown": backtest_summary.get("max_drawdown", 0.0),
                "number_of_trades": backtest_summary.get("number_of_trades", 0),
                "final_portfolio_value": backtest_summary.get("final_portfolio_value", 0.0),
                "status": backtest_summary.get("status", "success"),
            }
        ).get("summary", {})

    risk_summary = risk_summary or {}
    report = build_strategy_research_report(
        clean_strategy_name,
        symbols or [],
        backtest_summary,
        quality_summary or {},
        stability_summary=stability_summary,
        out_of_sample_summary=out_of_sample_summary,
        stress_summary=stress_summary,
        risk_summary=risk_summary,
        warnings=pipeline_warnings,
    )
    markdown = strategy_report_to_markdown(report)
    standard_report = StandardReportV1(
        strategy_name=report.get("strategy_name", clean_strategy_name),
        generated_at=report.get("generated_at", ""),
        backtest_summary=backtest_summary,
        quality_summary=quality_summary or {},
        risk_summary=risk_summary,
        stability_summary=stability_summary or {},
        out_of_sample_summary=out_of_sample_summary or {},
        stress_summary=stress_summary or {},
        confidence_level=_confidence_from_report(report),
        data_freshness_score=float((quality_summary or {}).get("data_quality_score", 0.0) or 0.0),
        stability_index=float((stability_summary or {}).get("stable_window_ratio", 0.0) or 0.0),
    ).to_dict()
    archive_result = save_strategy_research_report(report, markdown) if archive else {}
    elapsed_seconds = round(perf_counter() - started_at, 4)
    return {
        "status": "success",
        "report": report,
        "markdown": markdown,
        "standard_report": standard_report,
        "standard_validation": validate_standard_report(standard_report),
        "archive": archive_result,
        "elapsed_seconds": elapsed_seconds,
        "warnings": pipeline_warnings,
    }


def _confidence_from_report(report: dict) -> str:
    research_view = str(report.get("research_view", "Neutral"))
    quality_score = float((report.get("key_metrics", {}) or {}).get("quality_score", 0.0) or 0.0)
    if research_view == "Positive" and quality_score >= 75:
        return "High"
    if research_view == "Cautious" or quality_score < 55:
        return "Low"
    return "Medium"
