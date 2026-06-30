from __future__ import annotations

from pre_sandbox_approval.init import boundary


def build_risk_acknowledgement_policy() -> dict:
    return {
        **boundary(),
        "acknowledgements": {
            "sandbox_is_not_production": True,
            "no_real_money": True,
            "no_real_order": True,
            "no_automated_live_trading": True,
            "manual_approval_remains_required": True,
            "kill_switch_exists": True,
            "rollback_plan_exists": True,
            "audit_trail_required": True,
            "provider_terms_must_be_reviewed": True,
            "market_data_terms_must_be_reviewed": True,
        },
    }
