from __future__ import annotations

from provider_fault_injection import boundary
from provider_fault_injection.fault_replay_runner import run_fault_scenario


def simulate_kill_switch_trigger(provider: str, scenario: str) -> dict:
    result = run_fault_scenario(provider, scenario)
    return {
        **result,
        "kill_switch_triggered": True,
        "kill_switch_simulated": True,
        "final_state": "KILL_SWITCH_SIMULATED",
        **boundary(),
    }


def validate_kill_switch_effect(result: dict) -> dict:
    errors = []
    if result.get("kill_switch_triggered") is not True:
        errors.append("kill switch was not triggered")
    if result.get("order_submission_enabled") is not False:
        errors.append("order submission must remain disabled")
    if result.get("sandbox_api_enabled") is not False:
        errors.append("sandbox api must remain disabled")
    return {"provider": result.get("provider", "unknown"), "scenario": result.get("scenario", "unknown"), "valid": not errors, "errors": errors, "warnings": [], **boundary()}
