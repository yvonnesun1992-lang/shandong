from __future__ import annotations

import json
import subprocess

from fastapi.testclient import TestClient


SENSITIVE_TERMS = ["secret", "token", "password", "authorization", "api_key"]


def test_monitoring_data_reader_missing_files_returns_fallback(tmp_path):
    from runtime.monitoring_data_reader import MonitoringDataReader

    reader = MonitoringDataReader(
        log_path=tmp_path / "missing.jsonl",
        checkpoint_path=tmp_path / "missing_checkpoint.json",
        soak_report_path=tmp_path / "missing_report.md",
    )

    assert reader.read_runtime_logs() == []
    assert reader.read_latest_checkpoint()["available"] is False
    assert reader.read_soak_report()["available"] is False
    assert reader.get_recent_events(limit=10) == []


def test_monitoring_summary_outputs_paper_trading_safety(tmp_path):
    from runtime.monitoring_data_reader import MonitoringDataReader
    from runtime.monitoring_summary import build_monitoring_summary

    checkpoint = tmp_path / "runtime_state_checkpoint.json"
    checkpoint.write_text(
        json.dumps(
            {
                "portfolio": {"cash": 99_000, "equity": 101_000},
                "positions": {"AAPL": {"quantity": 10, "avg_price": 100}},
                "pnl": {"equity": 101_000, "drawdown": 0.01},
                "mode": "NORMAL",
                "health": {"status": "HEALTHY"},
                "checkpoint_saved_at": "2026-01-01T00:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )
    summary = build_monitoring_summary(MonitoringDataReader(checkpoint_path=checkpoint))

    assert summary["paper_trading"] is True
    assert summary["real_trading"] is False
    assert summary["broker_connected"] is False
    assert summary["latest_equity"] == 101_000
    assert summary["open_positions"][0]["symbol"] == "AAPL"


def test_v5_monitoring_api_endpoints_return_safe_200():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/monitoring/summary",
        "/api/v5/monitoring/pnl",
        "/api/v5/monitoring/positions",
        "/api/v5/monitoring/signals",
        "/api/v5/monitoring/trades",
        "/api/v5/monitoring/errors",
        "/api/v5/monitoring/health",
        "/api/v5/monitoring/risk",
        "/api/v5/monitoring/soak-report",
    ]

    for path in paths:
        response = client.get(path)
        payload = response.json()
        assert response.status_code == 200
        assert payload["success"] is True
        assert _is_safe(payload)
        encoded = json.dumps(payload).lower()
        assert "paper_trading" in encoded
        assert "real_trading" in encoded
        assert "broker_connected" in encoded


def test_monitoring_report_and_cli_can_run():
    from runtime.monitoring_report import generate_monitoring_report

    result = generate_monitoring_report()
    assert result["path"].endswith("reports/v5_4_monitoring_report.md")
    assert result["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert _is_safe(result)

    completed = subprocess.run(
        [".venv312/bin/python", "scripts/run_v54_monitoring_snapshot.py"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode in {0, 1}
    assert "verdict" in completed.stdout.lower()
    assert _is_safe(json.loads(completed.stdout))


def test_frontend_monitoring_helpers_page_and_navigation_exist():
    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-monitoring/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")

    assert "fetchV5MonitoringSummary" in api_client
    assert "fetchV5MonitoringPnl" in api_client
    assert "fetchV5MonitoringPositions" in api_client
    assert "fetchV5MonitoringSignals" in api_client
    assert "fetchV5MonitoringTrades" in api_client
    assert "fetchV5MonitoringErrors" in api_client
    assert "fetchV5MonitoringHealth" in api_client
    assert "fetchV5MonitoringRisk" in api_client
    assert "fetchV5MonitoringSoakReport" in api_client
    assert "Paper trading only" in page
    assert "No real broker connected" in page
    assert "No real orders" in page
    assert "No real capital" in page
    assert "V5 Monitoring" in shell
    assert "/v5-monitoring" in shell


def test_existing_v5_tests_still_available():
    assert "test_paper_trading_runner_completes_closed_loop" in _read("tests/test_v50_paper_trading_core.py")
    assert "test_runtime_loop_runs_and_updates_portfolio" in _read("tests/test_v51_trading_engine_runtime.py")
    assert "test_engine_crash_recovery_logs_error" in _read("tests/test_v52_production_stability_engineering.py")
    assert "soak" in _read("tests/test_v53_long_run_soak_test.py").lower()


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def _is_safe(payload) -> bool:
    encoded = json.dumps(payload, default=str).lower()
    return not any(term in encoded for term in SENSITIVE_TERMS)
