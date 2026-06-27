from __future__ import annotations

import json
import subprocess
import sys

from fastapi.testclient import TestClient


SENSITIVE_TERMS = ["secret", "token", "password", "api_key", "database_url", "authorization", "/users/apple"]


def test_v5_deployment_config_defaults_are_paper_only():
    from config.v5_deployment_config import get_v5_deployment_status

    status = get_v5_deployment_status()

    assert status["deployment_mode"] in {"local", "dry_run"}
    assert status["runtime_mode"] == "paper"
    assert status["monitoring_mode"] == "local"
    assert status["storage_mode"] == "local_files"
    assert status["paper_trading"] is True
    assert status["real_trading"] is False
    assert status["broker_connected"] is False
    assert status["real_money_enabled"] is False
    assert status["production_deployment"] is False
    assert _is_safe(status)


def test_v55_deployment_dry_run_check_outputs_safe_readiness():
    from scripts.v55_deployment_dry_run_check import run_v55_deployment_dry_run_check

    result = run_v55_deployment_dry_run_check()

    assert result["success"] is True
    assert result["dry_run_ready"] is True
    assert result["deployment_ready"] is False
    assert result["safety"]["paper_trading"] is True
    assert result["safety"]["real_trading"] is False
    assert result["safety"]["broker_connected"] is False
    assert result["safety"]["real_money_enabled"] is False
    assert result["safety"]["production_deployment"] is False
    assert any(check["name"] == "v5_4_monitoring_module" for check in result["checks"])
    assert _is_safe(result)


def test_v5_deployment_api_endpoints_return_safe_200():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    for path in ["/api/v5/deployment/dry-run", "/api/v5/deployment/readiness"]:
        response = client.get(path)
        payload = response.json()

        assert response.status_code == 200
        assert payload["success"] is True
        assert payload["data"]["deployment"]["version"] == "V5.5"
        assert payload["data"]["deployment"]["dry_run_ready"] is True
        assert payload["data"]["deployment"]["deployment_ready"] is False
        assert payload["data"]["deployment"]["paper_trading"] is True
        assert payload["data"]["deployment"]["real_trading"] is False
        assert payload["data"]["deployment"]["broker_connected"] is False
        assert payload["data"]["deployment"]["real_money_enabled"] is False
        assert _is_safe(payload)


def test_v55_deployment_report_and_cli_can_run():
    from runtime.v55_deployment_report import generate_v55_deployment_report

    result = generate_v55_deployment_report()
    assert result["path"].endswith("reports/v5_5_deployment_dry_run_report.md")
    assert result["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert _is_safe(result)

    completed = subprocess.run(
        [sys.executable, "scripts/run_v55_deployment_dry_run.py"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode in {0, 1}
    payload = json.loads(completed.stdout)
    assert payload["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert _is_safe(payload)


def test_v55_frontend_page_helpers_and_navigation_exist():
    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-deployment/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")

    assert "fetchV5DeploymentDryRun" in api_client
    assert "fetchV5DeploymentReadiness" in api_client
    assert "Deployment Dry Run Status" in page
    assert "Paper trading only" in page
    assert "Real trading: disabled" in page
    assert "Broker: not connected" in page
    assert "Real money: disabled" in page
    assert "Production deployment: not enabled" in page
    assert "Deployment mode: dry run" in page
    assert "V5 Deployment" in shell
    assert "/v5-deployment" in shell
    assert _is_safe({"api_client": api_client, "page": page, "shell": shell})


def test_v55_docs_and_existing_v5_tests_are_available():
    assert "V5.5" in _read("docs/V5_PRODUCTION_DEPLOYMENT_DRY_RUN.md")
    assert "V5.5" in _read("README.md")
    assert "V5.5" in _read("REVIEW_PACKAGE.md")
    assert "test_paper_trading_runner_completes_closed_loop" in _read("tests/test_v50_paper_trading_core.py")
    assert "test_runtime_loop_runs_and_updates_portfolio" in _read("tests/test_v51_trading_engine_runtime.py")
    assert "test_engine_crash_recovery_logs_error" in _read("tests/test_v52_production_stability_engineering.py")
    assert "soak" in _read("tests/test_v53_long_run_soak_test.py").lower()
    assert "monitoring" in _read("tests/test_v54_live_paper_trading_monitoring_api.py").lower()


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def _is_safe(payload) -> bool:
    encoded = json.dumps(payload, default=str).lower()
    return not any(term in encoded for term in SENSITIVE_TERMS)
