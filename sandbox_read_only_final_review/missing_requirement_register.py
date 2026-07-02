from __future__ import annotations

from sandbox_read_only_final_review.init import boundary

MISSING_REQUIREMENTS = [
    "live credential vault",
    "sandbox account credentials",
    "provider docs independent verification",
    "sandbox API endpoint allowlist",
    "network egress policy",
    "read-only credential scope proof",
    "account/balance/position redaction live test",
    "immutable audit log storage",
    "kill switch live test",
    "rollback rehearsal",
    "compliance signoff",
    "operator training",
    "emergency contact path",
    "production incident runbook",
]


def build_missing_requirement_register(provider: str = "alpaca") -> dict:
    return {
        **boundary(),
        "provider": provider,
        "missing_requirements": MISSING_REQUIREMENTS,
        "missing_count": len(MISSING_REQUIREMENTS),
        "read_only_connector_allowed": False,
        "warnings": ["missing requirements block real read-only sandbox access"],
    }
