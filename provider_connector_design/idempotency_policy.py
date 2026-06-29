from __future__ import annotations

from provider_connector_design import boundary


def build_idempotency_policy(provider: str) -> dict:
    return {
        "provider": provider,
        "idempotency_policy": {
            "client_order_id_required": True,
            "idempotency_key_required": True,
            "duplicate_submission_detection": "local_registry_placeholder",
            "retry_safe_window": "future_provider_window_placeholder",
            "order_status_reconciliation": "future_reconciliation_placeholder",
            "local_pending_order_registry": "required_before_runtime",
            "provider_response_replay_handling": "redacted_replay_placeholder",
            "failure_recovery": "manual_review_before_retry",
        },
        "duplicate_order_protection": True,
        **boundary(),
    }
