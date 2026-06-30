from __future__ import annotations

import re
from pathlib import Path
import json


SENSITIVE_PATTERN = re.compile(r"(api_key|secret|token|password|authorization|database_url|sk-[A-Za-z0-9])", re.IGNORECASE)


def scan_runtime_outputs(paths: list[str | Path]) -> dict:
    findings = []
    for path in paths:
        root = Path(path)
        if not root.exists():
            continue
        files = [root] if root.is_file() else [item for item in root.rglob("*") if item.is_file()]
        for file_path in files:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            for line_no, line in enumerate(text.splitlines(), start=1):
                if SENSITIVE_PATTERN.search(line):
                    findings.append({"path": file_path.as_posix(), "line": line_no, "kind": "sensitive-pattern"})
                    break
    return {"safe": not findings, "findings": findings}


def scan_payload(payload: dict | list | str) -> dict:
    text = json.dumps(payload, default=str) if not isinstance(payload, str) else payload
    findings = []
    for match in SENSITIVE_PATTERN.finditer(text):
        findings.append({"kind": "sensitive-pattern", "match": match.group(0)})
    return {"safe": not findings, "findings": findings}


def scan_deployment_outputs(payload: dict | list | str, report_path: str | Path | None = None) -> dict:
    findings = scan_payload(payload)["findings"]
    if report_path:
        report = Path(report_path)
        if report.exists():
            findings.extend(scan_runtime_outputs([report])["findings"])
    return {"safe": not findings, "findings": findings}


def scan_live_paper_outputs(payload: dict | list | str, report_path: str | Path | None = None) -> dict:
    findings = scan_payload(payload)["findings"]
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    if "broker credential" in text or "/users/apple" in text:
        findings.append({"kind": "sensitive-pattern", "match": "blocked-live-paper-output"})
    if report_path:
        report = Path(report_path)
        if report.exists():
            findings.extend(scan_runtime_outputs([report])["findings"])
    return {"safe": not findings, "findings": findings}


def scan_live_alpha_outputs(payload: dict | list | str, report_path: str | Path | None = None) -> dict:
    findings = scan_payload(payload)["findings"]
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    if "broker credential" in text or "/users/apple" in text:
        findings.append({"kind": "sensitive-pattern", "match": "blocked-live-alpha-output"})
    if report_path:
        report = Path(report_path)
        if report.exists():
            findings.extend(scan_runtime_outputs([report])["findings"])
    return {"safe": not findings, "findings": findings}


def scan_broker_planning_outputs(payload: dict | list | str, report_path: str | Path | None = None) -> dict:
    findings = scan_payload(payload)["findings"]
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    blocked_terms = [
        "broker credential",
        "account_id",
        "authorization",
        "/users/apple",
    ]
    for term in blocked_terms:
        if term in text:
            findings.append({"kind": "sensitive-pattern", "match": "blocked-broker-planning-output"})
            break
    if report_path:
        report = Path(report_path)
        if report.exists():
            findings.extend(scan_runtime_outputs([report])["findings"])
            report_text = report.read_text(encoding="utf-8", errors="ignore").lower()
            if any(term in report_text for term in blocked_terms):
                findings.append({"kind": "sensitive-pattern", "match": "blocked-broker-planning-report"})
    return {"safe": not findings, "findings": findings}


def scan_approval_outputs(payload: dict | list | str, report_path: str | Path | None = None) -> dict:
    findings = scan_payload(payload)["findings"]
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    blocked_terms = [
        "broker credential",
        "account_id",
        "real_order_id",
        "authorization",
        "/users/apple",
    ]
    for term in blocked_terms:
        if term in text:
            findings.append({"kind": "sensitive-pattern", "match": "blocked-approval-output"})
            break
    if report_path:
        report = Path(report_path)
        if report.exists():
            findings.extend(scan_runtime_outputs([report])["findings"])
            report_text = report.read_text(encoding="utf-8", errors="ignore").lower()
            if any(term in report_text for term in blocked_terms):
                findings.append({"kind": "sensitive-pattern", "match": "blocked-approval-report"})
    return {"safe": not findings, "findings": findings}


def scan_sandbox_outputs(payload: dict | list | str, report_path: str | Path | None = None) -> dict:
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    findings = _scan_sandbox_sensitive_text(text)
    blocked_terms = [
        "broker credential",
        "account_id",
        "real_order_id",
        "authorization",
        "/users/apple",
    ]
    for term in blocked_terms:
        if term in text:
            findings.append({"kind": "sensitive-pattern", "match": "blocked-sandbox-output"})
            break
    if report_path:
        report = Path(report_path)
        if report.exists():
            report_text = report.read_text(encoding="utf-8", errors="ignore").lower()
            findings.extend(_scan_sandbox_sensitive_text(report_text))
            if any(term in report_text for term in blocked_terms):
                findings.append({"kind": "sensitive-pattern", "match": "blocked-sandbox-report"})
    return {"safe": not findings, "findings": findings}


def scan_sandbox_simulation_outputs(payload: dict | list | str, report_path: str | Path | None = None) -> dict:
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    findings = _scan_sandbox_sensitive_text(text)
    blocked_terms = [
        "broker credential",
        "account_id",
        "real_order_id",
        "authorization",
        "/users/apple",
    ]
    for term in blocked_terms:
        if term in text:
            findings.append({"kind": "sensitive-pattern", "match": "blocked-sandbox-simulation-output"})
            break
    if report_path:
        report = Path(report_path)
        if report.exists():
            report_text = report.read_text(encoding="utf-8", errors="ignore").lower()
            findings.extend(_scan_sandbox_sensitive_text(report_text))
            if any(term in report_text for term in blocked_terms):
                findings.append({"kind": "sensitive-pattern", "match": "blocked-sandbox-simulation-report"})
    return {"safe": not findings, "findings": findings}


def scan_sandbox_robustness_outputs(payload: dict | list | str, report_path: str | Path | None = None) -> dict:
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    findings = _scan_sandbox_sensitive_text(text)
    blocked_terms = [
        "broker credential",
        "account_id",
        "real_order_id",
        "authorization",
        "/users/apple",
    ]
    for term in blocked_terms:
        if term in text:
            findings.append({"kind": "sensitive-pattern", "match": "blocked-sandbox-robustness-output"})
            break
    if report_path:
        report = Path(report_path)
        if report.exists():
            report_text = report.read_text(encoding="utf-8", errors="ignore").lower()
            findings.extend(_scan_sandbox_sensitive_text(report_text))
            if any(term in report_text for term in blocked_terms):
                findings.append({"kind": "sensitive-pattern", "match": "blocked-sandbox-robustness-report"})
    return {"safe": not findings, "findings": findings}


def scan_sandbox_connector_outputs(payload: dict | list | str, report_path: str | Path | None = None) -> dict:
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    findings = _scan_sandbox_sensitive_text(text)
    blocked_terms = [
        "broker credential",
        "account_id",
        "real_order_id",
        "raw provider response",
        "authorization",
        "/users/apple",
    ]
    for term in blocked_terms:
        if term in text:
            findings.append({"kind": "sensitive-pattern", "match": "blocked-sandbox-connector-output"})
            break
    if report_path:
        report = Path(report_path)
        if report.exists():
            report_text = report.read_text(encoding="utf-8", errors="ignore").lower()
            findings.extend(_scan_sandbox_sensitive_text(report_text))
            if any(term in report_text for term in blocked_terms):
                findings.append({"kind": "sensitive-pattern", "match": "blocked-sandbox-connector-report"})
    return {"safe": not findings, "findings": findings}


def scan_sandbox_connector_mock_outputs(payload: dict | list | str, report_path: str | Path | None = None) -> dict:
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    findings = _scan_sandbox_sensitive_text(text)
    blocked_terms = [
        "broker credential",
        "account_id",
        "real_order_id",
        "raw provider response",
        "authorization",
        "/users/apple",
    ]
    for term in blocked_terms:
        if term in text:
            findings.append({"kind": "sensitive-pattern", "match": "blocked-sandbox-connector-mock-output"})
            break
    if report_path:
        report = Path(report_path)
        if report.exists():
            report_text = report.read_text(encoding="utf-8", errors="ignore").lower()
            findings.extend(_scan_sandbox_sensitive_text(report_text))
            if any(term in report_text for term in blocked_terms):
                findings.append({"kind": "sensitive-pattern", "match": "blocked-sandbox-connector-mock-report"})
    return {"safe": not findings, "findings": findings}


def scan_broker_adapter_outputs(payload: dict | list | str, report_path: str | Path | None = None) -> dict:
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    findings = _scan_sandbox_sensitive_text(text)
    blocked_terms = [
        "broker credential",
        "account_id",
        "real_order_id",
        "authorization",
        "/users/apple",
    ]
    runtime_terms = [
        "alpaca_trade_api",
        "ib_insync",
        "tigeropen",
        "robin_stocks",
        "oauthlib",
    ]
    for term in blocked_terms + runtime_terms:
        if term in text:
            findings.append({"kind": "sensitive-pattern", "match": "blocked-broker-adapter-output"})
            break
    if report_path:
        report = Path(report_path)
        if report.exists():
            report_text = report.read_text(encoding="utf-8", errors="ignore").lower()
            findings.extend(_scan_sandbox_sensitive_text(report_text))
            if any(term in report_text for term in blocked_terms + runtime_terms):
                findings.append({"kind": "sensitive-pattern", "match": "blocked-broker-adapter-report"})
    return {"safe": not findings, "findings": findings}


def scan_sandbox_bridge_outputs(payload: dict | list | str, report_path: str | Path | None = None) -> dict:
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    findings = _scan_sandbox_sensitive_text(text)
    blocked_terms = [
        "broker credential",
        "account_id",
        "real_order_id",
        "authorization",
        "/users/apple",
    ]
    runtime_terms = [
        "alpaca_trade_api",
        "ib_insync",
        "tigeropen",
        "robin_stocks",
        "oauthlib",
        "https://sandbox",
    ]
    for term in blocked_terms + runtime_terms:
        if term in text:
            findings.append({"kind": "sensitive-pattern", "match": "blocked-sandbox-bridge-output"})
            break
    if report_path:
        report = Path(report_path)
        if report.exists():
            report_text = report.read_text(encoding="utf-8", errors="ignore").lower()
            findings.extend(_scan_sandbox_sensitive_text(report_text))
            if any(term in report_text for term in blocked_terms + runtime_terms):
                findings.append({"kind": "sensitive-pattern", "match": "blocked-sandbox-bridge-report"})
    return {"safe": not findings, "findings": findings}


def scan_integration_test_outputs(payload: dict | list | str, report_path: str | Path | None = None) -> dict:
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    findings = _scan_sandbox_sensitive_text(text)
    blocked_terms = [
        "broker credential",
        "account_id",
        "real_order_id",
        "authorization",
        "/users/apple",
    ]
    runtime_terms = [
        "alpaca_trade_api",
        "ib_insync",
        "tigeropen",
        "robin_stocks",
        "oauthlib",
        "https://sandbox",
    ]
    for term in blocked_terms + runtime_terms:
        if term in text:
            findings.append({"kind": "sensitive-pattern", "match": "blocked-integration-test-output"})
            break
    if report_path:
        report = Path(report_path)
        if report.exists():
            report_text = report.read_text(encoding="utf-8", errors="ignore").lower()
            findings.extend(_scan_sandbox_sensitive_text(report_text))
            if any(term in report_text for term in blocked_terms + runtime_terms):
                findings.append({"kind": "sensitive-pattern", "match": "blocked-integration-test-report"})
    return {"safe": not findings, "findings": findings}


def scan_transition_blueprint_outputs(payload: dict | list | str, report_path: str | Path | None = None) -> dict:
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    findings = _scan_sandbox_sensitive_text(text)
    blocked_terms = [
        "broker credential",
        "account_id",
        "real_order_id",
        "raw provider response",
        "authorization",
        "/users/apple",
    ]
    runtime_terms = [
        "alpaca_trade_api",
        "ib_insync",
        "tigeropen",
        "robin_stocks",
        "oauthlib",
        "https://sandbox",
    ]
    for term in blocked_terms + runtime_terms:
        if term in text:
            findings.append({"kind": "sensitive-pattern", "match": "blocked-transition-blueprint-output"})
            break
    if report_path:
        report = Path(report_path)
        if report.exists():
            report_text = report.read_text(encoding="utf-8", errors="ignore").lower()
            findings.extend(_scan_sandbox_sensitive_text(report_text))
            if any(term in report_text for term in blocked_terms + runtime_terms):
                findings.append({"kind": "sensitive-pattern", "match": "blocked-transition-blueprint-report"})
    return {"safe": not findings, "findings": findings}


def scan_provider_selection_outputs(payload: dict | list | str, report_path: str | Path | None = None) -> dict:
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    findings = _scan_sandbox_sensitive_text(text)
    blocked_terms = [
        "broker credential",
        "account_id",
        "real_order_id",
        "raw provider response",
        "authorization",
        "/users/apple",
    ]
    runtime_terms = [
        "alpaca_trade_api",
        "ib_insync",
        "tigeropen",
        "robin_stocks",
        "oauthlib",
        "https://sandbox",
    ]
    for term in blocked_terms + runtime_terms:
        if term in text:
            findings.append({"kind": "sensitive-pattern", "match": "blocked-provider-selection-output"})
            break
    if report_path:
        report = Path(report_path)
        if report.exists():
            report_text = report.read_text(encoding="utf-8", errors="ignore").lower()
            findings.extend(_scan_sandbox_sensitive_text(report_text))
            if any(term in report_text for term in blocked_terms + runtime_terms):
                findings.append({"kind": "sensitive-pattern", "match": "blocked-provider-selection-report"})
    return {"safe": not findings, "findings": findings}


def scan_provider_onboarding_outputs(payload: dict | list | str, report_path: str | Path | None = None) -> dict:
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    findings = _scan_sandbox_sensitive_text(text)
    blocked_terms = [
        "broker credential",
        "account_id",
        "real_order_id",
        "raw provider response",
        "provider portal session",
        "authorization",
        "/users/apple",
    ]
    runtime_terms = [
        "alpaca_trade_api",
        "ib_insync",
        "tigeropen",
        "robin_stocks",
        "oauthlib",
        "https://sandbox",
        "provider portal login",
    ]
    for term in blocked_terms + runtime_terms:
        if term in text:
            findings.append({"kind": "sensitive-pattern", "match": "blocked-provider-onboarding-output"})
            break
    if report_path:
        report = Path(report_path)
        if report.exists():
            report_text = report.read_text(encoding="utf-8", errors="ignore").lower()
            findings.extend(_scan_sandbox_sensitive_text(report_text))
            if any(term in report_text for term in blocked_terms + runtime_terms):
                findings.append({"kind": "sensitive-pattern", "match": "blocked-provider-onboarding-report"})
    return {"safe": not findings, "findings": findings}


def scan_provider_connector_design_outputs(payload: dict | list | str, report_path: str | Path | None = None) -> dict:
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    findings = _scan_sandbox_sensitive_text(text)
    blocked_terms = [
        "broker credential",
        "account_id",
        "real_order_id",
        "raw provider payload",
        "raw provider response:",
        "provider endpoint url",
        "authorization",
        "/users/apple",
    ]
    runtime_terms = [
        "alpaca_trade_api",
        "ib_insync",
        "tigeropen",
        "robin_stocks",
        "oauthlib",
        "https://sandbox",
        "provider portal login",
    ]
    for term in blocked_terms + runtime_terms:
        if term in text:
            findings.append({"kind": "sensitive-pattern", "match": "blocked-provider-connector-design-output"})
            break
    if report_path:
        report = Path(report_path)
        if report.exists():
            report_text = report.read_text(encoding="utf-8", errors="ignore").lower()
            findings.extend(_scan_sandbox_sensitive_text(report_text))
            if any(term in report_text for term in blocked_terms + runtime_terms):
                findings.append({"kind": "sensitive-pattern", "match": "blocked-provider-connector-design-report"})
    return {"safe": not findings, "findings": findings}


def scan_provider_mock_contract_outputs(payload: dict | list | str, report_path: str | Path | None = None) -> dict:
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    findings = _scan_sandbox_sensitive_text(text)
    blocked_terms = [
        "broker credential",
        "account_id",
        "real_order_id",
        "raw provider payload:",
        "raw provider response:",
        "provider endpoint url",
        "authorization",
        "/users/apple",
    ]
    runtime_terms = [
        "alpaca_trade_api",
        "ib_insync",
        "tigeropen",
        "robin_stocks",
        "oauthlib",
        "https://sandbox",
        "provider portal login",
    ]
    for term in blocked_terms + runtime_terms:
        if term in text:
            findings.append({"kind": "sensitive-pattern", "match": "blocked-provider-mock-contract-output"})
            break
    if report_path:
        report = Path(report_path)
        if report.exists():
            report_text = report.read_text(encoding="utf-8", errors="ignore").lower()
            findings.extend(_scan_sandbox_sensitive_text(report_text))
            if any(term in report_text for term in blocked_terms + runtime_terms):
                findings.append({"kind": "sensitive-pattern", "match": "blocked-provider-mock-contract-report"})
    return {"safe": not findings, "findings": findings}


def scan_provider_offline_replay_outputs(payload: dict | list | str, report_path: str | Path | None = None) -> dict:
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    findings = _scan_sandbox_sensitive_text(text)
    blocked_terms = [
        "broker credential",
        "account_id",
        "real_order_id",
        "raw provider payload:",
        "raw provider response:",
        "provider_endpoint_url",
        "authorization",
        "/users/apple",
    ]
    runtime_terms = [
        "alpaca_trade_api",
        "ib_insync",
        "tigeropen",
        "robin_stocks",
        "oauthlib",
        "https://sandbox",
        "paper-api.",
        "provider portal login",
    ]
    for term in blocked_terms + runtime_terms:
        if term in text:
            findings.append({"kind": "sensitive-pattern", "match": "blocked-provider-offline-replay-output"})
            break
    if report_path:
        report = Path(report_path)
        if report.exists():
            report_text = report.read_text(encoding="utf-8", errors="ignore").lower()
            findings.extend(_scan_sandbox_sensitive_text(report_text))
            if any(term in report_text for term in blocked_terms + runtime_terms):
                findings.append({"kind": "sensitive-pattern", "match": "blocked-provider-offline-replay-report"})
    return {"safe": not findings, "findings": findings}


def scan_provider_fault_injection_outputs(payload: dict | list | str, report_path: str | Path | None = None) -> dict:
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    findings = _scan_sandbox_sensitive_text(text)
    blocked_terms = [
        "broker credential",
        "account_id",
        "real_order_id",
        "raw provider payload:",
        "raw provider response:",
        "provider_endpoint_url",
        "authorization",
        "/users/apple",
    ]
    runtime_terms = [
        "alpaca_trade_api",
        "ib_insync",
        "tigeropen",
        "robin_stocks",
        "oauthlib",
        "https://sandbox",
        "paper-api.",
        "provider portal login",
    ]
    for term in blocked_terms + runtime_terms:
        if term in text:
            findings.append({"kind": "sensitive-pattern", "match": "blocked-provider-fault-injection-output"})
            break
    if report_path:
        report = Path(report_path)
        if report.exists():
            report_text = report.read_text(encoding="utf-8", errors="ignore").lower()
            findings.extend(_scan_sandbox_sensitive_text(report_text))
            if any(term in report_text for term in blocked_terms + runtime_terms):
                findings.append({"kind": "sensitive-pattern", "match": "blocked-provider-fault-injection-report"})
    return {"safe": not findings, "findings": findings}


def scan_provider_offline_soak_outputs(payload: dict | list | str, report_path: str | Path | None = None) -> dict:
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    findings = _scan_sandbox_sensitive_text(text)
    blocked_terms = [
        "broker credential",
        "account_id",
        "real_order_id",
        "raw provider payload:",
        "raw provider response:",
        "provider_endpoint_url",
        "authorization",
        "/users/apple",
    ]
    runtime_terms = [
        "alpaca_trade_api",
        "ib_insync",
        "tigeropen",
        "robin_stocks",
        "oauthlib",
        "https://sandbox",
        "paper-api.",
        "provider portal login",
    ]
    for term in blocked_terms + runtime_terms:
        if term in text:
            findings.append({"kind": "sensitive-pattern", "match": "blocked-provider-offline-soak-output"})
            break
    if report_path:
        report = Path(report_path)
        if report.exists():
            report_text = report.read_text(encoding="utf-8", errors="ignore").lower()
            findings.extend(_scan_sandbox_sensitive_text(report_text))
            if any(term in report_text for term in blocked_terms + runtime_terms):
                findings.append({"kind": "sensitive-pattern", "match": "blocked-provider-offline-soak-report"})
    return {"safe": not findings, "findings": findings}


def scan_sandbox_evidence_outputs(payload: dict | list | str, report_path: str | Path | None = None) -> dict:
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    findings = _scan_sandbox_sensitive_text(text)
    blocked_terms = [
        "broker credential",
        "account_id",
        "real_order_id",
        "raw provider payload:",
        "raw provider response:",
        "provider_endpoint_url",
        "authorization",
        "/users/apple",
    ]
    runtime_terms = [
        "alpaca_trade_api",
        "ib_insync",
        "tigeropen",
        "robin_stocks",
        "oauthlib",
        "https://sandbox",
        "paper-api.",
        "provider portal login",
    ]
    for term in blocked_terms + runtime_terms:
        if term in text:
            findings.append({"kind": "sensitive-pattern", "match": "blocked-sandbox-evidence-output"})
            break
    if report_path:
        report = Path(report_path)
        if report.exists():
            report_text = report.read_text(encoding="utf-8", errors="ignore").lower()
            findings.extend(_scan_sandbox_sensitive_text(report_text))
            if any(term in report_text for term in blocked_terms + runtime_terms):
                findings.append({"kind": "sensitive-pattern", "match": "blocked-sandbox-evidence-report"})
    return {"safe": not findings, "findings": findings}


def scan_credential_vault_design_outputs(payload: dict | list | str, report_path: str | Path | None = None) -> dict:
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    findings = _scan_sandbox_sensitive_text(text)
    blocked_terms = [
        "secret_value=demo",
        "api_key=demo",
        "token=demo",
        "password=demo",
        "account_id",
        "real_order_id",
        "raw provider payload:",
        "raw provider response:",
        "provider_endpoint_url",
        "authorization",
        "/users/apple",
    ]
    runtime_terms = [
        "alpaca_trade_api",
        "ib_insync",
        "tigeropen",
        "robin_stocks",
        "oauthlib",
        "https://sandbox",
        "paper-api.",
        "provider portal login",
    ]
    for term in blocked_terms + runtime_terms:
        if term in text:
            findings.append({"kind": "sensitive-pattern", "match": "blocked-credential-vault-design-output"})
            break
    if report_path:
        report = Path(report_path)
        if report.exists():
            report_text = report.read_text(encoding="utf-8", errors="ignore").lower()
            findings.extend(_scan_sandbox_sensitive_text(report_text))
            if any(term in report_text for term in blocked_terms + runtime_terms):
                findings.append({"kind": "sensitive-pattern", "match": "blocked-credential-vault-design-report"})
    return {"safe": not findings, "findings": findings}


def _scan_sandbox_sensitive_text(text: str) -> list[dict]:
    findings = []
    patterns = [
        r"sk-[a-z0-9]",
        r"api[_-]?key\s*[:=]\s*[a-z0-9]",
        r"token\s*[:=]\s*[a-z0-9]",
        r"password\s*[:=]\s*[a-z0-9]",
        r"authorization\s*[:=]\s*[a-z0-9]",
        r"-----begin",
    ]
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            findings.append({"kind": "sensitive-pattern", "match": "blocked-sandbox-sensitive-value"})
            break
    return findings
