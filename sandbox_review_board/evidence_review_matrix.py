from __future__ import annotations

from pathlib import Path

from sandbox_review_board.init import boundary


EVIDENCE = {
    "V5.23 offline replay evidence": "tests/test_v523_provider_offline_replay.py",
    "V5.24 fault injection evidence": "tests/test_v524_provider_fault_injection.py",
    "V5.25 offline soak evidence": "tests/test_v525_provider_offline_soak.py",
    "V5.26 sandbox readiness evidence pack": "reports/v5_26_sandbox_readiness_evidence_report.md",
    "V5.27 credential vault design": "reports/v5_27_credential_vault_design_report.md",
    "V5.28 approval gate": "reports/v5_28_pre_sandbox_approval_report.md",
    "V5.29 launch plan": "reports/v5_29_sandbox_dry_run_launch_report.md",
    "security scan": "runtime/security_scan.py",
    "system_doctor": "scripts/system_doctor.py",
    "pytest summary": "tests/test_v529_sandbox_dry_run_launch.py",
    "frontend structure check": "web/frontend/app/v5-sandbox-dry-run-launch/page.tsx",
}


def build_evidence_review_matrix(provider: str = "alpaca") -> dict:
    items = []
    missing = []
    for name, path in EVIDENCE.items():
        present = Path(path).exists()
        items.append({"name": name, "path": path, "present": present, "review_status": "pending_review"})
        if not present:
            missing.append(name)
    blocking = ["missing production requirements remain unresolved", "review board cannot approve sandbox launch"]
    if missing:
        blocking.append("evidence items missing")
    return {
        **boundary(),
        "provider": provider,
        "evidence_items": items,
        "evidence_ready": False,
        "blocking_items": blocking,
        "warnings": ["evidence requires human review and cannot unlock sandbox"],
    }
