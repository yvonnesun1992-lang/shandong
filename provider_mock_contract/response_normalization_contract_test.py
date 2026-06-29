from __future__ import annotations

from provider_connector_design.order_response_mapping import build_order_response_mapping
from provider_mock_contract import boundary
from provider_mock_contract.mock_provider_payloads import build_mock_payload

__test__ = False


ORDER_PAYLOAD_TYPES = ["accepted_order_response", "partial_fill_response", "filled_order_response", "rejected_order_response", "canceled_order_response"]


def test_response_normalization(provider: str) -> dict:
    design = build_order_response_mapping(provider)
    errors = []
    statuses = []
    if design.get("raw_response_policy") != "redacted_only":
        errors.append("raw response policy must be redacted_only")
    for payload_type in ORDER_PAYLOAD_TYPES:
        payload = build_mock_payload(provider, payload_type)
        status = payload.get("status")
        statuses.append(status)
        if payload.get("provider_order_ref") != "PROVIDER_ORDER_REF_PLACEHOLDER":
            errors.append(f"{payload_type} provider ref is not placeholder")
        if not status:
            errors.append(f"{payload_type} missing status")
        if payload_type == "rejected_order_response" and not payload.get("rejection_reason"):
            errors.append("rejected response missing rejection reason")
    return {"provider": provider, "passed": not errors, "tested_statuses": statuses, "errors": errors, **boundary()}
