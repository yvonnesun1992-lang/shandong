from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from broker.broker_safety_gate import broker_readiness_summary, validate_broker_safety
from broker.order_mapping_plan import build_order_mapping_plan
from broker.planned_broker_adapter import PlannedBrokerAdapter
from config.v5_broker_integration_config import get_broker_integration_status


DEFAULT_REPORT_PATH = Path("reports/v5_8_broker_integration_planning_report.md")


def build_broker_integration_summary() -> dict[str, Any]:
    status = get_broker_integration_status()
    adapter = PlannedBrokerAdapter(provider=status["broker_provider"])
    safety = validate_broker_safety()
    mapping = build_order_mapping_plan()
    readiness = broker_readiness_summary()
    adapter_status = adapter.get_account()
    missing = readiness["required_before_live"]
    warnings = [
        "broker integration planning only",
        "real broker connection disabled",
        "real orders disabled",
        "real money disabled",
    ]
    verdict = "WARNING" if safety["safe"] else "FAIL"
    return {
        "version": "V5.8",
        "verdict": verdict,
        "broker_status": status,
        "adapter_status": adapter_status,
        "order_mapping_plan": mapping,
        "account_position_mapping_plan": {
            "account_mapping_ready": False,
            "position_mapping_ready": False,
            "positions_source": "paper account only",
            "broker_positions_read": False,
            "broker_balance_read": False,
            "paper_trading": True,
        },
        "safety_gate": safety,
        "readiness": readiness,
        "missing_production_requirements": missing,
        "paper_trading": True,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "planning_only": True,
        "warnings": warnings,
        "errors": [],
    }


def generate_broker_integration_report(path: str | Path = DEFAULT_REPORT_PATH) -> dict[str, Any]:
    summary = build_broker_integration_summary()
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_render_report(summary), encoding="utf-8")
    return {"path": str(target), "verdict": summary["verdict"], "summary": summary}


def _render_report(summary: dict[str, Any]) -> str:
    status = summary["broker_status"]
    lines = [
        "# V5.8 Broker Integration Planning Report",
        "",
        "## Broker Integration Status",
        f"- Broker integration mode: {status['broker_integration_mode']}",
        f"- Planned provider: {status['broker_provider']}",
        f"- Execution mode: {status['broker_execution_mode']}",
        f"- Broker connected: {status['broker_connected']}",
        f"- Real orders enabled: {status['real_orders_enabled']}",
        f"- Real money enabled: {status['real_money_enabled']}",
        f"- Paper trading: {status['paper_trading']}",
        "",
        "## Adapter Status",
        f"- Status: {summary['adapter_status']['status']}",
        f"- Reason: {summary['adapter_status']['reason']}",
        "",
        "## Order Mapping Plan",
        f"- Mapping ready: {summary['order_mapping_plan']['mapping_ready']}",
        f"- Planned fields: {', '.join(summary['order_mapping_plan']['planned_fields'])}",
        f"- Unsupported fields: {', '.join(summary['order_mapping_plan']['unsupported_fields'])}",
        "",
        "## Account / Position Mapping Plan",
        "```json",
        json.dumps(summary["account_position_mapping_plan"], indent=2, ensure_ascii=False),
        "```",
        "",
        "## Safety Gate",
        f"- Safe: {summary['safety_gate']['safe']}",
        f"- Manual approval required: {summary['safety_gate']['manual_approval_required']}",
        f"- Kill switch required: {summary['safety_gate']['kill_switch_required']}",
        f"- Position limit required: {summary['safety_gate']['position_limit_required']}",
        "",
        "## Missing Production Requirements",
        *[f"- {item}" for item in summary["missing_production_requirements"]],
        "",
        "## Safety Boundary",
        "- Current stage does not connect to a broker",
        "- Current stage does not submit real orders",
        "- Current stage does not access real capital",
        "- Current stage is planning only",
        "- Current stage is not production live trading",
        "",
        "## Final Verdict",
        summary["verdict"],
        "",
    ]
    return "\n".join(lines)
