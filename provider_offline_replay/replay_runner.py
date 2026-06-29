from __future__ import annotations

from provider_offline_replay import boundary
from provider_offline_replay.replay_event_loader import load_all_replay_scenarios, load_replay_scenario
from provider_offline_replay.replay_state_machine import is_terminal_state, transition


def run_replay_scenario(provider: str, scenario: str) -> dict:
    loaded = load_replay_scenario(provider, scenario)
    current_state = "INIT"
    steps = []
    errors = []
    for event in loaded["events"]:
        result = transition(current_state, event["event_type"])
        step = {
            "event_index": event["event_index"],
            "event_type": event["event_type"],
            "previous_state": result["previous_state"],
            "next_state": result["next_state"],
            "accepted": result["accepted"],
            "warnings": result["warnings"],
            "errors": result["errors"],
        }
        steps.append(step)
        errors.extend(result["errors"])
        current_state = result["next_state"]

    terminal = is_terminal_state(current_state)
    if not terminal:
        errors.append(f"scenario {scenario} ended in non-terminal state {current_state}")

    return {
        "provider": provider,
        "scenario": scenario,
        "events_loaded": len(loaded["events"]),
        "steps": steps,
        "final_state": current_state,
        "terminal": terminal,
        "passed": not errors,
        "warnings": [],
        "errors": errors,
        **boundary(),
    }


def run_all_replay_scenarios(provider: str) -> dict:
    loaded = load_all_replay_scenarios(provider)
    results = [run_replay_scenario(provider, scenario) for scenario in loaded["scenarios"]]
    return {
        "provider": provider,
        "total_scenarios": len(results),
        "results": results,
        "passed": sum(1 for result in results if result["passed"]),
        "failed": sum(1 for result in results if not result["passed"]),
        "warnings": [warning for result in results for warning in result.get("warnings", [])],
        "errors": [error for result in results for error in result.get("errors", [])],
        **boundary(),
    }
