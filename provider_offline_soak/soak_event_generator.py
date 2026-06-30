from __future__ import annotations

import random

from provider_offline_soak import boundary
from provider_offline_soak.soak_scenario_plan import build_soak_scenario_plan


def generate_soak_events(provider: str, scenario: str) -> dict:
    plan = build_soak_scenario_plan(provider)["scenarios"][scenario]
    seed = f"V5.25:{provider}:{scenario}"
    rng = random.Random(seed)
    event_types = _expand_mix(plan["replay_mix"], plan["fault_mix"])
    events = []
    for index in range(plan["event_count"]):
        event_type = event_types[index % len(event_types)]
        events.append(
            {
                "event_ref": f"SOAK_EVENT_PLACEHOLDER_{scenario}_{index:05d}",
                "provider": provider,
                "scenario": scenario,
                "sequence": index,
                "event_type": event_type,
                "state_before": "SOAK_RUNNING",
                "state_after": _state_after(event_type),
                "audit_expected": True,
                "network_call_enabled": False,
                "sandbox_submission_enabled": False,
                "order_submission_enabled": False,
                "deterministic_marker": rng.randint(1000, 9999),
                **boundary(),
            }
        )
    return {"provider": provider, "scenario": scenario, "event_count": plan["event_count"], "events": events, **boundary()}


def generate_all_soak_events(provider: str) -> dict:
    scenarios = build_soak_scenario_plan(provider)["scenarios"]
    results = [generate_soak_events(provider, scenario) for scenario in scenarios]
    return {"provider": provider, "total_scenarios": len(results), "results": results, **boundary()}


def _expand_mix(replay_mix: dict, fault_mix: dict) -> list[str]:
    expanded = []
    for source in [replay_mix, fault_mix]:
        for event_type, count in source.items():
            expanded.extend([event_type] * max(1, min(count, 100)))
    return expanded or ["normal"]


def _state_after(event_type: str) -> str:
    if event_type in {"timeout", "rate_limit"}:
        return "RECOVERED"
    if event_type == "duplicate":
        return "DUPLICATE_DETECTED"
    if event_type == "safety":
        return "SAFETY_CHECKED"
    return "PROCESSED"
