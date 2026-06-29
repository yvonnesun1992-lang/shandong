from __future__ import annotations

from provider_offline_replay import boundary
from provider_offline_replay.replay_event_loader import load_replay_scenario


RECOVERY_SCENARIOS = [
    "timeout_then_recovery",
    "rate_limit_then_backoff",
    "duplicate_order_replay",
    "state_machine_error_recovery",
]


def validate_failure_recovery(provider: str) -> dict:
    errors = []
    checked = []
    for scenario in RECOVERY_SCENARIOS:
        loaded = load_replay_scenario(provider, scenario)
        event_types = [event["event_type"] for event in loaded["events"]]
        checked.append(scenario)
        if "RECOVERY_REPLAYED" not in event_types:
            errors.append(f"{scenario} missing recovery event")
        if "AUDIT_EVENT_WRITTEN" not in event_types:
            errors.append(f"{scenario} missing audit event")
        if scenario == "duplicate_order_replay" and "DUPLICATE_ORDER_DETECTED" not in event_types:
            errors.append("duplicate_order_replay missing duplicate detection")
        if scenario == "rate_limit_then_backoff" and not any(event.get("recovery_action_placeholder") == "BACKOFF_PLACEHOLDER" for event in loaded["events"]):
            errors.append("rate_limit_then_backoff missing backoff placeholder")

    return {
        "provider": provider,
        "valid": not errors,
        "recovery_scenarios_checked": checked,
        "errors": errors,
        "warnings": [],
        "external_retry_call_enabled": False,
        **boundary(),
    }
