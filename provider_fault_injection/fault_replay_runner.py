from __future__ import annotations

from provider_fault_injection import boundary
from provider_fault_injection.fault_injector import inject_all_faults, inject_fault


def run_fault_scenario(provider: str, scenario: str) -> dict:
    injected = inject_fault(provider, scenario)
    event_types = [event["event_type"] for event in injected.get("events", [])]
    detected = injected.get("expected_detection") in event_types
    recovered = injected.get("expected_recovery") in event_types
    audit_written = injected.get("expected_audit") in event_types
    errors = list(injected.get("errors", []))
    if not detected:
        errors.append(f"{scenario} was not detected")
    if not recovered:
        errors.append(f"{scenario} was not recovered")
    if not audit_written:
        errors.append(f"{scenario} audit event was not written")
    return {
        "provider": provider,
        "scenario": scenario,
        "fault_type": injected.get("fault_type", "unknown"),
        "detected": detected,
        "recovered": recovered,
        "final_state": injected.get("expected_final_state", "SAFE_RECOVERED"),
        "audit_written": audit_written,
        "events": injected.get("events", []),
        "warnings": [],
        "errors": errors,
        "passed": not errors,
        **boundary(),
    }


def run_all_fault_scenarios(provider: str) -> dict:
    injected = inject_all_faults(provider)
    results = [run_fault_scenario(provider, result["scenario"]) for result in injected["results"]]
    return {
        "provider": provider,
        "total_scenarios": len(results),
        "results": results,
        "passed": sum(1 for result in results if result["passed"]),
        "failed": sum(1 for result in results if not result["passed"]),
        "warnings": [warning for result in results for warning in result.get("warnings", [])],
        "errors": [error for result in results for error in result.get("errors", [])],
        **boundary(),
    }
