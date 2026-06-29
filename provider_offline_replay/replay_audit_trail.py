from __future__ import annotations

from provider_offline_replay import boundary
from provider_offline_replay.replay_runner import run_all_replay_scenarios


def build_replay_audit_trail(replay_result: dict) -> dict:
    audit_events = [
        {
            "audit_event_id_placeholder": f"AUDIT_EVENT_ID_PLACEHOLDER_{step['event_index']:03d}",
            "scenario": replay_result["scenario"],
            "event_index": step["event_index"],
            "event_type": step["event_type"],
            "previous_state": step["previous_state"],
            "next_state": step["next_state"],
            "timestamp_placeholder": "TIMESTAMP_PLACEHOLDER",
            "actor": "offline_replay_harness",
            "raw_payload_stored": False,
            "provider_payload_redacted": True,
        }
        for step in replay_result.get("steps", [])
    ]
    return {
        "provider": replay_result.get("provider", "unknown"),
        "scenario": replay_result.get("scenario", "unknown"),
        "audit_events": audit_events,
        "valid": bool(audit_events),
        "errors": [] if audit_events else ["no audit events generated"],
        "warnings": [],
        **boundary(),
    }


def build_all_replay_audit_trails(provider: str) -> dict:
    results = run_all_replay_scenarios(provider)
    trails = [build_replay_audit_trail(result) for result in results["results"]]
    errors = [error for trail in trails for error in trail.get("errors", [])]
    return {
        "provider": provider,
        "valid": not errors,
        "audit_trails": trails,
        "errors": errors,
        "warnings": [],
        **boundary(),
    }
