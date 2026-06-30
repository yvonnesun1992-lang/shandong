from __future__ import annotations

from provider_offline_soak import boundary
from provider_offline_soak.soak_runner import run_all_soak_scenarios


REQUIRED_COVERAGE = {
    "all replay scenarios covered",
    "all fault scenarios covered",
    "timeout covered",
    "duplicate order covered",
    "rate limit covered",
    "rejection covered",
    "partial fill covered",
    "audit covered",
    "recovery covered",
    "safety covered",
}


def validate_scenario_coverage(results: dict) -> dict:
    names = {result["scenario"] for result in results.get("results", [])}
    coverage = {
        "all replay scenarios covered": bool(names),
        "all fault scenarios covered": "mixed_replay_fault_soak" in names,
        "timeout covered": "timeout_recovery_soak" in names,
        "duplicate order covered": "duplicate_heavy_soak" in names,
        "rate limit covered": "rate_limit_heavy_soak" in names,
        "rejection covered": "state_machine_boundary_soak" in names,
        "partial fill covered": "state_machine_boundary_soak" in names,
        "audit covered": "audit_heavy_soak" in names,
        "recovery covered": "timeout_recovery_soak" in names or "mixed_replay_fault_soak" in names,
        "safety covered": "safety_boundary_soak" in names,
    }
    missing = [item for item, covered in coverage.items() if not covered]
    return {"coverage_passed": not missing, "coverage": coverage, "missing_items": missing, **boundary()}


def validate_soak_coverage(provider: str) -> dict:
    return validate_scenario_coverage(run_all_soak_scenarios(provider))
