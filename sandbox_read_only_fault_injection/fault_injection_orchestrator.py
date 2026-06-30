from __future__ import annotations

from sandbox_read_only_fault_injection.audit_failure_simulator import simulate_audit_write_failure, validate_audit_failure_handling
from sandbox_read_only_fault_injection.fault_injection_runner import run_fault_injection
from sandbox_read_only_fault_injection.fault_injection_safety_validator import build_fault_injection_safety_summary
from sandbox_read_only_fault_injection.fault_payload_catalog import build_all_fault_payloads
from sandbox_read_only_fault_injection.fault_schema_validator import validate_all_fault_schemas
from sandbox_read_only_fault_injection.init import boundary
from sandbox_read_only_fault_injection.order_path_intrusion_detector import detect_all_order_path_intrusions
from sandbox_read_only_fault_injection.rate_limit_fault_simulator import simulate_rate_limit_fault, validate_rate_limit_fault_handling
from sandbox_read_only_fault_injection.redaction_failure_detector import detect_all_redaction_failures
from sandbox_read_only_fault_injection.stale_snapshot_detector import detect_all_stale_snapshots


def run_read_only_fault_injection(provider: str = "alpaca") -> dict:
    result = {
        **boundary(),
        "provider": provider,
        "payloads": build_all_fault_payloads(provider),
        "schema": validate_all_fault_schemas(provider),
        "redaction": detect_all_redaction_failures(provider),
        "stale": detect_all_stale_snapshots(provider),
        "audit_failure": validate_audit_failure_handling(simulate_audit_write_failure(provider)),
        "rate_limit": validate_rate_limit_fault_handling(simulate_rate_limit_fault(provider)),
        "order_intrusion": detect_all_order_path_intrusions(provider),
        "runner": run_fault_injection(provider),
        "safety": build_fault_injection_safety_summary(),
    }
    return result


def summarize_fault_injection(result: dict) -> dict:
    runner = result.get("runner", {})
    errors = list(runner.get("errors", []))
    unexpectedly_accepted = list(runner.get("unexpectedly_accepted", []))
    warnings = []
    for key in ["schema", "redaction", "stale", "audit_failure", "rate_limit", "order_intrusion", "runner", "safety"]:
        warnings.extend(result.get(key, {}).get("warnings", []))
    safe = not errors and not unexpectedly_accepted
    return {
        **boundary(),
        "provider": result.get("provider", "alpaca"),
        "total_fault_cases": runner.get("total_fault_cases", 0),
        "blocked_fault_cases": runner.get("blocked_fault_cases", 0),
        "unexpectedly_accepted": unexpectedly_accepted,
        "errors": errors,
        "warnings": warnings,
        "verdict": "FAIL" if not safe else "WARNING" if warnings else "PASS",
    }
