from __future__ import annotations

import json
import sys
from pathlib import Path

from scripts import system_doctor


def test_check_python_version_accepts_current_python():
    result = system_doctor.check_python_version(sys.version_info)

    assert result["status"] == "ok"
    assert result["name"] == "python_version"


def test_check_dependencies_handles_success():
    result = system_doctor.check_dependencies(["json"], importer=__import__)

    assert result["status"] == "ok"
    assert result["details"]["loaded"] == ["json"]


def test_check_dependencies_handles_missing_dependency():
    def missing_importer(name: str):
        raise ImportError(name)

    result = system_doctor.check_dependencies(["missing_package"], importer=missing_importer)

    assert result["status"] == "error"
    assert result["details"]["missing"] == ["missing_package"]
    assert "pip install" in result["message"]


def test_check_required_directories_can_run(tmp_path, monkeypatch):
    existing = tmp_path / "config"
    missing = tmp_path / "data"
    existing.mkdir()
    monkeypatch.setattr(system_doctor, "PROJECT_ROOT", tmp_path)

    result = system_doctor.check_required_directories([existing, missing])

    assert result["status"] == "warning"
    assert result["details"]["missing"] == ["data"]


def test_check_required_files_can_run(tmp_path, monkeypatch):
    existing = tmp_path / "config" / "settings.json"
    missing = tmp_path / "config" / "watchlists.json"
    existing.parent.mkdir()
    existing.write_text(json.dumps({"ok": True}), encoding="utf-8")
    monkeypatch.setattr(system_doctor, "PROJECT_ROOT", tmp_path)

    result = system_doctor.check_required_files([existing, missing])

    assert result["status"] == "warning"
    assert result["details"]["missing"] == ["config/watchlists.json"]


def test_run_doctor_returns_structured_result(monkeypatch):
    monkeypatch.setattr(system_doctor, "check_dependencies", lambda: system_doctor.make_check("dependencies", "ok", "ok"))
    monkeypatch.setattr(
        system_doctor,
        "check_required_directories",
        lambda: system_doctor.make_check("required_directories", "ok", "ok"),
    )
    monkeypatch.setattr(
        system_doctor,
        "check_required_files",
        lambda: system_doctor.make_check("required_files", "ok", "ok"),
    )

    result = system_doctor.run_doctor(lambda: {"overall_status": "ok", "checks": []})

    assert result["overall_status"] == "ok"
    assert result["ok_count"] == 5
    assert result["error_count"] == 0


def test_run_doctor_handles_health_check_failure(monkeypatch):
    monkeypatch.setattr(system_doctor, "check_dependencies", lambda: system_doctor.make_check("dependencies", "ok", "ok"))
    monkeypatch.setattr(
        system_doctor,
        "check_required_directories",
        lambda: system_doctor.make_check("required_directories", "ok", "ok"),
    )
    monkeypatch.setattr(
        system_doctor,
        "check_required_files",
        lambda: system_doctor.make_check("required_files", "ok", "ok"),
    )

    def broken_health_check():
        raise ValueError("bad health")

    result = system_doctor.run_doctor(broken_health_check)

    assert result["overall_status"] == "error"
    assert any(check["name"] == "system_health" and check["status"] == "error" for check in result["checks"])


def test_system_doctor_source_has_no_runtime_broker_or_ai_calls():
    source = Path("scripts/system_doctor.py").read_text(encoding="utf-8")

    for word in ["IBKR", "Alpaca", "Robinhood", "broker order", "place_order", "real trade", "OpenAI API"]:
        assert word not in source


def test_system_doctor_does_not_save_sensitive_fields():
    result = system_doctor.run_doctor(lambda: {"overall_status": "ok", "checks": []})
    text = json.dumps(result, ensure_ascii=False).lower()

    for word in ["api_key", "password", "token"]:
        assert word not in text
