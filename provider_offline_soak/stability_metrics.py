from __future__ import annotations

from provider_offline_soak import boundary
from provider_offline_soak.soak_runner import run_all_soak_scenarios


def compute_stability_metrics(soak_result: dict) -> dict:
    event_count = max(1, int(soak_result.get("event_count", 0)))
    processed = int(soak_result.get("processed_events", 0))
    warnings = len(soak_result.get("warnings", []))
    errors = len(soak_result.get("errors", []))
    duplicate_count = int(soak_result.get("duplicate_events_detected", 0))
    recovery_count = int(soak_result.get("recovery_events_detected", 0))
    invalid_transitions = int(soak_result.get("invalid_transition_count", 0))
    audit_events = int(soak_result.get("audit_events_written", 0))
    safety_violation_count = sum(1 for value in soak_result.get("safety_flags", {}).values() if value is True)
    error_rate = errors / event_count
    warning_rate = warnings / event_count
    audit_coverage = min(1.0, audit_events / event_count)
    stability_score = round(max(0.0, 1.0 - error_rate - warning_rate - invalid_transitions / event_count - safety_violation_count), 4)
    return {
        "provider": soak_result.get("provider", "unknown"),
        "scenario": soak_result.get("scenario", "unknown"),
        "processed_event_ratio": round(processed / event_count, 4),
        "warning_rate": round(warning_rate, 4),
        "error_rate": round(error_rate, 4),
        "recovery_rate": round(recovery_count / event_count, 4),
        "audit_coverage_rate": round(audit_coverage, 4),
        "duplicate_detection_rate": round(duplicate_count / event_count, 4),
        "invalid_transition_rate": round(invalid_transitions / event_count, 4),
        "safety_violation_count": safety_violation_count,
        "memory_growth_placeholder": "STABLE_PLACEHOLDER",
        "stability_score": stability_score,
        **boundary(),
    }


def compute_all_stability_metrics(provider: str) -> dict:
    results = run_all_soak_scenarios(provider)["results"]
    metrics = [compute_stability_metrics(result) for result in results]
    average_score = round(sum(item["stability_score"] for item in metrics) / max(1, len(metrics)), 4)
    return {"provider": provider, "total_scenarios": len(metrics), "average_stability_score": average_score, "metrics": metrics, **boundary()}
