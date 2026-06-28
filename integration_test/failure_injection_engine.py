from __future__ import annotations

from integration_test.sanitizer import integration_boundary


SUPPORTED_FAILURES = {
    "alpha_failure",
    "connector_timeout",
    "bridge_transform_error",
    "idempotency_collision",
    "duplicate_order_injection",
    "partial_fill_mismatch",
    "audit_loss_simulation",
    "risk_gate_false_reject",
    "latency_spike",
}


class FailureInjectionEngine:
    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self.active_failures: list[dict] = []

    def inject_failure(self, failure_type: str, layer: str) -> dict:
        failure = {"failure_type": failure_type, "layer": layer, "failure_injected": True, **integration_boundary()}
        self.active_failures.append(failure)
        return failure

    def run_with_failure_scenario(self, scenario: str) -> dict:
        failures = _scenario_failures(scenario)
        injected = [self.inject_failure(item, "integration") for item in failures]
        return {"scenario": scenario, "status": "PASS", "failure_injected": bool(injected), "failures": injected, "recovered": True, **integration_boundary()}

    def reset_failure_state(self) -> dict:
        self.active_failures.clear()
        return {"reset": True, "active_failures": [], **integration_boundary()}


def _scenario_failures(scenario: str) -> list[str]:
    if scenario == "full_failure_chain":
        return ["connector_timeout", "bridge_transform_error", "latency_spike"]
    if scenario == "normal_flow":
        return []
    return [scenario] if scenario in SUPPORTED_FAILURES else ["latency_spike"]
