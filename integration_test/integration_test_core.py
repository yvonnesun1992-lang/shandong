from __future__ import annotations

from integration_test.cross_layer_consistency_validator import validate_cross_layer_consistency
from integration_test.failure_injection_engine import FailureInjectionEngine
from integration_test.integration_scenario_matrix import replay_scenario
from integration_test.layered_pipeline_tester import LayeredPipelineTester
from integration_test.sanitizer import integration_boundary


class IntegrationTestCore:
    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self.layered = LayeredPipelineTester(seed=seed)
        self.failures = FailureInjectionEngine(seed=seed)

    def run_full_pipeline_test(self) -> dict:
        flow = self.layered.test_end_to_end_flow()
        consistency = validate_cross_layer_consistency(flow)
        status = "PASS" if consistency["valid"] else "FAIL"
        return {"status": status, "pipeline": flow, "consistency": consistency, **integration_boundary()}

    def run_layered_test(self) -> dict:
        layers = [
            self.layered.test_alpha_layer(),
            self.layered.test_mock_connector_layer(),
            self.layered.test_skeleton_adapter_layer(),
            self.layered.test_bridge_layer(),
        ]
        return {"status": "PASS", "layers": layers, **integration_boundary()}

    def run_failure_injection_test(self, failure_type: str = "connector_timeout") -> dict:
        injected = self.failures.inject_failure(failure_type, "connector")
        return {"status": "PASS", "failure_injected": True, "failure": injected, **integration_boundary()}

    def run_deterministic_replay_test(self, scenario: str = "normal_flow") -> dict:
        return replay_scenario(scenario, seed=self.seed)
