from __future__ import annotations

import inspect
import time
from pathlib import Path

from src.core.cache_manager import StrategyCacheManager, build_cache_key
from src.core.standard_report import StandardReportV1, validate_standard_report


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_cache_works_with_ttl():
    cache = StrategyCacheManager(default_ttl_seconds=1)
    key = build_cache_key("trend_default", "us_default", "baseline", {"max_position": 0.15})

    cache.set(key, {"result": "cached"})
    assert cache.get(key) == {"result": "cached"}
    assert cache.stats()["hit_count"] == 1

    time.sleep(1.05)
    assert cache.get(key) is None
    assert cache.stats()["expired_count"] == 1


def test_cache_key_is_stable_for_params_order():
    first = build_cache_key("trend_default", "us_default", "baseline", {"b": 2, "a": 1})
    second = build_cache_key("trend_default", "us_default", "baseline", {"a": 1, "b": 2})

    assert first == second


def test_standard_report_structure_valid():
    report = StandardReportV1(
        strategy_name="trend_default",
        generated_at="2026-06-19T00:00:00+00:00",
        backtest_summary={"total_return": 0.18},
        quality_summary={"total_quality_score": 78},
        risk_summary={"risk_level": "Low"},
        stability_summary={"stability_level": "Medium"},
        out_of_sample_summary={"overfit_risk_level": "Low"},
        stress_summary={"overall_stress_level": "Low"},
    )

    payload = report.to_dict()

    assert validate_standard_report(payload)["valid"] is True
    assert payload["schema_version"] == "StandardReportV1"
    assert payload["strategy_name"] == "trend_default"


def test_invalid_standard_report_reports_missing_fields():
    result = validate_standard_report({"strategy_name": "trend_default"})

    assert result["valid"] is False
    assert "backtest_summary" in result["missing_fields"]


def test_control_center_loads_in_app_main():
    source = PROJECT_ROOT.joinpath("app/main.py").read_text(encoding="utf-8")

    assert "Strategy Control Center" in source
    assert "首页总览" in source
    assert "生成策略研究报告" in source
    assert "历史报告管理" in source
    assert "策略研究看板" in source
    assert "系统健康面板" in source


def test_no_breaking_report_modules_still_import():
    import src.reports.strategy_research_dashboard as dashboard
    import src.reports.strategy_report_archive as archive
    import src.reports.strategy_report_compare as compare
    import src.reports.strategy_report_trend as trend

    assert hasattr(archive, "list_strategy_research_reports")
    assert hasattr(compare, "compare_strategy_research_reports")
    assert hasattr(trend, "build_strategy_report_trend")
    assert hasattr(dashboard, "build_strategy_research_dashboard")


def test_v129_modules_keep_research_only_boundaries():
    import src.core.cache_manager as cache_manager
    import src.core.standard_report as standard_report

    combined = "\n".join(
        [
            inspect.getsource(cache_manager),
            inspect.getsource(standard_report),
            PROJECT_ROOT.joinpath("app/main.py").read_text(encoding="utf-8"),
        ]
    )
    forbidden = [
        "IB" + "KR",
        "富" + "途",
        "Al" + "paca",
        "Robin" + "hood",
        "broker " + "order",
        "place_" + "order",
        "real " + "trade",
        "api_" + "key=",
        "sec" + "ret=",
        "tok" + "en=",
        "Open" + "AI API",
        "AI " + "prediction",
        "eval(",
        "exec(",
    ]
    for word in forbidden:
        assert word not in combined
