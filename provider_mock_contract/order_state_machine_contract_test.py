from __future__ import annotations

from provider_connector_design.order_state_machine_design import STATES, build_order_state_machine_design
from provider_mock_contract import boundary

__test__ = False


def test_order_state_machine(provider: str) -> dict:
    design = build_order_state_machine_design(provider)
    states = set(design["states"])
    errors = [state for state in STATES if state not in states]
    if design.get("sandbox_submission_enabled") is not False:
        errors.append("sandbox submission must remain disabled")
    if design.get("real_submission_enabled") is not False:
        errors.append("real submission must remain disabled")
    if not design.get("blocked_transitions"):
        errors.append("blocked transitions missing")
    if not design.get("manual_approval_required_transitions"):
        errors.append("manual approval transitions missing")
    if not design.get("kill_switch_blocked_transitions"):
        errors.append("kill switch transitions missing")
    return {
        "provider": provider,
        "passed": not errors,
        "states_tested": STATES.copy(),
        "blocked_transitions_tested": bool(design.get("blocked_transitions")),
        "sandbox_submission_enabled": False,
        "real_submission_enabled": False,
        "errors": errors,
        **boundary(),
    }
