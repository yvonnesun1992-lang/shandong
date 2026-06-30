from __future__ import annotations

from pathlib import Path

from sandbox_preflight_packet.init import boundary


CHECKS = {
    "V5.26 evidence pack exists": "reports/v5_26_sandbox_readiness_evidence_report.md",
    "V5.27 credential vault design exists": "reports/v5_27_credential_vault_design_report.md",
    "V5.28 approval gate exists": "reports/v5_28_pre_sandbox_approval_report.md",
    "V5.29 launch plan exists": "reports/v5_29_sandbox_dry_run_launch_report.md",
    "V5.30 review board exists": "reports/v5_30_sandbox_review_board_report.md",
}


def build_final_preflight_checklist(provider: str = "alpaca") -> dict:
    checks = []
    missing = []
    for name, path in CHECKS.items():
        ok = Path(path).exists()
        checks.append({"name": name, "status": "ok" if ok else "missing"})
        if not ok:
            missing.append(name)
    required = [
        "review board decision is NO_GO",
        "sandbox API disabled",
        "secret read disabled",
        "account read disabled",
        "order submission disabled",
        "broker disconnected",
        "real money disabled",
        "provider selected",
        "evidence gaps listed",
        "risk blockers listed",
        "rollback plan exists",
        "kill switch plan exists",
        "audit plan exists",
    ]
    checks.extend({"name": item, "status": "blocked" if "disabled" in item or "NO_GO" in item else "planned"} for item in required)
    blocking = ["final decision remains NO_GO", "sandbox API disabled", "secret read disabled", "account read disabled", "order submission disabled"]
    if missing:
        blocking.append("preflight artifacts missing")
    return {
        **boundary(),
        "provider": provider,
        "preflight_ready": False,
        "checks": checks,
        "blocking_items": blocking,
        "warnings": ["final preflight packet is packet-only and cannot return GO"],
    }
