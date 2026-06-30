from __future__ import annotations

from provider_fault_injection import boundary
from provider_fault_injection.fault_replay_runner import run_all_fault_scenarios


ROLLBACK_SCENARIOS = {"state_machine_corruption", "recovery_rollback"}
KILL_SWITCH_SCENARIOS = {"kill_switch_trigger"}


def validate_fault_recovery(result: dict) -> dict:
    errors = []
    event_types = [event["event_type"] for event in result.get("events", [])]
    if not result.get("recovered"):
        errors.append(f"{result.get('scenario')} recovery failed")
    if result.get("scenario") in ROLLBACK_SCENARIOS and "ROLLBACK_REPLAYED" not in event_types:
        errors.append(f"{result.get('scenario')} missing rollback event")
    if result.get("scenario") in KILL_SWITCH_SCENARIOS and "KILL_SWITCH_TRIGGERED" not in event_types:
        errors.append("kill_switch_trigger missing kill switch event")
    if not result.get("audit_written"):
        errors.append(f"{result.get('scenario')} missing audit event")
    if result.get("final_state") not in {"SAFE_RECOVERED", "KILL_SWITCH_SIMULATED"}:
        errors.append(f"{result.get('scenario')} final state is not safe")
    if result.get("order_submission_enabled") is not False:
        errors.append("order submission must remain disabled")
    if result.get("sandbox_api_enabled") is not False:
        errors.append("sandbox api must remain disabled")
    return {"provider": result.get("provider", "unknown"), "scenario": result.get("scenario", "unknown"), "valid": not errors, "errors": errors, "warnings": [], **boundary()}


def validate_all_fault_recovery(provider: str) -> dict:
    all_results = run_all_fault_scenarios(provider)
    validations = [validate_fault_recovery(result) for result in all_results["results"]]
    errors = [error for validation in validations for error in validation.get("errors", [])]
    return {"provider": provider, "valid": not errors, "errors": errors, "warnings": [], "validations": validations, **boundary()}
