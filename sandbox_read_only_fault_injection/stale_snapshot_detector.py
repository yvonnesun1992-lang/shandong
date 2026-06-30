from __future__ import annotations

from sandbox_read_only_fault_injection.fault_payload_catalog import FAULT_TYPES, build_fault_payload
from sandbox_read_only_fault_injection.init import boundary

ALLOWED_SNAPSHOT_AGE_SECONDS = 900


def detect_stale_snapshot(payload: dict) -> dict:
    findings: list[str] = []
    if payload.get("stale_snapshot") is True:
        findings.append("stale_snapshot true")
    if payload.get("snapshot_age_seconds", 0) > ALLOWED_SNAPSHOT_AGE_SECONDS:
        findings.append("snapshot_age_seconds too high")
    if "timestamp_placeholder" not in payload:
        findings.append("timestamp_missing")
    if payload.get("timestamp_placeholder_expired") is True:
        findings.append("timestamp_placeholder_expired")
    if payload.get("market_session_mismatch_placeholder") is True:
        findings.append("market_session_mismatch_placeholder")
    return {
        **boundary(),
        "provider": payload.get("provider", "alpaca"),
        "fault_type": payload.get("fault_type", "unknown"),
        "stale_detected": bool(findings),
        "findings": findings,
        "warnings": findings,
    }


def detect_all_stale_snapshots(provider: str = "alpaca") -> dict:
    results = [detect_stale_snapshot(build_fault_payload(provider, fault_type)) for fault_type in FAULT_TYPES]
    return {
        **boundary(),
        "provider": provider,
        "stale_detected": any(result["stale_detected"] for result in results),
        "results": results,
        "findings": [finding for result in results for finding in result["findings"]],
    }
