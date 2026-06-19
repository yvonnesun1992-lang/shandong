from __future__ import annotations

import inspect

from src.reports import strategy_report_trend
from src.reports.strategy_report_trend import (
    RESEARCH_DISCLAIMER,
    build_strategy_report_trend,
    export_strategy_report_trend_csv,
)


def sample_report(
    report_id: str,
    strategy_name: str = "trend_default",
    generated_at: str = "2026-06-18T00:00:00+00:00",
    saved_at: str = "2026-06-18T01:00:00",
    quality_score: float = 70,
    max_drawdown: float = -0.12,
    total_return: float = 0.18,
    research_view: str = "Neutral",
    quality_level: str = "Good",
    overfit_risk_level: str = "Medium",
    overall_stress_level: str = "Low",
    risk_highlights: list[str] | None = None,
) -> dict:
    return {
        "report_id": report_id,
        "generated_at": generated_at,
        "saved_at": saved_at,
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


def test_two_same_strategy_reports_generate_trend():
    trend = build_strategy_report_trend(
        [
            sample_report("strategy_report_20260618_100000_aaa111", quality_score=70),
            sample_report("strategy_report_20260619_100000_bbb222", quality_score=78),
        ],
        "trend_default",
    )

    assert trend["trend_summary"]["strategy_name"] == "trend_default"
    assert trend["trend_summary"]["report_count"] == 2
    assert len(trend["trend_rows"]) == 2
    assert len(trend["risk_trend_rows"]) == 2
    assert trend["trend_summary"]["latest_report_id"] == "strategy_report_20260619_100000_bbb222"
    assert trend["disclaimer"] == RESEARCH_DISCLAIMER


def test_single_report_is_insufficient():
    trend = build_strategy_report_trend([sample_report("strategy_report_20260618_100000_aaa111")])

    assert trend["trend_summary"]["trend_view"] == "Insufficient"
    assert any("至少需要 2 份" in warning for warning in trend["warnings"])


def test_missing_fields_do_not_crash():
    trend = build_strategy_report_trend([{}, {"strategy_name": "partial"}], "partial")

    assert trend["trend_summary"]["strategy_name"] == "partial"
    assert trend["trend_summary"]["report_count"] == 1
    assert trend["trend_rows"][0]["strategy_name"] == "partial"


def test_quality_score_rise_is_improving():
    trend = build_strategy_report_trend(
        [
            sample_report("strategy_report_20260618_100000_aaa111", quality_score=62, max_drawdown=-0.12),
            sample_report("strategy_report_20260619_100000_bbb222", quality_score=70, max_drawdown=-0.13),
        ]
    )

    assert trend["trend_summary"]["trend_view"] == "Improving"


def test_quality_score_drop_is_deteriorating():
    trend = build_strategy_report_trend(
        [
            sample_report("strategy_report_20260618_100000_aaa111", quality_score=76),
            sample_report("strategy_report_20260619_100000_bbb222", quality_score=68),
        ]
    )

    assert trend["trend_summary"]["trend_view"] == "Deteriorating"


def test_drawdown_worsening_is_deteriorating():
    trend = build_strategy_report_trend(
        [
            sample_report("strategy_report_20260618_100000_aaa111", quality_score=76, max_drawdown=-0.10),
            sample_report("strategy_report_20260619_100000_bbb222", quality_score=78, max_drawdown=-0.22),
        ]
    )

    assert trend["trend_summary"]["trend_view"] == "Deteriorating"


def test_small_changes_are_stable():
    trend = build_strategy_report_trend(
        [
            sample_report("strategy_report_20260618_100000_aaa111", quality_score=70, max_drawdown=-0.12),
            sample_report("strategy_report_20260619_100000_bbb222", quality_score=73, max_drawdown=-0.13),
        ]
    )

    assert trend["trend_summary"]["trend_view"] == "Stable"


def test_can_filter_by_strategy_name():
    trend = build_strategy_report_trend(
        [
            sample_report("strategy_report_20260618_100000_aaa111", strategy_name="trend_default"),
            sample_report("strategy_report_20260619_100000_bbb222", strategy_name="breakout"),
            sample_report("strategy_report_20260620_100000_ccc333", strategy_name="breakout"),
        ],
        "breakout",
    )

    assert trend["trend_summary"]["strategy_name"] == "breakout"
    assert trend["trend_summary"]["report_count"] == 2
    assert all(row["strategy_name"] == "breakout" for row in trend["trend_rows"])


def test_risk_trend_rows_return_risk_count():
    trend = build_strategy_report_trend(
        [
            sample_report("strategy_report_20260618_100000_aaa111", risk_highlights=["风险一", "风险二"]),
            sample_report("strategy_report_20260619_100000_bbb222", risk_highlights=[]),
        ]
    )

    assert trend["risk_trend_rows"][0]["risk_count"] == 2
    assert trend["risk_trend_rows"][1]["risk_count"] == 1


def test_export_strategy_report_trend_csv_returns_bytes():
    trend = build_strategy_report_trend(
        [
            sample_report("strategy_report_20260618_100000_aaa111"),
            sample_report("strategy_report_20260619_100000_bbb222"),
        ]
    )

    csv_bytes = export_strategy_report_trend_csv(trend["trend_rows"])

    assert isinstance(csv_bytes, bytes)
    text = csv_bytes.decode("utf-8-sig")
    assert "report_id" in text
    assert "quality_score" in text
    assert "strategy_report_20260618_100000_aaa111" in text


def test_export_empty_strategy_report_trend_csv_has_header():
    csv_bytes = export_strategy_report_trend_csv([])

    assert isinstance(csv_bytes, bytes)
    assert "report_id" in csv_bytes.decode("utf-8-sig")


def test_trend_does_not_generate_real_trade_advice():
    trend = build_strategy_report_trend(
        [
            sample_report("strategy_report_20260618_100000_aaa111"),
            sample_report("strategy_report_20260619_100000_bbb222"),
        ]
    )
    forbidden = ["建议买入", "建议卖出", "保证收益"]

    combined = str(trend)
    for phrase in forbidden:
        assert phrase not in combined


def test_strategy_report_trend_module_keeps_research_only_boundaries():
    source = inspect.getsource(strategy_report_trend)
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
