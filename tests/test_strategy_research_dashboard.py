from __future__ import annotations

import inspect

from src.reports import strategy_research_dashboard
from src.reports.strategy_research_dashboard import (
    RESEARCH_DISCLAIMER,
    build_strategy_research_dashboard,
    export_strategy_dashboard_csv,
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


def test_multiple_strategy_reports_generate_dashboard():
    dashboard = build_strategy_research_dashboard(
        [
            sample_report("strategy_report_20260618_100000_aaa111", "trend_default"),
            sample_report("strategy_report_20260619_100000_bbb222", "breakout"),
        ]
    )

    assert dashboard["dashboard_summary"]["strategy_count"] == 2
    assert dashboard["dashboard_summary"]["total_report_count"] == 2
    assert len(dashboard["strategy_rows"]) == 2
    assert dashboard["disclaimer"] == RESEARCH_DISCLAIMER


def test_same_strategy_uses_latest_report():
    dashboard = build_strategy_research_dashboard(
        [
            sample_report(
                "strategy_report_20260618_100000_aaa111",
                "trend_default",
                generated_at="2026-06-18T00:00:00+00:00",
                quality_score=60,
            ),
            sample_report(
                "strategy_report_20260619_100000_bbb222",
                "trend_default",
                generated_at="2026-06-19T00:00:00+00:00",
                quality_score=82,
            ),
        ]
    )

    row = dashboard["strategy_rows"][0]
    assert row["latest_report_id"] == "strategy_report_20260619_100000_bbb222"
    assert row["latest_quality_score"] == 82.0


def test_empty_reports_do_not_crash():
    dashboard = build_strategy_research_dashboard([])

    assert dashboard["dashboard_summary"]["strategy_count"] == 0
    assert dashboard["strategy_rows"] == []
    assert any("暂无" in warning for warning in dashboard["warnings"])


def test_missing_fields_do_not_crash():
    dashboard = build_strategy_research_dashboard([{}, {"strategy_name": "partial"}])

    assert dashboard["dashboard_summary"]["strategy_count"] >= 1
    assert any(row["strategy_name"] == "partial" for row in dashboard["strategy_rows"])


def test_high_priority_is_assigned():
    dashboard = build_strategy_research_dashboard(
        [
            sample_report("strategy_report_20260618_100000_aaa111", quality_score=74, max_drawdown=-0.12),
            sample_report("strategy_report_20260619_100000_bbb222", quality_score=82, max_drawdown=-0.13),
        ]
    )

    assert dashboard["strategy_rows"][0]["research_priority"] == "High"


def test_low_priority_is_assigned():
    dashboard = build_strategy_research_dashboard(
        [
            sample_report("strategy_report_20260618_100000_aaa111", quality_score=76, research_view="Positive"),
            sample_report("strategy_report_20260619_100000_bbb222", quality_score=52, research_view="Cautious"),
        ]
    )

    assert dashboard["strategy_rows"][0]["research_priority"] == "Low"


def test_watch_priority_is_assigned_for_one_report():
    dashboard = build_strategy_research_dashboard(
        [sample_report("strategy_report_20260618_100000_aaa111", quality_score=88, research_view="Positive")]
    )

    assert dashboard["strategy_rows"][0]["research_priority"] == "Watch"


def test_counts_strategy_and_reports():
    dashboard = build_strategy_research_dashboard(
        [
            sample_report("strategy_report_20260618_100000_aaa111", "trend_default"),
            sample_report("strategy_report_20260619_100000_bbb222", "trend_default"),
            sample_report("strategy_report_20260620_100000_ccc333", "breakout"),
        ]
    )

    assert dashboard["dashboard_summary"]["strategy_count"] == 2
    assert dashboard["dashboard_summary"]["total_report_count"] == 3


def test_counts_improving_deteriorating_and_cautious():
    dashboard = build_strategy_research_dashboard(
        [
            sample_report("strategy_report_20260618_100000_aaa111", "up", quality_score=62),
            sample_report("strategy_report_20260619_100000_bbb222", "up", quality_score=72),
            sample_report("strategy_report_20260618_100000_ccc333", "down", quality_score=78),
            sample_report("strategy_report_20260619_100000_ddd444", "down", quality_score=66, research_view="Cautious"),
        ]
    )

    summary = dashboard["dashboard_summary"]
    assert summary["improving_strategy_count"] == 1
    assert summary["deteriorating_strategy_count"] == 1
    assert summary["cautious_strategy_count"] == 1


def test_best_strategy_name_uses_highest_quality_score():
    dashboard = build_strategy_research_dashboard(
        [
            sample_report("strategy_report_20260618_100000_aaa111", "trend_default", quality_score=71),
            sample_report("strategy_report_20260619_100000_bbb222", "breakout", quality_score=85),
        ]
    )

    assert dashboard["dashboard_summary"]["best_strategy_name"] == "breakout"
    assert dashboard["dashboard_summary"]["best_quality_score"] == 85.0


def test_risk_rows_return_high_risk_strategies():
    dashboard = build_strategy_research_dashboard(
        [
            sample_report("strategy_report_20260618_100000_aaa111", "quiet", quality_score=72),
            sample_report(
                "strategy_report_20260619_100000_bbb222",
                "risky",
                quality_score=60,
                research_view="Cautious",
                overfit_risk_level="High",
                overall_stress_level="High",
                risk_highlights=["风险一", "风险二", "风险三"],
            ),
        ]
    )

    assert any(row["strategy_name"] == "risky" for row in dashboard["risk_rows"])
    risky_row = next(row for row in dashboard["risk_rows"] if row["strategy_name"] == "risky")
    assert risky_row["risk_count"] == 3


def test_export_strategy_dashboard_csv_returns_bytes():
    dashboard = build_strategy_research_dashboard(
        [
            sample_report("strategy_report_20260618_100000_aaa111", "trend_default"),
            sample_report("strategy_report_20260619_100000_bbb222", "breakout"),
        ]
    )

    csv_bytes = export_strategy_dashboard_csv(dashboard["strategy_rows"])

    assert isinstance(csv_bytes, bytes)
    text = csv_bytes.decode("utf-8-sig")
    assert "strategy_name" in text
    assert "trend_default" in text


def test_export_empty_strategy_dashboard_csv_has_header():
    csv_bytes = export_strategy_dashboard_csv([])

    assert isinstance(csv_bytes, bytes)
    assert "strategy_name" in csv_bytes.decode("utf-8-sig")


def test_dashboard_does_not_generate_real_trade_advice():
    dashboard = build_strategy_research_dashboard(
        [
            sample_report("strategy_report_20260618_100000_aaa111", "trend_default"),
            sample_report("strategy_report_20260619_100000_bbb222", "breakout"),
        ]
    )
    forbidden = ["建议买入", "建议卖出", "保证收益"]

    combined = str(dashboard)
    for phrase in forbidden:
        assert phrase not in combined


def test_strategy_research_dashboard_module_keeps_research_only_boundaries():
    source = inspect.getsource(strategy_research_dashboard)
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
