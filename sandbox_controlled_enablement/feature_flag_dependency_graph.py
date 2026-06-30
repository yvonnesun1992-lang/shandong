from __future__ import annotations

from sandbox_controlled_enablement.init import boundary


def build_feature_flag_dependency_graph(provider: str = "alpaca") -> dict:
    graph = {
        "CONTROLLED_GO": {
            "depends_on": ["future_review_board_approval", "preflight_packet_accepted"],
            "enabled": False,
            "blocked": True,
        },
        "SECRET_READ": {
            "depends_on": ["vault_live", "audit_logging", "operator_approval"],
            "enabled": False,
            "blocked": True,
        },
        "SANDBOX_API": {
            "depends_on": ["secret_read", "provider_docs_verified", "kill_switch"],
            "enabled": False,
            "blocked": True,
        },
        "ACCOUNT_READ": {
            "depends_on": ["sandbox_api", "read_only_scope", "audit_logging"],
            "enabled": False,
            "blocked": True,
        },
        "ORDER_PREVIEW": {
            "depends_on": ["account_read", "manual_approval"],
            "enabled": False,
            "blocked": True,
        },
        "ORDER_SUBMISSION": {
            "depends_on": ["future_review_only"],
            "enabled": False,
            "blocked": True,
            "reason": "order submission is blocked in V5.32",
        },
        "REAL_MONEY": {
            "depends_on": [],
            "enabled": False,
            "blocked": True,
            "reason": "real money is always blocked in V5.32",
        },
        "KILL_SWITCH": {"depends_on": ["future_live_test"], "enabled": False, "blocked": True},
        "AUDIT_LOGGING": {"depends_on": ["immutable_storage"], "enabled": False, "blocked": True},
        "ROLLBACK_READY": {"depends_on": ["rollback_rehearsal"], "enabled": False, "blocked": True},
        "MANUAL_APPROVAL_REQUIRED": {"depends_on": ["operator_policy"], "enabled": False, "blocked": True},
    }
    return {
        **boundary(),
        "provider": provider,
        "dependency_graph": graph,
        "current_flags": {name: False for name in graph},
        "invalid_unlock_paths": [
            "CONTROLLED_GO without future review board approval",
            "SECRET_READ without live vault and audit logging",
            "SANDBOX_API without secret-read dry approval",
            "ACCOUNT_READ without read-only scope",
            "ORDER_PREVIEW without manual approval",
            "ORDER_SUBMISSION in V5.32",
            "REAL_MONEY in V5.32",
        ],
    }
