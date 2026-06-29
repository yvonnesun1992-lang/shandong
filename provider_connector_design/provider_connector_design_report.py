from __future__ import annotations

from pathlib import Path

from config.v5_provider_connector_design_config import get_connector_design_status, get_design_provider
from provider_connector_design import boundary
from provider_connector_design.account_position_mapping import build_account_position_mapping
from provider_connector_design.connector_safety_boundary import build_connector_safety_boundary
from provider_connector_design.idempotency_policy import build_idempotency_policy
from provider_connector_design.order_request_mapping import build_order_request_mapping
from provider_connector_design.order_response_mapping import build_order_response_mapping
from provider_connector_design.order_state_machine_design import build_order_state_machine_design
from provider_connector_design.provider_error_mapping import build_provider_error_mapping
from provider_connector_design.provider_field_mapping import build_provider_field_mapping
from provider_connector_design.rate_limit_policy import build_rate_limit_policy


REPORT_PATH = Path("reports/v5_21_provider_connector_design_report.md")


def build_provider_connector_design_summary(provider: str | None = None, check: str = "all") -> dict:
    design_provider = provider or get_design_provider()
    safety = build_connector_safety_boundary()
    missing = [
        "future provider docs must be reviewed by a human",
        "connector runtime remains disabled",
        "sandbox API remains disabled",
        "account read remains disabled",
        "order submission remains disabled",
        "credential vault remains future work",
    ]
    return {
        "version": "V5.21",
        "check": check,
        "connector_design_status": get_connector_design_status(),
        "design_provider": design_provider,
        "field_mapping": build_provider_field_mapping(design_provider),
        "order_request": build_order_request_mapping(design_provider),
        "order_response": build_order_response_mapping(design_provider),
        "account_position": build_account_position_mapping(design_provider),
        "error_mapping": build_provider_error_mapping(design_provider),
        "rate_limit": build_rate_limit_policy(design_provider),
        "idempotency": build_idempotency_policy(design_provider),
        "state_machine": build_order_state_machine_design(design_provider),
        "safety": safety,
        "missing_production_requirements": missing,
        "warnings": ["provider connector design is design-only; runtime requirements remain incomplete"],
        "verdict": "PASS" if safety["safe"] else "FAIL",
        **boundary(),
    }


def generate_provider_connector_design_report(provider: str | None = None, check: str = "all") -> dict:
    summary = build_provider_connector_design_summary(provider=provider, check=check)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(_render_report(summary), encoding="utf-8")
    verdict = "WARNING" if summary["verdict"] == "PASS" and summary["warnings"] else summary["verdict"]
    return {"verdict": verdict, "path": REPORT_PATH.as_posix(), "design_only": True, "summary": summary, "warnings": summary["warnings"]}


def _render_report(summary: dict) -> str:
    return f"""# V5.21 Provider-Specific Sandbox Connector Design

Verdict: {summary['verdict']}

## Connector Design Mode

- Mode: {summary['connector_design_status']['connector_design_mode']}
- Design provider: {summary['design_provider']}
- Design only: true
- Connector runtime enabled: false
- Sandbox API enabled: false
- Account read enabled: false
- Order submission enabled: false
- Broker connected: false
- Real money enabled: false
- Paper trading: true

## Field Mapping Design

- Rows: {len(summary['field_mapping']['field_mappings'])}
- Requires future provider docs: true

## Order Request Mapping

- Required internal fields: {len(summary['order_request']['required_internal_fields'])}
- Order submission enabled: false

## Order Response Mapping

- Raw response policy: redacted_only

## Account / Position Mapping

- Real account read enabled: false
- Sandbox account read enabled: false

## Error Mapping Design

- Error types: {len(summary['error_mapping']['error_mapping'])}

## Rate Limit Policy

- Network calls enabled: false

## Idempotency Policy

- Duplicate order protection: true

## Order State Machine Design

- States: {len(summary['state_machine']['states'])}
- Sandbox submission enabled: false
- Real submission enabled: false

## Connector Safety Boundary

- Safe: {str(summary['safety']['safe']).lower()}
- Errors: {len(summary['safety']['errors'])}

## Missing Production Requirements

{chr(10).join(f'- {item}' for item in summary['missing_production_requirements'])}

## Boundary

Current stage is provider-specific connector design only.
Current stage does not access provider portal.
Current stage does not connect to a real broker.
Current stage does not connect to sandbox API.
Current stage does not create API keys.
Current stage does not read real accounts.
Current stage does not submit real or sandbox orders.
Current stage does not use real funds.
Current stage is not a production trading system.
"""
