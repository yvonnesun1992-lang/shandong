from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd
import pytest

from src.workflows.run_log import (
    delete_workflow_run_log,
    export_workflow_run_summary_csv,
    generate_run_id,
    list_workflow_run_logs,
    load_workflow_run_log,
    save_workflow_run_log,
)


def sample_workflow_result() -> dict:
    return {
        "run_id": generate_run_id(),
        "created_at": "2026-06-02T10:00:00",
        "started_at": "2026-06-02T10:00:00",
        "finished_at": "2026-06-02T10:00:03",
        "elapsed_seconds": 3.0,
        "success": True,
        "market": "us",
        "watchlist_name": "us_default",
        "total_symbols": 2,
        "success_count": 1,
        "failed_count": 1,
        "success_symbols": ["NVDA"],
        "failed_symbols": [{"symbol": "FAIL", "error": "sample error"}],
        "report_id": "daily_report_20260602_100000_abcd1234",
        "report_path": "reports/daily/daily_report_20260602_100000_abcd1234.json",
        "summary": {"average_score": 80.0},
        "trend_scores": pd.DataFrame([{"symbol": "NVDA", "score": 80}]),
    }


def test_generate_run_id_is_safe_and_unique():
    first = generate_run_id()
    second = generate_run_id()

    assert first != second
    assert re.fullmatch(r"[A-Za-z0-9_-]+", first)
    assert "/" not in first
    assert "\\" not in first
    assert ".." not in first


def test_save_workflow_run_log_writes_json(tmp_path):
    saved = save_workflow_run_log(sample_workflow_result(), tmp_path)

    path = tmp_path / f"{saved['run_id']}.json"
    assert path.exists()
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["run_id"] == saved["run_id"]
    assert isinstance(loaded["trend_scores"], list)


def test_list_workflow_run_logs_empty(tmp_path):
    logs = list_workflow_run_logs(tmp_path)

    assert logs.empty


def test_list_workflow_run_logs_has_key_columns(tmp_path):
    saved = save_workflow_run_log(sample_workflow_result(), tmp_path)

    logs = list_workflow_run_logs(tmp_path)

    assert not logs.empty
    assert saved["run_id"] in logs["run_id"].tolist()
    assert {
        "run_id",
        "created_at",
        "market",
        "watchlist_name",
        "success",
        "total_symbols",
        "success_count",
        "failed_count",
        "report_id",
        "elapsed_seconds",
    }.issubset(logs.columns)


def test_load_workflow_run_log_reads_json(tmp_path):
    saved = save_workflow_run_log(sample_workflow_result(), tmp_path)

    loaded = load_workflow_run_log(saved["run_id"], tmp_path)

    assert loaded["run_id"] == saved["run_id"]
    assert loaded["success_count"] == 1


def test_delete_workflow_run_log_removes_file(tmp_path):
    saved = save_workflow_run_log(sample_workflow_result(), tmp_path)

    delete_workflow_run_log(saved["run_id"], tmp_path)

    assert not (tmp_path / f"{saved['run_id']}.json").exists()


def test_load_invalid_workflow_run_json_raises(tmp_path):
    (tmp_path / "broken.json").write_text("{bad json", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid"):
        load_workflow_run_log("broken", tmp_path)


def test_missing_workflow_run_log_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_workflow_run_log("missing_run", tmp_path)


def test_path_traversal_run_id_is_rejected(tmp_path):
    with pytest.raises(ValueError):
        load_workflow_run_log("../outside", tmp_path)


def test_workflow_run_log_stays_inside_output_dir(tmp_path):
    saved = save_workflow_run_log(sample_workflow_result(), tmp_path)

    log_path = (tmp_path / f"{saved['run_id']}.json").resolve()

    assert log_path.parent == tmp_path.resolve()
    assert not (tmp_path.parent / f"{saved['run_id']}.json").exists()


def test_export_workflow_run_summary_csv(tmp_path):
    saved = save_workflow_run_log(sample_workflow_result(), tmp_path)

    csv_text = export_workflow_run_summary_csv(tmp_path)

    assert "run_id" in csv_text
    assert "elapsed_seconds" in csv_text
    assert saved["run_id"] in csv_text


def test_workflow_run_log_rejects_sensitive_keys(tmp_path):
    result = sample_workflow_result()
    result["api_key"] = "bad"

    with pytest.raises(ValueError, match="API keys"):
        save_workflow_run_log(result, tmp_path)


def test_run_log_module_does_not_reference_broker_or_ai_clients():
    import src.workflows.run_log as run_log

    module_text = Path(run_log.__file__).read_text(encoding="utf-8")
    forbidden = [
        "IBKR",
        "富途",
        "Alpaca",
        "Robinhood",
        "broker order",
        "place_order",
        "real trade",
        "OpenAI API",
        "AI prediction",
    ]

    for word in forbidden:
        assert word not in module_text
