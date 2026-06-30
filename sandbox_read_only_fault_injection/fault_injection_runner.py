from __future__ import annotations

from sandbox_read_only_fault_injection.audit_failure_simulator import (
    simulate_audit_write_failure,
    validate_audit_failure_handling,
)
from sandbox_read_only_fault_injection.fault_payload_catalog import FAULT_TYPES, build_fault_payload
from sandbox_read_only_fault_injection.fault_schema_validator import validate_fault_schema
from sandbox_read_only_fault_injection.init import boundary
from sandbox_read_only_fault_injection.order_path_intrusion_detector import detect_order_path_intrusion
from sandbox_read_only_fault_injection.rate_limit_fault_simulator import (
    simulate_rate_limit_fault,
    validate_rate_limit_fault_handling,
)
from sandbox_read_only_fault_injection.redaction_failure_detector import detect_redaction_failure
from sandbox_read_only_fault_injection.stale_snapshot_detector import detect_stale_snapshot


def run_fault_case(provider: str = "alpaca", fault_type: str = "unredacted_account_id") -> dict:
    payload = build_fault_payload(provider, fault_type)
    schema = validate_fault_schema(payload)
    redaction = detect_redaction_failure(payload)
    stale = detect_stale_snapshot(payload)
    audit = validate_audit_failure_handling(simulate_audit_write_failure(provider)) if fault_type == "audit_write_failure" else {**boundary(), "audit_failure_detected": False, "findings": []}
    rate_limit = validate_rate_limit_fault_handling(simulate_rate_limit_fault(provider)) if fault_type == "rate_limit_error" else {**boundary(), "rate_limit_fault_detected": False, "findings": []}
    order = detect_order_path_intrusion(payload)
    detected = any(
        [
            schema["schema_faults_detected"],
            redaction["redaction_failure_detected"],
            stale["stale_detected"],
            audit["audit_failure_detected"],
            rate_limit["rate_limit_fault_detected"],
            order["order_intrusion_detected"],
        ]
    )
    warnings = (
        schema.get("warnings", [])
        + redaction.get("warnings", [])
        + stale.get("warnings", [])
        + audit.get("warnings", [])
        + rate_limit.get("warnings", [])
        + order.get("warnings", [])
    )
    return {
        **boundary(),
        "provider": provider,
        "fault_type": fault_type,
        "schema_fault_detected": schema["schema_faults_detected"],
        "redaction_failure_detected": redaction["redaction_failure_detected"],
        "stale_detected": stale["stale_detected"],
        "audit_failure_detected": audit["audit_failure_detected"],
        "rate_limit_fault_detected": rate_limit["rate_limit_fault_detected"],
        "order_intrusion_detected": order["order_intrusion_detected"],
        "accepted": False,
        "blocked": detected,
        "warnings": warnings or [f"{fault_type} blocked by fault injection policy"],
        "errors": [] if detected else [f"{fault_type} was not detected"],
    }


def run_fault_injection(provider: str = "alpaca") -> dict:
    results = [run_fault_case(provider, fault_type) for fault_type in FAULT_TYPES]
    blocked = [result for result in results if result["blocked"] and not result["accepted"]]
    unexpected = [result["fault_type"] for result in results if result["accepted"] or not result["blocked"]]
    return {
        **boundary(),
        "provider": provider,
        "results": results,
        "total_fault_cases": len(results),
        "blocked_fault_cases": len(blocked),
        "unexpectedly_accepted": unexpected,
        "warnings": [warning for result in results for warning in result.get("warnings", [])],
        "errors": [error for result in results for error in result.get("errors", [])],
    }
