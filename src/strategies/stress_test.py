from __future__ import annotations

from typing import Any


RESEARCH_DISCLAIMER = "仅供投资研究，不构成投资建议，不代表未来收益。"

DEFAULT_STRESS_SCENARIOS = [
    {"scenario_name": "轻度压力", "return_shock": -0.10, "drawdown_multiplier": 1.25},
    {"scenario_name": "中度压力", "return_shock": -0.20, "drawdown_multiplier": 1.75},
    {"scenario_name": "重度压力", "return_shock": -0.35, "drawdown_multiplier": 2.50},
]


def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_status(result: dict[str, Any]) -> str:
    status = str(result.get("status", "success")).strip().lower()
    return status or "success"


def _clean_base_result(base_result: dict[str, Any]) -> dict[str, Any]:
    initial_cash = _safe_float(base_result.get("initial_cash"), 0.0)
    final_value = _safe_float(base_result.get("final_portfolio_value"), 0.0)
    total_return = _safe_float(base_result.get("total_return"), 0.0)
    if initial_cash <= 0 and final_value > 0:
        initial_cash = final_value / (1 + total_return) if total_return > -0.999999 else final_value
    if initial_cash <= 0:
        initial_cash = 100000.0
    return {
        "period_name": str(base_result.get("period_name", "Base")).strip() or "Base",
        "total_return": total_return,
        "annualized_return": _safe_float(base_result.get("annualized_return"), 0.0),
        "max_drawdown": _safe_float(base_result.get("max_drawdown"), 0.0),
        "number_of_trades": int(_safe_float(base_result.get("number_of_trades"), 0.0)),
        "final_portfolio_value": final_value,
        "initial_cash": initial_cash,
        "status": _safe_status(base_result),
        "error": str(base_result.get("error", "")).strip(),
    }


def _clean_scenarios(scenarios: list[dict] | None) -> tuple[list[dict], list[str]]:
    warnings = []
    raw_scenarios = scenarios if scenarios else DEFAULT_STRESS_SCENARIOS
    clean_scenarios = []
    for index, scenario in enumerate(raw_scenarios, start=1):
        if not isinstance(scenario, dict):
            warnings.append(f"压力情景 {index} 格式无效，已跳过。")
            continue
        scenario_name = str(scenario.get("scenario_name", f"压力情景 {index}")).strip() or f"压力情景 {index}"
        return_shock = _safe_float(scenario.get("return_shock"), 0.0)
        drawdown_multiplier = _safe_float(scenario.get("drawdown_multiplier"), 1.0)
        if drawdown_multiplier <= 0:
            warnings.append(f"{scenario_name} 的回撤放大倍数无效，已改为 1.0。")
            drawdown_multiplier = 1.0
        clean_scenarios.append(
            {
                "scenario_name": scenario_name,
                "return_shock": return_shock,
                "drawdown_multiplier": drawdown_multiplier,
            }
        )
    if not clean_scenarios:
        warnings.append("没有有效压力情景，已使用默认压力情景。")
        clean_scenarios = [dict(item) for item in DEFAULT_STRESS_SCENARIOS]
    return clean_scenarios, warnings


def _scenario_risk_level(
    stressed_total_return: float,
    drawdown_breach: bool,
    scenario_name: str,
) -> str:
    is_heavy = "重度" in scenario_name or "severe" in scenario_name.lower()
    if stressed_total_return < 0 and drawdown_breach:
        return "High"
    if is_heavy and (stressed_total_return < 0 or drawdown_breach):
        return "High"
    if stressed_total_return < 0 or drawdown_breach:
        return "Medium"
    return "Low"


def _overall_level(scenario_results: list[dict], base_failed: bool) -> str:
    if base_failed:
        return "High"
    levels = {str(result.get("scenario_risk_level", "Low")) for result in scenario_results}
    if "High" in levels:
        return "High"
    if "Medium" in levels:
        return "Medium"
    return "Low"


def build_strategy_stress_report(
    base_result: dict,
    scenarios: list[dict] | None = None,
    max_acceptable_drawdown: float = -0.25,
) -> dict:
    """Build stress scenarios from an existing portfolio backtest summary."""
    base = _clean_base_result(base_result or {})
    max_acceptable_drawdown = -abs(_safe_float(max_acceptable_drawdown, -0.25) or 0.25)
    clean_scenarios, warnings = _clean_scenarios(scenarios)
    warnings.insert(0, RESEARCH_DISCLAIMER)

    base_failed = base["status"] != "success"
    if base_failed:
        warnings.append("基准情景回测失败，压力测试结果仅记录失败状态。")

    scenario_results = []
    for scenario in clean_scenarios:
        stressed_total_return = base["total_return"] + scenario["return_shock"]
        stressed_max_drawdown = -abs(base["max_drawdown"]) * scenario["drawdown_multiplier"]
        stressed_final_value = base["initial_cash"] * (1 + stressed_total_return)
        estimated_loss_value = max(base["initial_cash"] - stressed_final_value, 0.0)
        drawdown_breach = stressed_max_drawdown < max_acceptable_drawdown
        scenario_risk_level = _scenario_risk_level(
            stressed_total_return,
            drawdown_breach,
            scenario["scenario_name"],
        )

        if base_failed:
            stressed_total_return = 0.0
            stressed_max_drawdown = 0.0
            stressed_final_value = 0.0
            estimated_loss_value = base["initial_cash"]
            drawdown_breach = True
            scenario_risk_level = "High"

        scenario_results.append(
            {
                "scenario_name": scenario["scenario_name"],
                "return_shock": scenario["return_shock"],
                "drawdown_multiplier": scenario["drawdown_multiplier"],
                "base_total_return": base["total_return"],
                "stressed_total_return": stressed_total_return,
                "base_max_drawdown": base["max_drawdown"],
                "stressed_max_drawdown": stressed_max_drawdown,
                "stressed_final_value": stressed_final_value,
                "estimated_loss_value": estimated_loss_value,
                "drawdown_breach": drawdown_breach,
                "scenario_risk_level": scenario_risk_level,
                "status": "failed" if base_failed else "success",
            }
        )

    if any(result["stressed_total_return"] < 0 for result in scenario_results):
        warnings.append("部分压力情景下收益为负，需关注资金损失风险。")
    if any(result["drawdown_breach"] for result in scenario_results):
        warnings.append("部分压力情景下最大回撤超过可接受阈值。")
    if base["number_of_trades"] <= 0:
        warnings.append("基准回测交易次数较少，压力测试样本质量有限。")

    worst_return_result = min(scenario_results, key=lambda item: item["stressed_total_return"])
    worst_drawdown_result = min(scenario_results, key=lambda item: item["stressed_max_drawdown"])
    worst_loss_result = max(scenario_results, key=lambda item: item["estimated_loss_value"])
    overall_stress_level = _overall_level(scenario_results, base_failed)

    checks = [
        {
            "name": "基准情景",
            "status": "pass" if not base_failed else "fail",
            "message": f"基准收益 {base['total_return']:.2%}，最大回撤 {base['max_drawdown']:.2%}。",
        },
        {
            "name": "收益下修",
            "status": "fail"
            if any(result["scenario_risk_level"] == "High" for result in scenario_results)
            else "warn"
            if any(result["stressed_total_return"] < 0 for result in scenario_results)
            else "pass",
            "message": f"最差压力收益 {worst_return_result['stressed_total_return']:.2%}。",
        },
        {
            "name": "回撤放大",
            "status": "warn" if any(result["drawdown_breach"] for result in scenario_results) else "pass",
            "message": f"最差压力回撤 {worst_drawdown_result['stressed_max_drawdown']:.2%}。",
        },
        {
            "name": "资金损失风险",
            "status": "warn" if worst_loss_result["estimated_loss_value"] > 0 else "pass",
            "message": f"最大估算损失 {worst_loss_result['estimated_loss_value']:.2f}。",
        },
        {
            "name": "数据质量风险",
            "status": "warn" if base["number_of_trades"] <= 0 else "pass",
            "message": f"基准回测交易次数 {base['number_of_trades']}。",
        },
        {
            "name": "总体压力等级",
            "status": "fail" if overall_stress_level == "High" else "warn" if overall_stress_level == "Medium" else "pass",
            "message": f"总体压力等级为 {overall_stress_level}。",
        },
    ]

    return {
        "summary": {
            "base_total_return": base["total_return"],
            "base_max_drawdown": base["max_drawdown"],
            "base_final_portfolio_value": base["final_portfolio_value"],
            "base_trades": base["number_of_trades"],
            "max_acceptable_drawdown": max_acceptable_drawdown,
            "worst_scenario_name": worst_return_result["scenario_name"],
            "worst_stressed_return": worst_return_result["stressed_total_return"],
            "worst_stressed_drawdown": worst_drawdown_result["stressed_max_drawdown"],
            "worst_estimated_loss": worst_loss_result["estimated_loss_value"],
            "overall_stress_level": overall_stress_level,
            "disclaimer": RESEARCH_DISCLAIMER,
        },
        "scenario_results": scenario_results,
        "warnings": warnings,
        "checks": checks,
    }
