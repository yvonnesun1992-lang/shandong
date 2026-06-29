from __future__ import annotations

from provider_connector_design.order_request_mapping import REQUIRED_INTERNAL_FIELDS, build_order_request_mapping
from provider_mock_contract import boundary

__test__ = False


def build_mock_internal_order() -> dict:
    order = {field: f"{field.upper()}_PLACEHOLDER" for field in REQUIRED_INTERNAL_FIELDS}
    return {**order, **boundary()}


def test_order_request_mapping(provider: str) -> dict:
    order = build_mock_internal_order()
    design = build_order_request_mapping(provider)
    errors = [field for field in ["internal_order_id", "client_order_id", "symbol", "side", "order_type", "quantity", "risk_check_id", "approval_id", "idempotency_key"] if not order.get(field)]
    if design.get("order_submission_enabled") is not False:
        errors.append("order submission must remain disabled")
    if any("endpoint" in item and "disabled" not in item for item in design.get("provider_fields_placeholder", [])):
        errors.append("provider endpoint must remain disabled placeholder")
    return {"provider": provider, "passed": not errors, "errors": errors, "request_mapping_tested": True, **boundary()}
