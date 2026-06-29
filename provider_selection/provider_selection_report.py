from __future__ import annotations

from pathlib import Path

from config.v5_provider_selection_config import get_candidate_providers, get_provider_selection_status
from provider_selection import PROVIDER_BOUNDARY
from provider_selection.account_preparation_checklist import build_account_preparation_checklist
from provider_selection.api_permission_checklist import build_api_permission_checklist
from provider_selection.compliance_checklist import build_compliance_checklist
from provider_selection.market_data_permission_checklist import build_market_data_permission_checklist
from provider_selection.provider_capability_matrix import build_provider_capability_matrix
from provider_selection.provider_risk_matrix import build_provider_risk_matrix
from provider_selection.provider_selection_safety_validator import build_provider_selection_safety_summary
from provider_selection.provider_selection_scoring import rank_providers
from provider_selection.provider_universe import build_provider_universe


REPORT_PATH = Path("reports/v5_19_provider_selection_report.md")


def build_provider_selection_summary(provider: str = "alpaca", ranking_only: bool = False, check: str = "all") -> dict:
    candidates = get_candidate_providers()
    selected_provider = provider if provider in candidates else candidates[0]
    ranking = rank_providers(candidates)
    account = build_account_preparation_checklist(selected_provider)
    api = build_api_permission_checklist(selected_provider)
    market_data = build_market_data_permission_checklist(selected_provider)
    compliance = build_compliance_checklist(selected_provider)
    safety = build_provider_selection_safety_summary()
    blocking = account["blocking_items"] + api["blocking_items"] + market_data["blocking_items"] + compliance["blocking_items"]
    warnings = ["future account, API, market data, and compliance preparation remains incomplete"]
    verdict = "PASS" if safety["safe"] else "FAIL"
    return {
        "version": "V5.19",
        "check": check,
        "ranking_only": ranking_only,
        "verdict": verdict,
        "status": get_provider_selection_status(),
        "universe": build_provider_universe(candidates),
        "capability_matrix": build_provider_capability_matrix(candidates),
        "risk_matrix": build_provider_risk_matrix(candidates),
        "account_checklist": account,
        "api_permissions": api,
        "market_data": market_data,
        "compliance": compliance,
        "ranking": ranking,
        "recommended_provider": ranking["recommended_provider"],
        "safety": safety,
        "warnings": warnings,
        "missing_production_requirements": blocking,
        **PROVIDER_BOUNDARY,
    }


def generate_provider_selection_report(provider: str = "alpaca", ranking_only: bool = False, check: str = "all") -> dict:
    summary = build_provider_selection_summary(provider=provider, ranking_only=ranking_only, check=check)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(_render_report(summary), encoding="utf-8")
    return {
        "verdict": "WARNING" if summary["verdict"] == "PASS" and summary["warnings"] else summary["verdict"],
        "path": REPORT_PATH.as_posix(),
        "selection_only": True,
        "summary": summary,
        "warnings": summary["warnings"],
    }


def _render_report(summary: dict) -> str:
    return f"""# V5.19 Broker Sandbox Provider Selection

Verdict: {summary['verdict']}

## Provider Selection Status

- Mode: {summary['status']['provider_selection_mode']}
- Candidate providers: {', '.join(summary['status']['candidate_providers'])}
- Selection only: true
- Provider connection enabled: false
- Sandbox API enabled: false
- Broker connected: false
- Real orders enabled: false
- Real money enabled: false
- Paper trading: true

## Provider Universe

- Providers: alpaca, ibkr, futu, tiger, schwab

## Capability Matrix

- Rows: {len(summary['capability_matrix']['matrix'])}

## Risk Matrix

- Rows: {len(summary['risk_matrix']['matrix'])}

## Account Preparation Checklist

- Provider: {summary['account_checklist']['provider']}
- Ready: false
- Blocking items: {len(summary['account_checklist']['blocking_items'])}

## API Permission Checklist

- API ready: false
- Credential storage: future_vault

## Market Data Permission Checklist

- Market data ready: false

## Compliance Checklist

- Compliance ready: false
- Legal advice provided: false

## Provider Ranking

- Recommended provider: {summary['recommended_provider']}
- Rankings: {len(summary['ranking']['rankings'])}

## Safety Validation

- Safe: {str(summary['safety']['safe']).lower()}
- Errors: {len(summary['safety']['errors'])}

## Missing Production Requirements

{chr(10).join(f'- {item}' for item in summary['missing_production_requirements'][:20])}

## Boundary

Current stage is provider selection and account preparation only.
Current stage does not connect to a real broker.
Current stage does not connect to sandbox API.
Current stage does not submit real orders.
Current stage does not use real funds.
Current stage is not a production trading system.
"""
