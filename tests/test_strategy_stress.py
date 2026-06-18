from __future__ import annotations

import inspect

from src.strategies.stress_test import (
    RESEARCH_DISCLAIMER,
    build_strategy_stress_report,
)


def base_result() -> dict:
    return {
        "period_name": "Base",
        "total_return": 0.18,
        "annualized_return": 0.22,
        "max_drawdown": -0.12,
        "number_of_trades": 18,
        "final_portfolio_value": 118000,
        "initial_cash": 100000,
        "status": "success",
    }


def test_normal_base_result_generates_stress_report():
    report = build_strategy_stress_report(base_result())

    summary = report["summary"]
    assert summary["base_total_return"] == 0.18
    assert summary["base_max_drawdown"] == -0.12
    assert summary["overall_stress_level"] in {"Low", "Medium", "High"}
    assert summary["disclaimer"] == RESEARCH_DISCLAIMER
    assert len(report["scenario_results"]) == 3
    assert report["checks"]
    assert report["warnings"]


def test_default_three_stress_scenarios_exist():
    report = build_strategy_stress_report(base_result())

    scenario_names = [item["scenario_name"] for item in report["scenario_results"]]
    assert scenario_names == ["轻度压力", "中度压力", "重度压力"]


def test_severe_negative_return_is_medium_or_high_risk():
    report = build_strategy_stress_report(base_result())

    severe = next(item for item in report["scenario_results"] if item["scenario_name"] == "重度压力")
    assert severe["stressed_total_return"] < 0
    assert severe["scenario_risk_level"] in {"Medium", "High"}
    assert report["summary"]["overall_stress_level"] in {"Medium", "High"}


def test_drawdown_breach_creates_warning_or_fail_check():
    report = build_strategy_stress_report(base_result(), max_acceptable_drawdown=-0.15)

    assert any(item["drawdown_breach"] for item in report["scenario_results"])
    assert any("最大回撤超过可接受阈值" in warning for warning in report["warnings"])
    assert any(check["name"] == "回撤放大" and check["status"] in {"warn", "fail"} for check in report["checks"])


def test_failed_base_result_is_high_risk_without_crashing():
    failed_base = {**base_result(), "status": "failed", "error": "No symbols have enough data."}

    report = build_strategy_stress_report(failed_base)

    assert report["summary"]["overall_stress_level"] == "High"
    assert all(item["scenario_risk_level"] == "High" for item in report["scenario_results"])
    assert any(check["name"] == "基准情景" and check["status"] == "fail" for check in report["checks"])


def test_custom_scenarios_are_applied():
    scenarios = [
        {"scenario_name": "自定义压力", "return_shock": -0.05, "drawdown_multiplier": 1.10},
    ]

    report = build_strategy_stress_report(base_result(), scenarios=scenarios)

    assert len(report["scenario_results"]) == 1
    scenario = report["scenario_results"][0]
    assert scenario["scenario_name"] == "自定义压力"
    assert scenario["stressed_total_return"] == 0.13
    assert round(scenario["stressed_max_drawdown"], 3) == -0.132


def test_invalid_scenario_parameters_do_not_crash():
    scenarios = [
        {"scenario_name": "参数异常", "return_shock": -0.05, "drawdown_multiplier": -2.0},
    ]

    report = build_strategy_stress_report(base_result(), scenarios=scenarios)

    assert report["scenario_results"][0]["drawdown_multiplier"] == 1.0
    assert any("回撤放大倍数无效" in warning for warning in report["warnings"])


def test_scenario_results_return_required_fields():
    report = build_strategy_stress_report(base_result())

    required_fields = {
        "scenario_name",
        "stressed_total_return",
        "stressed_max_drawdown",
        "stressed_final_value",
        "estimated_loss_value",
        "drawdown_breach",
        "scenario_risk_level",
    }
    for scenario in report["scenario_results"]:
        assert required_fields.issubset(scenario)


def test_all_positive_scenarios_with_drawdown_inside_limit_can_be_low():
    scenarios = [
        {"scenario_name": "轻度压力", "return_shock": -0.02, "drawdown_multiplier": 1.05},
    ]

    report = build_strategy_stress_report(base_result(), scenarios=scenarios, max_acceptable_drawdown=-0.25)

    assert report["summary"]["overall_stress_level"] == "Low"


def test_overall_stress_level_is_returned():
    report = build_strategy_stress_report(base_result())

    assert report["summary"]["overall_stress_level"] in {"Low", "Medium", "High"}


def test_strategy_stress_module_keeps_research_only_boundaries():
    import src.strategies.stress_test as stress_test

    source = inspect.getsource(stress_test)
    forbidden = [
        "IB" + "KR",
        "富" + "途",
        "Al" + "paca",
        "Robin" + "hood",
        "broker " + "order",
        "place_" + "order",
        "real " + "trade",
        "api_" + "key",
        "sec" + "ret",
        "pass" + "word",
        "tok" + "en",
        "Open" + "AI API",
        "AI " + "prediction",
        "eval(",
        "exec(",
    ]
    for word in forbidden:
        assert word not in source
