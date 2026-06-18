from __future__ import annotations

import inspect

from src.risk.control import RESEARCH_DISCLAIMER, build_risk_control_report


def sample_allocation_rows() -> list[dict]:
    return [
        {"symbol": "AAPL", "target_weight": 0.18, "target_value": 18000},
        {"symbol": "MSFT", "target_weight": 0.15, "target_value": 15000},
        {"symbol": "NVDA", "target_weight": 0.12, "target_value": 12000},
        {"symbol": "GOOGL", "target_weight": 0.10, "target_value": 10000},
        {"symbol": "META", "target_weight": 0.08, "target_value": 8000},
        {"symbol": "AMD", "target_weight": 0.07, "target_value": 7000},
    ]


def test_normal_allocation_rows_generate_risk_report():
    report = build_risk_control_report(sample_allocation_rows())

    assert report["summary"]["portfolio_value"] == 100000
    assert report["summary"]["total_target_value"] == 70000
    assert report["summary"]["cash_buffer_value"] == 30000
    assert report["summary"]["number_of_positions"] == 6
    assert report["summary"]["risk_level"] in {"Low", "Medium", "High"}
    assert report["summary"]["disclaimer"] == RESEARCH_DISCLAIMER
    assert report["position_risks"] == []
    assert report["checks"]


def test_overweight_symbol_creates_fail_and_warning():
    report = build_risk_control_report(
        [{"symbol": "AAPL", "target_weight": 0.25, "target_value": 25000}],
        max_position_pct=0.2,
    )

    assert "AAPL" in report["overweight_symbols"]
    assert any(risk["risk"] == "单股仓位超过限制" for risk in report["position_risks"])
    assert any(check["name"] == "仓位风险" and check["status"] == "fail" for check in report["checks"])
    assert any("单股仓位超过限制" in warning for warning in report["warnings"])


def test_top3_concentration_creates_fail():
    report = build_risk_control_report(
        [
            {"symbol": "AAPL", "target_weight": 0.25, "target_value": 25000},
            {"symbol": "MSFT", "target_weight": 0.20, "target_value": 20000},
            {"symbol": "NVDA", "target_weight": 0.15, "target_value": 15000},
            {"symbol": "AMD", "target_weight": 0.05, "target_value": 5000},
        ],
        max_position_pct=0.3,
        max_top3_pct=0.5,
    )

    assert report["summary"]["top3_position_pct"] == 0.6
    assert any(check["name"] == "集中度风险" and check["status"] == "fail" for check in report["checks"])
    assert any("前三大持仓占比过高" in warning for warning in report["warnings"])


def test_too_few_positions_warns_about_diversification():
    report = build_risk_control_report(
        [{"symbol": "AAPL", "target_weight": 0.2, "target_value": 20000}],
        min_positions=5,
    )

    assert report["summary"]["number_of_positions"] == 1
    assert any(check["name"] == "分散度风险" and check["status"] == "warn" for check in report["checks"])
    assert any("分散度不足" in warning for warning in report["warnings"])


def test_low_cash_buffer_warns():
    report = build_risk_control_report(sample_allocation_rows(), cash_buffer_pct=0.03)

    assert any(check["name"] == "现金缓冲风险" and check["status"] == "warn" for check in report["checks"])
    assert any("现金缓冲偏低" in warning for warning in report["warnings"])


def test_empty_allocation_rows_do_not_crash():
    report = build_risk_control_report([])

    assert report["summary"]["total_target_value"] == 0
    assert report["summary"]["number_of_positions"] == 0
    assert report["summary"]["risk_level"] in {"Medium", "High"}
    assert any("目标仓位数据为空" in warning for warning in report["warnings"])


def test_non_positive_portfolio_value_does_not_crash():
    report = build_risk_control_report(
        [{"symbol": "AAPL", "target_weight": 0.2, "target_value": 20000}],
        portfolio_value=0,
    )

    assert report["summary"]["portfolio_value"] == 0
    assert report["summary"]["invested_pct"] == 0
    assert any("组合总金额无效" in warning for warning in report["warnings"])
    assert any(check["name"] == "数据质量风险" and check["status"] == "fail" for check in report["checks"])


def test_missing_weight_or_value_is_handled():
    report = build_risk_control_report(
        [
            {"symbol": "AAPL", "target_value": 15000},
            {"symbol": "MSFT", "target_weight": 0.1},
            {"symbol": "BAD"},
        ],
        portfolio_value=100000,
    )

    assert report["summary"]["number_of_positions"] == 2
    assert any("BAD" in warning for warning in report["warnings"])
    assert any(check["name"] == "数据质量风险" and check["status"] == "warn" for check in report["checks"])


def test_risk_control_module_keeps_research_only_boundaries():
    import src.risk.control as control

    source = inspect.getsource(control)
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
