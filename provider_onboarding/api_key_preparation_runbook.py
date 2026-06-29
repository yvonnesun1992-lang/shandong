from __future__ import annotations

from provider_onboarding import boundary


STEPS = [
    "API key creation owner",
    "key scope plan",
    "read-only key vs trading key separation",
    "sandbox key vs real key separation",
    "vault storage required",
    "no plaintext storage",
    "no frontend exposure",
    "no logging",
    "rotation schedule",
    "emergency revoke process",
    "CI masking requirement",
]


def build_api_key_preparation_runbook(provider: str) -> dict:
    return {
        "provider": provider,
        "api_key_ready": False,
        "steps": STEPS.copy(),
        "blocking_items": [
            "future credential vault must be selected before any key exists",
            "API key creation remains disabled",
            "frontend exposure of credentials remains prohibited",
        ],
        "credential_storage": "future_vault",
        **boundary(),
    }
