from __future__ import annotations

from provider_connector_design.idempotency_policy import build_idempotency_policy
from provider_mock_contract import boundary

__test__ = False


def test_idempotency_policy(provider: str) -> dict:
    policy = build_idempotency_policy(provider)
    body = policy["idempotency_policy"]
    errors = []
    for key in ["client_order_id_required", "idempotency_key_required", "retry_safe_window", "local_pending_order_registry", "provider_response_replay_handling"]:
        if not body.get(key):
            errors.append(f"missing {key}")
    if policy.get("duplicate_order_protection") is not True:
        errors.append("duplicate protection must be true")
    if policy.get("order_submission_enabled") is not False:
        errors.append("order submission must remain disabled")
    return {"provider": provider, "passed": not errors, "duplicate_order_protection": policy["duplicate_order_protection"], "errors": errors, **boundary()}
