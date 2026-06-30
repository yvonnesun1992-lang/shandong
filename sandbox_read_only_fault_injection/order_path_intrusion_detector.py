from __future__ import annotations

import json

from sandbox_read_only_fault_injection.fault_payload_catalog import FAULT_TYPES, build_fault_payload
from sandbox_read_only_fault_injection.init import boundary

ORDER_FIELDS = ["order_preview_enabled", "order_submission_enabled", "order_submitted"]
ORDER_TERMS = ["order_id", "real_order_id", "sandbox_order_id", "submit_order", "cancel_order", "replace_order", "trade_intent", "execution_intent"]


def detect_order_path_intrusion(payload: dict | list | str) -> dict:
    findings: list[str] = []
    if isinstance(payload, dict):
        for field in ORDER_FIELDS:
            if payload.get(field) is True:
                findings.append(f"{field} true")
        for term in ORDER_TERMS:
            if term in payload:
                findings.append(f"{term} present")
    text = json.dumps(payload, default=str).lower() if not isinstance(payload, str) else payload.lower()
    for term in ORDER_TERMS:
        if term in text:
            findings.append(f"{term} text detected")
    return {
        **boundary(),
        "order_intrusion_detected": bool(findings),
        "manual_approval_can_override": False,
        "controlled_go_can_override": False,
        "findings": sorted(set(findings)),
        "warnings": sorted(set(findings)),
    }


def detect_all_order_path_intrusions(provider: str = "alpaca") -> dict:
    results = [detect_order_path_intrusion(build_fault_payload(provider, fault_type)) for fault_type in FAULT_TYPES]
    return {
        **boundary(),
        "provider": provider,
        "order_intrusion_detected": any(result["order_intrusion_detected"] for result in results),
        "results": results,
        "findings": [finding for result in results for finding in result["findings"]],
    }
