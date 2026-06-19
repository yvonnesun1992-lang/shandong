from __future__ import annotations

import inspect

from src.reports import strategy_report_compare
from src.reports.strategy_report_compare import (
    RESEARCH_DISCLAIMER,
    compare_strategy_research_reports,
    export_strategy_report_comparison_csv,
)


def sample_report(
    report_id: str,
    strategy_name: str = "trend_default",
    quality_score: float = 72,
    max_drawdown: float = -0.12,
    total_return: float = 0.18,
    research_view: str = "Positive",
    quality_level: str = "Good",
    overfit_risk_level: str = "Medium",
    overall_stress_level: str = "Low",
    risk_highlights: list[str] | None = None,
) -> dict:
    return {
        "report_id": report_id,
        "generated_at": "2026-06-18T00:00:00+00:00",
        "strategy_name": strategy_name,
        "symbols": ["AAPL", "MSFT"],
        "research_view": research_view,
        "key_metrics": {
            "total_return": total_return,
            "max_drawdown": max_drawdown,
            "quality_score": quality_score,
            "quality_level": quality_level,
        },
        "quality_summary": {
            "total_quality_score": quality_score,
            "quality_level": quality_level,
        },
        "module_summaries": {
            "out_of_sample": {"overfit_risk_level": overfit_risk_level},
            "stress": {"overall_stress_level": overall_stress_level},
        },
        "risk_highlights": risk_highlights or ["回撤风险需要继续复盘。"],
        "warnings": [RESEARCH_DISCLAIMER],
        "disclaimer": RESEARCH_DISCLAIMER,
    }


def test_two_normal_reports_generate_comparison():
    comparison = compare_strategy_research_reports(
        [
            sample_report("strategy_report_20260618_100000_aaa111", quality_score=70),
            sample_report("strategy_report_20260618_110000_bbb222", quality_score=82),
        ]
    )

    assert comparison["comparison_summary"]["report_count"] == 2
    assert len(comparison["comparison_rows"]) == 2
    assert len(comparison["risk_rows"]) == 2
    assert comparison["best_report_id"] == "strategy_report_20260618_110000_bbb222"
    assert comparison["best_strategy_name"] == "trend_default"
    assert comparison["best_quality_score"] == 82.0
    assert comparison["disclaimer"] == RESEARCH_DISCLAIMER


def test_five_reports_generate_comparison():
    reports = [
        sample_report(f"strategy_report_20260618_10000{index}_{index}{index}{index}abc", quality_score=60 + index)
        for index in range(5)
    ]

    comparison = compare_strategy_research_reports(reports)

    assert comparison["comparison_summary"]["report_count"] == 5
    assert len(comparison["comparison_rows"]) == 5


def test_single_report_does_not_crash_and_returns_warning():
    comparison = compare_strategy_research_reports([sample_report("strategy_report_20260618_100000_aaa111")])

    assert comparison["comparison_summary"]["report_count"] == 1
    assert any("至少需要 2 份" in warning for warning in comparison["warnings"])


def test_missing_fields_do_not_crash():
    comparison = compare_strategy_research_reports([{}, {"strategy_name": "partial"}])

    assert comparison["comparison_summary"]["report_count"] == 2
    assert comparison["comparison_rows"][0]["strategy_name"] == "N/A"
    assert comparison["comparison_rows"][1]["strategy_name"] == "partial"


def test_best_report_id_uses_highest_quality_score():
    comparison = compare_strategy_research_reports(
        [
            sample_report("strategy_report_20260618_100000_aaa111", quality_score=61),
            sample_report("strategy_report_20260618_110000_bbb222", quality_score=88),
            sample_report("strategy_report_20260618_120000_ccc333", quality_score=73),
        ]
    )

    assert comparison["best_report_id"] == "strategy_report_20260618_110000_bbb222"


def test_best_report_tie_uses_lower_drawdown():
    comparison = compare_strategy_research_reports(
        [
            sample_report("strategy_report_20260618_100000_aaa111", quality_score=80, max_drawdown=-0.22),
            sample_report("strategy_report_20260618_110000_bbb222", quality_score=80, max_drawdown=-0.08),
        ]
    )

    assert comparison["best_report_id"] == "strategy_report_20260618_110000_bbb222"


def test_cautious_report_count_is_counted():
    comparison = compare_strategy_research_reports(
        [
            sample_report("strategy_report_20260618_100000_aaa111", research_view="Cautious"),
            sample_report("strategy_report_20260618_110000_bbb222", research_view="Positive"),
            sample_report("strategy_report_20260618_120000_ccc333", research_view="Cautious"),
        ]
    )

    assert comparison["comparison_summary"]["cautious_report_count"] == 2


def test_risk_rows_return_risk_count():
    comparison = compare_strategy_research_reports(
        [
            sample_report(
                "strategy_report_20260618_100000_aaa111",
                risk_highlights=["风险一", "风险二"],
            ),
            sample_report("strategy_report_20260618_110000_bbb222", risk_highlights=[]),
        ]
    )

    assert comparison["risk_rows"][0]["risk_count"] == 2
    assert comparison["risk_rows"][1]["risk_count"] == 1


def test_export_strategy_report_comparison_csv_returns_bytes():
    comparison = compare_strategy_research_reports(
        [
            sample_report("strategy_report_20260618_100000_aaa111"),
            sample_report("strategy_report_20260618_110000_bbb222"),
        ]
    )

    csv_bytes = export_strategy_report_comparison_csv(comparison["comparison_rows"])

    assert isinstance(csv_bytes, bytes)
    text = csv_bytes.decode("utf-8-sig")
    assert "report_id" in text
    assert "quality_score" in text
    assert "strategy_report_20260618_100000_aaa111" in text


def test_export_empty_strategy_report_comparison_csv_has_header():
    csv_bytes = export_strategy_report_comparison_csv([])

    assert isinstance(csv_bytes, bytes)
    assert "report_id" in csv_bytes.decode("utf-8-sig")


def test_comparison_does_not_generate_real_trade_advice():
    comparison = compare_strategy_research_reports(
        [
            sample_report("strategy_report_20260618_100000_aaa111"),
            sample_report("strategy_report_20260618_110000_bbb222"),
        ]
    )
    forbidden = ["建议买入", "建议卖出", "保证收益"]

    combined = str(comparison)
    for phrase in forbidden:
        assert phrase not in combined


def test_strategy_report_compare_module_keeps_research_only_boundaries():
    source = inspect.getsource(strategy_report_compare)
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
