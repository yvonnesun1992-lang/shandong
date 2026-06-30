from __future__ import annotations

from provider_offline_soak import boundary
from provider_offline_soak.stability_metrics import compute_all_stability_metrics


def evaluate_stability_gate(metrics: dict) -> dict:
    blocking_items = []
    warnings = []
    if metrics.get("safety_violation_count", 0) != 0:
        blocking_items.append("safety violations must be zero")
    if metrics.get("sandbox_api_enabled", False) is True:
        blocking_items.append("sandbox api must remain disabled")
    if metrics.get("order_submission_enabled", False) is True:
        blocking_items.append("order submission must remain disabled")
    if metrics.get("audit_coverage_rate", 0) < 0.95:
        blocking_items.append("audit coverage below threshold")
    if metrics.get("invalid_transition_rate", 1) != 0:
        blocking_items.append("invalid transition rate must be zero")
    if metrics.get("error_rate", 1) > 0.05:
        blocking_items.append("error rate above threshold")
    if metrics.get("stability_score", 0) < 0.80:
        blocking_items.append("stability score below threshold")
    if metrics.get("warning_rate", 0) > 0:
        warnings.append("offline warnings observed within budget")
    gate = "FAIL" if blocking_items else ("WARNING" if warnings else "PASS")
    return {"passed": not blocking_items, "gate": gate, "blocking_items": blocking_items, "warnings": warnings, **boundary()}


def evaluate_all_stability_gates(provider: str) -> dict:
    all_metrics = compute_all_stability_metrics(provider)
    gates = [evaluate_stability_gate(metrics) for metrics in all_metrics["metrics"]]
    failed = sum(1 for gate in gates if not gate["passed"])
    return {"provider": provider, "total_scenarios": len(gates), "failed": failed, "gates": gates, **boundary()}
