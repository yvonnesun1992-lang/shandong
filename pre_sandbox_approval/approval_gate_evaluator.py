from __future__ import annotations

from pre_sandbox_approval.init import boundary


def evaluate_pre_sandbox_approval_gate(context: dict | None = None) -> dict:
    context = context or {}
    warnings: list[str] = []
    if context.get("simulated_operator_approval") or context.get("operator_approval_granted"):
        warnings.append("simulated approval requested but blocked in V5.28")
    return {
        **boundary(),
        "provider": context.get("provider", "alpaca"),
        "approval_gate": "BLOCKED",
        "decision": "BLOCKED",
        "simulated_approval_requested": bool(context.get("simulated_operator_approval") or context.get("operator_approval_granted")),
        "warnings": warnings,
    }


def build_approval_gate_summary(provider: str = "alpaca") -> dict:
    return evaluate_pre_sandbox_approval_gate({"provider": provider})
