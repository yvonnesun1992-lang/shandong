from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient


FALSE_KEYS = [
    "read_only_runtime_enabled",
    "sandbox_api_enabled",
    "secret_read_enabled",
    "account_read_enabled",
    "position_read_enabled",
    "balance_read_enabled",
    "order_preview_enabled",
    "order_submission_enabled",
    "broker_connected",
    "real_money_enabled",
]


def test_read_only_connector_config_defaults_and_blocks_env_requests(monkeypatch):
    from config.v5_read_only_connector_config import (
        get_read_only_connector_mode,
        get_read_only_connector_provider,
        get_read_only_connector_status,
    )

    assert get_read_only_connector_mode() == "read_only_blueprint_only"
    assert get_read_only_connector_provider() in {"alpaca", "ibkr", "futu", "tiger", "schwab"}
    status = get_read_only_connector_status()
    assert status["version"] == "V5.33"
    assert status["read_only_blueprint_only"] is True
    assert status["paper_trading"] is True
    for key in FALSE_KEYS:
        assert status[key] is False

    for env_name in [
        "SHANDONG_V5_ENABLE_READ_ONLY_RUNTIME",
        "SHANDONG_V5_ENABLE_SANDBOX_API",
        "SHANDONG_V5_ENABLE_SECRET_READ",
        "SHANDONG_V5_ENABLE_ACCOUNT_READ",
        "SHANDONG_V5_ENABLE_POSITION_READ",
        "SHANDONG_V5_ENABLE_BALANCE_READ",
        "SHANDONG_V5_ENABLE_ORDER_PREVIEW",
        "SHANDONG_V5_ENABLE_ORDER_SUBMISSION",
        "SHANDONG_V5_ENABLE_REAL_MONEY",
    ]:
        monkeypatch.setenv(env_name, "true")
    blocked = get_read_only_connector_status()
    for key in FALSE_KEYS:
        assert blocked[key] is False
    warnings = " | ".join(blocked["warnings"]).lower()
    assert "read-only runtime requested but blocked in v5.33" in warnings
    assert "sandbox api requested but blocked in v5.33" in warnings
    assert "secret read requested but blocked in v5.33" in warnings
    assert "account read requested but blocked in v5.33" in warnings
    assert "position read requested but blocked in v5.33" in warnings
    assert "balance read requested but blocked in v5.33" in warnings
    assert "order preview requested but blocked in v5.33" in warnings
    assert "order submission requested but blocked in v5.33" in warnings
    assert "real money requested but blocked in v5.33" in warnings
    assert _is_safe(blocked)


def test_read_only_connector_components_schemas_redaction_audit_safety_and_orchestrator():
    from sandbox_read_only_connector.account_snapshot_schema import build_account_snapshot_schema
    from sandbox_read_only_connector.balance_snapshot_schema import build_balance_snapshot_schema
    from sandbox_read_only_connector.position_snapshot_schema import build_position_snapshot_schema
    from sandbox_read_only_connector.read_only_audit_policy import build_read_only_audit_event, build_read_only_audit_policy
    from sandbox_read_only_connector.read_only_connector_orchestrator import (
        build_read_only_connector_blueprint,
        summarize_read_only_connector_blueprint,
    )
    from sandbox_read_only_connector.read_only_credential_scope import build_read_only_credential_scope
    from sandbox_read_only_connector.read_only_rate_limit_policy import build_read_only_rate_limit_policy
    from sandbox_read_only_connector.read_only_redaction_policy import build_redaction_policy, validate_redacted_payload
    from sandbox_read_only_connector.read_only_safety_validator import build_read_only_safety_summary, validate_read_only_safety
    from sandbox_read_only_connector.read_only_scope_definition import build_read_only_scope_definition

    scope = build_read_only_scope_definition("alpaca")
    credential = build_read_only_credential_scope("alpaca")
    account_schema = build_account_snapshot_schema("alpaca")
    balance_schema = build_balance_snapshot_schema("alpaca")
    position_schema = build_position_snapshot_schema("alpaca")
    redaction = build_redaction_policy("alpaca")
    rate_limit = build_read_only_rate_limit_policy("alpaca")
    audit_policy = build_read_only_audit_policy("alpaca")
    audit_event = build_read_only_audit_event("alpaca", "balance_snapshot")
    safety = build_read_only_safety_summary()
    blueprint = build_read_only_connector_blueprint("alpaca")
    summary = summarize_read_only_connector_blueprint(blueprint)

    assert scope["scope_ready"] is False
    assert "validate connector config" in scope["read_only_scope"]["allowed_future_actions"]
    assert "order submission" in scope["read_only_scope"]["disallowed_actions"]
    assert credential["credential_scope_ready"] is False
    assert credential["secret_read_enabled"] is False
    assert "no trading permission" in credential["credential_scope"]["requirements"]
    assert account_schema["schema"]["raw_payload_stored"] is False
    assert account_schema["schema"]["provider_payload_redacted"] is True
    assert balance_schema["schema"]["value_redacted"] is True
    assert balance_schema["schema"]["raw_payload_stored"] is False
    assert position_schema["schema"]["value_redacted"] is True
    assert position_schema["schema"]["raw_payload_stored"] is False
    assert redaction["redaction_ready"] is False
    assert validate_redacted_payload({"cash_balance": 100})["redacted"] is False
    assert validate_redacted_payload({"cash_balance_placeholder": "REDACTED"})["redacted"] is True
    assert rate_limit["write_request_budget"] == 0
    assert rate_limit["network_calls_enabled"] is False
    assert audit_policy["order_submitted"] is False
    assert audit_event["order_submitted"] is False
    assert audit_event["raw_payload_stored"] is False
    assert safety["safe"] is True
    for key in FALSE_KEYS:
        assert validate_read_only_safety({key: True})["safe"] is False
    assert validate_read_only_safety({"payload": "secret_value=demo"})["safe"] is False
    assert validate_read_only_safety({"cash_balance": 123})["safe"] is False
    assert summary["verdict"] in {"PASS", "WARNING"}
    for item in [scope, credential, account_schema, balance_schema, position_schema, redaction, rate_limit, audit_policy, audit_event, safety, summary]:
        assert item["read_only_blueprint_only"] is True
        assert _is_safe(item)


def test_read_only_connector_api_endpoints_return_locked_boundaries():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/read-only-connector/status",
        "/api/v5/read-only-connector/scope",
        "/api/v5/read-only-connector/credential-scope",
        "/api/v5/read-only-connector/account-schema",
        "/api/v5/read-only-connector/balance-schema",
        "/api/v5/read-only-connector/position-schema",
        "/api/v5/read-only-connector/redaction",
        "/api/v5/read-only-connector/rate-limit",
        "/api/v5/read-only-connector/audit",
        "/api/v5/read-only-connector/safety",
        "/api/v5/read-only-connector/summary",
    ]
    for path in paths:
        response = client.get(path)
        payload = response.json()
        text = json.dumps(payload).lower()
        assert response.status_code == 200
        assert payload["success"] is True
        assert "read_only_blueprint_only" in text
        assert "paper_trading" in text
        for key in FALSE_KEYS:
            assert key in text
        assert _is_safe(payload)


def test_report_cli_frontend_docs_navigation_and_security_scan_are_present():
    from runtime.security_scan import scan_read_only_connector_outputs
    from sandbox_read_only_connector.sandbox_read_only_connector_report import generate_sandbox_read_only_connector_report

    report = generate_sandbox_read_only_connector_report(provider="alpaca")
    assert report["path"].endswith("reports/v5_33_sandbox_read_only_connector_report.md")
    assert report["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert report["read_only_blueprint_only"] is True
    assert scan_read_only_connector_outputs(report)["safe"] is True
    assert _is_safe(report)

    for args in [[], ["--provider", "alpaca"], ["--provider", "ibkr"], ["--check", "scope"], ["--check", "redaction"], ["--check", "safety"]]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v533_read_only_connector.py", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["verdict"] in {"PASS", "WARNING"}
        assert payload["read_only_blueprint_only"] is True
        assert _is_safe(payload)

    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-read-only-connector/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")
    docs = _read("docs/V5_READ_ONLY_CONNECTOR_BLUEPRINT.md")
    scanner = _read("runtime/security_scan.py")
    for name in [
        "fetchV5ReadOnlyConnectorStatus",
        "fetchV5ReadOnlyConnectorScope",
        "fetchV5ReadOnlyConnectorCredentialScope",
        "fetchV5ReadOnlyConnectorAccountSchema",
        "fetchV5ReadOnlyConnectorBalanceSchema",
        "fetchV5ReadOnlyConnectorPositionSchema",
        "fetchV5ReadOnlyConnectorRedaction",
        "fetchV5ReadOnlyConnectorRateLimit",
        "fetchV5ReadOnlyConnectorAudit",
        "fetchV5ReadOnlyConnectorSafety",
        "fetchV5ReadOnlyConnectorSummary",
    ]:
        assert name in api_client
    assert "V5 Read-Only Connector" in shell
    assert "Read-Only Connector" in page
    assert "Blueprint only" in page
    assert "V5.33 Sandbox Dry-Run Read-Only Connector Blueprint" in docs
    assert "scan_read_only_connector_outputs" in scanner


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def _is_safe(payload: object) -> bool:
    text = json.dumps(payload, default=str).lower()
    blocked = [
        "api_key=demo",
        "secret_value=demo",
        "token=demo",
        "password=demo",
        "authorization",
        "real_order_id",
        "account_id",
        "raw provider response",
        "provider_endpoint_url",
        "read_only_runtime_enabled\": true",
        "sandbox_api_enabled\": true",
        "secret_read_enabled\": true",
        "account_read_enabled\": true",
        "position_read_enabled\": true",
        "balance_read_enabled\": true",
        "order_preview_enabled\": true",
        "order_submission_enabled\": true",
        "broker_connected\": true",
        "real_money_enabled\": true",
        "paper-api.",
        "api.alpaca.",
    ]
    return not any(term in text for term in blocked)
