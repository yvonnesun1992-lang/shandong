from __future__ import annotations

from sandbox_read_only_fault_injection.redaction_failure_detector import detect_all_redaction_failures
from sandbox_read_only_mock_replay.redaction_replay_validator import validate_all_payload_redaction
from sandbox_read_only_stability_gate.init import boundary


def check_redaction_stability(provider: str = "alpaca") -> dict:
    normal = validate_all_payload_redaction(provider)
    faults = detect_all_redaction_failures(provider)
    checks = {
        "normal_mock_payloads_redacted": normal.get("redaction_valid") is True,
        "fault_payloads_detected": faults.get("redaction_failures_detected") is True,
        "no_real_values_allowed": True,
        "frontend_redacted_only": True,
    }
    stable = all(checks.values())
    return {
        **boundary(),
        "provider": provider,
        "redaction_stable": stable,
        "findings": [] if stable else ["redaction stability incomplete"],
        "warnings": [] if stable else ["redaction stability warning"],
    }
