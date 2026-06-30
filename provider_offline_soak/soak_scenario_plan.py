from __future__ import annotations

from provider_offline_soak import boundary


SCENARIO_DEFINITIONS = {
    "short_soak_100_events": (100, {"normal": 80, "duplicate": 10, "timeout": 5, "rate_limit": 5}),
    "medium_soak_1000_events": (1000, {"normal": 820, "duplicate": 60, "timeout": 40, "rate_limit": 40, "partial_fill": 40}),
    "long_soak_5000_events": (5000, {"normal": 4300, "duplicate": 200, "timeout": 150, "rate_limit": 150, "rejection": 100, "partial_fill": 100}),
    "mixed_replay_fault_soak": (1200, {"normal": 760, "duplicate": 120, "timeout": 120, "rate_limit": 120, "rejection": 40, "partial_fill": 40}),
    "duplicate_heavy_soak": (900, {"normal": 500, "duplicate": 350, "timeout": 20, "rate_limit": 20, "rejection": 10}),
    "rate_limit_heavy_soak": (900, {"normal": 500, "rate_limit": 350, "duplicate": 20, "timeout": 20, "partial_fill": 10}),
    "timeout_recovery_soak": (900, {"normal": 520, "timeout": 320, "duplicate": 20, "rate_limit": 20, "rejection": 20}),
    "audit_heavy_soak": (800, {"normal": 560, "audit": 160, "duplicate": 30, "timeout": 25, "rate_limit": 25}),
    "state_machine_boundary_soak": (750, {"normal": 510, "partial_fill": 120, "rejection": 60, "duplicate": 30, "timeout": 30}),
    "safety_boundary_soak": (600, {"normal": 430, "safety": 100, "duplicate": 25, "timeout": 25, "rate_limit": 20}),
}


def build_soak_scenario_plan(provider: str) -> dict:
    scenarios = {
        name: {
            "provider": provider,
            "scenario": name,
            "event_count": event_count,
            "replay_mix": {"normal": mix.get("normal", 0), "audit": mix.get("audit", 0), "partial_fill": mix.get("partial_fill", 0)},
            "fault_mix": {key: value for key, value in mix.items() if key not in {"normal", "audit", "partial_fill"}},
            "expected_terminal_state": "SOAK_COMPLETED",
            "expected_warning_budget": max(1, int(event_count * 0.04)),
            "expected_error_budget": max(0, int(event_count * 0.02)),
            **boundary(),
        }
        for name, (event_count, mix) in SCENARIO_DEFINITIONS.items()
    }
    return {"provider": provider, "scenarios": scenarios, "total_scenarios": len(scenarios), **boundary()}
