from __future__ import annotations

from provider_fault_injection import boundary
from provider_fault_injection.fault_replay_runner import run_all_fault_scenarios


def build_fault_audit_trail(result: dict) -> dict:
    audit_events = [
        {
            "audit_event_id_placeholder": f"FAULT_AUDIT_EVENT_ID_PLACEHOLDER_{event['event_index']:03d}",
            "scenario": result["scenario"],
            "fault_type": result["fault_type"],
            "detected": result["detected"],
            "recovered": result["recovered"],
            "previous_state": "FAULT_PENDING" if event["event_index"] == 0 else "FAULT_PROGRESS",
            "next_state": result["final_state"] if event["event_type"] == "AUDIT_EVENT_WRITTEN" else "FAULT_PROGRESS",
            "timestamp_placeholder": "TIMESTAMP_PLACEHOLDER",
            "actor": "offline_fault_injection_suite",
            "raw_payload_stored": False,
            "provider_payload_redacted": True,
        }
        for event in result.get("events", [])
    ]
    return {
        "provider": result.get("provider", "unknown"),
        "scenario": result.get("scenario", "unknown"),
        "fault_type": result.get("fault_type", "unknown"),
        "audit_events": audit_events,
        "valid": bool(audit_events),
        "errors": [] if audit_events else ["no audit events generated"],
        "warnings": [],
        **boundary(),
    }


def build_all_fault_audit_trails(provider: str) -> dict:
    results = run_all_fault_scenarios(provider)
    trails = [build_fault_audit_trail(result) for result in results["results"]]
    errors = [error for trail in trails for error in trail.get("errors", [])]
    return {"provider": provider, "valid": not errors, "audit_trails": trails, "errors": errors, "warnings": [], **boundary()}
