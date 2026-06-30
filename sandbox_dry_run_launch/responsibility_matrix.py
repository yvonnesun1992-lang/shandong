from __future__ import annotations

from sandbox_dry_run_launch.init import boundary


def build_responsibility_matrix(provider: str = "alpaca") -> dict:
    roles = {
        "strategy_owner": ["confirm strategy scope", "review paper-only boundary"],
        "technical_operator": ["validate local dry-run plan", "confirm feature flags locked"],
        "risk_operator": ["confirm risk limits", "confirm kill switch plan"],
        "compliance_reviewer": ["review disclosures", "confirm provider terms review requirement"],
        "vault_operator": ["review vault placeholder design", "confirm no secret read"],
        "emergency_operator": ["trigger kill switch plan", "confirm rollback plan"],
    }
    return {
        **boundary(),
        "provider": provider,
        "roles": {
            role: {
                "responsibilities": responsibilities,
                "approval_required": True,
                "can_enable_flags": False,
                "can_read_secret": False,
                "can_submit_order": False,
                "can_trigger_kill_switch": role == "emergency_operator",
            }
            for role, responsibilities in roles.items()
        },
    }
