from __future__ import annotations

from provider_fault_injection import boundary
from provider_fault_injection.fault_audit_trail import build_all_fault_audit_trails
from provider_fault_injection.fault_detection_validator import validate_all_fault_detections
from provider_fault_injection.fault_injector import inject_all_faults
from provider_fault_injection.fault_recovery_validator import validate_all_fault_recovery
from provider_fault_injection.fault_replay_runner import run_all_fault_scenarios
from provider_fault_injection.fault_safety_validator import build_fault_safety_summary
from provider_fault_injection.kill_switch_simulation import simulate_kill_switch_trigger, validate_kill_switch_effect


def run_fault_injection_suite(provider: str) -> dict:
    injected = inject_all_faults(provider)
    runner = run_all_fault_scenarios(provider)
    detection = validate_all_fault_detections(provider)
    recovery = validate_all_fault_recovery(provider)
    kill_switch = simulate_kill_switch_trigger(provider, "kill_switch_trigger")
    kill_switch_validation = validate_kill_switch_effect(kill_switch)
    audit = build_all_fault_audit_trails(provider)
    safety = build_fault_safety_summary()
    results = {
        "provider": provider,
        "injected": injected,
        "runner": runner,
        "detection": detection,
        "recovery": recovery,
        "kill_switch": kill_switch,
        "kill_switch_validation": kill_switch_validation,
        "audit": audit,
        "safety": safety,
    }
    return summarize_fault_results(results)


def summarize_fault_results(results: dict) -> dict:
    errors = []
    warnings = []
    runner = results["runner"]
    for key in ["injected", "runner", "detection", "recovery", "kill_switch_validation", "audit", "safety"]:
        item = results[key]
        errors.extend(item.get("errors", []))
        warnings.extend(item.get("warnings", []))
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
