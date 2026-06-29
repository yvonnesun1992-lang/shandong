from __future__ import annotations

from provider_offline_replay import boundary


SCENARIO_EVENTS = {
    "normal_order_lifecycle": [
        "INTERNAL_ORDER_CREATED",
        "RISK_CHECK_PASSED",
        "APPROVAL_SIMULATED",
        "SUBMISSION_BLOCKED",
        "PROVIDER_ACCEPTED_PLACEHOLDER",
        "PROVIDER_FILLED_PLACEHOLDER",
        "AUDIT_EVENT_WRITTEN",
    ],
    "partial_fill_lifecycle": [
        "INTERNAL_ORDER_CREATED",
        "RISK_CHECK_PASSED",
        "APPROVAL_SIMULATED",
        "SUBMISSION_BLOCKED",
        "PROVIDER_ACCEPTED_PLACEHOLDER",
        "PROVIDER_PARTIAL_FILL_PLACEHOLDER",
        "PROVIDER_FILLED_PLACEHOLDER",
        "AUDIT_EVENT_WRITTEN",
    ],
    "rejected_order_lifecycle": [
        "INTERNAL_ORDER_CREATED",
        "RISK_CHECK_PASSED",
        "APPROVAL_SIMULATED",
        "SUBMISSION_BLOCKED",
        "PROVIDER_REJECTED_PLACEHOLDER",
        "AUDIT_EVENT_WRITTEN",
    ],
    "canceled_order_lifecycle": [
        "INTERNAL_ORDER_CREATED",
        "RISK_CHECK_PASSED",
        "APPROVAL_SIMULATED",
        "SUBMISSION_BLOCKED",
        "PROVIDER_ACCEPTED_PLACEHOLDER",
        "PROVIDER_CANCELED_PLACEHOLDER",
        "AUDIT_EVENT_WRITTEN",
    ],
    "timeout_then_recovery": [
        "INTERNAL_ORDER_CREATED",
        "RISK_CHECK_PASSED",
        "APPROVAL_SIMULATED",
        "SUBMISSION_BLOCKED",
        "PROVIDER_TIMEOUT_PLACEHOLDER",
        "RECOVERY_REPLAYED",
        "PROVIDER_ACCEPTED_PLACEHOLDER",
        "PROVIDER_FILLED_PLACEHOLDER",
        "AUDIT_EVENT_WRITTEN",
    ],
    "duplicate_order_replay": [
        "INTERNAL_ORDER_CREATED",
        "RISK_CHECK_PASSED",
        "APPROVAL_SIMULATED",
        "SUBMISSION_BLOCKED",
        "DUPLICATE_ORDER_DETECTED",
        "RECOVERY_REPLAYED",
        "AUDIT_EVENT_WRITTEN",
    ],
    "rate_limit_then_backoff": [
        "INTERNAL_ORDER_CREATED",
        "RISK_CHECK_PASSED",
        "APPROVAL_SIMULATED",
        "SUBMISSION_BLOCKED",
        "PROVIDER_RATE_LIMIT_PLACEHOLDER",
        "RECOVERY_REPLAYED",
        "PROVIDER_ACCEPTED_PLACEHOLDER",
        "PROVIDER_FILLED_PLACEHOLDER",
        "AUDIT_EVENT_WRITTEN",
    ],
    "market_closed_rejection": [
        "INTERNAL_ORDER_CREATED",
        "RISK_CHECK_PASSED",
        "APPROVAL_SIMULATED",
        "SUBMISSION_BLOCKED",
        "PROVIDER_REJECTED_PLACEHOLDER",
        "AUDIT_EVENT_WRITTEN",
    ],
    "insufficient_funds_rejection": [
        "INTERNAL_ORDER_CREATED",
        "RISK_CHECK_PASSED",
        "APPROVAL_SIMULATED",
        "SUBMISSION_BLOCKED",
        "PROVIDER_REJECTED_PLACEHOLDER",
        "AUDIT_EVENT_WRITTEN",
    ],
    "state_machine_error_recovery": [
        "INTERNAL_ORDER_CREATED",
        "RISK_CHECK_PASSED",
        "APPROVAL_SIMULATED",
        "SUBMISSION_BLOCKED",
        "PROVIDER_TIMEOUT_PLACEHOLDER",
        "RECOVERY_REPLAYED",
        "AUDIT_EVENT_WRITTEN",
    ],
}


def build_replay_event_catalog(provider: str) -> dict:
    return {
        "provider": provider,
        "scenarios": {
            scenario: _build_events(provider, scenario, event_types)
            for scenario, event_types in SCENARIO_EVENTS.items()
        },
        **boundary(),
    }


def _build_events(provider: str, scenario: str, event_types: list[str]) -> list[dict]:
    return [
        {
            "provider": provider,
            "scenario": scenario,
            "event_index": index,
            "event_type": event_type,
            "event_id_placeholder": f"REPLAY_EVENT_ID_PLACEHOLDER_{index:03d}",
            "internal_order_ref_placeholder": "INTERNAL_ORDER_REF_PLACEHOLDER",
            "client_order_ref_placeholder": "CLIENT_ORDER_REF_PLACEHOLDER",
            "provider_order_ref_placeholder": "PROVIDER_ORDER_REF_PLACEHOLDER",
            "account_ref_placeholder": "ACCOUNT_REF_PLACEHOLDER",
            "provider_endpoint_placeholder": "DISABLED_PROVIDER_ENDPOINT_PLACEHOLDER",
            "raw_payload_stored": False,
            "provider_payload_redacted": True,
            "offline_replay_only": True,
            "recovery_action_placeholder": "BACKOFF_PLACEHOLDER" if event_type == "PROVIDER_RATE_LIMIT_PLACEHOLDER" else "NONE_PLACEHOLDER",
        }
        for index, event_type in enumerate(event_types)
    ]
