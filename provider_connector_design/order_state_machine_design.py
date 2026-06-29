from __future__ import annotations

from provider_connector_design import boundary


STATES = [
    "CREATED",
    "RISK_CHECKED",
    "APPROVAL_PENDING",
    "APPROVED_SIMULATED",
    "SUBMISSION_BLOCKED",
    "SUBMITTED_PLACEHOLDER",
    "ACCEPTED_PLACEHOLDER",
    "PARTIALLY_FILLED_PLACEHOLDER",
    "FILLED_PLACEHOLDER",
    "CANCELED_PLACEHOLDER",
    "REJECTED_PLACEHOLDER",
    "ERROR_PLACEHOLDER",
]


def build_order_state_machine_design(provider: str) -> dict:
    return {
        "provider": provider,
        "states": STATES.copy(),
        "transitions": [
            ["CREATED", "RISK_CHECKED"],
            ["RISK_CHECKED", "APPROVAL_PENDING"],
            ["APPROVAL_PENDING", "APPROVED_SIMULATED"],
            ["APPROVED_SIMULATED", "SUBMISSION_BLOCKED"],
        ],
        "blocked_transitions": [
            ["SUBMISSION_BLOCKED", "SUBMITTED_PLACEHOLDER"],
            ["SUBMITTED_PLACEHOLDER", "ACCEPTED_PLACEHOLDER"],
            ["ACCEPTED_PLACEHOLDER", "FILLED_PLACEHOLDER"],
        ],
        "manual_approval_required_transitions": [["RISK_CHECKED", "APPROVAL_PENDING"]],
        "kill_switch_blocked_transitions": [["APPROVED_SIMULATED", "SUBMITTED_PLACEHOLDER"]],
        "rollback_transitions": [["APPROVED_SIMULATED", "CANCELED_PLACEHOLDER"], ["ERROR_PLACEHOLDER", "SUBMISSION_BLOCKED"]],
        "sandbox_submission_enabled": False,
        "real_submission_enabled": False,
        **boundary(),
    }
