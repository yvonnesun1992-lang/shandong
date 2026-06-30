from __future__ import annotations

from provider_offline_soak import boundary
from provider_offline_soak.soak_coverage_validator import validate_soak_coverage
from provider_offline_soak.soak_runner import run_all_soak_scenarios
from provider_offline_soak.soak_safety_validator import build_soak_safety_summary
from provider_offline_soak.stability_gate import evaluate_all_stability_gates
from provider_offline_soak.stability_metrics import compute_all_stability_metrics


def run_offline_soak(provider: str) -> dict:
    runner = run_all_soak_scenarios(provider)
    metrics = compute_all_stability_metrics(provider)
    gates = evaluate_all_stability_gates(provider)
    coverage = validate_soak_coverage(provider)
    safety = build_soak_safety_summary()
    return {"provider": provider, "runner": runner, "metrics": metrics, "gates": gates, "coverage": coverage, "safety": safety, **boundary()}


def summarize_offline_soak_results(results: dict) -> dict:
    total = results["runner"]["total_scenarios"]
    failed = results["gates"]["failed"]
    warnings = []
    errors = []
    if not results["coverage"]["coverage_passed"]:
        errors.extend(results["coverage"]["missing_items"])
    if not results["safety"]["safe"]:
        errors.extend(results["safety"]["errors"])
    if results["metrics"]["average_stability_score"] < 0.95:
        warnings.append("offline soak stability score has warning budget usage")
    verdict = "FAIL" if failed or errors else ("WARNING" if warnings else "PASS")
    return {
        "provider": results["provider"],
        "total_scenarios": total,
        "passed": total - failed,
        "failed": failed,
        "warnings": warnings,
        "errors": errors,
        "stability_score": results["metrics"]["average_stability_score"],
        "verdict": verdict,
        **boundary(),
    }
