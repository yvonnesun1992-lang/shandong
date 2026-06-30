from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient


FALSE_KEYS = [
    "vault_runtime_enabled",
    "secret_read_enabled",
    "secret_write_enabled",
    "sandbox_api_enabled",
    "broker_connected",
    "order_submission_enabled",
    "real_money_enabled",
]


def test_vault_design_config_defaults_and_blocks_real_path_env(monkeypatch):
    from config.v5_credential_vault_design_config import get_vault_design_mode, get_vault_design_provider, get_vault_design_status

    assert get_vault_design_mode() == "vault_design_only"
    assert get_vault_design_provider() in {"alpaca", "ibkr", "futu", "tiger", "schwab"}
    status = get_vault_design_status()
    assert status["version"] == "V5.27"
    assert status["vault_design_only"] is True
    assert status["paper_trading"] is True
    for key in FALSE_KEYS:
        assert status[key] is False

    monkeypatch.setenv("SHANDONG_V5_ENABLE_VAULT_RUNTIME", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_SECRET_READ", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_SECRET_WRITE", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_SANDBOX_API", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_ORDER_SUBMISSION", "true")
    monkeypatch.setenv("SHANDONG_V5_ENABLE_REAL_MONEY", "true")
    blocked = get_vault_design_status()
    for key in FALSE_KEYS:
        assert blocked[key] is False
    warnings = " | ".join(blocked["warnings"]).lower()
    assert "vault runtime requested but blocked in v5.27" in warnings
    assert "secret read requested but blocked in v5.27" in warnings
    assert "secret write requested but blocked in v5.27" in warnings
    assert "sandbox api requested but blocked in v5.27" in warnings
    assert "order submission requested but blocked in v5.27" in warnings
    assert "real money requested but blocked in v5.27" in warnings
    assert _is_safe(blocked)


def test_vault_contract_policies_audit_safety_and_orchestrator():
    from credential_vault_design.rotation_revocation_runbook import build_rotation_revocation_runbook
    from credential_vault_design.secret_access_policy import build_secret_access_policy
    from credential_vault_design.secret_scope_policy import build_secret_scope_policy
    from credential_vault_design.vault_audit_design import build_vault_audit_design
    from credential_vault_design.vault_design_orchestrator import build_vault_design, summarize_vault_design
    from credential_vault_design.vault_interface_contract import (
        audit_secret_access_plan,
        get_secret_reference,
        revoke_secret_plan,
        rotate_secret_plan,
        validate_secret_reference,
    )
    from credential_vault_design.vault_safety_validator import build_vault_safety_summary, validate_vault_design_safety

    reference = get_secret_reference("alpaca", "sandbox_read_only_key")
    validation = validate_secret_reference(reference)
    rotation = rotate_secret_plan(reference)
    revoke = revoke_secret_plan(reference)
    audit_plan = audit_secret_access_plan(reference)
    scope = build_secret_scope_policy()
    access = build_secret_access_policy()
    runbook = build_rotation_revocation_runbook("alpaca")
    audit = build_vault_audit_design("alpaca")
    safety = build_vault_safety_summary()
    design = build_vault_design("alpaca")
    summary = summarize_vault_design(design)

    assert reference["secret_reference"] == "SECRET_REF_PLACEHOLDER"
    assert reference["secret_value_present"] is False
    assert validation["valid"] is True
    assert rotation["secret_reference"] == "SECRET_REF_PLACEHOLDER"
    assert revoke["secret_reference"] == "SECRET_REF_PLACEHOLDER"
    assert audit_plan["raw_secret_logged"] is False
    assert scope["sandbox_real_isolated"] is True
    assert scope["read_only_trading_isolated"] is True
    assert scope["frontend_access_allowed"] is False
    assert access["roles"]["frontend_user"]["access_enabled"] is False
    assert access["roles"]["runtime_service"]["access_enabled"] is False
    assert runbook["provider"] == "alpaca"
    assert audit["raw_secret_logged"] is False
    assert audit["secret_value_redacted"] is True
    assert safety["safe"] is True
    assert validate_vault_design_safety({"vault_runtime_enabled": True})["safe"] is False
    assert validate_vault_design_safety({"secret_read_enabled": True})["safe"] is False
    assert validate_vault_design_safety({"secret_write_enabled": True})["safe"] is False
    assert validate_vault_design_safety({"payload": "secret_value=demo"})["safe"] is False
    assert validate_vault_design_safety({"payload": "api_key=demo"})["safe"] is False
    assert validate_vault_design_safety({"payload": "token=demo"})["safe"] is False
    assert summary["verdict"] in {"PASS", "WARNING"}
    for item in [reference, validation, rotation, revoke, audit_plan, scope, access, runbook, audit, safety, summary]:
        assert item["vault_design_only"] is True
        assert _is_safe(item)


def test_credential_vault_design_api_endpoints_return_safe_boundaries():
    from src.api.v2.server import create_v2_api_app

    client = TestClient(create_v2_api_app())
    paths = [
        "/api/v5/credential-vault-design/status",
        "/api/v5/credential-vault-design/interface",
        "/api/v5/credential-vault-design/scope-policy",
        "/api/v5/credential-vault-design/access-policy",
        "/api/v5/credential-vault-design/rotation-revocation",
        "/api/v5/credential-vault-design/audit",
        "/api/v5/credential-vault-design/safety",
        "/api/v5/credential-vault-design/summary",
    ]
    for path in paths:
        response = client.get(path)
        payload = response.json()
        text = json.dumps(payload).lower()
        assert response.status_code == 200
        assert payload["success"] is True
        assert "vault_design_only" in text
        assert "paper_trading" in text
        for key in FALSE_KEYS:
            assert key in text
        assert _is_safe(payload)


def test_report_cli_frontend_docs_navigation_and_security_scan_are_present():
    from credential_vault_design.credential_vault_design_report import generate_credential_vault_design_report
    from runtime.security_scan import scan_credential_vault_design_outputs

    report = generate_credential_vault_design_report(provider="alpaca")
    assert report["path"].endswith("reports/v5_27_credential_vault_design_report.md")
    assert report["verdict"] in {"PASS", "WARNING", "FAIL"}
    assert report["vault_design_only"] is True
    assert scan_credential_vault_design_outputs(report)["safe"] is True
    assert _is_safe(report)

    for args in [[], ["--provider", "alpaca"], ["--provider", "ibkr"], ["--check", "safety"], ["--check", "access-policy"]]:
        completed = subprocess.run(
            [sys.executable, "scripts/run_v527_credential_vault_design.py", *args],
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0
        payload = json.loads(completed.stdout)
        assert payload["verdict"] in {"PASS", "WARNING"}
        assert payload["vault_design_only"] is True
        assert _is_safe(payload)

    api_client = _read("web/frontend/app/lib/apiClient.ts")
    page = _read("web/frontend/app/v5-credential-vault-design/page.tsx")
    shell = _read("web/frontend/app/components/ProductionShell.tsx")
    docs = _read("docs/V5_CREDENTIAL_VAULT_DESIGN.md")
    scanner = _read("runtime/security_scan.py")
    for name in [
        "fetchV5CredentialVaultDesignStatus",
        "fetchV5CredentialVaultDesignInterface",
        "fetchV5CredentialVaultDesignScopePolicy",
        "fetchV5CredentialVaultDesignAccessPolicy",
        "fetchV5CredentialVaultDesignRotationRevocation",
        "fetchV5CredentialVaultDesignAudit",
        "fetchV5CredentialVaultDesignSafety",
        "fetchV5CredentialVaultDesignSummary",
    ]:
        assert name in api_client
    assert "V5 Credential Vault" in shell
    assert "Credential Vault Status" in page
    assert "Vault Interface Contract" in page
    assert "V5.27 Credential Vault Interface Design" in docs
    assert "scan_credential_vault_design_outputs" in scanner


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def _is_safe(payload: object) -> bool:
    text = json.dumps(payload, default=str).lower()
    blocked = [
        "secret_value=demo",
        "api_key=demo",
        "token=demo",
        "password=demo",
        "authorization",
        "real_order_id",
        "account_id",
        "raw provider response",
        "sandbox_api_enabled\": true",
        "order_submission_enabled\": true",
        "broker_connected\": true",
        "real_money_enabled\": true",
        "paper-api.",
        "api.alpaca.",
    ]
    return not any(term in text for term in blocked)
