from __future__ import annotations

import inspect

from src.core.cache_manager import StrategyCacheManager, build_cache_key
from src.core.report_pipeline import generate_full_strategy_report
from src.core.standard_report import StandardReportV1, validate_standard_report
from src.ui.layout import safe_render


def test_cache_auto_invalidation_when_context_changes():
    cache = StrategyCacheManager(default_ttl_seconds=60)
    cache.update_context(strategy="trend_default", watchlist="us_default", preset="baseline")
    key = build_cache_key("trend_default", "us_default", "baseline", {"window": 20})
    cache.set_dashboard(key, {"dashboard": "cached"})
    assert cache.get_dashboard(key) == {"dashboard": "cached"}

    cache.update_context(strategy="trend_default", watchlist="cn_default", preset="baseline")

    assert cache.get_dashboard(key) is None
    assert cache.stats()["cache_size"] == 0


def test_cache_named_result_helpers_work():
    cache = StrategyCacheManager(default_ttl_seconds=60)
    key = build_cache_key("trend_default", "us_default", "baseline", {})

    cache.set_report(key, {"report": 1})
    cache.set_compare(key, {"compare": 1})
    cache.set_trend(key, {"trend": 1})

    assert cache.get_report(key) == {"report": 1}
    assert cache.get_compare(key) == {"compare": 1}
    assert cache.get_trend(key) == {"trend": 1}


def test_standard_report_v1_enhanced_fields_are_valid():
    report = StandardReportV1(
        strategy_name="trend_default",
        generated_at="2026-06-19T00:00:00+00:00",
        backtest_summary={"total_return": 0.18},
        quality_summary={"total_quality_score": 78},
        risk_summary={"risk_level": "Low"},
        confidence_level="Medium",
        data_freshness_score=92,
        stability_index=0.71,
    ).to_dict()

    assert report["confidence_level"] == "Medium"
    assert report["data_freshness_score"] == 92.0
    assert report["stability_index"] == 0.71
    assert validate_standard_report(report)["valid"] is True


def test_report_pipeline_generates_research_report_without_archive():
    result = generate_full_strategy_report(
        strategy_name="trend_default",
        symbols=["AAPL", "MSFT"],
        backtest_summary={
            "total_return": 0.12,
            "annualized_return": 0.10,
            "max_drawdown": -0.08,
            "number_of_trades": 8,
            "final_portfolio_value": 112000,
            "status": "success",
        },
        risk_summary={"risk_level": "Low"},
        archive=False,
    )

    assert result["status"] == "success"
    assert result["report"]["strategy_name"] == "trend_default"
    assert result["standard_report"]["schema_version"] == "StandardReportV1"
    assert result["archive"] == {}


def test_report_pipeline_handles_empty_data_safely():
    result = generate_full_strategy_report(strategy_name="", symbols=[], backtest_summary={}, archive=False)

    assert result["status"] == "success"
    assert result["report"]["strategy_name"] == "Unnamed strategy"
    assert result["standard_validation"]["valid"] is True


def test_safe_render_returns_fallback_on_error():
    def broken_renderer():
        raise ValueError("bad report")

    result = safe_render(broken_renderer, fallback="fallback")

    assert result["ok"] is False
    assert result["fallback"] == "fallback"
    assert "bad report" in result["error"]


def test_v130_modules_keep_research_only_boundaries():
    import src.core.cache_manager as cache_manager
    import src.core.report_pipeline as report_pipeline
    import src.core.standard_report as standard_report

    combined = "\n".join(
        [
            inspect.getsource(cache_manager),
            inspect.getsource(report_pipeline),
            inspect.getsource(standard_report),
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
