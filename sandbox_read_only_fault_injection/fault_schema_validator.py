from __future__ import annotations

from sandbox_read_only_fault_injection.fault_payload_catalog import FAULT_TYPES, build_fault_payload
from sandbox_read_only_fault_injection.init import boundary


def validate_fault_schema(payload: dict) -> dict:
    findings: list[str] = []
    if payload.get("account_ref") != "ACCOUNT_REF_PLACEHOLDER":
        findings.append("missing account_ref placeholder")
    if "timestamp_placeholder" not in payload:
        findings.append("missing timestamp placeholder")
    if "malformed" in str(payload.get("payload_type", "")):
        findings.append("malformed payload type")
    if payload.get("payload_type") == "unknown_provider_payload":
        findings.append("unknown provider payload")
    if payload.get("raw_payload_stored") is True:
        findings.append("raw_payload_stored true")
    if payload.get("provider_payload_redacted") is False:
        findings.append("provider_payload_redacted false")
    if payload.get("values_redacted") is False:
        findings.append("values_redacted false")
    return {
        **boundary(),
        "provider": payload.get("provider", "alpaca"),
        "fault_type": payload.get("fault_type", "unknown"),
        "schema_faults_detected": bool(findings),
        "findings": findings,
        "warnings": findings,
    }


def validate_all_fault_schemas(provider: str = "alpaca") -> dict:
    results = [validate_fault_schema(build_fault_payload(provider, fault_type)) for fault_type in FAULT_TYPES]
    return {
        **boundary(),
        "provider": provider,
        "schema_faults_detected": any(result["schema_faults_detected"] for result in results),
        "results": results,
        "findings": [finding for result in results for finding in result["findings"]],
    }
