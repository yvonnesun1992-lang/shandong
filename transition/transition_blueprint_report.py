from __future__ import annotations

from pathlib import Path

from config.v5_transition_blueprint_config import get_transition_status
from transition.credential_vault_blueprint import build_credential_vault_blueprint
from transition.environment_separation_blueprint import build_environment_separation_blueprint
from transition.feature_flag_blueprint import build_feature_flag_blueprint
from transition.kill_switch_blueprint import build_kill_switch_blueprint
from transition.real_order_blocker_policy import build_real_order_blocker_policy
from transition.rollback_blueprint import build_rollback_blueprint
from transition.sandbox_enablement_checklist import build_sandbox_enablement_checklist
from transition.transition_readiness_blueprint import build_transition_readiness_blueprint
from transition.transition_safety_validator import build_transition_safety_summary


REPORT_PATH = Path("reports/v5_18_transition_blueprint_report.md")


def build_transition_blueprint_summary(check: str = "all") -> dict:
    status = get_transition_status()
    readiness = build_transition_readiness_blueprint()
    checklist = build_sandbox_enablement_checklist()
    safety = build_transition_safety_summary()
    warnings = []
    if checklist["blocking_items"]:
        warnings.append("future sandbox enablement has blocking checklist items")
    verdict = "PASS" if safety["safe"] and status["blueprint_only"] else "FAIL"
    return {
        "version": "V5.18",
        "check": check,
        "verdict": verdict,
        "blueprint_only": True,
        "transition_enabled": False,
        "sandbox_api_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "status": status,
        "readiness": readiness,
        "credential_vault": build_credential_vault_blueprint(),
        "environments": build_environment_separation_blueprint(),
        "feature_flags": build_feature_flag_blueprint(),
        "sandbox_checklist": checklist,
        "real_order_blocker": build_real_order_blocker_policy(),
        "kill_switch": build_kill_switch_blueprint(),
        "rollback": build_rollback_blueprint(),
        "safety": safety,
        "warnings": warnings,
        "missing_production_requirements": checklist["blocking_items"],
    }


def generate_transition_blueprint_report(check: str = "all") -> dict:
    summary = build_transition_blueprint_summary(check)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(_render_report(summary), encoding="utf-8")
    return {
        "verdict": "WARNING" if summary["verdict"] == "PASS" and summary["warnings"] else summary["verdict"],
        "path": REPORT_PATH.as_posix(),
        "blueprint_only": True,
        "summary": summary,
        "warnings": summary["warnings"],
    }


def _render_report(summary: dict) -> str:
    return f"""# V5.18 Sandbox to Real Broker Transition Blueprint

Verdict: {summary['verdict']}

## Transition Status

- Mode: {summary['status']['transition_blueprint_mode']}
- Target provider: {summary['status']['transition_target_provider']}
- Blueprint only: true
- Transition enabled: false
- Sandbox API enabled: false
- Broker connected: false
- Real orders enabled: false
- Real money enabled: false
- Paper trading: true

## Readiness Blueprint

- Sections: {len(summary['readiness']['sections'])}
- Ready sections: 0

## Credential Vault Blueprint

- Future vault required: true
- Repository storage allowed: false
- Frontend storage allowed: false
- Log storage allowed: false

## Environment Separation Blueprint

- Environments: local, test, staging, sandbox, production
- Broker connection allowed now: false
- Real orders allowed now: false

## Feature Flag Blueprint

- Real path flags default to false
- Manual approval, kill switch, and audit logging default to true

## Sandbox Enablement Checklist

- Ready to enable sandbox API: false
- Ready to submit sandbox orders: false
- Blocking items: {len(summary['sandbox_checklist']['blocking_items'])}

## Real Order Blocker Policy

- Blocked: true
- Reason: real order path disabled in V5.18

## Kill Switch Blueprint

- Controls: {len(summary['kill_switch']['controls'])}

## Rollback Blueprint

- Steps: {len(summary['rollback']['steps'])}

## Transition Safety Validation

- Safe: {str(summary['safety']['safe']).lower()}
- Errors: {len(summary['safety']['errors'])}

## Missing Production Requirements

{chr(10).join(f'- {item}' for item in summary['missing_production_requirements'])}

## Boundary

Current stage is transition blueprint only.
Current stage does not connect to a real broker.
Current stage does not connect to sandbox API.
Current stage does not submit real orders.
Current stage does not use real funds.
Current stage is not a production trading system.
"""
