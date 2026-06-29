from __future__ import annotations

from provider_offline_replay import boundary
from provider_offline_replay.replay_runner import run_all_replay_scenarios, run_replay_scenario
from provider_offline_replay.replay_safety_validator import validate_replay_safety


def validate_replay_consistency(replay_result: dict) -> dict:
    errors = list(replay_result.get("errors", []))
    steps = replay_result.get("steps", [])
    if not steps:
        errors.append("replay result has no steps")
    if any(not step.get("accepted") for step in steps):
        errors.append("replay result contains rejected state transition")
    if not replay_result.get("terminal"):
        errors.append("replay result did not reach terminal state")
    if "AUDIT_EVENT_WRITTEN" not in [step.get("event_type") for step in steps]:
        errors.append("audit event was not written")
    if replay_result.get("scenario") == "duplicate_order_replay" and "DUPLICATE_ORDER_DETECTED" not in [step.get("event_type") for step in steps]:
        errors.append("duplicate order protection was not replayed")
    safety = validate_replay_safety(replay_result)
    errors.extend(safety.get("errors", []))
    return {
        "provider": replay_result.get("provider", "unknown"),
        "scenario": replay_result.get("scenario", "unknown"),
        "valid": not errors,
        "errors": errors,
        "warnings": replay_result.get("warnings", []),
        "validated_scenarios": 1,
        **boundary(),
    }


def validate_all_replay_consistency(provider: str) -> dict:
    all_results = run_all_replay_scenarios(provider)
    validations = [validate_replay_consistency(result) for result in all_results["results"]]
    errors = [error for validation in validations for error in validation.get("errors", [])]
    warnings = [warning for validation in validations for warning in validation.get("warnings", [])]
    return {
        "provider": provider,
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "validated_scenarios": len(validations),
        "validations": validations,
        **boundary(),
    }
