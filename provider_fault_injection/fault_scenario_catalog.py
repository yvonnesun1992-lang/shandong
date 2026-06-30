from __future__ import annotations

from provider_fault_injection import boundary


FAULT_DEFINITIONS = {
    "connector_timeout": ("timeout", "TIMEOUT_DETECTED", "RECOVERY_REPLAYED", "AUDIT_EVENT_WRITTEN", "SAFE_RECOVERED"),
    "provider_reject": ("provider_reject", "REJECTION_DETECTED", "RECOVERY_REPLAYED", "AUDIT_EVENT_WRITTEN", "SAFE_RECOVERED"),
    "duplicate_order": ("duplicate_order", "DUPLICATE_ORDER_DETECTED", "RECOVERY_REPLAYED", "AUDIT_EVENT_WRITTEN", "SAFE_RECOVERED"),
    "stale_response": ("stale_response", "STALE_RESPONSE_DETECTED", "RECOVERY_REPLAYED", "AUDIT_EVENT_WRITTEN", "SAFE_RECOVERED"),
    "out_of_order_event": ("out_of_order_event", "OUT_OF_ORDER_EVENT_DETECTED", "RECOVERY_REPLAYED", "AUDIT_EVENT_WRITTEN", "SAFE_RECOVERED"),
    "partial_fill_mismatch": ("partial_fill_mismatch", "PARTIAL_FILL_MISMATCH_DETECTED", "RECOVERY_REPLAYED", "AUDIT_EVENT_WRITTEN", "SAFE_RECOVERED"),
    "rate_limit_storm": ("rate_limit_storm", "RATE_LIMIT_STORM_DETECTED", "RECOVERY_REPLAYED", "AUDIT_EVENT_WRITTEN", "SAFE_RECOVERED"),
    "audit_loss": ("audit_loss", "AUDIT_LOSS_DETECTED", "RECOVERY_REPLAYED", "AUDIT_EVENT_WRITTEN", "SAFE_RECOVERED"),
    "state_machine_corruption": ("state_machine_corruption", "CORRUPTED_STATE_DETECTED", "ROLLBACK_REPLAYED", "AUDIT_EVENT_WRITTEN", "SAFE_RECOVERED"),
    "recovery_rollback": ("recovery_rollback", "ROLLBACK_REQUIRED_DETECTED", "ROLLBACK_REPLAYED", "AUDIT_EVENT_WRITTEN", "SAFE_RECOVERED"),
    "kill_switch_trigger": ("kill_switch_trigger", "KILL_SWITCH_CONDITION_DETECTED", "KILL_SWITCH_TRIGGERED", "AUDIT_EVENT_WRITTEN", "KILL_SWITCH_SIMULATED"),
    "idempotency_collision": ("idempotency_collision", "IDEMPOTENCY_COLLISION_DETECTED", "RECOVERY_REPLAYED", "AUDIT_EVENT_WRITTEN", "SAFE_RECOVERED"),
}


def build_fault_scenario_catalog(provider: str) -> dict:
    return {
        "provider": provider,
        "scenarios": {
            scenario: _build_scenario(provider, scenario, definition)
            for scenario, definition in FAULT_DEFINITIONS.items()
        },
        **boundary(),
    }


def _build_scenario(provider: str, scenario: str, definition: tuple[str, str, str, str, str]) -> dict:
    fault_type, detection, recovery, audit, final_state = definition
    return {
        "provider": provider,
        "scenario": scenario,
        "scenario_id_placeholder": f"FAULT_SCENARIO_ID_PLACEHOLDER_{scenario.upper()}",
        "fault_type": fault_type,
        "injected_event_sequence": [
            "FAULT_BASELINE_CREATED",
            "FAULT_INJECTED",
            detection,
            recovery,
            audit,
        ],
        "expected_detection": detection,
        "expected_recovery": recovery,
        "expected_audit": audit,
        "expected_final_state": final_state,
        "fault_injection_only": True,
        "raw_payload_stored": False,
        "provider_payload_redacted": True,
        "provider_endpoint_placeholder": "DISABLED_PROVIDER_ENDPOINT_PLACEHOLDER",
    }
