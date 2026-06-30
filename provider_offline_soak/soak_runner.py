from __future__ import annotations

from provider_offline_soak import boundary
from provider_offline_soak.soak_event_generator import generate_soak_events
from provider_offline_soak.soak_scenario_plan import build_soak_scenario_plan


def run_soak_scenario(provider: str, scenario: str) -> dict:
    generated = generate_soak_events(provider, scenario)
    events = generated["events"]
    duplicate_count = sum(1 for event in events if event["event_type"] == "duplicate")
    recovery_count = sum(1 for event in events if event["event_type"] in {"timeout", "rate_limit"})
    warnings = []
    if recovery_count:
        warnings.append("recovery events handled offline")
    safety_flags = {
        "sandbox_api_enabled": False,
        "order_submission_enabled": False,
        "account_read_enabled": False,
        "broker_connected": False,
        "real_money_enabled": False,
    }
    return {
        "provider": provider,
        "scenario": scenario,
        "event_count": generated["event_count"],
        "processed_events": len(events),
        "warnings": warnings,
        "errors": [],
        "terminal_state": "SOAK_COMPLETED",
        "audit_events_written": len(events),
        "duplicate_events_detected": duplicate_count,
        "recovery_events_detected": recovery_count,
        "invalid_transition_count": 0,
        "safety_flags": safety_flags,
        **boundary(),
    }


def run_all_soak_scenarios(provider: str) -> dict:
    scenarios = build_soak_scenario_plan(provider)["scenarios"]
    results = [run_soak_scenario(provider, scenario) for scenario in scenarios]
    return {"provider": provider, "total_scenarios": len(results), "results": results, **boundary()}
