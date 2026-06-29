from __future__ import annotations

from pathlib import Path

from config.v5_provider_mock_contract_config import get_mock_contract_status, get_mock_contract_provider
from provider_mock_contract import boundary
from provider_mock_contract.contract_schema_validator import validate_all_mock_payloads
from provider_mock_contract.error_mapping_contract_test import test_error_mapping
from provider_mock_contract.idempotency_contract_test import test_idempotency_policy
from provider_mock_contract.mock_contract_safety_validator import build_mock_contract_safety_summary
from provider_mock_contract.mock_contract_test_orchestrator import run_mock_contract_tests, summarize_mock_contract_results
from provider_mock_contract.mock_provider_payloads import build_all_mock_payloads
from provider_mock_contract.order_state_machine_contract_test import test_order_state_machine
from provider_mock_contract.request_mapping_contract_test import test_order_request_mapping
from provider_mock_contract.response_normalization_contract_test import test_response_normalization


REPORT_PATH = Path("reports/v5_22_provider_mock_contract_report.md")


def build_provider_mock_contract_summary(provider: str | None = None, check: str = "all") -> dict:
    selected = provider or get_mock_contract_provider()
    results = run_mock_contract_tests(selected)
    summary = summarize_mock_contract_results(results)
    return {
        "version": "V5.22",
        "check": check,
        "provider": selected,
        "mock_contract_status": get_mock_contract_status(),
        "payload_catalog": build_all_mock_payloads(selected),
        "schema_validation": validate_all_mock_payloads(selected),
        "request_mapping": test_order_request_mapping(selected),
        "response_normalization": test_response_normalization(selected),
        "error_mapping": test_error_mapping(selected),
        "idempotency": test_idempotency_policy(selected),
        "state_machine": test_order_state_machine(selected),
        "safety": build_mock_contract_safety_summary(),
        "test_summary": summary,
        "missing_production_requirements": [
            "real sandbox connector remains disabled",
            "sandbox API remains disabled",
            "account read remains disabled",
            "order submission remains disabled",
            "raw provider payload storage remains prohibited",
        ],
        "warnings": summary["warnings"],
        "verdict": "PASS" if summary["failed"] == 0 and not summary["errors"] else "FAIL",
        **boundary(),
    }


def generate_provider_mock_contract_report(provider: str | None = None, check: str = "all") -> dict:
    summary = build_provider_mock_contract_summary(provider=provider, check=check)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(_render_report(summary), encoding="utf-8")
    verdict = "WARNING" if summary["verdict"] == "PASS" and summary["warnings"] else summary["verdict"]
    return {"verdict": verdict, "path": REPORT_PATH.as_posix(), "mock_contract_only": True, "summary": summary, "warnings": summary["warnings"]}


def _render_report(summary: dict) -> str:
    return f"""# V5.22 Provider Sandbox Connector Mock Contract Test

Verdict: {summary['verdict']}

## Mock Contract Mode

- Mode: {summary['mock_contract_status']['mock_contract_mode']}
- Provider: {summary['provider']}
- Mock contract only: true
- Mock contract runtime enabled: false
- Sandbox API enabled: false
- Account read enabled: false
- Order submission enabled: false
- Broker connected: false
- Real money enabled: false
- Paper trading: true

## Mock Payload Catalog

- Payloads: {len(summary['payload_catalog']['payloads'])}

## Schema Validation

- Valid: {str(summary['schema_validation']['valid']).lower()}
- Checked payloads: {summary['schema_validation']['checked_payloads']}

## Request Mapping Contract Test

- Passed: {str(summary['request_mapping']['passed']).lower()}
- Order submission enabled: false

## Response Normalization Contract Test

- Passed: {str(summary['response_normalization']['passed']).lower()}
- Tested statuses: {', '.join(summary['response_normalization']['tested_statuses'])}

## Error Mapping Contract Test

- Passed: {str(summary['error_mapping']['passed']).lower()}
- Tested errors: {len(summary['error_mapping']['tested_errors'])}

## Idempotency Contract Test

- Passed: {str(summary['idempotency']['passed']).lower()}
- Duplicate order protection: true

## Order State Machine Contract Test

- Passed: {str(summary['state_machine']['passed']).lower()}
- Sandbox submission enabled: false
- Real submission enabled: false

## Safety Validation

- Safe: {str(summary['safety']['safe']).lower()}
- Errors: {len(summary['safety']['errors'])}

## Missing Production Requirements

{chr(10).join(f'- {item}' for item in summary['missing_production_requirements'])}

## Boundary

Current stage is mock contract test only.
Current stage does not access provider portal.
Current stage does not connect to a real broker.
Current stage does not connect to sandbox API.
Current stage does not create API keys.
Current stage does not read real accounts.
Current stage does not submit real or sandbox orders.
Current stage does not use real funds.
Current stage is not a production trading system.
"""
