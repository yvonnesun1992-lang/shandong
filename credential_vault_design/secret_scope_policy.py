from __future__ import annotations

from credential_vault_design import boundary


def build_secret_scope_policy() -> dict:
    scopes = {
        "sandbox_read_only_key": {"environment": "sandbox", "trading_enabled": False},
        "sandbox_trading_key": {"environment": "sandbox", "trading_enabled": False},
        "real_read_only_key": {"environment": "real", "trading_enabled": False},
        "real_trading_key": {"environment": "real", "trading_enabled": False},
        "market_data_key": {"environment": "market_data", "trading_enabled": False},
        "audit_logging_key": {"environment": "audit", "trading_enabled": False},
    }
    return {
        "scopes": scopes,
        "sandbox_real_isolated": True,
        "read_only_trading_isolated": True,
        "frontend_access_allowed": False,
        "logs_record_secret": False,
        "ci_masks_secret": True,
        "manual_approval_releases_secret": False,
        **boundary(),
    }
