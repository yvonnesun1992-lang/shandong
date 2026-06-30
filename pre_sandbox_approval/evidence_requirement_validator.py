from __future__ import annotations

from pathlib import Path

from pre_sandbox_approval.init import boundary


EVIDENCE_FILES = {
    "V5.26 evidence pack exists": "reports/v5_26_sandbox_readiness_evidence_report.md",
    "V5.27 vault design exists": "reports/v5_27_credential_vault_design_report.md",
    "provider onboarding runbook exists": "docs/V5_SELECTED_PROVIDER_ONBOARDING.md",
    "connector design exists": "docs/V5_PROVIDER_CONNECTOR_DESIGN.md",
    "mock contract test exists": "tests/test_v522_provider_mock_contract.py",
    "offline replay exists": "tests/test_v523_provider_offline_replay.py",
    "fault injection exists": "tests/test_v524_provider_fault_injection.py",
    "offline soak exists": "tests/test_v525_provider_offline_soak.py",
}


def validate_evidence_requirements(provider: str = "alpaca") -> dict:
    missing = [name for name, path in EVIDENCE_FILES.items() if not Path(path).exists()]
    blocking = ["sandbox entry gate currently blocked"]
    if missing:
        blocking.append("evidence package incomplete")
    return {
        **boundary(),
        "provider": provider,
        "evidence_ready": False,
        "missing_items": missing,
        "blocking_items": blocking,
        "readiness_gaps_acknowledged": True,
        "sandbox_entry_gate_currently_blocked": True,
    }
