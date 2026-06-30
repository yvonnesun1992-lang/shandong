from __future__ import annotations

from sandbox_read_only_fault_injection.init import boundary


def simulate_audit_write_failure(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "fault_type": "audit_write_failure",
        "audit_write_success": False,
        "audit_fallback_written": True,
        "raw_payload_logged": False,
        "values_logged": False,
        "order_submitted": False,
        "warning": "audit write failure escalated to fallback",
    }


def validate_audit_failure_handling(payload: dict) -> dict:
    findings = []
    if payload.get("audit_write_success") is False:
        findings.append("audit_write_success false")
    if payload.get("audit_fallback_written") is not True:
        findings.append("audit fallback missing")
    if payload.get("raw_payload_logged") is not False:
        findings.append("raw payload logged")
    if payload.get("values_logged") is not False:
        findings.append("values logged")
    if payload.get("order_submitted") is not False:
        findings.append("order submitted during audit fault")
    return {
        **boundary(),
        "provider": payload.get("provider", "alpaca"),
        "audit_failure_detected": bool(findings),
        "findings": findings,
        "warnings": findings,
    }
