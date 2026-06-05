from __future__ import annotations

from pathlib import Path

from scripts import start_dashboard


def test_build_streamlit_command_uses_python_module():
    command = start_dashboard.build_streamlit_command("python")

    assert command == ["python", "-m", "streamlit", "run", "app/main.py"]


def test_has_blocking_errors_detects_error():
    result = {"checks": [{"status": "ok"}, {"status": "error"}]}

    assert start_dashboard.has_blocking_errors(result) is True


def test_has_blocking_errors_allows_warnings():
    result = {"checks": [{"status": "ok"}, {"status": "warning"}]}

    assert start_dashboard.has_blocking_errors(result) is False


def test_start_dashboard_does_not_run_streamlit_when_doctor_has_error():
    calls = []

    def doctor():
        return {
            "overall_status": "error",
            "checks": [{"name": "dependencies", "status": "error", "message": "missing", "details": {}}],
            "next_steps": [],
        }

    def runner(*args, **kwargs):
        calls.append((args, kwargs))
        return 0

    exit_code = start_dashboard.main(doctor_func=doctor, runner=runner)

    assert exit_code == 1
    assert calls == []


def test_start_dashboard_runs_streamlit_when_checks_pass():
    calls = []

    def doctor():
        return {
            "overall_status": "ok",
            "checks": [{"name": "dependencies", "status": "ok", "message": "ok", "details": {}}],
            "next_steps": [],
        }

    def runner(command, cwd=None):
        calls.append((command, cwd))
        return 0

    exit_code = start_dashboard.main(doctor_func=doctor, runner=runner)

    assert exit_code == 0
    assert calls
    assert calls[0][0][-3:] == ["streamlit", "run", "app/main.py"]


def test_launcher_scripts_do_not_contain_sensitive_values():
    combined = "\n".join(
        [
            Path("scripts/start_dashboard.py").read_text(encoding="utf-8"),
            Path("start_shandong.bat").read_text(encoding="utf-8"),
            Path("start_shandong.ps1").read_text(encoding="utf-8"),
        ]
    ).lower()

    for word in ["api_key", "secret", "password", "token", "place_order", "openai api"]:
        assert word not in combined

