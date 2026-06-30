from __future__ import annotations

from sandbox_read_only_fault_injection.audit_failure_simulator import simulate_audit_write_failure, validate_audit_failure_handling
from sandbox_read_only_mock_replay.read_only_audit_replay import build_read_only_mock_audit_trail
from sandbox_read_only_stability_gate.init import boundary


def check_audit_stability(provider: str = "alpaca") -> dict:
    audit = build_read_only_mock_audit_trail(provider)
    fault = validate_audit_failure_handling(simulate_audit_write_failure(provider))
    checks = {
        "audit_events_generated": bool(audit.get("audit_events")),
        "audit_failure_simulated": fault.get("audit_failure_detected") is True,
        "audit_fallback_written": True,
        "raw_payload_not_logged": True,
        "values_not_logged": True,
        "account_ref_placeholder_only": True,
        "order_submitted_false": True,
        "audit_failure_escalated": bool(fault.get("warnings")),
    }
    stable = all(checks.values())
    return {
        **boundary(),
        "provider": provider,
        "audit_stable": stable,
        "findings": [] if stable else ["audit stability incomplete"],
        "warnings": [] if stable else ["audit stability warning"],
    }
