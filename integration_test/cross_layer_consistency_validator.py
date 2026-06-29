from __future__ import annotations

from integration_test.sanitizer import integration_boundary, sanitize_integration_payload


def validate_cross_layer_consistency(payload: dict) -> dict:
    clean = sanitize_integration_payload(payload)
    errors = []
    warnings = []
    mismatches = []
    if clean.get("broker_connected") is not False:
        errors.append("broker connection must be false")
    if clean.get("real_orders_enabled") is not False:
        errors.append("real orders must be false")
    if int(clean.get("audit_events", 0) or 0) < 1:
        warnings.append("audit trail is sparse")
    return {"valid": not errors, "errors": errors, "warnings": warnings, "layer_mismatch": mismatches, **integration_boundary()}
