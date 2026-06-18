from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


RESEARCH_DISCLAIMER = "仅供投资研究，不构成投资建议，不代表未来收益。"


def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_list(values) -> list:
    if values is None:
        return []
    if isinstance(values, list):
        return values
    return [values]


def _research_view(
    quality_summary: dict,
    out_of_sample_summary: dict | None,
    stress_summary: dict | None,
) -> str:
    quality_level = str(quality_summary.get("quality_level", "Watch")).strip()
    overfit_risk = str((out_of_sample_summary or {}).get("overfit_risk_level", "")).strip()
    stress_level = str((stress_summary or {}).get("overall_stress_level", "")).strip()
    if quality_level == "Weak" or overfit_risk == "High" or stress_level == "High":
        return "Cautious"
    if quality_level == "Watch":
        return "Neutral"
    if quality_level in {"Excellent", "Good"} and overfit_risk != "High" and stress_level != "High":
        return "Positive"
    return "Neutral"


def _executive_summary(research_view: str, strategy_name: str, quality_summary: dict) -> str:
    quality_level = str(quality_summary.get("quality_level", "N/A"))
    total_score = quality_summary.get("total_quality_score", "N/A")
    if research_view == "Positive":
        stance = "值得进一步研究"
    elif research_view == "Neutral":
        stance = "需要谨慎观察"
    else:
        stance = "暂不适合提高研究优先级"
    return f"{strategy_name} 的综合质量等级为 {quality_level}，综合质量分为 {total_score}，研究视图为 {research_view}：{stance}。"


def _risk_highlights(
    backtest_summary: dict,
    quality_summary: dict,
    out_of_sample_summary: dict | None,
    stress_summary: dict | None,
    risk_summary: dict | None,
    warnings: list[str],
) -> list[str]:
    highlights = []
    max_drawdown = _safe_float(backtest_summary.get("max_drawdown"))
    if max_drawdown < -0.25:
        highlights.append("组合回测最大回撤超过 25%，需关注回撤风险。")
    if str(quality_summary.get("quality_level", "")) in {"Watch", "Weak"}:
        highlights.append("综合质量等级不高，适合继续观察而不是提高研究优先级。")
    if str((out_of_sample_summary or {}).get("overfit_risk_level", "")) == "High":
        highlights.append("样本外过拟合风险为 High。")
    if str((stress_summary or {}).get("overall_stress_level", "")) == "High":
        highlights.append("压力测试总体等级为 High。")
    if str((risk_summary or {}).get("risk_level", "")) == "High":
        highlights.append("风险控制等级为 High。")
    highlights.extend(str(warning) for warning in warnings if warning and warning != RESEARCH_DISCLAIMER)
    if not highlights:
        highlights.append("暂未发现高等级风险，但仍需结合更多样本继续研究。")
    return highlights


def build_strategy_research_report(
    strategy_name: str,
    symbols: list[str],
    backtest_summary: dict,
    quality_summary: dict,
    stability_summary: dict | None = None,
    out_of_sample_summary: dict | None = None,
    stress_summary: dict | None = None,
    risk_summary: dict | None = None,
    warnings: list[str] | None = None,
) -> dict:
    """Build a research-only strategy report from existing result summaries."""
    strategy_name = str(strategy_name or "Unnamed strategy").strip() or "Unnamed strategy"
    clean_symbols = [str(symbol).strip().upper() for symbol in symbols or [] if str(symbol).strip()]
    backtest_summary = backtest_summary or {}
    quality_summary = quality_summary or {}
    warnings_list = [RESEARCH_DISCLAIMER]
    warnings_list.extend(str(warning) for warning in _safe_list(warnings) if str(warning).strip())

    missing_modules = []
    if not stability_summary:
        missing_modules.append("稳定性")
    if not out_of_sample_summary:
        missing_modules.append("样本外")
    if not stress_summary:
        missing_modules.append("压力测试")
    if not risk_summary:
        missing_modules.append("风险控制")
    for module_name in missing_modules:
        warnings_list.append(f"缺少{module_name}摘要，报告对应部分置信度降低。")

    research_view = _research_view(quality_summary, out_of_sample_summary, stress_summary)
    generated_at = datetime.now(timezone.utc).isoformat()
    key_metrics = {
        "total_return": _safe_float(backtest_summary.get("total_return")),
        "annualized_return": _safe_float(backtest_summary.get("annualized_return")),
        "max_drawdown": _safe_float(backtest_summary.get("max_drawdown")),
        "number_of_trades": int(_safe_float(backtest_summary.get("number_of_trades"), 0.0)),
        "final_portfolio_value": _safe_float(backtest_summary.get("final_portfolio_value")),
        "quality_score": quality_summary.get("total_quality_score", 0),
        "quality_level": quality_summary.get("quality_level", "N/A"),
    }
    risk_highlights = _risk_highlights(
        backtest_summary,
        quality_summary,
        out_of_sample_summary,
        stress_summary,
        risk_summary,
        warnings_list,
    )

    return {
        "report_title": f"Strategy Research Report - {strategy_name}",
        "strategy_name": strategy_name,
        "symbols": clean_symbols,
        "generated_at": generated_at,
        "executive_summary": _executive_summary(research_view, strategy_name, quality_summary),
        "research_view": research_view,
        "key_metrics": key_metrics,
        "quality_summary": quality_summary,
        "risk_highlights": risk_highlights,
        "module_summaries": {
            "backtest": backtest_summary,
            "quality": quality_summary,
            "stability": stability_summary or {},
            "out_of_sample": out_of_sample_summary or {},
            "stress": stress_summary or {},
            "risk": risk_summary or {},
        },
        "warnings": warnings_list,
        "disclaimer": RESEARCH_DISCLAIMER,
    }


def _format_value(value) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def strategy_report_to_markdown(report: dict) -> str:
    """Render a strategy research report as Markdown."""
    report = report or {}
    key_metrics = report.get("key_metrics", {}) or {}
    module_summaries = report.get("module_summaries", {}) or {}
    lines = [
        f"# {report.get('report_title', 'Strategy Research Report')}",
        "",
        f"- 生成时间：{report.get('generated_at', '')}",
        f"- 策略名称：{report.get('strategy_name', '')}",
        f"- 股票池：{', '.join(report.get('symbols', []))}",
        f"- 综合研究结论：{report.get('research_view', 'Neutral')}",
        "",
        "## 执行摘要",
        "",
        str(report.get("executive_summary", "")),
        "",
        "## 核心指标",
        "",
    ]
    for key, value in key_metrics.items():
        lines.append(f"- {key}: {_format_value(value)}")
    lines.extend(["", "## 质量评分", ""])
    quality_summary = report.get("quality_summary", {}) or {}
    for key, value in quality_summary.items():
        lines.append(f"- {key}: {_format_value(value)}")
    lines.extend(["", "## 模块摘要", ""])
    for module_name, module_summary in module_summaries.items():
        lines.append(f"### {module_name}")
        if module_summary:
            for key, value in module_summary.items():
                lines.append(f"- {key}: {_format_value(value)}")
        else:
            lines.append("- 暂无摘要。")
        lines.append("")
    lines.extend(["## 主要风险", ""])
    for item in report.get("risk_highlights", []) or []:
        lines.append(f"- {item}")
    lines.extend(["", "## 免责声明", "", str(report.get("disclaimer", RESEARCH_DISCLAIMER)), ""])
    return "\n".join(lines)
