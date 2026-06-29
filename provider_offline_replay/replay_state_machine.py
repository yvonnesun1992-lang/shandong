from __future__ import annotations


TERMINAL_STATES = {"AUDIT_WRITTEN", "ERROR_RECOVERED"}


def valid_transition_map() -> dict[str, dict[str, str]]:
    return {
        "INIT": {"INTERNAL_ORDER_CREATED": "ORDER_CREATED"},
        "ORDER_CREATED": {"RISK_CHECK_PASSED": "RISK_CHECKED"},
        "RISK_CHECKED": {"APPROVAL_SIMULATED": "APPROVAL_SIMULATED"},
        "APPROVAL_SIMULATED": {"SUBMISSION_BLOCKED": "SUBMISSION_BLOCKED"},
        "SUBMISSION_BLOCKED": {
            "PROVIDER_ACCEPTED_PLACEHOLDER": "ACCEPTED_PLACEHOLDER",
            "PROVIDER_REJECTED_PLACEHOLDER": "REJECTED_PLACEHOLDER",
            "PROVIDER_TIMEOUT_PLACEHOLDER": "TIMEOUT_PLACEHOLDER",
            "PROVIDER_RATE_LIMIT_PLACEHOLDER": "RATE_LIMIT_PLACEHOLDER",
            "DUPLICATE_ORDER_DETECTED": "DUPLICATE_DETECTED",
        },
        "ACCEPTED_PLACEHOLDER": {
            "PROVIDER_PARTIAL_FILL_PLACEHOLDER": "PARTIAL_FILL_PLACEHOLDER",
            "PROVIDER_FILLED_PLACEHOLDER": "FILLED_PLACEHOLDER",
            "PROVIDER_CANCELED_PLACEHOLDER": "CANCELED_PLACEHOLDER",
        },
        "PARTIAL_FILL_PLACEHOLDER": {"PROVIDER_FILLED_PLACEHOLDER": "FILLED_PLACEHOLDER"},
        "TIMEOUT_PLACEHOLDER": {"RECOVERY_REPLAYED": "RECOVERY_REPLAYED"},
        "RATE_LIMIT_PLACEHOLDER": {"RECOVERY_REPLAYED": "RECOVERY_REPLAYED"},
        "DUPLICATE_DETECTED": {"RECOVERY_REPLAYED": "RECOVERY_REPLAYED"},
        "RECOVERY_REPLAYED": {
            "PROVIDER_ACCEPTED_PLACEHOLDER": "ACCEPTED_PLACEHOLDER",
            "AUDIT_EVENT_WRITTEN": "ERROR_RECOVERED",
        },
        "FILLED_PLACEHOLDER": {"AUDIT_EVENT_WRITTEN": "AUDIT_WRITTEN"},
        "REJECTED_PLACEHOLDER": {"AUDIT_EVENT_WRITTEN": "AUDIT_WRITTEN"},
        "CANCELED_PLACEHOLDER": {"AUDIT_EVENT_WRITTEN": "AUDIT_WRITTEN"},
    }


def transition(current_state: str, event_type: str) -> dict:
    next_state = valid_transition_map().get(current_state, {}).get(event_type)
    accepted = next_state is not None
    return {
        "event_type": event_type,
        "previous_state": current_state,
        "next_state": next_state if accepted else current_state,
        "accepted": accepted,
        "warnings": [],
        "errors": [] if accepted else [f"invalid transition from {current_state} with {event_type}"],
        "sandbox_submission_enabled": False,
        "real_submission_enabled": False,
    }


def is_terminal_state(state: str) -> bool:
    return state in TERMINAL_STATES
