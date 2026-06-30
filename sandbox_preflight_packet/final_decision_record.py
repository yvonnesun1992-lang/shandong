from __future__ import annotations

from sandbox_preflight_packet.init import boundary


def build_final_preflight_decision(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "decision": "NO_GO",
        "sandbox_dry_run_allowed": False,
        "decision_reason": [
            "final preflight packet is packet-only in V5.31",
            "review board decision remains NO_GO",
            "sandbox API remains disabled",
            "secret read remains disabled",
            "account read remains disabled",
            "order submission remains disabled",
        ],
    }


def evaluate_final_preflight_decision(context: dict | None = None) -> dict:
    context = context or {}
    result = build_final_preflight_decision(context.get("provider", "alpaca"))
    result["warnings"] = ["simulated packet approval requested but final decision remains NO_GO"] if context.get("simulated_packet_approval") or context.get("packet_approval") else []
    return result
