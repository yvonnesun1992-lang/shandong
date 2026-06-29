from __future__ import annotations

from pathlib import Path

from config.v5_provider_onboarding_config import get_onboarding_status
from provider_onboarding import boundary
from provider_onboarding.account_opening_runbook import build_account_opening_runbook
from provider_onboarding.api_key_preparation_runbook import build_api_key_preparation_runbook
from provider_onboarding.approval_risk_runbook import build_approval_risk_runbook
from provider_onboarding.market_data_onboarding_runbook import build_market_data_onboarding_runbook
from provider_onboarding.onboarding_safety_validator import build_onboarding_safety_summary
from provider_onboarding.sandbox_access_runbook import build_sandbox_access_runbook
from provider_onboarding.sandbox_dry_run_runbook import build_sandbox_dry_run_runbook
from provider_onboarding.selected_provider_resolver import build_selected_provider_summary


REPORT_PATH = Path("reports/v5_20_provider_onboarding_report.md")


def build_provider_onboarding_summary(provider: str | None = None, check: str = "all") -> dict:
    selected = build_selected_provider_summary()
    selected_provider = provider or selected["selected_provider"]
    account = build_account_opening_runbook(selected_provider)
    sandbox = build_sandbox_access_runbook(selected_provider)
    api_key = build_api_key_preparation_runbook(selected_provider)
    market_data = build_market_data_onboarding_runbook(selected_provider)
    approval = build_approval_risk_runbook(selected_provider)
    dry_run = build_sandbox_dry_run_runbook(selected_provider)
    safety = build_onboarding_safety_summary()
    blocking = (
        account["blocking_items"]
        + sandbox["blocking_items"]
        + api_key["blocking_items"]
        + market_data["blocking_items"]
        + approval["blocking_items"]
        + dry_run["blocking_items"]
    )
    return {
        "version": "V5.20",
        "check": check,
        "onboarding_status": get_onboarding_status(),
        "selected_provider": {**selected, "selected_provider": selected_provider},
        "account_opening": account,
        "sandbox_access": sandbox,
        "api_key_preparation": api_key,
        "market_data_onboarding": market_data,
        "approval_risk": approval,
        "sandbox_dry_run": dry_run,
        "safety": safety,
        "missing_production_requirements": blocking,
        "warnings": ["provider onboarding is a runbook only; production requirements remain incomplete"],
        "verdict": "PASS" if safety["safe"] else "FAIL",
        **boundary(),
    }


def generate_provider_onboarding_report(provider: str | None = None, check: str = "all") -> dict:
    summary = build_provider_onboarding_summary(provider=provider, check=check)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(_render_report(summary), encoding="utf-8")
    verdict = "WARNING" if summary["verdict"] == "PASS" and summary["warnings"] else summary["verdict"]
    return {
        "verdict": verdict,
        "path": REPORT_PATH.as_posix(),
        "runbook_only": True,
        "summary": summary,
        "warnings": summary["warnings"],
    }


def _render_report(summary: dict) -> str:
    provider = summary["selected_provider"]["selected_provider"]
    return f"""# V5.20 Selected Provider Sandbox Onboarding Runbook

Verdict: {summary['verdict']}

## Onboarding Mode

- Mode: {summary['onboarding_status']['onboarding_mode']}
- Runbook only: true
- Provider portal access enabled: false
- API key creation enabled: false
- Sandbox API enabled: false
- Broker connected: false
- Real orders enabled: false
- Real money enabled: false
- Paper trading: true

## Selected Provider

- Provider: {provider}
- Source: {summary['selected_provider']['source']}

## Account Opening Runbook

- Ready: false
- Steps: {len(summary['account_opening']['steps'])}

## Sandbox Access Runbook

- Ready: false
- Steps: {len(summary['sandbox_access']['steps'])}

## API Key Preparation Runbook

- Ready: false
- Credential storage: future_vault

## Market Data Onboarding Runbook

- Ready: false
- Steps: {len(summary['market_data_onboarding']['steps'])}

## Approval and Risk Runbook

- Ready: false
- Manual approval required: true
- Kill switch required: true

## Sandbox Dry Run Runbook

- Ready: false
- Sandbox orders enabled: false

## Onboarding Safety Validation

- Safe: {str(summary['safety']['safe']).lower()}
- Errors: {len(summary['safety']['errors'])}

## Blocking Items

{chr(10).join(f'- {item}' for item in summary['missing_production_requirements'][:24])}

## Boundary

Current stage is provider onboarding runbook only.
Current stage does not access provider portal.
Current stage does not connect to a real broker.
Current stage does not connect to sandbox API.
Current stage does not submit real or sandbox orders.
Current stage does not use real funds.
Current stage is not a production trading system.
"""
