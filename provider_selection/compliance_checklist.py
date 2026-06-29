from __future__ import annotations

from provider_selection import PROVIDER_BOUNDARY


COMPLIANCE_REQUIREMENTS = [
    "risk disclosure",
    "no investment advice disclaimer",
    "automated trading disclosure",
    "user consent",
    "audit log retention policy",
    "manual approval requirement",
    "kill switch requirement",
    "trading permission review",
    "jurisdiction review",
    "tax reporting awareness",
    "data privacy review",
]


def build_compliance_checklist(provider: str = "alpaca") -> dict:
    requirements = [{"requirement": item, "complete": False} for item in COMPLIANCE_REQUIREMENTS]
    return {"version": "V5.19", "provider": provider, "compliance_ready": False, "requirements": requirements, "blocking_items": COMPLIANCE_REQUIREMENTS, "legal_advice_provided": False, **PROVIDER_BOUNDARY}
