from __future__ import annotations


READINESS_SECTIONS = [
    "technical_readiness",
    "security_readiness",
    "credential_readiness",
    "operational_readiness",
    "risk_readiness",
    "compliance_readiness",
    "rollback_readiness",
    "monitoring_readiness",
    "audit_readiness",
]


def build_transition_readiness_blueprint() -> dict:
    sections = []
    for name in READINESS_SECTIONS:
        sections.append(
            {
                "section": name,
                "ready": False,
                "required_items": _required_items(name),
                "blocking_items": ["future operator approval required", "real connector remains disabled"],
                "owner": "future_operator",
                "notes": ["Blueprint only. No broker or sandbox runtime is enabled."],
            }
        )
    return {
        "version": "V5.18",
        "blueprint_only": True,
        "transition_enabled": False,
        "sandbox_api_enabled": False,
        "broker_connected": False,
        "real_orders_enabled": False,
        "real_money_enabled": False,
        "paper_trading": True,
        "sections": sections,
    }


def _required_items(section: str) -> list[str]:
    mapping = {
        "technical_readiness": ["connector contract freeze", "deterministic integration test pass", "staging runbook"],
        "security_readiness": ["credential vault design approved", "network egress review", "masked audit logging"],
        "credential_readiness": ["vault-backed injection", "rotation procedure", "environment separation"],
        "operational_readiness": ["operator training", "manual approval runbook", "incident escalation"],
        "risk_readiness": ["kill switch rehearsal", "position limits", "loss limits"],
        "compliance_readiness": ["disclosure review", "jurisdiction checklist", "paper-only acknowledgement"],
        "rollback_readiness": ["flag rollback", "queue freeze", "checkpoint restore"],
        "monitoring_readiness": ["latency monitor", "order lifecycle monitor", "risk dashboard"],
        "audit_readiness": ["immutable audit plan", "review retention", "postmortem template"],
    }
    return mapping[section]
