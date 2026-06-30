from __future__ import annotations

from provider_fault_injection import boundary
from provider_fault_injection.fault_scenario_catalog import build_fault_scenario_catalog


def inject_fault(provider: str, scenario: str) -> dict:
    catalog = build_fault_scenario_catalog(provider)
    definition = catalog["scenarios"].get(scenario)
    if definition is None:
        return {"provider": provider, "scenario": scenario, "events": [], "injected": False, "errors": ["unknown fault scenario"], **boundary()}
    events = [
        {
            "provider": provider,
            "scenario": scenario,
            "fault_type": definition["fault_type"],
            "event_index": index,
            "event_type": event_type,
            "fault_event_id_placeholder": f"FAULT_EVENT_ID_PLACEHOLDER_{index:03d}",
            "scenario_id_placeholder": definition["scenario_id_placeholder"],
            "raw_payload_stored": False,
            "provider_payload_redacted": True,
            "fault_injection_only": True,
        }
        for index, event_type in enumerate(definition["injected_event_sequence"])
    ]
    return {
        "provider": provider,
        "scenario": scenario,
        "fault_type": definition["fault_type"],
        "events": events,
        "expected_detection": definition["expected_detection"],
        "expected_recovery": definition["expected_recovery"],
        "expected_audit": definition["expected_audit"],
        "expected_final_state": definition["expected_final_state"],
        "injected": True,
        "errors": [],
        **boundary(),
    }


def inject_all_faults(provider: str) -> dict:
    catalog = build_fault_scenario_catalog(provider)
    results = [inject_fault(provider, scenario) for scenario in catalog["scenarios"]]
    return {
        "provider": provider,
        "total_scenarios": len(results),
        "results": results,
        "errors": [error for result in results for error in result.get("errors", [])],
        **boundary(),
    }
