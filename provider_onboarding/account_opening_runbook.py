from __future__ import annotations

from provider_onboarding import boundary


STEPS = [
    "account type preparation",
    "identity verification preparation",
    "region / jurisdiction review",
    "tax form awareness",
    "trading permission review",
    "paper trading / sandbox request",
    "account approval expectation",
    "operations owner assignment",
    "documentation to prepare",
    "cannot proceed automatically",
]


def build_account_opening_runbook(provider: str) -> dict:
    return {
        "provider": provider,
        "steps": STEPS.copy(),
        "blocking_items": [
            "human must review account type and jurisdiction requirements",
            "human must decide whether account opening is appropriate",
            "provider portal access remains disabled",
        ],
        "ready": False,
        "operations_owner": "future_human_operator",
        "legal_tax_advice": False,
        **boundary(),
    }
