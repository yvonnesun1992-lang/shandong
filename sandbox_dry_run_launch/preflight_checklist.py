from __future__ import annotations

from pathlib import Path

from sandbox_dry_run_launch.init import boundary


CHECKS = {
    "V5.26 evidence pack exists": "reports/v5_26_sandbox_readiness_evidence_report.md",
    "V5.27 vault design exists": "reports/v5_27_credential_vault_design_report.md",
    "V5.28 approval gate exists": "reports/v5_28_pre_sandbox_approval_report.md",
}


def build_preflight_checklist(provider: str = "alpaca") -> dict:
    checks = []
    missing = []
    for name, path in CHECKS.items():
        ok = Path(path).exists()
        checks.append({"name": name, "status": "ok" if ok else "missing"})
        if not ok:
            missing.append(name)
    required = [
        "provider selected",
        "dry-run scope approved placeholder",
        "feature flags locked",
        "kill switch plan exists",
        "rollback plan exists",
        "audit plan exists",
        "operator roles assigned placeholder",
        "compliance review placeholder",
        "credential vault not live",
        "sandbox API disabled",
        "order submission disabled",
    ]
    checks.extend({"name": item, "status": "planned"} for item in required)
    blocking = ["sandbox API disabled", "order submission disabled", "launch gate remains NO_GO"]
    if missing:
        blocking.append("preflight evidence incomplete")
    return {
        **boundary(),
        "provider": provider,
        "preflight_ready": False,
        "checks": checks,
        "blocking_items": blocking,
        "warnings": ["preflight is a launch plan only"],
    }
