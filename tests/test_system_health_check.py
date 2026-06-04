from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.config.settings import DEFAULT_SETTINGS
from src.data.sample_data import load_sample_ohlcv
from src.system import health_check
from src.system.health_check import (
    check_required_files,
    check_sample_data_health,
    check_security_boundary,
    check_settings_health,
    health_check_to_dataframe,
    run_system_health_check,
)


def test_run_system_health_check_returns_summary():
    result = run_system_health_check()

    assert result["overall_status"] in {"ok", "warning", "error"}
    assert isinstance(result["checks"], list)
    assert "generated_at" in result
    assert result["ok_count"] + result["warning_count"] + result["error_count"] == len(result["checks"])


def test_health_check_to_dataframe_returns_dataframe():
    result = {
        "checks": [
            {"name": "settings", "status": "ok", "message": "Settings are valid.", "details": {}},
        ]
    }

    table = health_check_to_dataframe(result)

    assert isinstance(table, pd.DataFrame)
    assert list(table.columns) == ["name", "status", "message"]
    assert table.loc[0, "name"] == "settings"


def test_required_directories_check_can_run(tmp_path, monkeypatch):
    existing_dir = tmp_path / "config"
    missing_dir = tmp_path / "reports"
    existing_dir.mkdir()
    monkeypatch.setattr(health_check, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(health_check, "REQUIRED_DIRECTORIES", [existing_dir, missing_dir])

    result = health_check.check_required_directories()

    assert result["status"] == "warning"
    assert "reports" in result["details"]["missing"]


def test_required_files_missing_returns_warning_without_crashing(tmp_path, monkeypatch):
    missing_file = tmp_path / "config" / "settings.json"
    monkeypatch.setattr(health_check, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(health_check, "REQUIRED_FILES", [missing_file])

    result = check_required_files()

    assert result["status"] == "warning"
    assert result["details"]["config/settings.json"] == "missing"


def test_settings_health_returns_error_for_damaged_json(tmp_path, monkeypatch):
    settings_path = tmp_path / "config" / "settings.json"
    settings_path.parent.mkdir()
    settings_path.write_text("{bad json", encoding="utf-8")
    monkeypatch.setattr(health_check, "DEFAULT_SETTINGS_PATH", settings_path)

    result = check_settings_health()

    assert result["status"] == "error"
    assert "Invalid settings JSON" in result["message"]


def test_settings_health_accepts_valid_settings(tmp_path, monkeypatch):
    settings_path = tmp_path / "config" / "settings.json"
    settings_path.parent.mkdir()
    settings_path.write_text(json.dumps(DEFAULT_SETTINGS), encoding="utf-8")
    monkeypatch.setattr(health_check, "DEFAULT_SETTINGS_PATH", settings_path)

    result = check_settings_health()

    assert result["status"] == "ok"


def test_sample_data_health_accepts_sample_files(monkeypatch):
    monkeypatch.setattr(
        health_check,
        "SAMPLE_DATA_FILES",
        [
            Path("data/sample/us_NVDA.csv").resolve(),
            Path("data/sample/cn_300308.csv").resolve(),
        ],
    )

    result = check_sample_data_health()

    assert result["status"] in {"ok", "warning"}
    assert result["details"]


def test_sample_data_health_reports_invalid_sample(tmp_path, monkeypatch):
    bad_csv = tmp_path / "data" / "sample" / "bad.csv"
    bad_csv.parent.mkdir(parents=True)
    bad_csv.write_text("date,close\n2024-01-01,1\n", encoding="utf-8")
    monkeypatch.setattr(health_check, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(health_check, "SAMPLE_DATA_FILES", [bad_csv])

    result = check_sample_data_health()

    assert result["status"] == "error"
    assert result["details"]["data/sample/bad.csv"]["errors"]


def test_security_boundary_check_does_not_report_broker_or_ai_risk():
    result = check_security_boundary()

    assert result["status"] == "ok"
    assert result["details"]["findings"] == []
    text = json.dumps(result, ensure_ascii=False).lower()
    assert "place_order" not in text


def test_single_check_failure_does_not_crash_overall(monkeypatch):
    def broken_check():
        raise RuntimeError("boom")

    monkeypatch.setattr(
        health_check,
        "check_required_directories",
        broken_check,
    )

    result = run_system_health_check()

    assert result["overall_status"] == "error"
    assert any(check["status"] == "error" and check["message"] == "boom" for check in result["checks"])


def test_health_check_does_not_save_sensitive_words_to_results():
    result = run_system_health_check()
    text = json.dumps(result, ensure_ascii=False).lower()

    for word in ["api_key", "password", "token"]:
        assert word not in text


def test_required_files_validates_sample_data(tmp_path, monkeypatch):
    sample_path = tmp_path / "data" / "sample" / "us_NVDA.csv"
    sample_path.parent.mkdir(parents=True)
    load_sample_ohlcv("us", "NVDA").to_csv(sample_path, index=False)
    monkeypatch.setattr(health_check, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(health_check, "REQUIRED_FILES", [sample_path])

    result = check_required_files()

    assert result["status"] == "ok"
    assert result["details"]["data/sample/us_NVDA.csv"] == "valid_csv"

