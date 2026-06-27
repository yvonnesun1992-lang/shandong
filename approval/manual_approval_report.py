from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from approval.approval_audit_trail import build_approval_audit_summary
from approval.approval_state_machine import ApprovalStateMachine
from approval.manual_approval_gate import approval_readiness_summary
from config.v5_manual_approval_config import get_manual_approval_policy, get_manual_approval_status


DEFAULT_REPORT_PATH = Path("reports/v5_9_manual_approval_gate_report.md")


def build_manual_approval_summary() -> dict[str, Any]:
    status = get_manual_approval_status()
    policy = get_manual_approval_policy()
    state_machine = ApprovalStateMachine().describe()
    audit_summary = build_approval_audit_summary()
    readiness = approval_readiness_summary()
    warnings = [
        "manual approval gate planning only",
        "auto approval disabled",
        "real order release disabled after simulated approval",
    ]
    verdict = "WARNING" if status["manual_approval_required"] and not status["auto_approval_enabled"] else "FAIL"
    return {
        "version": "V5.9",
        "verdict": verdict,
        "approval_status": status,
        "approval_policy": policy,
        "approval_state_machine": state_machine,
        "audit_trail_summary": audit_summary,
        "readiness": readiness,
        "missing_production_requirements": readiness["missing_production_requirements"],
        "manual_approval_required": True,
        "auto_approval_enabled": False,
        "real_order_after_approval": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "planning_only": True,
        "warnings": warnings,
        "errors": [],
    }


def generate_manual_approval_report(path: str | Path = DEFAULT_REPORT_PATH) -> dict[str, Any]:
    summary = build_manual_approval_summary()
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_render_report(summary), encoding="utf-8")
    return {"path": str(target), "verdict": summary["verdict"], "summary": summary}


def _render_report(summary: dict[str, Any]) -> str:
    status = summary["approval_status"]
    lines = [
        "# V5.9 Manual Approval Gate Planning Report",
        "",
        "## Manual Approval Status",
        f"- Manual approval mode: {status['manual_approval_mode']}",
        f"- Manual approval required: {status['manual_approval_required']}",
        f"- Auto approval enabled: {status['auto_approval_enabled']}",
        f"- Real order after approval: {status['real_order_after_approval']}",
        f"- Real orders enabled: {status['real_orders_enabled']}",
        f"- Real money enabled: {status['real_money_enabled']}",
        f"- Paper trading: {status['paper_trading']}",
        "",
        "## Approval State Machine",
        "```json",
        json.dumps(summary["approval_state_machine"], indent=2, ensure_ascii=False),
        "```",
        "",
        "## Reject-by-default Policy",
        f"- Reject by default: {summary['approval_policy']['reject_by_default']}",
        "- APPROVED_SIMULATED never releases a real order",
        "",
        "## Audit Trail Summary",
        "```json",
        json.dumps(summary["audit_trail_summary"], indent=2, ensure_ascii=False),
        "```",
        "",
        "## Missing Production Requirements",
        *[f"- {item}" for item in summary["missing_production_requirements"]],
        "",
        "## Safety Boundary",
        "- Current stage is manual approval planning only",
        "- Current stage does not connect to a broker",
        "- Current stage does not submit real orders",
        "- Current stage does not access real capital",
        "- Current stage is not production live trading",
        "",
        "## Final Verdict",
        summary["verdict"],
        "",
    ]
    return "\n".join(lines)
