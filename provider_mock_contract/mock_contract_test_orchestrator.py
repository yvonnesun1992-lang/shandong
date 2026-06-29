from __future__ import annotations

from provider_mock_contract import boundary
from provider_mock_contract.contract_schema_validator import validate_all_mock_payloads
from provider_mock_contract.error_mapping_contract_test import test_error_mapping
from provider_mock_contract.idempotency_contract_test import test_idempotency_policy
from provider_mock_contract.mock_contract_safety_validator import build_mock_contract_safety_summary
from provider_mock_contract.order_state_machine_contract_test import test_order_state_machine
from provider_mock_contract.request_mapping_contract_test import test_order_request_mapping
from provider_mock_contract.response_normalization_contract_test import test_response_normalization


def run_mock_contract_tests(provider: str) -> list[dict]:
    return [
        {"name": "schema_validation", **validate_all_mock_payloads(provider)},
        {"name": "request_mapping", **test_order_request_mapping(provider)},
        {"name": "response_normalization", **test_response_normalization(provider)},
        {"name": "error_mapping", **test_error_mapping(provider)},
        {"name": "idempotency", **test_idempotency_policy(provider)},
        {"name": "order_state_machine", **test_order_state_machine(provider)},
        {"name": "safety", **build_mock_contract_safety_summary()},
    ]


def summarize_mock_contract_results(results: list[dict]) -> dict:
    errors = [error for result in results for error in result.get("errors", [])]
    warnings = [warning for result in results for warning in result.get("warnings", [])]
    passed = sum(1 for result in results if result.get("passed", result.get("valid", result.get("safe", False))) is True)
    failed = len(results) - passed
    return {
        "provider": results[0].get("provider", "unknown") if results else "unknown",
        "total_tests": len(results),
        "passed": passed,
        "failed": failed,
        "warnings": warnings or ["mock contract tests are offline only; runtime validation remains future work"],
        "errors": errors,
        "verdict": "FAIL" if errors or failed else "WARNING",
        **boundary(),
    }
