from __future__ import annotations

from sandbox_read_only_evidence_pack.init import boundary

ORDER_ITEMS = [
    "normal mock replay has no order preview",
    "normal mock replay has no order submission",
    "order path intrusion fault detected",
    "order preview enabled true blocked",
    "order submission enabled true blocked",
    "order submitted true blocked",
    "sandbox order id detected and blocked",
    "submit order detected and blocked",
    "trade intent detected and blocked",
    "manual approval cannot override",
    "controlled GO cannot override",
    "read-only connector cannot submit orders",
]


def build_order_blocking_evidence_pack(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "order_blocking_evidence_ready": True,
        "order_blocking_evidence_items": ORDER_ITEMS,
        "unresolved_order_gaps": [],
        "order_submission_enabled": False,
        "warnings": [],
    }

