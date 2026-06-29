from __future__ import annotations

from provider_connector_design import boundary


FIELD_MAPPINGS = [
    {"internal": "symbol", "provider": "provider_symbol_placeholder", "notes": "symbol mapping"},
    {"internal": "side", "provider": "provider_side_placeholder", "notes": "side mapping"},
    {"internal": "order_type", "provider": "provider_order_type_placeholder", "notes": "order type mapping"},
    {"internal": "quantity", "provider": "provider_quantity_placeholder", "notes": "quantity mapping"},
    {"internal": "limit_price", "provider": "provider_price_placeholder", "notes": "price mapping"},
    {"internal": "time_in_force", "provider": "provider_tif_placeholder", "notes": "time in force mapping"},
    {"internal": "client_order_ref", "provider": "provider_client_ref_placeholder", "notes": "client order id mapping"},
    {"internal": "account_reference", "provider": "account_reference_placeholder", "notes": "account reference mapping placeholder"},
    {"internal": "position_fields", "provider": "position_field_placeholder", "notes": "position field mapping placeholder"},
    {"internal": "execution_report", "provider": "execution_report_placeholder", "notes": "execution report mapping placeholder"},
]


def build_provider_field_mapping(provider: str) -> dict:
    return {
        "provider": provider,
        "field_mappings": [item.copy() for item in FIELD_MAPPINGS],
        "unsupported_fields": ["advanced order routing", "provider-specific bracket fields"],
        "requires_future_provider_docs": True,
        **boundary(),
    }
