from __future__ import annotations

from provider_offline_replay import boundary
from provider_offline_replay.replay_event_catalog import build_replay_event_catalog


def load_replay_scenario(provider: str, scenario: str) -> dict:
    catalog = build_replay_event_catalog(provider)
    events = catalog["scenarios"].get(scenario, [])
    return {
        "provider": provider,
        "scenario": scenario,
        "events": events,
        "loaded": bool(events),
        **boundary(),
    }


def load_all_replay_scenarios(provider: str) -> dict:
    catalog = build_replay_event_catalog(provider)
    return {
        "provider": provider,
        "scenarios": catalog["scenarios"],
        "loaded": True,
        **boundary(),
    }
