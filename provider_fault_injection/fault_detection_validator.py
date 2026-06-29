from __future__ import annotations

from provider_fault_injection import boundary
from provider_fault_injection.fault_replay_runner import run_all_fault_scenarios


REQUIRED_DETECTIONS = {
    "connector_timeout",
    "duplicate_order",
    "stale_response",
    "out_of_order_event",
    "partial_fill_mismatch",
    "rate_limit_storm",
    "audit_loss",
    "state_machine_corruption",
    "idempotency_collision",
}


def validate_fault_detection(result: dict) -> dict:
    errors = [] if result.get("detected") else [f"{result.get('scenario')} detection failed"]
    return {"provider": result.get("provider", "unknown"), "scenario": result.get("scenario", "unknown"), "valid": not errors, "errors": errors, "warnings": [], **boundary()}


def validate_all_fault_detections(provider: str) -> dict:
    all_results = run_all_fault_scenarios(provider)
    validations = [validate_fault_detection(result) for result in all_results["results"]]
    detected_faults = [result["scenario"] for result in all_results["results"] if result["detected"]]
    errors = [error for validation in validations for error in validation.get("errors", [])]
    missing = sorted(REQUIRED_DETECTIONS - set(detected_faults))
    errors.extend([f"{scenario} detection missing" for scenario in missing])
    return {
        "provider": provider,
        "valid": not errors,
        "detected_faults": detected_faults,
        "errors": errors,
        "warnings": [],
        "validations": validations,
        **boundary(),
    }
