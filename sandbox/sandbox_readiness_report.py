from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from config.v5_broker_sandbox_config import get_sandbox_readiness_status
from sandbox.credential_isolation_plan import build_credential_isolation_plan
from sandbox.sandbox_order_lifecycle_plan import build_sandbox_order_lifecycle_plan
from sandbox.sandbox_provider_plan import build_sandbox_provider_plan, list_sandbox_provider_plans
from sandbox.sandbox_rollback_plan import build_sandbox_rollback_plan
from sandbox.sandbox_safety_checklist import build_sandbox_safety_checklist


DEFAULT_REPORT_PATH = Path("reports/v5_10_broker_sandbox_readiness_report.md")


def build_sandbox_readiness_summary() -> dict[str, Any]:
    status = get_sandbox_readiness_status()
    provider_plan = build_sandbox_provider_plan(status["sandbox_provider"])
    all_provider_plans = list_sandbox_provider_plans()
    credential_policy = build_credential_isolation_plan()
    order_lifecycle = build_sandbox_order_lifecycle_plan()
    safety_checklist = build_sandbox_safety_checklist()
    rollback_plan = build_sandbox_rollback_plan()
    missing = [
        *credential_policy["missing_requirements"],
        *safety_checklist["blocking_items"],
        "sandbox certification runbook",
        "operator approval drill",
    ]
    warnings = [
        "broker sandbox readiness planning only",
        "sandbox connection disabled",
        "sandbox order submission disabled",
    ]
    verdict = "WARNING" if not safety_checklist["ready_for_sandbox_connection"] else "PASS"
    return {
        "version": "V5.10",
        "verdict": verdict,
        "sandbox_status": status,
        "provider_plan": provider_plan,
        "all_provider_plans": all_provider_plans,
        "credential_policy": credential_policy,
        "order_lifecycle": order_lifecycle,
        "safety_checklist": safety_checklist,
        "rollback_plan": rollback_plan,
        "missing_production_requirements": missing,
        "sandbox_connection_enabled": False,
        "sandbox_orders_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "planning_only": True,
        "warnings": warnings,
        "errors": [],
    }


def generate_sandbox_readiness_report(path: str | Path = DEFAULT_REPORT_PATH) -> dict[str, Any]:
    summary = build_sandbox_readiness_summary()
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_render_report(summary), encoding="utf-8")
    return {"path": str(target), "verdict": summary["verdict"], "summary": summary}


def _render_report(summary: dict[str, Any]) -> str:
    status = summary["sandbox_status"]
    lines = [
        "# V5.10 Broker Sandbox Readiness Report",
        "",
        "## Sandbox Status",
        f"- Sandbox mode: {status['sandbox_mode']}",
        f"- Sandbox provider: {status['sandbox_provider']}",
        f"- Credential policy: {status['sandbox_credential_policy']}",
        f"- Sandbox connection enabled: {status['sandbox_connection_enabled']}",
        f"- Sandbox orders enabled: {status['sandbox_orders_enabled']}",
        f"- Broker connected: {status['broker_connected']}",
        f"- Real orders enabled: {status['real_orders_enabled']}",
        f"- Real money enabled: {status['real_money_enabled']}",
        f"- Paper trading: {status['paper_trading']}",
        "",
        "## Provider Plan",
        "```json",
        json.dumps(summary["provider_plan"], indent=2, ensure_ascii=False),
        "```",
        "",
        "## Credential Isolation Policy",
        "```json",
        json.dumps(summary["credential_policy"], indent=2, ensure_ascii=False),
        "```",
        "",
        "## Sandbox Order Lifecycle Plan",
        "```json",
        json.dumps(summary["order_lifecycle"], indent=2, ensure_ascii=False),
        "```",
        "",
        "## Safety Checklist",
        "```json",
        json.dumps(summary["safety_checklist"], indent=2, ensure_ascii=False),
        "```",
        "",
        "## Rollback Plan",
        "```json",
        json.dumps(summary["rollback_plan"], indent=2, ensure_ascii=False),
        "```",
        "",
        "## Missing Production Requirements",
        *[f"- {item}" for item in summary["missing_production_requirements"]],
        "",
        "## Safety Boundary",
        "- Current stage is sandbox readiness planning only",
        "- Current stage does not connect to a sandbox API",
        "- Current stage does not connect to a real broker",
        "- Current stage does not submit real or sandbox orders",
        "- Current stage does not access real capital",
        "- Current stage is not production live trading",
        "",
        "## Final Verdict",
        summary["verdict"],
        "",
    ]
    return "\n".join(lines)
