from __future__ import annotations

from sandbox_read_only_fault_injection.fault_injection_orchestrator import run_read_only_fault_injection, summarize_fault_injection
from sandbox_read_only_stability_gate.init import boundary


def collect_fault_evidence(provider: str = "alpaca") -> dict:
    summary = summarize_fault_injection(run_read_only_fault_injection(provider))
    checks = {
        "fault_payload_catalog_exists": summary.get("total_fault_cases", 0) > 0,
        "all_fault_cases_blocked_or_warned": summary.get("blocked_fault_cases") == summary.get("total_fault_cases"),
        "no_fault_case_accepted": summary.get("unexpectedly_accepted") == [],
        "sandbox_api_disabled": summary.get("sandbox_api_enabled") is False,
        "secret_read_disabled": summary.get("secret_read_enabled") is False,
        "account_read_disabled": summary.get("account_read_enabled") is False,
        "balance_read_disabled": summary.get("balance_read_enabled") is False,
        "position_read_disabled": summary.get("position_read_enabled") is False,
        "order_submission_disabled": summary.get("order_submission_enabled") is False,
    }
    ready = all(checks.values())
    return {
        **boundary(),
        "provider": provider,
        "fault_evidence_ready": ready,
        "fault_injection_passed": ready,
        "evidence_items": checks,
        "warnings": [] if ready else ["fault evidence incomplete"],
    }


def summarize_fault_evidence(evidence: dict) -> dict:
    return {
        **boundary(),
        "provider": evidence.get("provider", "alpaca"),
        "fault_evidence_ready": evidence.get("fault_evidence_ready", False),
        "fault_injection_passed": evidence.get("fault_injection_passed", False),
        "warnings": evidence.get("warnings", []),
    }
