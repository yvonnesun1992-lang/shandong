from __future__ import annotations

from typing import Any


RESEARCH_DISCLAIMER = "仅供投资研究，不构成投资建议，不代表未来收益。"


def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp_score(value: float) -> int:
    return int(round(max(0.0, min(float(value), 100.0))))


def _level_score(level: str, mapping: dict[str, int], default: int = 50) -> int:
    return mapping.get(str(level).strip(), default)


def _quality_level(total_score: int) -> str:
    if total_score >= 85:
        return "Excellent"
    if total_score >= 70:
        return "Good"
    if total_score >= 50:
        return "Watch"
    return "Weak"


def _return_score(summary: dict[str, Any]) -> tuple[int, str]:
    total_return = _safe_float(summary.get("total_return"))
    annualized_return = _safe_float(summary.get("annualized_return"))
    if total_return <= 0:
        score = 25 + min(max(annualized_return, -0.3), 0.0) * 50
        return _clamp_score(score), "收益为负或接近零，收益质量偏弱。"
    score = 55 + min(total_return, 0.5) * 70 + min(max(annualized_return, 0.0), 0.3) * 35
    return _clamp_score(score), "收益为正，具备进一步研究价值。"


def _drawdown_score(summary: dict[str, Any]) -> tuple[int, str]:
    max_drawdown = _safe_float(summary.get("max_drawdown"))
    drawdown_abs = abs(max_drawdown)
    if drawdown_abs >= 0.35:
        return 25, "最大回撤较大，回撤质量偏弱。"
    if drawdown_abs >= 0.25:
        return 45, "最大回撤超过 25%，需要重点关注。"
    if drawdown_abs >= 0.15:
        return 70, "最大回撤处于可观察区间。"
    return 88, "最大回撤较温和。"


def _stability_score(stability_summary: dict | None) -> tuple[int, str, list[str]]:
    if not stability_summary:
        return 45, "未纳入稳定性结果，稳定性质量置信度降低。", ["缺少稳定性评估结果。"]
    level_score = _level_score(str(stability_summary.get("stability_level")), {"High": 85, "Medium": 65, "Low": 35})
    return_consistency = _safe_float(stability_summary.get("return_consistency_score"), 0.0)
    drawdown_consistency = _safe_float(stability_summary.get("drawdown_consistency_score"), 0.0)
    failed_windows = int(_safe_float(stability_summary.get("failed_windows"), 0.0))
    score = level_score * 0.55 + return_consistency * 25 + drawdown_consistency * 20 - failed_windows * 5
    return _clamp_score(score), "已纳入多窗口稳定性结果。", []


def _out_of_sample_score(out_of_sample_summary: dict | None) -> tuple[int, str, list[str]]:
    if not out_of_sample_summary:
        return 45, "未纳入样本外结果，样本外质量置信度降低。", ["缺少样本外测试结果。"]
    risk_score = _level_score(
        str(out_of_sample_summary.get("overfit_risk_level")),
        {"Low": 85, "Medium": 60, "High": 25},
    )
    return_decay = _safe_float(out_of_sample_summary.get("return_decay"), 0.0)
    test_trades = int(_safe_float(out_of_sample_summary.get("test_trades"), 0.0))
    trade_bonus = min(test_trades, 10) * 1.5
    score = risk_score - min(max(return_decay, 0.0), 1.0) * 25 + trade_bonus
    return _clamp_score(score), "已纳入样本外测试结果。", []


def _stress_score(stress_summary: dict | None) -> tuple[int, str, list[str]]:
    if not stress_summary:
        return 45, "未纳入压力测试结果，压力质量置信度降低。", ["缺少压力测试结果。"]
    level_score = _level_score(
        str(stress_summary.get("overall_stress_level")),
        {"Low": 85, "Medium": 60, "High": 25},
    )
    worst_return = _safe_float(stress_summary.get("worst_stressed_return"), 0.0)
    worst_drawdown = abs(_safe_float(stress_summary.get("worst_stressed_drawdown"), 0.0))
    score = level_score + min(max(worst_return, -0.5), 0.3) * 30 - min(worst_drawdown, 0.5) * 20
    return _clamp_score(score), "已纳入压力测试结果。", []


def _data_quality_score(
    backtest_summary: dict[str, Any],
    stability_summary: dict | None,
    out_of_sample_summary: dict | None,
    stress_summary: dict | None,
) -> tuple[int, str, list[str]]:
    warnings = []
    score = 100
    trades = int(_safe_float(backtest_summary.get("number_of_trades"), 0.0))
    status = str(backtest_summary.get("status", "success")).strip().lower() or "success"
    if status != "success":
        score -= 45
        warnings.append("组合回测结果不是 success。")
    if trades < 3:
        score -= 25
        warnings.append("组合回测交易次数较少。")
    for label, value in [
        ("稳定性", stability_summary),
        ("样本外", out_of_sample_summary),
        ("压力测试", stress_summary),
    ]:
        if not value:
            score -= 10
            warnings.append(f"缺少{label}输入。")
    return _clamp_score(score), "按输入完整性、回测状态和交易次数评估。", warnings


def build_backtest_quality_score(
    backtest_summary: dict,
    stability_summary: dict | None = None,
    out_of_sample_summary: dict | None = None,
    stress_summary: dict | None = None,
) -> dict:
    """Score existing research results without changing backtest or strategy logic."""
    backtest_summary = backtest_summary or {}
    warnings = [RESEARCH_DISCLAIMER]

    return_score, return_message = _return_score(backtest_summary)
    drawdown_score, drawdown_message = _drawdown_score(backtest_summary)
    stability_score, stability_message, stability_warnings = _stability_score(stability_summary)
    out_of_sample_score, out_of_sample_message, out_of_sample_warnings = _out_of_sample_score(out_of_sample_summary)
    stress_score, stress_message, stress_warnings = _stress_score(stress_summary)
    data_quality_score, data_quality_message, data_quality_warnings = _data_quality_score(
        backtest_summary,
        stability_summary,
        out_of_sample_summary,
        stress_summary,
    )
    warnings.extend(stability_warnings + out_of_sample_warnings + stress_warnings + data_quality_warnings)

    component_scores = [
        return_score,
        drawdown_score,
        stability_score,
        out_of_sample_score,
        stress_score,
        data_quality_score,
    ]
    total_quality_score = _clamp_score(sum(component_scores) / len(component_scores))
    quality_level = _quality_level(total_quality_score)

    score_breakdown = [
        {"category": "收益质量", "score": return_score, "message": return_message},
        {"category": "回撤质量", "score": drawdown_score, "message": drawdown_message},
        {"category": "稳定性质量", "score": stability_score, "message": stability_message},
        {"category": "样本外质量", "score": out_of_sample_score, "message": out_of_sample_message},
        {"category": "压力测试质量", "score": stress_score, "message": stress_message},
        {"category": "数据质量风险", "score": data_quality_score, "message": data_quality_message},
    ]

    checks = []
    for item in score_breakdown:
        score = int(item["score"])
        checks.append(
            {
                "name": item["category"],
                "status": "fail" if score < 50 else "warn" if score < 70 else "pass",
                "message": f"{item['category']}评分 {score}。{item['message']}",
            }
        )
    checks.append(
        {
            "name": "综合质量等级",
            "status": "fail" if quality_level == "Weak" else "warn" if quality_level == "Watch" else "pass",
            "message": f"综合质量等级为 {quality_level}，总分 {total_quality_score}。",
        }
    )

    return {
        "summary": {
            "total_quality_score": total_quality_score,
            "quality_level": quality_level,
            "return_score": return_score,
            "drawdown_score": drawdown_score,
            "stability_score": stability_score,
            "out_of_sample_score": out_of_sample_score,
            "stress_score": stress_score,
            "data_quality_score": data_quality_score,
            "disclaimer": RESEARCH_DISCLAIMER,
        },
        "score_breakdown": score_breakdown,
        "warnings": warnings,
        "checks": checks,
    }
