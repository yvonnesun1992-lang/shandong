from __future__ import annotations

from pathlib import Path

from config.v5_credential_vault_design_config import get_vault_design_provider, get_vault_design_status
from credential_vault_design import boundary
from credential_vault_design.vault_design_orchestrator import build_vault_design, summarize_vault_design


REPORT_PATH = Path("reports/v5_27_credential_vault_design_report.md")


def generate_credential_vault_design_report(provider: str | None = None, check: str = "all") -> dict:
    selected = provider or get_vault_design_provider()
    design = build_vault_design(selected)
    summary = summarize_vault_design(design)
    status = get_vault_design_status()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(_render_report(status, design, summary), encoding="utf-8")
    return {"path": REPORT_PATH.as_posix(), "provider": selected, "check": check, "summary": summary, "verdict": summary["verdict"], **boundary()}


def _render_report(status: dict, design: dict, summary: dict) -> str:
    return f"""# V5.27 Credential Vault Interface Design

Final verdict: {summary["verdict"]}

Current phase is vault interface design only.

Boundary:
- Vault design mode: {status["vault_design_mode"]}
- Provider: {summary["provider"]}
- Vault runtime enabled: false
- Secret read enabled: false
- Secret write enabled: false
- Sandbox API enabled: false
- Broker connected: false
- Order submission enabled: false
- Real money enabled: false
- Paper trading: true

Design areas:
- Vault interface contract
- Secret scope policy
- Secret access policy
- Rotation and revocation runbook
- Vault audit design
- Safety validation

Safety validation:
- Safe: {design["safety"]["safe"]}
- No real vault connected.
- No secret read or write.
- No provider portal access.
- No broker connection.
- No sandbox API connection.

This is not a production trading system.
"""
