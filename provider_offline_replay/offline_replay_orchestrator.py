from __future__ import annotations

from provider_offline_replay import boundary
from provider_offline_replay.replay_audit_trail import build_all_replay_audit_trails
from provider_offline_replay.replay_consistency_validator import validate_all_replay_consistency
from provider_offline_replay.replay_event_loader import load_all_replay_scenarios
from provider_offline_replay.replay_failure_recovery_validator import validate_failure_recovery
from provider_offline_replay.replay_runner import run_all_replay_scenarios
from provider_offline_replay.replay_safety_validator import build_replay_safety_summary


def run_offline_replay(provider: str) -> dict:
    loaded = load_all_replay_scenarios(provider)
    runner = run_all_replay_scenarios(provider)
    consistency = validate_all_replay_consistency(provider)
    recovery = validate_failure_recovery(provider)
    audit = build_all_replay_audit_trails(provider)
    safety = build_replay_safety_summary()
    results = {
        "provider": provider,
        "loaded": loaded,
        "runner": runner,
        "consistency": consistency,
        "recovery": recovery,
        "audit": audit,
        "safety": safety,
    }
    return summarize_offline_replay_results(results)


def summarize_offline_replay_results(results: dict) -> dict:
    errors = []
    warnings = []
    runner = results["runner"]
    for key in ["consistency", "recovery", "audit", "safety"]:
        item = results[key]
        errors.extend(item.get("errors", []))
        warnings.extend(item.get("warnings", []))
    errors.extend(runner.get("errors", []))
    warnings.extend(runner.get("warnings", []))
    failed = runner.get("failed", 0) + (1 if errors else 0)
    verdict = "FAIL" if failed else "WARNING"
    if not errors and not warnings:
        verdict = "PASS"
    return {
        "provider": results["provider"],
        "total_scenarios": runner["total_scenarios"],
        "passed": runner["passed"],
        "failed": failed,
        "warnings": warnings,
        "errors": errors,
        "verdict": verdict,
        "details": results,
        **boundary(),
    }
