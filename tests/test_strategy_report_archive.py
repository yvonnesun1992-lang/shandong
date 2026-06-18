from __future__ import annotations

import inspect

import pytest

from src.reports import strategy_report_archive
from src.reports.strategy_report_archive import (
    delete_strategy_research_report,
    export_strategy_report_summary_csv,
    list_strategy_research_reports,
    load_strategy_research_report,
    save_strategy_research_report,
)


def sample_report() -> dict:
    return {
        "report_title": "Strategy Research Report - trend_default",
        "strategy_name": "trend_default",
        "symbols": ["AAPL", "MSFT"],
        "generated_at": "2026-06-18T00:00:00+00:00",
        "research_view": "Positive",
        "key_metrics": {
            "total_return": 0.18,
            "max_drawdown": -0.12,
            "quality_score": 72,
            "quality_level": "Good",
        },
        "quality_summary": {
            "total_quality_score": 72,
            "quality_level": "Good",
        },
        "risk_highlights": ["仅供研究。"],
        "warnings": ["仅供投资研究，不构成投资建议，不代表未来收益。"],
        "disclaimer": "仅供投资研究，不构成投资建议，不代表未来收益。",
    }


@pytest.fixture
def archive_dir(tmp_path, monkeypatch):
    target = tmp_path / "strategy_research_reports"
    monkeypatch.setattr(strategy_report_archive, "DEFAULT_STRATEGY_REPORT_ARCHIVE_DIR", target)
    return target


def test_save_strategy_research_report_saves_json(archive_dir):
    saved = save_strategy_research_report(sample_report())

    assert saved["report_id"].startswith("strategy_report_")
    assert saved["json_path"].endswith(".json")
    assert archive_dir.joinpath(saved["report_id"] + ".json").exists()
    assert saved["strategy_name"] == "trend_default"


def test_save_strategy_research_report_saves_markdown(archive_dir):
    saved = save_strategy_research_report(sample_report(), "# Report")

    assert saved["markdown_path"].endswith(".md")
    assert archive_dir.joinpath(saved["report_id"] + ".md").read_text(encoding="utf-8") == "# Report"


def test_list_strategy_research_reports_lists_saved_reports(archive_dir):
    save_strategy_research_report(sample_report())

    reports = list_strategy_research_reports()

    assert len(reports) == 1
    assert reports[0]["strategy_name"] == "trend_default"
    assert reports[0]["symbol_count"] == 2


def test_load_strategy_research_report_loads_report(archive_dir):
    saved = save_strategy_research_report(sample_report())

    report = load_strategy_research_report(saved["report_id"])

    assert report["report_id"] == saved["report_id"]
    assert report["strategy_name"] == "trend_default"


def test_delete_strategy_research_report_deletes_json_and_markdown(archive_dir):
    saved = save_strategy_research_report(sample_report(), "# Report")

    result = delete_strategy_research_report(saved["report_id"])

    assert result["deleted_count"] == 2
    assert not archive_dir.joinpath(saved["report_id"] + ".json").exists()
    assert not archive_dir.joinpath(saved["report_id"] + ".md").exists()


def test_export_strategy_report_summary_csv_returns_bytes(archive_dir):
    save_strategy_research_report(sample_report())

    csv_bytes = export_strategy_report_summary_csv(list_strategy_research_reports())

    assert isinstance(csv_bytes, bytes)
    text = csv_bytes.decode("utf-8-sig")
    assert "report_id" in text
    assert "trend_default" in text


def test_report_id_blocks_path_traversal(archive_dir):
    with pytest.raises(ValueError):
        load_strategy_research_report("../outside")
    with pytest.raises(ValueError):
        delete_strategy_research_report("strategy_report_20260618_120000_abc123/extra")


def test_invalid_report_id_cannot_read_outside_archive(archive_dir, tmp_path):
    outside = tmp_path / "strategy_report_20260618_120000_abc123.json"
    outside.write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError):
        load_strategy_research_report(str(outside))


def test_corrupt_json_does_not_break_listing(archive_dir):
    save_strategy_research_report(sample_report())
    archive_dir.mkdir(parents=True, exist_ok=True)
    (archive_dir / "strategy_report_20260618_120000_badbad.json").write_text("{bad json", encoding="utf-8")

    reports = list_strategy_research_reports()

    assert len(reports) == 1
    assert reports[0]["strategy_name"] == "trend_default"


def test_sensitive_keys_are_rejected(archive_dir):
    report = sample_report()
    report["credentials"] = {"api_key": "not-allowed"}

    with pytest.raises(ValueError):
        save_strategy_research_report(report)


def test_strategy_report_archive_module_keeps_research_only_boundaries():
    source = inspect.getsource(strategy_report_archive)
    forbidden = [
        "IB" + "KR",
        "富" + "途",
        "Al" + "paca",
        "Robin" + "hood",
        "broker " + "order",
        "place_" + "order",
        "real " + "trade",
        "Open" + "AI API",
        "AI " + "prediction",
        "eval(",
        "exec(",
    ]
    for word in forbidden:
        assert word not in source
