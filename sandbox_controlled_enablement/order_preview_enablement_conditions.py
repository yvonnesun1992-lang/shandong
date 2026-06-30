from __future__ import annotations

from sandbox_controlled_enablement.init import boundary


ORDER_PREVIEW_CONDITIONS = [
    "account read approved",
    "risk check required",
    "manual approval required",
    "order preview only",
    "no order submission",
    "preview payload redacted",
    "idempotency reference generated",
    "audit event written",
]


def build_order_preview_enablement_conditions(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "conditions": [{"name": item, "met": False} for item in ORDER_PREVIEW_CONDITIONS],
        "order_preview_ready": False,
        "order_preview_enabled": False,
        "order_submission_enabled": False,
        "blocking_items": ORDER_PREVIEW_CONDITIONS.copy(),
    }
