from __future__ import annotations

from pathlib import Path

from config.v5_sandbox_readiness_evidence_config import get_evidence_provider, get_evidence_status
from provider_sandbox_evidence import boundary
from provider_sandbox_evidence.evidence_orchestrator import build_sandbox_readiness_evidence_pack, summarize_evidence_pack


REPORT_PATH = Path("reports/v5_26_sandbox_readiness_evidence_report.md")


def generate_sandbox_readiness_evidence_report(provider: str | None = None, check: str = "all") -> dict:
    selected = provider or get_evidence_provider()
    pack = build_sandbox_readiness_evidence_pack(selected)
    summary = summarize_evidence_pack(pack)
    status = get_evidence_status()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(_render_report(status, pack, summary), encoding="utf-8")
    return {"path": REPORT_PATH.as_posix(), "provider": selected, "check": check, "summary": summary, "verdict": summary["verdict"], **boundary()}


def _render_report(status: dict, pack: dict, summary: dict) -> str:
    return f"""# V5.26 Provider Sandbox Readiness Evidence Pack

Final verdict: {summary["verdict"]}

Current phase is evidence pack only.

Boundary:
- Evidence mode: {status["evidence_mode"]}
- Provider: {summary["provider"]}
- Evidence runtime enabled: false
- Sandbox API enabled: false
- Account read enabled: false
- Order submission enabled: false
- Broker connected: false
- Real money enabled: false
- Paper trading: true

Evidence sources:
- V5.23 offline replay report
- V5.24 fault injection report
- V5.25 offline soak report

Readiness gaps:
{chr(10).join(f'- {item}' for item in summary["blocking_gaps"])}

Sandbox entry gate:
- Gate: BLOCKED
- Ready for sandbox API: false
- Ready for sandbox orders: false

Safety validation:
- Safe: {pack["safety"]["safe"]}
- No broker SDK import.
- No network calls.
- No plaintext credentials.
- No real account reference.
- No real order reference.
- No raw provider payload.
- No provider endpoint URL.

This is not a production trading system.
"""
