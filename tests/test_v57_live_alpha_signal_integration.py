from __future__ import annotations

import json
import subprocess
import sys

from fastapi.testclient import TestClient


SENSITIVE_TERMS = ["secret", "token", "password", "api_key", "authorization", "/users/apple", "broker credential"]


def test_live_feature_buffer_accumulates_ticks():
    from runtime.live_feature_buffer import LiveFeatureBuffer
    from runtime.live_market_data import MockLiveMarketDataAdapter

    buffer = LiveFeatureBuffer(min_window=3, max_window=5)
    adapter = MockLiveMarketDataAdapter(symbols=["AAPL"])
    for _ in range(6):
        buffer.append_tick(adapter.get_latest_ticks()[0])

    frame = buffer.get_symbol_frame("AAPL")
    assert len(frame) == 5
    assert buffer.is_ready("AAPL") is True
    assert list(frame.columns) == ["datetime", "open", "high", "low", "close", "volume", "source"]


def test_alpha_adapter_hold_when_not_ready_and_standard_signal_when_ready():
    from runtime.live_alpha_signal_adapter import LiveAlphaSignalAdapter
    from runtime.live_feature_buffer import LiveFeatureBuffer
    from runtime.live_market_data import MockLiveMarketDataAdapter

    adapter = LiveAlphaSignalAdapter(min_window=5)
    buffer = LiveFeatureBuffer(min_window=5, max_window=80)
    market = MockLiveMarketDataAdapter(symbols=["AAPL"])

    early_tick = market.get_latest_ticks()[0]
    buffer.append_tick(early_tick)
    hold = adapter.generate_signal("AAPL", buffer.get_symbol_frame("AAPL"))
    assert hold["action"] == "HOLD"
    assert hold["source"] == "v5_alpha"
    assert hold["paper_trading"] is True
    assert hold["real_trading"] is False

    for _ in range(80):
        buffer.append_tick(market.get_latest_ticks()[0])
    signal = adapter.generate_signal("AAPL", buffer.get_symbol_frame("AAPL"))
    assert signal["symbol"] == "AAPL"
    assert signal["action"] in {"BUY", "SELL", "HOLD"}
    assert 0.0 <= signal["strength"] <= 1.0
    assert signal["source"] == "v5_alpha"
    assert _is_safe(signal)


def test_live_alpha_runner_replaces_heartbeat_with_alpha_flow():
    from runtime.live_paper_alpha_runner import run_live_paper_alpha_staging
    from runtime.live_paper_staging_runner import run_live_paper_staging

    result = run_live_paper_alpha_staging(mode="mock_live", max_ticks=100, symbols=["AAPL", "MSFT"])
    heartbeat_result = run_live_paper_staging(mode="mock_live", max_ticks=5, symbols=["AAPL"])

    assert result["success"] is True
    assert result["ticks_processed"] >= 100
    assert result["signals_generated"] > 0
    assert result["hold_signals"] > 0
    assert result["orders_submitted"] >= 0
    assert result["paper_trading"] is True
    assert result["real_trading"] is False
    assert result["broker_connected"] is False
    assert result["real_money_enabled"] is False
    assert "_paper_observation_order" not in _read("runtime/live_paper_staging_runner.py")
    assert heartbeat_result["fills"] == []
    assert _is_safe(result)


def test_hold_signal_does_not_create_order():
    from trading.paper_account import PaperAccount
    from trading.signal_to_order import SignalToOrderConverter

    account = PaperAccount(initial_cash=100_000)
    order = SignalToOrderConverter().convert({"symbol": "AAPL", "action": "HOLD", "strength": 1.0}, account, 100.0)
    assert order is None


def test_v5_live_alpha_api_endpoints_return_safe_200():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    for path in ["/api/v5/live-alpha/status", "/api/v5/live-alpha/latest-signals", "/api/v5/live-alpha/summary", "/api/v5/live-alpha/buffer-status"]:
        response = client.get(path)
        payload = response.json()

        assert response.status_code == 200
        assert payload["success"] is True
        encoded = json.dumps(payload).lower()
        assert "paper_trading" in encoded
        assert "real_trading" in encoded
        assert "broker_connected" in encoded
        assert _is_safe(payload)


def test_live_alpha_report_and_cli_can_run():
    from runtime.live_alpha_report import generate_live_alpha_report

    result = generate_live_alpha_report(mode="mock_live", ticks=100)
    assert result["path"].endswith("reports/v5_7_live_alpha_signal_integration_report.md")
    assert result["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert _is_safe(result)

    completed = subprocess.run(
        [sys.executable, "scripts/run_v57_live_alpha_paper.py", "--mode", "mock_live", "--ticks", "30"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode in {0, 1}
    payload = json.loads(completed.stdout)
    assert payload["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert _is_safe(payload)


def test_v57_frontend_page_helpers_navigation_and_docs_exist():
    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-live-alpha/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")

    assert "fetchV5LiveAlphaStatus" in api_client
    assert "fetchV5LiveAlphaLatestSignals" in api_client
    assert "fetchV5LiveAlphaSummary" in api_client
    assert "fetchV5LiveAlphaBufferStatus" in api_client
    assert "Live Alpha Paper Status" in page
    assert "Alpha signal driven paper trading" in page
    assert "Paper trading only" in page
    assert "Real trading: disabled" in page
    assert "Broker: not connected" in page
    assert "Real money: disabled" in page
    assert "V5 Live Alpha" in shell
    assert "/v5-live-alpha" in shell
    assert "V5.7" in _read("docs/V5_LIVE_ALPHA_SIGNAL_INTEGRATION.md")
    assert "V5.7" in _read("README.md")
    assert "V5.7" in _read("REVIEW_PACKAGE.md")


def test_existing_v5_stack_tests_are_available():
    assert "test_paper_trading_runner_completes_closed_loop" in _read("tests/test_v50_paper_trading_core.py")
    assert "test_runtime_loop_runs_and_updates_portfolio" in _read("tests/test_v51_trading_engine_runtime.py")
    assert "test_engine_crash_recovery_logs_error" in _read("tests/test_v52_production_stability_engineering.py")
    assert "soak" in _read("tests/test_v53_long_run_soak_test.py").lower()
    assert "monitoring" in _read("tests/test_v54_live_paper_trading_monitoring_api.py").lower()
    assert "deployment" in _read("tests/test_v55_production_deployment_dry_run.py").lower()
    assert "live paper" in _read("tests/test_v56_live_paper_trading_staging.py").lower()


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def _is_safe(payload) -> bool:
    encoded = json.dumps(payload, default=str).lower()
    return not any(term in encoded for term in SENSITIVE_TERMS)
