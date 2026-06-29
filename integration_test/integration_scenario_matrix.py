from __future__ import annotations

from integration_test.sanitizer import integration_boundary


SCENARIOS = [
    "normal_flow",
    "high_latency_flow",
    "connector_reject_flow",
    "bridge_transform_failure",
    "skeleton_adapter_missing_method",
    "mock_connector_duplicate_order",
    "risk_gate_block_flow",
    "manual_approval_block_flow",
    "full_failure_chain",
    "recovery_flow",
]


def build_integration_scenario_matrix(seed: int = 42) -> dict:
    return {"version": "V5.17", "seed": seed, "scenarios": [{"name": item, "deterministic": True} for item in SCENARIOS], **integration_boundary()}


def replay_scenario(name: str, seed: int = 42) -> dict:
    scenario = name if name in SCENARIOS else "normal_flow"
    status = "WARNING" if scenario in {"full_failure_chain", "bridge_transform_failure"} else "PASS"
    return {
        "scenario": scenario,
        "seed": seed,
        "status": status,
        "order_id": f"integration-{scenario}",
        "mock_status": "MOCK_FILLED" if scenario == "normal_flow" else "MOCK_REJECTED",
        "bridge_status": "bridge_simulated_route",
        "skeleton_status": "skeleton_only_rejected",
        "risk_decision": "blocked" if scenario == "risk_gate_block_flow" else "allowed",
        "audit_events": 4,
        "warnings": [] if status == "PASS" else ["simulated failure path"],
        **integration_boundary(),
    }
