from __future__ import annotations

from provider_selection import PROVIDER_BOUNDARY
from provider_selection.provider_capability_matrix import CAPABILITY_BASE
from provider_selection.provider_risk_matrix import RISK_BASE
from provider_selection.provider_universe import PROVIDER_METADATA


def score_provider(provider: str) -> dict:
    capability_score = CAPABILITY_BASE.get(provider, (0, {}))[0]
    risk_score = RISK_BASE.get(provider, (100, "HIGH"))[0]
    capabilities = CAPABILITY_BASE.get(provider, (0, {}))[1]
    account_complexity_penalty = {"low": 5, "medium": 12, "high": 20}.get(capabilities.get("account opening complexity", "high"), 20)
    api_clarity_bonus = {"high": 12, "medium": 7, "low": 2}.get(capabilities.get("rate_limit_clarity", "low"), 2)
    region_bonus = 10 if capabilities.get("region availability") in {"US", "global"} else 6
    credential_bonus = {"high": 18, "medium": 10, "low": 2}.get(capabilities.get("credential isolation fit", "medium"), 10)
    approval_bonus = {"high": 16, "medium": 9, "low": 2}.get(capabilities.get("manual approval fit", "medium"), 9)
    final_score = capability_score - risk_score - account_complexity_penalty + api_clarity_bonus + region_bonus + credential_bonus + approval_bonus
    return {
        "provider": provider,
        "capability_score": capability_score,
        "risk_score": risk_score,
        "account_complexity_penalty": account_complexity_penalty,
        "api_clarity_bonus": api_clarity_bonus,
        "region_bonus": region_bonus,
        "credential_isolation_bonus": credential_bonus,
        "manual_approval_bonus": approval_bonus,
        "score": max(final_score, 0),
        **PROVIDER_BOUNDARY,
    }


def rank_providers(providers: list[str] | None = None) -> dict:
    selected = providers or list(PROVIDER_METADATA)
    rankings = sorted([score_provider(provider) for provider in selected if provider in PROVIDER_METADATA], key=lambda row: row["score"], reverse=True)
    recommended = rankings[0]["provider"] if rankings else "none"
    return {
        "version": "V5.19",
        "rankings": rankings,
        "recommended_provider": recommended,
        "reason": [
            "highest static provider selection score",
            "credential isolation and manual approval fit weighted heavily",
            "selection only; no provider API was called",
        ],
        **PROVIDER_BOUNDARY,
    }


def recommend_provider(providers: list[str] | None = None) -> dict:
    ranking = rank_providers(providers)
    return {"recommended_provider": ranking["recommended_provider"], "reason": ranking["reason"], **PROVIDER_BOUNDARY}
