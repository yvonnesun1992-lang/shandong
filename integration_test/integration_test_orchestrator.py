from __future__ import annotations

from integration_test.cross_layer_consistency_validator import validate_cross_layer_consistency
from integration_test.integration_scenario_matrix import SCENARIOS, replay_scenario
from integration_test.integration_safety_gate import validate_integration_safety
from integration_test.sanitizer import integration_boundary


def run_scenario(name: str) -> dict:
    result = replay_scenario(name)
    consistency = validate_cross_layer_consistency(result)
    safety = validate_integration_safety(result)
    status = "PASS" if consistency["valid"] and safety["safe"] else "FAIL"
    return {"scenario": result["scenario"], "status": status, "result": result, "consistency": consistency, "safety": safety, **integration_boundary()}


def run_all_tests() -> dict:
    results = [run_scenario(item) for item in SCENARIOS]
    summary = summarize_results({"results": results})
    return {"results": results, "summary": summary, **integration_boundary()}


def summarize_results(results: dict | list[dict]) -> dict:
    items = results.get("results", []) if isinstance(results, dict) else results
    passed = sum(1 for item in items if item.get("status") == "PASS")
    failed = sum(1 for item in items if item.get("status") == "FAIL")
    warnings = sum(1 for item in items if item.get("result", {}).get("warnings"))
    total = len(items)
    score = passed / total if total else 0.0
    return {"total_scenarios": total, "passed": passed, "failed": failed, "warnings": warnings, "integration_score": score, **integration_boundary()}
