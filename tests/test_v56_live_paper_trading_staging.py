from __future__ import annotations

import json
import math
import subprocess
import sys

from fastapi.testclient import TestClient


SENSITIVE_TERMS = ["secret", "token", "password", "api_key", "authorization", "/users/apple", "broker credential"]


def test_v5_live_data_config_defaults_are_paper_only():
    from config.v5_live_data_config import get_live_data_status

    status = get_live_data_status()

    assert status["live_data_mode"] == "mock_live"
    assert status["live_data_provider"] == "mock"
    assert status["symbols"] == ["AAPL", "MSFT", "NVDA", "SPY", "QQQ"]
    assert status["poll_interval_seconds"] == 60
    assert status["live_market_data"] is True
    assert status["paper_trading"] is True
    assert status["real_trading"] is False
    assert status["broker_connected"] is False
    assert _is_safe(status)


def test_live_market_data_adapter_outputs_standard_tick():
    from runtime.live_market_data import MockLiveMarketDataAdapter

    ticks = MockLiveMarketDataAdapter(symbols=["AAPL"]).get_latest_ticks()

    assert len(ticks) == 1
    tick = ticks[0]
    assert set(["datetime", "symbol", "open", "high", "low", "close", "volume", "source"]).issubset(tick)
    assert tick["symbol"] == "AAPL"
    assert tick["close"] > 0
    assert tick["source"] == "mock_live"


def test_live_data_normalizer_filters_invalid_ticks():
    from runtime.live_data_normalizer import normalize_live_ticks

    normalized = normalize_live_ticks(
        [
            {"datetime": "2026-01-01T00:00:00+00:00", "symbol": "AAPL", "open": 1, "high": 2, "low": 1, "close": 1.5, "volume": 100, "source": "mock_live"},
            {"datetime": "2026-01-01T00:00:00+00:00", "symbol": "MSFT", "close": 0, "source": "mock_live"},
            {"datetime": "2026-01-01T00:00:00+00:00", "symbol": "NVDA", "close": math.nan, "source": "mock_live"},
        ]
    )

    assert len(normalized["valid_ticks"]) == 1
    assert normalized["valid_ticks"][0]["symbol"] == "AAPL"
    assert len(normalized["invalid_ticks"]) == 2


def test_live_paper_runner_mock_and_yfinance_fallback_are_safe():
    from runtime.live_paper_staging_runner import run_live_paper_staging

    mock_result = run_live_paper_staging(mode="mock_live", max_ticks=20)
    fallback_result = run_live_paper_staging(mode="yfinance_polling", max_ticks=5)

    for result in [mock_result, fallback_result]:
        assert result["success"] is True
        assert result["ticks_processed"] > 0
        assert result["paper_trading"] is True
        assert result["real_trading"] is False
        assert result["broker_connected"] is False
        assert result["real_money_enabled"] is False
        assert result["health_status"] in {"HEALTHY", "DEGRADED", "FAILED"}
        assert _is_safe(result)
    assert fallback_result["mode"] in {"yfinance_polling", "mock_live"}


def test_v5_live_paper_api_endpoints_return_safe_200():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    for path in ["/api/v5/live-paper/status", "/api/v5/live-paper/config", "/api/v5/live-paper/latest-tick", "/api/v5/live-paper/summary"]:
        response = client.get(path)
        payload = response.json()

        assert response.status_code == 200
        assert payload["success"] is True
        encoded = json.dumps(payload).lower()
        assert "paper_trading" in encoded
        assert "real_trading" in encoded
        assert "broker_connected" in encoded
        assert _is_safe(payload)


def test_live_paper_report_and_cli_can_run():
    from runtime.live_paper_report import generate_live_paper_report

    result = generate_live_paper_report(mode="mock_live", ticks=5)
    assert result["path"].endswith("reports/v5_6_live_paper_staging_report.md")
    assert result["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert _is_safe(result)

    completed = subprocess.run(
        [sys.executable, "scripts/run_v56_live_paper_staging.py", "--mode", "mock_live", "--ticks", "5"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode in {0, 1}
    payload = json.loads(completed.stdout)
    assert payload["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert _is_safe(payload)


def test_v56_frontend_page_helpers_navigation_and_docs_exist():
    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-live-paper/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")

    assert "fetchV5LivePaperStatus" in api_client
    assert "fetchV5LivePaperConfig" in api_client
    assert "fetchV5LivePaperLatestTick" in api_client
    assert "fetchV5LivePaperSummary" in api_client
    assert "Live Paper Staging Status" in page
    assert "Live market data: enabled" in page
    assert "Paper trading only" in page
    assert "Real trading: disabled" in page
    assert "Broker: not connected" in page
    assert "Real money: disabled" in page
    assert "V5 Live Paper" in shell
    assert "/v5-live-paper" in shell
    assert "V5.6" in _read("docs/V5_LIVE_PAPER_TRADING_STAGING.md")
    assert "V5.6" in _read("README.md")
    assert "V5.6" in _read("REVIEW_PACKAGE.md")


def test_existing_v5_stack_tests_are_available():
    assert "test_paper_trading_runner_completes_closed_loop" in _read("tests/test_v50_paper_trading_core.py")
    assert "test_runtime_loop_runs_and_updates_portfolio" in _read("tests/test_v51_trading_engine_runtime.py")
    assert "test_engine_crash_recovery_logs_error" in _read("tests/test_v52_production_stability_engineering.py")
    assert "soak" in _read("tests/test_v53_long_run_soak_test.py").lower()
    assert "monitoring" in _read("tests/test_v54_live_paper_trading_monitoring_api.py").lower()
    assert "deployment" in _read("tests/test_v55_production_deployment_dry_run.py").lower()


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def _is_safe(payload) -> bool:
    encoded = json.dumps(payload, default=str).lower()
    return not any(term in encoded for term in SENSITIVE_TERMS)
