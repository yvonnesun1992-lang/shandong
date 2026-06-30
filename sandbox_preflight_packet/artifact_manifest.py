from __future__ import annotations

from pathlib import Path

from sandbox_preflight_packet.init import boundary


ARTIFACTS = {
    "V5.23 offline replay report": "reports/v5_23_provider_offline_replay_report.md",
    "V5.24 fault injection report": "reports/v5_24_provider_fault_injection_report.md",
    "V5.25 offline soak report": "reports/v5_25_provider_offline_soak_report.md",
    "V5.26 evidence report": "reports/v5_26_sandbox_readiness_evidence_report.md",
    "V5.27 vault design report": "reports/v5_27_credential_vault_design_report.md",
    "V5.28 approval report": "reports/v5_28_pre_sandbox_approval_report.md",
    "V5.29 launch plan report": "reports/v5_29_sandbox_dry_run_launch_report.md",
    "V5.30 review board report": "reports/v5_30_sandbox_review_board_report.md",
    "system_doctor result placeholder": "scripts/system_doctor.py",
    "pytest result placeholder": "tests/test_v531_sandbox_preflight_packet.py",
    "security scan placeholder": "runtime/security_scan.py",
    "frontend structure check placeholder": "web/frontend/app/v5-sandbox-preflight-packet/page.tsx",
}


def build_artifact_manifest(provider: str = "alpaca") -> dict:
    artifacts = [
        {"name": name, "path": path, "exists": Path(path).exists(), "local_only": True}
        for name, path in ARTIFACTS.items()
    ]
    return {
        **boundary(),
        "provider": provider,
        "artifacts": artifacts,
        "network_access": False,
        "broker_connected": False,
        "secret_read_enabled": False,
    }


def validate_artifact_manifest(manifest: dict) -> dict:
    missing = [item["name"] for item in manifest.get("artifacts", []) if not item.get("exists")]
    return {
        **boundary(),
        "valid": not missing,
        "missing_items": missing,
        "warnings": [] if not missing else ["some local artifacts are missing"],
    }
